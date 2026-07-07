# Recall Checker MCP Server — Architecture & Deployment Guide

## Overview

This is a **Model Context Protocol (MCP) server** that exposes product recall lookup as tools that AI assistants (Claude Desktop, VS Code Copilot, etc.) can call. It is deployed remotely on **Fly.io** and accessed over HTTPS via `mcp-remote`.

```
Claude Desktop
     │
     │  npx mcp-remote https://recall-checker.fly.dev/mcp
     ▼
Fly.io Proxy (HTTPS → internal port 8000)
     │
     ▼
Docker Container (python:3.10-slim)
     │
     ▼
FastMCP server (Uvicorn on 0.0.0.0:8000)
  ├── tool: check_recalls
  └── tool: get_recall_details
```

---

## File Explanations

### `server.py` — The MCP Server

```python
mcp = FastMCP("Recall Checker", host="0.0.0.0", port=8000, stateless_http=True)
```

**Key points:**
- Uses `FastMCP` from the `mcp` library to define tools
- `host="0.0.0.0"` — **critical**: binds to all network interfaces, not just localhost. Without this, Fly.io's proxy cannot reach the server inside the container.
- `port=8000` — must match `internal_port` in `fly.toml`
- `stateless_http=True` — each HTTP request is independent (no session state), suitable for serverless/auto-scaling deployments
- `mcp.run(transport="streamable-http")` — uses the Streamable HTTP transport which is the modern MCP protocol over HTTP (replaces SSE)

**Tools exposed:**
- `check_recalls(product_name)` — searches for recalls matching a product name
- `get_recall_details(recall_id)` — returns full details for a specific recall ID

> **v1 Note:** Uses mock data. Real CPSC API integration is pending.

---

### `Dockerfile` — Container Definition

```dockerfile
FROM python:3.10-slim          # Minimal Python 3.10 base image

WORKDIR /app                   # All files go in /app

COPY pyproject.toml .          # Copy dependency spec first (for layer caching)
RUN pip install --no-cache-dir -e .   # Install dependencies

COPY server.py .               # Copy server code (separate layer - rebuilt on code changes)

CMD ["python", "server.py"]    # Start the MCP server
```

**Why this structure matters:**
- `pyproject.toml` is copied and installed **before** `server.py`. Docker caches layers, so if only `server.py` changes, the expensive `pip install` step is skipped on subsequent builds — making deploys much faster.
- Uses `python:3.10-slim` to keep the image small (~53 MB total).

---

### `fly.toml` — Fly.io App Configuration

```toml
app = 'recall-checker'
primary_region = 'sin'          # Singapore (closest to your location)

[build]                         # Uses the Dockerfile to build the image

[http_service]
  internal_port = 8000          # Port the container listens on — must match server.py
  force_https = true            # All traffic redirected to HTTPS
  auto_stop_machines = 'stop'   # Machine stops when idle (saves cost)
  auto_start_machines = true    # Machine auto-starts on next request (cold start ~1-2s)
  min_machines_running = 0      # Scale to zero when idle

[[vm]]
  memory = '1gb'
  cpu_kind = 'shared'
  cpus = 1
```

**Key settings:**
- `internal_port = 8000` — Fly.io's edge proxy forwards external HTTPS traffic to this port inside the VM. Must exactly match `host`/`port` in `FastMCP()`.
- `auto_stop_machines / auto_start_machines` — enables scale-to-zero. The server stops after inactivity and wakes on the next request. This means the free tier works indefinitely.
- `min_machines_running = 0` — no always-on machines (cost saving).

---

### `deploy.py` — Deployment Helper Script

A Python wrapper around `flyctl` CLI commands that:

1. **Checks prerequisites** — verifies `flyctl` is installed, `fly.toml`, `Dockerfile`, and `server.py` exist
2. **Checks Docker** — warns if Docker is unavailable (Fly.io can build remotely without it)
3. **Authenticates** — runs `flyctl auth whoami`, opens browser login if needed
4. **Lists apps** — shows existing Fly.io apps
5. **Deploys** — runs `flyctl deploy` which builds the Docker image and deploys it

> **Note:** `deploy.py` runs `flyctl deploy` which uses the `fly.toml` in the current directory. If `fly.toml` references a deleted app, it will fail. In that case, delete `fly.toml` and run `flyctl launch --no-deploy` to generate a new one first.

---

## Claude Desktop Configuration

