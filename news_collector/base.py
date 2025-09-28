"""
Base News Collector Framework
Abstract base classes and utilities for all news collectors
"""

import time
import logging
import requests
from abc import ABC, abstractmethod
from typing import List, Dict, Optional, Any, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass
from urllib.parse import urljoin, urlparse
import hashlib
import json
import re
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class NewsItem:
    """Standardized news item structure"""
    title: str
    content: Optional[str]
    url: str
    published_at: datetime
    author: Optional[str] = None
    summary: Optional[str] = None
    external_id: Optional[str] = None
    category: Optional[str] = None
    raw_data: Optional[Dict] = None
    stock_symbols: Optional[List[str]] = None

@dataclass 
class CollectionResult:
    """Result of a collection operation"""
    success: bool
    items_collected: int
    items: List[NewsItem]
    errors: List[str]
    execution_time: float
    metadata: Optional[Dict] = None

class RateLimiter:
    """Simple rate limiter for API calls"""
    
    def __init__(self, max_calls: int, time_window: int = 3600):
        """
        Args:
            max_calls: Maximum number of calls allowed
            time_window: Time window in seconds (default: 1 hour)
        """
        self.max_calls = max_calls
        self.time_window = time_window
        self.calls = []
    
    def wait_if_needed(self):
        """Wait if rate limit would be exceeded"""
        now = time.time()
        
        # Remove old calls outside the time window
        self.calls = [call_time for call_time in self.calls 
                     if now - call_time < self.time_window]
        
        # Check if we need to wait
        if len(self.calls) >= self.max_calls:
            oldest_call = min(self.calls)
            wait_time = self.time_window - (now - oldest_call)
            if wait_time > 0:
                logger.info(f"Rate limit reached. Waiting {wait_time:.2f} seconds...")
                time.sleep(wait_time)
        
        # Record this call
        self.calls.append(now)

class RequestsHandler:
    """Enhanced requests handler with retries and error handling"""
    
    def __init__(self, 
                 timeout: int = 30,
                 max_retries: int = 3,
                 backoff_factor: float = 0.3,
                 user_agent: str = None):
        
        self.session = requests.Session()
        self.timeout = timeout
        
        # Configure retries
        retry_strategy = Retry(
            total=max_retries,
            backoff_factor=backoff_factor,
            status_forcelist=[429, 500, 502, 503, 504],
        )
        adapter = HTTPAdapter(max_retries=retry_strategy)
        self.session.mount("http://", adapter)
        self.session.mount("https://", adapter)
        
        # Set user agent
        if user_agent:
            self.session.headers.update({'User-Agent': user_agent})
        else:
            self.session.headers.update({
                'User-Agent': 'Financial-News-Collector/1.0 (Educational Research Purpose)'
            })
    
    def get(self, url: str, **kwargs) -> requests.Response:
        """Make GET request with error handling"""
        try:
            response = self.session.get(url, timeout=self.timeout, **kwargs)
            response.raise_for_status()
            return response
        except requests.exceptions.RequestException as e:
            logger.error(f"Request failed for {url}: {e}")
            raise
    
    def post(self, url: str, **kwargs) -> requests.Response:
        """Make POST request with error handling"""
        try:
            response = self.session.post(url, timeout=self.timeout, **kwargs)
            response.raise_for_status()
            return response
        except requests.exceptions.RequestException as e:
            logger.error(f"POST request failed for {url}: {e}")
            raise

