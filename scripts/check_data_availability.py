#!/usr/bin/env python3
"""
DATA AVAILABILITY CHECKER
Validates data availability for robo-advisor recommendations
"""

import sys
import os
from datetime import datetime, timedelta

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database import SessionLocal
from models.assets import Asset
from models.daily_price import DailyPrice
from models.quarterly_fundamental import QuarterlyFundamental
from models.news_article import NewsArticle
from sqlalchemy import func, and_

def check_data_availability():
    """Check data availability across all tables"""
    
    db = SessionLocal()
    
    print("\n" + "="*80)
    print("📊 LUMIA DATA AVAILABILITY REPORT")
    print("="*80)
    print(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
    
    # Assets
    print("📁 ASSETS:")
    total_assets = db.query(Asset).count()
    active_assets = db.query(Asset).filter(Asset.is_active == True).count()
    
    assets_by_type = db.query(
        Asset.type,
        func.count(Asset.id)
    ).filter(Asset.is_active == True).group_by(Asset.type).all()
    
    print(f"   Total Assets:  {total_assets:,}")
    print(f"   Active Assets: {active_assets:,}")
    print(f"   By Type:")
    for asset_type, count in assets_by_type:
        print(f"      • {asset_type:<15} {count:>6,}")
    
    # Daily Prices
    print(f"\n💵 DAILY PRICES:")
    total_prices = db.query(DailyPrice).count()
    assets_with_prices = db.query(func.count(func.distinct(DailyPrice.asset_id))).scalar()
    
    # Recent prices (last 30 days)
    thirty_days_ago = datetime.now() - timedelta(days=30)
    recent_prices = db.query(DailyPrice).filter(
        DailyPrice.date >= thirty_days_ago
    ).count()
    
    assets_with_recent_prices = db.query(
        func.count(func.distinct(DailyPrice.asset_id))
    ).filter(
        DailyPrice.date >= thirty_days_ago
    ).scalar()
    
    print(f"   Total Price Records:       {total_prices:,}")
    print(f"   Assets with Prices:        {assets_with_prices:,}")
    print(f"   Recent Prices (30d):       {recent_prices:,}")
    print(f"   Assets with Recent Prices: {assets_with_recent_prices:,}")
    
    # Price coverage by asset type
    print(f"   Coverage by Type:")
    for asset_type, total_count in assets_by_type:
        assets_with_price = db.query(
            func.count(func.distinct(DailyPrice.asset_id))
        ).join(Asset).filter(
            Asset.type == asset_type,
            Asset.is_active == True
        ).scalar()
        
        coverage = (assets_with_price / total_count * 100) if total_count > 0 else 0
        print(f"      • {asset_type:<15} {assets_with_price:>6,}/{total_count:<6,} ({coverage:>5.1f}%)")
    
    # Fundamentals
    print(f"\n📈 FUNDAMENTALS:")
    total_fundamentals = db.query(QuarterlyFundamental).count()
    assets_with_fundamentals = db.query(
        func.count(func.distinct(QuarterlyFundamental.asset_id))
    ).scalar()
    
    # Recent fundamentals (last 1 year)
    one_year_ago = datetime.now() - timedelta(days=365)
    recent_fundamentals = db.query(QuarterlyFundamental).filter(
        QuarterlyFundamental.report_date >= one_year_ago
    ).count()
    
    assets_with_recent_fundamentals = db.query(
        func.count(func.distinct(QuarterlyFundamental.asset_id))
    ).filter(
        QuarterlyFundamental.report_date >= one_year_ago
    ).scalar()
    
    print(f"   Total Fundamental Records:   {total_fundamentals:,}")
    print(f"   Assets with Fundamentals:    {assets_with_fundamentals:,}")
    print(f"   Recent Fundamentals (1y):    {recent_fundamentals:,}")
    print(f"   Assets with Recent Fund.:    {assets_with_recent_fundamentals:,}")
    
    # Fundamentals coverage by type
    print(f"   Coverage by Type:")
    for asset_type, total_count in assets_by_type:
        assets_with_fund = db.query(
            func.count(func.distinct(QuarterlyFundamental.asset_id))
        ).join(Asset).filter(
            Asset.type == asset_type,
            Asset.is_active == True
        ).scalar()
        
        coverage = (assets_with_fund / total_count * 100) if total_count > 0 else 0
        print(f"      • {asset_type:<15} {assets_with_fund:>6,}/{total_count:<6,} ({coverage:>5.1f}%)")
    
    # News & Sentiment
    print(f"\n📰 NEWS & SENTIMENT:")
    total_news = db.query(NewsArticle).count()
    assets_with_news = db.query(
        func.count(func.distinct(NewsArticle.asset_id))
    ).filter(NewsArticle.asset_id.isnot(None)).scalar()
    
    # Recent news (last 30 days)
    recent_news = db.query(NewsArticle).filter(
        NewsArticle.published_at >= thirty_days_ago
    ).count()
    
    assets_with_recent_news = db.query(
        func.count(func.distinct(NewsArticle.asset_id))
    ).filter(
        NewsArticle.published_at >= thirty_days_ago,
        NewsArticle.asset_id.isnot(None)
    ).scalar()
    
    # News with sentiment
    news_with_sentiment = db.query(NewsArticle).filter(
        NewsArticle.sentiment_score.isnot(None)
    ).count()
    
    print(f"   Total News Articles:       {total_news:,}")
    print(f"   Assets with News:          {assets_with_news:,}")
    print(f"   Recent News (30d):         {recent_news:,}")
    print(f"   Assets with Recent News:   {assets_with_recent_news:,}")
    print(f"   Articles with Sentiment:   {news_with_sentiment:,}")
    
    # Robo-Advisor Readiness
    print(f"\n🤖 ROBO-ADVISOR READINESS:")
    
    # Assets with complete data (prices + fundamentals + news in last 30 days)
    complete_assets = db.query(
        func.count(func.distinct(Asset.id))
    ).join(
        DailyPrice, Asset.id == DailyPrice.asset_id
    ).join(
        QuarterlyFundamental, Asset.id == QuarterlyFundamental.asset_id
    ).filter(
        Asset.is_active == True,
        DailyPrice.date >= thirty_days_ago
    ).scalar()
    
    print(f"   Assets with Complete Data: {complete_assets:,} (prices + fundamentals)")
    
    # By type
    print(f"   Complete Data by Type:")
    for asset_type, total_count in assets_by_type:
        complete_by_type = db.query(
            func.count(func.distinct(Asset.id))
        ).join(
            DailyPrice, Asset.id == DailyPrice.asset_id
        ).join(
            QuarterlyFundamental, Asset.id == QuarterlyFundamental.asset_id
        ).filter(
            Asset.is_active == True,
            Asset.type == asset_type,
            DailyPrice.date >= thirty_days_ago
        ).scalar()
        
        coverage = (complete_by_type / total_count * 100) if total_count > 0 else 0
        status = "✅" if coverage > 20 else "⚠️" if coverage > 5 else "❌"
        print(f"      {status} {asset_type:<15} {complete_by_type:>6,}/{total_count:<6,} ({coverage:>5.1f}%)")
    
    # Recommendations
    print(f"\n💡 RECOMMENDATIONS:")
    if complete_assets < 50:
        print("   ⚠️  LOW DATA AVAILABILITY")
        print("   Action: Run data collectors to populate database")
        print("   Command: python scripts/lumia_collector.py --run-all")
    elif complete_assets < 200:
        print("   ⚠️  MODERATE DATA AVAILABILITY")
        print("   Action: Consider running additional collectors")
        print("   Tip: Focus on high-quality assets with better coverage")
    else:
        print("   ✅ GOOD DATA AVAILABILITY")
        print("   Status: Ready for robo-advisor recommendations")
    
    print("\n" + "="*80 + "\n")
    
    db.close()

if __name__ == "__main__":
    try:
        check_data_availability()
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()
