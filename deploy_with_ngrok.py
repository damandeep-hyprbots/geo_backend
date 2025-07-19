#!/usr/bin/env python3
"""
Deployment script for GEO Agent API Architecture with ngrok
"""

import subprocess
import sys
import time
import os
import signal
import requests
import json
from pathlib import Path

def check_dependencies():
    """Check if required dependencies are installed"""
    print("🔍 Checking dependencies...")
    
    # Check Python packages
    required_packages = ['fastapi', 'uvicorn', 'requests', 'aiohttp', 'sse-starlette']
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package)
        except ImportError:
            missing_packages.append(package)
    
    if missing_packages:
        print(f"❌ Missing packages: {', '.join(missing_packages)}")
        print("Installing missing packages...")
        try:
            subprocess.run([sys.executable, '-m', 'pip', 'install'] + missing_packages, check=True)
            print("✅ Dependencies installed successfully")
        except subprocess.CalledProcessError:
            print("❌ Failed to install dependencies")
            return False
    
    print("✅ All dependencies are available")
    return True

def setup_ngrok():
    """Setup ngrok with authentication"""
    print("\n🔧 Setting up ngrok...")
    
    # Check if ngrok is installed
    try:
        result = subprocess.run(['ngrok', 'version'], capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✅ ngrok is installed: {result.stdout.strip()}")
        else:
            print("❌ ngrok is not working properly")
            return False
    except FileNotFoundError:
        print("❌ ngrok is not installed")
        install_choice = input("Would you like to install ngrok? (y/n): ").lower().strip()
        if install_choice == 'y':
            if not install_ngrok():
                return False
        else:
            return False
    
    # Check ngrok authentication
    try:
        result = subprocess.run(['ngrok', 'config', 'check'], capture_output=True, text=True)
        if result.returncode == 0:
            print("✅ ngrok is authenticated")
            return True
        else:
            print("❌ ngrok is not authenticated")
            return setup_ngrok_auth()
    except Exception as e:
        print(f"❌ Error checking ngrok auth: {e}")
        return False

def setup_ngrok_auth():
    """Guide user through ngrok authentication"""
    print("\n🔐 ngrok Authentication Required")
    print("=" * 50)
    print("To use ngrok, you need to authenticate with your ngrok account.")
    print("1. Sign up at https://ngrok.com/signup")
    print("2. Get your authtoken from https://dashboard.ngrok.com/get-started/your-authtoken")
    print("3. Enter your authtoken below")
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

def install_ngrok():
    """Install ngrok"""
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

def start_api_server():
    """Start the API server"""
    print("\n🚀 Starting API server...")
    
    try:
        # Start uvicorn server
        server_process = subprocess.Popen([
            sys.executable, '-m', 'uvicorn', 'api_architecture:app',
            '--host', '0.0.0.0',
            '--port', '8000',
            '--reload'
        ])
        
        # Wait for server to start
        time.sleep(5)
        
        # Check if server is running
        if server_process.poll() is None:
            print("✅ API server started successfully")
            return server_process
        else:
            print("❌ API server failed to start")
            return None
            
    except Exception as e:
        print(f"❌ Failed to start API server: {e}")
        return None

def start_ngrok_tunnel():
    """Start ngrok tunnel"""
    print("\n🌐 Starting ngrok tunnel...")
    
    try:
        # Start ngrok
        ngrok_process = subprocess.Popen([
            'ngrok', 'http', '8000', '--log=stdout', '--log-level=info'
        ], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        
        # Wait for ngrok to start
        time.sleep(5)
        
        # Check if ngrok is running
        if ngrok_process.poll() is not None:
            stdout, stderr = ngrok_process.communicate()
            print("❌ ngrok failed to start")
            print(f"stdout: {stdout}")
            print(f"stderr: {stderr}")
            return None, None
        
        # Get public URL
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
                        print(f"⏳ Waiting for tunnel... (attempt {attempt + 1}/10)")
                        time.sleep(2)
                else:
                    print(f"⏳ ngrok API not ready... (attempt {attempt + 1}/10)")
                    time.sleep(2)
            except requests.RequestException:
                print(f"⏳ ngrok API not responding... (attempt {attempt + 1}/10)")
                time.sleep(2)
        
        print("⚠️  ngrok started but couldn't get public URL")
        return ngrok_process, None
        
    except Exception as e:
        print(f"❌ Failed to start ngrok: {e}")
        return None, None

def test_api_endpoints(base_url):
    """Test API endpoints"""
    print(f"\n🧪 Testing API endpoints at {base_url}...")
    
    try:
        # Test health endpoint
        response = requests.get(f"{base_url}/health", timeout=5)
        if response.status_code == 200:
            print("✅ Health endpoint working")
        else:
            print("❌ Health endpoint failed")
            return False
        
        # Test score endpoint
        response = requests.post(f"{base_url}/api/score", 
                               json={"url": "https://example.com"}, 
                               timeout=10)
        if response.status_code == 200:
            print("✅ Score API working")
        else:
            print("❌ Score API failed")
            return False
        
        print("✅ All API endpoints are working")
        return True
        
    except Exception as e:
        print(f"❌ API test failed: {e}")
        return False

def main():
    """Main deployment function"""
    print("🚀 GEO Agent API Architecture Deployment")
    print("=" * 60)
    
    # Check dependencies
    if not check_dependencies():
        print("❌ Dependencies check failed")
        return
    
    # Setup ngrok
    use_ngrok = input("\nDo you want to use ngrok for public access? (y/n): ").lower().strip() == 'y'
    
    ngrok_process = None
    public_url = None
    
    if use_ngrok:
        if not setup_ngrok():
            print("❌ ngrok setup failed")
            use_ngrok = False
    
    # Start API server
    server_process = start_api_server()
    if not server_process:
        print("❌ Failed to start API server")
        return
    
    # Test local API
    print("\n🧪 Testing local API...")
    if not test_api_endpoints("http://localhost:8000"):
        print("❌ Local API test failed")
        server_process.terminate()
        return
    
    # Start ngrok if requested
    if use_ngrok:
        ngrok_process, public_url = start_ngrok_tunnel()
        if public_url:
            print(f"\n🧪 Testing public API at {public_url}...")
            if not test_api_endpoints(public_url):
                print("❌ Public API test failed")
    
    # Display final status
    print("\n" + "=" * 60)
    print("🎉 Deployment Complete!")
    print("=" * 60)
    print(f"📱 Local URL: http://localhost:8000")
    if public_url:
        print(f"🌍 Public URL: {public_url}")
    else:
        print("🌍 Public URL: Not available")
    print("📚 API Documentation: http://localhost:8000/docs")
    print("🔍 Interactive API: http://localhost:8000/redoc")
    print("=" * 60)
    print("\n🏗️  Available Endpoints:")
    print("   POST /api/score - Get score and markdown")
    print("   POST /api/ai-optimize - Start AI optimization")
    print("   GET /api/sse/{task_id} - Real-time updates")
    print("   GET /api/task/{task_id} - Get task status")
    print("   GET /api/tasks - List all tasks")
    print("=" * 60)
    print("\n🧪 Test the API:")
    print("   python test_architecture_client.py")
    print("=" * 60)
    print("\nPress Ctrl+C to stop the deployment")
    
    try:
        # Keep running
        while True:
            time.sleep(1)
            
            # Check if processes are still running
            if server_process.poll() is not None:
                print("❌ API server stopped unexpectedly")
                break
            
            if ngrok_process and ngrok_process.poll() is not None:
                print("❌ ngrok tunnel stopped unexpectedly")
                print("The API is still accessible locally at http://localhost:8000")
                break
                
    except KeyboardInterrupt:
        print("\n🛑 Shutting down deployment...")
    
    finally:
        # Clean up
        if server_process:
            server_process.terminate()
            server_process.wait()
        
        if ngrok_process:
            ngrok_process.terminate()
            ngrok_process.wait()
        
        print("✅ Deployment stopped")

if __name__ == "__main__":
    main() 