#!/usr/bin/env python3
"""
Startup script for GEO Agent API with SSE and ngrok integration
"""

import os
import sys
import subprocess
import time
import signal
import json
import requests
from threading import Thread
import uvicorn

def check_ngrok():
    """Check if ngrok is installed"""
    try:
        result = subprocess.run(['ngrok', 'version'], capture_output=True, text=True)
        if result.returncode == 0:
            print("✅ ngrok is installed")
            return True
        else:
            print("❌ ngrok is not installed or not in PATH")
            return False
    except FileNotFoundError:
        print("❌ ngrok is not installed")
        return False

def start_ngrok(port):
    """Start ngrok tunnel"""
    try:
        print(f"🚀 Starting ngrok tunnel for port {port}...")
        ngrok_process = subprocess.Popen(
            ['ngrok', 'http', str(port), '--log=stdout'],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        
        # Wait a moment for ngrok to start
        time.sleep(3)
        
        # Get the public URL
        try:
            response = requests.get('http://localhost:4040/api/tunnels')
            tunnels = response.json()
            if tunnels['tunnels']:
                public_url = tunnels['tunnels'][0]['public_url']
                print(f"✅ ngrok tunnel started: {public_url}")
                return ngrok_process, public_url
            else:
                print("❌ No ngrok tunnels found")
                return ngrok_process, None
        except Exception as e:
            print(f"❌ Error getting ngrok URL: {e}")
            return ngrok_process, None
            
    except Exception as e:
        print(f"❌ Error starting ngrok: {e}")
        return None, None

def start_api():
    """Start the FastAPI server"""
    print("🚀 Starting GEO Agent API with SSE...")
    print("=" * 50)
    print("Endpoints:")
    print("- GET  /health - Health check")
    print("- POST /api/score - Get score and markdown (direct response)")
    print("- POST /api/optimize - SSE streaming for optimization")
    print("=" * 50)
    
    # Import and run the API
    from api_sse_optimize import app
    uvicorn.run(app, host="0.0.0.0", port=8002)

def main():
    """Main function"""
    print("🌐 GEO Agent API - SSE with ngrok")
    print("=" * 40)
    
    # Check if ngrok is installed
    if not check_ngrok():
        print("\n📦 To install ngrok:")
        print("1. Download from: https://ngrok.com/download")
        print("2. Extract and add to PATH")
        print("3. Run: ngrok authtoken YOUR_TOKEN")
        print("\n🚀 Starting API without ngrok...")
        start_api()
        return
    
    # Ask user if they want to use ngrok
    use_ngrok = input("\n🤔 Do you want to use ngrok for public access? (y/n): ").lower().strip()
    
    if use_ngrok == 'y':
        print("\n🚀 Starting API with ngrok...")
        
        # Start ngrok in background
        ngrok_process, public_url = start_ngrok(8002)
        
        if ngrok_process and public_url:
            print(f"\n🌐 Public URL: {public_url}")
            print(f"📊 API Documentation: {public_url}/docs")
            print(f"🔍 Health Check: {public_url}/health")
            print("\n📋 Test Commands:")
            print(f"# Health check")
            print(f"curl {public_url}/health")
            print(f"\n# Score endpoint")
            print(f"curl -X POST {public_url}/api/score \\")
            print(f"  -H 'Content-Type: application/json' \\")
            print(f"  -d '{{\"url\": \"https://example.com\"}}'")
            print(f"\n# SSE optimization")
            print(f"curl -N -X POST {public_url}/api/optimize \\")
            print(f"  -H 'Content-Type: application/json' \\")
            print(f"  -d '{{")
            print(f"    \"url\": \"https://example.com\",")
            print(f"    \"html\": \"<html><body><h1>Test</h1></body></html>\",")
            print(f"    \"markdown\": \"# Test\\n\\nContent\",")
            print(f"    \"score\": 0.75,")
            print(f"    \"target_keyword\": \"test\"")
            print(f"  }}'")
            print("\n" + "=" * 50)
            
            # Start API
            try:
                start_api()
            except KeyboardInterrupt:
                print("\n🛑 Shutting down...")
                if ngrok_process:
                    ngrok_process.terminate()
                    print("✅ ngrok tunnel stopped")
        else:
            print("❌ Failed to start ngrok, starting API locally...")
            start_api()
    else:
        print("\n🚀 Starting API locally...")
        start_api()

if __name__ == "__main__":
    main() 