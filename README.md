# Generative Engine Optimization (GEO) AI Agent

A sophisticated AI agent that performs Generative Engine Optimization for websites using **LangGraph**, OpenAI, and Jina's reranker API. The agent implements a proper agentic workflow that iteratively improves website content and tracks relevance score improvements based on target keywords.

## 🚀 Features

- **LangGraph Agentic Workflow**: Uses LangGraph to create a structured, stateful workflow with proper error handling and conditional logic
- **Iterative Optimization**: Uses LangChain for LLM calls within a LangGraph workflow that optimizes website content step by step
- **Multiple Optimization Types**: Title, meta description, headings, content, internal linking, and schema markup
- **Score Tracking**: Monitors relevance scores using Jina's reranker API
- **Threshold-based Improvements**: Only keeps changes that meet improvement thresholds
- **HTML Processing**: Converts HTML to LLM-readable format for accurate scoring
- **Backup System**: Automatically backs up original content
- **History Tracking**: Saves optimization history and results
- **Error Handling**: Comprehensive error handling with graceful fallbacks



## 📁 Project Structure

```
final_code3/
├── config.py                           # Configuration and prompts
├── geo_agent.py                       # Original GEO AI agent (class-based)
├── langgraph_geo_agent.py             # Basic LangGraph GEO agent
├── langgraph_geo_agent_enhanced.py    # Enhanced LangGraph GEO agent with full integration
├── run_langgraph_geo.py               # Runner script for LangGraph agents
├── html_utils.py                      # HTML processing utilities
├── searcher.py                        # Website search functionality
├── webpage_reader.py                  # LLM-readable content extraction
├── reranker_api.py                    # Jina reranker API functions
├── website_similarity_analyzer.py     # Website similarity analysis
├── query_processor.py                 # Query processing pipeline
├── requirements.txt                   # Python dependencies
└── README.md                         # This file
```

## 🛠️ Installation

1. **Install dependencies**:
```bash
pip install -r requirements.txt
```

2. **Set up environment variables**:
```bash
export OPENAI_API_KEY="your_openai_api_key_here"
```

## 🎯 Usage

### LangGraph Agent Usage (Recommended)

```python
import asyncio
from langgraph_geo_agent_enhanced import EnhancedLangGraphGEOAgent

async def main():
    # Initialize the enhanced LangGraph agent
    agent = EnhancedLangGraphGEOAgent()
    
    # Optimize a website
    results = await agent.optimize_website(
        query="AI search engine optimization",
        target_url="https://example.com"  # Optional
    )
    
    if results["success"]:
        print(f"Initial Score: {results['initial_score']:.3f}")
        print(f"Final Score: {results['final_score']:.3f}")
        print(f"Improvement: {results['improvement']:.3f}")
        print(f"Iterations: {results['iterations']}")

# Run the agent
asyncio.run(main())
```

### Interactive Runner

```bash
python run_langgraph_geo.py
```

This provides an interactive interface to run the LangGraph agent with options for:
- Single optimization
- Demo optimizations
- Interactive mode

### Basic Usage (Original Class-based Agent)

```python
from geo_agent import GEOAgent
import os

# Initialize the agent
agent = GEOAgent(os.getenv("OPENAI_API_KEY"))

# Optimize a website
results = agent.optimize_website(
    website_url="https://www.hyperbots.com",
    target_keywords="AI agents automation",
    original_html="<html>...</html>"  # Optional: provide HTML directly
)
```

### Advanced Usage with HTML Fetching

```python
from geo_agent import GEOAgent
from html_utils import fetch_website_html
import os

# Initialize the agent
agent = GEOAgent(os.getenv("OPENAI_API_KEY"))

# Fetch website HTML
html = fetch_website_html("https://www.hyperbots.com")

if html:
    # Optimize the website
    results = agent.optimize_website(
        website_url="https://www.hyperbots.com",
        target_keywords="AI agents automation",
        original_html=html
    )
    
    print(f"Original Score: {results['original_score']:.4f}")
    print(f"Final Score: {results['final_score']:.4f}")
    print(f"Total Improvement: {results['total_improvement']:.2%}")
```

## ⚙️ Configuration

### Optimization Steps

The agent performs these optimization steps in order:

