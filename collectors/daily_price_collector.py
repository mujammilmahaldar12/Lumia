#!/usr/bin/env python3
"""
Daily Price Data Collector
Collects OHLCV data for all companies in the database
"""
import yfinance as yf
import pandas as pd
import time
import logging
from datetime import datetime, timedelta, date
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import IntegrityError
from sqlalchemy import and_
import sys
import os

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database import engine
from models.company import Company
from models.daily_price import DailyPrice

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class DailyPriceCollector:
    def __init__(self):
        """Initialize the daily price collector"""
        self.Session = sessionmaker(bind=engine)
    
    def get_companies_for_collection(self, limit=None, exchange=None):
        """
        Get companies from database for price collection
        
        Args:
            limit: Limit number of companies (for testing)
            exchange: 'US', 'IN' or None for all
        """
        session = self.Session()
        try:
            query = session.query(Company)
            
            if exchange == 'US':
                query = query.filter(~Company.symbol.like('%.NS'))
            elif exchange == 'IN':
                query = query.filter(Company.symbol.like('%.NS'))
            
            if limit:
                query = query.limit(limit)
            
            companies = query.all()
            logger.info(f"Found {len(companies)} companies for price collection")
            return companies
        finally:
            session.close()
    
    def get_latest_price_date(self, company_id):
        """Get the latest date we have price data for a company"""
        session = self.Session()
        try:
            latest = session.query(DailyPrice.date).filter_by(company_id=company_id).order_by(DailyPrice.date.desc()).first()
            return latest[0] if latest else None
        finally:
            session.close()
    
    def fetch_price_data(self, symbol, start_date=None, end_date=None, max_historical=True):
        """
        Fetch price data using yfinance with maximum historical coverage
        
        Args:
            symbol: Stock symbol (e.g., 'AAPL', 'TCS.NS')
            start_date: Start date for data collection
            end_date: End date for data collection
            max_historical: If True, tries to get maximum available history
        """
        try:
            logger.info(f"Fetching historical price data for {symbol}")
            
            # Set default date range
            if not end_date:
                end_date = datetime.now().date()
            if not start_date:
                if max_historical:
                    # Start from 2000 or 25 years ago, whichever is earlier
                    start_from_2000 = datetime(2000, 1, 1).date()
                    start_from_25y = end_date - timedelta(days=25*365)  # 25 years
                    start_date = min(start_from_2000, start_from_25y)
                else:
                    start_date = end_date - timedelta(days=365)  # Default: 1 year
            
            logger.info(f"Requesting data from {start_date} to {end_date} for {symbol}")
            
            # Create ticker
            ticker = yf.Ticker(symbol)
            
            # Try to get maximum historical data first
            try:
                if max_historical:
                    # Use "max" period to get all available data
                    hist = ticker.history(period="max")
                    logger.info(f"Retrieved maximum available history for {symbol}")
                else:
                    # Use specific date range
                    hist = ticker.history(start=start_date, end=end_date + timedelta(days=1))
            except Exception as e:
                logger.warning(f"Max history failed for {symbol}, trying date range: {e}")
                # Fallback to date range
                hist = ticker.history(start=start_date, end=end_date + timedelta(days=1))
            
            if hist.empty:
                logger.warning(f"No price data found for {symbol}")
                return []
            
            # Filter by date range if we got max history
            if max_historical and start_date:
                hist = hist[hist.index.date >= start_date]
            
            # Convert to list of records
            price_records = []
            for date_index, row in hist.iterrows():
                # Extract date from pandas timestamp
                trade_date = date_index.date()
                
                # Skip weekends and ensure we're in our date range
                if start_date and trade_date < start_date:
                    continue
                if end_date and trade_date > end_date:
                    continue
                
                price_record = {
                    'date': trade_date,
                    'open_price': float(row['Open']) if pd.notna(row['Open']) and row['Open'] > 0 else None,
                    'high_price': float(row['High']) if pd.notna(row['High']) and row['High'] > 0 else None,
                    'low_price': float(row['Low']) if pd.notna(row['Low']) and row['Low'] > 0 else None,
                    'close_price': float(row['Close']) if pd.notna(row['Close']) and row['Close'] > 0 else None,
                    'adj_close': float(row['Close']) if pd.notna(row['Close']) and row['Close'] > 0 else None,
                    'volume': int(row['Volume']) if pd.notna(row['Volume']) and row['Volume'] >= 0 else 0,
                    'dividends': float(row.get('Dividends', 0)) if pd.notna(row.get('Dividends', 0)) else 0.0,
                    'stock_splits': float(row.get('Stock Splits', 0)) if pd.notna(row.get('Stock Splits', 0)) else 0.0
                }
                price_records.append(price_record)
            
            # Show the actual date range we got
            if price_records:
                actual_start = min(r['date'] for r in price_records)
                actual_end = max(r['date'] for r in price_records)
                years_of_data = (actual_end - actual_start).days / 365.25
                logger.info(f"Fetched {len(price_records)} records for {symbol} from {actual_start} to {actual_end} ({years_of_data:.1f} years)")
            else:
                logger.warning(f"No valid price records found for {symbol}")
            
            return price_records
            
        except Exception as e:
            logger.error(f"Error fetching price data for {symbol}: {e}")
            return []
    
    def save_price_data(self, company_id, price_records):
        """Save price data to database"""
        session = self.Session()
        saved_count = 0
        skipped_count = 0
        
        try:
            for record in price_records:
                # Check if this date already exists for this company
                existing = session.query(DailyPrice).filter(
                    and_(
                        DailyPrice.company_id == company_id,
                        DailyPrice.date == record['date']
                    )
                ).first()
                
                if existing:
                    # Update existing record
                    for key, value in record.items():
                        if key != 'date':  # Don't update the date
                            setattr(existing, key, value)
                    skipped_count += 1
                else:
                    # Create new record
                    price_entry = DailyPrice(company_id=company_id, **record)
                    session.add(price_entry)
                    saved_count += 1
            
            session.commit()
            logger.info(f"Saved {saved_count} new records, updated {skipped_count} existing records")
            return True
            
        except Exception as e:
            session.rollback()
            logger.error(f"Error saving price data for company {company_id}: {e}")
            return False
        finally:
            session.close()
    
    def collect_company_prices(self, company, period_days=365, delay=1, force_max_history=False):
        """
        Collect price data for a single company
        
        Args:
            company: Company object from database
            period_days: Number of days to collect (default: 1 year)
            delay: Delay after processing (rate limiting)
            force_max_history: Force maximum historical collection even if data exists
        """
        try:
            # Determine date range
            end_date = datetime.now().date()
            
            # Check if we have existing data
            latest_date = self.get_latest_price_date(company.id)
            
            if latest_date and not force_max_history:
                # Continue from where we left off
                start_date = latest_date + timedelta(days=1)
                if start_date > end_date:
                    logger.info(f"Price data for {company.symbol} is already up to date")
                    return True
                use_max_history = False
            else:
                # Start from specified period or use maximum history
                if force_max_history or period_days > 7000:  # More than ~20 years
                    logger.info(f"Using maximum historical collection for {company.symbol}")
                    start_date = datetime(2000, 1, 1).date()  # Start from 2000
                    use_max_history = True
                else:
                    start_date = end_date - timedelta(days=period_days)
                    use_max_history = (latest_date is None)
            
            logger.info(f"Collecting prices for {company.symbol} from {start_date} to {end_date}")
            
            # Fetch price data
            price_records = self.fetch_price_data(company.symbol, start_date, end_date, max_historical=use_max_history)
            
            if not price_records:
                logger.warning(f"No price data available for {company.symbol}")
                return False
            
            # Save to database
            success = self.save_price_data(company.id, price_records)
            
            # Show summary for this company
            if success and price_records:
                years_collected = len(price_records) / 252  # ~252 trading days per year
                logger.info(f"💾 Saved {len(price_records)} records for {company.symbol} (~{years_collected:.1f} years of data)")
            
            # Rate limiting
            if delay > 0:
                time.sleep(delay)
            
            return success
            
        except Exception as e:
            logger.error(f"Error collecting prices for {company.symbol}: {e}")
            return False
    
    def collect_maximum_history(self, limit=None, exchange=None, delay=0.3):
        """
        Special method for collecting maximum available historical data
        This will attempt to get ALL available data for each company
        """
        companies = self.get_companies_for_collection(limit, exchange)
        
        if not companies:
            logger.error("No companies found for price collection")
            return
        
        total_companies = len(companies)
        successful = 0
        failed = 0
        total_records = 0
        
        exchange_name = "ALL" if not exchange else exchange
        logger.info(f"💥 Starting MAXIMUM HISTORY collection for {total_companies} {exchange_name} companies")
        logger.info(f"🎯 Target: Collect ALL available historical data (potentially back to 1970s)")
        
        start_time = datetime.now()
        
        for i, company in enumerate(companies, 1):
            logger.info(f"📊 Processing {i}/{total_companies}: {company.symbol} - {company.company_name}")
            
            try:
                # Force maximum history collection
                if self.collect_company_prices(company, period_days=15000, delay=delay, force_max_history=True):
                    successful += 1
                    
                    # Get count of records for this company
                    session = self.Session()
                    try:
                        company_records = session.query(DailyPrice).filter_by(company_id=company.id).count()
                        total_records += company_records
                        logger.info(f"✅ Success for {company.symbol} - Total records: {company_records}")
                    finally:
                        session.close()
                else:
                    failed += 1
                    logger.warning(f"❌ Failed for {company.symbol}")
            
            except KeyboardInterrupt:
                logger.info(f"\n⏸️ Maximum history collection paused by user at {i}/{total_companies}")
                break
            except Exception as e:
                failed += 1
                logger.error(f"❌ Error for {company.symbol}: {e}")
            
            # Progress update every 10 companies
            if i % 10 == 0:
                elapsed = datetime.now() - start_time
                avg_time = elapsed.total_seconds() / i
                remaining_time = avg_time * (total_companies - i)
                logger.info(f"⏱️  Progress: {i}/{total_companies} | Elapsed: {elapsed} | ETA: {timedelta(seconds=remaining_time)}")
        
        # Final summary
        processed = successful + failed
        elapsed_time = datetime.now() - start_time
        
        logger.info(f"\n🎉 MAXIMUM HISTORY COLLECTION SUMMARY")
        logger.info(f"=" * 60)
        logger.info(f"Companies processed: {processed}/{total_companies}")
        logger.info(f"Successful: {successful}")
        logger.info(f"Failed: {failed}")
        logger.info(f"Total price records collected: {total_records:,}")
        logger.info(f"Total time elapsed: {elapsed_time}")
        logger.info(f"Average time per company: {elapsed_time.total_seconds()/processed:.1f}s" if processed > 0 else "N/A")
        logger.info(f"Success rate: {(successful/processed)*100:.1f}%" if processed > 0 else "N/A")
    
    def collect_all_prices(self, limit=None, exchange=None, period_days=365, delay=0.5):
        """
        Collect price data for all companies
        
        Args:
            limit: Limit number of companies (for testing)
            exchange: 'US', 'IN' or None for all
            period_days: Number of days of history to collect
            delay: Delay between companies (rate limiting)
        """
        companies = self.get_companies_for_collection(limit, exchange)
        
        if not companies:
            logger.error("No companies found for price collection")
            return
        
        total_companies = len(companies)
        successful = 0
        failed = 0
        
        exchange_name = "ALL" if not exchange else exchange
        logger.info(f"🚀 Starting price collection for {total_companies} {exchange_name} companies")
        logger.info(f"📅 Collecting {period_days} days of historical data")
        
        for i, company in enumerate(companies, 1):
            logger.info(f"📊 Processing {i}/{total_companies}: {company.symbol} - {company.company_name}")
            
            try:
                if self.collect_company_prices(company, period_days, delay):
                    successful += 1
                    logger.info(f"✅ Success for {company.symbol}")
                else:
                    failed += 1
                    logger.warning(f"❌ Failed for {company.symbol}")
            
            except KeyboardInterrupt:
                logger.info(f"\n⏸️ Collection paused by user at {i}/{total_companies}")
                break
            except Exception as e:
                failed += 1
                logger.error(f"❌ Error for {company.symbol}: {e}")
        
        # Summary
        processed = successful + failed
        logger.info(f"\n🎉 PRICE COLLECTION SUMMARY")
        logger.info(f"=" * 50)
        logger.info(f"Companies processed: {processed}/{total_companies}")
        logger.info(f"Successful: {successful}")
        logger.info(f"Failed: {failed}")
        logger.info(f"Success rate: {(successful/processed)*100:.1f}%" if processed > 0 else "N/A")
    
    def get_price_statistics(self):
        """Get statistics about collected price data"""
        session = self.Session()
        try:
            # Total price records
            total_prices = session.query(DailyPrice).count()
            
            # Companies with price data
            companies_with_prices = session.query(DailyPrice.company_id).distinct().count()
            
            # Total companies
            total_companies = session.query(Company).count()
            
            # Latest and earliest dates
            latest_date = session.query(DailyPrice.date).order_by(DailyPrice.date.desc()).first()
            earliest_date = session.query(DailyPrice.date).order_by(DailyPrice.date.asc()).first()
            
            logger.info(f"\n📊 PRICE DATA STATISTICS")
            logger.info(f"=" * 40)
            logger.info(f"Total price records: {total_prices:,}")
            logger.info(f"Companies with price data: {companies_with_prices}/{total_companies}")
            logger.info(f"Coverage: {(companies_with_prices/total_companies)*100:.1f}%" if total_companies > 0 else "N/A")
            
            if latest_date and earliest_date:
                logger.info(f"Date range: {earliest_date[0]} to {latest_date[0]}")
            
            return {
                'total_prices': total_prices,
                'companies_with_prices': companies_with_prices,
                'total_companies': total_companies,
                'latest_date': latest_date[0] if latest_date else None,
                'earliest_date': earliest_date[0] if earliest_date else None
            }
            
        finally:
            session.close()

