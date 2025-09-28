"""News Collector Service - Fetches articles from NewsAPI and maps to assets."""

import os
import requests
import logging
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Tuple
from rapidfuzz import fuzz, process
from sqlalchemy.orm import Session
from sqlalchemy import func

from database import SessionLocal
from models import Asset, NewsArticle, NewsAssetMap

logger = logging.getLogger(__name__)


class NewsCollector:
    """
    Service for collecting news articles from NewsAPI and mapping them to assets.
    """
    
    def __init__(self, api_key: Optional[str] = None):
        """Initialize with NewsAPI key."""
        self.api_key = api_key or os.getenv("NEWSAPI_KEY")
        if not self.api_key:
            raise ValueError("NEWSAPI_KEY environment variable is required")
        
        self.base_url = "https://newsapi.org/v2"
        self.min_match_score = float(os.getenv("NEWS_MATCH_MIN_SCORE", "0.7"))
        
    def fetch_financial_news(self, hours_back: int = 24, page_size: int = 100) -> List[Dict]:
        """
        Fetch financial news from NewsAPI.
        
        Args:
            hours_back: How many hours back to fetch news
            page_size: Number of articles per page (max 100)
            
        Returns:
            List of article dictionaries from NewsAPI
        """
        from_date = datetime.now() - timedelta(hours=hours_back)
        
        # Financial keywords and sources for better targeting
        query = "stocks OR trading OR finance OR market OR investment OR earnings OR IPO OR cryptocurrency"
        
        params = {
            'q': query,
            'language': 'en',
            'sortBy': 'publishedAt',
            'from': from_date.strftime('%Y-%m-%dT%H:%M:%S'),
            'pageSize': page_size,
            'apiKey': self.api_key
        }
        
        try:
            response = requests.get(f"{self.base_url}/everything", params=params, timeout=30)
            response.raise_for_status()
            
            data = response.json()
            if data['status'] == 'ok':
                logger.info(f"Fetched {len(data['articles'])} articles from NewsAPI")
                return data['articles']
            else:
                logger.error(f"NewsAPI error: {data.get('message', 'Unknown error')}")
                return []
                
        except requests.RequestException as e:
            logger.error(f"Error fetching news from NewsAPI: {e}")
            return []
    
    def deduplicate_articles(self, db: Session, articles: List[Dict]) -> List[Dict]:
        """
        Remove articles that already exist in database based on URL.
        
        Args:
            db: Database session
            articles: List of articles from NewsAPI
            
        Returns:
            List of new articles not in database
        """
        if not articles:
            return []
        
        # Get existing URLs from database
        existing_urls = {
            url[0] for url in db.query(NewsArticle.url).all()
        }
        
        # Filter out existing articles
        new_articles = [
            article for article in articles 
            if article.get('url') and article['url'] not in existing_urls
        ]
        
        logger.info(f"Deduplication: {len(articles)} total -> {len(new_articles)} new articles")
        return new_articles
    
    def get_asset_mapping_data(self, db: Session) -> Dict[int, Tuple[str, str]]:
        """
        Get asset data for fuzzy matching.
        
        Returns:
            Dict mapping asset_id to (symbol, name) tuple
        """
        assets = db.query(Asset.id, Asset.symbol, Asset.name).filter(Asset.is_active == True).all()
        return {asset.id: (asset.symbol, asset.name) for asset in assets}
    
    def fuzzy_match_assets(self, text: str, asset_data: Dict[int, Tuple[str, str]]) -> List[Tuple[int, float, str]]:
        """
        Use fuzzy matching to find relevant assets mentioned in text.
        
        Args:
            text: Text to search for asset mentions
            asset_data: Dict of asset_id -> (symbol, name)
            
        Returns:
            List of (asset_id, score, matched_text) tuples
        """
        matches = []
        text_lower = text.lower()
        
        for asset_id, (symbol, name) in asset_data.items():
            # Check symbol match (exact or fuzzy)
            symbol_score = 0.0
            if symbol.lower() in text_lower:
                symbol_score = 1.0
            else:
                symbol_score = fuzz.partial_ratio(symbol.lower(), text_lower) / 100.0
            
            # Check name match (fuzzy)
            name_score = fuzz.partial_ratio(name.lower(), text_lower) / 100.0
            
            # Take the best score
            best_score = max(symbol_score, name_score)
            matched_text = symbol if symbol_score > name_score else name
            
            if best_score >= self.min_match_score:
                matches.append((asset_id, best_score, matched_text))
        
        # Sort by score descending
        matches.sort(key=lambda x: x[1], reverse=True)
        return matches
    
    def store_article(self, db: Session, article: Dict) -> Optional[NewsArticle]:
        """
        Store a single article in the database.
        
        Args:
            db: Database session
            article: Article data from NewsAPI
            
        Returns:
            Created NewsArticle instance or None if failed
        """
        try:
            # Parse published date
            published_at = None
            if article.get('publishedAt'):
                try:
                    published_at = datetime.fromisoformat(
                        article['publishedAt'].replace('Z', '+00:00')
                    )
                except Exception as e:
                    logger.warning(f"Could not parse published date {article['publishedAt']}: {e}")
            
            # Create article record
            db_article = NewsArticle(
                url=article['url'],
                title=article.get('title', ''),
                summary=article.get('description', ''),
                content=article.get('content', ''),
                source=article.get('source', {}).get('name', 'newsapi'),
                author=article.get('author'),
                published_at=published_at,
                is_processed=False
            )
            
            db.add(db_article)
            db.flush()  # Get the ID
            
            return db_article
            
        except Exception as e:
            logger.error(f"Error storing article {article.get('url', 'unknown')}: {e}")
            db.rollback()
            return None
    
    def create_asset_mappings(self, db: Session, article: NewsArticle, asset_data: Dict[int, Tuple[str, str]]) -> int:
        """
        Create asset mappings for an article using fuzzy matching.
        
        Args:
            db: Database session
            article: NewsArticle instance
            asset_data: Asset data for matching
            
        Returns:
            Number of mappings created
        """
        # Combine title and summary for matching
        search_text = f"{article.title} {article.summary or ''}"
        
        # Find matching assets
        matches = self.fuzzy_match_assets(search_text, asset_data)
        
        mappings_created = 0
        for asset_id, score, matched_text in matches[:10]:  # Limit to top 10 matches
            try:
                mapping = NewsAssetMap(
                    article_id=article.id,
                    asset_id=asset_id,
                    match_score=score,
                    match_method="fuzzy",
                    matched_text=matched_text[:500]  # Truncate if too long
                )
                db.add(mapping)
                mappings_created += 1
                
            except Exception as e:
                logger.error(f"Error creating asset mapping: {e}")
                continue
        
        return mappings_created
    
    def collect_and_store_news(self, hours_back: int = 24) -> Dict[str, int]:
        """
        Main function to collect news, deduplicate, and store with asset mappings.
        
        Args:
            hours_back: How many hours back to fetch news
            
        Returns:
            Dictionary with collection statistics
        """
        logger.info(f"Starting news collection for last {hours_back} hours")
        
        stats = {
            'articles_fetched': 0,
            'articles_new': 0,
            'articles_stored': 0,
            'mappings_created': 0,
            'errors': 0
        }
        
        db = SessionLocal()
        try:
            # Fetch articles from NewsAPI
            articles = self.fetch_financial_news(hours_back=hours_back)
            stats['articles_fetched'] = len(articles)
            
            if not articles:
                logger.warning("No articles fetched from NewsAPI")
                return stats
            
            # Deduplicate against existing articles
            new_articles = self.deduplicate_articles(db, articles)
            stats['articles_new'] = len(new_articles)
            
            if not new_articles:
                logger.info("No new articles to process")
                return stats
            
            # Get asset data for matching
            asset_data = self.get_asset_mapping_data(db)
            logger.info(f"Loaded {len(asset_data)} assets for matching")
            
            # Process each new article
            for article_data in new_articles:
                try:
                    # Store article
                    db_article = self.store_article(db, article_data)
                    if db_article:
                        stats['articles_stored'] += 1
                        
                        # Create asset mappings
                        mappings = self.create_asset_mappings(db, db_article, asset_data)
                        stats['mappings_created'] += mappings
                        
                    else:
                        stats['errors'] += 1
                        
                except Exception as e:
                    logger.error(f"Error processing article: {e}")
                    stats['errors'] += 1
                    db.rollback()
                    continue
            
            # Commit all changes
            db.commit()
            logger.info(f"News collection completed: {stats}")
            
        except Exception as e:
            logger.error(f"Error in news collection: {e}")
            db.rollback()
            stats['errors'] += 1
            
        finally:
            db.close()
        
        return stats


def main():
    """Main function for CLI usage."""
    logging.basicConfig(level=logging.INFO)
    
    collector = NewsCollector()
    results = collector.collect_and_store_news(hours_back=24)
    
    print(f"News Collection Results:")
    print(f"  Articles fetched: {results['articles_fetched']}")
    print(f"  New articles: {results['articles_new']}")
    print(f"  Articles stored: {results['articles_stored']}")
    print(f"  Asset mappings created: {results['mappings_created']}")
    print(f"  Errors: {results['errors']}")


if __name__ == "__main__":
    main()