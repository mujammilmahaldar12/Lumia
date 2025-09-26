# app/models/company.py - Legacy model, use Asset instead
from sqlalchemy import Column, Integer, String, BigInteger, Text, TIMESTAMP
from sqlalchemy.sql import func
from database import Base

# NOTE: This model is kept for backward compatibility
# New code should use the Asset model instead

class Company(Base):
    __tablename__ = "companies"
    
    id = Column(Integer, primary_key=True, index=True)
    symbol = Column(String(20), unique=True, nullable=False)
    company_name = Column(String(255), nullable=False)
    sector = Column(String(100))
    industry = Column(String(100))
    market_cap = Column(BigInteger)
    business_summary = Column(Text)
    last_updated = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now())
