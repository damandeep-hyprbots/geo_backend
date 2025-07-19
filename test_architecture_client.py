#!/usr/bin/env python3
"""
Test client for GEO Agent API Architecture
"""

import requests
import json
import time
import asyncio
import aiohttp
from typing import Dict, Any

class GEOArchitectureClient:
    """Client for GEO Agent API Architecture"""
    
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url.rstrip('/')
    
    def health_check(self) -> Dict[str, Any]:
        """Check API health"""
        try:
            response = requests.get(f"{self.base_url}/health")
            return response.json()
        except Exception as e:
            return {"error": str(e)}
    
    def get_score_and_markdown(self, url: str) -> Dict[str, Any]:
        """
        Get current score and markdown for a URL
        
        Frontend sends: URL
        Backend returns: Score + Markdown
        """
        try:
            payload = {
                "url": url
            }
            
            print(f"📊 Getting score and markdown for: {url}")
            
            response = requests.post(f"{self.base_url}/api/score", json=payload)
            return response.json()
            
        except Exception as e:
            return {"error": str(e)}
    
    def start_ai_optimization(self, url: str, html: str, markdown: str, score: float, target_keyword: str) -> Dict[str, Any]:
        """
        Start AI optimization
        
        Frontend sends: URL + HTML + Markdown + Score
        Backend returns: Task ID for SSE tracking
        """
        try:
            payload = {
                "url": url,
                "html": html,
                "markdown": markdown,
                "score": score,
                "target_keyword": target_keyword,
                "improvement_threshold": 0.02
            }
            
            print(f"🤖 Starting AI optimization for: {url}")
            print(f"Target keyword: {target_keyword}")
            print(f"Current score: {score}")
            
            response = requests.post(f"{self.base_url}/api/ai-optimize", json=payload)
            return response.json()
            
        except Exception as e:
            return {"error": str(e)}
    
    async def listen_to_sse(self, task_id: str):
        """
        Listen to Server-Sent Events for real-time updates
        
        Frontend connects to: /api/sse/{task_id}
        Backend streams: Real-time optimization events
        """
        print(f"🔗 Connecting to SSE stream for task: {task_id}")
        
        async with aiohttp.ClientSession() as session:
            async with session.get(f"{self.base_url}/api/sse/{task_id}") as response:
                async for line in response.content:
                    if line:
                        line_str = line.decode('utf-8').strip()
                        if line_str.startswith('data: '):
                            try:
                                data = json.loads(line_str[6:])  # Remove 'data: ' prefix
                                print(f"📡 SSE Event: {data}")
                                
                                # Handle different event types
                                if data.get('event') == 'optimization_complete':
                                    print("✅ Optimization completed!")
                                    return data
                                elif data.get('event') == 'error':
                                    print(f"❌ Error: {data}")
                                    return data
                                    
                            except json.JSONDecodeError:
                                print(f"⚠️  Invalid JSON in SSE: {line_str}")
    
    def get_task_status(self, task_id: str) -> Dict[str, Any]:
        """Get task status"""
        try:
            response = requests.get(f"{self.base_url}/api/task/{task_id}")
            return response.json()
        except Exception as e:
            return {"error": str(e)}
    
    def list_tasks(self) -> Dict[str, Any]:
        """List all tasks"""
        try:
            response = requests.get(f"{self.base_url}/api/tasks")
            return response.json()
        except Exception as e:
            return {"error": str(e)}

def test_score_api():
    """Test Score API"""
    print("🧪 Testing Score API")
    print("=" * 50)
    
    client = GEOArchitectureClient()
    
    # Test health
    health = client.health_check()
    print(f"Health check: {health}")
    
    # Test score API
    result = client.get_score_and_markdown("https://example.com")
    
    if result.get('success'):
        data = result.get('data', {})
        print(f"✅ Score API successful!")
        print(f"URL: {data.get('url')}")
        print(f"Score: {data.get('score', 0):.4f}")
        print(f"Markdown length: {len(data.get('markdown', ''))} characters")
        return data
    else:
        print("❌ Score API failed!")
        print(f"Error: {result.get('error', 'Unknown error')}")
        return None

