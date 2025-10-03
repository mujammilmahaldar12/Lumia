#!/usr/bin/env python3
"""
25-Year Historical Data Collection Script

This script runs the complete 25-year historical price collection
using the progressive commit system to prevent data loss from interruptions.
"""

import logging
from datetime import date, timedelta
from collectors.daily_price_collector import DailyPriceCollector
from database import SessionLocal
from models.daily_price import DailyPrice

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('25_year_collection.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

def main():
    """Run the complete 25-year historical collection."""
    print("=" * 60)
    print("🚀 STARTING 25-YEAR HISTORICAL DATA COLLECTION")
    print("=" * 60)
    
    # Calculate date range (25 years)
    end_date = date.today()
    start_date = end_date - timedelta(days=25 * 365)
    
    print(f"📅 Date Range: {start_date} to {end_date}")
    print(f"⏱️  Duration: 25 years")
    
    # Check current database state
    session = SessionLocal()
    try:
        initial_count = session.query(DailyPrice).count()
        print(f"💾 Initial database records: {initial_count:,}")
    finally:
        session.close()
    
    print("\n🔥 Features enabled:")
    print("  ✅ Progressive commits (saves every 50 stocks)")
    print("  ✅ Interruption-safe (Ctrl+C won't lose progress)")
    print("  ✅ Unicode-safe logging")
    print("  ✅ Robust error handling")
    print("  ✅ Automatic retry for failed stocks")
    
    print(f"\n⚠️  IMPORTANT: This will collect 25 years of data!")
    print(f"   This may take several hours to complete.")
    print(f"   You can interrupt with Ctrl+C and resume later.")
    
    response = input("\n❓ Continue with 25-year collection? (yes/no): ")
    if response.lower() not in ['yes', 'y']:
        print("❌ Collection cancelled.")
        return
    
    # Start collection
    print("\n🚀 Starting collection...")
    collector = DailyPriceCollector()
    
    try:
        results = collector.sync_prices_with_date_range(
            from_date=start_date.strftime('%Y-%m-%d'),
            to_date=end_date.strftime('%Y-%m-%d')
        )
        
        print("\n" + "=" * 60)
        print("🎉 COLLECTION COMPLETED SUCCESSFULLY!")
        print("=" * 60)
        
        print(f"📊 Results:")
        print(f"  • Total processed: {results['total_processed']:,}")
        print(f"  • Records added: {results['total_added']:,}")
        print(f"  • Failed assets: {results['total_failed']:,}")
        
        if 'by_type' in results:
            for asset_type, type_results in results['by_type'].items():
                print(f"  • {asset_type.title()}: {type_results.get('success', 0)} successful")
        
        # Final count
        session = SessionLocal()
        try:
            final_count = session.query(DailyPrice).count()
            added_records = final_count - initial_count
            print(f"\n💾 Final database records: {final_count:,}")
            print(f"📈 Records added this run: {added_records:,}")
        finally:
            session.close()
            
    except KeyboardInterrupt:
        print("\n\n⚠️  COLLECTION INTERRUPTED!")
        print("🔄 Don't worry - progress has been saved progressively.")
        print("💡 You can resume by running this script again.")
        
        # Show progress so far
        session = SessionLocal()
        try:
            current_count = session.query(DailyPrice).count()
            added_so_far = current_count - initial_count
            print(f"💾 Records saved so far: {added_so_far:,}")
        finally:
            session.close()
            
    except Exception as e:
        logger.error(f"❌ Collection failed: {str(e)}")
        print(f"\n❌ Collection failed: {str(e)}")
        print("💡 Check the log file: 25_year_collection.log")
        
    print("\n📋 Next steps:")
    print("  1. Check the log file for detailed results")
    print("  2. Run analytics on the collected data")
    print("  3. Set up automated daily updates")

if __name__ == "__main__":
    main()