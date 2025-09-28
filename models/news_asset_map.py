"""News Asset Mapping model for linking articles to assets."""

from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Index
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from database import Base


class NewsAssetMap(Base):
    """
    Model for mapping news articles to relevant assets using fuzzy matching.
    One article can be mapped to multiple assets with different confidence scores.
    """
    __tablename__ = "news_asset_map"

    id = Column(Integer, primary_key=True, index=True)
    article_id = Column(Integer, ForeignKey("news_articles.id"), nullable=False)
    asset_id = Column(Integer, ForeignKey("assets.id"), nullable=False)
    match_score = Column(Float, nullable=False)  # Fuzzy matching confidence (0.0-1.0)
    match_method = Column(String(50), default="fuzzy")  # How the match was made
    matched_text = Column(String(500))  # The text that caused the match
    created_at = Column(DateTime, default=func.now())

    # Relationships
    article = relationship("NewsArticle", back_populates="asset_mappings")
    asset = relationship("Asset")

    # Indexes for performance
    __table_args__ = (
        Index('idx_news_asset_map_article', 'article_id'),
        Index('idx_news_asset_map_asset', 'asset_id'),
        Index('idx_news_asset_map_score', 'match_score'),
        Index('idx_news_asset_map_article_asset', 'article_id', 'asset_id'),
    )

    def __repr__(self):
        return f"<NewsAssetMap(article_id={self.article_id}, asset_id={self.asset_id}, score={self.match_score:.3f})>"