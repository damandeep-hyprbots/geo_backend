# GEO Agent API Architecture

This implements the exact architecture you specified:

```
Frontend                     Backend              AI
(url) ----------------> score api
(score + md) <----------
(url+html+md+score) -------------------->
(SSE) <--------------------------------------
sse response - (optimized html, optimized score)
```

## 🏗️ Architecture Overview

### **1. Score API** (`/api/score`)
- **Frontend sends**: URL
- **Backend returns**: Current score + Markdown content
- **Purpose**: Get initial website analysis

### **2. AI Optimization API** (`/api/ai-optimize`)
- **Frontend sends**: URL + HTML + Markdown + Score
- **Backend returns**: Task ID for SSE tracking
- **Purpose**: Start AI optimization process

### **3. SSE API** (`/api/sse/{task_id}`)
- **Frontend connects**: To SSE stream
- **Backend streams**: Real-time optimization events
- **Purpose**: Get real-time updates and final optimized HTML + score

## 🚀 Quick Start

### 1. Install Dependencies
```bash
pip install -r requirements_architecture.txt
```

### 2. Start the API
```bash
python api_architecture.py
```

### 3. Access the API
- **Local URL**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/health

## 📋 API Endpoints

### Score API
```http
POST /api/score
```

**Request:**
```json
{
  "url": "https://example.com"
}
```

**Response:**
```json
{
  "success": true,
  "message": "Score and markdown retrieved successfully",
  "data": {
    "url": "https://example.com",
    "score": 0.75,
    "markdown": "# Example Website\n\nThis is the content...",
    "timestamp": "2024-01-15T10:30:00"
  },
  "timestamp": "2024-01-15T10:30:00"
}
```

### AI Optimization API
```http
POST /api/ai-optimize
```

**Request:**
```json
{
  "url": "https://example.com",
  "html": "<html><body>...</body></html>",
  "markdown": "# Example\n\nContent...",
  "score": 0.75,
  "target_keyword": "digital marketing",
  "improvement_threshold": 0.02
}
```

**Response:**
```json
{
  "success": true,
  "message": "AI optimization started successfully",
  "task_id": "ai_task_1705312200_12345",
  "timestamp": "2024-01-15T10:30:00"
}
```

### SSE API
```http
GET /api/sse/{task_id}
```

**SSE Events:**
```
event: status
data: {"status": "running", "message": "AI optimization started"}

event: initial_data
data: {"url": "https://example.com", "original_score": 0.75, "target_keyword": "digital marketing"}

event: step
data: {"step": "initialization", "message": "Initializing optimization..."}

event: step
data: {"step": "html_extraction", "message": "Extracted HTML (3816 characters)"}

event: step
data: {"step": "scoring", "message": "Initial score: 0.7500"}

event: step
data: {"step": "optimization", "message": "Starting HTML optimization..."}

event: optimization_complete
data: {"final_score": 0.85, "improvement": 0.10, "optimized_html": "<!DOCTYPE html>...", "original_html": "<!DOCTYPE html>...", "execution_time": 45.23}

event: complete
data: {"message": "Optimization completed"}
```

## 🧪 Testing

### Using the Test Client
```bash
python test_architecture_client.py
```

### Using curl

#### 1. Get Score and Markdown
```bash
curl -X POST http://localhost:8000/api/score \
  -H "Content-Type: application/json" \
  -d '{"url": "https://example.com"}'
```

#### 2. Start AI Optimization
```bash
curl -X POST http://localhost:8000/api/ai-optimize \
  -H "Content-Type: application/json" \
  -d '{
    "url": "https://example.com",
    "html": "<html><body>Test</body></html>",
    "markdown": "# Test\n\nContent.",
    "score": 0.5,
    "target_keyword": "test keyword"
  }'
```

#### 3. Listen to SSE (JavaScript)
```javascript
const eventSource = new EventSource('http://localhost:8000/api/sse/TASK_ID');

eventSource.onmessage = function(event) {
  const data = JSON.parse(event.data);
  console.log('SSE Event:', data);
  
  if (data.event === 'optimization_complete') {
    console.log('Optimization completed!');
    console.log('Final score:', data.final_score);
    console.log('Optimized HTML:', data.optimized_html);
  }
};
```

## 🔄 Complete Workflow Example

### Frontend Implementation (JavaScript)

```javascript
class GEOAgentClient {
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
const client = new GEOAgentClient();

async function optimizeWebsite(url, targetKeyword) {
  // Step 1: Get current score and markdown
  const scoreResult = await client.getScoreAndMarkdown(url);
  const { score, markdown } = scoreResult.data;
  
  // Step 2: Start AI optimization
  const optimizationResult = await client.startAIOptimization(
    url, html, markdown, score, targetKeyword
  );
  const taskId = optimizationResult.task_id;
  
  // Step 3: Listen to real-time updates
  client.listenToSSE(taskId, (event) => {
    console.log('SSE Event:', event);
    
    if (event.event === 'optimization_complete') {
      console.log('Final optimized HTML:', event.optimized_html);
      console.log('Final score:', event.final_score);
    }
  });
}
```

## 📊 SSE Event Types

| Event | Description | Data |
|-------|-------------|------|
| `status` | Task status updates | `{"status": "running", "message": "..."}` |
| `initial_data` | Initial optimization data | `{"url": "...", "original_score": 0.75}` |
| `step` | Optimization step progress | `{"step": "initialization", "message": "..."}` |
| `optimization_complete` | Final results | `{"final_score": 0.85, "optimized_html": "..."}` |
| `error` | Error occurred | `{"error": "Error message"}` |
| `keepalive` | Connection keepalive | `{"message": "Still processing..."}` |

## 🔧 Configuration

### Environment Variables
Create a `.env` file:
```env
OPENAI_API_KEY=your_openai_api_key_here
```

### API Configuration
The API uses the same configuration as the GEO agent. See `config.py` for options.

## 🚨 Error Handling

- **Validation Errors**: Invalid input parameters
- **Network Errors**: Website crawling issues
- **Processing Errors**: Optimization algorithm failures
- **SSE Errors**: Connection or streaming issues

## 📈 Performance

- **Score API**: 5-15 seconds
- **AI Optimization**: 30-180 seconds (depending on website size)
- **SSE Streaming**: Real-time updates throughout optimization

## 🛠️ Development

### Running in Development Mode
```bash
uvicorn api_architecture:app --reload --host 0.0.0.0 --port 8000
```

### Testing
```bash
python test_architecture_client.py
```

## 📝 API Response Format

### Success Response
```json
{
  "success": true,
  "message": "Operation completed successfully",
  "data": { /* operation-specific data */ },
  "timestamp": "2024-01-15T10:30:00"
}
```

### Error Response
```json
{
  "success": false,
  "message": "Operation failed",
  "error": "Detailed error message",
  "timestamp": "2024-01-15T10:30:00"
}
```

This architecture perfectly matches your specification and provides a complete workflow from frontend to backend to AI optimization with real-time updates via SSE! 