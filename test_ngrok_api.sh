#!/bin/bash

# Test script for ngrok API
# Replace YOUR_NGROK_URL with the actual ngrok URL

echo "🌐 Testing ngrok API"
echo "===================="

# Replace this with your actual ngrok URL
NGROK_URL="https://your-ngrok-url.ngrok.io"

echo "🔍 Testing health endpoint..."
curl -s "$NGROK_URL/health" | jq .

echo -e "\n📊 Testing score endpoint..."
curl -s -X POST "$NGROK_URL/api/score" \
  -H 'Content-Type: application/json' \
  -d '{"url": "https://httpbin.org/html"}' | jq .

echo -e "\n🚀 Testing SSE optimization..."
echo "This will stream events in real-time..."
echo "Press Ctrl+C to stop the stream"

curl -N -X POST "$NGROK_URL/api/optimize" \
  -H 'Content-Type: application/json' \
  -d '{
    "url": "https://example.com",
    "html": "<html><head><title>Example</title></head><body><h1>Example Website</h1><p>This is an example website for testing.</p></body></html>",
    "markdown": "# Example Website\n\nThis is an example website for testing.",
    "score": 0.75,
    "target_keyword": "example website"
  }'

echo -e "\n✅ Test completed!" 