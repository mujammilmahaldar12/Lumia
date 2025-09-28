"""News Sentiment model for storing sentiment analysis results."""

from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Index
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from database import Base


class NewsSentiment(Base):
    """
    Model for storing sentiment analysis results for news articles.
    Each record represents sentiment for one article-asset pair.
    """
    __tablename__ = "news_sentiments"

    id = Column(Integer, primary_key=True, index=True)
    article_id = Column(Integer, ForeignKey("news_articles.id"), nullable=False)
    asset_id = Column(Integer, ForeignKey("assets.id"), nullable=False)
    
    # Sentiment analysis results
    model_name = Column(String(100), nullable=False)  # "finbert" or "vader"
    polarity = Column(Float, nullable=False)  # Overall sentiment (-1.0 to 1.0)
    pos = Column(Float, nullable=False)  # Positive sentiment score (0.0-1.0)
    neg = Column(Float, nullable=False)  # Negative sentiment score (0.0-1.0)
    neu = Column(Float, nullable=False)  # Neutral sentiment score (0.0-1.0)
    
    created_at = Column(DateTime, default=func.now())

    # Relationships
    article = relationship("NewsArticle", back_populates="sentiments")
    asset = relationship("Asset")

    # Indexes for performance
    __table_args__ = (
        Index('idx_news_sentiments_article', 'article_id'),
        Index('idx_news_sentiments_asset', 'asset_id'),
        Index('idx_news_sentiments_polarity', 'polarity'),
        Index('idx_news_sentiments_created_at', 'created_at'),
        Index('idx_news_sentiments_article_asset', 'article_id', 'asset_id'),
        Index('idx_news_sentiments_asset_created', 'asset_id', 'created_at'),
    )

    def __repr__(self):
        return f"<NewsSentiment(article_id={self.article_id}, asset_id={self.asset_id}, polarity={self.polarity:.3f})>"