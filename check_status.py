#!/usr/bin/env python3
"""
Database Status and Collection Preview

This script shows current database status and estimates for 25-year collection.
"""

from database import SessionLocal
from models.daily_price import DailyPrice
from models.assets import Asset
from sqlalchemy import text

def main():
    """Show database status and collection estimates."""
    session = SessionLocal()
    
    try:
        print("=" * 60)
        print("📊 LUMIA DATABASE STATUS")
        print("=" * 60)
        
        # Current data
        total_prices = session.query(DailyPrice).count()
        total_assets = session.query(Asset).filter(Asset.is_active == True).count()
        
        print(f"💾 Current price records: {total_prices:,}")
        print(f"📈 Active assets: {total_assets:,}")
        
        # Asset breakdown
        stocks = session.query(Asset).filter(Asset.type == 'stock', Asset.is_active == True).count()
        cryptos = session.query(Asset).filter(Asset.type == 'crypto', Asset.is_active == True).count()
        etfs = session.query(Asset).filter(Asset.type == 'etf', Asset.is_active == True).count()
        
        print(f"\n📊 Asset Breakdown:")
        print(f"  • Stocks: {stocks:,}")
        print(f"  • Cryptocurrencies: {cryptos:,}")
        print(f"  • ETFs: {etfs:,}")
        
        # Recent symbols with data
        recent_query = text("""
            SELECT DISTINCT a.symbol, COUNT(dp.id) as price_count
            FROM daily_prices dp 
            JOIN assets a ON dp.asset_id = a.id 
            GROUP BY a.symbol 
            ORDER BY price_count DESC 
            LIMIT 10
        """)
        recent_results = session.execute(recent_query).fetchall()
        
        if recent_results:
            print(f"\n📈 Symbols with most data:")
            for symbol, count in recent_results:
                print(f"  • {symbol}: {count:,} records")
        
        # Date range of existing data
        date_range_query = text("""
            SELECT MIN(date) as earliest, MAX(date) as latest, COUNT(*) as total
            FROM daily_prices
        """)
        date_result = session.execute(date_range_query).fetchone()
        
        if date_result and date_result[0]:
            print(f"\n📅 Existing data range:")
            print(f"  • Earliest: {date_result[0]}")
            print(f"  • Latest: {date_result[1]}")
            print(f"  • Total records: {date_result[2]:,}")
        
        # Estimates for 25-year collection
        print(f"\n🎯 25-YEAR COLLECTION ESTIMATES:")
        print(f"  • Trading days per year: ~252")
        print(f"  • 25 years: ~6,300 trading days")
        print(f"  • Expected records per stock: ~6,300")
        print(f"  • Total estimated records: {stocks * 6300:,}")
        
        print(f"\n⚡ PROGRESSIVE COLLECTION BENEFITS:")
        print(f"  • Saves every 50 stocks (no data loss)")
        print(f"  • Can interrupt and resume anytime")
        print(f"  • Progress tracked in real-time")
        print(f"  • Robust error handling")
        
        print(f"\n🚀 READY FOR 25-YEAR COLLECTION!")
        print(f"   Run: python collect_25_years.py")
        
    finally:
        session.close()

if __name__ == "__main__":
    main()