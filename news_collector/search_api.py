"""
Simple Search API - Search the web for anything
"""
from duckduckgo_search import DDGS


def search(query, max_results=10):
    """
    Search the web for anything
    
    Args:
        query: Search query (e.g., "Apple stock price", "Tesla news")
        max_results: Number of results to return (default 10)
    
    Returns:
        List of search results with title, url, snippet
    """
    results = []
    
    try:
        with DDGS() as ddgs:
            search_results = ddgs.text(query, max_results=max_results)
            
            for r in search_results:
                results.append({
                    'title': r.get('title', ''),
                    'url': r.get('href', ''),
                    'snippet': r.get('body', '')
                })
    except Exception as e:
        print(f"Search error: {e}")
    
    return results
