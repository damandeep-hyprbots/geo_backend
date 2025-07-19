#!/usr/bin/env python3
"""
Simple usage example of GEO Agent API Architecture
"""

import requests
import asyncio
import aiohttp
import json

def simple_usage():
    """Simple usage example"""
    
    # API base URL
    base_url = "http://localhost:8000"
    
    print("🌐 Simple GEO Agent API Usage")
    print("=" * 40)
    
    # Step 1: Get score and markdown
    print("Step 1: Getting score and markdown...")
    response = requests.post(f"{base_url}/api/score", 
                           json={"url": "https://example.com"})
    
    if response.status_code == 200:
        data = response.json()
        if data.get('success'):
            score_data = data.get('data', {})
            print(f"✅ Score: {score_data.get('score', 0):.4f}")
            print(f"✅ Markdown length: {len(score_data.get('markdown', ''))} chars")
        else:
            print(f"❌ Failed: {data.get('error')}")
            return
    else:
        print(f"❌ HTTP Error: {response.status_code}")
        return
    
    # Step 2: Start AI optimization
    print("\nStep 2: Starting AI optimization...")
    optimization_payload = {
        "url": "https://example.com",
        "html": "<html><body><h1>Example</h1><p>Content</p></body></html>",
        "markdown": "# Example\n\nContent",
        "score": score_data.get('score', 0.5),
        "target_keyword": "example website"
    }
    
    response = requests.post(f"{base_url}/api/ai-optimize", 
                           json=optimization_payload)
    
    if response.status_code == 200:
        data = response.json()
        if data.get('success'):
            task_id = data.get('task_id')
            print(f"✅ Task started: {task_id}")
            
            # Step 3: Listen to SSE (simplified)
            print(f"\nStep 3: Listening to SSE for task: {task_id}")
            asyncio.run(listen_to_sse(base_url, task_id))
        else:
            print(f"❌ Failed: {data.get('error')}")
    else:
        print(f"❌ HTTP Error: {response.status_code}")

async def listen_to_sse(base_url, task_id):
    """Listen to SSE events"""
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(f"{base_url}/api/sse/{task_id}") as response:
                async for line in response.content:
                    if line:
                        line_str = line.decode('utf-8').strip()
                        if line_str.startswith('data: '):
                            try:
                                data = json.loads(line_str[6:])
                                print(f"📡 Event: {data.get('event', 'unknown')}")
                                
                                if data.get('event') == 'optimization_complete':
                                    print("✅ Optimization completed!")
                                    print(f"Final score: {data.get('final_score', 0):.4f}")
                                    print(f"Improvement: {data.get('improvement', 0):.4f}")
                                    return
                                elif data.get('event') == 'error':
                                    print(f"❌ Error: {data}")
                                    return
                                    
                            except json.JSONDecodeError:
                                pass
    except Exception as e:
        print(f"❌ SSE Error: {e}")

def curl_examples():
    """Show curl equivalent commands"""
    print("\n" + "=" * 40)
    print("Curl Equivalent Commands")
    print("=" * 40)
    
    print("1. Health Check:")
    print("curl http://localhost:8000/health")
    print()
    
    print("2. Get Score and Markdown:")
    print("curl -X POST http://localhost:8000/api/score \\")
    print("  -H 'Content-Type: application/json' \\")
    print("  -d '{\"url\": \"https://example.com\"}'")
    print()
    
    print("3. Start AI Optimization:")
    print("curl -X POST http://localhost:8000/api/ai-optimize \\")
    print("  -H 'Content-Type: application/json' \\")
    print("  -d '{")
    print("    \"url\": \"https://example.com\",")
    print("    \"html\": \"<html><body>Test</body></html>\",")
    print("    \"markdown\": \"# Test\\n\\nContent.\",")
    print("    \"score\": 0.5,")
    print("    \"target_keyword\": \"test keyword\"")
    print("  }'")

if __name__ == "__main__":
    simple_usage()
    curl_examples() 