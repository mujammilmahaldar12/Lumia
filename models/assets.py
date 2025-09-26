# app/models/assets.py
from sqlalchemy import Column, Integer, String, BigInteger, Text, TIMESTAMP, Boolean, Float
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from database import Base

class Asset(Base):
    """
    Universal Asset model for all tradeable instruments:
    - Stocks (US, Indian, International)
    - ETFs (Exchange Traded Funds)
    - Mutual Funds
    - Cryptocurrencies
    - Bonds, Indices, etc.
    """
    __tablename__ = "assets"

    id = Column(Integer, primary_key=True, index=True)
    symbol = Column(String(50), unique=True, nullable=False)  # Ticker, ISIN, or coin id
    name = Column(String(500), nullable=False)  # Full name
    
    # Asset classification
    type = Column(String(50), nullable=False)  # stock, etf, mutual_fund, crypto, index, bond, commodity
    subtype = Column(String(100))  # equity, debt, hybrid, large_cap, mid_cap, etc.
    
    # Exchange and location info
    exchange = Column(String(100))  # NASDAQ, NSE, BSE, Binance, etc.
    country = Column(String(50))  # US, IN, etc.
    currency = Column(String(10), default="USD")
    
    # Business classification (mainly for stocks)
    sector = Column(String(100))    
    industry = Column(String(100))  
    
    # Financial metrics
    market_cap = Column(BigInteger)
    total_assets = Column(BigInteger)  # For funds
    expense_ratio = Column(Float)  # For ETFs/Mutual Funds
    dividend_yield = Column(Float)
    
    # Status and metadata
    is_active = Column(Boolean, default=True)
    listing_date = Column(TIMESTAMP)
    delisting_date = Column(TIMESTAMP)
    
    # Additional info
    description = Column(Text)
    website = Column(String(500))
    isin = Column(String(20))  # International Securities Identification Number
    cusip = Column(String(20))  # For US securities
    
    # Tracking
    created_at = Column(TIMESTAMP, server_default=func.now())
    last_updated = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now())
    
    # Relationships
    daily_prices = relationship("DailyPrice", back_populates="asset", cascade="all, delete-orphan")
    quarterly_fundamentals = relationship("QuarterlyFundamental", back_populates="asset", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Asset(symbol='{self.symbol}', name='{self.name}', type='{self.type}')>"
    
    @property
    def display_name(self):
        """Human-readable display name"""
        return f"{self.name} ({self.symbol})"
    
    def is_stock(self):
        return self.type == 'stock'
    
    def is_etf(self):
        return self.type == 'etf'
    
    def is_mutual_fund(self):
        return self.type == 'mutual_fund'
    
    def is_crypto(self):
        return self.type == 'crypto'
