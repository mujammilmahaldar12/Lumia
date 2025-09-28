#!/usr/bin/env python3
"""
Automation CLI manager for Lumia Financial System.

This script manages the background scheduler service and provides controls
for starting, stopping, and monitoring the automation system.

Usage:
    python start_scheduler.py --help
    python start_scheduler.py start
    python start_scheduler.py start --config-check
    python start_scheduler.py status
    python start_scheduler.py test-job collect_news
"""

import argparse
import logging
import os
import sys
import signal
import time
from pathlib import Path
from typing import Optional

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from config import Config
from app.services.scheduler import SchedulerService


def setup_logging(verbose: bool = False) -> logging.Logger:
    """Setup logging for the CLI manager."""
    level = logging.DEBUG if verbose else logging.INFO
    
    # Ensure logs directory exists
    Path('logs').mkdir(exist_ok=True)
    
    logging.basicConfig(
        level=level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(),
            logging.FileHandler('logs/automation_manager.log', mode='a')
        ]
    )
    
    return logging.getLogger(__name__)


class AutomationManager:
    """Manager for the automation system."""
    
    def __init__(self, verbose: bool = False):
        self.logger = setup_logging(verbose)
        self.scheduler_service: Optional[SchedulerService] = None
        self.config = Config()
        
        # Signal handlers for graceful shutdown
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)
    
    def _signal_handler(self, signum, frame):
        """Handle shutdown signals."""
        self.logger.info(f"Received signal {signum}, shutting down...")
        if self.scheduler_service:
            self.scheduler_service.shutdown()
        sys.exit(0)
    
    def validate_environment(self) -> bool:
        """Validate that the environment is properly configured."""
        self.logger.info("Validating environment configuration...")
        
        try:
            # Check configuration
            if not self.config.validate_config():
                self.logger.error("Configuration validation failed")
                return False
            
            # Check database connectivity
            try:
                from database import get_db
                from sqlalchemy import text
                db = next(get_db())
                db.execute(text('SELECT 1'))
                db.close()
                self.logger.info("Database connectivity: OK")
            except Exception as e:
                self.logger.error(f"Database connectivity failed: {e}")
                return False
            
            # Check scripts directory
            scripts_dir = Path('scripts')
            required_scripts = ['collect_news.py', 'process_sentiment.py', 'generate_signals.py']
            
            for script in required_scripts:
                script_path = scripts_dir / script
                if not script_path.exists():
                    self.logger.error(f"Required script not found: {script_path}")
                    return False
            
            self.logger.info("All required scripts found")
            
            # Check API keys (if not mocking)
            if not self.config.MOCK_EXTERNAL_APIS:
                if not self.config.NEWSAPI_KEY:
                    self.logger.error("NEWSAPI_KEY is required")
                    return False
                self.logger.info("API keys: OK")
            
            # Check model dependencies
            try:
                import nltk
                # Try to access VADER
                from nltk.sentiment import SentimentIntensityAnalyzer
                self.logger.info("NLTK/VADER: OK")
            except Exception as e:
                self.logger.warning(f"NLTK/VADER setup issue: {e}")
            
            if self.config.USE_FINBERT:
                try:
                    from transformers import AutoTokenizer
                    self.logger.info("Transformers library: OK")
                except Exception as e:
                    self.logger.warning(f"Transformers setup issue: {e}")
            
            self.logger.info("Environment validation completed successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"Environment validation failed: {e}")
            return False
    
    def start_scheduler(self, config_check: bool = False) -> bool:
        """Start the automation scheduler."""
        try:
            # Validate environment first
            if config_check or not self.validate_environment():
                if config_check:
                    self.logger.info("Configuration check completed")
                    return True
                else:
                    self.logger.error("Environment validation failed, cannot start scheduler")
                    return False
            
            self.logger.info("Starting Lumia automation system...")
            
            # Create and start scheduler service
            self.scheduler_service = SchedulerService()
            
            self.logger.info("Scheduler service created, starting jobs...")
            self.scheduler_service.start()  # This will block
            
            return True
            
        except KeyboardInterrupt:
            self.logger.info("Scheduler interrupted by user")
            return True
        except Exception as e:
            self.logger.error(f"Failed to start scheduler: {e}")
            return False
    
    def test_job(self, job_name: str) -> bool:
        """Test a specific job manually."""
        self.logger.info(f"Testing job: {job_name}")
        
        try:
            scheduler_service = SchedulerService()
            
            if job_name == 'collect_news':
                success = scheduler_service.collect_news_job()
            elif job_name == 'process_sentiment':
                success = scheduler_service.process_sentiment_job()
            elif job_name == 'generate_signals':
                success = scheduler_service.generate_signals_job()
            elif job_name == 'weekend_maintenance':
                success = scheduler_service.weekend_maintenance_job()
            elif job_name == 'emergency_recovery':
                success = scheduler_service.emergency_recovery_job()
            else:
                self.logger.error(f"Unknown job: {job_name}")
                self.logger.info("Available jobs: collect_news, process_sentiment, generate_signals, weekend_maintenance, emergency_recovery")
                return False
            
            if success:
                self.logger.info(f"Job {job_name} completed successfully")
            else:
                self.logger.error(f"Job {job_name} failed")
            
            return success
            
        except Exception as e:
            self.logger.error(f"Failed to test job {job_name}: {e}")
            return False
    
    def show_status(self) -> bool:
        """Show current system status."""
        self.logger.info("Checking system status...")
        
        try:
            # Database status
            try:
                from database import get_db
                db = next(get_db())
                
                # Check recent data
                from models.news_article import NewsArticle
                from models.news_sentiment import NewsSentiment
                from models.asset_daily_signals import AssetDailySignals
                from datetime import datetime, timedelta
                
                recent_cutoff = datetime.utcnow() - timedelta(days=1)
                
                recent_articles = db.query(NewsArticle).filter(
                    NewsArticle.fetched_at >= recent_cutoff
                ).count()
                
                recent_sentiments = db.query(NewsSentiment).filter(
                    NewsSentiment.created_at >= recent_cutoff
                ).count()
                
                recent_signals = db.query(AssetDailySignals).filter(
                    AssetDailySignals.date >= recent_cutoff.date()
                ).count()
                
                unprocessed_articles = db.query(NewsArticle).filter(
                    NewsArticle.is_processed == False
                ).count()
                
                db.close()
                
                print("\n=== Lumia Automation System Status ===")
                print(f"Database: Connected")
                print(f"Recent articles (24h): {recent_articles}")
                print(f"Recent sentiments (24h): {recent_sentiments}")
                print(f"Recent signals (24h): {recent_signals}")
                print(f"Unprocessed articles: {unprocessed_articles}")
                
            except Exception as e:
                print(f"Database status: ERROR - {e}")
                return False
            
            # Configuration status
            print(f"\nConfiguration:")
            print(f"  News collection interval: {self.config.NEWS_COLLECTION_INTERVAL_HOURS} hour(s)")
            print(f"  Sentiment processing interval: {self.config.SENTIMENT_PROCESSING_INTERVAL_HOURS} hour(s)")
            print(f"  Market close time: {self.config.MARKET_CLOSE_HOUR}:{self.config.MARKET_CLOSE_MINUTE:02d}")
            print(f"  Timezone: {self.config.SCHEDULER_TIMEZONE}")
            print(f"  Debug mode: {self.config.DEBUG_MODE}")
            
            # API status
            print(f"\nExternal Services:")
            if self.config.MOCK_EXTERNAL_APIS:
                print("  NewsAPI: MOCKED")
            else:
                print(f"  NewsAPI: {'CONFIGURED' if self.config.NEWSAPI_KEY else 'NOT CONFIGURED'}")
            
            print(f"  FinBERT: {'ENABLED' if self.config.USE_FINBERT else 'DISABLED'}")
            
            # File system status
            logs_dir = Path('logs')
            if logs_dir.exists():
                log_files = list(logs_dir.glob('*.log'))
                print(f"\nLogs: {len(log_files)} file(s) in logs/")
            else:
                print(f"\nLogs: Directory not found")
            
            print()
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to get status: {e}")
            return False
    
    def create_sample_env_file(self) -> bool:
        """Create a sample .env file with configuration examples."""
        env_content = """# Lumia Financial Analytics System Configuration

# Database
DATABASE_URL=postgresql://postgres:password@localhost:5432/lumia_db

# API Keys
NEWSAPI_KEY=your_newsapi_key_here

# Scheduler Settings
NEWS_COLLECTION_INTERVAL_HOURS=1
SENTIMENT_PROCESSING_INTERVAL_HOURS=1
MARKET_CLOSE_HOUR=16
MARKET_CLOSE_MINUTE=0
SCHEDULER_TIMEZONE=America/New_York

# News Collection
NEWS_ARTICLES_PER_SYMBOL=50
MIN_FUZZY_MATCH_SCORE=0.7

# Sentiment Processing
SENTIMENT_BATCH_SIZE=25
MAX_SENTIMENT_ARTICLES_PER_RUN=200
USE_FINBERT=True

# Portfolio Settings
DEFAULT_RISK_FREE_RATE=0.05
MIN_MARKET_CAP=1000000000
MAX_PORTFOLIO_ASSETS=10
CRITICAL_SYMBOLS=SPY,QQQ,AAPL,MSFT,TSLA

# Logging
LOG_LEVEL=INFO
SCHEDULER_LOG_LEVEL=INFO
LOG_RETENTION_DAYS=30

# Development/Testing
DEBUG_MODE=False
MOCK_EXTERNAL_APIS=False
SKIP_MODEL_DOWNLOAD=False
"""
        
        try:
            env_file = Path('.env.sample')
            env_file.write_text(env_content)
            self.logger.info(f"Created sample environment file: {env_file}")
            print(f"Sample configuration created: {env_file}")
            print("Copy this to .env and update with your settings")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to create sample env file: {e}")
            return False


def main():
    """Main CLI function."""
    parser = argparse.ArgumentParser(
        description="Lumia Automation System Manager",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python start_scheduler.py start                    # Start the automation system
  python start_scheduler.py start --config-check     # Validate config and exit
  python start_scheduler.py status                   # Show system status
  python start_scheduler.py test-job collect_news    # Test news collection job
  python start_scheduler.py create-env               # Create sample .env file
        """
    )
    
    # Commands
    parser.add_argument(
        'command',
        choices=['start', 'status', 'test-job', 'create-env'],
        help='Command to execute'
    )
    
    # Options
    parser.add_argument(
        '--config-check',
        action='store_true',
        help='Only validate configuration and exit (use with start)'
    )
    parser.add_argument(
        '--job',
        type=str,
        help='Job name for test-job command'
    )
    parser.add_argument(
        '--verbose', '-v',
        action='store_true',
        help='Enable verbose logging'
    )
    
    args = parser.parse_args()
    
    # Validate job argument
    if args.command == 'test-job' and not args.job:
        parser.error("test-job command requires --job argument")
    
    try:
        manager = AutomationManager(verbose=args.verbose)
        
        if args.command == 'start':
            success = manager.start_scheduler(config_check=args.config_check)
        elif args.command == 'status':
            success = manager.show_status()
        elif args.command == 'test-job':
            success = manager.test_job(args.job)
        elif args.command == 'create-env':
            success = manager.create_sample_env_file()
        else:
            parser.error(f"Unknown command: {args.command}")
        
        return 0 if success else 1
        
    except KeyboardInterrupt:
        print("\nOperation interrupted by user")
        return 1
    except Exception as e:
        print(f"Error: {e}")
        return 1


if __name__ == '__main__':
    exit(main())