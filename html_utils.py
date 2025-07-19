import requests
from bs4 import BeautifulSoup
from typing import Optional, Dict
import re
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


def fetch_website_html(url: str) -> Optional[str]:
    """
    Fetch HTML content from a website using the crawler API.
    
    Args:
        url (str): Website URL
        
    Returns:
        Optional[str]: HTML content or None if failed
    """
    try:

        
        # Get crawler API URL from environment
        crawler_api_url = os.getenv("CRAWLER_API_URL")
        if not crawler_api_url:
            raise ValueError("CRAWLER_API_URL not found in environment variables")
        
        headers = {
            "Content-Type": "application/json"
        }
        data = {
            "url": url
        }
        
        response = requests.post(crawler_api_url, headers=headers, json=data, timeout=30)
        response.raise_for_status()
        
        result = response.json()
        
        # Extract HTML from the first page
        if 'pages' in result and len(result['pages']) > 0:
            html_content = result['pages'][0]['html']
            return html_content
        else:
            print(f"No pages found in response for {url}")
            return None
            
    except Exception as e:
        print(f"Error fetching HTML from {url}: {e}")
        return None


def extract_page_info(html: str) -> Dict:
    """
    Extract comprehensive page information from HTML.
    
    Args:
        html (str): HTML content
        
    Returns:
        Dict: Page information
    """
    soup = BeautifulSoup(html, 'html.parser')
    
    # Extract title
    title = ""
    title_tag = soup.find('title')
    if title_tag:
        title = title_tag.get_text().strip()
    
    # Extract meta description
    meta_description = ""
    meta_desc = soup.find('meta', attrs={'name': 'description'})
    if meta_desc and meta_desc.get('content'):
        meta_description = meta_desc['content'].strip()
    
    # Extract headings
    headings = []
    for tag in soup.find_all(['h1', 'h2', 'h3', 'h4', 'h5', 'h6']):
        headings.append({
            'level': tag.name,
            'text': tag.get_text().strip()
        })
    
    # Extract main content
    main_content = ""
    
    # Try to find main content area
    content_selectors = [
        'main',
        'article',
        '.content',
        '.main-content',
        '#content',
        '#main',
        '.post-content',
        '.entry-content'
    ]
    
    for selector in content_selectors:
        content_area = soup.select_one(selector)
        if content_area:
            main_content = content_area.get_text().strip()
            break
    
    # If no specific content area found, use body
    if not main_content:
        body = soup.find('body')
        if body:
            # Remove script and style tags
            for script in body(["script", "style"]):
                script.decompose()
            main_content = body.get_text().strip()
    
    # Extract links
    links = []
    for link in soup.find_all('a', href=True):
        links.append({
            'text': link.get_text().strip(),
            'href': link['href']
        })
    
    # Extract images
    images = []
    for img in soup.find_all('img', src=True):
        images.append({
            'alt': img.get('alt', ''),
            'src': img['src']
        })
    
    # Extract schema markup
    schema_markup = []
    for script in soup.find_all('script', type='application/ld+json'):
        try:
            import json
            schema = json.loads(script.string)
            schema_markup.append(schema)
        except:
            pass
    
    return {
        'title': title,
        'meta_description': meta_description,
        'headings': headings,
        'main_content': main_content,
        'links': links,
        'images': images,
        'schema_markup': schema_markup,
        'html': html
    }


def clean_html_for_llm(html: str) -> str:
    """
    Clean HTML for LLM processing by removing unnecessary elements.
    
    Args:
        html (str): Raw HTML
        
    Returns:
        str: Cleaned HTML
    """
    soup = BeautifulSoup(html, 'html.parser')
    
    # Remove script and style tags
    for script in soup(["script", "style"]):
        script.decompose()
    
    # Remove comments
    for comment in soup.find_all(string=lambda text: isinstance(text, str) and text.strip().startswith('<!--')):
        comment.extract()
    
    # Remove empty elements
    for tag in soup.find_all():
        if len(tag.get_text(strip=True)) == 0:
            tag.decompose()
    
    return str(soup)


