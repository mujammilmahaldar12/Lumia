# app/models/quarterly_fundamental.py
from sqlalchemy import Column, Integer, Float, Date, BigInteger, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship
from database import Base


class QuarterlyFundamental(Base):
    __tablename__ = "quarterly_fundamentals"
    
    id = Column(Integer, primary_key=True, index=True)
    asset_id = Column(Integer, ForeignKey("assets.id"), nullable=False)
    report_date = Column(Date, nullable=False)
    earnings_per_share = Column(Float)
    price_to_earnings_ratio = Column(Float)
    total_revenue = Column(BigInteger)
    net_income = Column(BigInteger)
    total_debt = Column(BigInteger)
    return_on_equity = Column(Float)

    # Relationship to Asset
    asset = relationship("Asset", back_populates="quarterly_fundamentals")

    __table_args__ = (UniqueConstraint("asset_id", "report_date", name="uix_asset_report"),)
