#!/usr/bin/env python3
"""
LUMIA DATA COLLECTOR - SINGLE ENTRY POINT

The ONLY script you need to run for all Lumia data collection!

FEATURES:
- AI decides what to collect automatically
- 25 years of historical data minimum  
- Smart date ranges for fast updates
- First-time setup vs daily maintenance
- Tracks everything intelligently

USAGE:
    python lumia_collector.py              # Smart auto mode (recommended)
    python lumia_collector.py --first-time # Force complete setup
    python lumia_collector.py --analysis   # Show what it would do
    python lumia_collector.py --status     # Database status

Author: Lumia Team
"""

import sys
import os
import argparse
import logging
from datetime import datetime

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import components
from components.intelligence import IntelligenceEngine, CollectionMode
from components.execution import ExecutionEngine
from database import SessionLocal
from utils.logging_config import setup_unicode_logging, configure_root_logging

# Configure Unicode-safe logging
configure_root_logging()
logger = setup_unicode_logging(
    'lumia.main',
    level='INFO',
    log_file=f'lumia_collection_{datetime.now().strftime("%Y%m%d")}.log',
    console=True
)

def print_banner():
    """Print banner"""
    print("\n" + "="*80)
    print("LUMIA DATA COLLECTOR - AI POWERED")
    print("="*80)
    print("Smart Analysis • 25 Years History • Optimized")
    print(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*80 + "\n")

def show_status(intelligence_engine, session):
    """Show database status"""
    report = intelligence_engine.analyze_database(session)
    
    print("\n📊 DATABASE STATUS REPORT")
    print("-" * 50)
    print(f"Database State: {report.database_state.value.upper()}")
    print(f"Total Assets: {report.total_assets:,}")
    print(f"Total Prices: {report.total_prices:,}")
    print(f"Recommended Mode: {report.collection_mode.value}")
    print(f"Reasoning: {report.priority_reasoning}")
    print(f"Collectors to Run: {', '.join(report.collectors_to_run)}")
    print(f"Estimated Time: {report.estimated_time_minutes} minutes")
    
    if report.asset_breakdown:
        print("\n📈 Asset Breakdown:")
        for asset_type, count in report.asset_breakdown.items():
            print(f"  {asset_type.title()}: {count:,}")
    
    if report.price_coverage:
        print(f"\n💰 Price Coverage:")
        coverage = report.price_coverage
        if 'latest_date' in coverage:
            print(f"  Latest Price Date: {coverage['latest_date']}")
            print(f"  Days Since Update: {coverage.get('days_since_update', 'N/A')}")
            print(f"  Coverage: {coverage.get('coverage_percentage', 0)*100:.1f}%")

def show_analysis(intelligence_engine, session):
    """Show analysis without executing"""
    report = intelligence_engine.analyze_database(session)
    
    print("\n🧠 INTELLIGENCE ANALYSIS REPORT")
    print("=" * 60)
    print(f"Database State: {report.database_state.value}")
    print(f"Recommended Mode: {report.collection_mode.value}")
    print(f"Reasoning: {report.priority_reasoning}")
    print(f"Collectors to Run: {', '.join(report.collectors_to_run)}")
    print(f"Estimated Time: {report.estimated_time_minutes} minutes")
    
    if report.optimal_date_range:
        date_range = report.optimal_date_range
        print(f"Date Range: {date_range['from_date']} to {date_range['to_date']}")
        print(f"Date Reasoning: {date_range.get('reasoning', 'N/A')}")
    
    print(f"Expected New Assets: ~{report.expected_new_assets:,}")
    print(f"Expected New Prices: ~{report.expected_new_prices:,}")
    print("\n💡 Run without --analysis to execute this plan")

def execute_collection(intelligence_engine, execution_engine, session, force_mode=None):
    """Execute the collection"""
    
    # Get intelligence report
    logger.info("[ANALYZING] Analyzing database state...")
    report = intelligence_engine.analyze_database(session)
    
    # Execute collection
    logger.info("[EXECUTING] Starting data collection...")
    results = execution_engine.execute_collection_plan(report, force_mode=force_mode)
    
    # Show results
    print("\n" + "="*80)
    print("🎉 COLLECTION COMPLETED!")
    print("="*80)
    print(f"⏱️  Duration: {results['total_duration']:.1f} seconds")
    print(f"✅ Success: {results['success_count']} collectors")
    print(f"❌ Failed: {results['failure_count']} collectors")
    print(f"📈 New Assets: {results['total_new_assets']:,}")
    print(f"💰 New Prices: {results['total_new_prices']:,}")
    
    if results['collectors_executed']:
        print(f"\nDetailed Results:")
        for collector, result in results['collectors_executed'].items():
            status_icon = "✅" if result['status'] == 'success' else "❌"
            duration = result.get('duration_seconds', 0)
            records = result.get('records_processed', 0)
            print(f"  {status_icon} {collector}: {records} records in {duration:.1f}s")
    
    return results['failure_count'] == 0

