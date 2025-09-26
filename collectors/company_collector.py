import yfinance as yf
import pandas as pd
import time
import logging
import requests
from datetime import datetime
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import IntegrityError
from io import StringIO
import sys
import os

# Add parent directory to path to import our modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database import engine, Base
from models.company import Company

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class CompanyCollector:
    def __init__(self):
        """Initialize the company collector with database session"""
        self.Session = sessionmaker(bind=engine)
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
        
    def get_us_company_list(self):
        """Get list of popular US stock symbols to collect data for"""
        # Popular US stocks from various sectors
        us_stocks = [
            # Tech Giants
            'AAPL', 'MSFT', 'GOOGL', 'AMZN', 'META', 'TSLA', 'NVDA', 'NFLX', 'ADBE', 'CRM',
            # Financial
            'JPM', 'BAC', 'WFC', 'GS', 'MS', 'C', 'AXP', 'BLK', 'SCHW', 'USB',
            # Healthcare
            'JNJ', 'PFE', 'UNH', 'ABBV', 'MRK', 'TMO', 'ABT', 'DHR', 'BMY', 'LLY',
            # Consumer
            'PG', 'KO', 'PEP', 'WMT', 'HD', 'MCD', 'NKE', 'SBUX', 'TGT', 'LOW',
            # Industrial
            'BA', 'CAT', 'GE', 'MMM', 'HON', 'UPS', 'LMT', 'RTX', 'DE', 'EMR',
            # Energy
            'XOM', 'CVX', 'COP', 'EOG', 'SLB', 'PXD', 'KMI', 'OXY', 'PSX', 'VLO'
        ]
        return us_stocks

    def get_indian_company_list(self):
        """Get comprehensive list of Indian NSE companies"""
        try:
            logger.info("Fetching NSE equity list...")
            
            # Try to get from NSE official CSV
            nse_url = "https://archives.nseindia.com/content/equities/EQUITY_L.csv"
            
            try:
                response = self.session.get(nse_url)
                if response.status_code == 200:
                    # Parse CSV data
                    csv_data = StringIO(response.text)
                    df = pd.read_csv(csv_data)
                    logger.info(f"Found {len(df)} NSE companies from official CSV")
                    return [f"{symbol}.NS" for symbol in df['SYMBOL'].tolist()]
            except Exception as e:
                logger.warning(f"NSE CSV failed: {e}")
            
            # Fallback: Comprehensive list of major Indian stocks
            logger.info("Using comprehensive Indian stock list...")
            return self.get_fallback_indian_list()
            
        except Exception as e:
            logger.error(f"Error fetching Indian list: {e}")
            return self.get_fallback_indian_list()
    
    def get_fallback_indian_list(self):
        """Comprehensive fallback list of major Indian companies"""
        major_indian_stocks = [
            # Banking & Financial Services
            'HDFCBANK', 'ICICIBANK', 'SBIN', 'KOTAKBANK', 'AXISBANK', 'INDUSINDBK', 'FEDERALBNK', 
            'BANKBARODA', 'PNB', 'CANBK', 'IDFCFIRSTB', 'RBLBANK', 'YESBANK', 'AUBANK', 'BANDHANBNK',
            
            # IT Services & Technology
            'TCS', 'INFY', 'WIPRO', 'HCLTECH', 'TECHM', 'LTI', 'MINDTREE', 'MPHASIS', 'COFORGE', 'LTTS',
            
            # Oil & Gas
            'RELIANCE', 'ONGC', 'IOC', 'BPCL', 'HINDPETRO', 'GAIL', 'OIL', 'MGL', 'IGL', 'PETRONET',
            
            # Automobiles
            'MARUTI', 'TATAMOTORS', 'M&M', 'BAJAJ-AUTO', 'HEROMOTOCO', 'EICHERMOT', 'TVSMOTOR', 'ASHOKLEY',
            
            # Pharmaceuticals
            'SUNPHARMA', 'DRREDDY', 'CIPLA', 'DIVISLAB', 'BIOCON', 'LUPIN', 'CADILAHC', 'GLENMARK',
            
            # FMCG & Consumer
            'HINDUNILVR', 'ITC', 'NESTLEIND', 'BRITANNIA', 'DABUR', 'GODREJCP', 'MARICO', 'COLPAL',
            
            # Metals & Mining
            'TATASTEEL', 'HINDALCO', 'JSWSTEEL', 'VEDL', 'COALINDIA', 'SAIL', 'NMDC', 'JINDALSTEL',
            
            # Cement
            'ULTRACEMCO', 'SHREECEM', 'ACC', 'AMBUJACEMENT', 'DALMIACEM', 'RAMCOCEM',
            
            # Telecom
            'BHARTIARTL', 'IDEA',
            
            # Power & Utilities
            'NTPC', 'POWERGRID', 'ADANIPOWER', 'TATAPOWER', 'NHPC', 'SJVN',
            
            # Infrastructure & Construction
            'LT', 'ADANIPORTS', 'ADANIENT', 'ADANIGREEN', 'GMR', 'IRB',
            
            # Retail & E-commerce
            'DMART', 'TRENT', 'SHOPERSTOP',
            
            # Insurance & Financial Services
            'SBILIFE', 'HDFCLIFE', 'ICICIPRULI', 'BAJAJFINSV', 'BAJFINANCE',
            
            # Media & Entertainment
            'ZEEL', 'SUNTV', 'NETWORK18',
            
            # Real Estate
            'DLF', 'GODREJPROP', 'OBEROIRLTY', 'BRIGADE',
            
            # Healthcare & Hospitals
            'APOLLOHOSP', 'FORTIS', 'MAXHEALTH',
            
            # Chemicals & Paints
            'ASIANPAINT', 'BERGERPAINTS', 'PIDILITIND', 'DEEPAKNTR', 'SRF',
            
            # Capital Goods
            'BHEL', 'BEL', 'HAL', 'BEML', 'CUMMINSIND', 'SIEMENS',
            
            # Consumer Durables
            'WHIRLPOOL', 'VOLTAS', 'BLUESTAR', 'HAVELLS', 'CROMPTON'
        ]
        
        # Add .NS suffix for NSE stocks
        return [f"{symbol}.NS" for symbol in major_indian_stocks]
    
    def fetch_company_info(self, symbol):
        """
        Fetch comprehensive company information using yfinance
        
        Args:
            symbol (str): Stock symbol (e.g., 'AAPL', 'MSFT')
            
        Returns:
            dict: Company information or None if failed
        """
        try:
            logger.info(f"Fetching data for {symbol}")
            
            # Create ticker object
            ticker = yf.Ticker(symbol)
            
            # Get company info
            info = ticker.info
            
            # Extract relevant fields (with fallbacks for missing data)
            company_data = {
                'symbol': symbol,
                'company_name': info.get('longName', info.get('shortName', symbol)),
                'sector': info.get('sector', 'Unknown'),
                'industry': info.get('industry', 'Unknown'),
                'market_cap': info.get('marketCap', 0),
                'business_summary': info.get('longBusinessSummary', 'No summary available')
            }
            
            # Validate data quality
            if not company_data['company_name'] or company_data['company_name'] == symbol:
                logger.warning(f"Poor data quality for {symbol} - missing company name")
                return None
                
            logger.info(f"Successfully fetched data for {symbol}: {company_data['company_name']}")
            return company_data
            
        except Exception as e:
            logger.error(f"Error fetching data for {symbol}: {str(e)}")
            return None
    
    def save_company(self, company_data):
        """
        Save company data to database
        
        Args:
            company_data (dict): Company information to save
            
        Returns:
            bool: True if saved successfully, False otherwise
        """
        session = self.Session()
        try:
            # Check if company already exists
            existing = session.query(Company).filter_by(symbol=company_data['symbol']).first()
            
            if existing:
                # Update existing company
                logger.info(f"Updating existing company: {company_data['symbol']}")
                for key, value in company_data.items():
                    if key != 'symbol':  # Don't update the symbol
                        setattr(existing, key, value)
                existing.last_updated = datetime.now()
            else:
                # Create new company
                logger.info(f"Adding new company: {company_data['symbol']} - {company_data['company_name']}")
                new_company = Company(**company_data)
                session.add(new_company)
            
            session.commit()
            return True
            
        except IntegrityError as e:
            session.rollback()
            logger.error(f"Database integrity error for {company_data['symbol']}: {str(e)}")
            return False
        except Exception as e:
            session.rollback()
            logger.error(f"Error saving company {company_data['symbol']}: {str(e)}")
            return False
        finally:
            session.close()
    
    def collect_us_companies(self, delay=1):
        """Collect US companies"""
        companies = self.get_us_company_list()
        logger.info(f"🇺🇸 Starting US stock collection for {len(companies)} companies...")
        return self._collect_companies(companies, delay)
    
    def collect_indian_companies(self, max_companies=None, delay=1):
        """Collect Indian NSE companies"""
        companies = self.get_indian_company_list()
        
        if max_companies:
            companies = companies[:max_companies]
        
        logger.info(f"🇮🇳 Starting Indian stock collection for {len(companies)} companies...")
        return self._collect_companies(companies, delay)
    
    def collect_all_companies(self, include_us=True, include_indian=True, max_indian=None, delay=1):
        """
        Collect data for all companies (US + Indian)
        
        Args:
            include_us (bool): Include US companies
            include_indian (bool): Include Indian companies  
            max_indian (int): Limit Indian companies (for testing)
            delay (float): Delay between API calls
        """
        total_successful = 0
        total_failed = 0
        
        if include_us:
            logger.info("=" * 60)
            logger.info("🇺🇸 COLLECTING US COMPANIES")
            logger.info("=" * 60)
            us_success, us_failed = self.collect_us_companies(delay)
            total_successful += us_success
            total_failed += us_failed
        
        if include_indian:
            logger.info("=" * 60)
            logger.info("🇮🇳 COLLECTING INDIAN COMPANIES")
            logger.info("=" * 60)
            indian_success, indian_failed = self.collect_indian_companies(max_indian, delay)
            total_successful += indian_success
            total_failed += indian_failed
        
        # Final summary
        total_processed = total_successful + total_failed
        logger.info("=" * 60)
        logger.info("🎉 FINAL COLLECTION SUMMARY")
        logger.info("=" * 60)
        logger.info(f"Total companies processed: {total_processed}")
        logger.info(f"Successfully saved: {total_successful}")
        logger.info(f"Failed: {total_failed}")
        logger.info(f"Overall success rate: {(total_successful/total_processed)*100:.1f}%")
        
        return total_successful, total_failed
    
    def _collect_companies(self, companies, delay=1):
        """Internal method to collect a list of companies"""
        total_companies = len(companies)
        successful_saves = 0
        failed_fetches = 0
        
        for i, symbol in enumerate(companies, 1):
            logger.info(f"Processing {i}/{total_companies}: {symbol}")
            
            try:
                # Fetch company data
                company_data = self.fetch_company_info(symbol)
                
                if company_data:
                    # Save to database
                    if self.save_company(company_data):
                        successful_saves += 1
                    else:
                        logger.error(f"Failed to save {symbol}")
                        failed_fetches += 1
                else:
                    failed_fetches += 1
                    logger.warning(f"Failed to fetch data for {symbol}")
            
            except Exception as e:
                logger.error(f"Error processing {symbol}: {e}")
                failed_fetches += 1
            
            # Rate limiting delay
            if delay > 0 and i < total_companies:
                time.sleep(delay)
        
        # Summary for this batch
        logger.info(f"Batch completed!")
        logger.info(f"Companies processed: {total_companies}")
        logger.info(f"Successfully saved: {successful_saves}")
        logger.info(f"Failed: {failed_fetches}")
        logger.info(f"Success rate: {(successful_saves/total_companies)*100:.1f}%")
        
        return successful_saves, failed_fetches
    
    def collect_specific_companies(self, symbols, delay=1):
        """
        Collect data for specific company symbols
        
        Args:
            symbols (list): List of stock symbols to collect
            delay (int): Delay between API calls
        """
        logger.info(f"Collecting data for specific companies: {symbols}")
        
        for symbol in symbols:
            company_data = self.fetch_company_info(symbol)
            if company_data:
                self.save_company(company_data)
            if delay > 0:
                time.sleep(delay)

