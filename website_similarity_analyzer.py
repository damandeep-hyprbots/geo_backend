import requests
import json
from typing import List, Dict, Optional
from searcher import search_and_get_top_k
from webpage_reader import get_llm_readable_webpage
from reranker_api import rerank_documents, get_top_results


def find_similar_websites(query: str, max_results: int = 10) -> List[Dict]:
    """
    Find similar websites based on a query.
    
    Args:
        query (str): The search query
        max_results (int): Maximum number of results (max 10)
        
    Returns:
        List[Dict]: Similar websites found
    """
    # Ensure max_results doesn't exceed 10
    max_results = min(max_results, 10)
    
    print(f"Searching for websites similar to: '{query}'")
    print(f"Maximum results: {max_results}")
    
    # Get search results
    similar_websites = search_and_get_top_k(query, max_results)
    
    print(f"Found {len(similar_websites)} similar websites")
    return similar_websites


def extract_website_content(website_url: str) -> Dict:
    """
    Extract LLM-readable content from a specific website.
    
    Args:
        website_url (str): The website URL to extract content from
        
    Returns:
        Dict: Website information with extracted content
    """
    print(f"\nExtracting content from your website: {website_url}")
    
    try:
        # Extract LLM-readable content
        content = get_llm_readable_webpage(website_url)
        
        if content:
            website_info = {
                'title': f"Your Website: {website_url}",
                'url': website_url,
                'description': "Your website content",
                'extracted_content': content,
                'content_length': len(content),
                'llm_readable_format': content,
                'is_your_website': True
            }
            print(f"✅ Successfully extracted {len(content)} characters from your website")
        else:
            website_info = {
                'title': f"Your Website: {website_url}",
                'url': website_url,
                'description': "Your website content",
                'extracted_content': None,
                'content_length': 0,
                'llm_readable_format': None,
                'is_your_website': True
            }
            print(f"❌ Failed to extract content from your website")
            
    except Exception as e:
        print(f"❌ Error extracting content from your website: {e}")
        website_info = {
            'title': f"Your Website: {website_url}",
            'url': website_url,
            'description': "Your website content",
            'extracted_content': None,
            'content_length': 0,
            'llm_readable_format': None,
            'is_your_website': True
        }
    
    return website_info


def extract_content_from_similar_websites(similar_websites: List[Dict]) -> List[Dict]:
    """
    Extract LLM-readable content from similar websites.
    
    Args:
        similar_websites (List[Dict]): List of similar websites
        
    Returns:
        List[Dict]: Similar websites with extracted content
    """
    results = []
    
    for i, website in enumerate(similar_websites, 1):
        url = website['url']
        print(f"\n[{i}/{len(similar_websites)}] Extracting content from: {url}")
        
        try:
            # Extract LLM-readable content
            content = get_llm_readable_webpage(url)
            
            if content:
                website['extracted_content'] = content
                website['content_length'] = len(content)
                website['llm_readable_format'] = content
                website['is_your_website'] = False
                print(f"✅ Successfully extracted {len(content)} characters")
            else:
                website['extracted_content'] = None
                website['content_length'] = 0
                website['llm_readable_format'] = None
                website['is_your_website'] = False
                print(f"❌ Failed to extract content")
                
        except Exception as e:
            print(f"❌ Error extracting content: {e}")
            website['extracted_content'] = None
            website['content_length'] = 0
            website['llm_readable_format'] = None
            website['is_your_website'] = False
        
        results.append(website)
    
    return results


def get_reranker_scores_for_all_websites(query: str, all_websites: List[Dict]) -> List[Dict]:
    """
    Get reranker scores for all websites (your website + similar websites).
    
    Args:
        query (str): The original query
        all_websites (List[Dict]): All websites with extracted content
        
    Returns:
        List[Dict]: All websites with reranker scores
    """
    print(f"\nGetting reranker scores for query: '{query}'")
    print(f"Total websites to score: {len(all_websites)}")
    
    # Filter out websites without content
    valid_websites = [website for website in all_websites if website.get('extracted_content')]
    
    if not valid_websites:
        print("No valid content found for reranking")
        return all_websites
    
    # Prepare documents for reranker
    documents = []
    for website in valid_websites:
        # Combine title, description, and extracted content for better context
        text_content = f"Title: {website.get('title', '')}\n"
        if 'description' in website:
            text_content += f"Description: {website['description']}\n"
        text_content += f"URL: {website['url']}\n"
        text_content += f"Content: {website['extracted_content'][:2000]}..."  # Limit content length
        
        documents.append({"text": text_content})
    
    # Get reranker scores
    try:
        response = rerank_documents(query, documents)
        
        # Map scores back to websites
        for i, website in enumerate(valid_websites):
            if i < len(response.get('results', [])):
                website['relevance_score'] = response['results'][i]['relevance_score']
            else:
                website['relevance_score'] = 0.0
        
        # Add scores to websites without content
        for website in all_websites:
            if not website.get('extracted_content'):
                website['relevance_score'] = 0.0
        
        print(f"✅ Successfully scored {len(valid_websites)} websites")
        
    except Exception as e:
        print(f"❌ Error getting reranker scores: {e}")
        # Set default scores
        for website in all_websites:
            website['relevance_score'] = 0.0
    
    return all_websites


