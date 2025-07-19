from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, HttpUrl
from typing import Optional, Dict, Any, List
import uvicorn
import asyncio
import json
import time
from datetime import datetime
import traceback
from sse_starlette.sse import EventSourceResponse
import queue
import threading

# Import the GEO agent
from geo_agent_enhanced import EnhancedGEOAgent, extract_llm_readable_content
from website_similarity_analyzer import analyze_website_similarity

# Initialize FastAPI app
app = FastAPI(
    title="GEO Agent API - Architecture",
    description="API for Generative Engine Optimization (GEO) Agent with Score API, AI API, and SSE",
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

# Initialize the GEO agent
geo_agent = EnhancedGEOAgent()

# Request/Response models
class ScoreRequest(BaseModel):
    url: HttpUrl

class ScoreResponse(BaseModel):
    success: bool
    message: str
    data: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    timestamp: str

class AIOptimizationRequest(BaseModel):
    url: HttpUrl
    html: str
    markdown: str
    score: float
    target_keyword: str
    improvement_threshold: Optional[float] = 0.02

class AIOptimizationResponse(BaseModel):
    success: bool
    message: str
    task_id: Optional[str] = None
    error: Optional[str] = None
    timestamp: str

# Global storage for optimization tasks and results
optimization_tasks = {}
task_queues = {}

@app.get("/", response_model=Dict[str, str])
async def root():
    """Root endpoint"""
    return {
        "message": "GEO Agent API - Architecture",
        "version": "1.0.0",
        "endpoints": {
            "score": "/api/score",
            "ai_optimize": "/api/ai-optimize",
            "sse": "/api/sse/{task_id}"
        }
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "version": "1.0.0"
    }

@app.post("/api/score", response_model=ScoreResponse)
async def get_score_and_markdown(request: ScoreRequest):
    """
    Get current score and markdown content for a URL
    
    Frontend sends: URL
    Backend returns: Score + Markdown
    """
    try:
        print(f"📊 Getting score for URL: {request.url}")
        
        # Convert HttpUrl to string
        website_url = str(request.url)
        
        # Get similar websites and calculate score
        results = analyze_website_similarity(
            query="website optimization",  # Generic query for scoring
            website_url=website_url,
            max_similar_results=1
        )
        
        # Find our website in the results
        our_website = None
        for result in results:
            if result.get('is_your_website', False):
                our_website = result
                break
        
        if our_website:
            score = our_website.get('relevance_score', 0.0)
            markdown = our_website.get('extracted_content', '')
        else:
            score = 0.0
            markdown = "No content extracted"
        
        # Extract markdown content if not available
        if not markdown or markdown == "No content extracted":
            try:
                from webpage_reader import crawl_website, extract_llm_readable_content
                raw_html = crawl_website(website_url)
                if raw_html:
                    markdown = extract_llm_readable_content(url=website_url, html_content=raw_html)
                else:
                    markdown = "Failed to extract content"
            except Exception as e:
                markdown = f"Error extracting content: {str(e)}"
        
        response_data = {
            "url": website_url,
            "score": score,
            "markdown": markdown,
            "timestamp": datetime.now().isoformat()
        }
        
        print(f"✅ Score calculated: {score:.4f}")
        
        return ScoreResponse(
            success=True,
            message="Score and markdown retrieved successfully",
            data=response_data,
            timestamp=datetime.now().isoformat()
        )
        
    except Exception as e:
        error_msg = f"Error getting score: {str(e)}"
        print(f"❌ {error_msg}")
        print(traceback.format_exc())
        
        return ScoreResponse(
            success=False,
            message="Failed to get score and markdown",
            error=error_msg,
            timestamp=datetime.now().isoformat()
        )

@app.post("/api/ai-optimize", response_model=AIOptimizationResponse)
async def ai_optimize_website(request: AIOptimizationRequest, background_tasks: BackgroundTasks):
    """
    AI API to send (url+html+md+score) to AI for optimization
    
    Frontend sends: URL + HTML + Markdown + Score
    Backend starts: AI optimization process
    Returns: Task ID for SSE tracking
    """
    try:
        print(f"🤖 Starting AI optimization for {request.url}")
        print(f"Target keyword: {request.target_keyword}")
        print(f"Current score: {request.score}")
        
        # Generate unique task ID
        task_id = f"ai_task_{int(time.time())}_{hash(str(request.url))}"
        
        # Create queue for SSE events
        task_queue = queue.Queue()
        task_queues[task_id] = task_queue
        
        # Store task info
        optimization_tasks[task_id] = {
            "status": "starting",
            "url": str(request.url),
            "target_keyword": request.target_keyword,
            "original_score": request.score,
            "original_html": request.html,
            "original_markdown": request.markdown,
            "start_time": datetime.now().isoformat(),
            "events": []
        }
        
        # Add optimization task to background tasks
        background_tasks.add_task(
            run_ai_optimization,
            task_id,
            str(request.url),
            request.html,
            request.markdown,
            request.score,
            request.target_keyword,
            request.improvement_threshold
        )
        
        print(f"✅ AI optimization task started: {task_id}")
        
        return AIOptimizationResponse(
            success=True,
            message="AI optimization started successfully",
            task_id=task_id,
            timestamp=datetime.now().isoformat()
        )
        
    except Exception as e:
        error_msg = f"Error starting AI optimization: {str(e)}"
        print(f"❌ {error_msg}")
        print(traceback.format_exc())
        
        return AIOptimizationResponse(
            success=False,
            message="Failed to start AI optimization",
            error=error_msg,
            timestamp=datetime.now().isoformat()
        )

async def run_ai_optimization(
    task_id: str, 
    url: str, 
    html: str, 
    markdown: str, 
    score: float, 
    target_keyword: str, 
    improvement_threshold: float
):
    """
    Run AI optimization with SSE events
    """
    try:
        # Update task status
        optimization_tasks[task_id]["status"] = "running"
        task_queues[task_id].put({
            "event": "status",
            "data": {"status": "running", "message": "AI optimization started"}
        })
        
        # Send initial data event
        task_queues[task_id].put({
            "event": "initial_data",
            "data": {
                "url": url,
                "original_score": score,
                "target_keyword": target_keyword,
                "html_length": len(html),
                "markdown_length": len(markdown)
            }
        })
        
        # Run optimization using the GEO agent
        task_queues[task_id].put({
            "event": "optimization_start",
            "data": {"message": "Starting HTML optimization..."}
        })
        
        # Create a custom optimization function that sends SSE events
        results = await run_optimization_with_sse(task_id, url, target_keyword, improvement_threshold)
        
        # Send final results
        task_queues[task_id].put({
            "event": "optimization_complete",
            "data": {
                "final_score": results.get('final_score', 0.0),
                "improvement": results.get('improvement', 0.0),
                "optimized_html": results.get('optimized_html', ''),
                "original_html": results.get('original_html', ''),
                "execution_time": results.get('execution_time_seconds', 0.0)
            }
        })
        
        # Update task status
        optimization_tasks[task_id]["status"] = "completed"
        optimization_tasks[task_id]["results"] = results
        
        task_queues[task_id].put({
            "event": "status",
            "data": {"status": "completed", "message": "Optimization completed successfully"}
        })
        
        print(f"✅ AI optimization completed for task {task_id}")
        
    except Exception as e:
        error_msg = f"Error in AI optimization: {str(e)}"
        print(f"❌ {error_msg}")
        
        # Update task status
        optimization_tasks[task_id]["status"] = "failed"
        optimization_tasks[task_id]["error"] = error_msg
        
        task_queues[task_id].put({
            "event": "error",
            "data": {"error": error_msg}
        })

async def run_optimization_with_sse(task_id: str, url: str, target_keyword: str, improvement_threshold: float):
    """
    Run optimization with SSE events
    """
    start_time = time.time()
    
    try:
        # Initialize agent state
        initial_state = {
            "website_url": url,
            "target_keyword": target_keyword,
            "current_html": "",
            "original_html": "",
            "current_score": 0.0,
            "improvement_threshold": improvement_threshold,
            "optimization_history": [],
            "best_score": 0.0,
            "best_html": "",
            "similar_websites": [],
            "final_result": None
        }
        
        # Send initialization event
        task_queues[task_id].put({
            "event": "step",
            "data": {"step": "initialization", "message": "Initializing optimization..."}
        })
        
        # Get initial HTML
        from webpage_reader import crawl_website
        raw_html = crawl_website(url)
        if raw_html:
            initial_state['current_html'] = raw_html
            initial_state['original_html'] = raw_html
            
            task_queues[task_id].put({
                "event": "step",
                "data": {"step": "html_extraction", "message": f"Extracted HTML ({len(raw_html)} characters)"}
            })
        
        # Get initial score
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
        
        if our_website:
            initial_score = our_website.get('relevance_score', 0.0)
            initial_state['current_score'] = initial_score
            initial_state['best_score'] = initial_score
            
            task_queues[task_id].put({
                "event": "step",
                "data": {"step": "scoring", "message": f"Initial score: {initial_score:.4f}"}
            })
        
        # Run optimization workflow
        task_queues[task_id].put({
            "event": "step",
            "data": {"step": "optimization", "message": "Starting HTML optimization..."}
        })
        
        # Run the optimization workflow
        final_state = geo_agent.workflow.invoke(initial_state)
        
        end_time = time.time()
        execution_time = end_time - start_time
        
        # Prepare results
        results = {
            "website_url": url,
            "target_keyword": target_keyword,
            "initial_score": initial_state.get('current_score', 0.0),
            "final_score": final_state.get('best_score', 0.0),
            "improvement": final_state.get('best_score', 0.0) - initial_state.get('current_score', 0.0),
            "original_html": final_state.get('original_html', ''),
            "optimized_html": final_state.get('best_html', ''),
            "execution_time_seconds": execution_time,
            "timestamp": datetime.now().isoformat()
        }
        
        task_queues[task_id].put({
            "event": "step",
            "data": {"step": "finalization", "message": f"Optimization completed in {execution_time:.2f} seconds"}
        })
        
        return results
        
    except Exception as e:
        print(f"Error in optimization: {e}")
        return {
            "error": str(e),
            "website_url": url,
            "target_keyword": target_keyword
        }

@app.get("/api/sse/{task_id}")
async def sse_endpoint(task_id: str):
    """
    SSE endpoint for real-time optimization progress
    
    Frontend connects to: /api/sse/{task_id}
    Backend streams: Real-time optimization events
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
    uvicorn.run(app, host="0.0.0.0", port=8000) 