class BaseNewsCollector(ABC):
    """Abstract base class for all news collectors"""
    
    def __init__(self, 
                 name: str,
                 base_url: str,
                 rate_limit_per_hour: int = 100,
                 api_key: Optional[str] = None):
        """
        Initialize base collector
        
        Args:
            name: Collector name
            base_url: Base URL for the news source
            rate_limit_per_hour: Maximum requests per hour
            api_key: API key if required
        """
        self.name = name
        self.base_url = base_url
        self.api_key = api_key
        
        # Initialize components
        self.rate_limiter = RateLimiter(rate_limit_per_hour)
        self.requests_handler = RequestsHandler()
        
        # Collection statistics
        self.stats = {
            'total_requests': 0,
            'successful_requests': 0,
            'failed_requests': 0,
            'items_collected': 0,
            'errors': []
        }
        
        logger.info(f"Initialized {self.name} collector")
    
    @abstractmethod
    def collect_recent_news(self, 
                           hours_back: int = 24,
                           max_items: int = 100) -> CollectionResult:
        """
        Collect recent news items
        
        Args:
            hours_back: How many hours back to collect news
            max_items: Maximum number of items to collect
            
        Returns:
            CollectionResult with collected news items
        """
        pass
    
    @abstractmethod
    def collect_stock_news(self, 
                          stock_symbol: str,
                          hours_back: int = 24,
                          max_items: int = 50) -> CollectionResult:
        """
        Collect news for a specific stock
        
        Args:
            stock_symbol: Stock ticker symbol
            hours_back: How many hours back to collect
            max_items: Maximum number of items to collect
            
        Returns:
            CollectionResult with stock-specific news
        """
        pass
    
    def _make_request(self, url: str, **kwargs) -> Optional[requests.Response]:
        """
        Make a rate-limited request
        
        Args:
            url: URL to request
            **kwargs: Additional arguments for requests
            
        Returns:
            Response object or None if failed
        """
        self.rate_limiter.wait_if_needed()
        self.stats['total_requests'] += 1
        
        try:
            response = self.requests_handler.get(url, **kwargs)
            self.stats['successful_requests'] += 1
            return response
        except Exception as e:
            self.stats['failed_requests'] += 1
            self.stats['errors'].append(str(e))
            logger.error(f"Request failed: {e}")
            return None
    
    def _extract_stock_symbols(self, text: str) -> List[str]:
        """
        Extract stock symbols from text using common patterns
        
        Args:
            text: Text to search for stock symbols
            
        Returns:
            List of found stock symbols
        """
        # Common stock symbol patterns
        patterns = [
            r'\b[A-Z]{1,5}\b',  # 1-5 uppercase letters
            r'\$[A-Z]{1,5}\b',  # $ prefix
            r'\b[A-Z]{1,5}\.NS\b',  # NSE stocks
            r'\b[A-Z]{1,5}\.BO\b',  # BSE stocks
        ]
        
        symbols = set()
        for pattern in patterns:
            matches = re.findall(pattern, text.upper())
            symbols.update(matches)
        
        # Filter out common words that match the pattern
        exclude_words = {'THE', 'AND', 'FOR', 'ARE', 'BUT', 'NOT', 'YOU', 'ALL', 'CAN', 'HER', 'WAS', 'ONE', 'OUR', 'HAD', 'BY', 'ITS', 'IT', 'IS', 'BE', 'TO', 'OF', 'AS', 'AT', 'ON', 'IN', 'UP', 'NO', 'IF', 'SO', 'MY', 'ME', 'AM', 'AN', 'US', 'OR', 'DO', 'GO', 'HE', 'WE', 'SHE', 'HIM', 'HIS', 'WHO', 'HOW', 'NOW', 'NEW', 'GET', 'GOT', 'HAS', 'HAD', 'SEE', 'SAW', 'SAY', 'PUT', 'SET', 'RUN', 'WIN', 'END', 'TOP', 'USE', 'WAY', 'WHY', 'YES', 'TRY', 'FEW', 'MAY', 'OLD', 'BIG', 'OUT', 'OFF', 'ADD', 'AGO', 'BOX', 'BUY', 'DAY', 'EAT', 'FAR', 'FIX', 'GAS', 'JOB', 'LAW', 'LOT', 'LOW', 'MAN', 'MAP', 'MAX', 'MIX', 'NET', 'OIL', 'OPT', 'PAY', 'PER', 'POP', 'PRO', 'RED', 'SEA', 'SET', 'SIX', 'SUN', 'TAB', 'TAX', 'TEN', 'TOP', 'TWO', 'VIA', 'WAR', 'WEB', 'WIN', 'YET', 'ZIP'}
        
        return [symbol for symbol in symbols if symbol not in exclude_words]
    
    def _clean_text(self, text: str) -> str:
        """
        Clean and normalize text content
        
        Args:
            text: Raw text to clean
            
        Returns:
            Cleaned text
        """
        if not text:
            return ""
        
        # Remove extra whitespace
        text = ' '.join(text.split())
        
        # Remove HTML tags if present
        text = re.sub(r'<[^>]+>', '', text)
        
        # Remove special characters but keep basic punctuation
        text = re.sub(r'[^\w\s.,!?;:\-\(\)\[\]\"\'%$]+', ' ', text)
        
        # Fix spacing around punctuation
        text = re.sub(r'\s+([.,!?;:])', r'\1', text)
        
        return text.strip()
    
    def _generate_content_hash(self, title: str, content: str = "") -> str:
        """
        Generate a hash for deduplication
        
        Args:
            title: Article title
            content: Article content
            
        Returns:
            Content hash string
        """
        combined = f"{title}|{content}"
        return hashlib.md5(combined.encode('utf-8')).hexdigest()
    
    def _parse_date(self, date_str: str) -> Optional[datetime]:
        """
        Parse various date formats into datetime object
        
        Args:
            date_str: Date string to parse
            
        Returns:
            Datetime object or None if parsing fails
        """
        if not date_str:
            return None
        
        # Common date formats
        formats = [
            "%Y-%m-%dT%H:%M:%SZ",
            "%Y-%m-%dT%H:%M:%S.%fZ",
            "%Y-%m-%d %H:%M:%S",
            "%Y-%m-%d",
            "%m/%d/%Y %H:%M:%S",
            "%m/%d/%Y",
            "%d/%m/%Y",
            "%B %d, %Y",
            "%b %d, %Y",
        ]
        
        for fmt in formats:
            try:
                return datetime.strptime(date_str.strip(), fmt)
            except ValueError:
                continue
        
        logger.warning(f"Could not parse date: {date_str}")
        return None
    
    def get_stats(self) -> Dict:
        """Get collection statistics"""
        return self.stats.copy()
    
    def reset_stats(self):
        """Reset collection statistics"""
        self.stats = {
            'total_requests': 0,
            'successful_requests': 0,
            'failed_requests': 0,
            'items_collected': 0,
            'errors': []
        }

