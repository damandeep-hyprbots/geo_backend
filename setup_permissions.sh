#!/bin/bash

echo "🔧 Setting up file permissions..."
echo "=================================="

# Make all Python files executable
echo "Making Python files executable..."

# Main API files
chmod +x api_architecture_simple.py
chmod +x start_simple_api.py
chmod +x simple_api_client.py

# Original files
chmod +x geo_agent_enhanced.py
chmod +x api_architecture.py
chmod +x start_architecture_api.py
chmod +x deploy_with_ngrok.py

# Utility files
chmod +x webpage_reader.py
chmod +x website_similarity_analyzer.py
chmod +x reranker_api.py
chmod +x searcher.py
chmod +x html_utils.py
chmod +x query_processor.py

# Test files
chmod +x test_agent.py
chmod +x test_api_client.py
chmod +x test_architecture_client.py

echo "✅ All Python files are now executable!"
echo ""
echo "You can now run:"
echo "  python start_simple_api.py"
echo "  python simple_api_client.py"
echo "  python api_architecture_simple.py"
echo ""
echo "Or directly:"
echo "  ./start_simple_api.py"
echo "  ./simple_api_client.py"
echo "  ./api_architecture_simple.py" 