import requests
import json
import os
from typing import Dict, Optional, Union
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


def crawl_website(url: str, crawler_api_url: str = None) -> Optional[str]:
    """
    Crawl a website and extract the HTML content from the first page.
    
    Args:
        url (str): The URL to crawl
        crawler_api_url (str): The crawler API endpoint
        
    Returns:
        Optional[str]: HTML content of the first page, or None if failed
    """
    headers = {
        "Content-Type": "application/json"
    }
    data = {
        "url": url
    }
    
    # Use provided API URL or get from environment
    crawler_api_url = crawler_api_url or os.getenv("CRAWLER_API_URL")
    if not crawler_api_url:
        raise ValueError("Crawler API URL not provided and not found in environment variables")
    
    try:
        response = requests.post(crawler_api_url, headers=headers, json=data)
        response.raise_for_status()
        
        result = response.json()
        
        # Extract HTML from the first page
        if 'pages' in result and len(result['pages']) > 0:
            html_content = result['pages'][0]['html']
            return html_content
        else:
            print(f"No pages found in response for {url}")
            return None
            
    except requests.exceptions.RequestException as e:
        print(f"Error crawling {url}: {e}")
        return None
    except (KeyError, IndexError) as e:
        print(f"Error parsing response for {url}: {e}")
        return None


def extract_llm_readable_content(
    url: str, 
    html_content: str, 
    api_key: str = None
) -> Optional[str]:
    """
    Extract LLM-readable content from HTML using Jina Reader API.
    
    Args:
        url (str): The original URL
        html_content (str): HTML content to process
        api_key (str): Jina API key
        
    Returns:
        Optional[str]: LLM-readable content, or None if failed
    """
    # Use provided API key or get from environment
        
    api_key = api_key or os.getenv("JINA_API_KEY")
    if not api_key:
        raise ValueError("Jina API key not provided and not found in environment variables")
    
    reader_url = "https://r.jina.ai/"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    if not url:
        
        data = {
            "url" : url,
            "html": html_content
        }
    else:
        data = {
            "url" : url,
            "html": html_content
        }

        
    try:
        response = requests.post(reader_url, headers=headers, json=data)
        response.raise_for_status()
        
        return response.text
        
    except requests.exceptions.RequestException as e:
        print(f"Error processing HTML for {url}: {e}")
        return None


def get_llm_readable_webpage(
    url: str,
    crawler_api_url: str = None,
    reader_api_key: str = None
) -> Optional[str]:
    """
    Complete pipeline: crawl website and extract LLM-readable content.
    
    Args:
        url (str): The URL to process
        crawler_api_url (str): The crawler API endpoint
        reader_api_key (str): Jina Reader API key
        
    Returns:
        Optional[str]: LLM-readable content, or None if failed
    """
    print(f"Crawling {url}...")
    
    # Step 1: Crawl the website to get HTML
    html_content = crawl_website(url, crawler_api_url)
    
    if html_content is None:
        print(f"Failed to crawl {url}")
        return None
    
    print(f"Successfully extracted HTML from {url}")
    print(f"HTML length: {len(html_content)} characters")
    
    # Step 2: Process HTML through Jina Reader API
    print(f"Processing HTML through Jina Reader API...")
    
    llm_content = extract_llm_readable_content(url, html_content, reader_api_key)
    
    if llm_content is None:
        print(f"Failed to extract LLM-readable content from {url}")
        return None
    
    print(f"Successfully extracted LLM-readable content from {url}")
    print(f"Content length: {len(llm_content)} characters")
    
    return llm_content


def process_multiple_urls(
    urls: list[str],
    crawler_api_url: str = "https://6ec323f734e6.ngrok-free.app/api/crawler/crawl",
    reader_api_key: str = "jina_08ef8da6068d4042b44a66286a67cf3dqne6ZOey1zK_kL-zqX6NSh-EdbN2"
) -> Dict[str, Optional[str]]:
    """
    Process multiple URLs and extract LLM-readable content from each.
    
    Args:
        urls (list[str]): List of URLs to process
        crawler_api_url (str): The crawler API endpoint
        reader_api_key (str): Jina Reader API key
        
    Returns:
        Dict[str, Optional[str]]: Dictionary mapping URLs to their LLM-readable content
    """
    results = {}
    
    for url in urls:
        print(f"\n{'='*50}")
        print(f"Processing: {url}")
        print(f"{'='*50}")
        
        content = get_llm_readable_webpage(url, crawler_api_url, reader_api_key)
        results[url] = content
        
        if content:
            print(f"✅ Successfully processed {url}")
        else:
            print(f"❌ Failed to process {url}")
    
    return results


def save_content_to_file(content: str, filename: str) -> None:
    """
    Save content to a file.
    
    Args:
        content (str): Content to save
        filename (str): Filename to save to
    """
    try:
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"Content saved to {filename}")
    except Exception as e:
        print(f"Error saving to {filename}: {e}")


def example_usage():
    """Example of how to use the webpage reader functionality."""
    
    # Example URL
    url = "https://www.hyperbots.com"
    
    print("Example: Extracting LLM-readable content from a webpage")
    print(f"URL: {url}")
    print()
    
    # Get LLM-readable content
    content = get_llm_readable_webpage(url)
    
    if content:
        print("\n" + "="*50)
        print("EXTRACTED CONTENT:")
        print("="*50)
        print(content[:1000] + "..." if len(content) > 1000 else content)
        
        # Save to file
        save_content_to_file(content, f"extracted_content_{url.replace('://', '_').replace('/', '_')}.txt")
    else:
        print("Failed to extract content")


def batch_process_example():
    """Example of batch processing multiple URLs."""
    
    urls = [
        "https://www.hyperbots.com",
        "https://jina.ai",
        "https://github.com/jina-ai"
    ]
    
    print("Batch processing multiple URLs...")
    results = process_multiple_urls(urls)
    
    print("\n" + "="*50)
    print("BATCH PROCESSING RESULTS:")
    print("="*50)
    
    for url, content in results.items():
        if content:
            print(f"✅ {url}: {len(content)} characters")
            # Save each result
            filename = f"extracted_{url.replace('://', '_').replace('/', '_').replace('.', '_')}.txt"
            save_content_to_file(content, filename)
        else:
            print(f"❌ {url}: Failed")


if __name__ == "__main__":
    example_usage() 