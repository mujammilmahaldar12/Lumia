# app/models/crypto.py
from sqlalchemy import Column, Integer, String, Float, ForeignKey, Text, TIMESTAMP, BigInteger, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from database import Base

class Crypto(Base):
    """
    Cryptocurrency-specific metadata that extends the base Asset model
    """
    __tablename__ = "cryptos"

    id = Column(Integer, primary_key=True, index=True)
    asset_id = Column(Integer, ForeignKey("assets.id"), unique=True, nullable=False)

    # Supply metrics
    circulating_supply = Column(BigInteger)
    total_supply = Column(BigInteger)
    max_supply = Column(BigInteger)
    
    # Blockchain info
    algorithm = Column(String(100))  # SHA-256, Ethash, etc.
    consensus_mechanism = Column(String(50))  # Proof of Work, Proof of Stake
    blockchain = Column(String(100))  # Bitcoin, Ethereum, Binance Smart Chain
    
    # Token details
    token_type = Column(String(50))  # Coin, Token, DeFi, NFT, etc.
    contract_address = Column(String(100))  # For tokens
    decimals = Column(Integer, default=18)
    
    # Market metrics
    all_time_high = Column(Float)
    all_time_high_date = Column(TIMESTAMP)
    all_time_low = Column(Float)
    all_time_low_date = Column(TIMESTAMP)
    
    # Technical details
    block_time = Column(Float)  # Average block time in seconds
    hashing_algorithm = Column(String(100))
    
    # Project info
    launch_date = Column(TIMESTAMP)
    whitepaper_url = Column(String(500))
    source_code_url = Column(String(500))
    
    # Social and community
    reddit_subscribers = Column(Integer)
    twitter_followers = Column(Integer)
    telegram_members = Column(Integer)
    
    # Status
    is_minable = Column(Boolean, default=False)
    
    created_at = Column(TIMESTAMP, server_default=func.now())
    last_updated = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now())
    
    # Relationships
    asset = relationship("Asset", backref="crypto_details")
    
    def __repr__(self):
        return f"<Crypto(asset_id={self.asset_id}, algorithm='{self.algorithm}')>"
