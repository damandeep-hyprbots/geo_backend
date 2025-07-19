import requests
import json
import os
from typing import List, Dict, Union, Optional
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


def rerank_documents(
    query: str,
    documents: List[Dict[str, Union[str, bytes]]],
    model: str = "jina-reranker-m0",
    api_key: str = None,
    return_documents: bool = False
) -> Dict:
    """
    Rerank documents using Jina's reranker API.
    
    Args:
        query (str): The search query
        documents (List[Dict]): List of documents to rerank. Each document should have
                               either 'text' or 'image' key
        model (str): The reranker model to use
        api_key (str): Jina API key
        return_documents (bool): Whether to return documents in response
        
    Returns:
        Dict: API response with reranked results
    """
    # Use provided API key or get from environment
    api_key = api_key or os.getenv("JINA_API_KEY")
    if not api_key:
        raise ValueError("Jina API key not provided and not found in environment variables")
    
    url = 'https://api.jina.ai/v1/rerank'
    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {api_key}'
    }
    
    data = {
        "model": model,
        "query": query,
        "documents": documents,
        "return_documents": return_documents
    }
    
    response = requests.post(url, headers=headers, json=data)
    return response.json()


def create_text_document(text: str) -> Dict[str, str]:
    """
    Create a text document for the reranker.
    
    Args:
        text (str): The text content
        
    Returns:
        Dict: Document with text key
    """
    return {"text": text}


def create_image_document(image_url: str) -> Dict[str, str]:
    """
    Create an image document for the reranker.
    
    Args:
        image_url (str): URL or base64 encoded image
        
    Returns:
        Dict: Document with image key
    """
    return {"image": image_url}


def create_image_document_from_base64(base64_image: str) -> Dict[str, str]:
    """
    Create an image document from base64 encoded image.
    
    Args:
        base64_image (str): Base64 encoded image string
        
    Returns:
        Dict: Document with image key
    """
    return {"image": base64_image}


def get_top_results(response: Dict, top_k: int = 5) -> List[Dict]:
    """
    Extract top k results from reranker response.
    
    Args:
        response (Dict): Response from rerank_documents function
        top_k (int): Number of top results to return
        
    Returns:
        List[Dict]: Top k results with index and relevance_score
    """
    if 'results' not in response:
        return []
    
    results = response['results']
    return results[:top_k]


def get_relevance_scores(response: Dict) -> List[float]:
    """
    Extract relevance scores from reranker response.
    
    Args:
        response (Dict): Response from rerank_documents function
        
    Returns:
        List[float]: List of relevance scores
    """
    if 'results' not in response:
        return []
    
    return [result['relevance_score'] for result in response['results']]


def get_document_indices(response: Dict) -> List[int]:
    """
    Extract document indices from reranker response.
    
    Args:
        response (Dict): Response from rerank_documents function
        
    Returns:
        List[int]: List of document indices in ranked order
    """
    if 'results' not in response:
        return []
    
    return [result['index'] for result in response['results']] 