In your Claude Desktop `claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "recall-checker": {
      "command": "npx",
      "args": [
        "mcp-remote",
        "https://recall-checker.fly.dev/mcp"
      ]
    }
  }
}
```

**Why `/mcp` at the end?**  
FastMCP's Streamable HTTP transport registers its endpoint at the `/mcp` path by default. The root `/` returns 404.

**What `mcp-remote` does:**  
It is an npm package that acts as a local stdio↔HTTP bridge. Claude Desktop speaks MCP over stdio; `mcp-remote` translates that to HTTPS calls to the remote server.

---

## Troubleshooting Log — What Went Wrong and How It Was Fixed

### Problem 1: `fly.toml` referenced a deleted app
**Error:** `app not found`  
**Cause:** The old `fly.toml` had `app = 'recall-checker-mcp-tidy-shape-8134'` which no longer existed on Fly.io.  
**Fix:** Deleted `fly.toml` and ran `flyctl launch --no-deploy` to generate a fresh one with a new app name (`recall-checker`).

---

### Problem 2: `Dockerfile` had wrong capitalisation
**Error:** `failed to read dockerfile: open Dockerfile: no such file or directory`  
**Cause:** The file was named `dockerFile` (capital F) instead of `Dockerfile`.  
**Fix:** Renamed `dockerFile` → `Dockerfile`.

---

### Problem 3: `FastMCP.run()` doesn't accept `host`/`port` arguments
**Error:** `TypeError: FastMCP.run() got an unexpected keyword argument 'host'`  
**Cause:** `mcp.run(transport="streamable-http", host="0.0.0.0", port=8080)` — `host` and `port` are not valid arguments for `run()`.  
**Fix:** Removed `host` and `port` from `mcp.run()`. Later moved them to the `FastMCP()` constructor (see Problem 5).

---

### Problem 4: Server listening on `127.0.0.1` instead of `0.0.0.0`
**Error:** `instance refused connection. is your app listening on 0.0.0.0:8000?`  
**Cause:** FastMCP defaults Uvicorn to bind on `127.0.0.1` (localhost only). Fly.io's proxy connects to the VM's network interface, not its loopback, so it could not reach the server.  
**Attempted fixes that did NOT work:**
- Passing `host`/`port` to `mcp.run()` — invalid arguments
- Setting `UVICORN_HOST`/`UVICORN_PORT` environment variables — not respected
- Monkey-patching `uvicorn.run` — FastMCP calls Uvicorn internally after the patch point
- Calling `mcp.streamable_http_app()` directly with `uvicorn.run()` — bypassed the MCP route setup, causing 404s
- Using `socat` in the Dockerfile to forward ports — overcomplicated and introduced race conditions

**Fix that worked:** Pass `host="0.0.0.0"` and `port=8000` directly to the **`FastMCP()` constructor**:
```python
mcp = FastMCP("Recall Checker", host="0.0.0.0", port=8000, stateless_http=True)
```
This is how the [ed-donner/faq](https://github.com/ed-donner/faq) reference repo does it.

---

### Problem 5: `mcp-remote` getting 404 on all requests
**Error:** `SseError: SSE error: Non-200 status code (404)` on `POST /`  
**Cause:** `mcp-remote` was connecting to `https://recall-checker.fly.dev` (root path), but FastMCP serves the MCP protocol at `/mcp`.  
**Fix:** Updated Claude Desktop config to use `https://recall-checker.fly.dev/mcp`.

---

## Quick Reference — Deploy Commands

```powershell
# First-time setup (if fly.toml is missing)
flyctl launch --no-deploy

# Deploy
flyctl deploy

# Check status
flyctl status

# View live logs
flyctl logs

# View recent logs (no stream)
flyctl logs -n
```

---

## Architecture Summary

| Component | Technology | Role |
|-----------|-----------|------|
| MCP Framework | `mcp` Python library (`FastMCP`) | Defines tools, handles protocol |
| HTTP Server | Uvicorn (via FastMCP) | Serves HTTP on `0.0.0.0:8000` |
| Container | Docker (`python:3.10-slim`) | Packages the app |
| Hosting | Fly.io (Singapore) | Runs the container, provides HTTPS |
| Client Bridge | `mcp-remote` (npm) | Bridges Claude Desktop stdio ↔ HTTPS |
| AI Client | Claude Desktop | Calls the MCP tools |
