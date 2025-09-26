# app/models/mutual_fund.py
from sqlalchemy import Column, Integer, String, Float, ForeignKey, Text, TIMESTAMP, BigInteger
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from database import Base

class MutualFund(Base):
    """
    Mutual Fund-specific metadata that extends the base Asset model
    """
    __tablename__ = "mutual_funds"

    id = Column(Integer, primary_key=True, index=True)
    asset_id = Column(Integer, ForeignKey("assets.id"), unique=True, nullable=False)

    # Fund basics
    nav = Column(Float)  # Net Asset Value
    expense_ratio = Column(Float)
    category = Column(String(100))  # Equity, Debt, Hybrid, Index, ELSS, etc.
    subcategory = Column(String(100))  # Large Cap, Mid Cap, Small Cap, etc.
    
    # Fund management
    fund_manager = Column(String(255))
    amc_name = Column(String(255))  # Asset Management Company
    
    # Fund details
    minimum_investment = Column(BigInteger)  # Minimum SIP/lumpsum amount
    minimum_sip = Column(Integer)
    exit_load = Column(Float)  # Exit load percentage
    
    # Performance and risk metrics
    aum = Column(BigInteger)  # Assets Under Management
    alpha = Column(Float)
    beta = Column(Float)
    sharpe_ratio = Column(Float)
    standard_deviation = Column(Float)
    
    # Returns (annualized)
    return_1yr = Column(Float)
    return_3yr = Column(Float)  
    return_5yr = Column(Float)
    return_since_inception = Column(Float)
    
    # Dates
    inception_date = Column(TIMESTAMP)
    
    # Investment strategy
    benchmark = Column(String(255))
    investment_objective = Column(Text)
    
    created_at = Column(TIMESTAMP, server_default=func.now())
    last_updated = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now())
    
    # Relationships
    asset = relationship("Asset", backref="mutual_fund_details")
    
    def __repr__(self):
        return f"<MutualFund(asset_id={self.asset_id}, nav={self.nav}, category='{self.category}')>"
