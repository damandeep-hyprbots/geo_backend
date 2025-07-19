#!/usr/bin/env python3
"""
Startup script for GEO Agent API with optional ngrok integration
"""

import subprocess
import sys
import time
import os
import signal
import requests
from pathlib import Path

def check_ngrok_installed():
    """Check if ngrok is installed"""
    try:
        result = subprocess.run(['ngrok', 'version'], capture_output=True, text=True)
        return result.returncode == 0
    except FileNotFoundError:
        return False

def install_ngrok():
    """Install ngrok if not already installed"""
    print("🔧 Installing ngrok...")
    
    # For macOS
    if sys.platform == "darwin":
        try:
            subprocess.run(['brew', 'install', 'ngrok/ngrok/ngrok'], check=True)
            print("✅ ngrok installed successfully via Homebrew")
            return True
        except subprocess.CalledProcessError:
            print("❌ Failed to install ngrok via Homebrew")
            return False
    
    # For Linux
    elif sys.platform.startswith("linux"):
        try:
            # Download ngrok
            subprocess.run([
                'curl', '-s', 'https://ngrok-agent.s3.amazonaws.com/ngrok.asc', '|', 'sudo', 'tee', '/etc/apt/trusted.gpg.d/ngrok.asc', '>', '/dev/null'
            ], shell=True, check=True)
            
            subprocess.run([
                'echo', '"deb https://ngrok-agent.s3.amazonaws.com buster main"', '|', 'sudo', 'tee', '/etc/apt/sources.list.d/ngrok.list'
            ], shell=True, check=True)
            
            subprocess.run(['sudo', 'apt', 'update'], check=True)
            subprocess.run(['sudo', 'apt', 'install', 'ngrok'], check=True)
            
            print("✅ ngrok installed successfully")
            return True
        except subprocess.CalledProcessError:
            print("❌ Failed to install ngrok")
            return False
    
    else:
        print("❌ Automatic ngrok installation not supported for this platform")
        print("Please install ngrok manually from https://ngrok.com/download")
        return False

def start_ngrok(port=8000):
    """Start ngrok tunnel"""
    print(f"🚀 Starting ngrok tunnel on port {port}...")
    
    try:
        # Start ngrok in background
        ngrok_process = subprocess.Popen(
            ['ngrok', 'http', str(port)],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        
        # Wait a moment for ngrok to start
        time.sleep(3)
        
        # Get ngrok URL
        try:
            response = requests.get('http://localhost:4040/api/tunnels', timeout=5)
            if response.status_code == 200:
                tunnels = response.json()
                if tunnels['tunnels']:
                    public_url = tunnels['tunnels'][0]['public_url']
                    print(f"✅ ngrok tunnel started: {public_url}")
                    return ngrok_process, public_url
        except requests.RequestException:
            pass
        
        print("⚠️  ngrok started but couldn't get public URL")
        return ngrok_process, None
        
    except Exception as e:
        print(f"❌ Failed to start ngrok: {e}")
        return None, None

def start_fastapi_server(port=8000):
    """Start the FastAPI server"""
    print(f"🚀 Starting FastAPI server on port {port}...")
    
    try:
        # Start uvicorn server
        server_process = subprocess.Popen([
            sys.executable, '-m', 'uvicorn', 'api:app',
            '--host', '0.0.0.0',
            '--port', str(port),
            '--reload'
        ])
        
        print(f"✅ FastAPI server started on http://localhost:{port}")
        return server_process
        
    except Exception as e:
        print(f"❌ Failed to start FastAPI server: {e}")
        return None

def signal_handler(signum, frame):
    """Handle shutdown signals"""
    print("\n🛑 Shutting down...")
    sys.exit(0)

def main():
    """Main function"""
    print("🌐 GEO Agent API Startup")
    print("=" * 50)
    
    # Set up signal handlers
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    # Check if ngrok is needed
    use_ngrok = input("Do you want to use ngrok for public access? (y/n): ").lower().strip() == 'y'
    
    if use_ngrok:
        if not check_ngrok_installed():
            print("❌ ngrok not found")
            install_choice = input("Would you like to install ngrok? (y/n): ").lower().strip()
            if install_choice == 'y':
                if not install_ngrok():
                    print("❌ Failed to install ngrok. Continuing without ngrok...")
                    use_ngrok = False
            else:
                use_ngrok = False
    
    # Start FastAPI server
    server_process = start_fastapi_server()
    if not server_process:
        print("❌ Failed to start server")
        return
    
    # Start ngrok if requested
    ngrok_process = None
    public_url = None
    
    if use_ngrok:
        ngrok_process, public_url = start_ngrok()
    
    print("\n" + "=" * 50)
    print("🎉 GEO Agent API is running!")
    print(f"📱 Local URL: http://localhost:8000")
    if public_url:
        print(f"🌍 Public URL: {public_url}")
    print("📚 API Documentation: http://localhost:8000/docs")
    print("🔍 Interactive API: http://localhost:8000/redoc")
    print("=" * 50)
    print("\nPress Ctrl+C to stop the server")
    
    try:
        # Keep the script running
        while True:
            time.sleep(1)
            
            # Check if processes are still running
            if server_process.poll() is not None:
                print("❌ FastAPI server stopped unexpectedly")
                break
            
            if ngrok_process and ngrok_process.poll() is not None:
                print("❌ ngrok tunnel stopped unexpectedly")
                break
                
    except KeyboardInterrupt:
        print("\n🛑 Shutting down...")
    
    finally:
        # Clean up processes
        if server_process:
            server_process.terminate()
            server_process.wait()
        
        if ngrok_process:
            ngrok_process.terminate()
            ngrok_process.wait()
        
        print("✅ Server stopped")

if __name__ == "__main__":
    main() 