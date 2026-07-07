#!/usr/bin/env python3
"""
Deployment script for Recall Checker MCP server to Fly.io
"""

import subprocess
import sys
import os
from pathlib import Path


def run_command(cmd, description=""):
    """Run a shell command and handle errors"""
    if description:
        print(f"\n📦 {description}...")
    try:
        result = subprocess.run(cmd, shell=True, check=True, capture_output=False)
        return result.returncode == 0
    except subprocess.CalledProcessError as e:
        print(f"❌ Command failed: {cmd}")
        print(f"Error: {e}")
        return False


def check_flyctl():
    """Check if flyctl is installed"""
    try:
        subprocess.run("flyctl version", shell=True, capture_output=True, check=True)
        print("✅ flyctl is installed")
        return True
    except subprocess.CalledProcessError:
        print("❌ flyctl is not installed")
        print("Install it from: https://fly.io/docs/getting-started/installing-flyctl/")
        return False


def check_docker():
    """Check if Docker is available"""
    try:
        subprocess.run("docker --version", shell=True, capture_output=True, check=True)
        print("✅ Docker is available")
        return True
    except subprocess.CalledProcessError:
        print("⚠️  Docker not found - flyctl will handle build on remote servers")
        return False


def authenticate():
    """Authenticate with Fly.io"""
    print("\n🔐 Checking Fly.io authentication...")
    try:
        subprocess.run("flyctl auth whoami", shell=True, capture_output=True, check=True)
        print("✅ Already authenticated with Fly.io")
        return True
    except subprocess.CalledProcessError:
        print("⚠️  Not authenticated. Opening login...")
        return run_command("flyctl auth login", "Authenticating with Fly.io")


def create_app():
    """Create app on Fly.io if it doesn't exist"""
    print("\n🚀 Creating/updating Fly.io app...")
    return run_command("flyctl apps list", "Checking existing apps")


def deploy():
    """Deploy to Fly.io"""
    return run_command("flyctl deploy", "Deploying to Fly.io")


def get_status():
    """Get deployment status"""
    try:
        result = subprocess.run("flyctl status", shell=True, capture_output=True, text=True)
        print("\n📊 Current status:")
        print(result.stdout)
        return True
    except Exception as e:
        print(f"Could not fetch status: {e}")
        return False


def main():
    """Main deployment flow"""
    print("=" * 60)
    print("Recall Checker MCP - Fly.io Deployment Script")
    print("=" * 60)
    
    # Get current directory
    script_dir = Path(__file__).parent
    os.chdir(script_dir)
    
    # Pre-deployment checks
    print("\n🔍 Checking prerequisites...")
    
    if not check_flyctl():
        print("\n❌ flyctl is required. Please install it first.")
        sys.exit(1)
    
    check_docker()
    
    # Check for fly.toml
    if not Path("fly.toml").exists():
        print("❌ fly.toml not found in current directory")
        sys.exit(1)
    
    if not Path("Dockerfile").exists():
        print("❌ Dockerfile not found in current directory")
        sys.exit(1)
    
    if not Path("server.py").exists():
        print("❌ server.py not found in current directory")
        sys.exit(1)
    
    print("✅ All required files found")
    
    # Authenticate
    if not authenticate():
        print("\n❌ Authentication failed")
        sys.exit(1)
    
    # Create/verify app
    if not create_app():
        print("\n⚠️  Could not verify app (but might still work)")
    
    # Deploy
    print("\n🚀 Starting deployment...")
    if deploy():
        print("\n✅ Deployment successful!")
        get_status()
        
        # Show next steps
        print("\n" + "=" * 60)
        print("Next Steps:")
        print("=" * 60)
        print("1. View logs: flyctl logs")
        print("2. SSH into app: flyctl ssh console")
        print("3. Scale app: flyctl scale count=3")
        print("4. Open dashboard: flyctl open")
        print("5. Get app URL: flyctl info")
        
        return 0
    else:
        print("\n❌ Deployment failed")
        return 1


if __name__ == "__main__":
    sys.exit(main())
