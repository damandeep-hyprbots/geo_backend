import requests
import json
from typing import List, Dict, Optional
from searcher import search_and_get_top_k, parse_search_results
from webpage_reader import get_llm_readable_webpage
from reranker_api import rerank_documents, get_top_results


def get_most_relevant_url_for_query(query: str, top_k: int = 5) -> List[Dict]:
    """
    Get the most relevant URLs for a given query using the searcher.
    
    Args:
        query (str): The search query
        top_k (int): Number of top results to return
        
    Returns:
        List[Dict]: Top-k most relevant URLs with their details
    """
    print(f"Searching for: '{query}'")
    
    # Get search results
    search_results = search_and_get_top_k(query, top_k)
    
    print(f"Found {len(search_results)} relevant URLs")
    return search_results


def extract_content_from_urls(urls: List[Dict]) -> List[Dict]:
    """
    Extract LLM-readable content from a list of URLs.
    
    Args:
        urls (List[Dict]): List of URL dictionaries with 'url' key
        
    Returns:
        List[Dict]: URLs with extracted content
    """
    results = []
    
    for i, url_info in enumerate(urls, 1):
        url = url_info['url']
        print(f"\n[{i}/{len(urls)}] Extracting content from: {url}")
        
        try:
            # Extract LLM-readable content
            content = get_llm_readable_webpage(url)
            
            if content:
                url_info['extracted_content'] = content
                url_info['content_length'] = len(content)
                url_info['llm_readable_format'] = content  # Store the LLM-readable format
                print(f"✅ Successfully extracted {len(content)} characters")
            else:
                url_info['extracted_content'] = None
                url_info['content_length'] = 0
                url_info['llm_readable_format'] = None
                print(f"❌ Failed to extract content")
                
        except Exception as e:
            print(f"❌ Error extracting content: {e}")
            url_info['extracted_content'] = None
            url_info['content_length'] = 0
            url_info['llm_readable_format'] = None
        
        results.append(url_info)
    
    return results


def get_reranker_scores_for_content(query: str, urls_with_content: List[Dict]) -> List[Dict]:
    """
    Get reranker scores for extracted content based on the query.
    
    Args:
        query (str): The original query
        urls_with_content (List[Dict]): URLs with extracted content
        
    Returns:
        List[Dict]: URLs with reranker scores
    """
    print(f"\nGetting reranker scores for query: '{query}'")
    
    # Filter out URLs without content
    valid_urls = [url_info for url_info in urls_with_content if url_info.get('extracted_content')]
    
    if not valid_urls:
        print("No valid content found for reranking")
        return urls_with_content
    
    # Prepare documents for reranker
    documents = []
    for url_info in valid_urls:
        # Combine title, description, and extracted content for better context
        text_content = f"Title: {url_info.get('title', '')}\n"
        if 'description' in url_info:
            text_content += f"Description: {url_info['description']}\n"
        text_content += f"URL: {url_info['url']}\n"
        text_content += f"Content: {url_info['extracted_content'][:2000]}..."  # Limit content length
        
        documents.append({"text": text_content})
    
    # Get reranker scores
    try:
        response = rerank_documents(query, documents)
        
        # Map scores back to URLs
        for i, url_info in enumerate(valid_urls):
            if i < len(response.get('results', [])):
                url_info['relevance_score'] = response['results'][i]['relevance_score']
            else:
                url_info['relevance_score'] = 0.0
        
        # Add scores to URLs without content
        for url_info in urls_with_content:
            if not url_info.get('extracted_content'):
                url_info['relevance_score'] = 0.0
        
        print(f"✅ Successfully scored {len(valid_urls)} URLs")
        
    except Exception as e:
        print(f"❌ Error getting reranker scores: {e}")
        # Set default scores
        for url_info in urls_with_content:
            url_info['relevance_score'] = 0.0
    
    return urls_with_content


def sort_by_relevance(urls_with_scores: List[Dict]) -> List[Dict]:
    """
    Sort URLs by relevance score (highest first).
    
    Args:
        urls_with_scores (List[Dict]): URLs with relevance scores
        
    Returns:
        List[Dict]: URLs sorted by relevance score
    """
    return sorted(urls_with_scores, key=lambda x: x.get('relevance_score', 0.0), reverse=True)


