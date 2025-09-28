"""
Main configuration and entry point for the Unified News Collection System
"""

import os
import logging
import argparse
from datetime import datetime
from typing import Dict, Any, Optional

from .news_collector.unified_pipeline import UnifiedNewsPipeline

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(f'logs/news_collection_{datetime.now().strftime("%Y%m%d")}.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

class NewsCollectionConfig:
    """Configuration class for the news collection system"""
    
    def __init__(self):
        # Database configuration
        self.database_url = os.getenv(
            'DATABASE_URL', 
            'postgresql://user:password@localhost:5432/news_db'
        )
        
        # API Keys configuration
        self.api_keys = {
            # Twitter/X API
            'twitter_bearer': os.getenv('TWITTER_BEARER_TOKEN'),
            'twitter_api_key': os.getenv('TWITTER_API_KEY'),
            'twitter_api_secret': os.getenv('TWITTER_API_SECRET'),
            'twitter_access_token': os.getenv('TWITTER_ACCESS_TOKEN'),
            'twitter_access_token_secret': os.getenv('TWITTER_ACCESS_TOKEN_SECRET'),
            
            # Reddit API
            'reddit_client_id': os.getenv('REDDIT_CLIENT_ID'),
            'reddit_client_secret': os.getenv('REDDIT_CLIENT_SECRET'),
            'reddit_user_agent': os.getenv('REDDIT_USER_AGENT', 'NewsCollector/1.0'),
            
            # SEC API
            'sec_api_key': os.getenv('SEC_API_KEY'),
            
            # Yahoo Finance (usually no key needed)
            'yahoo_finance_key': os.getenv('YAHOO_FINANCE_KEY'),
            
            # Alpha Vantage
            'alpha_vantage_key': os.getenv('ALPHA_VANTAGE_KEY'),
            
            # NewsAPI
            'news_api_key': os.getenv('NEWS_API_KEY'),
        }
        
        # Pipeline configuration
        self.pipeline_config = {
            'max_workers': int(os.getenv('MAX_WORKERS', '4')),
            'enable_scheduling': os.getenv('ENABLE_SCHEDULING', 'true').lower() == 'true',
            'default_hours_back': int(os.getenv('DEFAULT_HOURS_BACK', '24')),
            'max_articles_per_source': int(os.getenv('MAX_ARTICLES_PER_SOURCE', '100')),
            'batch_size_sentiment': int(os.getenv('BATCH_SIZE_SENTIMENT', '50')),
            'alert_impact_threshold': float(os.getenv('ALERT_IMPACT_THRESHOLD', '0.7')),
        }
        
        # Logging configuration
        self.log_level = os.getenv('LOG_LEVEL', 'INFO').upper()
        self.log_file = os.getenv('LOG_FILE', f'logs/news_collection_{datetime.now().strftime("%Y%m%d")}.log')

def create_pipeline(config: NewsCollectionConfig = None) -> UnifiedNewsPipeline:
    """
    Create and configure the unified news pipeline
    
    Args:
        config: Configuration object (optional)
        
    Returns:
        Configured UnifiedNewsPipeline instance
    """
    if config is None:
        config = NewsCollectionConfig()
    
    # Create logs directory if it doesn't exist
    os.makedirs('logs', exist_ok=True)
    
    # Set logging level
    logging.getLogger().setLevel(getattr(logging, config.log_level))
    
    logger.info("Initializing Unified News Collection Pipeline")
    logger.info(f"Database URL: {config.database_url}")
    logger.info(f"API Keys configured: {[k for k, v in config.api_keys.items() if v is not None]}")
    
    # Create pipeline
    pipeline = UnifiedNewsPipeline(
        database_url=config.database_url,
        api_keys=config.api_keys,
        max_workers=config.pipeline_config['max_workers'],
        enable_scheduling=config.pipeline_config['enable_scheduling']
    )
    
    # Update pipeline configuration
    pipeline.collection_config.update({
        'default_hours_back': config.pipeline_config['default_hours_back'],
        'max_articles_per_source': config.pipeline_config['max_articles_per_source'],
        'batch_size_sentiment': config.pipeline_config['batch_size_sentiment'],
        'alert_impact_threshold': config.pipeline_config['alert_impact_threshold'],
    })
    
    logger.info("Pipeline initialized successfully")
    return pipeline

def main():
    """Main entry point for command-line usage"""
    parser = argparse.ArgumentParser(description='Unified News Collection System')
    
    # Command selection
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Collect command
    collect_parser = subparsers.add_parser('collect', help='Collect news from all sources')
    collect_parser.add_argument('--hours', type=int, default=24, help='Hours to look back')
    collect_parser.add_argument('--max-articles', type=int, default=100, help='Max articles per source')
    collect_parser.add_argument('--sources', nargs='+', help='Specific sources to collect from')
    
    # Stock-specific collection
    stock_parser = subparsers.add_parser('stock', help='Collect news for specific stock')
    stock_parser.add_argument('symbol', help='Stock symbol (e.g., AAPL, GOOGL)')
    stock_parser.add_argument('--hours', type=int, default=24, help='Hours to look back')
    stock_parser.add_argument('--max-articles', type=int, default=50, help='Max articles per source')
    
    # Schedule command
    schedule_parser = subparsers.add_parser('schedule', help='Run scheduled collections')
    schedule_parser.add_argument('--daemon', action='store_true', help='Run as daemon process')
    
    # Stats command
    stats_parser = subparsers.add_parser('stats', help='Show pipeline statistics')
    
    # Recent collections command
    recent_parser = subparsers.add_parser('recent', help='Show recent collection jobs')
    recent_parser.add_argument('--limit', type=int, default=10, help='Number of recent jobs to show')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    # Load configuration
    config = NewsCollectionConfig()
    
    # Create pipeline
    pipeline = create_pipeline(config)
    
    try:
        if args.command == 'collect':
            logger.info(f"Starting news collection (hours={args.hours}, max_articles={args.max_articles})")
            result = pipeline.collect_all_news(
                hours_back=args.hours,
                max_articles=args.max_articles,
                sources=args.sources
            )
            print_collection_result(result)
            
        elif args.command == 'stock':
            logger.info(f"Starting stock-specific collection for {args.symbol}")
            result = pipeline.collect_stock_news(
                stock_symbol=args.symbol.upper(),
                hours_back=args.hours,
                max_articles=args.max_articles
            )
            print_collection_result(result)
            
        elif args.command == 'schedule':
            if args.daemon:
                logger.info("Starting scheduled collections as daemon")
                pipeline.run_scheduler()  # This runs indefinitely
            else:
                logger.info("Running one-time scheduled check")
                # Import schedule here to avoid dependency issues
                try:
                    import schedule
                    schedule.run_pending()
                    logger.info("Scheduled tasks completed")
                except ImportError:
                    logger.error("Schedule package not installed")
                    
        elif args.command == 'stats':
            stats = pipeline.get_pipeline_stats()
            print_pipeline_stats(stats)
            
        elif args.command == 'recent':
            jobs = pipeline.get_recent_collections(limit=args.limit)
            print_recent_jobs(jobs)
            
    except Exception as e:
        logger.error(f"Error executing command '{args.command}': {e}")
        raise

def print_collection_result(result: Dict[str, Any]):
    """Print formatted collection results"""
    if result['success']:
        print("\\n" + "="*60)
        print("NEWS COLLECTION COMPLETED SUCCESSFULLY")
        print("="*60)
        print(f"Job ID: {result['job_id']}")
        print(f"Articles Collected: {result.get('articles_collected', 0)}")
        if 'articles_unique' in result:
            print(f"Articles After Deduplication: {result['articles_unique']}")
        print(f"Articles Processed: {result.get('articles_processed', 0)}")
        print(f"Articles Stored: {result.get('articles_stored', 0)}")
        print(f"Alerts Generated: {result.get('alerts_generated', 0)}")
        print(f"Execution Time: {result['execution_time']:.2f} seconds")
        
        if result.get('errors'):
            print("\\nErrors Encountered:")
            for error in result['errors']:
                print(f"  - {error}")
        
        print("="*60)
    else:
        print("\\n" + "="*60)
        print("NEWS COLLECTION FAILED")
        print("="*60)
        print(f"Job ID: {result['job_id']}")
        print(f"Error: {result['error']}")
        print(f"Execution Time: {result['execution_time']:.2f} seconds")
        if result.get('errors'):
            print("\\nAdditional Errors:")
            for error in result['errors']:
                print(f"  - {error}")
        print("="*60)

def print_pipeline_stats(stats: Dict[str, Any]):
    """Print formatted pipeline statistics"""
    print("\\n" + "="*60)
    print("PIPELINE STATISTICS")
    print("="*60)
    print(f"Total Collections: {stats['total_collections']}")
    print(f"Total Articles Collected: {stats['total_articles_collected']}")
    print(f"Total Articles Processed: {stats['total_articles_processed']}")
    print(f"Total Articles Stored: {stats['total_articles_stored']}")
    print(f"Average Processing Time: {stats['average_processing_time']:.2f} seconds")
    if stats['last_collection_time']:
        print(f"Last Collection: {stats['last_collection_time']}")
    
    if stats['errors']:
        print(f"\\nRecent Errors ({len(stats['errors'])}):")
        for error in stats['errors'][-5:]:  # Show last 5 errors
            print(f"  - {error}")
    print("="*60)

def print_recent_jobs(jobs: list):
    """Print formatted recent job information"""
    print("\\n" + "="*80)
    print("RECENT COLLECTION JOBS")
    print("="*80)
    
    if not jobs:
        print("No recent jobs found.")
        print("="*80)
        return
    
    for job in jobs:
        print(f"Job ID: {job['job_id']}")
        print(f"Type: {job['collector_type']}")
        print(f"Status: {job['status']}")
        print(f"Started: {job['started_at']}")
        if job['completed_at']:
            print(f"Completed: {job['completed_at']}")
        print(f"Articles Collected: {job['articles_collected'] or 0}")
        print(f"Articles Processed: {job['articles_processed'] or 0}")
        print(f"Errors: {job['errors_encountered'] or 0}")
        print("-" * 60)
    
    print("="*80)

# Example configuration for environment variables
def create_env_template():
    """Create a template .env file with all required variables"""
    template = '''# Database Configuration
DATABASE_URL=postgresql://username:password@localhost:5432/news_db

# Twitter/X API Keys
TWITTER_BEARER_TOKEN=your_bearer_token_here
TWITTER_API_KEY=your_api_key_here
TWITTER_API_SECRET=your_api_secret_here
TWITTER_ACCESS_TOKEN=your_access_token_here
TWITTER_ACCESS_TOKEN_SECRET=your_access_token_secret_here

# Reddit API Keys
REDDIT_CLIENT_ID=your_reddit_client_id
REDDIT_CLIENT_SECRET=your_reddit_client_secret
REDDIT_USER_AGENT=NewsCollector/1.0

# SEC API Key (optional)
SEC_API_KEY=your_sec_api_key

# Other API Keys
ALPHA_VANTAGE_KEY=your_alpha_vantage_key
NEWS_API_KEY=your_news_api_key

# Pipeline Configuration
MAX_WORKERS=4
ENABLE_SCHEDULING=true
DEFAULT_HOURS_BACK=24
MAX_ARTICLES_PER_SOURCE=100
BATCH_SIZE_SENTIMENT=50
ALERT_IMPACT_THRESHOLD=0.7

# Logging Configuration
LOG_LEVEL=INFO
LOG_FILE=logs/news_collection.log
'''
    
    with open('.env.template', 'w') as f:
        f.write(template)
    
    print("Created .env.template file. Copy to .env and configure your API keys.")

if __name__ == "__main__":
    main()