def extract_keywords_from_content(content: str) -> list:
    """
    Extract potential keywords from content.
    
    Args:
        content (str): Text content
        
    Returns:
        list: List of potential keywords
    """
    # Simple keyword extraction (you could use more sophisticated methods)
    words = re.findall(r'\b\w+\b', content.lower())
    
    # Remove common stop words
    stop_words = {
        'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by',
        'is', 'are', 'was', 'were', 'be', 'been', 'being', 'have', 'has', 'had', 'do', 'does', 'did',
        'will', 'would', 'could', 'should', 'may', 'might', 'must', 'can', 'this', 'that', 'these', 'those'
    }
    
    # Count word frequency
    word_freq = {}
    for word in words:
        if word not in stop_words and len(word) > 3:
            word_freq[word] = word_freq.get(word, 0) + 1
    
    # Return top keywords
    sorted_keywords = sorted(word_freq.items(), key=lambda x: x[1], reverse=True)
    return [word for word, freq in sorted_keywords[:20]]


def validate_html_structure(html: str) -> Dict:
    """
    Validate HTML structure and provide suggestions.
    
    Args:
        html (str): HTML content
        
    Returns:
        Dict: Validation results
    """
    soup = BeautifulSoup(html, 'html.parser')
    
    issues = []
    suggestions = []
    
    # Check for title
    if not soup.find('title'):
        issues.append("Missing title tag")
        suggestions.append("Add a descriptive title tag")
    
    # Check for meta description
    if not soup.find('meta', attrs={'name': 'description'}):
        issues.append("Missing meta description")
        suggestions.append("Add a meta description tag")
    
    # Check for H1
    h1_tags = soup.find_all('h1')
    if len(h1_tags) == 0:
        issues.append("Missing H1 tag")
        suggestions.append("Add a main H1 heading")
    elif len(h1_tags) > 1:
        issues.append("Multiple H1 tags found")
        suggestions.append("Use only one H1 tag per page")
    
    # Check for proper heading hierarchy
    headings = soup.find_all(['h1', 'h2', 'h3', 'h4', 'h5', 'h6'])
    for i, heading in enumerate(headings):
        if i > 0:
            current_level = int(heading.name[1])
            prev_level = int(headings[i-1].name[1])
            if current_level > prev_level + 1:
                issues.append(f"Improper heading hierarchy: {headings[i-1].name} -> {heading.name}")
                suggestions.append("Maintain proper heading hierarchy (H1 -> H2 -> H3)")
    
    # Check for images without alt text
    images_without_alt = soup.find_all('img', alt='')
    if images_without_alt:
        issues.append(f"{len(images_without_alt)} images without alt text")
        suggestions.append("Add descriptive alt text to all images")
    
    # Check for internal links
    internal_links = []
    for link in soup.find_all('a', href=True):
        href = link['href']
        if href.startswith('/') or href.startswith('#'):
            internal_links.append(link.get_text().strip())
    
    if not internal_links:
        suggestions.append("Add internal links to improve site navigation")
    
    return {
        'issues': issues,
        'suggestions': suggestions,
        'total_headings': len(headings),
        'total_images': len(soup.find_all('img')),
        'total_links': len(soup.find_all('a')),
        'internal_links': len(internal_links)
    }


def create_html_template(title: str, content: str, meta_description: str = "") -> str:
    """
    Create a basic HTML template.
    
    Args:
        title (str): Page title
        content (str): Main content
        meta_description (str): Meta description
        
    Returns:
        str: HTML template
    """
    template = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title}</title>
    {f'<meta name="description" content="{meta_description}">' if meta_description else ''}
</head>
<body>
    {content}
</body>
</html>
    """
    return template.strip()


def example_usage():
    """Example usage of HTML utilities."""
    
    # Example HTML
    sample_html = """
    <html>
    <head>
        <title>Sample Website</title>
        <meta name="description" content="A sample website for testing">
    </head>
    <body>
        <h1>Welcome to Our Website</h1>
        <p>This is a sample website with some content.</p>
        <h2>About Us</h2>
        <p>We provide excellent services to our customers.</p>
        <a href="/about">Learn More</a>
    </body>
    </html>
    """
    
    # Extract page info
    page_info = extract_page_info(sample_html)
    print("Page Information:")
    print(f"Title: {page_info['title']}")
    print(f"Meta Description: {page_info['meta_description']}")
    print(f"Headings: {len(page_info['headings'])}")
    print(f"Links: {len(page_info['links'])}")
    
    # Validate HTML
    validation = validate_html_structure(sample_html)
    print("\nHTML Validation:")
    print(f"Issues: {validation['issues']}")
    print(f"Suggestions: {validation['suggestions']}")
    
    # Extract keywords
    keywords = extract_keywords_from_content(page_info['main_content'])
    print(f"\nPotential Keywords: {keywords[:10]}")


if __name__ == "__main__":
    example_usage() 