class NewsProcessor:
    """Process and enrich collected news items"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__ + '.NewsProcessor')
    
    def deduplicate_news(self, items: List[NewsItem]) -> List[NewsItem]:
        """Remove duplicate news items"""
        seen_hashes = set()
        unique_items = []
        
        for item in items:
            content_hash = hashlib.md5(
                f"{item.title}|{item.url}".encode('utf-8')
            ).hexdigest()
            
            if content_hash not in seen_hashes:
                seen_hashes.add(content_hash)
                unique_items.append(item)
        
        self.logger.info(f"Deduplicated {len(items)} -> {len(unique_items)} items")
        return unique_items
    
    def filter_by_relevance(self, 
                           items: List[NewsItem], 
                           keywords: List[str] = None) -> List[NewsItem]:
        """Filter news items by relevance keywords"""
        if not keywords:
            return items
        
        keywords_lower = [kw.lower() for kw in keywords]
        filtered_items = []
        
        for item in items:
            text = f"{item.title} {item.content or ''} {item.summary or ''}".lower()
            
            if any(keyword in text for keyword in keywords_lower):
                filtered_items.append(item)
        
        self.logger.info(f"Filtered {len(items)} -> {len(filtered_items)} items by relevance")
        return filtered_items
    
    def sort_by_relevance_and_time(self, items: List[NewsItem]) -> List[NewsItem]:
        """Sort items by publication time (newest first)"""
        return sorted(items, key=lambda x: x.published_at, reverse=True)

# Utility functions
def extract_domain(url: str) -> str:
    """Extract domain from URL"""
    parsed = urlparse(url)
    return parsed.netloc

def is_business_hours() -> bool:
    """Check if current time is during business hours (9 AM - 4 PM EST)"""
    now = datetime.now()
    return 9 <= now.hour <= 16

def get_market_hours_today() -> Tuple[datetime, datetime]:
    """Get market open and close times for today"""
    today = datetime.now().date()
    market_open = datetime.combine(today, datetime.min.time().replace(hour=9, minute=30))
    market_close = datetime.combine(today, datetime.min.time().replace(hour=16, minute=0))
    return market_open, market_close
