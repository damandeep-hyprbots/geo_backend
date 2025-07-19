#!/usr/bin/env python3
"""
Improved startup script for GEO Agent API with better ngrok integration
"""

import subprocess
import sys
import time
import os
import signal
import requests
import json
from pathlib import Path

def check_ngrok_installed():
    """Check if ngrok is installed"""
    try:
        result = subprocess.run(['ngrok', 'version'], capture_output=True, text=True)
        return result.returncode == 0
    except FileNotFoundError:
        return False

def check_ngrok_auth():
    """Check if ngrok is authenticated"""
    try:
        result = subprocess.run(['ngrok', 'config', 'check'], capture_output=True, text=True)
        return result.returncode == 0
    except Exception:
        return False

def setup_ngrok_auth():
    """Guide user through ngrok authentication"""
    print("🔐 ngrok Authentication Required")
    print("=" * 50)
    print("To use ngrok, you need to authenticate with your ngrok account.")
    print("1. Sign up at https://ngrok.com/signup")
    print("2. Get your authtoken from https://dashboard.ngrok.com/get-started/your-authtoken")
    print("3. Run the following command:")
    print("   ngrok config add-authtoken YOUR_AUTHTOKEN_HERE")
    print()
    
    authtoken = input("Enter your ngrok authtoken (or press Enter to skip): ").strip()
    
    if authtoken:
        try:
            subprocess.run(['ngrok', 'config', 'add-authtoken', authtoken], check=True)
            print("✅ ngrok authentication successful!")
            return True
        except subprocess.CalledProcessError:
            print("❌ Failed to authenticate ngrok")
            return False
    else:
        print("⏭️  Skipping ngrok authentication")
        return False

def start_ngrok_improved(port=8000):
    """Start ngrok tunnel with better error handling"""
    print(f"🚀 Starting ngrok tunnel on port {port}...")
    
    try:
        # Check if port is available
        import socket
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        result = sock.connect_ex(('localhost', port))
        sock.close()
        
        if result != 0:
            print(f"❌ Port {port} is not available. Make sure the FastAPI server is running.")
            return None, None
        
        # Start ngrok with more detailed output
        ngrok_process = subprocess.Popen(
            ['ngrok', 'http', str(port), '--log=stdout'],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        
        # Wait longer for ngrok to start
        print("⏳ Waiting for ngrok to start...")
        time.sleep(5)
        
        # Check if ngrok process is still running
        if ngrok_process.poll() is not None:
            stdout, stderr = ngrok_process.communicate()
            print(f"❌ ngrok failed to start")
            print(f"stdout: {stdout}")
            print(f"stderr: {stderr}")
            return None, None
        
        # Try to get ngrok URL with retries
        public_url = None
        for attempt in range(10):
            try:
                response = requests.get('http://localhost:4040/api/tunnels', timeout=3)
                if response.status_code == 200:
                    tunnels = response.json()
                    if tunnels.get('tunnels'):
                        public_url = tunnels['tunnels'][0]['public_url']
                        print(f"✅ ngrok tunnel started: {public_url}")
                        return ngrok_process, public_url
                    else:
                        print(f"⏳ Waiting for tunnel to be ready... (attempt {attempt + 1}/10)")
                        time.sleep(2)
                else:
                    print(f"⏳ ngrok API not ready yet... (attempt {attempt + 1}/10)")
                    time.sleep(2)
            except requests.RequestException:
                print(f"⏳ ngrok API not responding... (attempt {attempt + 1}/10)")
                time.sleep(2)
        
        print("⚠️  ngrok started but couldn't get public URL after 10 attempts")
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
        
        # Wait a moment for server to start
        time.sleep(3)
        
        # Check if server is running
        if server_process.poll() is None:
            print(f"✅ FastAPI server started on http://localhost:{port}")
            return server_process
        else:
            print("❌ FastAPI server failed to start")
            return None
        
    except Exception as e:
        print(f"❌ Failed to start FastAPI server: {e}")
        return None

def signal_handler(signum, frame):
    """Handle shutdown signals"""
    print("\n🛑 Shutting down...")
    sys.exit(0)

def main():
    """Main function"""
    print("🌐 GEO Agent API Startup (Improved)")
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
        
        # Check ngrok authentication
        if use_ngrok and not check_ngrok_auth():
            print("⚠️  ngrok not authenticated")
            if not setup_ngrok_auth():
                print("❌ ngrok authentication failed. Continuing without ngrok...")
                use_ngrok = False
    
    # Start FastAPI server first
    server_process = start_fastapi_server()
    if not server_process:
        print("❌ Failed to start server")
        return
    
    # Start ngrok if requested
    ngrok_process = None
    public_url = None
    
    if use_ngrok:
        ngrok_process, public_url = start_ngrok_improved()
        if not ngrok_process:
            print("⚠️  ngrok failed to start. Continuing with local access only...")
    
    print("\n" + "=" * 50)
    print("🎉 GEO Agent API is running!")
    print(f"📱 Local URL: http://localhost:8000")
    if public_url:
        print(f"🌍 Public URL: {public_url}")
    else:
        print("🌍 Public URL: Not available (ngrok failed)")
    print("📚 API Documentation: http://localhost:8000/docs")
    print("🔍 Interactive API: http://localhost:8000/redoc")
    print("=" * 50)
    print("\nPress Ctrl+C to stop the server")
    
    try:
        # Keep the script running with better monitoring
        while True:
            time.sleep(2)
            
            # Check if processes are still running
            if server_process.poll() is not None:
                print("❌ FastAPI server stopped unexpectedly")
                break
            
            if ngrok_process and ngrok_process.poll() is not None:
                print("❌ ngrok tunnel stopped unexpectedly")
                print("This might be due to:")
                print("- ngrok authentication issues")
                print("- network connectivity problems")
                print("- ngrok service being down")
                print("The API is still accessible locally at http://localhost:8000")
                break
                
    except KeyboardInterrupt:
        print("\n🛑 Shutting down...")
    
    finally:
        # Clean up processes
        if server_process:
            print("🛑 Stopping FastAPI server...")
            server_process.terminate()
            server_process.wait()
        
        if ngrok_process:
            print("🛑 Stopping ngrok tunnel...")
            ngrok_process.terminate()
            ngrok_process.wait()
        
        print("✅ Server stopped")

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

if __name__ == "__main__":
    main() 