def interactive_menu():
    """Interactive menu for company collection"""
    collector = CompanyCollector()
    
    while True:
        print("\n" + "=" * 60)
        print("🏢 COMPANY DATA COLLECTOR")
        print("=" * 60)
        print("1️⃣  Collect US Companies Only (~60 companies)")
        print("2️⃣  Collect Indian Companies (100 companies)")
        print("3️⃣  Collect Indian Companies (500 companies)")  
        print("4️⃣  Collect Indian Companies (1000 companies)")
        print("5️⃣  Collect ALL Indian Companies (2000+ companies)")
        print("6️⃣  Collect Both US + Indian (Limited)")
        print("7️⃣  Collect EVERYTHING (US + ALL Indian)")
        print("8️⃣  Collect Specific Companies")
        print("9️⃣  Show Database Statistics")
        print("0️⃣  Exit")
        
        choice = input("\n🤔 Select an option (0-9): ").strip()
        
        if choice == '1':
            print("\n🇺🇸 Collecting US companies...")
            collector.collect_us_companies(delay=0.5)
            
        elif choice == '2':
            print("\n🇮🇳 Collecting 100 Indian companies...")
            collector.collect_indian_companies(max_companies=100, delay=0.5)
            
        elif choice == '3':
            print("\n🇮🇳 Collecting 500 Indian companies...")
            collector.collect_indian_companies(max_companies=500, delay=0.5)
            
        elif choice == '4':
            print("\n🇮🇳 Collecting 1000 Indian companies...")
            collector.collect_indian_companies(max_companies=1000, delay=0.5)
            
        elif choice == '5':
            print("\n🚨 WARNING: This will collect 2000+ Indian companies!")
            print("⏰ This process will take 2-4 hours to complete")
            confirm = input("🤔 Are you sure? (y/N): ").strip().lower()
            if confirm == 'y':
                print("\n🇮🇳 Collecting ALL Indian companies...")
                print("💡 You can stop anytime with Ctrl+C and resume later")
                try:
                    collector.collect_indian_companies(delay=0.3)
                except KeyboardInterrupt:
                    print("\n⏸️ Collection paused by user")
            else:
                print("❌ Collection cancelled")
                
        elif choice == '6':
            print("\n🌍 Collecting US + Limited Indian companies...")
            collector.collect_all_companies(max_indian=100, delay=0.5)
            
        elif choice == '7':
            print("\n🚨 WARNING: This will collect EVERYTHING!")
            print("⏰ This process will take 3-5 hours to complete")
            confirm = input("🤔 Are you sure? (y/N): ").strip().lower()
            if confirm == 'y':
                print("\n🌍 Collecting EVERYTHING...")
                try:
                    collector.collect_all_companies(delay=0.3)
                except KeyboardInterrupt:
                    print("\n⏸️ Collection paused by user")
            else:
                print("❌ Collection cancelled")
                
        elif choice == '8':
            print("\n📝 Enter stock symbols separated by commas")
            print("Examples: AAPL,MSFT,GOOGL or TCS.NS,RELIANCE.NS")
            symbols_input = input("Symbols: ").strip()
            if symbols_input:
                symbols = [s.strip() for s in symbols_input.split(',')]
                print(f"\n🎯 Collecting {len(symbols)} specific companies...")
                collector.collect_specific_companies(symbols, delay=0.5)
            else:
                print("❌ No symbols entered")
                
        elif choice == '9':
            show_database_stats()
            
        elif choice == '0':
            print("👋 Goodbye!")
            break
            
        else:
            print("❌ Invalid choice. Please select 0-9.")

