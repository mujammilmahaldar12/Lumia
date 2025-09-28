"""
News Collector Database Models
Comprehensive models for storing financial news, sentiment analysis, and metadata
"""

from sqlalchemy import Column, Integer, String, DateTime, Text, Float, Boolean, ForeignKey, JSON, Index
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid

Base = declarative_base()

class NewsSource(Base):
    """News sources and their metadata"""
    __tablename__ = 'news_sources'
    
    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False, unique=True)
    base_url = Column(String(500), nullable=False)
    source_type = Column(String(50), nullable=False)  # 'financial_news', 'social_media', 'company_website', 'algo_trading'
    reliability_score = Column(Float, default=0.5)  # 0-1 reliability metric
    api_key_required = Column(Boolean, default=False)
    rate_limit_per_hour = Column(Integer, default=100)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    articles = relationship("NewsArticle", back_populates="source")

class NewsArticle(Base):
    """Financial news articles with metadata"""
    __tablename__ = 'news_articles'
    
    id = Column(Integer, primary_key=True)
    external_id = Column(String(255), nullable=True)  # Original ID from source
    title = Column(String(1000), nullable=False)
    content = Column(Text, nullable=True)
    summary = Column(Text, nullable=True)
    url = Column(String(2000), nullable=False)
    author = Column(String(255), nullable=True)
    published_at = Column(DateTime, nullable=False)
    collected_at = Column(DateTime, default=datetime.utcnow)
    
    # Source information
    source_id = Column(Integer, ForeignKey('news_sources.id'), nullable=False)
    
    # Article categorization
    article_type = Column(String(50), nullable=False)  # 'research', 'news', 'tweet', 'press_release', 'algo_news'
    category = Column(String(100), nullable=True)  # 'earnings', 'merger', 'ipo', 'regulation', etc.
    
    # Processing status
    is_processed = Column(Boolean, default=False)
    processing_error = Column(Text, nullable=True)
    
    # Metadata
    language = Column(String(10), default='en')
    word_count = Column(Integer, nullable=True)
    read_time_minutes = Column(Integer, nullable=True)
    
    # Raw data
    raw_data = Column(JSON, nullable=True)  # Store original API response
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    source = relationship("NewsSource", back_populates="articles")
    sentiments = relationship("SentimentAnalysis", back_populates="article")
    entities = relationship("ExtractedEntity", back_populates="article")
    stock_mentions = relationship("StockMention", back_populates="article")
    
    # Indexes
    __table_args__ = (
        Index('idx_article_published_at', 'published_at'),
        Index('idx_article_source_id', 'source_id'),
        Index('idx_article_type_category', 'article_type', 'category'),
        Index('idx_article_processed', 'is_processed'),
        Index('idx_article_external_id', 'external_id'),
    )

class SentimentAnalysis(Base):
    """Sentiment analysis results for news articles"""
    __tablename__ = 'sentiment_analysis'
    
    id = Column(Integer, primary_key=True)
    article_id = Column(Integer, ForeignKey('news_articles.id'), nullable=False)
    
    # Sentiment scores
    overall_sentiment = Column(String(20), nullable=False)  # 'positive', 'negative', 'neutral'
    sentiment_score = Column(Float, nullable=False)  # -1 to 1
    confidence_score = Column(Float, nullable=False)  # 0 to 1
    
    # Detailed sentiment breakdown
    bullish_score = Column(Float, default=0.0)  # 0 to 1
    bearish_score = Column(Float, default=0.0)  # 0 to 1
    uncertainty_score = Column(Float, default=0.0)  # 0 to 1
    
    # Market impact prediction
    market_impact_score = Column(Float, default=0.0)  # 0 to 1
    urgency_score = Column(Float, default=0.0)  # 0 to 1
    
    # Analysis metadata
    model_used = Column(String(100), nullable=False)  # 'finbert', 'fingpt', 'custom'
    model_version = Column(String(50), nullable=True)
    analysis_timestamp = Column(DateTime, default=datetime.utcnow)
    
    # Raw analysis results
    raw_analysis = Column(JSON, nullable=True)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    article = relationship("NewsArticle", back_populates="sentiments")
    
    # Indexes
    __table_args__ = (
        Index('idx_sentiment_article_id', 'article_id'),
        Index('idx_sentiment_overall', 'overall_sentiment'),
        Index('idx_sentiment_impact', 'market_impact_score'),
    )

