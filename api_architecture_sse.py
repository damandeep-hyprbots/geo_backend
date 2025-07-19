#!/usr/bin/env python3
"""
GEO Agent API with SSE for optimization
- /api/score: Direct response (no SSE)
- /api/optimize: SSE streaming for real-time updates
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
from fastapi.responses import StreamingResponse
from sse_starlette.sse import EventSourceResponse
import queue
import threading
import asyncio
from dotenv import load_dotenv

# Import GEO Agent components
from geo_agent_enhanced import EnhancedGEOAgent
from website_similarity_analyzer import analyze_website_similarity
from webpage_reader import crawl_website, extract_llm_readable_content

# Load environment variables
load_dotenv()

# Initialize FastAPI app
app = FastAPI(
    title="GEO Agent API - SSE Version",
    description="API with SSE streaming for optimization",
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

# Global storage for optimization tasks
optimization_tasks = {}
task_queues = {}

# Pydantic models
class ScoreRequest(BaseModel):
    url: HttpUrl

class ScoreResponse(BaseModel):
    success: bool
    message: str
    data: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    timestamp: str

class OptimizeRequest(BaseModel):
    url: HttpUrl
    target_keyword: str
    improvement_threshold: float = 0.02

class OptimizeResponse(BaseModel):
    success: bool
    message: str
    task_id: Optional[str] = None
    error: Optional[str] = None
    timestamp: str

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "GEO Agent API - SSE Version",
        "timestamp": datetime.now().isoformat()
    }

@app.get("/")
async def root():
    """Root endpoint with API information"""
    return {
        "message": "GEO Agent API - SSE Version",
        "version": "1.0.0",
        "endpoints": {
            "health": "GET /health - Health check",
            "score": "POST /api/score - Get score and markdown (direct response)",
            "optimize": "POST /api/optimize - Start optimization (returns task_id)",
            "sse": "GET /api/sse/{task_id} - SSE stream for optimization progress",
            "task_status": "GET /api/task/{task_id} - Get task status",
            "tasks": "GET /api/tasks - List all tasks"
        },
        "usage": {
            "step1": "POST /api/score with URL to get current score",
            "step2": "POST /api/optimize with URL and keyword to start optimization",
            "step3": "GET /api/sse/{task_id} to stream real-time progress",
            "step4": "GET /api/task/{task_id} to get final results"
        }
    }

@app.post("/api/score", response_model=ScoreResponse)
async def get_score_and_markdown(request: ScoreRequest):
    """
    Score API: Get current score and markdown for a URL
    Direct response (no SSE)
    
    Request: {"url": "https://example.com"}
    Response: {"success": true, "data": {"score": 0.75, "markdown": "..."}}
    """
    try:
        print(f"📊 Getting score and markdown for: {request.url}")
        
        # Convert HttpUrl to string
        website_url = str(request.url)
        
        # Step 1: Crawl the website
        print(f"🔄 Crawling website: {website_url}")
        raw_html = crawl_website(website_url)
        
        if not raw_html:
            return ScoreResponse(
                success=False,
                message="Failed to crawl website",
                error="Could not retrieve HTML content",
                timestamp=datetime.now().isoformat()
            )
        
        print(f"✅ Successfully crawled HTML ({len(raw_html)} characters)")
        
        # Step 2: Extract markdown content
        print(f"📝 Extracting markdown content...")
        markdown_content = extract_llm_readable_content(
            url=website_url, 
            html_content=raw_html
        )
        
        print(f"✅ Extracted markdown ({len(markdown_content)} characters)")
        
        # Step 3: Get similarity analysis and score
        print(f"🎯 Analyzing website similarity...")
        results = analyze_website_similarity(
            query="website content",  # Generic query for scoring
            website_url=website_url,
            max_similar_results=1
        )
        
        # Find our website in results
        our_website = None
        for result in results:
            if result.get('is_your_website', False):
                our_website = result
                break
        
        score = our_website.get('relevance_score', 0.0) if our_website else 0.0
        
        # Prepare response data
        data = {
            "url": website_url,
            "score": score,
            "markdown": markdown_content,
            "html_length": len(raw_html),
            "markdown_length": len(markdown_content),
            "crawl_success": True
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

@app.post("/api/optimize", response_model=OptimizeResponse)
async def start_optimization(request: OptimizeRequest, background_tasks: BackgroundTasks):
    """
    Optimization API: Start optimization process
    Returns task_id for SSE tracking
    
    Request: {"url": "https://example.com", "target_keyword": "example", "improvement_threshold": 0.02}
    Response: {"success": true, "task_id": "task_123", "message": "Optimization started"}
    """
    try:
        print(f"🔧 Starting optimization for: {request.url}")
        print(f"Target keyword: {request.target_keyword}")
        print(f"Improvement threshold: {request.improvement_threshold}")
        
        # Generate unique task ID
        task_id = f"optimize_task_{int(time.time())}_{hash(str(request.url))}"
        
        # Create queue for SSE events
        task_queue = queue.Queue()
        task_queues[task_id] = task_queue
        
        # Store task info
        optimization_tasks[task_id] = {
            "status": "starting",
            "url": str(request.url),
            "target_keyword": request.target_keyword,
            "improvement_threshold": request.improvement_threshold,
            "start_time": datetime.now().isoformat(),
            "events": []
        }
        
        # Add optimization task to background tasks
        background_tasks.add_task(
            run_optimization_with_sse,
            task_id,
            str(request.url),
            request.target_keyword,
            request.improvement_threshold
        )
        
        print(f"✅ Optimization task started: {task_id}")
        
        return OptimizeResponse(
            success=True,
            message="Optimization started successfully",
            task_id=task_id,
            timestamp=datetime.now().isoformat()
        )
        
    except Exception as e:
        error_msg = f"Error starting optimization: {str(e)}"
        print(f"❌ {error_msg}")
        print(traceback.format_exc())
        
        return OptimizeResponse(
            success=False,
            message="Failed to start optimization",
            error=error_msg,
            timestamp=datetime.now().isoformat()
        )

async def run_optimization_with_sse(task_id: str, url: str, target_keyword: str, improvement_threshold: float):
    """
    Run optimization with SSE events
    """
    start_time = time.time()
    
    try:
        # Update task status
        optimization_tasks[task_id]["status"] = "running"
        
        # Send initial event
        task_queues[task_id].put({
            "event": "optimization_started",
            "data": {
                "message": "Optimization started",
                "url": url,
                "target_keyword": target_keyword,
                "timestamp": datetime.now().isoformat()
            }
        })
        
        # Step 1: Crawl website
        task_queues[task_id].put({
            "event": "step",
            "data": {
                "step": "crawling",
                "message": f"Crawling website: {url}",
                "progress": 10
            }
        })
        
        raw_html = crawl_website(url)
        if not raw_html:
            raise Exception("Failed to crawl website")
        
        task_queues[task_id].put({
            "event": "step",
            "data": {
                "step": "crawling_complete",
                "message": f"Successfully crawled HTML ({len(raw_html)} characters)",
                "progress": 20
            }
        })
        
        # Step 2: Get initial score
        task_queues[task_id].put({
            "event": "step",
            "data": {
                "step": "scoring",
                "message": "Getting initial score...",
                "progress": 30
            }
        })
        
        results = analyze_website_similarity(
            query=target_keyword,
            website_url=url,
            max_similar_results=1
        )
        
        our_website = None
        for result in results:
            if result.get('is_your_website', False):
                our_website = result
                break
        
        initial_score = our_website.get('relevance_score', 0.0) if our_website else 0.0
        
        task_queues[task_id].put({
            "event": "step",
            "data": {
                "step": "scoring_complete",
                "message": f"Initial score: {initial_score:.4f}",
                "progress": 40,
                "initial_score": initial_score
            }
        })
        
        # Step 3: Run optimization
        task_queues[task_id].put({
            "event": "step",
            "data": {
                "step": "optimization",
                "message": "Starting HTML optimization...",
                "progress": 50
            }
        })
        
        # Run the optimization workflow
        final_state = geo_agent.workflow.invoke({
            "website_url": url,
            "target_keyword": target_keyword,
            "current_html": raw_html,
            "original_html": raw_html,
            "current_score": initial_score,
            "improvement_threshold": improvement_threshold,
            "optimization_history": [],
            "best_score": initial_score,
            "best_html": raw_html,
            "similar_websites": results,
            "final_result": None
        })
        
        end_time = time.time()
        execution_time = end_time - start_time
        
        # Step 4: Prepare final results
        final_score = final_state.get('best_score', initial_score)
        improvement = final_score - initial_score
        
        task_queues[task_id].put({
            "event": "step",
            "data": {
                "step": "optimization_complete",
                "message": f"Optimization completed in {execution_time:.2f} seconds",
                "progress": 90,
                "final_score": final_score,
                "improvement": improvement,
                "execution_time": execution_time
            }
        })
        
        # Step 5: Send final results
        final_results = {
            "website_url": url,
            "target_keyword": target_keyword,
            "initial_score": initial_score,
            "final_score": final_score,
            "improvement": improvement,
            "original_html": final_state.get('original_html', ''),
            "optimized_html": final_state.get('best_html', ''),
            "execution_time_seconds": execution_time,
            "optimization_summary": final_state.get('final_result', {}).get('optimization_summary', {}),
            "similar_websites": results
        }
        
        task_queues[task_id].put({
            "event": "optimization_complete",
            "data": final_results
        })
        
        # Update task status
        optimization_tasks[task_id]["status"] = "completed"
        optimization_tasks[task_id]["results"] = final_results
        
        print(f"✅ Optimization completed for task {task_id}")
        
    except Exception as e:
        error_msg = f"Error in optimization: {str(e)}"
        print(f"❌ {error_msg}")
        print(traceback.format_exc())
        
        # Update task status
        optimization_tasks[task_id]["status"] = "failed"
        optimization_tasks[task_id]["error"] = error_msg
        
        task_queues[task_id].put({
            "event": "error",
            "data": {"error": error_msg}
        })

@app.get("/api/sse/{task_id}")
async def sse_endpoint(task_id: str):
    """
    SSE endpoint for real-time optimization progress
    
    Connect to: GET /api/sse/{task_id}
    Streams: Real-time optimization events
    """
    if task_id not in task_queues:
        raise HTTPException(status_code=404, detail="Task not found")
    
    async def event_generator():
        queue = task_queues[task_id]
        
        try:
            while True:
                try:
                    # Get event from queue with timeout
                    event_data = queue.get(timeout=1)
                    
                    yield {
                        "event": event_data["event"],
                        "data": json.dumps(event_data["data"]),
                        "timestamp": datetime.now().isoformat()
                    }
                    
                    # If optimization is complete, send final event and break
                    if event_data["event"] == "optimization_complete":
                        yield {
                            "event": "complete",
                            "data": json.dumps({"message": "Optimization completed"}),
                            "timestamp": datetime.now().isoformat()
                        }
                        break
                        
                except queue.Empty:
                    # Send keepalive
                    yield {
                        "event": "keepalive",
                        "data": json.dumps({"message": "Still processing..."}),
                        "timestamp": datetime.now().isoformat()
                    }
                    
        except Exception as e:
            yield {
                "event": "error",
                "data": json.dumps({"error": str(e)}),
                "timestamp": datetime.now().isoformat()
            }
    
    return EventSourceResponse(event_generator())

@app.get("/api/task/{task_id}")
async def get_task_status(task_id: str):
    """Get task status and results"""
    if task_id not in optimization_tasks:
        raise HTTPException(status_code=404, detail="Task not found")
    
    return optimization_tasks[task_id]

@app.get("/api/tasks")
async def list_tasks():
    """List all optimization tasks"""
    tasks = []
    for task_id, task in optimization_tasks.items():
        tasks.append({
            "task_id": task_id,
            "status": task.get("status", "unknown"),
            "url": task.get("url", ""),
            "target_keyword": task.get("target_keyword", ""),
            "start_time": task.get("start_time", ""),
            "error": task.get("error", None)
        })
    
    return {"tasks": tasks, "total": len(tasks)}

if __name__ == "__main__":
    import uvicorn
    print("🚀 Starting GEO Agent API - SSE Version")
    print("=" * 50)
    print("Endpoints:")
    print("- GET  /health - Health check")
    print("- POST /api/score - Get score and markdown (direct response)")
    print("- POST /api/optimize - Start optimization (returns task_id)")
    print("- GET  /api/sse/{task_id} - SSE stream for optimization progress")
    print("- GET  /api/task/{task_id} - Get task status")
    print("- GET  /api/tasks - List all tasks")
    print("=" * 50)
    
    uvicorn.run(app, host="0.0.0.0", port=8000) 