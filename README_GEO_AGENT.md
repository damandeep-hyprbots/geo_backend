# GEO Agentic Framework

A sophisticated agentic framework using LangGraph and LangChain for iterative website SEO optimization. The framework automatically improves website HTML content to achieve better search engine relevance scores for target keywords.

## 🚀 Features

### Core Capabilities
- **Iterative Optimization**: Automatically improves website content through multiple optimization steps
- **Intelligent Scoring**: Uses Jina's reranker API to evaluate content relevance
- **Threshold-Based Improvements**: Only keeps changes that meet minimum improvement thresholds
- **HTML Structure Analysis**: Parses and optimizes specific HTML elements (title, meta description, headings, content)
- **State Management**: Maintains optimization history and tracks best performing versions

### Agent Types
1. **Basic GEO Agent** (`geo_agent.py`): Simple optimization with basic HTML handling
2. **Enhanced GEO Agent** (`geo_agent_enhanced.py`): Advanced optimization with sophisticated HTML parsing and targeted strategies

## 🏗️ Architecture

### LangGraph Workflow
```
START → Initialize → Get Initial Score → Analyze HTML → Optimize Content → Evaluate Improvement → Update State → [Continue/Finalize] → END
```

### State Management
The agent maintains a comprehensive state including:
- Website URL and target keyword
- Current HTML content and relevance score
- Optimization history and best performing version
- HTML element analysis (title, meta description, headings)
- Optimization focus and step tracking

### Optimization Steps
1. **Title Optimization**: Optimize page title for SEO (60 characters max)
2. **Meta Description**: Create compelling meta descriptions (160 characters max)
3. **Heading Optimization**: Improve heading structure and hierarchy
4. **Content Optimization**: Enhance main content readability and keyword density
5. **Internal Linking**: Add relevant internal links
6. **Schema Markup**: Add structured data markup

## 📦 Installation

### Prerequisites
- Python 3.8+
- OpenAI API key
- Jina API key

### Setup
```bash
# Install dependencies
pip install -r requirements.txt

# Set up environment variables
export OPENAI_API_KEY="your_openai_api_key"
export JINA_API_KEY="your_jina_api_key"
```

## 🎯 Usage

### Basic Usage

```python
from geo_agent import GEOAgent

# Initialize the agent
agent = GEOAgent()

# Optimize a website
results = agent.optimize_website(
    website_url="https://example.com",
    target_keyword="AI agents for finance",
    max_steps=3,
    improvement_threshold=0.02
)

# Display results
display_optimization_results(results)
```

### Enhanced Usage

```python
from geo_agent_enhanced import EnhancedGEOAgent

# Initialize the enhanced agent
agent = EnhancedGEOAgent()

# Optimize with more sophisticated strategies
results = agent.optimize_website(
    website_url="https://example.com",
    target_keyword="AI agents for finance",
    max_steps=3,
    improvement_threshold=0.015
)

# Display enhanced results
display_optimization_results(results)
```

### Running Tests

```bash
# Run the comprehensive test suite
python test_geo_agent.py
```

## ⚙️ Configuration

### Agent Configuration (`config.py`)

```python
AGENT_CONFIG = {
    "llm_model": "gpt-4o",  # or "gpt-3.5-turbo"
    "temperature": 0.7,
    "max_tokens": 2000,
    "improvement_threshold": 0.02,  # 2% minimum improvement
    "max_iterations": 10,
    "convergence_threshold": 0.01,  # Stop if improvement < 1%
}
```

### Optimization Steps Configuration

```python
OPTIMIZATION_STEPS = [
    {
        "name": "title_optimization",
        "description": "Optimize page title for SEO",
        "prompt_key": "title_optimization",
        "threshold": 0.05,  # 5% improvement required
        "max_attempts": 3
    },
    # ... more steps
]
```

## 🔧 Customization

### Adding New Optimization Steps

1. Add a new prompt to `GEO_PROMPTS` in `config.py`:
```python
GEO_PROMPTS["custom_optimization"] = """
Your custom optimization prompt here.
Use placeholders: {current_content}, {target_keywords}, {website_url}
"""
```

