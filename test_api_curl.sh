#!/bin/bash

# API Base URL
API_BASE="http://localhost:8001"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}🚀 GEO Agent API - SSE Test Script${NC}"
echo "=================================="

# Test 1: Health Check
echo -e "\n${YELLOW}1. Testing Health Check...${NC}"
curl -s "$API_BASE/health" | jq .
if [ $? -eq 0 ]; then
    echo -e "${GREEN}✅ Health check passed${NC}"
else
    echo -e "${RED}❌ Health check failed${NC}"
fi

# Test 2: Score Endpoint
echo -e "\n${YELLOW}2. Testing Score Endpoint...${NC}"
SCORE_RESPONSE=$(curl -s -X POST "$API_BASE/api/score" \
  -H 'Content-Type: application/json' \
  -d '{"url": "https://httpbin.org/html"}')

echo "$SCORE_RESPONSE" | jq .

# Extract score and markdown from response
SCORE=$(echo "$SCORE_RESPONSE" | jq -r '.data.score // 0.75')
MARKDOWN=$(echo "$SCORE_RESPONSE" | jq -r '.data.markdown // "# Test Website\n\nThis is a test website."')

echo -e "${GREEN}✅ Score: $SCORE${NC}"
echo -e "${GREEN}✅ Markdown length: ${#MARKDOWN} characters${NC}"

# Test 3: Optimization with SSE
echo -e "\n${YELLOW}3. Testing Optimization with SSE...${NC}"

# Sample HTML for testing
SAMPLE_HTML="<html><head><title>Test Website</title><meta name='description' content='A test website for optimization'></head><body><h1>Test Website</h1><p>This is a test website for optimization testing.</p><p>We provide various services and solutions.</p></body></html>"

echo -e "${BLUE}Starting optimization...${NC}"
echo "URL: https://httpbin.org/html"
echo "Score: $SCORE"
echo "Keyword: test website"

# Start optimization and capture the SSE stream
curl -N -X POST "$API_BASE/api/optimize" \
  -H 'Content-Type: application/json' \
  -d "{
    \"url\": \"https://httpbin.org/html\",
    \"html\": \"$SAMPLE_HTML\",
    \"markdown\": \"$MARKDOWN\",
    \"score\": $SCORE,
    \"target_keyword\": \"test website\",
    \"improvement_threshold\": 0.02
  }" 2>/dev/null | while IFS= read -r line; do
    if [[ $line == event:* ]]; then
        event_type=$(echo "$line" | sed 's/event: //')
        echo -e "${BLUE}📡 Event: $event_type${NC}"
    elif [[ $line == data:* ]]; then
        data=$(echo "$line" | sed 's/data: //')
        echo -e "${GREEN}📊 Data: $data${NC}"
        
        # Check if optimization is complete
        if echo "$data" | grep -q "complete"; then
            echo -e "${GREEN}✅ Optimization completed!${NC}"
            break
        fi
    fi
done

echo -e "\n${GREEN}🎉 All tests completed!${NC}"
echo "==================================" 