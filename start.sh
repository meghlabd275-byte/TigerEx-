#!/bin/bash
# TigerEx Startup Script
# =====================

echo "🦁 Starting TigerEx..."

# Set port
PORT=${1:-8000}

echo "Starting TigerEx API on port $PORT..."

# Go to backend directory
cd "$(dirname "$0")/unified-backend"

# Run server
python3 server.py

echo "✅ TigerEx started!"