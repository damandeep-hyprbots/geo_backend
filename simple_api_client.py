#!/usr/bin/env python3
"""
Simple Python client for GEO Agent API - Direct Response Version
"""

import requests
import json
import time
from typing import Dict, Any, Optional

class GEOAgentSimpleAPI:
    """Simple Python client for GEO Agent API"""
    
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url.rstrip('/')
    
    def health_check(self) -> Dict[str, Any]:
        """Check API health"""
        try:
            response = requests.get(f"{self.base_url}/health")
            return response.json()
        except Exception as e:
            return {"error": str(e)}
    
    def get_score_and_markdown(self, url: str) -> Optional[Dict[str, Any]]:
        """
        Get score and markdown for a URL
        
        Args:
            url: Website URL to analyze
            
        Returns:
            Dict containing score and markdown data, or None if failed
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
    
    def optimize_website(self, url: str, target_keyword: str, improvement_threshold: float = 0.02) -> Optional[Dict[str, Any]]:
        """
        Optimize website for target keyword
        
        Args:
            url: Website URL to optimize
            target_keyword: Target keyword for optimization
            improvement_threshold: Minimum improvement required
            
        Returns:
            Dict containing optimization results, or None if failed
        """
        try:
            payload = {
                "url": url,
                "target_keyword": target_keyword,
                "improvement_threshold": improvement_threshold
            }
            
            print(f"🔧 Starting optimization for: {url}")
            print(f"Target keyword: {target_keyword}")
            print(f"Improvement threshold: {improvement_threshold}")
            
            start_time = time.time()
            
            response = requests.post(f"{self.base_url}/api/optimize", json=payload)
            result = response.json()
            
            end_time = time.time()
            request_time = end_time - start_time
            
            if result.get('success'):
                data = result.get('data', {})
                print(f"✅ Optimization completed in {request_time:.2f} seconds")
                print(f"Initial score: {data.get('initial_score', 0):.4f}")
                print(f"Final score: {data.get('final_score', 0):.4f}")
                print(f"Improvement: {data.get('improvement', 0):.4f}")
                print(f"Execution time: {data.get('execution_time_seconds', 0):.2f} seconds")
                return data
            else:
                print(f"❌ Failed: {result.get('error', 'Unknown error')}")
                return None
                
        except Exception as e:
            print(f"❌ Error: {e}")
            return None
    
    def get_api_info(self) -> Dict[str, Any]:
        """Get API information"""
        try:
            response = requests.get(f"{self.base_url}/api/info")
            return response.json()
        except Exception as e:
            return {"error": str(e)}

def example_1_basic_usage():
    """Example 1: Basic usage - Get score and markdown"""
    print("=" * 60)
    print("Example 1: Basic Usage - Get Score and Markdown")
    print("=" * 60)
    
    api = GEOAgentSimpleAPI()
    
    # Get score and markdown
    result = api.get_score_and_markdown("https://example.com")
    
    if result:
        print(f"URL: {result.get('url')}")
        print(f"Score: {result.get('score', 0):.4f}")
        print(f"HTML length: {result.get('html_length', 0)} characters")
        print(f"Markdown preview: {result.get('markdown', '')[:100]}...")
    else:
        print("Failed to get score and markdown")

def example_2_optimization():
    """Example 2: Website optimization"""
    print("\n" + "=" * 60)
    print("Example 2: Website Optimization")
    print("=" * 60)
    
    api = GEOAgentSimpleAPI()
    
    # Optimize website
    result = api.optimize_website(
        url="https://example.com",
        target_keyword="example website",
        improvement_threshold=0.02
    )
    
    if result:
        print(f"\nOptimization Results:")
        print(f"Website: {result.get('website_url')}")
        print(f"Target keyword: {result.get('target_keyword')}")
        print(f"Initial score: {result.get('initial_score', 0):.4f}")
        print(f"Final score: {result.get('final_score', 0):.4f}")
        print(f"Improvement: {result.get('improvement', 0):.4f}")
        print(f"Execution time: {result.get('execution_time_seconds', 0):.2f} seconds")
        
        # Show HTML comparison
        original_length = len(result.get('original_html', ''))
        optimized_length = len(result.get('optimized_html', ''))
        print(f"Original HTML length: {original_length} characters")
        print(f"Optimized HTML length: {optimized_length} characters")
        print(f"Length difference: {optimized_length - original_length} characters")
        
        # Show optimization summary
        summary = result.get('optimization_summary', {})
        print(f"Total steps: {summary.get('total_steps', 0)}")
        print(f"Successful steps: {summary.get('successful_steps', 0)}")
        print(f"Best improvement: {summary.get('best_improvement', 0):.4f}")
    else:
        print("Failed to optimize website")

def example_3_complete_workflow():
    """Example 3: Complete workflow"""
    print("\n" + "=" * 60)
    print("Example 3: Complete Workflow")
    print("=" * 60)
    
    api = GEOAgentSimpleAPI()
    
    # Step 1: Get current score and markdown
    print("Step 1: Getting current score and markdown...")
    score_data = api.get_score_and_markdown("https://example.com")
    
    if not score_data:
        print("❌ Failed to get score data")
        return
    
    # Step 2: Optimize website
    print("\nStep 2: Optimizing website...")
    optimization_result = api.optimize_website(
        url=score_data.get('url', 'https://example.com'),
        target_keyword="example website",
        improvement_threshold=0.02
    )
    
    if optimization_result:
        print("✅ Complete workflow successful!")
        print(f"Final score: {optimization_result.get('final_score', 0):.4f}")
        print(f"Improvement: {optimization_result.get('improvement', 0):.4f}")
    else:
        print("❌ Complete workflow failed!")

def example_4_curl_equivalent():
    """Example 4: Show curl equivalent commands"""
    print("\n" + "=" * 60)
    print("Example 4: Curl Equivalent Commands")
    print("=" * 60)
    
    print("1. Health Check:")
    print("curl http://localhost:8000/health")
    print()
    
    print("2. Get Score and Markdown:")
    print("curl -X POST http://localhost:8000/api/score \\")
    print("  -H 'Content-Type: application/json' \\")
    print("  -d '{\"url\": \"https://example.com\"}'")
    print()
    
    print("3. Optimize Website:")
    print("curl -X POST http://localhost:8000/api/optimize \\")
    print("  -H 'Content-Type: application/json' \\")
    print("  -d '{")
    print("    \"url\": \"https://example.com\",")
    print("    \"target_keyword\": \"example website\",")
    print("    \"improvement_threshold\": 0.02")
    print("  }'")
    print()
    
    print("4. Get API Info:")
    print("curl http://localhost:8000/api/info")

def example_5_javascript_equivalent():
    """Example 5: Show JavaScript equivalent"""
    print("\n" + "=" * 60)
    print("Example 5: JavaScript Equivalent")
    print("=" * 60)
    
    js_code = """
