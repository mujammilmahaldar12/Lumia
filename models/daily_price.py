# app/models/daily_price.py
from sqlalchemy import Column, Integer, String, Float, Date, BigInteger, TIMESTAMP, ForeignKey, UniqueConstraint
from sqlalchemy.sql import func
from database import Base

class DailyPrice(Base):
    __tablename__ = "daily_prices"
    
    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey("companies.id"), nullable=False)
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

    __table_args__ = (UniqueConstraint("company_id", "date", name="uix_company_date"),)
