"""
Configuration settings for Lumia Financial Analytics System.

This module contains all environment variable configurations and default settings
for the application, scheduler, and external service integrations.
"""

import os
from typing import Optional
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


class Config:
    """Main configuration class."""
    
    # Database Configuration
    DATABASE_URL: str = os.getenv(
        'DATABASE_URL',
        'postgresql://postgres:password@localhost:5432/lumia_db'
    )
    
    # API Keys
    NEWSAPI_KEY: Optional[str] = os.getenv('NEWSAPI_KEY')
    
    # News Collection Settings
    NEWS_COLLECTION_INTERVAL_HOURS: int = int(os.getenv('NEWS_COLLECTION_INTERVAL_HOURS', '1'))
    NEWS_API_RATE_LIMIT: int = int(os.getenv('NEWS_API_RATE_LIMIT', '100'))  # requests per hour
    NEWS_ARTICLES_PER_SYMBOL: int = int(os.getenv('NEWS_ARTICLES_PER_SYMBOL', '50'))
    MIN_FUZZY_MATCH_SCORE: float = float(os.getenv('MIN_FUZZY_MATCH_SCORE', '0.7'))
    
    # Sentiment Processing Settings
    SENTIMENT_PROCESSING_INTERVAL_HOURS: int = int(os.getenv('SENTIMENT_PROCESSING_INTERVAL_HOURS', '1'))
    SENTIMENT_BATCH_SIZE: int = int(os.getenv('SENTIMENT_BATCH_SIZE', '25'))
    MAX_SENTIMENT_ARTICLES_PER_RUN: int = int(os.getenv('MAX_SENTIMENT_ARTICLES_PER_RUN', '200'))
    
    # Signal Generation Settings
    MARKET_CLOSE_HOUR: int = int(os.getenv('MARKET_CLOSE_HOUR', '16'))  # 4 PM EST
    MARKET_CLOSE_MINUTE: int = int(os.getenv('MARKET_CLOSE_MINUTE', '0'))
    SIGNAL_LOOKBACK_DAYS: int = int(os.getenv('SIGNAL_LOOKBACK_DAYS', '30'))
    
    # Scheduler Settings
    SCHEDULER_TIMEZONE: str = os.getenv('SCHEDULER_TIMEZONE', 'America/New_York')
    SCHEDULER_LOG_LEVEL: str = os.getenv('SCHEDULER_LOG_LEVEL', 'INFO')
    SCHEDULER_GRACE_PERIOD_MINUTES: int = int(os.getenv('SCHEDULER_GRACE_PERIOD_MINUTES', '5'))
    
    # Market Hours (for scheduling)
    MARKET_OPEN_HOUR: int = int(os.getenv('MARKET_OPEN_HOUR', '9'))
    MARKET_OPEN_MINUTE: int = int(os.getenv('MARKET_OPEN_MINUTE', '30'))
    
    # Portfolio Recommendation Settings
    DEFAULT_RISK_FREE_RATE: float = float(os.getenv('DEFAULT_RISK_FREE_RATE', '0.05'))  # 5%
    MIN_MARKET_CAP: int = int(os.getenv('MIN_MARKET_CAP', '1000000000'))  # $1B
    MAX_PORTFOLIO_ASSETS: int = int(os.getenv('MAX_PORTFOLIO_ASSETS', '10'))
    
    # Critical Assets (always prioritized)
    CRITICAL_SYMBOLS: list = os.getenv('CRITICAL_SYMBOLS', 'SPY,QQQ,AAPL,MSFT,TSLA').split(',')
    
    # Logging Settings
    LOG_LEVEL: str = os.getenv('LOG_LEVEL', 'INFO')
    LOG_FILE_MAX_SIZE: int = int(os.getenv('LOG_FILE_MAX_SIZE', '10485760'))  # 10MB
    LOG_RETENTION_DAYS: int = int(os.getenv('LOG_RETENTION_DAYS', '30'))
    
    # FastAPI Settings
    API_HOST: str = os.getenv('API_HOST', '0.0.0.0')
    API_PORT: int = int(os.getenv('API_PORT', '8000'))
    API_WORKERS: int = int(os.getenv('API_WORKERS', '1'))
    DEBUG_MODE: bool = os.getenv('DEBUG_MODE', 'False').lower() == 'true'
    
    # External Service Timeouts
    HTTP_TIMEOUT_SECONDS: int = int(os.getenv('HTTP_TIMEOUT_SECONDS', '30'))
    DB_CONNECTION_TIMEOUT: int = int(os.getenv('DB_CONNECTION_TIMEOUT', '30'))
    
    # Model Settings
    USE_FINBERT: bool = os.getenv('USE_FINBERT', 'True').lower() == 'true'
    FINBERT_MODEL_NAME: str = os.getenv('FINBERT_MODEL_NAME', 'ProsusAI/finbert')
    NLTK_DATA_PATH: Optional[str] = os.getenv('NLTK_DATA_PATH')
    
    # Development/Testing
    SKIP_MODEL_DOWNLOAD: bool = os.getenv('SKIP_MODEL_DOWNLOAD', 'False').lower() == 'true'
    MOCK_EXTERNAL_APIS: bool = os.getenv('MOCK_EXTERNAL_APIS', 'False').lower() == 'true'
    
    @classmethod
    def validate_config(cls) -> bool:
        """Validate critical configuration settings."""
        errors = []
        
        # Check required API keys
        if not cls.NEWSAPI_KEY and not cls.MOCK_EXTERNAL_APIS:
            errors.append("NEWSAPI_KEY is required (or set MOCK_EXTERNAL_APIS=True)")
        
        # Validate database URL
        if not cls.DATABASE_URL:
            errors.append("DATABASE_URL is required")
        
        # Validate market hours
        if cls.MARKET_CLOSE_HOUR < cls.MARKET_OPEN_HOUR:
            errors.append("MARKET_CLOSE_HOUR must be after MARKET_OPEN_HOUR")
        
        # Validate intervals
        if cls.NEWS_COLLECTION_INTERVAL_HOURS < 1:
            errors.append("NEWS_COLLECTION_INTERVAL_HOURS must be at least 1")
        
        if cls.SENTIMENT_PROCESSING_INTERVAL_HOURS < 1:
            errors.append("SENTIMENT_PROCESSING_INTERVAL_HOURS must be at least 1")
        
        if errors:
            print("Configuration validation errors:")
            for error in errors:
                print(f"  - {error}")
            return False
        
        return True
    
    @classmethod
    def get_scheduler_config(cls) -> dict:
        """Get scheduler-specific configuration."""
        return {
            'timezone': cls.SCHEDULER_TIMEZONE,
            'news_interval_hours': cls.NEWS_COLLECTION_INTERVAL_HOURS,
            'sentiment_interval_hours': cls.SENTIMENT_PROCESSING_INTERVAL_HOURS,
            'market_close_hour': cls.MARKET_CLOSE_HOUR,
            'market_close_minute': cls.MARKET_CLOSE_MINUTE,
            'market_open_hour': cls.MARKET_OPEN_HOUR,
            'market_open_minute': cls.MARKET_OPEN_MINUTE,
            'grace_period_minutes': cls.SCHEDULER_GRACE_PERIOD_MINUTES,
            'log_level': cls.SCHEDULER_LOG_LEVEL
        }
    
    @classmethod
    def get_collection_config(cls) -> dict:
        """Get news collection configuration."""
        return {
            'api_key': cls.NEWSAPI_KEY,
            'rate_limit': cls.NEWS_API_RATE_LIMIT,
            'articles_per_symbol': cls.NEWS_ARTICLES_PER_SYMBOL,
            'min_match_score': cls.MIN_FUZZY_MATCH_SCORE,
            'timeout': cls.HTTP_TIMEOUT_SECONDS
        }
    
    @classmethod
    def get_sentiment_config(cls) -> dict:
        """Get sentiment processing configuration."""
        return {
            'batch_size': cls.SENTIMENT_BATCH_SIZE,
            'max_articles_per_run': cls.MAX_SENTIMENT_ARTICLES_PER_RUN,
            'use_finbert': cls.USE_FINBERT,
            'finbert_model': cls.FINBERT_MODEL_NAME,
            'skip_model_download': cls.SKIP_MODEL_DOWNLOAD
        }
    
    @classmethod
    def get_recommendation_config(cls) -> dict:
        """Get portfolio recommendation configuration."""
        return {
            'risk_free_rate': cls.DEFAULT_RISK_FREE_RATE,
            'min_market_cap': cls.MIN_MARKET_CAP,
            'max_assets': cls.MAX_PORTFOLIO_ASSETS,
            'critical_symbols': cls.CRITICAL_SYMBOLS
        }


def load_config_from_env_file(file_path: str = '.env'):
    """Load configuration from environment file."""
    try:
        from dotenv import load_dotenv
        load_dotenv(file_path)
        print(f"Loaded configuration from {file_path}")
        return True
    except ImportError:
        print("python-dotenv not installed, skipping .env file loading")
        return False
    except FileNotFoundError:
        print(f"Environment file {file_path} not found")
        return False


# Auto-load .env file if it exists
load_config_from_env_file()

# Global config instance (created after .env is loaded)
config = Config()