1. **Title Optimization** (5% threshold)
2. **Meta Description** (3% threshold)
3. **Heading Structure** (4% threshold)
4. **Content Optimization** (8% threshold)
5. **Internal Linking** (2% threshold)
6. **Schema Markup** (3% threshold)

### Agent Configuration

```python
AGENT_CONFIG = {
    "llm_model": "gpt-4",
    "temperature": 0.7,
    "max_tokens": 2000,
    "improvement_threshold": 0.02,  # 2% minimum improvement
    "max_iterations": 10,
    "convergence_threshold": 0.01,  # Stop if improvement < 1%
    "backup_original": True,
    "save_optimization_history": True
}
```

## 🔄 LangGraph Optimization Process

The LangGraph agent implements a structured workflow with the following steps:

1. **Input Validation**: Validates query and API keys
2. **Website Fetching**: Retrieves target website HTML
3. **Related Site Search**: Finds and analyzes related websites for context
4. **Content Extraction**: Extracts LLM-readable content from related sites
5. **Initial Scoring**: Gets baseline relevance score
6. **Content Analysis**: Analyzes content and generates optimization recommendations
7. **Content Optimization**: Applies LLM-based optimizations using LangChain
8. **Improvement Evaluation**: Scores the optimized content
9. **Conditional Iteration**: Continues optimization if improvement threshold is met
10. **Results Saving**: Saves optimized HTML and detailed history

### Workflow Graph

```
validate_input → fetch_target_website → search_related_sites → extract_related_content
     ↓
get_initial_score → analyze_content → optimize_content → evaluate_improvement
     ↓
[continue] ← should_continue → [finish] → save_results → END
```

### Error Handling

The workflow includes comprehensive error handling:
- Input validation errors
- Network failures
- API timeouts
- LLM response parsing errors
- Graceful fallbacks for missing APIs

## 📊 Output Files

The agent creates several output files:

- `website_backups/`: Original HTML backups
- `optimized_content/`: Optimized HTML files
- `geo_optimization_history.json`: Detailed optimization history
- `llm_content/`: LLM-readable content files

## 🎯 Example Results

```
🚀 GENERATIVE ENGINE OPTIMIZATION (GEO) AGENT
============================================================
Website: https://www.hyperbots.com
Target Keywords: AI agents automation

📊 Getting initial relevance score...
Initial relevance score: 0.4521

🔄 Optimizing: Optimize page title for SEO
   Attempt 1/3
   Current score: 0.4521
   New score: 0.4876
   Improvement: 7.85%
   ✅ Improvement meets threshold (5.0%)

🔄 Optimizing: Optimize meta description
   Attempt 1/3
   Current score: 0.4876
   New score: 0.5123
   Improvement: 5.07%
   ✅ Improvement meets threshold (3.0%)

✅ OPTIMIZATION COMPLETE
============================================================
Original Score: 0.4521
Final Score: 0.5123
Total Improvement: 13.31%
Iterations: 1
Optimized HTML saved to: optimized_content/optimized_https___www_hyperbots_com_20241201_143022.html
```

## 🔧 Customization

### Adding New Optimization Types

1. Add prompt to `GEO_PROMPTS` in `config.py`
2. Add step configuration to `OPTIMIZATION_STEPS`
3. Implement optimization logic in `apply_optimization()` method

### Adjusting Thresholds

Modify the `threshold` values in `OPTIMIZATION_STEPS` to make the agent more or less strict about improvements.

### Changing LLM Model

Update `AGENT_CONFIG["llm_model"]` to use different OpenAI models.

## 🚨 Error Handling

The agent includes comprehensive error handling for:
- API failures
- HTML parsing errors
- Network timeouts
- Invalid responses

## 📈 Performance Monitoring

The agent tracks:
- Relevance score improvements
- Optimization attempts
- Convergence metrics
- Time spent on each step

## 🔍 Debugging

Enable detailed logging by modifying the print statements in the agent. The optimization history file contains detailed information about each step.

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License.

## 🆘 Support

For issues and questions:
1. Check the optimization history file for detailed logs
2. Verify your API keys are set correctly
3. Ensure all dependencies are installed
4. Check the HTML structure of your website

## 🔗 Related Components

- **Searcher**: Finds similar websites for comparison
- **Webpage Reader**: Extracts LLM-readable content
- **Reranker API**: Scores content relevance
- **Website Similarity Analyzer**: Compares your website with competitors 