// JavaScript equivalent of the Python client

class GEOAgentSimpleAPI {
  constructor(baseUrl = 'http://localhost:8000') {
    this.baseUrl = baseUrl;
  }

  // Get score and markdown
  async getScoreAndMarkdown(url) {
    const response = await fetch(`${this.baseUrl}/api/score`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ url })
    });
    return await response.json();
  }

  // Optimize website
  async optimizeWebsite(url, targetKeyword, improvementThreshold = 0.02) {
    const response = await fetch(`${this.baseUrl}/api/optimize`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        url, target_keyword: targetKeyword, improvement_threshold: improvementThreshold
      })
    });
    return await response.json();
  }

  // Get API info
  async getApiInfo() {
    const response = await fetch(`${this.baseUrl}/api/info`);
    return await response.json();
  }
}

// Usage
const api = new GEOAgentSimpleAPI();

async function optimizeWebsite(url, targetKeyword) {
  // Step 1: Get current score and markdown
  const scoreResult = await api.getScoreAndMarkdown(url);
  if (scoreResult.success) {
    console.log('Current score:', scoreResult.data.score);
  }
  
  // Step 2: Optimize website
  const optimizationResult = await api.optimizeWebsite(url, targetKeyword);
  if (optimizationResult.success) {
    console.log('Final score:', optimizationResult.data.final_score);
    console.log('Improvement:', optimizationResult.data.improvement);
    console.log('Optimized HTML length:', optimizationResult.data.optimized_html.length);
  }
}

// Example usage
optimizeWebsite('https://example.com', 'example website');
"""
    
    print(js_code)

def main():
    """Main function to run all examples"""
    print("🌐 GEO Agent Simple API - Python Examples")
    print("=" * 60)
    
    # Example 1: Basic usage
    example_1_basic_usage()
    
    # Example 2: Optimization
    example_2_optimization()
    
    # Example 3: Complete workflow
    example_3_complete_workflow()
    
    # Example 4: Curl equivalent
    example_4_curl_equivalent()
    
    # Example 5: JavaScript equivalent
    example_5_javascript_equivalent()
    
    print("\n" + "=" * 60)
    print("✅ All examples completed!")
    print("=" * 60)

if __name__ == "__main__":
    main() 