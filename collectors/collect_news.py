"""
📰 LUMIA NEWS COLLECTOR
Fetches news articles from multiple sources and stores them with asset links
"""

import os
import sys
import logging
from datetime import datetime, timedelta
from typing import List, Dict, Optional
from sqlalchemy import func
from sqlalchemy.orm import Session

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database import SessionLocal
from models.assets import Asset
from models.news_article import NewsArticle

# Import from news_collector package (separate from this file)
import news_collector.news_api as news_api


class NewsCollector:
    """
    Intelligent news collection system
    Fetches news from multiple sources and stores with proper asset linking
    """
    
    def __init__(self):
        self.logger = logging.getLogger('lumia.news_collector')
        self.session = None
    
    def get_db_session(self):
        """Get database session"""
        if not self.session:
            self.session = SessionLocal()
        return self.session
    
    def collect_news_for_stocks(self, limit_stocks: Optional[int] = None, 
                                 articles_per_stock: int = 5) -> Dict:
        """
        Collect news for stock assets
        
        Args:
            limit_stocks: Maximum number of stocks to process (None = all)
            articles_per_stock: Number of articles to fetch per stock
        
        Returns:
            Dictionary with collection results
        """
        self.logger.info("[NEWS] Starting news collection for stocks...")
        
        db = self.get_db_session()
        
        # Get active stocks (prioritize high market cap or recently updated)
        query = db.query(Asset).filter(
            Asset.type == 'stock',
            Asset.is_active == True
        ).order_by(Asset.symbol)
        
        if limit_stocks:
            stocks = query.limit(limit_stocks).all()
        else:
            stocks = query.all()
        
        self.logger.info(f"[NEWS] Processing {len(stocks)} stocks")
        
        results = {
            'total_stocks_processed': 0,
            'total_articles_fetched': 0,
            'total_articles_saved': 0,
            'total_duplicates_skipped': 0,
            'total_errors': 0,
            'by_source': {}
        }
        
        for stock in stocks:
            try:
                self.logger.info(f"[NEWS] Fetching news for {stock.symbol} ({stock.name})")
                
                stock_results = self._collect_news_for_asset(
                    asset=stock,
                    articles_per_source=articles_per_stock
                )
                
                results['total_stocks_processed'] += 1
                results['total_articles_fetched'] += stock_results['articles_fetched']
                results['total_articles_saved'] += stock_results['articles_saved']
                results['total_duplicates_skipped'] += stock_results['duplicates_skipped']
                
                # Merge source stats
                for source, count in stock_results['by_source'].items():
                    results['by_source'][source] = results['by_source'].get(source, 0) + count
                
            except Exception as e:
                self.logger.error(f"[NEWS] Error processing {stock.symbol}: {e}")
                results['total_errors'] += 1
        
        self.logger.info(f"[NEWS] ✅ Collection complete: {results['total_articles_saved']} new articles saved")
        return results
    
    def collect_news_for_crypto(self, limit_cryptos: Optional[int] = None,
                                 articles_per_crypto: int = 5) -> Dict:
        """
        Collect news for cryptocurrency assets
        
        Args:
            limit_cryptos: Maximum number of cryptos to process (None = all)
            articles_per_crypto: Number of articles to fetch per crypto
        
        Returns:
            Dictionary with collection results
        """
        self.logger.info("[NEWS] Starting news collection for cryptocurrencies...")
        
        db = self.get_db_session()
        
        query = db.query(Asset).filter(
            Asset.type == 'crypto',
            Asset.is_active == True
        ).order_by(Asset.symbol)
        
        if limit_cryptos:
            cryptos = query.limit(limit_cryptos).all()
        else:
            cryptos = query.all()
        
        self.logger.info(f"[NEWS] Processing {len(cryptos)} cryptocurrencies")
        
        results = {
            'total_cryptos_processed': 0,
            'total_articles_fetched': 0,
            'total_articles_saved': 0,
            'total_duplicates_skipped': 0,
            'total_errors': 0,
            'by_source': {}
        }
        
        for crypto in cryptos:
            try:
                self.logger.info(f"[NEWS] Fetching news for {crypto.symbol} ({crypto.name})")
                
                crypto_results = self._collect_news_for_asset(
                    asset=crypto,
                    articles_per_source=articles_per_crypto
                )
                
                results['total_cryptos_processed'] += 1
                results['total_articles_fetched'] += crypto_results['articles_fetched']
                results['total_articles_saved'] += crypto_results['articles_saved']
                results['total_duplicates_skipped'] += crypto_results['duplicates_skipped']
                
                # Merge source stats
                for source, count in crypto_results['by_source'].items():
                    results['by_source'][source] = results['by_source'].get(source, 0) + count
                
            except Exception as e:
                self.logger.error(f"[NEWS] Error processing {crypto.symbol}: {e}")
                results['total_errors'] += 1
        
        self.logger.info(f"[NEWS] ✅ Collection complete: {results['total_articles_saved']} new articles saved")
        return results
    
    def _collect_news_for_asset(self, asset: Asset, articles_per_source: int = 5) -> Dict:
        """
        Collect news for a single asset from multiple sources
        
        Args:
            asset: Asset object
            articles_per_source: Number of articles per source
        
        Returns:
            Dictionary with collection results
        """
        results = {
            'articles_fetched': 0,
            'articles_saved': 0,
            'duplicates_skipped': 0,
            'by_source': {}
        }
        
        all_articles = []
        
        # Collect from different sources based on asset type
        if asset.type == 'stock':
            # Source 1: Finnhub (best for stocks)
            try:
                articles = news_api.get_news_from_finnhub(asset.symbol, articles_per_source)
                all_articles.extend(articles)
                results['by_source']['finnhub'] = len(articles)
            except Exception as e:
                self.logger.warning(f"[NEWS] Finnhub failed for {asset.symbol}: {e}")
            
            # Source 2: Polygon
            try:
                articles = news_api.get_news_from_polygon(asset.symbol, articles_per_source)
                all_articles.extend(articles)
                results['by_source']['polygon'] = len(articles)
            except Exception as e:
                self.logger.warning(f"[NEWS] Polygon failed for {asset.symbol}: {e}")
            
            # Source 3: Alpha Vantage
            try:
                articles = news_api.get_news_from_alphavantage(asset.symbol, articles_per_source)
                all_articles.extend(articles)
                results['by_source']['alphavantage'] = len(articles)
            except Exception as e:
                self.logger.warning(f"[NEWS] AlphaVantage failed for {asset.symbol}: {e}")
            
            # Source 4: NewsAPI (fallback - uses company name)
            try:
                articles = news_api.get_news_from_newsapi(asset.name, articles_per_source)
                all_articles.extend(articles)
                results['by_source']['newsapi'] = len(articles)
            except Exception as e:
                self.logger.warning(f"[NEWS] NewsAPI failed for {asset.symbol}: {e}")
        
        elif asset.type == 'crypto':
            # Source 1: CryptoPanic (best for crypto)
            try:
                articles = news_api.get_news_from_cryptopanic(asset.symbol, articles_per_source * 2)
                all_articles.extend(articles)
                results['by_source']['cryptopanic'] = len(articles)
            except Exception as e:
                self.logger.warning(f"[NEWS] CryptoPanic failed for {asset.symbol}: {e}")
            
            # Source 2: NewsAPI (fallback)
            try:
                articles = news_api.get_news_from_newsapi(f"{asset.symbol} {asset.name}", articles_per_source)
                all_articles.extend(articles)
                results['by_source']['newsapi'] = len(articles)
            except Exception as e:
                self.logger.warning(f"[NEWS] NewsAPI failed for {asset.symbol}: {e}")
        
        results['articles_fetched'] = len(all_articles)
        
        # Save articles to database
        if all_articles:
            saved, duplicates = self._save_articles(all_articles, asset)
            results['articles_saved'] = saved
            results['duplicates_skipped'] = duplicates
        
        return results
    
    def _save_articles(self, articles: List[Dict], asset: Asset) -> tuple:
        """
        Save articles to database with deduplication
        
        Args:
            articles: List of article dictionaries
            asset: Asset object to link to
        
        Returns:
            Tuple of (saved_count, duplicate_count)
        """
        db = self.get_db_session()
        
        saved_count = 0
        duplicate_count = 0
        
        for article_data in articles:
            try:
                url = article_data.get('url', '')
                
                if not url:
                    continue
                
                # Check for duplicate
                existing = db.query(NewsArticle).filter(NewsArticle.url == url).first()
                
                if existing:
                    duplicate_count += 1
                    continue
                
                # Parse published date
                published_at = None
                date_str = article_data.get('date', '')
                if date_str:
                    try:
                        # Try multiple date formats
                        for fmt in ['%Y-%m-%dT%H:%M:%S%z', '%Y-%m-%dT%H:%M:%SZ', 
                                    '%Y-%m-%d %H:%M:%S', '%Y%m%dT%H%M%S']:
                            try:
                                published_at = datetime.strptime(date_str[:19], fmt[:19])
                                break
                            except:
                                continue
                    except:
                        self.logger.warning(f"[NEWS] Could not parse date: {date_str}")
                
                # Extract sentiment if available
                sentiment_score = None
                sentiment_label = None
                if 'sentiment' in article_data:
                    sentiment_label = article_data['sentiment']
                    # Map labels to scores
                    sentiment_map = {
                        'Bullish': 0.8,
                        'Somewhat-Bullish': 0.4,
                        'Neutral': 0.0,
                        'Somewhat-Bearish': -0.4,
                        'Bearish': -0.8
                    }
                    sentiment_score = sentiment_map.get(sentiment_label, 0.0)
                
                # Create news article
                news = NewsArticle(
                    asset_id=asset.id,
                    asset_symbol=asset.symbol,
                    url=url,
                    title=article_data.get('title', '')[:500],
                    summary=article_data.get('description', ''),
                    content=article_data.get('content', ''),
                    source=article_data.get('api', article_data.get('source', 'Unknown')),
                    author=article_data.get('author', ''),
                    published_at=published_at,
                    sentiment_score=sentiment_score,
                    sentiment_label=sentiment_label,
                    is_processed=sentiment_score is not None
                )
                
                db.add(news)
                saved_count += 1
                
                # Commit in batches
                if saved_count % 10 == 0:
                    db.commit()
            
            except Exception as e:
                self.logger.error(f"[NEWS] Error saving article: {e}")
                db.rollback()
        
        # Final commit
        try:
            db.commit()
        except Exception as e:
            self.logger.error(f"[NEWS] Error committing articles: {e}")
            db.rollback()
        
        return saved_count, duplicate_count
    
    def get_news_stats(self) -> Dict:
        """Get statistics about news collection"""
        db = self.get_db_session()
        
        total_articles = db.query(NewsArticle).count()
        assets_with_news = db.query(func.count(func.distinct(NewsArticle.asset_id))).filter(
            NewsArticle.asset_id.isnot(None)
        ).scalar()
        
        recent_articles = db.query(NewsArticle).filter(
            NewsArticle.published_at >= datetime.now() - timedelta(days=7)
        ).count()
        
        by_source = {}
        sources = db.query(NewsArticle.source, func.count(NewsArticle.id)).group_by(
            NewsArticle.source
        ).all()
        
        for source, count in sources:
            by_source[source] = count
        
        return {
            'total_articles': total_articles,
            'assets_with_news': assets_with_news,
            'recent_articles_7d': recent_articles,
            'by_source': by_source
        }


