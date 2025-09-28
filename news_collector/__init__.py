"""
Unified News Collection System

A comprehensive news collection and sentiment analysis system that gathers financial news
from multiple sources, processes it through FinGPT-based sentiment analysis, and stores
results in a database for further analysis.

Main Components:
- Stock Research Collector: Yahoo Finance, MarketWatch, Seeking Alpha, Reuters, CNBC
- Social Media Collector: Twitter/X and Reddit integration
- Company Website Collector: SEC EDGAR filings and company IR pages
- Algorithmic Trading Collector: Fintech publications and regulatory sources
- Sentiment Analyzer: FinGPT/FinBERT-powered financial sentiment analysis
- Unified Pipeline: Orchestrates all collectors with database storage and scheduling

Usage:
    from Lumia.main import create_pipeline
    
    pipeline = create_pipeline()
    result = pipeline.collect_all_news(hours_back=24)
    print(result)

Command Line Usage:
    python -m Lumia.main collect --hours 24 --max-articles 100
    python -m Lumia.main stock AAPL --hours 12
    python -m Lumia.main schedule --daemon
    python -m Lumia.main stats
"""

from .unified_pipeline import UnifiedNewsPipeline
from .base import NewsItem, CollectionResult, BaseNewsCollector
from .stock_research_collector import StockResearchCollector
from .social_media_collector import SocialMediaCollector
from .company_website_collector import CompanyWebsiteCollector
from .algo_trading_collector import AlgoTradingNewsCollector
from .sentiment_analyzer import FinGPTAnalyzer

__version__ = "1.0.0"
__author__ = "News Collection System"
__description__ = "Comprehensive financial news collection and sentiment analysis system"

__all__ = [
    'UnifiedNewsPipeline',
    'NewsItem',
    'CollectionResult',
    'BaseNewsCollector',
    'StockResearchCollector',
    'SocialMediaCollector',
    'CompanyWebsiteCollector',
    'AlgoTradingNewsCollector',
    'FinGPTAnalyzer',
]

# Package-level configuration
DEFAULT_CONFIG = {
    'max_workers': 4,
    'enable_scheduling': True,
    'default_hours_back': 24,
    'max_articles_per_source': 100,
    'batch_size_sentiment': 50,
    'alert_impact_threshold': 0.7,
    'deduplication_threshold': 0.8,
}

def get_version():
    """Get package version"""
    return __version__

def get_default_config():
    """Get default configuration dictionary"""
    return DEFAULT_CONFIG.copy()
