#!/usr/bin/env python3
"""
Script to start the frontend development server.
"""

import subprocess
import sys
import os
from pathlib import Path

def main():
    """Start the React frontend development server."""
    
    frontend_dir = Path(__file__).parent.parent / "frontend"
    
    if not frontend_dir.exists():
        print("❌ Frontend directory not found!")
        return 1
    
    print("🚀 Starting React frontend development server...")
    print(f"📁 Working directory: {frontend_dir}")
    
    try:
        # Check if node_modules exists
        node_modules = frontend_dir / "node_modules"
        if not node_modules.exists():
            print("📦 Installing dependencies...")
            subprocess.run(["npm", "install"], cwd=frontend_dir, check=True)
        
        # Start the development server
        print("🎯 Starting development server on http://localhost:3000")
        subprocess.run(["npm", "start"], cwd=frontend_dir, check=True)
        
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to start frontend: {e}")
        return 1
    except KeyboardInterrupt:
        print("\n👋 Frontend server stopped")
        return 0

if __name__ == "__main__":
    sys.exit(main())