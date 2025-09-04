#!/usr/bin/env python3
"""
Startup script for the Instagram Bot Web Application
This script starts the FastAPI server with proper configuration.
"""

import uvicorn
import os
import sys
from pathlib import Path

def main():
    """Start the FastAPI server."""
    print("🚀 Starting Instagram Bot Web Application...")
    print("=" * 50)
    
    # Check if required files exist
    if not os.path.exists("backend.py"):
        print("❌ Error: backend.py not found!")
        print("Please make sure you're in the correct directory.")
        sys.exit(1)
    
    if not os.path.exists("static/index.html"):
        print("❌ Error: static/index.html not found!")
        print("Please make sure the static directory exists.")
        sys.exit(1)
    
    print("✅ All required files found")
    print("🌐 Starting web server...")
    print("📱 Open your browser and go to: http://localhost:8000")
    print("⏹️  Press Ctrl+C to stop the server")
    print("=" * 50)
    
    try:
        # Start the server
        uvicorn.run(
            "backend:app",
            host="0.0.0.0",
            port=8000,
            reload=True,  # Auto-reload on code changes
            log_level="info"
        )
    except KeyboardInterrupt:
        print("\n🛑 Server stopped by user")
    except Exception as e:
        print(f"❌ Error starting server: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
