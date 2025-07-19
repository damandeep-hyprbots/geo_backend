#!/usr/bin/env python3
"""
GEO Agent API with SSE streaming and ngrok integration
- /api/score: Direct response (no SSE)
- /api/optimize: SSE streaming for real-time updates
- Automatic ngrok tunnel for public access
"""

import json
import time
import traceback
import asyncio
import subprocess
import requests
import threading
from datetime import datetime
from typing import Dict, Any
from pydantic import BaseModel, HttpUrl
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from sse_starlette.sse import EventSourceResponse
from dotenv import load_dotenv

# Import GEO Agent components
from geo_agent_enhanced import EnhancedGEOAgent
from webpage_reader import crawl_website, extract_llm_readable_content
from website_similarity_analyzer import analyze_website_similarity

# Load environment variables
load_dotenv()

# Initialize FastAPI app
app = FastAPI(
    title="GEO Agent API - SSE Optimize with ngrok",
    description="API with SSE streaming on optimize and ngrok integration",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize GEO Agent
geo_agent = EnhancedGEOAgent()

# Global variables for ngrok
ngrok_process = None
public_url = None

# Pydantic models
class ScoreRequest(BaseModel):
    url: HttpUrl

class ScoreResponse(BaseModel):
    success: bool
    message: str
    data: Any = None
    error: str = None
    timestamp: str

class OptimizeRequest(BaseModel):
    url: HttpUrl
    html: str
    markdown: str
    score: float
    target_keyword: str
    improvement_threshold: float = 0.02

class OptimizeResponse(BaseModel):
    success: bool
    message: str
    original_html: str = None
    optimized_html: str = None
    updated_score: float = None
    error: str = None
    timestamp: str

def check_ngrok():
    """Check if ngrok is installed"""
    try:
        result = subprocess.run(['ngrok', 'version'], capture_output=True, text=True)
        if result.returncode == 0:
            return True
        else:
            return False
    except FileNotFoundError:
        return False

def start_ngrok_tunnel(port):
    """Start ngrok tunnel"""
    global ngrok_process, public_url
    try:
        print(f"🚀 Starting ngrok tunnel for port {port}...")
        ngrok_process = subprocess.Popen(
            ['ngrok', 'http', str(port), '--log=stdout'],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        
        # Wait for ngrok to start
        time.sleep(3)
        
        # Get the public URL
        try:
            response = requests.get('http://localhost:4040/api/tunnels')
            tunnels = response.json()
            if tunnels['tunnels']:
                public_url = tunnels['tunnels'][0]['public_url']
                print(f"✅ ngrok tunnel started: {public_url}")
                return True
            else:
                print("❌ No ngrok tunnels found")
                return False
        except Exception as e:
            print(f"❌ Error getting ngrok URL: {e}")
            return False
            
    except Exception as e:
        print(f"❌ Error starting ngrok: {e}")
        return False

@app.get("/health")
async def health_check():
    return {
        "status": "healthy", 
        "timestamp": datetime.now().isoformat(),
        "ngrok_url": public_url,
        "ngrok_active": public_url is not None
    }

@app.get("/")
async def root():
    return {
        "message": "GEO Agent API - SSE Optimize with ngrok",
        "version": "1.0.0",
        "ngrok_url": public_url,
        "endpoints": {
            "health": "GET /health - Health check with ngrok status",
            "score": "POST /api/score - Get score and markdown (direct response)",
            "optimize": "POST /api/optimize - SSE streaming for optimization",
            "ngrok_status": "GET /ngrok/status - Get ngrok tunnel status"
        }
    }

@app.get("/ngrok/status")
async def ngrok_status():
    """Get ngrok tunnel status"""
    return {
        "active": public_url is not None,
        "public_url": public_url,
        "local_port": 8002,
        "timestamp": datetime.now().isoformat()
    }

@app.post("/api/score", response_model=ScoreResponse)
async def get_score_and_markdown(request: ScoreRequest):
    try:
        url = str(request.url)
        raw_html = crawl_website(url)
        if not raw_html:
            return ScoreResponse(
                success=False,
                message="Failed to crawl website",
                error="Could not retrieve HTML content",
                timestamp=datetime.now().isoformat()
            )
        markdown = extract_llm_readable_content(url=url, html_content=raw_html)
        results = analyze_website_similarity(query="website content", website_url=url, max_similar_results=1)
        initial_score = next((r['relevance_score'] for r in results if r.get('is_your_website')), 0.0)
        data = {"url": url, "score": initial_score, "markdown": markdown}
        return ScoreResponse(
            success=True,
            message="Score and markdown retrieved successfully",
            data=data,
            timestamp=datetime.now().isoformat()
        )
    except Exception as e:
        return ScoreResponse(
            success=False,
            message="Failed to get score and markdown",
            error=str(e),
            timestamp=datetime.now().isoformat()
        )

@app.post("/api/optimize/v1")
async def optimize(request: OptimizeRequest):
    """
    SSE streaming endpoint: Start optimization and stream events in response
    Input: (url + html + markdown + score)
    Output: (original_html, optimized_html, updated_score)
    """
    url = str(request.url)
    html = request.html
    markdown = request.markdown
    initial_score = request.score
    keyword = request.target_keyword
    threshold = request.improvement_threshold

    async def event_generator():
        try:
            # Send initial event
            yield {
                "event": "start",
                "data": {
                    "message": "Optimization started",
                    "url": url,
                    "keyword": keyword,
                    "timestamp": datetime.now().isoformat()
                }
            }

            # Step: Validate inputs
            yield {
                "event": "step",
                "data": {
                    "step": "validation",
                    "message": "Validating inputs...",
                    "timestamp": datetime.now().isoformat()
                }
            }

            if not html or not markdown:
                yield {
                    "event": "error",
                    "data": {
                        "error": "HTML and markdown are required",
                        "timestamp": datetime.now().isoformat()
                    }
                }
                return

            yield {
                "event": "step",
                "data": {
                    "step": "validated",
                    "message": "Inputs validated",
                    "timestamp": datetime.now().isoformat()
                }
            }

            # Step: Optimization
            yield {
                "event": "step",
                "data": {
                    "step": "optimization",
                    "message": "Running optimization...",
                    "timestamp": datetime.now().isoformat()
                }
            }

            start_time = time.time()
            
            # Run optimization
            final_state = geo_agent.workflow.invoke({
                "website_url": url,
                "target_keyword": keyword,
                "current_html": html,
                "original_html": html,
                "current_score": initial_score,
                "improvement_threshold": threshold,
                "optimization_history": [],
                "best_score": initial_score,
                "best_html": html,
                "iteration_count": 0,
                "max_iterations": 5,
                "final_result": None
            })
            
            final_score = final_state.get('best_score', initial_score)
            optimized_html = final_state.get('best_html', html)
            original_html = final_state.get('original_html', html)
            improvement = final_score - initial_score
            elapsed = time.time() - start_time

            # Send keepalive during processing
            yield {
                "event": "keepalive",
                "data": {
                    "message": "Processing optimization...",
                    "timestamp": datetime.now().isoformat()
                }
            }

            # Final event with results
            yield {
                "event": "complete",
                "data": {
                    "original_html": original_html,
                    "optimized_html": optimized_html,
                    "updated_score": final_score,
                    "initial_score": initial_score,
                    "improvement": improvement,
                    "time": elapsed,
                    "timestamp": datetime.now().isoformat()
                }
            }

        except Exception as e:
            yield {
                "event": "error",
                "data": {
                    "error": str(e),
                    "timestamp": datetime.now().isoformat()
                }
            }

    # Return EventSourceResponse for proper SSE streaming
    return EventSourceResponse(event_generator())


@app.get("/api/optimize")
async def optimize(
    url: str = Query("https://www.hyperbots.com", description="Website URL"),
    html: str = Query(None, description="Base64-encoded HTML content"),
    markdown: str = Query(None, description="Base64-encoded Markdown content"),
    score: float = Query(0.00, description="Initial SEO/GEO score"),
    keyword: str = Query("Finance and Automation", description="Target keyword for optimization"),
    threshold: float = Query(0.01, description="Minimum score improvement threshold"),
):
    """
    SSE streaming endpoint using GET with query parameters (base64 encoded for HTML & Markdown).
    Input: url, html (b64), markdown (b64), score, keyword, threshold
    Output: SSE stream with start, step, complete, error events
    """

    try:
        initial_score = score
        html = base64.b64decode(html).decode("utf-8") if html else ""
        markdown = base64.b64decode(markdown).decode("utf-8") if markdown else ""

    except Exception as e:
        return EventSourceResponse(
            iter([{
                "event": "error",
                "data": {
                    "error": f"Invalid query params: {str(e)}",
                    "timestamp": datetime.now().isoformat()
                }
            }])
        )

    async def event_generator():
        try:
            # Send initial event
            yield {
                "event": "start",
                "data": json.dumps({
                    "message": "Optimization started",
                    "url": url,
                    "keyword": keyword,
                    "timestamp": datetime.now().isoformat()
                })
            }

            # Step: Validation
            yield {
                "event": "step",
                "data": json.dumps({
                    "step": "validation",
                    "message": "Validating inputs...",
                    "timestamp": datetime.now().isoformat()
                })
            }

            # if not html or not markdown:
            #     yield {
            #         "event": "error",
            #         "data": json.dumps({
            #             "error": "HTML and Markdown content are required",
            #             "timestamp": datetime.now().isoformat()
            #         })
            #     }
            #     return

            yield {
                "event": "step",
                "data": json.dumps({
                    "step": "validated",
                    "message": "Inputs validated",
                    "timestamp": datetime.now().isoformat()
                })
            }

            # Step: Optimization
            yield {
                "event": "step",
                "data": json.dumps({
                    "step": "optimization",
                    "message": "Running optimization...",
                    "timestamp": datetime.now().isoformat()
                })
            }

            start_time = time.time()

            # Perform the actual optimization using your agent
            final_state = geo_agent.workflow.invoke({
                "website_url": url,
                "target_keyword": keyword,
                "current_html": html,
                "original_html": html,
                "current_score": initial_score,
                "improvement_threshold": threshold,
                "optimization_history": [],
                "best_score": initial_score,
                "best_html": html,
                "iteration_count": 0,
                "max_iterations": 5,
                "final_result": None
            })

            final_score = final_state.get('best_score', initial_score)
            optimized_html = final_state.get('best_html', html)
            original_html = final_state.get('original_html', html)
            improvement = final_score - initial_score
            elapsed = time.time() - start_time

            # Keepalive (optional)
            yield {
                "event": "keepalive",
                "data": json.dumps({
                    "message": "Processing optimization...",
                    "timestamp": datetime.now().isoformat()
                })
            }

            # Final result
            yield {
                "event": "complete",
                "data": json.dumps({
                    "original_html": original_html,
                    "optimized_html": optimized_html,
                    "updated_score": final_score,
                    "initial_score": initial_score,
                    "improvement": improvement,
                    "time": elapsed,
                    "timestamp": datetime.now().isoformat()
                })
            }

        except Exception as e:
            yield {
                "event": "error",
                "data": json.dumps({
                    "error": str(e),
                    "timestamp": datetime.now().isoformat()
                })
            }

    return EventSourceResponse(event_generator())

def main():
    """Main function to start the API with ngrok"""
    import uvicorn
    
    print("🌐 GEO Agent API - SSE Optimize with ngrok")
    print("=" * 50)
    
    # Check if ngrok is available
    if check_ngrok():
        print("✅ ngrok is available")
        
        # Start ngrok tunnel
        if start_ngrok_tunnel(8002):
            print(f"\n🌐 Public URL: {public_url}")
            print(f"📊 API Documentation: {public_url}/docs")
            print(f"🔍 Health Check: {public_url}/health")
            print(f"📡 ngrok Status: {public_url}/ngrok/status")
            print("\n📋 Test Commands:")
            print(f"# Health check")
            print(f"curl {public_url}/health")
            print(f"\n# Score endpoint")
            print(f"curl -X POST {public_url}/api/score \\")
            print(f"  -H 'Content-Type: application/json' \\")
            print(f"  -d '{{\"url\": \"https://example.com\"}}'")
            print(f"\n# SSE optimization")
            print(f"curl -N -X POST {public_url}/api/optimize \\")
            print(f"  -H 'Content-Type: application/json' \\")
            print(f"  -d '{{")
            print(f"    \"url\": \"https://example.com\",")
            print(f"    \"html\": \"<html><body><h1>Test</h1></body></html>\",")
            print(f"    \"markdown\": \"# Test\\n\\nContent\",")
            print(f"    \"score\": 0.75,")
            print(f"    \"target_keyword\": \"test\"")
            print(f"  }}'")
            print("\n" + "=" * 50)
        else:
            print("❌ Failed to start ngrok tunnel")
    else:
        print("❌ ngrok is not installed")
        print("📦 To install ngrok:")
        print("1. Download from: https://ngrok.com/download")
        print("2. Extract and add to PATH")
        print("3. Run: ngrok authtoken YOUR_TOKEN")
    
    print("\n🚀 Starting API server...")
    print("Endpoints:")
    print("- GET  /health - Health check with ngrok status")
    print("- GET  /ngrok/status - Get ngrok tunnel status")
    print("- POST /api/score - Get score and markdown (direct response)")
    print("- POST /api/optimize - SSE streaming for optimization")
    print("=" * 50)
    
    try:
        uvicorn.run(app, host="0.0.0.0", port=8002)
    except KeyboardInterrupt:
        print("\n🛑 Shutting down...")
        if ngrok_process:
            ngrok_process.terminate()
            print("✅ ngrok tunnel stopped")

if __name__ == "__main__":
    main() 
