"""News Article model for storing fetched news articles."""

from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, Float, Index, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from database import Base


class NewsArticle(Base):
    """
    Model for storing news articles fetched from various sources.
    Links to specific assets (stocks) for sentiment analysis.
    """
    __tablename__ = "news_articles"

    id = Column(Integer, primary_key=True, index=True)
    asset_id = Column(Integer, ForeignKey('assets.id'), nullable=True, index=True)  # Link to asset
    asset_symbol = Column(String(50), nullable=True, index=True)  # Redundant but useful for queries
    
    url = Column(String(2000), unique=True, nullable=False)  # Source URL - used for deduplication
    title = Column(String(500), nullable=False)
    summary = Column(Text)  # Article summary/description
    content = Column(Text)  # Full article content if available
    source = Column(String(100), nullable=False)  # News source (e.g., "newsapi", "finnhub")
    author = Column(String(200))
    published_at = Column(DateTime)  # When article was published
    fetched_at = Column(DateTime, default=func.now())  # When we fetched it
    
    # Sentiment analysis results
    is_processed = Column(Boolean, default=False)  # Whether sentiment analysis has been run
    sentiment_score = Column(Float, nullable=True)  # -1.0 to 1.0 (negative to positive)
    sentiment_label = Column(String(20), nullable=True)  # 'positive', 'negative', 'neutral'
    
    # Relationship to Asset
    asset = relationship("Asset", backref="news_articles")

    # Indexes for performance
    __table_args__ = (
        Index('idx_news_articles_url', 'url'),
        Index('idx_news_articles_asset_id', 'asset_id'),
        Index('idx_news_articles_asset_symbol', 'asset_symbol'),
        Index('idx_news_articles_published_at', 'published_at'),
        Index('idx_news_articles_is_processed', 'is_processed'),
        Index('idx_news_articles_source_published', 'source', 'published_at'),
        Index('idx_news_articles_asset_published', 'asset_id', 'published_at'),
    )

    def __repr__(self):
        return f"<NewsArticle(id={self.id}, title='{self.title[:50]}...', source='{self.source}')>"