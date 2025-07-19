#!/usr/bin/env python3
"""
Startup script for GEO Agent Simple API with optional ngrok hosting
"""

import os
import sys
import subprocess
import time
import requests
import json

def start_api_server():
    """Start the API server"""
    print("🚀 Starting GEO Agent Simple API...")
    print("=" * 50)
    
    try:
        # Start the API server
        process = subprocess.Popen([
            sys.executable, "api_architecture_simple.py"
        ], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        
        # Wait a moment for the server to start
        time.sleep(3)
        
        # Check if server is running
        try:
            response = requests.get("http://localhost:8000/health", timeout=5)
            if response.status_code == 200:
                print("✅ API server is running!")
                print("🌐 Local API URL: http://localhost:8000")
                print("📚 API Documentation: http://localhost:8000/docs")
                print("🔍 Health Check: http://localhost:8000/health")
                print("\n📋 Available endpoints:")
                print("- GET  /health - Health check")
                print("- POST /api/score - Get score and markdown")
                print("- POST /api/optimize - Optimize website")
                print("- GET  /api/info - API information")
                
                return process
            else:
                print(f"❌ Server responded with status {response.status_code}")
                return None
                
        except requests.exceptions.RequestException as e:
            print(f"❌ Could not connect to server: {e}")
            return None
            
    except Exception as e:
        print(f"❌ Error starting server: {e}")
        return None

def start_ngrok():
    """Start ngrok tunnel"""
    print("\n🌐 Starting ngrok tunnel...")
    
    try:
        # Start ngrok tunnel
        ngrok_process = subprocess.Popen([
            "ngrok", "http", "8000"
        ], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        
        # Wait for ngrok to start
        time.sleep(5)
        
        # Get ngrok public URL
        try:
            response = requests.get("http://localhost:4040/api/tunnels", timeout=5)
            if response.status_code == 200:
                tunnels = response.json()
                if tunnels.get('tunnels'):
                    public_url = tunnels['tunnels'][0]['public_url']
                    print(f"✅ Ngrok tunnel started!")
                    print(f"🌐 Public URL: {public_url}")
                    print(f"🔗 API URL: {public_url}")
                    print(f"📚 Documentation: {public_url}/docs")
                    print(f"🔍 Health Check: {public_url}/health")
                    return ngrok_process, public_url
                else:
                    print("❌ No ngrok tunnels found")
                    return None, None
            else:
                print(f"❌ Could not get ngrok tunnels: {response.status_code}")
                return None, None
                
        except requests.exceptions.RequestException as e:
            print(f"❌ Could not connect to ngrok API: {e}")
            return None, None
            
    except Exception as e:
        print(f"❌ Error starting ngrok: {e}")
        return None, None

def test_api(base_url):
    """Test the API with a simple request"""
    print(f"\n🧪 Testing API at {base_url}...")
    
    try:
        # Test health endpoint
        response = requests.get(f"{base_url}/health")
        if response.status_code == 200:
            print("✅ Health check passed")
        else:
            print(f"❌ Health check failed: {response.status_code}")
            return False
        
        # Test score endpoint
        response = requests.post(
            f"{base_url}/api/score",
            json={"url": "https://example.com"}
        )
        if response.status_code == 200:
            result = response.json()
            if result.get('success'):
                print("✅ Score endpoint working")
            else:
                print(f"❌ Score endpoint failed: {result.get('error')}")
                return False
        else:
            print(f"❌ Score endpoint failed: {response.status_code}")
            return False
        
        print("✅ API tests passed!")
        return True
        
    except Exception as e:
        print(f"❌ API test failed: {e}")
        return False

def ask_ngrok_usage():
    """Ask user if they want to use ngrok"""
    while True:
        response = input("Do you want to use ngrok for public access? (y/n): ").lower().strip()
        if response in ['y', 'yes']:
            return True
        elif response in ['n', 'no']:
            return False
        else:
            print("Please enter 'y' for yes or 'n' for no.")

def main():
    """Main function"""
    print("🌐 GEO Agent Simple API")
    print("=" * 50)
    
    # Start API server
    api_process = start_api_server()
    if not api_process:
        print("\n❌ Failed to start API server.")
        return
    
    # Ask about ngrok usage
    use_ngrok = ask_ngrok_usage()
    
    ngrok_process = None
    public_url = None
    
    if use_ngrok:
        # Start ngrok tunnel
        ngrok_process, public_url = start_ngrok()
        if not ngrok_process:
            print("\n❌ Failed to start ngrok tunnel.")
            print("Make sure ngrok is installed and authenticated.")
            print("Install ngrok: https://ngrok.com/download")
            print("Authenticate: ngrok authtoken YOUR_TOKEN")
            print("\nContinuing with local API only...")
            public_url = "http://localhost:8000"
        else:
            public_url = public_url
    else:
        print("\n✅ Running in local mode only.")
        public_url = "http://localhost:8000"
    
    # Test API
    if test_api(public_url):
        print("\n🎉 API is ready to use!")
        
        if use_ngrok and ngrok_process:
            print(f"\n🌐 Public API URL: {public_url}")
            print("\n📖 Quick usage examples:")
            print("1. Get score and markdown:")
            print(f"   curl -X POST {public_url}/api/score \\")
            print("     -H 'Content-Type: application/json' \\")
            print("     -d '{\"url\": \"https://example.com\"}'")
            print()
            print("2. Optimize website:")
            print(f"   curl -X POST {public_url}/api/optimize \\")
            print("     -H 'Content-Type: application/json' \\")
            print("     -d '{")
            print("       \"url\": \"https://example.com\",")
            print("       \"target_keyword\": \"example website\"")
            print("     }'")
            print()
            print("3. Python client usage:")
            print("   # Update base_url in simple_api_client.py to:")
            print(f"   # base_url = \"{public_url}\"")
            print()
            print("4. Ngrok dashboard:")
            print("   http://localhost:4040")
        else:
            print(f"\n🌐 Local API URL: {public_url}")
            print("\n📖 Quick usage examples:")
            print("1. Get score and markdown:")
            print(f"   curl -X POST {public_url}/api/score \\")
            print("     -H 'Content-Type: application/json' \\")
            print("     -d '{\"url\": \"https://example.com\"}'")
            print()
            print("2. Optimize website:")
            print(f"   curl -X POST {public_url}/api/optimize \\")
            print("     -H 'Content-Type: application/json' \\")
            print("     -d '{")
            print("       \"url\": \"https://example.com\",")
            print("       \"target_keyword\": \"example website\"")
            print("     }'")
            print()
            print("3. Run Python client:")
            print("   python simple_api_client.py")
    else:
        print("\n❌ API tests failed.")
    
    try:
        if ngrok_process:
            print("\n⏹️  Press Ctrl+C to stop both server and ngrok...")
        else:
            print("\n⏹️  Press Ctrl+C to stop the server...")
        
        # Keep processes running
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n⏹️  Stopping server...")
        api_process.terminate()
        if ngrok_process:
            ngrok_process.terminate()
            ngrok_process.wait()
        api_process.wait()
        print("✅ Server stopped.")

if __name__ == "__main__":
    main() 