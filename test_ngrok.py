#!/usr/bin/env python3
"""
Simple ngrok test script
"""

import subprocess
import time
import requests
import sys

def test_ngrok_basic():
    """Test basic ngrok functionality"""
    print("🧪 Testing ngrok basic functionality")
    print("=" * 50)
    
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
        return False
    
    # Check ngrok authentication
    try:
        result = subprocess.run(['ngrok', 'config', 'check'], capture_output=True, text=True)
        if result.returncode == 0:
            print("✅ ngrok is authenticated")
        else:
            print("❌ ngrok is not authenticated")
            print("You need to run: ngrok config add-authtoken YOUR_TOKEN")
            return False
    except Exception as e:
        print(f"❌ Error checking ngrok auth: {e}")
        return False
    
    return True

def test_ngrok_tunnel():
    """Test ngrok tunnel creation"""
    print("\n🧪 Testing ngrok tunnel creation")
    print("=" * 50)
    
    # Start a simple HTTP server on port 8080
    print("🚀 Starting test HTTP server on port 8080...")
    
    try:
        # Start a simple Python HTTP server
        server_process = subprocess.Popen([
            sys.executable, '-m', 'http.server', '8080'
        ], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        
        # Wait for server to start
        time.sleep(2)
        
        # Start ngrok tunnel
        print("🚀 Starting ngrok tunnel...")
        ngrok_process = subprocess.Popen([
            'ngrok', 'http', '8080', '--log=stdout'
        ], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        
        # Wait for ngrok to start
        print("⏳ Waiting for ngrok to start...")
        time.sleep(5)
        
        # Check if ngrok is running
        if ngrok_process.poll() is not None:
            stdout, stderr = ngrok_process.communicate()
            print("❌ ngrok failed to start")
            print(f"stdout: {stdout}")
            print(f"stderr: {stderr}")
            server_process.terminate()
            return False
        
        # Try to get the public URL
        print("🔍 Getting ngrok public URL...")
        for attempt in range(10):
            try:
                response = requests.get('http://localhost:4040/api/tunnels', timeout=3)
                if response.status_code == 200:
                    tunnels = response.json()
                    if tunnels.get('tunnels'):
                        public_url = tunnels['tunnels'][0]['public_url']
                        print(f"✅ ngrok tunnel created: {public_url}")
                        
                        # Test the tunnel
                        print("🧪 Testing tunnel...")
                        test_response = requests.get(public_url, timeout=5)
                        if test_response.status_code == 200:
                            print("✅ Tunnel is working!")
                        else:
                            print(f"⚠️  Tunnel returned status code: {test_response.status_code}")
                        
                        # Clean up
                        ngrok_process.terminate()
                        server_process.terminate()
                        return True
                    else:
                        print(f"⏳ Waiting for tunnel... (attempt {attempt + 1}/10)")
                        time.sleep(2)
                else:
                    print(f"⏳ ngrok API not ready... (attempt {attempt + 1}/10)")
                    time.sleep(2)
            except requests.RequestException:
                print(f"⏳ ngrok API not responding... (attempt {attempt + 1}/10)")
                time.sleep(2)
        
        print("❌ Failed to get ngrok URL after 10 attempts")
        ngrok_process.terminate()
        server_process.terminate()
        return False
        
    except Exception as e:
        print(f"❌ Error testing ngrok tunnel: {e}")
        return False

def main():
    """Main test function"""
    print("🌐 ngrok Test Script")
    print("=" * 50)
    
    # Test 1: Basic functionality
    if not test_ngrok_basic():
        print("\n❌ Basic ngrok test failed. Please fix ngrok installation/authentication.")
        return
    
    # Test 2: Tunnel creation
    if not test_ngrok_tunnel():
        print("\n❌ ngrok tunnel test failed.")
        print("This might be due to:")
        print("- Network connectivity issues")
        print("- ngrok service being down")
        print("- Firewall blocking ngrok")
        return
    
    print("\n✅ All ngrok tests passed!")
    print("ngrok is working correctly and can be used with the API.")

if __name__ == "__main__":
    main() 