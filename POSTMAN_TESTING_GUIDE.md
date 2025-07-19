# 🚀 GEO Agent API - Postman Testing Guide

## 📋 **API Overview**

This API has two main endpoints:
- **`/api/score`**: Direct response (no SSE) - Get current score and markdown
- **`/api/optimize`**: SSE streaming - Start optimization and get real-time progress

## 🔧 **Setup**

### **1. Start the API**
```bash
python api_architecture_sse.py
```

### **2. API Base URL**
```
http://localhost:8000
```

## 📊 **Endpoint 1: /api/score (Direct Response)**

### **Request Details:**
- **Method**: `POST`
- **URL**: `http://localhost:8000/api/score`
- **Headers**: 
  ```
  Content-Type: application/json
  ```
- **Body** (raw JSON):
  ```json
  {
    "url": "https://example.com"
  }
  ```

### **Expected Response:**
```json
{
  "success": true,
  "message": "Score and markdown retrieved successfully",
  "data": {
    "url": "https://example.com",
    "score": 0.7500,
    "markdown": "# Example Website\n\nContent...",
    "html_length": 15000,
    "markdown_length": 500,
    "crawl_success": true
  },
  "timestamp": "2024-01-01T12:00:00"
}
```

### **Postman Setup:**
1. Create new request
2. Set method to `POST`
3. Set URL to `http://localhost:8000/api/score`
4. Add header: `Content-Type: application/json`
5. Set body to raw JSON with the request payload
6. Send request

## 🔄 **Endpoint 2: /api/optimize (SSE Streaming)**

### **Step 1: Start Optimization**

#### **Request Details:**
- **Method**: `POST`
- **URL**: `http://localhost:8000/api/optimize`
- **Headers**: 
  ```
  Content-Type: application/json
  ```
- **Body** (raw JSON):
  ```json
  {
    "url": "https://example.com",
    "target_keyword": "example website",
    "improvement_threshold": 0.02
  }
  ```

#### **Expected Response:**
```json
{
  "success": true,
  "message": "Optimization started successfully",
  "task_id": "optimize_task_1234567890_12345",
  "timestamp": "2024-01-01T12:00:00"
}
```

#### **Postman Setup:**
1. Create new request
2. Set method to `POST`
3. Set URL to `http://localhost:8000/api/optimize`
4. Add header: `Content-Type: application/json`
5. Set body to raw JSON with the request payload
6. Send request
7. **Save the `task_id` from the response**

### **Step 2: Connect to SSE Stream**

#### **Request Details:**
- **Method**: `GET`
- **URL**: `http://localhost:8000/api/sse/{task_id}`
  (Replace `{task_id}` with the actual task_id from step 1)
- **Headers**: 
  ```
  Accept: text/event-stream
  Cache-Control: no-cache
  ```

#### **Expected SSE Events:**
```
event: optimization_started
data: {"message": "Optimization started", "url": "https://example.com", "target_keyword": "example website", "timestamp": "2024-01-01T12:00:00"}

event: step
data: {"step": "crawling", "message": "Crawling website: https://example.com", "progress": 10}

event: step
data: {"step": "crawling_complete", "message": "Successfully crawled HTML (15000 characters)", "progress": 20}

event: step
data: {"step": "scoring", "message": "Getting initial score...", "progress": 30}

event: step
data: {"step": "scoring_complete", "message": "Initial score: 0.7500", "progress": 40, "initial_score": 0.75}

event: step
data: {"step": "optimization", "message": "Starting HTML optimization...", "progress": 50}

event: step
data: {"step": "optimization_complete", "message": "Optimization completed in 45.23 seconds", "progress": 90, "final_score": 0.8500, "improvement": 0.1000, "execution_time": 45.23}

event: optimization_complete
data: {"website_url": "https://example.com", "target_keyword": "example website", "initial_score": 0.75, "final_score": 0.85, "improvement": 0.1, "original_html": "<html>...</html>", "optimized_html": "<html>...</html>", "execution_time_seconds": 45.23, "optimization_summary": {...}, "similar_websites": [...]}

event: complete
data: {"message": "Optimization completed"}
```

