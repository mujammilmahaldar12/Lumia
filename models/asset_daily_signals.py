"""Asset Daily Signals model for aggregated daily metrics."""

from sqlalchemy import Column, Integer, Float, Date, DateTime, ForeignKey, Index
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from database import Base


class AssetDailySignals(Base):
    """
    Model for storing aggregated daily signals for each asset.
    Combines sentiment, price, and fundamental data into daily metrics.
    """
    __tablename__ = "asset_daily_signals"

    id = Column(Integer, primary_key=True, index=True)
    asset_id = Column(Integer, ForeignKey("assets.id"), nullable=False)
    date = Column(Date, nullable=False)
    
    # Sentiment signals
    avg_sentiment = Column(Float)  # Daily average sentiment
    article_count = Column(Integer, default=0)  # Number of articles for this day
    sentiment_7d_avg = Column(Float)  # 7-day rolling average sentiment
    sentiment_30d_avg = Column(Float)  # 30-day rolling average sentiment
    
    # Price signals
    volatility_30d = Column(Float)  # 30-day price volatility
    return_30d = Column(Float)  # 30-day return
    return_365d = Column(Float)  # 365-day return
    
    # Fundamental signals (placeholders for future expansion)
    fundamental_score = Column(Float)  # Composite fundamental score
    
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())

    # Relationships
    asset = relationship("Asset")

    # Indexes for performance
    __table_args__ = (
        Index('idx_asset_daily_signals_asset_date', 'asset_id', 'date', unique=True),
        Index('idx_asset_daily_signals_date', 'date'),
        Index('idx_asset_daily_signals_asset', 'asset_id'),
        Index('idx_asset_daily_signals_avg_sentiment', 'avg_sentiment'),
    )

    def __repr__(self):
        return f"<AssetDailySignals(asset_id={self.asset_id}, date={self.date}, avg_sentiment={self.avg_sentiment})>"