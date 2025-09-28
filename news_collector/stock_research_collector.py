"""
Stock Research News Collector
Collect financial research and analyst recommendations from major financial news sources
"""

import json
import time
from datetime import datetime, timedelta
from typing import List, Dict, Optional
from urllib.parse import urljoin, quote
import logging

from .base import BaseNewsCollector, NewsItem, CollectionResult

logger = logging.getLogger(__name__)

class StockResearchCollector(BaseNewsCollector):
    """
    Collect stock research from multiple financial news sources:
    - Yahoo Finance
    - MarketWatch  
    - Seeking Alpha
    - Reuters
    - Bloomberg (limited public access)
    - Financial Times
    - CNBC
    """
    
    def __init__(self, api_keys: Dict[str, str] = None):
        """
        Initialize stock research collector
        
        Args:
            api_keys: Dictionary of API keys for various sources
        """
        super().__init__(
            name="Stock Research Collector",
            base_url="https://finance.yahoo.com",
            rate_limit_per_hour=200
        )
        
        self.api_keys = api_keys or {}
        
        # Configure source endpoints
        self.sources = {
            'yahoo_finance': {
                'base_url': 'https://finance.yahoo.com',
                'news_endpoint': '/rss/headline',
                'stock_endpoint': '/quote/{symbol}/news',
                'requires_api': False
            },
            'marketwatch': {
                'base_url': 'https://www.marketwatch.com',
                'news_endpoint': '/rss/topstories',
                'stock_endpoint': '/investing/stock/{symbol}',
                'requires_api': False
            },
            'seeking_alpha': {
                'base_url': 'https://seekingalpha.com',
                'news_endpoint': '/api/v3/news',
                'stock_endpoint': '/api/v3/symbols/{symbol}/news',
                'requires_api': True
            },
            'reuters': {
                'base_url': 'https://www.reuters.com',
                'news_endpoint': '/business/finance',
                'stock_endpoint': '/companies/{symbol}',
                'requires_api': False
            },
            'cnbc': {
                'base_url': 'https://www.cnbc.com',
                'news_endpoint': '/id/10000664/device/rss/rss.html',
                'stock_endpoint': '/quotes/{symbol}',
                'requires_api': False
            }
        }
    
    def collect_recent_news(self, 
                           hours_back: int = 24,
                           max_items: int = 100) -> CollectionResult:
        """
        Collect recent financial news from all sources
        
        Args:
            hours_back: Hours to look back for news
            max_items: Maximum items to collect per source
            
        Returns:
            CollectionResult with collected news
        """
        start_time = time.time()
        all_items = []
        errors = []
        
        logger.info(f"Collecting recent financial news ({hours_back} hours back)")
        
        # Collect from each source
        for source_name, config in self.sources.items():
            try:
                logger.info(f"Collecting from {source_name}...")
                items = self._collect_from_source(source_name, config, hours_back, max_items)
                all_items.extend(items)
                logger.info(f"Collected {len(items)} items from {source_name}")
                
            except Exception as e:
                error_msg = f"Error collecting from {source_name}: {str(e)}"
                logger.error(error_msg)
                errors.append(error_msg)
                
            # Rate limiting between sources
            time.sleep(1)
        
        # Deduplicate and process
        unique_items = self._deduplicate_by_url(all_items)
        
        execution_time = time.time() - start_time
        self.stats['items_collected'] += len(unique_items)
        
        return CollectionResult(
            success=len(errors) < len(self.sources),  # Success if less than all sources failed
            items_collected=len(unique_items),
            items=unique_items,
            errors=errors,
            execution_time=execution_time,
            metadata={'sources_used': list(self.sources.keys())}
        )
    
    def collect_stock_news(self, 
                          stock_symbol: str,
                          hours_back: int = 24,
                          max_items: int = 50) -> CollectionResult:
        """
        Collect news for a specific stock symbol
        
        Args:
            stock_symbol: Stock ticker symbol (e.g., 'AAPL', 'TSLA')
            hours_back: Hours to look back
            max_items: Maximum items to collect
            
        Returns:
            CollectionResult with stock-specific news
        """
        start_time = time.time()
        all_items = []
        errors = []
        
        logger.info(f"Collecting news for stock: {stock_symbol}")
        
        # Yahoo Finance stock-specific news
        yahoo_items = self._collect_yahoo_stock_news(stock_symbol, hours_back, max_items)
        all_items.extend(yahoo_items)
        
        # MarketWatch stock news
        mw_items = self._collect_marketwatch_stock_news(stock_symbol, hours_back, max_items)
        all_items.extend(mw_items)
        
        # Seeking Alpha (if API key available)
        if 'seeking_alpha' in self.api_keys:
            sa_items = self._collect_seeking_alpha_stock_news(stock_symbol, hours_back, max_items)
            all_items.extend(sa_items)
        
        # General news search for the stock
        search_items = self._search_stock_mentions(stock_symbol, hours_back, max_items)
        all_items.extend(search_items)
        
        # Deduplicate and filter
        unique_items = self._deduplicate_by_url(all_items)
        relevant_items = self._filter_stock_relevance(unique_items, stock_symbol)
        
        execution_time = time.time() - start_time
        self.stats['items_collected'] += len(relevant_items)
        
        return CollectionResult(
            success=len(relevant_items) > 0,
            items_collected=len(relevant_items),
            items=relevant_items,
            errors=errors,
            execution_time=execution_time,
            metadata={'stock_symbol': stock_symbol}
        )
    
    def _collect_from_source(self, 
                           source_name: str, 
                           config: Dict, 
                           hours_back: int, 
                           max_items: int) -> List[NewsItem]:
        """Collect news from a specific source"""
        
        if source_name == 'yahoo_finance':
            return self._collect_yahoo_general_news(hours_back, max_items)
        elif source_name == 'marketwatch':
            return self._collect_marketwatch_general_news(hours_back, max_items)
        elif source_name == 'reuters':
            return self._collect_reuters_news(hours_back, max_items)
        elif source_name == 'cnbc':
            return self._collect_cnbc_news(hours_back, max_items)
        else:
            return []
    
    def _collect_yahoo_general_news(self, hours_back: int, max_items: int) -> List[NewsItem]:
        """Collect general financial news from Yahoo Finance"""
        items = []
        
        try:
            # Yahoo Finance RSS feed for financial news
            url = "https://finance.yahoo.com/rss/headline"
            response = self._make_request(url)
            
            if response:
                # Parse RSS feed (simplified - you'd use feedparser in production)
                # For now, we'll collect via their web scraping approach
                items.extend(self._scrape_yahoo_finance_news(hours_back, max_items))
                
        except Exception as e:
            logger.error(f"Error collecting Yahoo Finance news: {e}")
        
        return items[:max_items]
    
    def _collect_yahoo_stock_news(self, symbol: str, hours_back: int, max_items: int) -> List[NewsItem]:
        """Collect Yahoo Finance news for specific stock"""
        items = []
        
        try:
            # Yahoo Finance stock news endpoint (public API)
            url = f"https://query1.finance.yahoo.com/v1/finance/search"
            params = {
                'q': symbol,
                'lang': 'en-US',
                'region': 'US',
                'quotesCount': 1,
                'newsCount': max_items
            }
            
            response = self._make_request(url, params=params)
            
            if response and response.status_code == 200:
                data = response.json()
                
                if 'news' in data:
                    for article in data['news'][:max_items]:
                        try:
                            published_time = datetime.fromtimestamp(article.get('providerPublishTime', 0))
                            cutoff_time = datetime.now() - timedelta(hours=hours_back)
                            
                            if published_time >= cutoff_time:
                                item = NewsItem(
                                    title=article.get('title', ''),
                                    content=None,  # Would need separate call to get full content
                                    url=article.get('link', ''),
                                    published_at=published_time,
                                    author=article.get('publisher', ''),
                                    summary=article.get('summary', ''),
                                    external_id=article.get('uuid'),
                                    category='stock_news',
                                    stock_symbols=[symbol.upper()],
                                    raw_data=article
                                )
                                items.append(item)
                                
                        except Exception as e:
                            logger.error(f"Error parsing Yahoo Finance article: {e}")
                            continue
                            
        except Exception as e:
            logger.error(f"Error collecting Yahoo Finance stock news for {symbol}: {e}")
        
        return items
    
    def _collect_marketwatch_stock_news(self, symbol: str, hours_back: int, max_items: int) -> List[NewsItem]:
        """Collect MarketWatch news for specific stock"""
        items = []
        
        try:
            # MarketWatch stock page scraping
            url = f"https://www.marketwatch.com/investing/stock/{symbol.lower()}"
            response = self._make_request(url)
            
            if response and response.status_code == 200:
                # Parse HTML for news articles (simplified approach)
                # In production, you'd use BeautifulSoup or similar
                items.extend(self._parse_marketwatch_stock_page(response.text, symbol, hours_back, max_items))
                
        except Exception as e:
            logger.error(f"Error collecting MarketWatch news for {symbol}: {e}")
        
        return items
    
    def _collect_marketwatch_general_news(self, hours_back: int, max_items: int) -> List[NewsItem]:
        """Collect general MarketWatch news"""
        items = []
        
        try:
            # MarketWatch top stories RSS
            url = "https://feeds.content.dowjones.io/public/rss/mw_topstories"
            response = self._make_request(url)
            
            if response and response.status_code == 200:
                # Parse RSS feed
                items.extend(self._parse_marketwatch_rss(response.text, hours_back, max_items))
                
        except Exception as e:
            logger.error(f"Error collecting MarketWatch general news: {e}")
        
        return items[:max_items]
    
    def _collect_seeking_alpha_stock_news(self, symbol: str, hours_back: int, max_items: int) -> List[NewsItem]:
        """Collect Seeking Alpha news for specific stock (requires API key)"""
        items = []
        
        if 'seeking_alpha' not in self.api_keys:
            logger.warning("Seeking Alpha API key not provided")
            return items
        
        try:
            # Seeking Alpha API (if available)
            url = f"https://seekingalpha.com/api/v3/symbols/{symbol}/news"
            headers = {
                'Authorization': f'Bearer {self.api_keys["seeking_alpha"]}',
                'Accept': 'application/json'
            }
            
            response = self._make_request(url, headers=headers)
            
            if response and response.status_code == 200:
                data = response.json()
                
                for article in data.get('data', [])[:max_items]:
                    try:
                        published_time = self._parse_date(article.get('publishedAt'))
                        if not published_time:
                            continue
                            
                        cutoff_time = datetime.now() - timedelta(hours=hours_back)
                        
                        if published_time >= cutoff_time:
                            item = NewsItem(
                                title=article.get('title', ''),
                                content=article.get('content', ''),
                                url=f"https://seekingalpha.com{article.get('uri', '')}",
                                published_at=published_time,
                                author=article.get('author', {}).get('nick', ''),
                                summary=article.get('summary', ''),
                                external_id=str(article.get('id')),
                                category='analyst_research',
                                stock_symbols=[symbol.upper()],
                                raw_data=article
                            )
                            items.append(item)
                            
                    except Exception as e:
                        logger.error(f"Error parsing Seeking Alpha article: {e}")
                        continue
                        
        except Exception as e:
            logger.error(f"Error collecting Seeking Alpha news for {symbol}: {e}")
        
        return items
    
    def _collect_reuters_news(self, hours_back: int, max_items: int) -> List[NewsItem]:
        """Collect Reuters business news"""
        items = []
        
        try:
            # Reuters business news RSS
            url = "https://www.reutersagency.com/feed/?best-topics=business-finance&post_type=best"
            response = self._make_request(url)
            
            if response and response.status_code == 200:
                items.extend(self._parse_reuters_rss(response.text, hours_back, max_items))
                
        except Exception as e:
            logger.error(f"Error collecting Reuters news: {e}")
        
        return items[:max_items]
    
    def _collect_cnbc_news(self, hours_back: int, max_items: int) -> List[NewsItem]:
        """Collect CNBC financial news"""
        items = []
        
        try:
            # CNBC RSS feed
            url = "https://www.cnbc.com/id/100003114/device/rss/rss.html"
            response = self._make_request(url)
            
            if response and response.status_code == 200:
                items.extend(self._parse_cnbc_rss(response.text, hours_back, max_items))
                
        except Exception as e:
            logger.error(f"Error collecting CNBC news: {e}")
        
        return items[:max_items]
    
    def _search_stock_mentions(self, symbol: str, hours_back: int, max_items: int) -> List[NewsItem]:
        """Search for stock mentions across multiple sources"""
        items = []
        
        search_queries = [
            f'"{symbol}" stock',
            f'"{symbol}" earnings',
            f'"{symbol}" analyst',
            f'"{symbol}" price target'
        ]
        
        for query in search_queries:
            try:
                # Use Google Finance or Yahoo Finance search
                search_items = self._search_financial_news(query, hours_back, max_items // len(search_queries))
                items.extend(search_items)
                
            except Exception as e:
                logger.error(f"Error searching for '{query}': {e}")
        
        return items
    
    def _search_financial_news(self, query: str, hours_back: int, max_items: int) -> List[NewsItem]:
        """Search financial news using Yahoo Finance search"""
        items = []
        
        try:
            # Yahoo Finance search API
            url = "https://query1.finance.yahoo.com/v1/finance/search"
            params = {
                'q': query,
                'lang': 'en-US',
                'region': 'US',
                'quotesCount': 0,
                'newsCount': max_items
            }
            
            response = self._make_request(url, params=params)
            
            if response and response.status_code == 200:
                data = response.json()
                
                for article in data.get('news', [])[:max_items]:
                    try:
                        published_time = datetime.fromtimestamp(article.get('providerPublishTime', 0))
                        cutoff_time = datetime.now() - timedelta(hours=hours_back)
                        
                        if published_time >= cutoff_time:
                            # Extract stock symbols from title and summary
                            text = f"{article.get('title', '')} {article.get('summary', '')}"
                            stock_symbols = self._extract_stock_symbols(text)
                            
                            item = NewsItem(
                                title=article.get('title', ''),
                                content=None,
                                url=article.get('link', ''),
                                published_at=published_time,
                                author=article.get('publisher', ''),
                                summary=article.get('summary', ''),
                                external_id=article.get('uuid'),
                                category='financial_news',
                                stock_symbols=stock_symbols,
                                raw_data=article
                            )
                            items.append(item)
                            
                    except Exception as e:
                        logger.error(f"Error parsing search result: {e}")
                        continue
                        
        except Exception as e:
            logger.error(f"Error searching for '{query}': {e}")
        
        return items
    
    def _deduplicate_by_url(self, items: List[NewsItem]) -> List[NewsItem]:
        """Remove duplicate items based on URL"""
        seen_urls = set()
        unique_items = []
        
        for item in items:
            if item.url not in seen_urls:
                seen_urls.add(item.url)
                unique_items.append(item)
        
        return unique_items
    
    def _filter_stock_relevance(self, items: List[NewsItem], symbol: str) -> List[NewsItem]:
        """Filter items for relevance to specific stock"""
        relevant_items = []
        symbol_variations = [symbol.upper(), symbol.lower(), f"${symbol.upper()}"]
        
        for item in items:
            text = f"{item.title} {item.summary or ''}".lower()
            
            # Check if stock symbol appears in title or summary
            if any(var.lower() in text for var in symbol_variations):
                # Boost relevance if in stock_symbols list
                if item.stock_symbols and symbol.upper() in item.stock_symbols:
                    relevant_items.insert(0, item)  # Put at front
                else:
                    relevant_items.append(item)
        
        return relevant_items
    
    # Simplified parsing methods (in production, use proper HTML/XML parsers)
    def _scrape_yahoo_finance_news(self, hours_back: int, max_items: int) -> List[NewsItem]:
        """Scrape Yahoo Finance news page"""
        # Placeholder - implement with BeautifulSoup
        return []
    
    def _parse_marketwatch_stock_page(self, html: str, symbol: str, hours_back: int, max_items: int) -> List[NewsItem]:
        """Parse MarketWatch stock page for news"""
        # Placeholder - implement with BeautifulSoup
        return []
    
    def _parse_marketwatch_rss(self, xml: str, hours_back: int, max_items: int) -> List[NewsItem]:
        """Parse MarketWatch RSS feed"""
        # Placeholder - implement with feedparser
        return []
    
    def _parse_reuters_rss(self, xml: str, hours_back: int, max_items: int) -> List[NewsItem]:
        """Parse Reuters RSS feed"""
        # Placeholder - implement with feedparser
        return []
    
    def _parse_cnbc_rss(self, xml: str, hours_back: int, max_items: int) -> List[NewsItem]:
        """Parse CNBC RSS feed"""
        # Placeholder - implement with feedparser
        return []

# Example usage and testing
if __name__ == "__main__":
    # Initialize collector
    collector = StockResearchCollector()
    
    # Test general news collection
    result = collector.collect_recent_news(hours_back=24, max_items=20)
    print(f"Collected {result.items_collected} general news items")
    
    # Test stock-specific news collection
    stock_result = collector.collect_stock_news("AAPL", hours_back=24, max_items=10)
    print(f"Collected {stock_result.items_collected} AAPL news items")
    
    # Print statistics
    print("Collector Statistics:", collector.get_stats())