def sort_by_relevance(websites_with_scores: List[Dict]) -> List[Dict]:
    """
    Sort websites by relevance score (highest first).
    
    Args:
        websites_with_scores (List[Dict]): Websites with relevance scores
        
    Returns:
        List[Dict]: Websites sorted by relevance score
    """
    return sorted(websites_with_scores, key=lambda x: x.get('relevance_score', 0.0), reverse=True)


def analyze_website_similarity(query: str, website_url: str, max_similar_results: int = 10) -> List[Dict]:
    """
    Complete pipeline: find similar websites → extract content → add your website → rerank → sort.
    
    Args:
        query (str): The search query
        website_url (str): Your website URL
        max_similar_results (int): Maximum number of similar websites to find (max 10)
        
    Returns:
        List[Dict]: All websites with content and relevance scores, sorted by relevance
    """
    print("="*60)
    print(f"ANALYZING WEBSITE SIMILARITY")
    print(f"Query: '{query}'")
    print(f"Your Website: {website_url}")
    print("="*60)
    
    # Step 1: Find similar websites
    print("\n1. FINDING SIMILAR WEBSITES")
    print("-" * 40)
    similar_websites = find_similar_websites(query, max_similar_results)
    
    # Step 2: Extract content from similar websites
    print("\n2. EXTRACTING CONTENT FROM SIMILAR WEBSITES")
    print("-" * 40)
    similar_websites_with_content = extract_content_from_similar_websites(similar_websites)
    
    # Step 3: Extract content from your website
    print("\n3. EXTRACTING CONTENT FROM YOUR WEBSITE")
    print("-" * 40)
    your_website = extract_website_content(website_url)
    
    # Step 4: Combine all websites
    print("\n4. COMBINING ALL WEBSITES")
    print("-" * 40)
    all_websites = [your_website] + similar_websites_with_content
    print(f"Total websites to analyze: {len(all_websites)}")
    
    # Step 5: Get reranker scores
    print("\n5. CALCULATING RELEVANCE SCORES")
    print("-" * 40)
    websites_with_scores = get_reranker_scores_for_all_websites(query, all_websites)
    
    # Step 6: Sort by relevance
    print("\n6. SORTING BY RELEVANCE")
    print("-" * 40)
    sorted_results = sort_by_relevance(websites_with_scores)
    
    return sorted_results


def display_similarity_results(results: List[Dict], query: str, your_website_url: str) -> None:
    """
    Display the similarity analysis results.
    
    Args:
        results (List[Dict]): Processed results
        query (str): Original query
        your_website_url (str): Your website URL
    """
    print("\n" + "="*60)
    print(f"SIMILARITY ANALYSIS RESULTS")
    print(f"Query: '{query}'")
    print(f"Your Website: {your_website_url}")
    print("="*60)
    
    for i, result in enumerate(results, 1):
        website_type = "YOUR WEBSITE" if result.get('is_your_website') else "SIMILAR WEBSITE"
        print(f"\n{i}. [{website_type}] {result['title']}")
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


def save_similarity_results_to_file(results: List[Dict], query: str, your_website_url: str, filename: str = None) -> None:
    """
    Save similarity analysis results to a JSON file.
    
    Args:
        results (List[Dict]): Results to save
        query (str): Original query
        your_website_url (str): Your website URL
        filename (str): Optional filename
    """
    if filename is None:
        # Create filename from query and website
        safe_query = "".join(c for c in query if c.isalnum() or c in (' ', '-', '_')).rstrip()
        safe_url = "".join(c for c in your_website_url if c.isalnum() or c in ('-', '_', '.'))
        filename = f"similarity_results_{safe_query.replace(' ', '_')}_{safe_url.replace('://', '_').replace('/', '_')}.json"
    
    try:
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump({
                'query': query,
                'your_website_url': your_website_url,
                'results': results,
                'timestamp': str(datetime.datetime.now())
            }, f, indent=2, ensure_ascii=False)
        print(f"\n✅ Similarity results saved to: {filename}")
    except Exception as e:
        print(f"\n❌ Error saving similarity results: {e}")


def example_usage():
    """Example of how to use the website similarity analyzer."""
    
    # Example parameters
    query = "AI search engine"
    your_website_url = "https://www.hyperbots.com"
    max_similar_results = 5
    
    # Analyze website similarity
    results = analyze_website_similarity(query, your_website_url, max_similar_results)
    
    # Display results
    display_similarity_results(results, query, your_website_url)
    
    # Save results
    save_similarity_results_to_file(results, query, your_website_url)
    
    return results


if __name__ == "__main__":
    import datetime
    example_usage() 