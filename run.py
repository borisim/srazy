#!/usr/bin/env python3
"""
Simple run script for the Srazy application
"""
import os
import sys

# Add the app directory to the Python path
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from app.backend.app import app

if __name__ == '__main__':
    print("=" * 50)
    print("Starting Srazy Web Application")
    print("=" * 50)
    print(f"Server running at: http://localhost:5000")
    print("Press CTRL+C to stop the server")
    print("=" * 50)
    
    app.run(host='0.0.0.0', port=5000, debug=True)