def collect_stock_news(limit: Optional[int] = 100, articles_per_stock: int = 5) -> Dict:
    """
    Convenience function to collect stock news
    
    Args:
        limit: Maximum number of stocks to process
        articles_per_stock: Articles per stock
    
    Returns:
        Collection results dictionary
    """
    collector = NewsCollector()
    return collector.collect_news_for_stocks(limit, articles_per_stock)


def collect_crypto_news(limit: Optional[int] = None, articles_per_crypto: int = 5) -> Dict:
    """
    Convenience function to collect crypto news
    
    Args:
        limit: Maximum number of cryptos to process
        articles_per_crypto: Articles per crypto
    
    Returns:
        Collection results dictionary
    """
    collector = NewsCollector()
    return collector.collect_news_for_crypto(limit, articles_per_crypto)


# ============================================================================
# TESTING & DEMO
# ============================================================================

if __name__ == "__main__":
    """
    Test the news collector
    Run: python collectors/news_collector.py
    """
    import argparse
    
    # Setup logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    parser = argparse.ArgumentParser(description='Lumia News Collector')
    parser.add_argument('--type', choices=['stock', 'crypto', 'stats'], 
                       default='stats', help='What to collect')
    parser.add_argument('--limit', type=int, default=None, 
                       help='Number of assets to process (default: ALL)')
    parser.add_argument('--articles', type=int, default=5,
                       help='Articles per asset')
    
    args = parser.parse_args()
    
    print("\n" + "="*70)
    print("📰 LUMIA NEWS COLLECTOR - TEST MODE")
    print("="*70 + "\n")
    
    collector = NewsCollector()
    
    if args.type == 'stats':
        # Show current statistics
        print("📊 Current News Database Statistics:\n")
        stats = collector.get_news_stats()
        
        print(f"Total Articles:           {stats['total_articles']:,}")
        print(f"Assets with News:         {stats['assets_with_news']:,}")
        print(f"Recent Articles (7 days): {stats['recent_articles_7d']:,}")
        print("\nBy Source:")
        for source, count in stats['by_source'].items():
            print(f"  • {source:15s}: {count:,} articles")
        
        print("\n" + "="*70)
        print("💡 To collect news, run:")
        print("   python collectors/collect_news.py --type stock          # All stocks")
        print("   python collectors/collect_news.py --type stock --limit 100  # First 100")
        print("   python collectors/collect_news.py --type crypto         # All crypto")
        print("="*70 + "\n")
    
    elif args.type == 'stock':
        # Collect stock news
        limit_msg = f"{args.limit} stocks" if args.limit else "ALL stocks"
        print(f"🔍 Collecting news for {limit_msg} ({args.articles} articles each)...\n")
        results = collector.collect_news_for_stocks(
            limit_stocks=args.limit,
            articles_per_stock=args.articles
        )
        
        print("\n" + "="*70)
        print("✅ COLLECTION COMPLETE")
        print("="*70)
        print(f"Stocks Processed:    {results['total_stocks_processed']}")
        print(f"Articles Fetched:    {results['total_articles_fetched']}")
        print(f"Articles Saved:      {results['total_articles_saved']}")
        print(f"Duplicates Skipped:  {results['total_duplicates_skipped']}")
        print(f"Errors:              {results['total_errors']}")
        print("\nBy Source:")
        for source, count in results['by_source'].items():
            print(f"  • {source:15s}: {count} articles")
        print("="*70 + "\n")
    
    elif args.type == 'crypto':
        # Collect crypto news
        limit_msg = f"{args.limit} cryptocurrencies" if args.limit else "ALL cryptocurrencies"
        print(f"🔍 Collecting news for {limit_msg} ({args.articles} articles each)...\n")
        results = collector.collect_news_for_crypto(
            limit_cryptos=args.limit,
            articles_per_crypto=args.articles
        )
        
        print("\n" + "="*70)
        print("✅ COLLECTION COMPLETE")
        print("="*70)
        print(f"Cryptos Processed:   {results['total_cryptos_processed']}")
        print(f"Articles Fetched:    {results['total_articles_fetched']}")
        print(f"Articles Saved:      {results['total_articles_saved']}")
        print(f"Duplicates Skipped:  {results['total_duplicates_skipped']}")
        print(f"Errors:              {results['total_errors']}")
        print("\nBy Source:")
        for source, count in results['by_source'].items():
            print(f"  • {source:15s}: {count} articles")
        print("="*70 + "\n")

