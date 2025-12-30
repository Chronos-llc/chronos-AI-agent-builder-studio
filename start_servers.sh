#!/bin/bash

echo "========================================================"
echo "   Chronos AI Agent Builder Studio - Server Startup"
echo "========================================================"
echo

# Check if Docker is running
echo "Checking Docker status..."
if ! docker info >/dev/null 2>&1; then
    echo "ERROR: Docker is not running. Please start Docker Desktop first."
    exit 1
fi

echo "Docker is running! ✓"
echo

# Start database services
echo "Starting database services..."
docker-compose up -d postgres redis
if [ $? -ne 0 ]; then
    echo "ERROR: Failed to start database services"
    exit 1
fi

echo "Database services started! ✓"
echo "Waiting for services to be ready..."
sleep 10

echo
echo "========================================================"
echo "Services Started Successfully!"
echo "========================================================"
echo
echo "🌐 Frontend:     http://localhost:3000"
echo "🔧 Backend API:  http://localhost:8000"
echo "📚 API Docs:     http://localhost:8000/docs"
echo "🗄️  Database:    localhost:5432"
echo "🔴 Redis:        localhost:6379"
echo
echo "To start the servers manually:"
echo "1. Backend:  cd backend && python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload"
echo "2. Frontend: cd frontend && npm run dev"
echo
read -p "Press Enter to continue..."