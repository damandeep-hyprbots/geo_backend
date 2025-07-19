#!/usr/bin/env python3
"""
Simplified GEO Agent API - No SSE, Direct Response
"""

import os
import json
import time
import traceback
from datetime import datetime
from typing import Dict, Any, Optional
from pydantic import BaseModel, HttpUrl
from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

# Import GEO Agent components
from geo_agent_enhanced import EnhancedGEOAgent
from website_similarity_analyzer import analyze_website_similarity
from webpage_reader import crawl_website, extract_llm_readable_content

# Load environment variables
load_dotenv()

# Initialize FastAPI app
app = FastAPI(
    title="GEO Agent API - Simple",
    description="Generative Engine Optimization Agent API - Direct Response Version",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize GEO Agent
geo_agent = EnhancedGEOAgent()

# Pydantic models for request/response
class ScoreRequest(BaseModel):
    url: HttpUrl

class ScoreResponse(BaseModel):
    success: bool
    message: str
    data: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    timestamp: str

class OptimizationRequest(BaseModel):
    url: HttpUrl
    target_keyword: str
    improvement_threshold: float = 0.02

class OptimizationResponse(BaseModel):
    success: bool
    message: str
    data: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    timestamp: str

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "GEO Agent API - Simple",
        "timestamp": datetime.now().isoformat()
    }

@app.post("/api/score", response_model=ScoreResponse)
async def get_score_and_markdown(request: ScoreRequest):
    """
    Score API: Get current score and markdown for a URL
    
    Frontend sends: URL
    Backend returns: Score + Markdown
    """
    try:
        print(f"📊 Getting score and markdown for: {request.url}")
        
        # Get initial HTML
        raw_html = crawl_website(str(request.url))
        if not raw_html:
            return ScoreResponse(
                success=False,
                message="Failed to crawl website",
                error="Could not retrieve HTML content",
                timestamp=datetime.now().isoformat()
            )
        
        # Extract markdown content
        markdown_content = extract_llm_readable_content(
            url=str(request.url), 
            html_content=raw_html
        )
        
        # Get similarity analysis and score
        results = analyze_website_similarity(
            query="website content",  # Generic query for scoring
            website_url=str(request.url),
            max_similar_results=1
        )
        
        # Find our website in results
        our_website = None
        for result in results:
            if result.get('is_your_website', False):
                our_website = result
                break
        
        score = our_website.get('relevance_score', 0.0) if our_website else 0.0
        
        data = {
            "url": str(request.url),
            "score": score,
            "markdown": markdown_content,
            "html_length": len(raw_html),
            "markdown_length": len(markdown_content)
        }
        
        print(f"✅ Score: {score:.4f}, Markdown length: {len(markdown_content)} chars")
        
        return ScoreResponse(
            success=True,
            message="Score and markdown retrieved successfully",
            data=data,
            timestamp=datetime.now().isoformat()
        )
        
    except Exception as e:
        error_msg = f"Error getting score and markdown: {str(e)}"
        print(f"❌ {error_msg}")
        print(traceback.format_exc())
        
        return ScoreResponse(
            success=False,
            message="Failed to get score and markdown",
            error=error_msg,
            timestamp=datetime.now().isoformat()
        )

@app.post("/api/optimize", response_model=OptimizationResponse)
async def optimize_website(request: OptimizationRequest):
    """
    Optimization API: Optimize website for target keyword
    
    Frontend sends: URL + Target Keyword
    Backend returns: Final optimization results
    """
    try:
        print(f"🔧 Starting optimization for: {request.url}")
        print(f"Target keyword: {request.target_keyword}")
        print(f"Improvement threshold: {request.improvement_threshold}")
        
        start_time = time.time()
        
        # Run the complete optimization workflow
        results = geo_agent.optimize_website(
            website_url=str(request.url),
            target_keyword=request.target_keyword,
            improvement_threshold=request.improvement_threshold
        )
        
        end_time = time.time()
        execution_time = end_time - start_time
        
        if 'error' in results:
            return OptimizationResponse(
                success=False,
                message="Optimization failed",
                error=results['error'],
                timestamp=datetime.now().isoformat()
            )
        
        # Prepare response data
        response_data = {
            "website_url": str(request.url),
            "target_keyword": request.target_keyword,
            "initial_score": results.get('initial_score', 0.0),
            "final_score": results.get('final_score', 0.0),
            "improvement": results.get('improvement', 0.0),
            "original_html": results.get('original_html', ''),
            "optimized_html": results.get('optimized_html', ''),
            "execution_time_seconds": execution_time,
            "optimization_summary": results.get('optimization_summary', {}),
            "similar_websites": results.get('similar_websites', [])
        }
        
        print(f"✅ Optimization completed in {execution_time:.2f} seconds")
        print(f"Initial score: {response_data['initial_score']:.4f}")
        print(f"Final score: {response_data['final_score']:.4f}")
        print(f"Improvement: {response_data['improvement']:.4f}")
        
        return OptimizationResponse(
            success=True,
            message="Optimization completed successfully",
            data=response_data,
            timestamp=datetime.now().isoformat()
        )
        
    except Exception as e:
        error_msg = f"Error during optimization: {str(e)}"
        print(f"❌ {error_msg}")
        print(traceback.format_exc())
        
        return OptimizationResponse(
            success=False,
            message="Optimization failed",
            error=error_msg,
            timestamp=datetime.now().isoformat()
        )

@app.get("/api/info")
async def get_api_info():
    """Get API information and endpoints"""
    return {
        "name": "GEO Agent API - Simple",
        "version": "1.0.0",
        "description": "Direct response API for website optimization",
        "endpoints": {
            "health": "GET /health - Health check",
            "score": "POST /api/score - Get score and markdown",
            "optimize": "POST /api/optimize - Optimize website",
            "info": "GET /api/info - API information"
        },
        "timestamp": datetime.now().isoformat()
    }

if __name__ == "__main__":
    import uvicorn
    print("🚀 Starting GEO Agent API - Simple")
    print("=" * 50)
    print("Endpoints:")
    print("- GET  /health - Health check")
    print("- POST /api/score - Get score and markdown")
    print("- POST /api/optimize - Optimize website")
    print("- GET  /api/info - API information")
    print("=" * 50)
    
    uvicorn.run(app, host="0.0.0.0", port=8000) 