def interactive_menu():
    """Interactive menu for price collection"""
    collector = DailyPriceCollector()
    
    while True:
        print("\n" + "=" * 60)
        print("📊 DAILY PRICE DATA COLLECTOR")
        print("=" * 60)
        print("1️⃣  Collect US Companies (25+ years maximum history)")
        print("2️⃣  Collect Indian Companies (25+ years maximum history)")
        print("3️⃣  Collect ALL Companies (25+ years maximum history)")
        print("4️⃣  Quick Test (10 companies, 30 days)")
        print("5️⃣  Update Recent Prices Only (last 30 days)")
        print("6️⃣  Custom Period Collection (specify years)")
        print("7️⃣  Massive Historical Collection (ALL companies, MAX history)")
        print("8️⃣  Show Price Data Statistics")
        print("0️⃣  Exit")
        
        choice = input("\n🤔 Select an option (0-8): ").strip()
        
        if choice == '1':
            print("\n🇺🇸 Collecting US company prices (25+ years maximum history)...")
            print("📊 This will collect maximum available historical data for each US company")
            confirm = input("🤔 Continue? This may take 1-2 hours (y/N): ").strip().lower()
            if confirm == 'y':
                collector.collect_all_prices(exchange='US', period_days=9125, delay=0.5)  # 25 years
            
        elif choice == '2':
            print("\n�🇳 Collecting Indian company prices (25+ years maximum history)...")
            print("📊 This will collect maximum available historical data for each Indian company")
            confirm = input("🤔 Continue? This may take 2-3 hours (y/N): ").strip().lower()
            if confirm == 'y':
                collector.collect_all_prices(exchange='IN', period_days=9125, delay=0.5)  # 25 years
            
        elif choice == '3':
            print("\n🌍 Collecting ALL company prices (25+ years maximum history)...")
            print("⚠️  MASSIVE OPERATION: This will collect 25+ years for ALL 2000+ companies!")
            print("📊 Expected time: 6-12 hours")
            print("💾 Expected data: 500K+ price records")
            confirm = input("🤔 Are you absolutely sure? (y/N): ").strip().lower()
            if confirm == 'y':
                collector.collect_all_prices(period_days=9125, delay=0.3)  # 25 years
            
        elif choice == '4':
            print("\n🧪 Quick test with 10 companies (30 days)...")
            collector.collect_all_prices(limit=10, period_days=30, delay=1)
            
        elif choice == '5':
            print("\n🔄 Updating recent prices only (last 30 days)...")
            collector.collect_all_prices(period_days=30, delay=0.3)
                
        elif choice == '6':
            try:
                years = int(input("📅 Enter number of years of history to collect: "))
                days = years * 365
                exchange = input("🌍 Enter exchange (US/IN/ALL): ").strip().upper()
                exchange = exchange if exchange in ['US', 'IN'] else None
                
                print(f"\n📈 Collecting {years} years of data...")
                collector.collect_all_prices(
                    exchange=exchange, 
                    period_days=days, 
                    delay=0.5
                )
            except ValueError:
                print("❌ Invalid number of years")
                
        elif choice == '7':
            print("\n💥 MASSIVE HISTORICAL COLLECTION")
            print("🚨 This will attempt to collect MAXIMUM available history for ALL companies")
            print("📊 Some companies may have data back to 1970s!")
            print("⏰ Expected time: 8-15 hours")
            print("💾 Expected data: 1M+ price records")
            print("🔥 This is the ULTIMATE historical collection!")
            
            confirm1 = input("\n🤔 Do you understand this is a MASSIVE operation? (y/N): ").strip().lower()
            if confirm1 == 'y':
                confirm2 = input("🤔 Are you sure you want to proceed? (y/N): ").strip().lower()
                if confirm2 == 'y':
                    print("\n🚀 Starting MAXIMUM historical collection...")
                    print("💡 You can stop anytime with Ctrl+C and resume later")
                    try:
                        # Use special maximum history collection method
                        collector.collect_maximum_history(delay=0.2)
                    except KeyboardInterrupt:
                        print("\n⏸️ Massive collection paused by user")
                else:
                    print("❌ Massive collection cancelled")
            else:
                print("❌ Massive collection cancelled")
                
        elif choice == '8':
            collector.get_price_statistics()
            
        elif choice == '0':
            print("👋 Goodbye!")
            break
            
        else:
            print("❌ Invalid choice. Please select 0-8.")

def main():
    """Main function"""
    print("📊 Daily Price Data Collector")
    print("Collecting OHLCV data for stored companies...")
    
    try:
        interactive_menu()
    except KeyboardInterrupt:
        print("\n👋 Exiting...")
    except Exception as e:
        logger.error(f"Error in main: {e}")

if __name__ == "__main__":
    main()
