#!/usr/bin/env python3
"""
CLI script for collecting financial news.

Usage:
    python collect_news.py --help
    python collect_news.py --symbols AAPL,TSLA,SPY --limit 100
    python collect_news.py --all-assets --days 7
"""

import argparse
import asyncio
import logging
from datetime import datetime, timedelta
from typing import List, Optional

from Lumia.database import get_db
from Lumia.services.news_collector import NewsCollector
from Lumia.models.company import Company


def setup_logging(verbose: bool = False):
    """Setup logging configuration."""
    level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(
        level=level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )


def parse_symbols(symbols_str: str) -> List[str]:
    """Parse comma-separated symbols string."""
    if not symbols_str:
        return []
    return [s.strip().upper() for s in symbols_str.split(',') if s.strip()]


async def collect_news_for_symbols(
    symbols: List[str], 
    limit: int, 
    days: int,
    min_match_score: float
):
    """Collect news for specific symbols."""
    db = next(get_db())
    collector = NewsCollector(db)
    
    try:
        logging.info(f"Starting news collection for symbols: {symbols}")
        
        # If symbols provided, use them directly
        if symbols:
            target_symbols = symbols
        else:
            # Get all active company symbols from database
            logging.info("Fetching all company symbols from database...")
            companies = db.query(Company).filter(Company.is_active == True).all()
            target_symbols = [company.symbol for company in companies]
            logging.info(f"Found {len(target_symbols)} active companies")
        
        if not target_symbols:
            logging.error("No symbols to process")
            return
        
        # Collect news for each symbol
        total_articles = 0
        total_mapped = 0
        
        for symbol in target_symbols:
            try:
                logging.info(f"Collecting news for {symbol}...")
                
                # Collect news
                articles = await collector.collect_news_for_symbol(
                    symbol=symbol,
                    limit=limit,
                    days_back=days
                )
                
                if articles:
                    # Map articles to assets
                    mapped_count = await collector.map_articles_to_assets(
                        articles,
                        min_match_score=min_match_score
                    )
                    
                    total_articles += len(articles)
                    total_mapped += mapped_count
                    
                    logging.info(
                        f"Collected {len(articles)} articles for {symbol}, "
                        f"mapped {mapped_count} to assets"
                    )
                else:
                    logging.info(f"No articles found for {symbol}")
                    
            except Exception as e:
                logging.error(f"Error collecting news for {symbol}: {e}")
                continue
        
        logging.info(
            f"Collection complete. Total articles: {total_articles}, "
            f"Total mapped: {total_mapped}"
        )
        
    except Exception as e:
        logging.error(f"News collection failed: {e}")
        raise
    finally:
        db.close()


async def collect_general_news(limit: int, min_match_score: float):
    """Collect general financial news."""
    db = next(get_db())
    collector = NewsCollector(db)
    
    try:
        logging.info("Starting general financial news collection...")
        
        articles = await collector.fetch_financial_news(
            query="financial markets stocks economy",
            limit=limit
        )
        
        if articles:
            # Deduplicate articles
            unique_articles = collector.deduplicate_articles(articles)
            logging.info(f"Collected {len(unique_articles)} unique articles")
            
            # Map to assets using fuzzy matching
            mapped_count = await collector.map_articles_to_assets(
                unique_articles,
                min_match_score=min_match_score
            )
            
            logging.info(f"Mapped {mapped_count} articles to assets")
        else:
            logging.info("No general articles found")
            
    except Exception as e:
        logging.error(f"General news collection failed: {e}")
        raise
    finally:
        db.close()


def main():
    """Main CLI function."""
    parser = argparse.ArgumentParser(
        description="Collect financial news articles"
    )
    
    # Symbol selection
    symbol_group = parser.add_mutually_exclusive_group(required=True)
    symbol_group.add_argument(
        '--symbols',
        type=str,
        help='Comma-separated list of symbols (e.g., AAPL,TSLA,SPY)'
    )
    symbol_group.add_argument(
        '--all-assets',
        action='store_true',
        help='Collect news for all active assets in database'
    )
    symbol_group.add_argument(
        '--general',
        action='store_true',
        help='Collect general financial news'
    )
    
    # Collection parameters
    parser.add_argument(
        '--limit',
        type=int,
        default=50,
        help='Maximum articles per symbol (default: 50)'
    )
    parser.add_argument(
        '--days',
        type=int,
        default=7,
        help='Number of days back to search (default: 7)'
    )
    parser.add_argument(
        '--min-match-score',
        type=float,
        default=0.6,
        help='Minimum fuzzy match score for asset mapping (default: 0.6)'
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
    if args.limit <= 0:
        parser.error("Limit must be positive")
    if args.days <= 0:
        parser.error("Days must be positive")
    if not (0.0 <= args.min_match_score <= 1.0):
        parser.error("Min match score must be between 0.0 and 1.0")
    
    try:
        # Run collection based on mode
        if args.general:
            asyncio.run(collect_general_news(
                limit=args.limit,
                min_match_score=args.min_match_score
            ))
        else:
            symbols = parse_symbols(args.symbols) if args.symbols else []
            asyncio.run(collect_news_for_symbols(
                symbols=symbols,
                limit=args.limit,
                days=args.days,
                min_match_score=args.min_match_score
            ))
            
        logging.info("News collection completed successfully")
        
    except KeyboardInterrupt:
        logging.info("Collection interrupted by user")
    except Exception as e:
        logging.error(f"Collection failed: {e}")
        return 1
    
    return 0


if __name__ == '__main__':
    exit(main())