@echo off
echo ========================================================
echo    Chronos AI Agent Builder Studio - Server Startup
echo ========================================================
echo.

REM Check if Docker is running
echo Checking Docker status...
docker info >nul 2>&1
if errorlevel 1 (
    echo ERROR: Docker is not running. Please start Docker Desktop first.
    pause
    exit /b 1
)

echo Docker is running! ✓
echo.

REM Start database services
echo Starting database services...
docker-compose up -d postgres redis
if errorlevel 1 (
    echo ERROR: Failed to start database services
    pause
    exit /b 1
)

echo Database services started! ✓
echo Waiting for services to be ready...
timeout /t 10 /nobreak >nul

echo.
echo ========================================================
echo Services Started Successfully!
echo ========================================================
echo.
echo 🌐 Frontend:     http://localhost:3000
echo 🔧 Backend API:  http://localhost:8000
echo 📚 API Docs:     http://localhost:8000/docs
echo 🗄️  Database:    localhost:5432
echo 🔴 Redis:        localhost:6379
echo.
echo To start the servers manually:
echo 1. Backend:  cd backend ^&^& python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
echo 2. Frontend: cd frontend ^&^& npm run dev
echo.
echo Press any key to continue...
pause >nul