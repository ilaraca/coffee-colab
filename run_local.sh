#!/bin/bash

# Exit immediately if a command exits with a non-zero status
set -e

# Export custom DB URL with port 5433
export DATABASE_URL="postgresql://user:password@localhost:5433/coffeecolab"

echo "========================================"
echo "☕️ Coffee Co-lab: Local Runner"
echo "========================================"

# Check for --setup flag
SETUP=false
if [ "$1" == "--setup" ]; then
    SETUP=true
    echo "🔧 Setup mode enabled (Re-installing & Seeding)"
fi

# 1. Check/Start Docker
if ! docker info > /dev/null 2>&1; then
  echo "Error: Docker is not running. Please start Docker Desktop."
  exit 1
fi

echo "Checking Database..."
docker compose up -d

# 2. Virtual Environment
if [ ! -d "venv" ]; then
    echo "Creating venv..."
    python3 -m venv venv
    SETUP=true # Force setup if venv is new
fi

# 3. Dependencies & Seeding (Only if --setup or new venv)
if [ "$SETUP" = true ]; then
    echo "Installing Dependencies..."
    ./venv/bin/pip install -r requirements.txt > /dev/null
    
    echo "Waiting for DB..."
    sleep 3
    
    echo "Running Migrations..."
    ./venv/bin/alembic upgrade head
    
    echo "Seeding Database..."
    ./venv/bin/python scripts/seed.py
else
    echo "Skipping installation & seeding (use --setup to force)."
fi

# 5. Start Server
echo "========================================"
echo "🚀 Server Starting..."
echo "📍 URL: http://127.0.0.1:8000"
echo "========================================"

./venv/bin/uvicorn app.main:app --reload --reload-dir app
