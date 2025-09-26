#!/usr/bin/env python3
"""
Assets Collector - Updated company collector for the new assets-based structure
Collects company data and stores it in the assets table
"""
import yfinance as yf
import pandas as pd
import sys
import os
from datetime import datetime
import logging
from typing import Optional, List
import time

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database import SessionLocal
from models.assets import Asset

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class AssetsCollector:
    def __init__(self):
        self.session = SessionLocal()
        self.collected_count = 0
        self.failed_count = 0
        
    def __del__(self):
        if hasattr(self, 'session'):
            self.session.close()
    
    def asset_exists(self, symbol: str) -> bool:
        """Check if asset already exists in database"""
        return self.session.query(Asset).filter_by(symbol=symbol).first() is not None
    
    def collect_asset_info(self, symbol: str) -> Optional[dict]:
        """Collect asset information using yfinance"""
        try:
            ticker = yf.Ticker(symbol)
            info = ticker.info
            
            if not info or 'symbol' not in info:
                return None
            
            # Determine asset properties
            asset_type = "stock"
            if symbol.endswith('.NS'):
                exchange = "NSE"
                currency = "INR"
            elif symbol.endswith('.BO'):
                exchange = "BSE"
                currency = "INR"
            else:
                exchange = info.get('exchange', 'NASDAQ')
                currency = info.get('currency', 'USD')
            
            asset_data = {
                'symbol': symbol,
                'name': info.get('longName', info.get('shortName', symbol)),
                'type': asset_type,
                'exchange': exchange,
                'sector': info.get('sector'),
                'industry': info.get('industry'),
                'currency': currency,
                'market_cap': info.get('marketCap'),
                'description': info.get('longBusinessSummary')
            }
            
            return asset_data
            
        except Exception as e:
            logger.warning(f"Failed to collect info for {symbol}: {e}")
            return None
    
    def save_asset(self, asset_data: dict) -> bool:
        """Save asset to database"""
        try:
            # Check if already exists
            if self.asset_exists(asset_data['symbol']):
                logger.info(f"Asset {asset_data['symbol']} already exists, skipping")
                return True
            
            asset = Asset(**asset_data)
            self.session.add(asset)
            self.session.commit()
            
            self.collected_count += 1
            logger.info(f"✅ Saved: {asset_data['symbol']} - {asset_data['name']}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to save {asset_data['symbol']}: {e}")
            self.session.rollback()
            self.failed_count += 1
            return False
    
    def collect_us_stocks(self):
        """Collect major US stocks"""
        logger.info("🇺🇸 Starting US stocks collection...")
        
        # Major US stocks
        us_symbols = [
            'AAPL', 'MSFT', 'GOOGL', 'AMZN', 'TSLA', 'META', 'NVDA', 'BRK-B', 'JNJ', 'WMT',
            'V', 'PG', 'JPM', 'UNH', 'MA', 'HD', 'DIS', 'PYPL', 'ADBE', 'NFLX',
            'CRM', 'BAC', 'CMCSA', 'XOM', 'ABT', 'VZ', 'KO', 'PFE', 'PEP', 'TMO',
            'AVGO', 'COST', 'NKE', 'MRK', 'DHR', 'ABBV', 'ACN', 'LLY', 'CVX', 'MCD',
            'NEE', 'QCOM', 'TXN', 'WFC', 'BMY', 'AMD', 'PM', 'UNP', 'IBM', 'INTC',
            'HON', 'COP', 'T', 'LOW', 'UPS', 'ORCL', 'MDT', 'LMT', 'BA', 'SPGI'
        ]
        
        for i, symbol in enumerate(us_symbols):
            logger.info(f"Processing US stock {i+1}/{len(us_symbols)}: {symbol}")
            
            asset_data = self.collect_asset_info(symbol)
            if asset_data:
                self.save_asset(asset_data)
            else:
                self.failed_count += 1
            
            # Small delay to avoid rate limiting
            time.sleep(0.1)
        
        logger.info(f"🇺🇸 US stocks collection completed")
    
    def collect_indian_stocks_from_csv(self):
        """Collect Indian stocks from NSE CSV file"""
        logger.info("🇮🇳 Starting Indian stocks collection from CSV...")
        
        try:
            # Download NSE companies list
            url = "https://nsearchives.nseindia.com/content/equities/EQUITY_L.csv"
            logger.info("Downloading NSE companies list...")
            
            df = pd.read_csv(url)
            logger.info(f"Found {len(df)} companies in NSE list")
            
            # Process each company
            for i, row in df.iterrows():
                symbol = f"{row['SYMBOL']}.NS"
                
                if i % 100 == 0:
                    logger.info(f"Processing Indian stock {i+1}/{len(df)}: {symbol}")
                
                # Skip if already exists
                if self.asset_exists(symbol):
                    continue
                
                asset_data = self.collect_asset_info(symbol)
                if asset_data:
                    self.save_asset(asset_data)
                else:
                    self.failed_count += 1
                
                # Small delay
                time.sleep(0.05)
                
                # Progress update every 100 stocks
                if i % 100 == 99:
                    success_rate = (self.collected_count / (i + 1)) * 100 if i > 0 else 0
                    logger.info(f"Progress: {i+1}/{len(df)} processed, {self.collected_count} saved, {success_rate:.1f}% success rate")
            
        except Exception as e:
            logger.error(f"❌ Failed to collect Indian stocks: {e}")
    
    def collect_all_assets(self):
        """Collect all assets (US + Indian stocks)"""
        logger.info("🚀 Starting comprehensive assets collection...")
        start_time = datetime.now()
        
        # Collect US stocks first
        self.collect_us_stocks()
        
        # Collect Indian stocks
        self.collect_indian_stocks_from_csv()
        
        end_time = datetime.now()
        duration = end_time - start_time
        
        logger.info(f"🎉 Assets collection completed!")
        logger.info(f"✅ Total collected: {self.collected_count}")
        logger.info(f"❌ Total failed: {self.failed_count}")
        logger.info(f"⏱️ Duration: {duration}")
        
        if self.collected_count > 0:
            success_rate = (self.collected_count / (self.collected_count + self.failed_count)) * 100
            logger.info(f"📊 Success rate: {success_rate:.1f}%")
    
    def show_stats(self):
        """Show current database statistics"""
        total_assets = self.session.query(Asset).count()
        
        # Count by type
        stocks = self.session.query(Asset).filter_by(type='stock').count()
        
        # Count by exchange
        us_stocks = self.session.query(Asset).filter(Asset.exchange.in_(['NASDAQ', 'NYSE'])).count()
        indian_stocks = self.session.query(Asset).filter(Asset.exchange.in_(['NSE', 'BSE'])).count()
        
        logger.info(f"📊 Database Statistics:")
        logger.info(f"   Total assets: {total_assets}")
        logger.info(f"   Stocks: {stocks}")
        logger.info(f"   US stocks: {us_stocks}")
        logger.info(f"   Indian stocks: {indian_stocks}")
        
        # Show sample assets
        sample = self.session.query(Asset).limit(3).all()
        if sample:
            logger.info(f"📋 Sample assets:")
            for asset in sample:
                logger.info(f"   {asset.symbol} - {asset.name} ({asset.exchange})")

def main():
    """Main interactive menu"""
    print("🚀 ASSETS COLLECTOR")
    print("=" * 50)
    
    collector = AssetsCollector()
    
    while True:
        print("\n📋 Choose an option:")
        print("1. Collect US stocks (60 major stocks)")
        print("2. Collect Indian stocks (NSE companies)")
        print("3. Collect all assets (US + Indian)")
        print("4. Show database statistics") 
        print("5. Exit")
        
        try:
            choice = input("\n🤔 Enter your choice (1-5): ").strip()
            
            if choice == '1':
                collector.collect_us_stocks()
            elif choice == '2':
                collector.collect_indian_stocks_from_csv()
            elif choice == '3':
                collector.collect_all_assets()
            elif choice == '4':
                collector.show_stats()
            elif choice == '5':
                print("👋 Goodbye!")
                break
            else:
                print("❌ Invalid choice, please try again")
                
        except KeyboardInterrupt:
            print("\n\n⏹️ Collection stopped by user")
            break
        except Exception as e:
            logger.error(f"❌ Error: {e}")

if __name__ == "__main__":
    main()