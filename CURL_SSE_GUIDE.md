# 🚀 Curl Guide for SSE Testing

## 📋 **Quick Start**

### **1. Start the API**
```bash
python api_sse_optimize.py
```

### **2. Test Score Endpoint (Direct Response)**
```bash
curl -X POST http://localhost:8001/api/score \
  -H 'Content-Type: application/json' \
  -d '{"url": "https://example.com"}'
```

### **3. Test Optimization with SSE**

#### **Step 1: Start Optimization**
```bash
curl -X POST http://localhost:8001/api/optimize \
  -H 'Content-Type: application/json' \
  -d '{
    "url": "https://example.com",
    "html": "<html><head><title>Example</title></head><body><h1>Example Website</h1><p>This is an example website for testing.</p></body></html>",
    "markdown": "# Example Website\n\nThis is an example website for testing.",
    "score": 0.75,
    "target_keyword": "example website",
    "improvement_threshold": 0.02
  }'
```

**Expected Response:**
```json
{
  "success": true,
  "message": "Optimization started successfully",
  "task_id": "optimize_task_1234567890_12345",
  "timestamp": "2024-01-01T12:00:00"
}
```

#### **Step 2: Connect to SSE Stream**
```bash
# Replace TASK_ID with the actual task_id from step 1
curl -N http://localhost:8001/api/sse/TASK_ID
```

## 📊 **SSE Events You'll See**

```
event: start
data: {"message": "Optimization started", "url": "https://example.com", "keyword": "example website"}

event: step
data: {"step": "validation", "message": "Validating inputs..."}

event: step
data: {"step": "validated", "message": "Inputs validated"}

event: step
data: {"step": "optimization", "message": "Running optimization..."}

event: complete
data: {"original_html": "<html>...</html>", "optimized_html": "<html>...</html>", "updated_score": 0.8500, "initial_score": 0.7500, "improvement": 0.1000, "time": 45.23}
```

## 🔧 **Complete End-to-End Test**

### **Option 1: Manual Step-by-Step**
```bash
# 1. Health check
curl http://localhost:8001/health

# 2. Get score
curl -X POST http://localhost:8001/api/score \
  -H 'Content-Type: application/json' \
  -d '{"url": "https://example.com"}'

# 3. Start optimization with payload
curl -X POST http://localhost:8001/api/optimize \
  -H 'Content-Type: application/json' \
  -d '{
    "url": "https://example.com",
    "html": "<html><head><title>Example</title></head><body><h1>Example Website</h1><p>This is an example website for testing.</p></body></html>",
    "markdown": "# Example Website\n\nThis is an example website for testing.",
    "score": 0.75,
    "target_keyword": "example website"
  }'

# 4. Connect to SSE (replace TASK_ID)
curl -N http://localhost:8001/api/sse/TASK_ID
```

### **Option 2: Automated Script**
```bash
# Run the automated test script
./test_api_curl.sh
```

## 🎯 **Quick Test Commands**

### **Test Score Only:**
```bash
curl -X POST http://localhost:8001/api/score \
  -H 'Content-Type: application/json' \
  -d '{"url": "https://httpbin.org/html"}'
```

### **Test Optimization Only:**
```bash
# Start optimization with sample data
curl -X POST http://localhost:8001/api/optimize \
  -H 'Content-Type: application/json' \
  -d '{
    "url": "https://httpbin.org/html",
    "html": "<html><head><title>HTTPBin</title></head><body><h1>HTTPBin</h1><p>HTTPBin provides HTTP Request & Response Service.</p></body></html>",
    "markdown": "# HTTPBin\n\nHTTPBin provides HTTP Request & Response Service.",
    "score": 0.65,
    "target_keyword": "httpbin"
  }'
```

### **Test with Different URLs:**
```bash
# Test with different URLs
curl -X POST http://localhost:8001/api/optimize \
  -H 'Content-Type: application/json' \
  -d '{
    "url": "https://httpbin.org/html",
    "html": "<html><head><title>HTTPBin</title></head><body><h1>HTTPBin</h1><p>HTTPBin provides HTTP Request & Response Service.</p></body></html>",
    "markdown": "# HTTPBin\n\nHTTPBin provides HTTP Request & Response Service.",
    "score": 0.65,
    "target_keyword": "httpbin"
  }'

curl -X POST http://localhost:8001/api/optimize \
  -H 'Content-Type: application/json' \
  -d '{
    "url": "https://example.com",
    "html": "<html><head><title>Example</title></head><body><h1>Example Website</h1><p>This is an example website for testing.</p></body></html>",
    "markdown": "# Example Website\n\nThis is an example website for testing.",
    "score": 0.75,
    "target_keyword": "example website"
  }'
```

## ⚠️ **Important Notes**

### **Payload Structure:**
- **Input:** `(url + html + markdown + score)`
- **Output:** `(original_html, optimized_html, updated_score)`

### **Required Fields:**
- `url`: The website URL
- `html`: The original HTML content
- `markdown`: The markdown content
- `score`: The initial score (float)
- `target_keyword`: The keyword to optimize for
- `improvement_threshold`: Optional, defaults to 0.02

### **SSE Testing:**
- Use `curl -N` for SSE (no buffering)
- Keep the connection open to receive all events
- Events stream in real-time
- Press Ctrl+C to stop SSE stream

### **Error Handling:**
```bash
# If validation fails
curl -X POST http://localhost:8001/api/optimize \
  -H 'Content-Type: application/json' \
  -d '{
    "url": "https://example.com",
    "html": "",
    "markdown": "",
    "score": 0.75,
    "target_keyword": "example"
  }'
# Response: {"event": "error", "data": {"error": "HTML and markdown are required"}}
```

### **Performance:**
- Optimization takes 30-60 seconds
- SSE shows real-time progress
- Keep connection alive for full results

## 🎉 **Success Indicators**

✅ **Score Endpoint Working:**
```json
{
  "success": true,
  "data": {
    "score": 0.7500,
    "markdown": "...",
    "crawl_success": true
  }
}
```

✅ **Optimization Started:**
```json
{
  "success": true,
  "task_id": "optimize_task_1234567890_12345"
}
```

✅ **SSE Events Flowing:**
```
event: start
event: step
event: step
...
event: complete
```

✅ **Final Results:**
```json
{
  "original_html": "<html>...</html>",
  "optimized_html": "<html>...</html>",
  "updated_score": 0.8500,
  "initial_score": 0.7500,
  "improvement": 0.1000,
  "time": 45.23
}
```

This guide should help you test the SSE functionality with curl! 🚀 