#### **Postman Setup for SSE:**
1. Create new request
2. Set method to `GET`
3. Set URL to `http://localhost:8000/api/sse/{task_id}`
4. Add headers:
   ```
   Accept: text/event-stream
   Cache-Control: no-cache
   ```
5. **Important**: In Postman, go to the "Body" tab and select "None" (SSE doesn't need a body)
6. Send request
7. **Watch the response in real-time** - Postman will show the streaming events

## 🔍 **Additional Endpoints**

### **Get Task Status**
- **Method**: `GET`
- **URL**: `http://localhost:8000/api/task/{task_id}`
- **Response**: Task status and results

### **List All Tasks**
- **Method**: `GET`
- **URL**: `http://localhost:8000/api/tasks`
- **Response**: List of all optimization tasks

### **Health Check**
- **Method**: `GET`
- **URL**: `http://localhost:8000/health`
- **Response**: API health status

## 🧪 **Complete Testing Workflow**

### **Test 1: Score Endpoint**
1. Send POST to `/api/score`
2. Verify response contains score and markdown
3. Check that `crawl_success` is `true`

### **Test 2: Optimization with SSE**
1. Send POST to `/api/optimize` with URL and keyword
2. Extract `task_id` from response
3. Send GET to `/api/sse/{task_id}` to start SSE stream
4. Watch real-time progress events
5. Wait for `optimization_complete` event
6. Verify final results

### **Test 3: Task Status**
1. After optimization, send GET to `/api/task/{task_id}`
2. Verify task status is "completed"
3. Check final results

## ⚠️ **Important Notes**

### **SSE Testing in Postman:**
- Postman supports SSE natively
- Events will stream in real-time in the response body
- Each event has format: `event: {event_name}\ndata: {json_data}\n\n`
- Keep the connection open to receive all events

### **Error Handling:**
- If crawling fails, you'll get an error event
- If optimization fails, check the error message in the response
- Task status will show "failed" for unsuccessful optimizations

### **Performance:**
- Optimization can take 30-60 seconds
- SSE keeps connection alive with keepalive events
- Progress is shown from 10% to 90%

## 🎯 **Example Test Data**

### **Good Test URLs:**
```json
{
  "url": "https://example.com",
  "target_keyword": "example website"
}
```

```json
{
  "url": "https://httpbin.org/html",
  "target_keyword": "httpbin"
}
```

### **Test Keywords:**
- "website optimization"
- "digital marketing"
- "seo best practices"
- "web development"

## 🔧 **Troubleshooting**

### **Common Issues:**

1. **SSE not working in Postman:**
   - Make sure you're using the latest version of Postman
   - Check that headers are set correctly
   - Try refreshing the request

2. **Task not found:**
   - Verify the task_id is correct
   - Check that the optimization was started successfully

3. **Crawling failed:**
   - Try a different URL
   - Check if the website is accessible
   - Verify the URL format

4. **Optimization taking too long:**
   - This is normal for complex websites
   - Check the progress events in SSE
   - Wait for completion

## 📱 **Alternative Testing Tools**

### **Using curl:**
```bash
# Test score endpoint
curl -X POST http://localhost:8000/api/score \
  -H 'Content-Type: application/json' \
  -d '{"url": "https://example.com"}'

# Test optimization endpoint
curl -X POST http://localhost:8000/api/optimize \
  -H 'Content-Type: application/json' \
  -d '{"url": "https://example.com", "target_keyword": "example"}'

# Test SSE (replace TASK_ID)
curl -N http://localhost:8000/api/sse/TASK_ID
```

### **Using Python:**
```python
import requests
import json

# Test score endpoint
response = requests.post(
    "http://localhost:8000/api/score",
    json={"url": "https://example.com"}
)
print(response.json())

# Test optimization endpoint
response = requests.post(
    "http://localhost:8000/api/optimize",
    json={
        "url": "https://example.com",
        "target_keyword": "example website"
    }
)
task_id = response.json()["task_id"]
print(f"Task ID: {task_id}")
```

This guide should help you test all aspects of the API in Postman! 🎉 