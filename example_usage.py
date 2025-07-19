#!/usr/bin/env python3
"""
Example usage of GEO Agent API Architecture using Python
"""

import requests
import json
import asyncio
import aiohttp
import time
from typing import Dict, Any

class GEOAgentAPI:
    """Python client for GEO Agent API Architecture"""
    
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
        Step 1: Get current score and markdown for a URL
        
        Args:
            url: Website URL to analyze
            
        Returns:
            Dict containing score and markdown
        """
        try:
            payload = {"url": url}
            
            print(f"📊 Getting score and markdown for: {url}")
            
            response = requests.post(f"{self.base_url}/api/score", json=payload)
            result = response.json()
            
            if result.get('success'):
                data = result.get('data', {})
                print(f"✅ Score: {data.get('score', 0):.4f}")
                print(f"✅ Markdown length: {len(data.get('markdown', ''))} characters")
                return data
            else:
                print(f"❌ Failed: {result.get('error', 'Unknown error')}")
                return None
                
        except Exception as e:
            print(f"❌ Error: {e}")
            return None
    
    def start_ai_optimization(self, url: str, html: str, markdown: str, score: float, target_keyword: str) -> str:
        """
        Step 2: Start AI optimization
        
        Args:
            url: Website URL
            html: Current HTML content
            markdown: Current markdown content
            score: Current score
            target_keyword: Target keyword for optimization
            
        Returns:
            Task ID for SSE tracking
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
            result = response.json()
            
            if result.get('success'):
                task_id = result.get('task_id')
                print(f"✅ AI optimization started! Task ID: {task_id}")
                return task_id
            else:
                print(f"❌ Failed: {result.get('error', 'Unknown error')}")
                return None
                
        except Exception as e:
            print(f"❌ Error: {e}")
            return None
    
    async def listen_to_sse(self, task_id: str):
        """
        Step 3: Listen to Server-Sent Events for real-time updates
        
        Args:
            task_id: Task ID from AI optimization
            
        Returns:
            Final optimization results
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

def example_1_basic_usage():
    """Example 1: Basic usage - Get score and markdown"""
    print("=" * 60)
    print("Example 1: Basic Usage - Get Score and Markdown")
    print("=" * 60)
    
    api = GEOAgentAPI()
    
    # Step 1: Get score and markdown
    result = api.get_score_and_markdown("https://example.com")
    
    if result:
        print(f"URL: {result.get('url')}")
        print(f"Score: {result.get('score', 0):.4f}")
        print(f"Markdown preview: {result.get('markdown', '')[:100]}...")
    else:
        print("Failed to get score and markdown")

def example_2_ai_optimization():
    """Example 2: AI optimization with sample data"""
    print("\n" + "=" * 60)
    print("Example 2: AI Optimization with Sample Data")
    print("=" * 60)
    
    api = GEOAgentAPI()
    
    # Sample data
    url = "https://example.com"
    html = """
    <html>
        <head>
            <title>Example Website</title>
            <meta name="description" content="An example website">
        </head>
        <body>
            <h1>Welcome to Example</h1>
            <p>This is an example website for testing.</p>
            <h2>About Us</h2>
            <p>We provide excellent services.</p>
        </body>
    </html>
    """
    markdown = """
    # Welcome to Example
    
    This is an example website for testing.
    
    ## About Us
    
    We provide excellent services.
    """
    score = 0.5
    target_keyword = "example website"
    
    # Start AI optimization
    task_id = api.start_ai_optimization(url, html, markdown, score, target_keyword)
    
    if task_id:
        print(f"Task ID: {task_id}")
        return task_id
    else:
        print("Failed to start AI optimization")
        return None

async def example_3_sse_listening(task_id: str):
    """Example 3: Listen to SSE events"""
    print("\n" + "=" * 60)
    print("Example 3: SSE Listening")
    print("=" * 60)
    
    api = GEOAgentAPI()
    
    # Listen to SSE events
    result = await api.listen_to_sse(task_id)
    
    if result:
        print("✅ SSE listening completed!")
        print(f"Final result: {result}")
        return result
    else:
        print("❌ SSE listening failed!")
        return None

async def example_4_complete_workflow():
    """Example 4: Complete workflow"""
    print("\n" + "=" * 60)
    print("Example 4: Complete Workflow")
    print("=" * 60)
    
    api = GEOAgentAPI()
    
    # Step 1: Get score and markdown
    print("Step 1: Getting score and markdown...")
    score_data = api.get_score_and_markdown("https://example.com")
    
    if not score_data:
        print("❌ Failed to get score data")
        return
    
    # Step 2: Start AI optimization
    print("\nStep 2: Starting AI optimization...")
    task_id = api.start_ai_optimization(
        score_data.get('url', 'https://example.com'),
        "<html><body>Sample HTML</body></html>",
        score_data.get('markdown', ''),
        score_data.get('score', 0.5),
        "example website"
    )
    
    if not task_id:
        print("❌ Failed to start AI optimization")
        return
    
    # Step 3: Listen to SSE events
    print(f"\nStep 3: Listening to SSE events for task: {task_id}")
    result = await api.listen_to_sse(task_id)
    
    if result:
        print("✅ Complete workflow successful!")
        print(f"Final result: {result}")
    else:
        print("❌ Complete workflow failed!")

def example_5_curl_equivalent():
    """Example 5: Show curl equivalent commands"""
    print("\n" + "=" * 60)
    print("Example 5: Curl Equivalent Commands")
    print("=" * 60)
    
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
    print()
    
    print("4. Get Task Status:")
    print("curl http://localhost:8000/api/task/TASK_ID")
    print()
    
    print("5. List All Tasks:")
    print("curl http://localhost:8000/api/tasks")

def example_6_javascript_equivalent():
    """Example 6: Show JavaScript equivalent"""
    print("\n" + "=" * 60)
    print("Example 6: JavaScript Equivalent")
    print("=" * 60)
    
    js_code = """
