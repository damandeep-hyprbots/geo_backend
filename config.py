# Configuration for Generative Engine Optimization (GEO) AI Agent

# GEO Prompts from https://www.getpassionfruit.com/blog/gpt-prompts-for-geo-2025
GEO_PROMPTS = {
    "title_optimization": """
    Optimize the title of this webpage for better search engine visibility and user engagement.
    
    Current title: {current_title}
    Target keywords: {target_keywords}
    Website URL: {website_url}
    
    Requirements:
    - Keep it under 60 characters
    - Include primary keywords naturally
    - Make it compelling and click-worthy
    - Maintain brand consistency
    
    Provide only the optimized title, nothing else.
    """,
    
    "meta_description": """
    Create an optimized meta description for this webpage.
    
    Current content: {current_content}
    Target keywords: {target_keywords}
    Website URL: {website_url}
    
    Requirements:
    - Keep it under 160 characters
    - Include target keywords naturally
    - Make it compelling and action-oriented
    - Include a clear value proposition
    
    Provide only the optimized meta description, nothing else.
    """,
    
    "content_optimization": """
    Optimize the main content of this webpage for better search engine visibility and user engagement.
    
    Current content: {current_content}
    Target keywords: {target_keywords}
    Website URL: {website_url}
    
    Requirements:
    - Improve readability and structure
    - Include target keywords naturally (2-3% density)
    - Add relevant headings (H1, H2, H3)
    - Include internal and external links where appropriate
    - Optimize for featured snippets
    - Make content more engaging and valuable
    - Maintain original meaning and intent
    
    Provide the optimized HTML content with proper structure.
    """,
    
    "heading_optimization": """
    Optimize the headings structure of this webpage for better SEO and user experience.
    
    Current headings: {current_headings}
    Target keywords: {target_keywords}
    Website URL: {website_url}
    
    Requirements:
    - Use proper heading hierarchy (H1, H2, H3)
    - Include target keywords in headings naturally
    - Make headings descriptive and engaging
    - Ensure only one H1 per page
    - Use long-tail keywords in subheadings
    
    Provide the optimized headings structure.
    """,
    
    "internal_linking": """
    Optimize the internal linking structure of this webpage.
    
    Current content: {current_content}
    Website URL: {website_url}
    Available internal pages: {internal_pages}
    
    Requirements:
    - Add relevant internal links naturally
    - Use descriptive anchor text
    - Link to related content
    - Improve site navigation
    - Distribute link equity effectively
    
    Provide the content with optimized internal linking.
    """,
    
    "schema_markup": """
    Add appropriate schema markup to this webpage for better search engine understanding.
    
    Current content: {current_content}
    Website URL: {website_url}
    Page type: {page_type}
    
    Requirements:
    - Add relevant schema markup (JSON-LD)
    - Include organization, article, or product schema as appropriate
    - Add breadcrumb schema
    - Include FAQ schema if applicable
    - Ensure valid JSON-LD structure
    
    Provide the schema markup to be added to the page.
    """
}

# Optimization Steps Configuration
OPTIMIZATION_STEPS = [
    {
        "name": "title_optimization",
        "description": "Optimize page title for SEO",
        "prompt_key": "title_optimization",
        "threshold": 0.05,  # 5% improvement required
        "max_attempts": 3
    },
    {
        "name": "meta_description",
        "description": "Optimize meta description",
        "prompt_key": "meta_description", 
        "threshold": 0.03,  # 3% improvement required
        "max_attempts": 3
    },
    {
        "name": "heading_optimization",
        "description": "Optimize heading structure",
        "prompt_key": "heading_optimization",
        "threshold": 0.04,  # 4% improvement required
        "max_attempts": 3
    },
    {
        "name": "content_optimization",
        "description": "Optimize main content",
        "prompt_key": "content_optimization",
        "threshold": 0.08,  # 8% improvement required
        "max_attempts": 5
    },
    {
        "name": "internal_linking",
        "description": "Optimize internal linking",
        "prompt_key": "internal_linking",
        "threshold": 0.02,  # 2% improvement required
        "max_attempts": 3
    },
    {
        "name": "schema_markup",
        "description": "Add schema markup",
        "prompt_key": "schema_markup",
        "threshold": 0.03,  # 3% improvement required
        "max_attempts": 2
    }
]

# Agent Configuration
AGENT_CONFIG = {
    "llm_model": "gpt-4o-mini",  # or "gpt-3.5-turbo"
    "temperature": 0.7,
    "max_tokens": 16384,  # Hard limit to stay under 30k API limit
    "improvement_threshold": 0.02,  # 2% minimum improvement to keep changes
    "max_iterations": 10,
    "convergence_threshold": 0.01,  # Stop if improvement is less than 1%
    "backup_original": True,
    "save_optimization_history": True
}

# Scoring Configuration
SCORING_CONFIG = {
    "reranker_model": "jina-reranker-m0",
    "content_weight": 0.6,
    "title_weight": 0.2,
    "meta_weight": 0.1,
    "structure_weight": 0.1
}

# File Paths
PATHS = {
    "optimization_history": "geo_optimization_history.json",
    "backup_dir": "website_backups",
    "optimized_content_dir": "optimized_content"
} 