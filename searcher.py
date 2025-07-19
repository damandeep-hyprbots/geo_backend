import requests
import json
import os
from typing import List, Dict, Optional
import traceback
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def search_jina(query: str, api_key: str = None) -> str:
    """
    Search using Jina's search API.
    
    Args:
        query (str): Search query
        api_key (str): Jina API key
        
    Returns:
        str: Raw search response text
    """
    # Use provided API key or get from environment
    api_key = api_key or os.getenv("JINA_API_KEY")
    if not api_key:
        raise ValueError("Jina API key not provided and not found in environment variables")
    
    url = "https://s.jina.ai/"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "X-Respond-With": "no-content"
    }
    params = {"q": query}
    
    response = requests.get(url, headers=headers, params=params)
    return response.text


def parse_search_results(search_response: str) -> List[Dict]:
    """
    Parse the search results from the API response.
    
    Args:
        search_response (str): Raw search response text
        
    Returns:
        List[Dict]: Parsed search results
    """
    results = []
    lines = search_response.strip().split('\n')
    
    current_result = {}
    
    for line in lines:
        line = line.strip()
        if not line:
            continue
            
        if line.startswith('[') and ']' in line and 'Title:' in line:
            # New result
            if current_result:
                results.append(current_result)
            current_result = {}
            
            # Extract title
            title_start = line.find('Title:') + 6
            title_end = line.find('URL Source:') if 'URL Source:' in line else len(line)
            current_result['title'] = line[title_start:title_end].strip()
            
        elif 'URL Source:' in line:
            url_start = line.find('URL Source:') + 11
            current_result['url'] = line[url_start:].strip()
            
        elif 'Description:' in line:
            desc_start = line.find('Description:') + 12
            current_result['description'] = line[desc_start:].strip()
            
        elif 'Date:' in line:
            date_start = line.find('Date:') + 5
            current_result['date'] = line[date_start:].strip()
    
    # Add the last result
    if current_result:
        results.append(current_result)
    
    return results





def get_top_k_websites(
    search_results: List[Dict], 
    top_k: int = 5
) -> List[Dict]:
    """
    Get top-k websites from search results in original order.
    
    Args:
        search_results (List[Dict]): Search results
        top_k (int): Number of top results to return
        
    Returns:
        List[Dict]: Top-k results in original order
    """
    # Return top-k results in original order
    return search_results[:top_k]


def search_and_get_top_k(query: str, top_k: int = 5) -> List[Dict]:
    """
    Complete pipeline: search and get top-k websites in original order.
    
    Args:
        query (str): Search query
        top_k (int): Number of top results to return
        
    Returns:
        List[Dict]: Top-k search results in original order
    """
    try:
        # First, perform the search
        search_response = search_jina(query)
        
        # Parse the search results
        search_results = parse_search_results(search_response)
        
        # Get top-k results in original order
        top_results = get_top_k_websites(search_results, top_k)
        
        print(f"Found {len(top_results)} results for query: '{query}'")
        
        return top_results
    except Exception as e:
        print(traceback.format_exc())
        print(f"Error searching for {query}: {e}")
        return []


# Example usage function
def example_usage():
    """Example of how to use the search functionality."""
    
    query = "ai agents for finance"
    
    # Use the actual search function
    top_results = search_and_get_top_k(query, top_k=5)
    
    if top_results:
        print(f"Top {len(top_results)} websites for '{query}' (in original order):\n")
        for i, result in enumerate(top_results, 1):
            print(f"{i}. {result.get('title', 'N/A')}")
            print(f"   URL: {result.get('url', 'N/A')}")
            print(f"   Description: {result.get('description', 'N/A')[:100]}...")
            print()
    else:
        print(f"No results found for query: '{query}'")


if __name__ == "__main__":
    example_usage() 