// JavaScript equivalent of the Python client

class GEOAgentAPI {
  constructor(baseUrl = 'http://localhost:8000') {
    this.baseUrl = baseUrl;
  }

  // Step 1: Get score and markdown
  async getScoreAndMarkdown(url) {
    const response = await fetch(`${this.baseUrl}/api/score`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ url })
    });
    return await response.json();
  }

  // Step 2: Start AI optimization
  async startAIOptimization(url, html, markdown, score, targetKeyword) {
    const response = await fetch(`${this.baseUrl}/api/ai-optimize`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        url, html, markdown, score, target_keyword: targetKeyword
      })
    });
    return await response.json();
  }

  // Step 3: Listen to SSE events
  listenToSSE(taskId, onEvent) {
    const eventSource = new EventSource(`${this.baseUrl}/api/sse/${taskId}`);
    
    eventSource.onmessage = function(event) {
      const data = JSON.parse(event.data);
      onEvent(data);
      
      if (data.event === 'optimization_complete') {
        eventSource.close();
      }
    };
    
    return eventSource;
  }
}

// Usage
const api = new GEOAgentAPI();

async function optimizeWebsite(url, targetKeyword) {
  // Step 1: Get current score and markdown
  const scoreResult = await api.getScoreAndMarkdown(url);
  const { score, markdown } = scoreResult.data;
  
  // Step 2: Start AI optimization
  const optimizationResult = await api.startAIOptimization(
    url, html, markdown, score, targetKeyword
  );
  const taskId = optimizationResult.task_id;
  
  // Step 3: Listen to real-time updates
  api.listenToSSE(taskId, (event) => {
    console.log('SSE Event:', event);
    
    if (event.event === 'optimization_complete') {
      console.log('Final optimized HTML:', event.optimized_html);
      console.log('Final score:', event.final_score);
    }
  });
}
"""
    
    print(js_code)

def main():
    """Main function to run all examples"""
    print("🌐 GEO Agent API Architecture - Python Examples")
    print("=" * 60)
    
    # Example 1: Basic usage
    example_1_basic_usage()
    
    # Example 2: AI optimization
    task_id = example_2_ai_optimization()
    
    # Example 3: SSE listening (if task was created)
    if task_id:
        asyncio.run(example_3_sse_listening(task_id))
    
    # Example 4: Complete workflow
    asyncio.run(example_4_complete_workflow())
    
    # Example 5: Curl equivalent
    example_5_curl_equivalent()
    
    # Example 6: JavaScript equivalent
    example_6_javascript_equivalent()
    
    print("\n" + "=" * 60)
    print("✅ All examples completed!")
    print("=" * 60)

if __name__ == "__main__":
    main() 