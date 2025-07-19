from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, HttpUrl
from typing import Optional, Dict, Any
import uvicorn
import asyncio
import json
import time
from datetime import datetime
import traceback

# Import the GEO agent
from geo_agent_enhanced import EnhancedGEOAgent, save_optimization_results

# Initialize FastAPI app
app = FastAPI(
    title="GEO Agent API",
    description="API for Generative Engine Optimization (GEO) Agent",
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
class OptimizationRequest(BaseModel):
    website_url: HttpUrl
    target_keyword: str
    improvement_threshold: Optional[float] = 0.02

class OptimizationResponse(BaseModel):
    success: bool
    message: str
    data: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    timestamp: str

class HealthResponse(BaseModel):
    status: str
    timestamp: str
    version: str

# Global storage for optimization results (in production, use a proper database)
optimization_results = {}

@app.get("/", response_model=HealthResponse)
async def root():
    """Health check endpoint"""
    return HealthResponse(
        status="healthy",
        timestamp=datetime.now().isoformat(),
        version="1.0.0"
    )

@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint"""
    return HealthResponse(
        status="healthy",
        timestamp=datetime.now().isoformat(),
        version="1.0.0"
    )

@app.post("/optimize", response_model=OptimizationResponse)
async def optimize_website(request: OptimizationRequest):
    """
    Optimize a website for a target keyword
    
    Args:
        request: OptimizationRequest containing website URL, target keyword, and improvement threshold
        
    Returns:
        OptimizationResponse with optimization results
    """
    try:
        print(f"\n🚀 Starting optimization for {request.website_url}")
        print(f"Target keyword: {request.target_keyword}")
        print(f"Improvement threshold: {request.improvement_threshold}")
        
        # Convert HttpUrl to string
        website_url = str(request.website_url)
        
        # Run optimization
        start_time = time.time()
        results = geo_agent.optimize_website(
            website_url=website_url,
            target_keyword=request.target_keyword,
            improvement_threshold=request.improvement_threshold
        )
        end_time = time.time()
        
        # Check for errors
        if 'error' in results:
            return OptimizationResponse(
                success=False,
                message="Optimization failed",
                error=results['error'],
                timestamp=datetime.now().isoformat()
            )
        
        # Add execution time to results
        results['execution_time_seconds'] = end_time - start_time
        results['timestamp'] = datetime.now().isoformat()
        
        # Store results with a unique ID
        result_id = f"{request.target_keyword}_{int(time.time())}"
        optimization_results[result_id] = results
        
        print(f"✅ Optimization completed in {results['execution_time_seconds']:.2f} seconds")
        
        return OptimizationResponse(
            success=True,
            message="Optimization completed successfully",
            data=results,
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

@app.get("/results/{result_id}")
async def get_optimization_result(result_id: str):
    """
    Get optimization results by ID
    
    Args:
        result_id: The ID of the optimization result
        
    Returns:
        The optimization results
    """
    if result_id not in optimization_results:
        raise HTTPException(status_code=404, detail="Result not found")
    
    return optimization_results[result_id]

@app.get("/results")
async def list_optimization_results():
    """
    List all optimization results
    
    Returns:
        List of all optimization result IDs and basic info
    """
    results_list = []
    for result_id, result in optimization_results.items():
        results_list.append({
            "result_id": result_id,
            "website_url": result.get("website_url", ""),
            "target_keyword": result.get("target_keyword", ""),
            "final_score": result.get("final_score", 0.0),
            "improvement": result.get("improvement", 0.0),
            "timestamp": result.get("timestamp", ""),
            "execution_time_seconds": result.get("execution_time_seconds", 0.0)
        })
    
    return {
        "total_results": len(results_list),
        "results": results_list
    }

@app.delete("/results/{result_id}")
async def delete_optimization_result(result_id: str):
    """
    Delete optimization result by ID
    
    Args:
        result_id: The ID of the optimization result to delete
        
    Returns:
        Success message
    """
    if result_id not in optimization_results:
        raise HTTPException(status_code=404, detail="Result not found")
    
    del optimization_results[result_id]
    return {"message": f"Result {result_id} deleted successfully"}

@app.post("/optimize/async")
async def optimize_website_async(request: OptimizationRequest, background_tasks: BackgroundTasks):
    """
    Start optimization asynchronously
    
    Args:
        request: OptimizationRequest containing website URL, target keyword, and improvement threshold
        background_tasks: FastAPI background tasks
        
    Returns:
        Response with task ID
    """
    try:
        # Generate task ID
        task_id = f"task_{request.target_keyword}_{int(time.time())}"
        
        # Add optimization task to background tasks
        background_tasks.add_task(
            run_optimization_async,
            task_id,
            str(request.website_url),
            request.target_keyword,
            request.improvement_threshold
        )
        
        return {
            "success": True,
            "message": "Optimization started asynchronously",
            "task_id": task_id,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        return OptimizationResponse(
            success=False,
            message="Failed to start async optimization",
            error=str(e),
            timestamp=datetime.now().isoformat()
        )

async def run_optimization_async(task_id: str, website_url: str, target_keyword: str, improvement_threshold: float):
    """
    Run optimization asynchronously
    
    Args:
        task_id: Unique task ID
        website_url: Website URL to optimize
        target_keyword: Target keyword
        improvement_threshold: Improvement threshold
    """
    try:
        print(f"🔄 Starting async optimization for task {task_id}")
        
        # Run optimization
        results = geo_agent.optimize_website(
            website_url=website_url,
            target_keyword=target_keyword,
            improvement_threshold=improvement_threshold
        )
        
        # Store results with task ID
        results['task_id'] = task_id
        results['timestamp'] = datetime.now().isoformat()
        optimization_results[task_id] = results
        
        print(f"✅ Async optimization completed for task {task_id}")
        
    except Exception as e:
        print(f"❌ Async optimization failed for task {task_id}: {e}")
        optimization_results[task_id] = {
            "task_id": task_id,
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }

@app.get("/status/{task_id}")
async def get_task_status(task_id: str):
    """
    Get status of async optimization task
    
    Args:
        task_id: The task ID to check
        
    Returns:
        Task status and results if available
    """
    if task_id not in optimization_results:
        return {
            "task_id": task_id,
            "status": "not_found",
            "message": "Task not found"
        }
    
    result = optimization_results[task_id]
    
    if 'error' in result:
        return {
            "task_id": task_id,
            "status": "failed",
            "error": result['error'],
            "timestamp": result.get('timestamp', '')
        }
    
    return {
        "task_id": task_id,
        "status": "completed",
        "result": result,
        "timestamp": result.get('timestamp', '')
    }

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000) 