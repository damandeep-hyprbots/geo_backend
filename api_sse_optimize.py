#!/usr/bin/env python3
"""
GEO Agent API with SSE streaming on /api/optimize
- /api/score: Direct response (no SSE)
- /api/optimize: SSE streaming for real-time updates
"""

import json
import time
import traceback
import asyncio
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
    title="GEO Agent API - SSE Optimize",
    description="API with SSE streaming on optimize",
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

@app.get("/health")
async def health_check():
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}

@app.get("/")
async def root():
    return {"message": "GEO Agent API - SSE Optimize", "version": "1.0.0"}

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

@app.post("/api/optimize")
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

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8002)
