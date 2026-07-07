# Recall Checker MCP Server

A minimal Model Context Protocol (MCP) server that checks for product recalls from the CPSC (Consumer Product Safety Commission) database in real-time. No watchlist, no storage — just ask and get answers, like weather.

## Features

This server exposes two tools:

### 1. `check_recalls`
Search for active product recalls by product name.

**Parameters:**
- `product_name` (string, required): Product to search for (e.g., "baby crib", "Samsung Galaxy", "Bluetooth speaker")

**Returns:**
- List of active recalls including:
  - Recall ID
  - Product name
  - Recall title
  - Hazard description
  - Date announced

### 2. `get_recall_details`
Get full details on a specific recall, including what consumers should do.

**Parameters:**
- `recall_id` (string, required): Recall ID (from check_recalls results)

**Returns:**
- Complete recall information:
  - Product name and description
  - Hazard description
  - Date announced
  - Remedy/action to take
  - Number of affected units

## Installation

```bash
# Create a virtual environment
python -m venv venv

# Activate it (Windows PowerShell):
.\venv\Scripts\Activate.ps1

# Install dependencies
pip install mcp requests pydantic
```

## Running the Server

```bash
# Activate venv first
.\venv\Scripts\Activate.ps1

# Start the server
python server.py
```

The server listens on stdio and connects to the CPSC API in real-time for each query.

## Deployment to Fly.io

### Prerequisites
- Fly.io account (free tier available)
- `flyctl` CLI installed: https://fly.io/docs/getting-started/installing-flyctl/
- Docker installed (optional - Fly.io can build remotely)

### Deploy

```bash
# Run the deployment script
python deploy.py
```

Or manually:

```bash
# Authenticate
flyctl auth login

# Deploy
flyctl deploy
```

### Connect to Deployed Server

Once deployed to Fly.io, you can:

1. **View logs**:
   ```bash
   flyctl logs -a recall-checker-mcp
   ```

2. **SSH into the machine**:
   ```bash
   flyctl ssh console -a recall-checker-mcp
   ```

3. **Get app info**:
   ```bash
   flyctl info -a recall-checker-mcp
   ```

### For Claude Desktop Integration with Fly.io

Since MCP servers use stdio, you have two options:

**Option 1: Local deployment** (recommended for now)
- Run locally on your machine
- Update Claude Desktop config to point to local venv

**Option 2: Remote via SSH tunnel**
- Deploy to Fly.io
- Use SSH tunneling to connect from Claude Desktop
- Or wrap the server in an HTTP interface (future enhancement)


## Example Usage

**In Claude or another MCP client:**

1. Check for recalls:
   - "Search for recalls on baby cribs"
   - "Are there recalls for Samsung phones?"
   - "Check for Bluetooth speaker recalls"

2. Get details:
   - "Tell me more about recall 12345"
   - "What's the remedy for that Samsung recall?"

## How It Works

- **No caching**: Searches mock recall database (v1) for each request
- **No storage**: No watchlist, no database, no background jobs
- **Minimal footprint**: Just like weather API — ask, search, answer
- **Real-time ready**: Architecture designed to swap in live CPSC API calls

## Data Source

**v1 Status**: Using mock recall data for demonstration.

The mock database includes example recalls for:
- Baby cribs (entrapment hazard)
- LED bulbs (fire hazard)
- Building blocks (magnet hazard)

**Future v2**: Will integrate with CPSC's public REST API: `https://www.saferproducts.gov/RestWebServices/Recall` once API endpoint access is resolved. The server architecture is designed to swap in real API calls with one code change.

## Architecture

- **MCP Python SDK (FastMCP)**: Server implementation
- **Requests library**: CPSC API calls
- **Pydantic**: Response validation

## v1 Scope

This is intentionally minimal for v1. Future versions can add:
- Watchlist storage
- Historical recall tracking
- Email notifications
- NHTSA vehicle recalls
- Multi-product batch checking

## Notes

- CPSC API is free and public (no authentication needed)
- Response times depend on CPSC API availability
- Search is best with specific product names (e.g., "baby gate" vs "gate")