def test_ai_optimization():
    """Test AI Optimization API"""
    print("\n🧪 Testing AI Optimization API")
    print("=" * 50)
    
    client = GEOArchitectureClient()
    
    # Sample data
    url = "https://example.com"
    html = "<html><head><title>Example</title></head><body><h1>Hello World</h1></body></html>"
    markdown = "# Hello World\n\nThis is an example page."
    score = 0.5
    target_keyword = "example website"
    
    # Start AI optimization
    result = client.start_ai_optimization(url, html, markdown, score, target_keyword)
    
    if result.get('success'):
        task_id = result.get('task_id')
        print(f"✅ AI optimization started!")
        print(f"Task ID: {task_id}")
        return task_id
    else:
        print("❌ AI optimization failed!")
        print(f"Error: {result.get('error', 'Unknown error')}")
        return None

async def test_sse_streaming(task_id: str):
    """Test SSE streaming"""
    print(f"\n🧪 Testing SSE Streaming for task: {task_id}")
    print("=" * 50)
    
    client = GEOArchitectureClient()
    
    # Listen to SSE events
    result = await client.listen_to_sse(task_id)
    
    if result:
        print("✅ SSE streaming completed!")
        return result
    else:
        print("❌ SSE streaming failed!")
        return None

def test_complete_workflow():
    """Test complete workflow"""
    print("\n🧪 Testing Complete Workflow")
    print("=" * 50)
    
    client = GEOArchitectureClient()
    
    # Step 1: Get score and markdown
    print("Step 1: Getting score and markdown...")
    score_data = test_score_api()
    
    if not score_data:
        print("❌ Failed to get score data")
        return
    
    # Step 2: Start AI optimization
    print("\nStep 2: Starting AI optimization...")
    task_id = test_ai_optimization()
    
    if not task_id:
        print("❌ Failed to start AI optimization")
        return
    
    # Step 3: Listen to SSE events
    print(f"\nStep 3: Listening to SSE events for task: {task_id}")
    
    # Run SSE test
    async def run_sse_test():
        return await test_sse_streaming(task_id)
    
    # Run the async function
    import asyncio
    result = asyncio.run(run_sse_test())
    
    if result:
        print("✅ Complete workflow successful!")
        print(f"Final result: {result}")
    else:
        print("❌ Complete workflow failed!")

def test_api_endpoints():
    """Test all API endpoints"""
    print("\n🧪 Testing All API Endpoints")
    print("=" * 50)
    
    client = GEOArchitectureClient()
    
    # Test health
    print("1. Testing health endpoint...")
    health = client.health_check()
    print(f"Health: {health}")
    
    # Test score API
    print("\n2. Testing score API...")
    score_result = client.get_score_and_markdown("https://example.com")
    print(f"Score API: {'success' if score_result.get('success') else 'failed'}")
    
    # Test AI optimization
    print("\n3. Testing AI optimization API...")
    ai_result = client.start_ai_optimization(
        "https://example.com",
        "<html><body>Test</body></html>",
        "# Test\n\nTest content.",
        0.5,
        "test keyword"
    )
    print(f"AI API: {'success' if ai_result.get('success') else 'failed'}")
    
    # Test task listing
    print("\n4. Testing task listing...")
    tasks = client.list_tasks()
    print(f"Tasks: {tasks.get('total', 0)} found")

def main():
    """Main test function"""
    print("🌐 GEO Agent API Architecture Test Client")
    print("=" * 50)
    
    # Test 1: Score API
    test_score_api()
    
    # Test 2: AI Optimization API
    task_id = test_ai_optimization()
    
    # Test 3: SSE Streaming (if task was created)
    if task_id:
        async def run_sse():
            await test_sse_streaming(task_id)
        
        asyncio.run(run_sse())
    
    # Test 4: Complete workflow
    test_complete_workflow()
    
    # Test 5: All endpoints
    test_api_endpoints()
    
    print("\n✅ All tests completed!")

if __name__ == "__main__":
    main() 