class ExtractedEntity(Base):
    """Named entities extracted from news articles"""
    __tablename__ = 'extracted_entities'
    
    id = Column(Integer, primary_key=True)
    article_id = Column(Integer, ForeignKey('news_articles.id'), nullable=False)
    
    entity_text = Column(String(500), nullable=False)
    entity_type = Column(String(50), nullable=False)  # 'PERSON', 'ORG', 'STOCK', 'MONEY', 'DATE', etc.
    start_position = Column(Integer, nullable=True)
    end_position = Column(Integer, nullable=True)
    confidence_score = Column(Float, default=1.0)
    
    # Financial entity specific fields
    stock_symbol = Column(String(20), nullable=True)
    company_name = Column(String(500), nullable=True)
    monetary_value = Column(Float, nullable=True)
    currency = Column(String(10), nullable=True)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    article = relationship("NewsArticle", back_populates="entities")
    
    # Indexes
    __table_args__ = (
        Index('idx_entity_article_id', 'article_id'),
        Index('idx_entity_type', 'entity_type'),
        Index('idx_entity_stock_symbol', 'stock_symbol'),
    )

class StockMention(Base):
    """Explicit stock mentions and their context in articles"""
    __tablename__ = 'stock_mentions'
    
    id = Column(Integer, primary_key=True)
    article_id = Column(Integer, ForeignKey('news_articles.id'), nullable=False)
    
    # Stock information
    stock_symbol = Column(String(20), nullable=False)
    company_name = Column(String(500), nullable=True)
    exchange = Column(String(20), nullable=True)
    
    # Mention context
    mention_context = Column(Text, nullable=True)  # Surrounding text
    mention_type = Column(String(50), nullable=True)  # 'primary', 'secondary', 'comparison'
    sentiment = Column(String(20), nullable=True)  # Mention-specific sentiment
    
    # Position in article
    position_start = Column(Integer, nullable=True)
    position_end = Column(Integer, nullable=True)
    
    # Relevance scoring
    relevance_score = Column(Float, default=0.5)  # How relevant is this mention to the stock
    
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    article = relationship("NewsArticle", back_populates="stock_mentions")
    
    # Indexes
    __table_args__ = (
        Index('idx_stock_mention_article_id', 'article_id'),
        Index('idx_stock_mention_symbol', 'stock_symbol'),
        Index('idx_stock_mention_relevance', 'relevance_score'),
    )

class CollectionJob(Base):
    """Track news collection jobs and their status"""
    __tablename__ = 'collection_jobs'
    
    id = Column(Integer, primary_key=True)
    job_id = Column(String(100), nullable=False, unique=True, default=lambda: str(uuid.uuid4()))
    
    # Job configuration
    collector_type = Column(String(50), nullable=False)  # 'stock_research', 'social_media', etc.
    source_id = Column(Integer, ForeignKey('news_sources.id'), nullable=True)
    parameters = Column(JSON, nullable=True)  # Job-specific parameters
    
    # Execution details
    started_at = Column(DateTime, nullable=False)
    completed_at = Column(DateTime, nullable=True)
    status = Column(String(20), nullable=False, default='running')  # 'running', 'completed', 'failed'
    
    # Results
    articles_collected = Column(Integer, default=0)
    articles_processed = Column(Integer, default=0)
    errors_encountered = Column(Integer, default=0)
    
    # Error details
    error_message = Column(Text, nullable=True)
    error_traceback = Column(Text, nullable=True)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Indexes
    __table_args__ = (
        Index('idx_job_status', 'status'),
        Index('idx_job_started_at', 'started_at'),
        Index('idx_job_collector_type', 'collector_type'),
    )

class NewsAlert(Base):
    """High-impact news alerts and notifications"""
    __tablename__ = 'news_alerts'
    
    id = Column(Integer, primary_key=True)
    article_id = Column(Integer, ForeignKey('news_articles.id'), nullable=False)
    
    # Alert details
    alert_type = Column(String(50), nullable=False)  # 'high_impact', 'breaking', 'earnings', 'merger'
    priority = Column(String(20), nullable=False)  # 'low', 'medium', 'high', 'critical'
    impact_score = Column(Float, nullable=False)  # 0-1 predicted market impact
    
    # Stock-specific alerts
    affected_stocks = Column(JSON, nullable=True)  # List of stock symbols
    sector_impact = Column(String(100), nullable=True)
    
    # Alert metadata
    alert_message = Column(Text, nullable=False)
    is_sent = Column(Boolean, default=False)
    sent_at = Column(DateTime, nullable=True)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Indexes
    __table_args__ = (
        Index('idx_alert_priority', 'priority'),
        Index('idx_alert_impact', 'impact_score'),
        Index('idx_alert_type', 'alert_type'),
        Index('idx_alert_is_sent', 'is_sent'),
    )
