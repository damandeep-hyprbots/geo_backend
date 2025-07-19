# GEO Agent API

A FastAPI-based REST API for the Enhanced Generative Engine Optimization (GEO) Agent that optimizes websites for better search engine relevance.

## 🌟 Features

- **Synchronous Optimization**: Optimize websites immediately and get results
- **Asynchronous Optimization**: Start long-running optimizations in the background
- **Real-time Status Tracking**: Monitor optimization progress
- **Result Management**: Store and retrieve optimization results
- **Public Access**: Optional ngrok integration for public URL access
- **Interactive Documentation**: Auto-generated API docs with Swagger UI

## 🚀 Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements_api.txt
```

### 2. Start the API Server

#### Option A: Simple Start
```bash
python api.py
```

#### Option B: With ngrok Integration
```bash
python start_api.py
```

### 3. Access the API

- **Local URL**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs
- **Interactive API**: http://localhost:8000/redoc
- **Health Check**: http://localhost:8000/health

## 📋 API Endpoints

### Health Check
```http
GET /health
```

### Synchronous Optimization
```http
POST /optimize
```

**Request Body:**
```json
{
  "website_url": "https://example.com",
  "target_keyword": "digital marketing",
  "improvement_threshold": 0.02
}
```

**Response:**
```json
{
  "success": true,
  "message": "Optimization completed successfully",
  "data": {
    "website_url": "https://example.com",
    "target_keyword": "digital marketing",
    "initial_score": 0.0,
    "final_score": 0.85,
    "improvement": 0.85,
    "original_html": "<!DOCTYPE html>...",
    "optimized_html": "<!DOCTYPE html>...",
    "execution_time_seconds": 45.23,
    "timestamp": "2024-01-15T10:30:00"
  },
  "timestamp": "2024-01-15T10:30:00"
}
```

### Asynchronous Optimization
```http
POST /optimize/async
```

**Request Body:** Same as synchronous optimization

**Response:**
```json
{
  "success": true,
  "message": "Optimization started asynchronously",
  "task_id": "task_digital_marketing_1705312200",
  "timestamp": "2024-01-15T10:30:00"
}
```

### Check Task Status
```http
GET /status/{task_id}
```

**Response:**
```json
{
  "task_id": "task_digital_marketing_1705312200",
  "status": "completed",
  "result": {
    "website_url": "https://example.com",
    "target_keyword": "digital marketing",
    "final_score": 0.85,
    "improvement": 0.85,
    "original_html": "<!DOCTYPE html>...",
    "optimized_html": "<!DOCTYPE html>..."
  },
  "timestamp": "2024-01-15T10:30:00"
}
```

### List All Results
```http
GET /results
```

### Get Specific Result
```http
GET /results/{result_id}
```

### Delete Result
```http
DELETE /results/{result_id}
```

## 🧪 Testing

### Using the Test Client

```bash
python test_api_client.py
```

### Using curl

```bash
# Health check
curl http://localhost:8000/health

# Synchronous optimization
curl -X POST http://localhost:8000/optimize \
  -H "Content-Type: application/json" \
  -d '{
    "website_url": "https://example.com",
    "target_keyword": "digital marketing",
    "improvement_threshold": 0.02
  }'

# Async optimization
curl -X POST http://localhost:8000/optimize/async \
  -H "Content-Type: application/json" \
  -d '{
    "website_url": "https://example.com",
    "target_keyword": "SEO optimization",
    "improvement_threshold": 0.02
  }'
```

### Using Python Requests

```python
import requests

# Optimize website
response = requests.post('http://localhost:8000/optimize', json={
    'website_url': 'https://example.com',
    'target_keyword': 'digital marketing',
    'improvement_threshold': 0.02
})

result = response.json()
print(f"Success: {result['success']}")
print(f"Final Score: {result['data']['final_score']}")
```

## 🔧 Configuration

### Environment Variables

Create a `.env` file in your project directory:

```env
OPENAI_API_KEY=your_openai_api_key_here
```

### API Configuration

The API uses the same configuration as the GEO agent. See `config.py` for available options.

## 🌐 ngrok Integration

The API includes optional ngrok integration for public access:

### Automatic Installation

The startup script can automatically install ngrok:

- **macOS**: Uses Homebrew (`brew install ngrok/ngrok/ngrok`)
- **Linux**: Uses apt package manager
- **Other platforms**: Manual installation required

### Manual Installation

1. Download ngrok from https://ngrok.com/download
2. Extract and add to PATH
3. Run the startup script

### Usage

```bash
python start_api.py
```

The script will:
1. Check if ngrok is installed
2. Offer to install if missing
3. Start the FastAPI server
4. Start ngrok tunnel
5. Display both local and public URLs

## 📊 Response Format

### Success Response
```json
{
  "success": true,
  "message": "Operation completed successfully",
  "data": {
    // Operation-specific data
  },
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

## 🔍 Optimization Results

The optimization results include:

- **original_html**: HTML before optimization
- **optimized_html**: HTML after optimization
- **initial_score**: Relevance score before optimization
- **final_score**: Relevance score after optimization
- **improvement**: Score improvement
- **execution_time_seconds**: Time taken for optimization
- **optimization_history**: Detailed optimization steps
- **similar_websites**: Analysis of competitor websites

## 🚨 Error Handling

The API includes comprehensive error handling:

- **Validation Errors**: Invalid input parameters
- **Network Errors**: Website crawling issues
- **Processing Errors**: Optimization algorithm failures
- **Timeout Errors**: Long-running operations

## 🔒 Security Considerations

- **CORS**: Configured for development (allow all origins)
- **Input Validation**: Pydantic models for request validation
- **Error Sanitization**: Sensitive information filtered from error responses
- **Rate Limiting**: Consider implementing for production use

## 📈 Performance

### Optimization Times
- **Small websites**: 30-60 seconds
- **Medium websites**: 1-3 minutes
- **Large websites**: 3-5 minutes

### Memory Usage
- **Base API**: ~50MB
- **Per optimization**: +10-50MB depending on website size

## 🛠️ Development

### Running in Development Mode

```bash
uvicorn api:app --reload --host 0.0.0.0 --port 8000
```

### Running Tests

```bash
python test_api_client.py
```

### Adding New Endpoints

1. Add new route in `api.py`
2. Define request/response models
3. Add error handling
4. Update documentation

## 📝 License

This project is part of the GEO Agent system. See the main project license for details.

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## 📞 Support

For issues and questions:
1. Check the API documentation at `/docs`
2. Review the test client examples
3. Check the main project README
4. Open an issue on GitHub 