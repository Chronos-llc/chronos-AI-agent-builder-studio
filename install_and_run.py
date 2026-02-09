#!/usr/bin/env python3
"""
Complete installation and startup script for Chronos AI Agent Builder Studio
"""
import os
import sys
import subprocess
import time
import asyncio
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent

def run_command(command, cwd=None, shell=False, capture_output=True):
    """Run a command and return the result"""
    try:
        resolved_cwd = str(cwd or ROOT_DIR)
        if shell:
            result = subprocess.run(command, shell=True, cwd=resolved_cwd, 
                                  capture_output=capture_output, text=True, timeout=30)
        else:
            result = subprocess.run(command, cwd=resolved_cwd, 
                                  capture_output=capture_output, text=True, timeout=30)
        
        return result.returncode == 0, result.stdout, result.stderr
    except subprocess.TimeoutExpired:
        return False, "", "Command timed out"
    except Exception as e:
        return False, "", str(e)

def check_python_dependencies():
    """Check if required Python packages are installed"""
    print("🐍 Checking Python dependencies...")
    
    required_packages = [
        'fastapi', 'uvicorn', 'sqlalchemy', 'pydantic', 
        'jose[cryptography]', 'passlib[bcrypt]', 'httpx',
        'aiofiles', 'structlog'
    ]
    
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package.split('[')[0])
            print(f"  ✅ {package}")
        except ImportError:
            missing_packages.append(package)
            print(f"  ❌ {package}")
    
    return missing_packages

def install_python_packages():
    """Install missing Python packages"""
    print("\n📦 Installing Python dependencies...")
    
    # Try installing requirements.txt first
    success, stdout, stderr = run_command([
        sys.executable, "-m", "pip", "install", "-r", "backend/requirements.txt"
    ])
    
    if not success:
        print(f"❌ Failed to install from requirements.txt: {stderr}")
        return False
    
    print("✅ Python dependencies installed successfully")
    return True

def check_nodejs():
    """Check if Node.js is available"""
    print("\n📦 Checking Node.js...")
    
    success, stdout, stderr = run_command(["node", "--version"])
    if success:
        print(f"✅ Node.js version: {stdout.strip()}")
        return True
    else:
        print("❌ Node.js not found")
        return False

def install_frontend_deps():
    """Install frontend dependencies"""
    print("\n📦 Installing frontend dependencies...")
    
    success, stdout, stderr = run_command(["npm", "install"], cwd=ROOT_DIR / "frontend")
    
    if not success:
        print(f"❌ Failed to install frontend dependencies: {stderr}")
        return False
    
    print("✅ Frontend dependencies installed successfully")
    return True

def check_docker_services():
    """Check if Docker services are running"""
    print("\n🐳 Checking Docker services...")
    
    success, stdout, stderr = run_command(["docker-compose", "ps"])
    
    if "Up" in stdout:
        print("✅ Database services are running")
        return True
    else:
        print("❌ Database services are not running")
        print("💡 Please run: docker-compose up -d postgres redis")
        return False

def create_uploads_directory():
    """Create uploads directory"""
    print("\n📁 Creating uploads directory...")
    
    uploads_dir = ROOT_DIR / "backend" / "uploads"
    uploads_dir.mkdir(parents=True, exist_ok=True)
    
    print("✅ Uploads directory created")

def start_backend():
    """Start the backend server"""
    print("\n🔥 Starting backend server...")
    
    try:
        # Start uvicorn server
        process = subprocess.Popen([
            sys.executable, "-m", "uvicorn", 
            "app.main:app",
            "--app-dir", "backend",
            "--reload-dir", "backend",
            "--host", "0.0.0.0", 
            "--port", "8000", 
            "--reload"
        ], cwd=str(ROOT_DIR), stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        
        # Wait a moment for startup
        time.sleep(3)
        
        # Check if process is still running
        if process.poll() is None:
            print("✅ Backend server started successfully!")
            print("🔗 API: http://localhost:8000")
            print("📚 Docs: http://localhost:8000/docs")
            return process
        else:
            stdout, stderr = process.communicate()
            print(f"❌ Backend failed to start: {stderr.decode()}")
            return None
            
    except Exception as e:
        print(f"❌ Error starting backend: {e}")
        return None

def start_frontend():
    """Start the frontend server"""
    print("\n⚛️  Starting frontend server...")
    
    try:
        # Start npm dev server
        process = subprocess.Popen([
            "npm", "run", "dev"
        ], cwd=str(ROOT_DIR / "frontend"), stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        
        # Wait a moment for startup
        time.sleep(5)
        
        # Check if process is still running
        if process.poll() is None:
            print("✅ Frontend server started successfully!")
            print("🌐 Frontend: http://localhost:3000")
            return process
        else:
            stdout, stderr = process.communicate()
            print(f"❌ Frontend failed to start: {stderr.decode()}")
            return None
            
    except Exception as e:
        print(f"❌ Error starting frontend: {e}")
        return None

def main():
    """Main installation and startup function"""
    print("🚀 Chronos AI Agent Builder Studio - Auto Installation")
    print("=" * 60)
    
    # Create uploads directory
    create_uploads_directory()
    
    # Check and install Python dependencies
    missing_packages = check_python_dependencies()
    if missing_packages:
        print(f"\n📦 Installing missing packages: {', '.join(missing_packages)}")
        if not install_python_packages():
            print("❌ Failed to install Python dependencies")
            print("💡 Please run manually: pip install -r backend/requirements.txt")
            return
    
    # Check Node.js
    if not check_nodejs():
        print("❌ Node.js is required but not found")
        print("💡 Please install Node.js from https://nodejs.org/")
        return
    
    # Install frontend dependencies
    if not install_frontend_deps():
        print("❌ Failed to install frontend dependencies")
        print("💡 Please run manually: cd frontend && npm install")
        return
    
    # Check Docker services
    if not check_docker_services():
        print("❌ Database services are not running")
        print("💡 Please run: docker-compose up -d postgres redis")
        return
    
    print("\n" + "=" * 60)
    print("🎉 All dependencies installed!")
    print("=" * 60)
    
    # Start services
    backend_process = start_backend()
    if not backend_process:
        print("❌ Failed to start backend server")
        return
    
    frontend_process = start_frontend()
    if not frontend_process:
        print("❌ Failed to start frontend server")
        backend_process.terminate()
        return
    
    print("\n" + "=" * 60)
    print("🎊 SUCCESS! Application is running!")
    print("=" * 60)
    print("🌐 Frontend: http://localhost:3000")
    print("🔧 Backend API: http://localhost:8000")
    print("📚 API Documentation: http://localhost:8000/docs")
    print("🗄️  Database: localhost:5432")
    print("🔴 Redis: localhost:6379")
    print("=" * 60)
    print("\n📝 Instructions:")
    print("1. Open http://localhost:3000 in your browser")
    print("2. Register a new user account")
    print("3. Start building your AI agents!")
    print("\n🛑 Press Ctrl+C to stop all servers")
    print("=" * 60)
    
    try:
        # Wait for both processes
        backend_process.wait()
        frontend_process.wait()
    except KeyboardInterrupt:
        print("\n🛑 Shutting down servers...")
        backend_process.terminate()
        frontend_process.terminate()
        
        # Wait for processes to terminate
        try:
            backend_process.wait(timeout=5)
            frontend_process.wait(timeout=5)
        except subprocess.TimeoutExpired:
            backend_process.kill()
            frontend_process.kill()
        
        print("✅ All servers stopped")

if __name__ == "__main__":
    main()
