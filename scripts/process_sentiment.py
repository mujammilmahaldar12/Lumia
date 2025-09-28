#!/usr/bin/env python3
"""
CLI script for processing sentiment analysis on collected news articles.

Usage:
    python process_sentiment.py --help
    python process_sentiment.py --unprocessed --batch-size 50
    python process_sentiment.py --article-ids 123,456,789
    python process_sentiment.py --reprocess --symbols AAPL,TSLA
"""

import argparse
import asyncio
import logging
from datetime import datetime, timedelta
from typing import List, Optional

from Lumia.database import get_db
from Lumia.services.sentiment_worker import SentimentWorker
from Lumia.models.news_article import NewsArticle
from Lumia.models.news_sentiment import NewsSentiment


def setup_logging(verbose: bool = False):
    """Setup logging configuration."""
    level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(
        level=level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )


def parse_ids(ids_str: str) -> List[int]:
    """Parse comma-separated IDs string."""
    if not ids_str:
        return []
    try:
        return [int(id_str.strip()) for id_str in ids_str.split(',') if id_str.strip()]
    except ValueError as e:
        raise argparse.ArgumentTypeError(f"Invalid ID format: {e}")


def parse_symbols(symbols_str: str) -> List[str]:
    """Parse comma-separated symbols string."""
    if not symbols_str:
        return []
    return [s.strip().upper() for s in symbols_str.split(',') if s.strip()]


async def process_unprocessed_articles(batch_size: int, max_articles: Optional[int]):
    """Process all unprocessed articles."""
    db = next(get_db())
    worker = SentimentWorker(db)
    
    try:
        logging.info("Finding unprocessed articles...")
        
        # Query unprocessed articles
        query = db.query(NewsArticle).filter(
            NewsArticle.is_processed == False
        ).order_by(NewsArticle.published_at.desc())
        
        if max_articles:
            query = query.limit(max_articles)
            
        articles = query.all()
        
        if not articles:
            logging.info("No unprocessed articles found")
            return
        
        logging.info(f"Found {len(articles)} unprocessed articles")
        
        # Process in batches
        total_processed = 0
        
        for i in range(0, len(articles), batch_size):
            batch = articles[i:i + batch_size]
            
            logging.info(f"Processing batch {i//batch_size + 1}/{(len(articles)-1)//batch_size + 1} ({len(batch)} articles)")
            
            try:
                processed_count = await worker.process_sentiment_batch(batch)
                total_processed += processed_count
                
                logging.info(f"Processed {processed_count}/{len(batch)} articles in batch")
                
            except Exception as e:
                logging.error(f"Batch processing failed: {e}")
                continue
        
        logging.info(f"Processing complete. Total processed: {total_processed}/{len(articles)}")
        
    except Exception as e:
        logging.error(f"Sentiment processing failed: {e}")
        raise
    finally:
        db.close()


async def process_specific_articles(article_ids: List[int]):
    """Process specific articles by ID."""
    db = next(get_db())
    worker = SentimentWorker(db)
    
    try:
        logging.info(f"Processing articles: {article_ids}")
        
        # Fetch articles
        articles = db.query(NewsArticle).filter(
            NewsArticle.id.in_(article_ids)
        ).all()
        
        if not articles:
            logging.error("No articles found for given IDs")
            return
        
        found_ids = [article.id for article in articles]
        missing_ids = set(article_ids) - set(found_ids)
        
        if missing_ids:
            logging.warning(f"Articles not found: {missing_ids}")
        
        logging.info(f"Found {len(articles)} articles to process")
        
        # Process each article
        processed_count = 0
        
        for article in articles:
            try:
                logging.info(f"Processing article {article.id}: {article.title[:50]}...")
                
                success = await worker.process_article_sentiment(article)
                if success:
                    processed_count += 1
                    logging.info(f"Successfully processed article {article.id}")
                else:
                    logging.error(f"Failed to process article {article.id}")
                    
            except Exception as e:
                logging.error(f"Error processing article {article.id}: {e}")
                continue
        
        logging.info(f"Processing complete. Processed {processed_count}/{len(articles)} articles")
        
    except Exception as e:
        logging.error(f"Article processing failed: {e}")
        raise
    finally:
        db.close()


