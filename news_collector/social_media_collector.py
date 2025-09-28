"""
Social Media News Collector
Collect financial sentiment and news from Twitter/X and other social media platforms
"""

import json
import time
import re
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Set
import logging

from .base import BaseNewsCollector, NewsItem, CollectionResult

logger = logging.getLogger(__name__)

class SocialMediaCollector(BaseNewsCollector):
    """
    Collect financial sentiment and news from social media platforms:
    - Twitter/X API v2
    - Reddit (financial subreddits)
    - Discord (financial communities)
    - Telegram (financial channels)
    - LinkedIn (company pages and financial professionals)
    """
    
    def __init__(self, api_keys: Dict[str, str] = None):
        """
        Initialize social media collector
        
        Args:
            api_keys: Dictionary containing API keys for various platforms
                     Expected keys: 'twitter_bearer', 'reddit_client_id', 'reddit_client_secret'
        """
        super().__init__(
            name="Social Media Collector",
            base_url="https://api.twitter.com",
            rate_limit_per_hour=300  # Twitter API v2 rate limit
        )
        
        self.api_keys = api_keys or {}
        
        # Configure platform endpoints
        self.platforms = {
            'twitter': {
                'base_url': 'https://api.twitter.com/2',
                'search_endpoint': '/tweets/search/recent',
                'user_timeline_endpoint': '/users/{user_id}/tweets',
                'requires_api': True,
                'rate_limit': 300  # requests per 15 minutes
            },
            'reddit': {
                'base_url': 'https://www.reddit.com',
                'search_endpoint': '/r/{subreddit}/search.json',
                'hot_endpoint': '/r/{subreddit}/hot.json',
                'requires_api': True,
                'rate_limit': 60  # requests per minute
            }
        }
        
        # Financial Twitter accounts to monitor
        self.financial_twitter_accounts = {
            # Official company accounts (we'll get these dynamically)
            'market_analysts': [
                'jimcramer', 'cathiedwood', 'elonmusk', 'chamath',
                'garyblack00', 'wolfofallst', 'marketwatch', 'cnbc',
                'bloomberg', 'financialtimes', 'wsj', 'yahoofinance'
            ],
            'financial_news': [
                'reuters', 'ap', 'marketwatch', 'seekingalpha',
                'barrons', 'benzinga', 'investopedia'
            ],
            'analysts': [
                'zerohedge', 'therealdanielhowitt', 'spreadcharts',
                'fintwit_master', 'stocktwits'
            ]
        }
        
        # Financial subreddits to monitor
        self.financial_subreddits = [
            'investing', 'stocks', 'SecurityAnalysis', 'ValueInvesting',
            'financialindependence', 'StockMarket', 'pennystocks',
            'options', 'SecurityAnalysis', 'financialplanning'
        ]
        
        # Financial keywords and hashtags
        self.financial_keywords = [
            'earnings', 'IPO', 'merger', 'acquisition', 'buyback',
            'dividend', 'split', 'guidance', 'revenue', 'profit',
            'loss', 'beat', 'miss', 'upgrade', 'downgrade',
            'price target', 'analyst', 'recommendation', 'SEC',
            'filing', 'insider', 'trading', 'volume', 'breakout'
        ]
        
        self.financial_hashtags = [
            '#earnings', '#stocks', '#investing', '#trading',
            '#finance', '#markets', '#IPO', '#merger',
            '#fintwit', '#stockmarket', '#options', '#crypto'
        ]
    
    def collect_recent_news(self, 
                           hours_back: int = 24,
                           max_items: int = 200) -> CollectionResult:
        """
        Collect recent financial social media posts
        
        Args:
            hours_back: Hours to look back for posts
            max_items: Maximum items to collect
            
        Returns:
            CollectionResult with collected social media posts
        """
        start_time = time.time()
        all_items = []
        errors = []
        
        logger.info(f"Collecting recent financial social media posts ({hours_back} hours back)")
        
        # Twitter general financial sentiment
        if self._has_twitter_api():
            try:
                twitter_items = self._collect_twitter_financial_sentiment(hours_back, max_items // 2)
                all_items.extend(twitter_items)
                logger.info(f"Collected {len(twitter_items)} Twitter posts")
            except Exception as e:
                error_msg = f"Error collecting Twitter posts: {str(e)}"
                logger.error(error_msg)
                errors.append(error_msg)
        
        # Reddit financial discussions
        if self._has_reddit_api():
            try:
                reddit_items = self._collect_reddit_financial_posts(hours_back, max_items // 2)
                all_items.extend(reddit_items)
                logger.info(f"Collected {len(reddit_items)} Reddit posts")
            except Exception as e:
                error_msg = f"Error collecting Reddit posts: {str(e)}"
                logger.error(error_msg)
                errors.append(error_msg)
        
        # Deduplicate and process
        unique_items = self._deduplicate_posts(all_items)
        
        execution_time = time.time() - start_time
        self.stats['items_collected'] += len(unique_items)
        
        return CollectionResult(
            success=len(unique_items) > 0,
            items_collected=len(unique_items),
            items=unique_items,
            errors=errors,
            execution_time=execution_time,
            metadata={'platforms_used': ['twitter', 'reddit']}
        )
    
    def collect_stock_news(self, 
                          stock_symbol: str,
                          hours_back: int = 24,
                          max_items: int = 100) -> CollectionResult:
        """
        Collect social media mentions for a specific stock
        
        Args:
            stock_symbol: Stock ticker symbol
            hours_back: Hours to look back
            max_items: Maximum items to collect
            
        Returns:
            CollectionResult with stock-specific social media mentions
        """
        start_time = time.time()
        all_items = []
        errors = []
        
        logger.info(f"Collecting social media mentions for stock: {stock_symbol}")
        
        # Twitter mentions
        if self._has_twitter_api():
            try:
                twitter_items = self._collect_twitter_stock_mentions(stock_symbol, hours_back, max_items // 2)
                all_items.extend(twitter_items)
                logger.info(f"Collected {len(twitter_items)} Twitter mentions for {stock_symbol}")
            except Exception as e:
                error_msg = f"Error collecting Twitter mentions: {str(e)}"
                logger.error(error_msg)
                errors.append(error_msg)
        
        # Reddit stock discussions
        if self._has_reddit_api():
            try:
                reddit_items = self._collect_reddit_stock_mentions(stock_symbol, hours_back, max_items // 2)
                all_items.extend(reddit_items)
                logger.info(f"Collected {len(reddit_items)} Reddit mentions for {stock_symbol}")
            except Exception as e:
                error_msg = f"Error collecting Reddit mentions: {str(e)}"
                logger.error(error_msg)
                errors.append(error_msg)
        
        # Official company Twitter account
        try:
            company_items = self._collect_company_twitter_posts(stock_symbol, hours_back, max_items // 4)
            all_items.extend(company_items)
            logger.info(f"Collected {len(company_items)} company Twitter posts for {stock_symbol}")
        except Exception as e:
            error_msg = f"Error collecting company Twitter posts: {str(e)}"
            logger.error(error_msg)
            errors.append(error_msg)
        
        # Filter for relevance and deduplicate
        relevant_items = self._filter_social_media_relevance(all_items, stock_symbol)
        unique_items = self._deduplicate_posts(relevant_items)
        
        execution_time = time.time() - start_time
        self.stats['items_collected'] += len(unique_items)
        
        return CollectionResult(
            success=len(unique_items) > 0,
            items_collected=len(unique_items),
            items=unique_items,
            errors=errors,
            execution_time=execution_time,
            metadata={'stock_symbol': stock_symbol}
        )
    
    def collect_company_social_media(self, 
                                   company_name: str,
                                   stock_symbol: str,
                                   hours_back: int = 24) -> CollectionResult:
        """
        Collect official company social media posts
        
        Args:
            company_name: Company name for searching
            stock_symbol: Stock ticker symbol
            hours_back: Hours to look back
            
        Returns:
            CollectionResult with official company posts
        """
        start_time = time.time()
        all_items = []
        errors = []
        
        logger.info(f"Collecting official social media for {company_name} ({stock_symbol})")
        
        # Find and collect from official company Twitter
        if self._has_twitter_api():
            try:
                company_twitter = self._find_company_twitter_account(company_name, stock_symbol)
                if company_twitter:
                    twitter_items = self._collect_user_tweets(company_twitter, hours_back)
                    all_items.extend(twitter_items)
                    logger.info(f"Collected {len(twitter_items)} official Twitter posts")
            except Exception as e:
                error_msg = f"Error collecting company Twitter: {str(e)}"
                logger.error(error_msg)
                errors.append(error_msg)
        
        execution_time = time.time() - start_time
        self.stats['items_collected'] += len(all_items)
        
        return CollectionResult(
            success=len(all_items) > 0,
            items_collected=len(all_items),
            items=all_items,
            errors=errors,
            execution_time=execution_time,
            metadata={'company_name': company_name, 'stock_symbol': stock_symbol}
        )
    
    def _collect_twitter_financial_sentiment(self, hours_back: int, max_items: int) -> List[NewsItem]:
        """Collect general financial sentiment from Twitter"""
        items = []
        
        if not self._has_twitter_api():
            return items
        
        try:
            # Build search query for financial discussions
            financial_query = self._build_twitter_financial_query()
            
            url = f"{self.platforms['twitter']['base_url']}/tweets/search/recent"
            headers = {
                'Authorization': f"Bearer {self.api_keys['twitter_bearer']}",
                'Content-Type': 'application/json'
            }
            
            params = {
                'query': financial_query,
                'max_results': min(max_items, 100),  # Twitter API limit
                'tweet.fields': 'created_at,author_id,public_metrics,context_annotations,entities',
                'user.fields': 'username,name,verified',
                'expansions': 'author_id'
            }
            
            # Add time filter
            end_time = datetime.now()
            start_time = end_time - timedelta(hours=hours_back)
            params['start_time'] = start_time.strftime('%Y-%m-%dT%H:%M:%SZ')
            
            response = self._make_request(url, params=params, headers=headers)
            
            if response and response.status_code == 200:
                data = response.json()
                
                # Parse user data
                users_map = {}
                for user in data.get('includes', {}).get('users', []):
                    users_map[user['id']] = user
                
                # Parse tweets
                for tweet in data.get('data', []):
                    try:
                        author_id = tweet.get('author_id')
                        author_info = users_map.get(author_id, {})
                        
                        published_time = self._parse_date(tweet.get('created_at'))
                        if not published_time:
                            continue
                        
                        # Extract stock symbols and financial entities
                        tweet_text = tweet.get('text', '')
                        stock_symbols = self._extract_stock_symbols_from_tweet(tweet_text)
                        
                        # Determine category based on content
                        category = self._categorize_financial_tweet(tweet_text)
                        
                        item = NewsItem(
                            title=f"Twitter: {tweet_text[:100]}...",
                            content=tweet_text,
                            url=f"https://twitter.com/{author_info.get('username', 'unknown')}/status/{tweet['id']}",
                            published_at=published_time,
                            author=author_info.get('name', author_info.get('username', 'Unknown')),
                            summary=tweet_text[:200] if len(tweet_text) > 200 else tweet_text,
                            external_id=tweet['id'],
                            category=category,
                            stock_symbols=stock_symbols,
                            raw_data={
                                'platform': 'twitter',
                                'tweet_data': tweet,
                                'author_data': author_info,
                                'metrics': tweet.get('public_metrics', {})
                            }
                        )
                        items.append(item)
                        
                    except Exception as e:
                        logger.error(f"Error parsing tweet: {e}")
                        continue
                        
        except Exception as e:
            logger.error(f"Error collecting Twitter financial sentiment: {e}")
        
        return items
    
    def _collect_twitter_stock_mentions(self, stock_symbol: str, hours_back: int, max_items: int) -> List[NewsItem]:
        """Collect Twitter mentions for specific stock"""
        items = []
        
        if not self._has_twitter_api():
            return items
        
        try:
            # Build stock-specific query
            query_variations = [
                f"${stock_symbol}",
                f"${stock_symbol.lower()}",
                f"{stock_symbol} stock",
                f"{stock_symbol} earnings",
                f"{stock_symbol} price"
            ]
            
            query = " OR ".join(query_variations)
            query += " -is:retweet"  # Exclude retweets
            
            url = f"{self.platforms['twitter']['base_url']}/tweets/search/recent"
            headers = {
                'Authorization': f"Bearer {self.api_keys['twitter_bearer']}",
                'Content-Type': 'application/json'
            }
            
            params = {
                'query': query,
                'max_results': min(max_items, 100),
                'tweet.fields': 'created_at,author_id,public_metrics,context_annotations',
                'user.fields': 'username,name,verified',
                'expansions': 'author_id'
            }
            
            # Add time filter
            end_time = datetime.now()
            start_time = end_time - timedelta(hours=hours_back)
            params['start_time'] = start_time.strftime('%Y-%m-%dT%H:%M:%SZ')
            
            response = self._make_request(url, params=params, headers=headers)
            
            if response and response.status_code == 200:
                data = response.json()
                
                # Parse user data
                users_map = {}
                for user in data.get('includes', {}).get('users', []):
                    users_map[user['id']] = user
                
                # Parse tweets
                for tweet in data.get('data', []):
                    try:
                        author_id = tweet.get('author_id')
                        author_info = users_map.get(author_id, {})
                        
                        published_time = self._parse_date(tweet.get('created_at'))
                        if not published_time:
                            continue
                        
                        tweet_text = tweet.get('text', '')
                        
                        # Calculate relevance score
                        relevance_score = self._calculate_tweet_relevance(tweet_text, stock_symbol)
                        
                        if relevance_score > 0.3:  # Only include relevant tweets
                            item = NewsItem(
                                title=f"Twitter ({stock_symbol}): {tweet_text[:80]}...",
                                content=tweet_text,
                                url=f"https://twitter.com/{author_info.get('username', 'unknown')}/status/{tweet['id']}",
                                published_at=published_time,
                                author=author_info.get('name', author_info.get('username', 'Unknown')),
                                summary=tweet_text[:150] if len(tweet_text) > 150 else tweet_text,
                                external_id=tweet['id'],
                                category='social_sentiment',
                                stock_symbols=[stock_symbol.upper()],
                                raw_data={
                                    'platform': 'twitter',
                                    'tweet_data': tweet,
                                    'author_data': author_info,
                                    'relevance_score': relevance_score,
                                    'metrics': tweet.get('public_metrics', {})
                                }
                            )
                            items.append(item)
                            
                    except Exception as e:
                        logger.error(f"Error parsing stock tweet: {e}")
                        continue
                        
        except Exception as e:
            logger.error(f"Error collecting Twitter stock mentions for {stock_symbol}: {e}")
        
        return items
    
    def _collect_reddit_financial_posts(self, hours_back: int, max_items: int) -> List[NewsItem]:
        """Collect financial posts from Reddit"""
        items = []
        
        if not self._has_reddit_api():
            return items
        
        try:
            items_per_subreddit = max_items // len(self.financial_subreddits)
            
            for subreddit in self.financial_subreddits:
                try:
                    subreddit_items = self._collect_subreddit_posts(subreddit, hours_back, items_per_subreddit)
                    items.extend(subreddit_items)
                    
                    # Rate limiting
                    time.sleep(1)
                    
                except Exception as e:
                    logger.error(f"Error collecting from r/{subreddit}: {e}")
                    continue
                    
        except Exception as e:
            logger.error(f"Error collecting Reddit financial posts: {e}")
        
        return items
    
    def _collect_reddit_stock_mentions(self, stock_symbol: str, hours_back: int, max_items: int) -> List[NewsItem]:
        """Collect Reddit mentions for specific stock"""
        items = []
        
        if not self._has_reddit_api():
            return items
        
        try:
            # Search across financial subreddits for stock mentions
            for subreddit in self.financial_subreddits[:3]:  # Limit to top 3 subreddits
                try:
                    url = f"https://www.reddit.com/r/{subreddit}/search.json"
                    params = {
                        'q': f"{stock_symbol} OR ${stock_symbol}",
                        'sort': 'new',
                        'restrict_sr': 'on',
                        'limit': max_items // 3
                    }
                    
                    headers = {
                        'User-Agent': 'Financial News Collector 1.0'
                    }
                    
                    response = self._make_request(url, params=params, headers=headers)
                    
                    if response and response.status_code == 200:
                        data = response.json()
                        
                        for post in data.get('data', {}).get('children', []):
                            try:
                                post_data = post.get('data', {})
                                
                                # Check if within time range
                                created_time = datetime.fromtimestamp(post_data.get('created_utc', 0))
                                cutoff_time = datetime.now() - timedelta(hours=hours_back)
                                
                                if created_time >= cutoff_time:
                                    title = post_data.get('title', '')
                                    content = post_data.get('selftext', '')
                                    
                                    # Check relevance
                                    text = f"{title} {content}"
                                    if self._is_stock_relevant(text, stock_symbol):
                                        item = NewsItem(
                                            title=f"Reddit r/{subreddit}: {title}",
                                            content=content,
                                            url=f"https://reddit.com{post_data.get('permalink', '')}",
                                            published_at=created_time,
                                            author=post_data.get('author', 'Unknown'),
                                            summary=title,
                                            external_id=post_data.get('id'),
                                            category='social_discussion',
                                            stock_symbols=[stock_symbol.upper()],
                                            raw_data={
                                                'platform': 'reddit',
                                                'subreddit': subreddit,
                                                'post_data': post_data,
                                                'score': post_data.get('score', 0),
                                                'num_comments': post_data.get('num_comments', 0)
                                            }
                                        )
                                        items.append(item)
                                        
                            except Exception as e:
                                logger.error(f"Error parsing Reddit post: {e}")
                                continue
                                
                    # Rate limiting
                    time.sleep(2)
                    
                except Exception as e:
                    logger.error(f"Error searching r/{subreddit} for {stock_symbol}: {e}")
                    continue
                    
        except Exception as e:
            logger.error(f"Error collecting Reddit stock mentions for {stock_symbol}: {e}")
        
        return items
    
    # Helper methods
    def _has_twitter_api(self) -> bool:
        """Check if Twitter API key is available"""
        return 'twitter_bearer' in self.api_keys
    
    def _has_reddit_api(self) -> bool:
        """Check if Reddit API credentials are available"""
        return 'reddit_client_id' in self.api_keys and 'reddit_client_secret' in self.api_keys
    
    def _build_twitter_financial_query(self) -> str:
        """Build Twitter search query for financial content"""
        hashtag_query = " OR ".join(self.financial_hashtags)
        keyword_query = " OR ".join([f'"{kw}"' for kw in self.financial_keywords[:5]])  # Limit query length
        
        query = f"({hashtag_query}) OR ({keyword_query})"
        query += " -is:retweet -is:reply"  # Exclude retweets and replies
        
        return query
    
    def _extract_stock_symbols_from_tweet(self, text: str) -> List[str]:
        """Extract stock symbols from tweet text"""
        # Twitter-specific patterns
        patterns = [
            r'\$[A-Z]{1,5}\b',  # $AAPL format
            r'#[A-Z]{1,5}\b',   # #AAPL format
        ]
        
        symbols = set()
        for pattern in patterns:
            matches = re.findall(pattern, text.upper())
            # Remove $ and # prefixes
            symbols.update([match.lstrip('$#') for match in matches])
        
        # Also use base class method
        base_symbols = self._extract_stock_symbols(text)
        symbols.update(base_symbols)
        
        return list(symbols)
    
    def _categorize_financial_tweet(self, text: str) -> str:
        """Categorize financial tweet based on content"""
        text_lower = text.lower()
        
        if any(word in text_lower for word in ['earnings', 'revenue', 'profit', 'loss']):
            return 'earnings'
        elif any(word in text_lower for word in ['merger', 'acquisition', 'deal', 'buyout']):
            return 'merger_acquisition'
        elif any(word in text_lower for word in ['ipo', 'listing', 'debut']):
            return 'ipo'
        elif any(word in text_lower for word in ['dividend', 'split', 'buyback']):
            return 'corporate_action'
        elif any(word in text_lower for word in ['analyst', 'upgrade', 'downgrade', 'target']):
            return 'analyst_opinion'
        else:
            return 'general_sentiment'
    
    def _calculate_tweet_relevance(self, text: str, stock_symbol: str) -> float:
        """Calculate relevance score for tweet to specific stock"""
        text_lower = text.lower()
        symbol_lower = stock_symbol.lower()
        
        score = 0.0
        
        # Direct symbol mentions
        if f'${symbol_lower}' in text_lower:
            score += 0.5
        if f'#{symbol_lower}' in text_lower:
            score += 0.3
        if symbol_lower in text_lower:
            score += 0.2
        
        # Financial keywords boost relevance
        financial_words = ['earnings', 'revenue', 'stock', 'price', 'target', 'analyst']
        for word in financial_words:
            if word in text_lower:
                score += 0.1
        
        return min(score, 1.0)  # Cap at 1.0
    
    def _is_stock_relevant(self, text: str, stock_symbol: str) -> bool:
        """Check if text is relevant to specific stock"""
        text_lower = text.lower()
        symbol_lower = stock_symbol.lower()
        
        # Check for symbol variations
        symbol_variations = [
            symbol_lower,
            f'${symbol_lower}',
            f'#{symbol_lower}',
            f'{symbol_lower} stock'
        ]
        
        return any(var in text_lower for var in symbol_variations)
    
    def _deduplicate_posts(self, items: List[NewsItem]) -> List[NewsItem]:
        """Remove duplicate social media posts"""
        seen_ids = set()
        unique_items = []
        
        for item in items:
            # Use external_id and URL for deduplication
            key = f"{item.external_id}_{item.url}"
            if key not in seen_ids:
                seen_ids.add(key)
                unique_items.append(item)
        
        return unique_items
    
    def _filter_social_media_relevance(self, items: List[NewsItem], stock_symbol: str) -> List[NewsItem]:
        """Filter social media posts for relevance to specific stock"""
        relevant_items = []
        
        for item in items:
            if item.stock_symbols and stock_symbol.upper() in item.stock_symbols:
                relevant_items.append(item)
            elif self._is_stock_relevant(f"{item.title} {item.content}", stock_symbol):
                relevant_items.append(item)
        
        return relevant_items
    
    # Placeholder methods (implement based on specific API requirements)
    def _find_company_twitter_account(self, company_name: str, stock_symbol: str) -> Optional[str]:
        """Find official company Twitter account"""
        # Implement Twitter user search for company
        return None
    
    def _collect_user_tweets(self, username: str, hours_back: int) -> List[NewsItem]:
        """Collect tweets from specific user"""
        # Implement user timeline collection
        return []
    
    def _collect_company_twitter_posts(self, stock_symbol: str, hours_back: int, max_items: int) -> List[NewsItem]:
        """Collect official company Twitter posts"""
        # Implement company-specific Twitter collection
        return []
    
    def _collect_subreddit_posts(self, subreddit: str, hours_back: int, max_items: int) -> List[NewsItem]:
        """Collect posts from specific subreddit"""
        # Implement subreddit post collection
        return []

# Example usage
if __name__ == "__main__":
    # Initialize with API keys
    api_keys = {
        'twitter_bearer': 'your_twitter_bearer_token',
        'reddit_client_id': 'your_reddit_client_id',
        'reddit_client_secret': 'your_reddit_client_secret'
    }
    
    collector = SocialMediaCollector(api_keys)
    
    # Test general social media collection
    result = collector.collect_recent_news(hours_back=24, max_items=50)
    print(f"Collected {result.items_collected} social media posts")
    
    # Test stock-specific collection
    stock_result = collector.collect_stock_news("AAPL", hours_back=12, max_items=25)
    print(f"Collected {stock_result.items_collected} AAPL social media mentions")
