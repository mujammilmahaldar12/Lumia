# app/models/daily_price.py
from sqlalchemy import Column, Integer, String, Float, Date, BigInteger, TIMESTAMP, ForeignKey, UniqueConstraint
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from database import Base

class DailyPrice(Base):
    __tablename__ = "daily_prices"
    
    id = Column(Integer, primary_key=True, index=True)
    asset_id = Column(Integer, ForeignKey("assets.id"), nullable=False)
    date = Column(Date, nullable=False)
    open_price = Column(Float)
    high_price = Column(Float)
    low_price = Column(Float)
    close_price = Column(Float)
    adj_close = Column(Float)
    volume = Column(BigInteger)
    dividends = Column(Float)
    stock_splits = Column(Float)
    created_at = Column(TIMESTAMP, server_default=func.now())

    # Relationship to Asset
    asset = relationship("Asset", back_populates="daily_prices")

    __table_args__ = (UniqueConstraint("asset_id", "date", name="uix_asset_date"),)