def main():
    """Main entry point"""
    
    parser = argparse.ArgumentParser(
        description='Lumia Data Collector - Single Entry Point',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
EXAMPLES:
    python lumia_collector.py                  # Smart auto mode (recommended)
    python lumia_collector.py --first-time    # Force complete setup (25 years)
    python lumia_collector.py --daily-only    # Only update daily prices
    python lumia_collector.py --news-only     # Only collect news (stocks + crypto)
    python lumia_collector.py --analysis      # Show analysis without collecting
    python lumia_collector.py --status        # Show database status
    python lumia_collector.py --quiet         # Minimal output
        """
    )
    
    parser.add_argument('--first-time', action='store_true',
                       help='Force first-time setup (collect 25 years of data)')
    parser.add_argument('--daily-only', action='store_true', 
                       help='Only collect daily price updates')
    parser.add_argument('--news-only', action='store_true',
                       help='Only collect news articles (stocks + crypto)')
    parser.add_argument('--analysis', action='store_true',
                       help='Show intelligence analysis without collecting')
    parser.add_argument('--status', action='store_true',
                       help='Show current database status')
    parser.add_argument('--quiet', action='store_true',
                       help='Minimize output (errors only)')
    parser.add_argument('--json', action='store_true',
                       help='Output results in JSON format')
    
    args = parser.parse_args()
    
    # Set logging level
    if args.quiet:
        logging.getLogger().setLevel(logging.ERROR)
    
    # Show banner unless quiet
    if not args.quiet and not args.json:
        print_banner()
    
    try:
        # Initialize components
        session = SessionLocal()
        intelligence_engine = IntelligenceEngine()
        execution_engine = ExecutionEngine(session)
        
        if args.status:
            show_status(intelligence_engine, session)
            return
        
        if args.analysis:
            show_analysis(intelligence_engine, session)
            return
        
        # Determine force mode
        force_mode = None
        if args.first_time:
            force_mode = CollectionMode.FIRST_TIME_SETUP
            logger.info("[OVERRIDE] Forcing first-time setup (25 years of data)")
        elif args.daily_only:
            force_mode = CollectionMode.PRICE_ONLY
            logger.info("[OVERRIDE] Forcing daily-only mode")
        elif args.news_only:
            # Custom handling for news-only mode
            from collectors.collect_news import collect_stock_news, collect_crypto_news
            
            logger.info("[NEWS] Collecting news for ALL stocks and cryptocurrencies...")
            print("\n📰 NEWS COLLECTION MODE")
            print("="*80)
            
            # Collect stock news
            print("\n🔍 Collecting stock news (ALL stocks)...")
            stock_results = collect_stock_news(limit=None, articles_per_stock=5)
            print(f"✅ Stock News: {stock_results['total_articles_saved']} new articles")
            
            # Collect crypto news
            print("\n🔍 Collecting crypto news (ALL cryptocurrencies)...")
            crypto_results = collect_crypto_news(limit=None, articles_per_crypto=5)
            print(f"✅ Crypto News: {crypto_results['total_articles_saved']} new articles")
            
            print("\n" + "="*80)
            print(f"🎉 TOTAL: {stock_results['total_articles_saved'] + crypto_results['total_articles_saved']} new articles collected!")
            print("="*80 + "\n")
            
            return
        
        # Execute collection
        success = execute_collection(intelligence_engine, execution_engine, session, force_mode)
        
        if success:
            logger.info("All collectors completed successfully!")
            sys.exit(0)
        else:
            logger.warning("Some collectors failed")
            sys.exit(1)
            
    except KeyboardInterrupt:
        logger.info("Collection interrupted by user")
        sys.exit(130)
    except Exception as e:
        logger.error(f"Critical error: {str(e)}")
        if not args.quiet:
            import traceback
            traceback.print_exc()
        sys.exit(1)
    finally:
        if 'session' in locals():
            session.close()

if __name__ == '__main__':
    main()