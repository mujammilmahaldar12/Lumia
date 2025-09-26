# app/models/etf.py
from sqlalchemy import Column, Integer, String, Float, ForeignKey, Text, TIMESTAMP
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from database import Base

class ETF(Base):
    """
    ETF-specific metadata that extends the base Asset model
    """
    __tablename__ = "etfs"

    id = Column(Integer, primary_key=True, index=True)
    asset_id = Column(Integer, ForeignKey("assets.id"), unique=True, nullable=False)

    # ETF-specific fields
    nav = Column(Float)  # Net Asset Value
    expense_ratio = Column(Float)  # Annual expense ratio
    underlying_index = Column(String(255))  # e.g. S&P 500, NIFTY 50
    index_provider = Column(String(100))  # e.g. S&P, MSCI, NSE
    
    # Holdings and composition
    top_10_holdings_weight = Column(Float)  # Percentage
    number_of_holdings = Column(Integer)
    
    # Performance metrics
    tracking_error = Column(Float)
    avg_daily_volume = Column(Integer)
    
    # Dates
    inception_date = Column(TIMESTAMP)
    
    # Metadata
    fund_manager = Column(String(255))
    benchmark = Column(String(255))
    investment_objective = Column(Text)
    
    created_at = Column(TIMESTAMP, server_default=func.now())
    last_updated = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now())
    
    # Relationships
    asset = relationship("Asset", backref="etf_details")
    
    def __repr__(self):
        return f"<ETF(asset_id={self.asset_id}, nav={self.nav})>"