def process_query_complete_pipeline(query: str, top_k: int = 5) -> List[Dict]:
    """
    Complete pipeline: search → extract content → rerank → sort by relevance.
    
    Args:
        query (str): The search query
        top_k (int): Number of top results to process
        
    Returns:
        List[Dict]: Processed URLs with content and relevance scores, sorted by relevance
    """
    print("="*60)
    print(f"PROCESSING QUERY: '{query}'")
    print("="*60)
    
    # Step 1: Get most relevant URLs
    print("\n1. SEARCHING FOR RELEVANT URLS")
    print("-" * 40)
    urls = get_most_relevant_url_for_query(query, top_k)
    
    # Step 2: Extract content from URLs
    print("\n2. EXTRACTING CONTENT FROM URLS")
    print("-" * 40)
    urls_with_content = extract_content_from_urls(urls)
    
    # Step 3: Get reranker scores
    print("\n3. CALCULATING RELEVANCE SCORES")
    print("-" * 40)
    urls_with_scores = get_reranker_scores_for_content(query, urls_with_content)
    
    # Step 4: Sort by relevance
    print("\n4. SORTING BY RELEVANCE")
    print("-" * 40)
    sorted_results = sort_by_relevance(urls_with_scores)
    
    return sorted_results


def display_results(results: List[Dict], query: str) -> None:
    """
    Display the final results in a formatted way.
    
    Args:
        results (List[Dict]): Processed results
        query (str): Original query
    """
    print("\n" + "="*60)
    print(f"FINAL RESULTS FOR QUERY: '{query}'")
    print("="*60)
    
    for i, result in enumerate(results, 1):
        print(f"\n{i}. {result['title']}")
        print(f"   URL: {result['url']}")
        print(f"   Relevance Score: {result.get('relevance_score', 0.0):.4f}")
        print(f"   Content Length: {result.get('content_length', 0)} characters")
        
        if result.get('extracted_content'):
            content_preview = result['extracted_content'][:200] + "..." if len(result['extracted_content']) > 200 else result['extracted_content']
            print(f"   Content Preview: {content_preview}")
        else:
            print(f"   Content: Not available")
        
        print(f"   Description: {result.get('description', 'N/A')[:100]}...")
        
        # Show LLM-readable format availability
        if result.get('llm_readable_format'):
            print(f"   ✅ LLM-readable format available ({len(result['llm_readable_format'])} characters)")
        else:
            print(f"   ❌ LLM-readable format not available")


def save_results_to_file(results: List[Dict], query: str, filename: str = None) -> None:
    """
    Save results to a JSON file.
    
    Args:
        results (List[Dict]): Results to save
        query (str): Original query
        filename (str): Optional filename, will generate one if not provided
    """
    if filename is None:
        # Create filename from query
        safe_query = "".join(c for c in query if c.isalnum() or c in (' ', '-', '_')).rstrip()
        filename = f"query_results_{safe_query.replace(' ', '_')}.json"
    
    try:
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump({
                'query': query,
                'results': results,
                'timestamp': str(datetime.datetime.now())
            }, f, indent=2, ensure_ascii=False)
        print(f"\n✅ Results saved to: {filename}")
    except Exception as e:
        print(f"\n❌ Error saving results: {e}")


def save_llm_readable_content_to_files(results: List[Dict], query: str, base_dir: str = "llm_content") -> None:
    """
    Save LLM-readable content to individual text files.
    
    Args:
        results (List[Dict]): Processed results
        query (str): Original query
        base_dir (str): Directory to save files in
    """
    import os
    
    # Create directory if it doesn't exist
    os.makedirs(base_dir, exist_ok=True)
    
    saved_count = 0
    for i, result in enumerate(results, 1):
        if result.get('llm_readable_format'):
            # Create safe filename from URL
            url = result['url']
            safe_filename = "".join(c for c in url if c.isalnum() or c in ('-', '_', '.'))
            safe_filename = safe_filename.replace('://', '_').replace('/', '_')
            filename = f"{base_dir}/content_{i}_{safe_filename}.txt"
            
            try:
                with open(filename, 'w', encoding='utf-8') as f:
                    f.write(f"Title: {result.get('title', 'N/A')}\n")
                    f.write(f"URL: {result['url']}\n")
                    f.write(f"Relevance Score: {result.get('relevance_score', 0.0):.4f}\n")
                    f.write(f"Query: {query}\n")
                    f.write("-" * 50 + "\n")
                    f.write(result['llm_readable_format'])
                
                print(f"✅ Saved LLM content to: {filename}")
                saved_count += 1
                
            except Exception as e:
                print(f"❌ Error saving content for {url}: {e}")
    
    print(f"\n📁 Saved {saved_count} LLM-readable content files to '{base_dir}/' directory")


def example_usage():
    """Example of how to use the complete query processing pipeline."""
    
    # Example query
    query = "Jina AI search foundation"
    
    # Process the query through the complete pipeline
    results = process_query_complete_pipeline(query, top_k=3)
    
    # Display results
    display_results(results, query)
    
    # Save results to JSON
    save_results_to_file(results, query)
    
    # Save LLM-readable content to individual files
    save_llm_readable_content_to_files(results, query)
    
    return results


if __name__ == "__main__":
    import datetime
    example_usage() 