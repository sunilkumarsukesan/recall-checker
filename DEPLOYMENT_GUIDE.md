# Deployment Guide: Recall Checker MCP to Fly.io

## Overview

This guide covers deploying the Recall Checker MCP server to Fly.io with Docker.

## Prerequisites

1. **Fly.io account**
   - Sign up at https://fly.io (free tier available)

2. **flyctl CLI**
   - Install from: https://fly.io/docs/getting-started/installing-flyctl/
   - Verify: `flyctl version`

3. **Docker** (optional)
   - Fly.io can build remotely, but Docker speeds up local iteration
   - Verify: `docker version`

## Quick Deploy (Using deploy.py)

```bash
# From the recall-checker directory
python deploy.py
```

This script will:
1. ✅ Check for flyctl
2. ✅ Check for Docker
3. ✅ Authenticate with Fly.io
4. ✅ Deploy the app
5. ✅ Show status and next steps

## Manual Deploy

### Step 1: Authenticate

```bash
flyctl auth login
```

This opens a browser to authenticate.

### Step 2: Deploy

```bash
flyctl deploy
```

Fly.io will:
- Build the Docker image
- Create the app (if first time)
- Deploy to the `ord` (Chicago) region
- Start the server

### Step 3: Check Status

```bash
flyctl status
```

or

```bash
flyctl logs -a recall-checker-mcp
```

## Working with Deployed App

### View Logs
```bash
flyctl logs -a recall-checker-mcp
```

### SSH into Machine
```bash
flyctl ssh console -a recall-checker-mcp
python server.py  # Run server in console
```

### Scale Machines
```bash
flyctl scale count=3  # Run 3 instances
```

### Open Dashboard
```bash
flyctl open -a recall-checker-mcp
```

### Get App Info
```bash
flyctl info -a recall-checker-mcp
```

## Configuration

### Current Settings (fly.toml)

- **App**: `recall-checker-mcp`
- **Region**: `ord` (Chicago)
- **Memory**: 256MB
- **CPU**: 1 shared vCPU
- **Auto-scaling**: Enabled

### Customize

Edit `fly.toml`:

```toml
primary_region = "lax"  # Change region to Los Angeles
[[vm]]
memory = "512mb"        # Increase to 512MB
cpus = 2                # Use 2 CPUs
```

Then redeploy:
```bash
flyctl deploy
```

## Regions

Available regions:
- `ord` - Chicago
- `lax` - Los Angeles  
- `sjc` - San Jose
- `iad` - Virginia
- `yyz` - Toronto
- `lhr` - London
- `ams` - Amsterdam
- `fra` - Frankfurt
- `tpe` - Taipei
- `sin` - Singapore
- `syd` - Sydney

## Monitoring

### Memory Usage
```bash
flyctl status -a recall-checker-mcp
```

### Metrics Dashboard
```bash
flyctl open -a recall-checker-mcp
```

Navigate to "Metrics" tab to see CPU, memory, request rates.

## Troubleshooting

### App won't start
```bash
flyctl logs -a recall-checker-mcp
```
Check logs for errors. Common issues:
- Missing dependencies (check `pyproject.toml`)
- Python version mismatch

### Deploy fails
```bash
# Force clean rebuild
flyctl deploy --ha=false
```

### Need to check logs in real-time
```bash
flyctl logs -a recall-checker-mcp --follow
```

## Next Steps

### Option 1: Local Testing First
1. Test locally: `python server.py`
2. Test with mock data: `python test_server.py`
3. Then deploy to Fly.io

### Option 2: HTTP Wrapper (Future)
For easier integration with web clients, add an HTTP wrapper:
- Wrap MCP stdio in FastAPI/Flask
- Expose as REST API
- Deploy to Fly.io's HTTP service tier

### Option 3: Use Environment Variables
Add secrets for future real CPSC API keys:
```bash
flyctl secrets set CPSC_API_KEY=your_key_here
```

## Rollback

If something breaks:
```bash
flyctl releases  # See release history
flyctl rollback  # Rollback to previous version
```

## Delete App

```bash
flyctl apps destroy recall-checker-mcp
```

## Cost

Fly.io free tier includes:
- 3 shared-cpu VMs (256MB each)
- 160 GB egress/month
- Perfect for testing

Paid: $0.015/vCPU-hour + $0.15/GB storage