def show_database_stats():
    """Show database statistics"""
    from database import SessionLocal
    
    session = SessionLocal()
    try:
        total = session.query(Company).count()
        us_companies = session.query(Company).filter(~Company.symbol.like('%.NS')).count()
        indian_companies = session.query(Company).filter(Company.symbol.like('%.NS')).count()
        
        print(f"\n📊 DATABASE STATISTICS")
        print(f"=" * 40)
        print(f"Total companies: {total}")
        print(f"US companies: {us_companies}")
        print(f"Indian companies (.NS): {indian_companies}")
        
        if total > 0:
            # Show recent additions
            recent = session.query(Company).order_by(Company.last_updated.desc()).limit(5).all()
            print(f"\n🕐 Most Recent Companies:")
            for company in recent:
                market_cap_b = company.market_cap / 1e9 if company.market_cap else 0
                print(f"  • {company.symbol:15} - {company.company_name[:40]:<40} (${market_cap_b:.1f}B)")
        
    finally:
        session.close()

def main():
    """Main function"""
    print("🏢 Company Data Collector")
    print("Starting interactive menu...")
    
    try:
        interactive_menu()
    except KeyboardInterrupt:
        print("\n👋 Exiting...")
    except Exception as e:
        logger.error(f"Error in main: {e}")

if __name__ == "__main__":
    main()