async def reprocess_by_symbols(symbols: List[str], days_back: int):
    """Reprocess articles for specific symbols."""
    db = next(get_db())
    worker = SentimentWorker(db)
    
    try:
        logging.info(f"Reprocessing articles for symbols: {symbols}")
        
        # Calculate date range
        cutoff_date = datetime.utcnow() - timedelta(days=days_back)
        
        # Query articles mapped to assets with these symbols
        query = """
        SELECT DISTINCT na.id
        FROM news_articles na
        JOIN news_asset_map nam ON na.id = nam.article_id
        JOIN companies c ON nam.asset_id = c.id
        WHERE c.symbol = ANY(%s)
        AND na.published_at >= %s
        ORDER BY na.published_at DESC
        """
        
        result = db.execute(query, (symbols, cutoff_date))
        article_ids = [row[0] for row in result.fetchall()]
        
        if not article_ids:
            logging.info("No articles found for given symbols")
            return
        
        logging.info(f"Found {len(article_ids)} articles to reprocess")
        
        # Delete existing sentiment analysis
        delete_query = """
        DELETE FROM news_sentiments ns
        WHERE ns.article_id IN %s
        """
        
        db.execute(delete_query, (tuple(article_ids),))
        db.commit()
        
        logging.info("Deleted existing sentiment analysis")
        
        # Fetch and reprocess articles
        articles = db.query(NewsArticle).filter(
            NewsArticle.id.in_(article_ids)
        ).all()
        
        processed_count = await worker.process_sentiment_batch(articles)
        
        logging.info(f"Reprocessing complete. Processed {processed_count}/{len(articles)} articles")
        
    except Exception as e:
        logging.error(f"Reprocessing failed: {e}")
        raise
    finally:
        db.close()


def get_processing_stats():
    """Get and display processing statistics."""
    db = next(get_db())
    
    try:
        # Total articles
        total_articles = db.query(NewsArticle).count()
        
        # Processed articles
        processed_articles = db.query(NewsArticle).filter(
            NewsArticle.is_processed == True
        ).count()
        
        # Recent articles (last 7 days)
        week_ago = datetime.utcnow() - timedelta(days=7)
        recent_articles = db.query(NewsArticle).filter(
            NewsArticle.published_at >= week_ago
        ).count()
        
        # Sentiment analysis count
        total_sentiments = db.query(NewsSentiment).count()
        
        # Recent sentiments
        recent_sentiments = db.query(NewsSentiment).join(NewsArticle).filter(
            NewsArticle.published_at >= week_ago
        ).count()
        
        print("\n=== Processing Statistics ===")
        print(f"Total articles: {total_articles}")
        print(f"Processed articles: {processed_articles} ({processed_articles/total_articles*100:.1f}%)" if total_articles > 0 else "Processed articles: 0")
        print(f"Recent articles (7 days): {recent_articles}")
        print(f"Total sentiment analyses: {total_sentiments}")
        print(f"Recent sentiments (7 days): {recent_sentiments}")
        print()
        
    except Exception as e:
        logging.error(f"Failed to get statistics: {e}")
    finally:
        db.close()


def main():
    """Main CLI function."""
    parser = argparse.ArgumentParser(
        description="Process sentiment analysis for news articles"
    )
    
    # Processing mode
    mode_group = parser.add_mutually_exclusive_group(required=True)
    mode_group.add_argument(
        '--unprocessed',
        action='store_true',
        help='Process all unprocessed articles'
    )
    mode_group.add_argument(
        '--article-ids',
        type=str,
        help='Comma-separated list of article IDs to process'
    )
    mode_group.add_argument(
        '--reprocess',
        action='store_true',
        help='Reprocess articles (use with --symbols)'
    )
    mode_group.add_argument(
        '--stats',
        action='store_true',
        help='Show processing statistics'
    )
    
    # Processing parameters
    parser.add_argument(
        '--batch-size',
        type=int,
        default=25,
        help='Batch size for processing (default: 25)'
    )
    parser.add_argument(
        '--max-articles',
        type=int,
        help='Maximum number of articles to process'
    )
    parser.add_argument(
        '--symbols',
        type=str,
        help='Comma-separated symbols for reprocessing'
    )
    parser.add_argument(
        '--days-back',
        type=int,
        default=30,
        help='Days back for reprocessing (default: 30)'
    )
    
    # Logging
    parser.add_argument(
        '--verbose', '-v',
        action='store_true',
        help='Enable verbose logging'
    )
    
    args = parser.parse_args()
    
    # Setup logging
    setup_logging(args.verbose)
    
    # Validate arguments
    if args.batch_size <= 0:
        parser.error("Batch size must be positive")
    if args.max_articles and args.max_articles <= 0:
        parser.error("Max articles must be positive")
    if args.reprocess and not args.symbols:
        parser.error("--reprocess requires --symbols")
    
    try:
        # Handle stats mode
        if args.stats:
            get_processing_stats()
            return 0
        
        # Run processing based on mode
        if args.unprocessed:
            asyncio.run(process_unprocessed_articles(
                batch_size=args.batch_size,
                max_articles=args.max_articles
            ))
        elif args.article_ids:
            article_ids = parse_ids(args.article_ids)
            asyncio.run(process_specific_articles(article_ids))
        elif args.reprocess:
            symbols = parse_symbols(args.symbols)
            asyncio.run(reprocess_by_symbols(
                symbols=symbols,
                days_back=args.days_back
            ))
            
        logging.info("Sentiment processing completed successfully")
        
    except KeyboardInterrupt:
        logging.info("Processing interrupted by user")
    except Exception as e:
        logging.error(f"Processing failed: {e}")
        return 1
    
    return 0


if __name__ == '__main__':
    exit(main())