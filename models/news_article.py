"""News Article model for storing fetched news articles."""

from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, Index
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from database import Base


class NewsArticle(Base):
    """
    Model for storing news articles fetched from various sources.
    """
    __tablename__ = "news_articles"

    id = Column(Integer, primary_key=True, index=True)
    url = Column(String(2000), unique=True, nullable=False)  # Source URL - used for deduplication
    title = Column(String(500), nullable=False)
    summary = Column(Text)  # Article summary/description
    content = Column(Text)  # Full article content if available
    source = Column(String(100), nullable=False)  # News source (e.g., "newsapi", "reuters")
    author = Column(String(200))
    published_at = Column(DateTime)  # When article was published
    fetched_at = Column(DateTime, default=func.now())  # When we fetched it
    is_processed = Column(Boolean, default=False)  # Whether sentiment analysis has been run
    
    # Relationships
    asset_mappings = relationship("NewsAssetMap", back_populates="article")
    sentiments = relationship("NewsSentiment", back_populates="article")

    # Indexes for performance
    __table_args__ = (
        Index('idx_news_articles_url', 'url'),
        Index('idx_news_articles_published_at', 'published_at'),
        Index('idx_news_articles_is_processed', 'is_processed'),
        Index('idx_news_articles_source_published', 'source', 'published_at'),
    )

    def __repr__(self):
        return f"<NewsArticle(id={self.id}, title='{self.title[:50]}...', source='{self.source}')>"