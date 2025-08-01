#!/usr/bin/env python3
"""
Complete setup script for the AI Scrum Master project.
This script sets up both backend and frontend for development.
"""

import subprocess
import sys
import os
import time
from pathlib import Path

def run_command(command, cwd=None, description=""):
    """Run a command and handle errors."""
    print(f"🔄 {description}")
    try:
        result = subprocess.run(command, cwd=cwd, check=True, capture_output=True, text=True)
        print(f"✅ {description} - Success")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} - Failed")
        print(f"Error: {e.stderr}")
        return False

def check_prerequisites():
    """Check if required tools are installed."""
    print("🔍 Checking prerequisites...")
    
    tools = [
        ("docker", "Docker"),
        ("docker-compose", "Docker Compose"), 
        ("python", "Python"),
        ("node", "Node.js"),
        ("npm", "NPM")
    ]
    
    missing = []
    for tool, name in tools:
        try:
            subprocess.run([tool, "--version"], capture_output=True, check=True)
            print(f"✅ {name} is installed")
        except (subprocess.CalledProcessError, FileNotFoundError):
            print(f"❌ {name} is not installed")
            missing.append(name)
    
    if missing:
        print(f"\n⚠️ Missing tools: {', '.join(missing)}")
        print("Please install the missing tools before continuing.")
        return False
    
    return True

def setup_environment():
    """Set up environment files."""
    print("\n📝 Setting up environment files...")
    
    root_dir = Path(__file__).parent.parent
    
    # Backend .env
    backend_env = root_dir / "backend" / ".env"
    backend_env_example = root_dir / "backend" / ".env.example"
    
    if not backend_env.exists() and backend_env_example.exists():
        print("📄 Creating backend/.env from example...")
        with open(backend_env_example) as f:
            content = f.read()
        with open(backend_env, 'w') as f:
            f.write(content)
        print("✅ Created backend/.env")
        print("⚠️ Please edit backend/.env with your API keys!")
    
    # Frontend .env
    frontend_env = root_dir / "frontend" / ".env"
    frontend_env_example = root_dir / "frontend" / ".env.example"
    
    if not frontend_env.exists() and frontend_env_example.exists():
        print("📄 Creating frontend/.env from example...")
        with open(frontend_env_example) as f:
            content = f.read()
        with open(frontend_env, 'w') as f:
            f.write(content)
        print("✅ Created frontend/.env")

def setup_backend():
    """Set up the Python backend."""
    print("\n🐍 Setting up Python backend...")
    
    root_dir = Path(__file__).parent.parent
    backend_dir = root_dir / "backend"
    
    # Check for requirements.txt
    if not (backend_dir / "requirements.txt").exists():
        print("❌ Backend requirements.txt not found!")
        return False
    
    print("📦 Installing Python dependencies...")
    print("ℹ️ This may take a few minutes...")
    
    # Try to install in virtual environment if it exists
    venv_python = backend_dir / "venv" / "bin" / "python"
    if not venv_python.exists():
        venv_python = backend_dir / "venv" / "Scripts" / "python.exe"  # Windows
    
    if venv_python.exists():
        pip_cmd = [str(venv_python), "-m", "pip", "install", "-r", "requirements.txt"]
    else:
        pip_cmd = ["pip", "install", "-r", "requirements.txt"]
    
    return run_command(
        pip_cmd,
        cwd=backend_dir,
        description="Installing Python dependencies"
    )

def setup_frontend():
    """Set up the React frontend."""
    print("\n⚛️ Setting up React frontend...")
    
    root_dir = Path(__file__).parent.parent
    frontend_dir = root_dir / "frontend"
    
    if not (frontend_dir / "package.json").exists():
        print("❌ Frontend package.json not found!")
        return False
    
    print("📦 Installing Node.js dependencies...")
    print("ℹ️ This may take a few minutes...")
    
    return run_command(
        ["npm", "install"],
        cwd=frontend_dir,
        description="Installing Node.js dependencies"
    )

def setup_docker():
    """Set up Docker services."""
    print("\n🐳 Setting up Docker services...")
    
    root_dir = Path(__file__).parent.parent
    
    print("🛠️ Building Docker images...")
    success = run_command(
        ["docker-compose", "build"],
        cwd=root_dir,
        description="Building Docker images"
    )
    
    if not success:
        return False
    
    print("🚀 Starting Docker services...")
    return run_command(
        ["docker-compose", "up", "-d", "postgres", "redis"],
        cwd=root_dir,
        description="Starting PostgreSQL and Redis"
    )

def test_setup():
    """Test the setup by running the test suite."""
    print("\n🧪 Testing the setup...")
    
    root_dir = Path(__file__).parent.parent
    
    # Wait a bit for services to start
    print("⏳ Waiting for services to start...")
    time.sleep(10)
    
    # Test the MVP
    test_script = root_dir / "scripts" / "test_mvp.py"
    if test_script.exists():
        return run_command(
            ["python", str(test_script)],
            cwd=root_dir,
            description="Running MVP tests"
        )
    
    return True

def main():
    """Main setup process."""
    print("🚀 AI Scrum Master - Complete Setup")
    print("=" * 50)
    
    # Check prerequisites
    if not check_prerequisites():
        return 1
    
    # Setup environment
    setup_environment()
    
    # Setup backend
    if not setup_backend():
        print("\n❌ Backend setup failed!")
        return 1
    
    # Setup frontend
    if not setup_frontend():
        print("\n❌ Frontend setup failed!")
        return 1
    
    # Setup Docker
    if not setup_docker():
        print("\n❌ Docker setup failed!")
        return 1
    
    # Test setup
    if not test_setup():
        print("\n⚠️ Some tests failed, but setup is mostly complete")
    
    print("\n" + "=" * 50)
    print("🎉 Setup Complete!")
    print("=" * 50)
    print()
    print("📋 Next steps:")
    print("1. Edit backend/.env with your OpenAI API key")
    print("2. Configure Slack and Jira credentials (optional)")
    print("3. Start the development servers:")
    print("   Backend:  cd backend && uvicorn app.main:app --reload")
    print("   Frontend: cd frontend && npm start")
    print()
    print("4. Or use Docker for everything:")
    print("   docker-compose up -d")
    print()
    print("📚 Documentation:")
    print("   - API Docs: http://localhost:8000/docs")
    print("   - Frontend: http://localhost:3000")
    print("   - Test MVP: python scripts/test_mvp.py")
    print()
    print("🎯 Your AI Scrum Master is ready!")
    
    return 0

if __name__ == "__main__":
    sys.exit(main())