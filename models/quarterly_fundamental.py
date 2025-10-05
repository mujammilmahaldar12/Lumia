# app/models/quarterly_fundamental.py
from sqlalchemy import Column, Integer, Float, Date, Numeric, ForeignKey, UniqueConstraint, TIMESTAMP
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from database import Base


class QuarterlyFundamental(Base):
    __tablename__ = "quarterly_fundamentals"
    
    id = Column(Integer, primary_key=True, index=True)
    asset_id = Column(Integer, ForeignKey("assets.id"), nullable=False)
    report_date = Column(Date, nullable=False)
    
    # Valuation metrics
    price_to_earnings_ratio = Column(Float)
    price_to_book_ratio = Column(Float)
    price_to_sales_ratio = Column(Float)
    peg_ratio = Column(Float)
    
    # Profitability metrics
    return_on_equity = Column(Float)
    return_on_assets = Column(Float)
    profit_margin = Column(Float)
    operating_margin = Column(Float)
    gross_margin = Column(Float)
    
    # Income statement (use Numeric for large values)
    total_revenue = Column(Numeric(20, 2))
    cost_of_revenue = Column(Numeric(20, 2))
    gross_profit = Column(Numeric(20, 2))
    operating_income = Column(Numeric(20, 2))
    net_income = Column(Numeric(20, 2))
    ebitda = Column(Numeric(20, 2))
    
    # Per share metrics
    earnings_per_share = Column(Float)
    book_value_per_share = Column(Float)
    revenue_per_share = Column(Float)
    
    # Balance sheet (use Numeric for large values)
    total_assets = Column(Numeric(20, 2))
    total_liabilities = Column(Numeric(20, 2))
    total_equity = Column(Numeric(20, 2))
    total_debt = Column(Numeric(20, 2))
    cash_and_equivalents = Column(Numeric(20, 2))
    
    # Debt metrics
    debt_to_equity_ratio = Column(Float)
    current_ratio = Column(Float)
    quick_ratio = Column(Float)
    
    # Cash flow (use Numeric for large values)
    operating_cash_flow = Column(Numeric(20, 2))
    free_cash_flow = Column(Numeric(20, 2))
    capital_expenditure = Column(Numeric(20, 2))
    
    # Growth metrics
    revenue_growth = Column(Float)
    earnings_growth = Column(Float)
    
    # Other metrics (use Numeric for large values)
    shares_outstanding = Column(Numeric(20, 2))
    market_cap = Column(Numeric(20, 2))
    enterprise_value = Column(Numeric(20, 2))
    
    # Timestamps
    created_at = Column(TIMESTAMP, server_default=func.now())
    last_updated = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now())

    # Relationship to Asset
    asset = relationship("Asset", back_populates="quarterly_fundamentals")

    __table_args__ = (UniqueConstraint("asset_id", "report_date", name="uix_asset_report"),)
