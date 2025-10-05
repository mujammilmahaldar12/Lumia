"""
5 News API Functions - Each searches a different news source
"""
import os
import requests
from datetime import datetime, timedelta
from dotenv import load_dotenv

load_dotenv()

NEWSAPI_KEY = os.getenv('NEWSAPI_KEY')
FINNHUB_KEY = os.getenv('FINNHUB_KEY')
POLYGON_KEY = os.getenv('POLYGON_KEY')
CRYPTOPANIC_KEY = os.getenv('CRYPTOPANIC_KEY')
ALPHAVANTAGE_KEY = os.getenv('ALPHAVANTAGE_KEY')


def get_news_from_newsapi(company, max_results=10):
    """
    API 1: NewsAPI.org - Global news from 80,000+ sources
    
    Args:
        company: Company name to search for
        max_results: Number of articles (default 10)
    
    Returns:
        List of news articles
    """
    articles = []
    
    try:
        url = "https://newsapi.org/v2/everything"
        params = {
            'q': company,
            'apiKey': NEWSAPI_KEY,
            'language': 'en',
            'sortBy': 'publishedAt',
            'pageSize': max_results
        }
        
        response = requests.get(url, params=params, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            
            for article in data.get('articles', [])[:max_results]:
                articles.append({
                    'title': article.get('title', ''),
                    'description': article.get('description', ''),
                    'url': article.get('url', ''),
                    'source': article.get('source', {}).get('name', 'NewsAPI'),
                    'date': article.get('publishedAt', ''),
                    'image': article.get('urlToImage', ''),
                    'api': 'NewsAPI'
                })
    except Exception as e:
        print(f"NewsAPI error: {e}")
    
    return articles


def get_news_from_finnhub(symbol, max_results=10):
    """
    API 2: Finnhub - Financial news and stock market data
    
    Args:
        symbol: Stock symbol (e.g., "AAPL", "TSLA")
        max_results: Number of articles (default 10)
    
    Returns:
        List of news articles
    """
    articles = []
    
    try:
        from_date = (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d')
        to_date = datetime.now().strftime('%Y-%m-%d')
        
        url = "https://finnhub.io/api/v1/company-news"
        params = {
            'symbol': symbol,
            'from': from_date,
            'to': to_date,
            'token': FINNHUB_KEY
        }
        
        response = requests.get(url, params=params, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            
            for item in data[:max_results]:
                articles.append({
                    'title': item.get('headline', ''),
                    'description': item.get('summary', ''),
                    'url': item.get('url', ''),
                    'source': item.get('source', 'Finnhub'),
                    'date': datetime.fromtimestamp(item.get('datetime', 0)).isoformat(),
                    'image': item.get('image', ''),
                    'api': 'Finnhub'
                })
    except Exception as e:
        print(f"Finnhub error: {e}")
    
    return articles


def get_news_from_polygon(symbol, max_results=10):
    """
    API 3: Polygon.io - US stock market news
    
    Args:
        symbol: Stock symbol (e.g., "AAPL", "TSLA")
        max_results: Number of articles (default 10)
    
    Returns:
        List of news articles
    """
    articles = []
    
    try:
        url = f"https://api.polygon.io/v2/reference/news"
        params = {
            'ticker': symbol,
            'limit': max_results,
            'apiKey': POLYGON_KEY
        }
        
        response = requests.get(url, params=params, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            
            for item in data.get('results', [])[:max_results]:
                articles.append({
                    'title': item.get('title', ''),
                    'description': item.get('description', ''),
                    'url': item.get('article_url', ''),
                    'source': item.get('publisher', {}).get('name', 'Polygon'),
                    'date': item.get('published_utc', ''),
                    'image': item.get('image_url', ''),
                    'api': 'Polygon'
                })
    except Exception as e:
        print(f"Polygon error: {e}")
    
    return articles


def get_news_from_cryptopanic(currency='BTC', max_results=10):
    """
    API 4: CryptoPanic - Cryptocurrency news
    
    Args:
        currency: Crypto currency code (e.g., "BTC", "ETH")
        max_results: Number of articles (default 10)
    
   Returns:
        List of news articles
    """
    articles = []
    
    try:
        url = "https://cryptopanic.com/api/v1/posts/"
        params = {
            'auth_token': CRYPTOPANIC_KEY,
            'currencies': currency,
            'filter': 'hot',
            'public': 'true'
        }
        
        response = requests.get(url, params=params, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            
            for item in data.get('results', [])[:max_results]:
                articles.append({
                    'title': item.get('title', ''),
                    'description': '',
                    'url': item.get('url', ''),
                    'source': item.get('source', {}).get('title', 'CryptoPanic'),
                    'date': item.get('published_at', ''),
                    'image': '',
                    'api': 'CryptoPanic'
                })
    except Exception as e:
        print(f"CryptoPanic error: {e}")
    
    return articles


def get_news_from_alphavantage(symbol, max_results=10):
    """
    API 5: Alpha Vantage - Market news and sentiment
    
    Args:
        symbol: Stock symbol (e.g., "AAPL", "TSLA") or topic
        max_results: Number of articles (default 10)
    
    Returns:
        List of news articles
    """
    articles = []
    
    try:
        url = "https://www.alphavantage.co/query"
        params = {
            'function': 'NEWS_SENTIMENT',
            'tickers': symbol,
            'apikey': ALPHAVANTAGE_KEY,
            'limit': max_results
        }
        
        response = requests.get(url, params=params, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            
            for item in data.get('feed', [])[:max_results]:
                articles.append({
                    'title': item.get('title', ''),
                    'description': item.get('summary', ''),
                    'url': item.get('url', ''),
                    'source': item.get('source', 'AlphaVantage'),
                    'date': item.get('time_published', ''),
                    'image': item.get('banner_image', ''),
                    'sentiment': item.get('overall_sentiment_label', ''),
                    'api': 'AlphaVantage'
                })
    except Exception as e:
        print(f"AlphaVantage error: {e}")
    
    return articles
