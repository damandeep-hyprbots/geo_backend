#!/usr/bin/env python3
"""
Test client for GEO Agent API
"""

import requests
import json
import time
from typing import Dict, Any

class GEOAgentClient:
    """Client for GEO Agent API"""
    
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url.rstrip('/')
    
    def health_check(self) -> Dict[str, Any]:
        """Check API health"""
        try:
            response = requests.get(f"{self.base_url}/health")
            return response.json()
        except Exception as e:
            return {"error": str(e)}
    
    def optimize_website(self, website_url: str, target_keyword: str, improvement_threshold: float = 0.02) -> Dict[str, Any]:
        """Optimize a website for a target keyword"""
        try:
            payload = {
                "website_url": website_url,
                "target_keyword": target_keyword,
                "improvement_threshold": improvement_threshold
            }
            
            print(f"🚀 Starting optimization for {website_url}")
            print(f"Target keyword: {target_keyword}")
            
            response = requests.post(f"{self.base_url}/optimize", json=payload)
            return response.json()
            
        except Exception as e:
            return {"error": str(e)}
    
    def optimize_website_async(self, website_url: str, target_keyword: str, improvement_threshold: float = 0.02) -> Dict[str, Any]:
        """Start async optimization"""
        try:
            payload = {
                "website_url": website_url,
                "target_keyword": target_keyword,
                "improvement_threshold": improvement_threshold
            }
            
            print(f"🚀 Starting async optimization for {website_url}")
            print(f"Target keyword: {target_keyword}")
            
            response = requests.post(f"{self.base_url}/optimize/async", json=payload)
            return response.json()
            
        except Exception as e:
            return {"error": str(e)}
    
    def get_task_status(self, task_id: str) -> Dict[str, Any]:
        """Get status of async task"""
        try:
            response = requests.get(f"{self.base_url}/status/{task_id}")
            return response.json()
        except Exception as e:
            return {"error": str(e)}
    
    def get_results(self) -> Dict[str, Any]:
        """Get all optimization results"""
        try:
            response = requests.get(f"{self.base_url}/results")
            return response.json()
        except Exception as e:
            return {"error": str(e)}
    
    def get_result(self, result_id: str) -> Dict[str, Any]:
        """Get specific optimization result"""
        try:
            response = requests.get(f"{self.base_url}/results/{result_id}")
            return response.json()
        except Exception as e:
            return {"error": str(e)}

def test_sync_optimization():
    """Test synchronous optimization"""
    print("🧪 Testing Synchronous Optimization")
    print("=" * 50)
    
    client = GEOAgentClient()
    
    # Health check
    health = client.health_check()
    print(f"Health check: {health}")
    
    # Test optimization
    result = client.optimize_website(
        website_url="https://example.com",
        target_keyword="digital marketing",
        improvement_threshold=0.02
    )
    
    print(f"Optimization result: {json.dumps(result, indent=2)}")
    
    if result.get('success'):
        print("✅ Optimization completed successfully!")
        data = result.get('data', {})
        print(f"Final score: {data.get('final_score', 0):.4f}")
        print(f"Improvement: {data.get('improvement', 0):.4f}")
        print(f"Execution time: {data.get('execution_time_seconds', 0):.2f} seconds")
    else:
        print("❌ Optimization failed!")
        print(f"Error: {result.get('error', 'Unknown error')}")

def test_async_optimization():
    """Test asynchronous optimization"""
    print("\n🧪 Testing Asynchronous Optimization")
    print("=" * 50)
    
    client = GEOAgentClient()
    
    # Start async optimization
    result = client.optimize_website_async(
        website_url="https://example.com",
        target_keyword="SEO optimization",
        improvement_threshold=0.02
    )
    
    print(f"Async optimization started: {json.dumps(result, indent=2)}")
    
    if result.get('success'):
        task_id = result.get('task_id')
        print(f"Task ID: {task_id}")
        
        # Poll for status
        print("⏳ Polling for completion...")
        for i in range(30):  # Wait up to 5 minutes
            time.sleep(10)  # Check every 10 seconds
            
            status = client.get_task_status(task_id)
            print(f"Status check {i+1}: {status.get('status', 'unknown')}")
            
            if status.get('status') == 'completed':
                print("✅ Async optimization completed!")
                task_result = status.get('result', {})
                print(f"Final score: {task_result.get('final_score', 0):.4f}")
                print(f"Improvement: {task_result.get('improvement', 0):.4f}")
                break
            elif status.get('status') == 'failed':
                print("❌ Async optimization failed!")
                print(f"Error: {status.get('error', 'Unknown error')}")
                break
        else:
            print("⏰ Timeout waiting for completion")
    else:
        print("❌ Failed to start async optimization!")
        print(f"Error: {result.get('error', 'Unknown error')}")

def test_api_endpoints():
    """Test all API endpoints"""
    print("\n🧪 Testing All API Endpoints")
    print("=" * 50)
    
    client = GEOAgentClient()
    
    # Test health endpoint
    print("1. Testing health endpoint...")
    health = client.health_check()
    print(f"Health: {health}")
    
    # Test optimization
    print("\n2. Testing optimization endpoint...")
    result = client.optimize_website(
        website_url="https://example.com",
        target_keyword="web development",
        improvement_threshold=0.01
    )
    
    if result.get('success'):
        print("✅ Optimization successful")
        
        # Test results endpoint
        print("\n3. Testing results endpoint...")
        results = client.get_results()
        print(f"Total results: {results.get('total_results', 0)}")
        
        if results.get('results'):
            latest_result = results['results'][0]
            result_id = latest_result['result_id']
            
            # Test specific result endpoint
            print(f"\n4. Testing specific result endpoint for {result_id}...")
            specific_result = client.get_result(result_id)
            print(f"Result found: {'final_score' in specific_result}")
    
    else:
        print("❌ Optimization failed")
        print(f"Error: {result.get('error', 'Unknown error')}")

def main():
    """Main test function"""
    print("🌐 GEO Agent API Test Client")
    print("=" * 50)
    
    # Test 1: Sync optimization
    test_sync_optimization()
    
    # Test 2: Async optimization
    test_async_optimization()
    
    # Test 3: All endpoints
    test_api_endpoints()
    
    print("\n✅ All tests completed!")

if __name__ == "__main__":
    main() 