2. Add the step configuration to `OPTIMIZATION_STEPS`:
```python
{
    "name": "custom_optimization",
    "description": "Your custom optimization",
    "prompt_key": "custom_optimization",
    "threshold": 0.03,
    "max_attempts": 3
}
```

### Custom HTML Element Handling

Extend the `_update_html_element` method in `EnhancedGEOAgent` to handle custom HTML elements:

```python
def _update_html_element(self, current_html: str, step_name: str, optimized_content: str, elements: Dict) -> str:
    if step_name == "custom_optimization":
        # Your custom HTML update logic
        soup = BeautifulSoup(current_html, 'html.parser')
        # ... custom logic
        return str(soup)
    # ... existing logic
```

## 📊 Results and Analysis

### Optimization Results Structure

```python
{
    'website_url': 'https://example.com',
    'target_keyword': 'AI agents for finance',
    'initial_score': 0.1234,
    'final_score': 0.2345,
    'total_improvement': 0.1111,
    'optimization_history': [
        {
            'step': 1,
            'step_name': 'title_optimization',
            'previous_score': 0.1234,
            'new_score': 0.1567,
            'improvement': 0.0333,
            'html': '<html>...</html>'
        }
    ],
    'optimized_html': '<html>...</html>',
    'steps_attempted': 3
}
```

### Performance Metrics

- **Initial Score**: Relevance score before optimization
- **Final Score**: Best achieved relevance score
- **Total Improvement**: Overall improvement achieved
- **Successful Steps**: Number of optimization steps that met threshold
- **Optimization History**: Detailed history of each improvement

## 🧪 Testing

The framework includes comprehensive testing capabilities:

### Test Scenarios
1. **Basic Agent Test**: Tests the fundamental optimization capabilities
2. **Enhanced Agent Test**: Tests advanced HTML parsing and optimization
3. **Keyword Variation Test**: Tests optimization with different target keywords
4. **Threshold Sensitivity Test**: Tests different improvement thresholds
5. **Agent Comparison Test**: Compares basic vs enhanced agent performance

### Running Tests
```bash
python test_geo_agent.py
```

## 🔍 Troubleshooting

### Common Issues

1. **API Key Errors**
   - Ensure `OPENAI_API_KEY` and `JINA_API_KEY` are set
   - Check API key validity and quotas

2. **HTML Parsing Errors**
   - Verify website accessibility
   - Check for malformed HTML content

3. **No Improvement Detected**
   - Lower the improvement threshold
   - Increase max_steps
   - Check target keyword relevance

4. **Rate Limiting**
   - Add delays between API calls
   - Implement retry logic

### Debug Mode

Enable detailed logging by modifying the agent configuration:

```python
AGENT_CONFIG["debug"] = True
```

## 🚀 Advanced Features

### Parallel Optimization
Run multiple optimization strategies simultaneously:

```python
from concurrent.futures import ThreadPoolExecutor

def parallel_optimization(website_url, keywords):
    with ThreadPoolExecutor(max_workers=3) as executor:
        futures = [
            executor.submit(agent.optimize_website, website_url, keyword)
            for keyword in keywords
        ]
        return [future.result() for future in futures]
```

### Custom Scoring Functions
Implement custom relevance scoring:

```python
def custom_scoring_function(content, keyword):
    # Your custom scoring logic
    return custom_score

# Integrate with agent
agent.custom_scorer = custom_scoring_function
```

## 📈 Performance Optimization

### Caching
Implement caching for API responses:

```python
import functools

@functools.lru_cache(maxsize=128)
def cached_rerank_documents(query, documents):
    return rerank_documents(query, documents)
```

### Batch Processing
Process multiple websites efficiently:

```python
def batch_optimize(websites_and_keywords):
    results = []
    for website_url, keyword in websites_and_keywords:
        result = agent.optimize_website(website_url, keyword)
        results.append(result)
    return results
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Add tests for new functionality
4. Ensure all tests pass
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- LangGraph for the agentic framework
- LangChain for LLM integration
- Jina AI for search and reranking capabilities
- OpenAI for language model access

## 📞 Support

For questions and support:
- Create an issue on GitHub
- Check the troubleshooting section
- Review the test examples

---

**Note**: This framework is designed for educational and research purposes. Always respect website terms of service and API rate limits when using in production environments. 