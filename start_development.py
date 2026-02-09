#!/usr/bin/env python3
"""
Development startup script for Chronos AI Agent Builder Studio
"""
import os
import sys
import subprocess
import time
import signal
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent


def run_command(command, cwd=None, description=""):
    """Run a command and handle errors"""
    print(f"\n{'='*60}")
    print(f"🚀 {description}")
    print(f"Command: {' '.join(command)}")
    print(f"{'='*60}")
    
    try:
        process = subprocess.Popen(
            command,
            cwd=str(cwd or ROOT_DIR),
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            bufsize=1,
            universal_newlines=True
        )
        
        # Stream output in real-time
        while True:
            output = process.stdout.readline()
            if output == '' and process.poll() is not None:
                break
            if output:
                print(output.strip())
        
        # Check for errors
        stderr = process.stderr.read()
        if stderr:
            print(f"ERROR: {stderr}")
            
        return_code = process.poll()
        if return_code != 0:
            print(f"❌ Command failed with return code: {return_code}")
            return False
        else:
            print(f"✅ {description} completed successfully")
            return True
            
    except Exception as e:
        print(f"❌ Error running command: {e}")
        return False


def setup_environment():
    """Setup development environment"""
    print("🔧 Setting up development environment...")
    
    # Create uploads directory
    uploads_dir = ROOT_DIR / "backend" / "uploads"
    uploads_dir.mkdir(parents=True, exist_ok=True)
    print(f"✅ Created uploads directory: {uploads_dir}")
    
    # Create .env file if it doesn't exist
    env_file = ROOT_DIR / ".env"
    if not env_file.exists():
        env_example = ROOT_DIR / ".env.example"
        if env_example.exists():
            import shutil
            shutil.copy(env_example, env_file)
            print(f"✅ Created .env file from .env.example")
            print("⚠️  Please update .env file with your configuration")
        else:
            print("❌ .env.example file not found")
            return False
    else:
        print("✅ .env file already exists")
    
    return True


def install_dependencies():
    """Install Python and Node.js dependencies"""
    print("\n📦 Installing dependencies...")
    
    # Install Python dependencies
    success = run_command(
        [sys.executable, "-m", "pip", "install", "-r", "backend/requirements.txt"],
        cwd=ROOT_DIR,
        description="Installing Python dependencies"
    )
    
    if not success:
        print("❌ Failed to install Python dependencies")
        return False
    
    # Install Node.js dependencies
    success = run_command(
        ["npm", "install"],
        cwd=ROOT_DIR / "frontend",
        description="Installing Node.js dependencies"
    )
    
    if not success:
        print("❌ Failed to install Node.js dependencies")
        return False
    
    return True


def start_services():
    """Start development services"""
    print("\n🚀 Starting development services...")
    
    # Start database and Redis with Docker Compose
    print("🐳 Starting database and Redis...")
    success = run_command(
        ["docker-compose", "up", "-d", "postgres", "redis"],
        cwd=ROOT_DIR,
        description="Starting PostgreSQL and Redis"
    )
    
    if not success:
        print("❌ Failed to start database services")
        return False
    
    # Wait for services to be ready
    print("⏳ Waiting for services to be ready...")
    time.sleep(10)
    
    return True


def run_migrations():
    """Run database migrations"""
    print("\n🗃️  Setting up database...")
    
    # Create database tables
    success = run_command(
        [sys.executable, "-m", "app.main"],
        cwd=ROOT_DIR / "backend",
        description="Creating database tables"
    )
    
    return success


def start_applications():
    """Start backend and frontend applications"""
    print("\n🎯 Starting applications...")
    
    # Start backend
    print("🔥 Starting backend server...")
    backend_process = subprocess.Popen([
        sys.executable, "-m", "uvicorn", 
        "app.main:app",
        "--app-dir", "backend",
        "--reload-dir", "backend",
        "--host", "0.0.0.0", 
        "--port", "8000", 
        "--reload"
    ], cwd=str(ROOT_DIR))
    
    # Start frontend
    print("⚛️  Starting frontend server...")
    frontend_process = subprocess.Popen([
        "npm", "run", "dev"
    ], cwd=str(ROOT_DIR / "frontend"))
    
    return backend_process, frontend_process


def main():
    """Main startup function"""
    print("🎉 Welcome to Chronos AI Agent Builder Studio!")
    print("Setting up your development environment...\n")
    
    try:
        # Setup environment
        if not setup_environment():
            print("❌ Environment setup failed")
            return 1
        
        # Install dependencies
        if not install_dependencies():
            print("❌ Dependency installation failed")
            return 1
        
        # Start services
        if not start_services():
            print("❌ Service startup failed")
            return 1
        
        # Run migrations
        if not run_migrations():
            print("❌ Database setup failed")
            return 1
        
        # Start applications
        backend_process, frontend_process = start_applications()
        
        print("\n" + "="*60)
        print("🎊 Development environment is ready!")
        print("="*60)
        print("🌐 Frontend: http://localhost:3000")
        print("🔧 Backend API: http://localhost:8000")
        print("📚 API Docs: http://localhost:8000/docs")
        print("🗄️  Database: localhost:5432")
        print("🔴 Redis: localhost:6379")
        print("="*60)
        print("\nPress Ctrl+C to stop all services")
        print("="*60)
        
        # Wait for processes
        try:
            backend_process.wait()
            frontend_process.wait()
        except KeyboardInterrupt:
            print("\n🛑 Shutting down services...")
            
            # Terminate processes
            backend_process.terminate()
            frontend_process.terminate()
            
            # Wait for processes to terminate
            backend_process.wait(timeout=5)
            frontend_process.wait(timeout=5)
            
            # Force kill if needed
            if backend_process.poll() is None:
                backend_process.kill()
            if frontend_process.poll() is None:
                frontend_process.kill()
            
            print("✅ All services stopped")
        
    except Exception as e:
        print(f"❌ Startup failed: {e}")
        return 1
    
    return 0


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
