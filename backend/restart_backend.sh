#!/bin/bash
# Script to restart the backend server

echo "🛑 Stopping any existing backend processes..."
pkill -f "uvicorn app.main:app" || true
sleep 2

echo "🔍 Checking if port 8000 is free..."
if lsof -i :8000 > /dev/null 2>&1; then
    echo "⚠️  Port 8000 is still in use. Killing processes..."
    lsof -ti :8000 | xargs kill -9 2>/dev/null || true
    sleep 2
fi

echo "✅ Starting backend server..."
cd "$(dirname "$0")"
source venv/bin/activate
uvicorn app.main:app --reload --port 8000

