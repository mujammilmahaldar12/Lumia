"""
Stocks Manager - Complete stock data management system
Handles downloading, updating, and managing stock data from official sources.

Author: Lumia Team
Purpose: Manage Indian (NSE/BSE) and US stocks data efficiently
"""

import requests
import pandas as pd
import yfinance as yf
from datetime import datetime, date
from typing import List, Dict, Tuple, Optional
import logging
import time
from sqlalchemy.orm import Session
from sqlalchemy import and_

# Import our models
from models.assets import Asset
from database import get_db


class StocksManager:
    """
    Complete stocks management system.
    Handles downloading, cross-checking, updating stock data.
    """
    
    def __init__(self):
        self.logger = self._setup_logger()
        self.db = None
        
        # Official data sources
        self.nse_url = "https://nsearchives.nseindia.com/content/equities/EQUITY_L.csv"
        self.bse_url = "https://api.bseindia.com/BseIndiaAPI/api/ListOfScrips/w"
        
        # US stocks - we'll use predefined list for now (can be expanded)
        self.us_major_stocks = [
            "AAPL", "MSFT", "GOOGL", "AMZN", "TSLA", "META", "NVDA", "JPM", 
            "JNJ", "V", "WMT", "PG", "UNH", "HD", "MA", "BAC", "ADBE", "CRM", 
            "NFLX", "KO", "PEP", "TMO", "ABT", "COST", "AVGO", "XOM", "LLY"
        ]
        
        # Fallback Indian stocks list (major NSE stocks) if API fails
        self.nse_fallback_stocks = [
            "RELIANCE.NS", "TCS.NS", "HDFCBANK.NS", "INFY.NS", "HINDUNILVR.NS",
            "ICICIBANK.NS", "KOTAKBANK.NS", "BHARTIARTL.NS", "SBIN.NS", "LICI.NS",
            "ITC.NS", "LT.NS", "AXISBANK.NS", "MARUTI.NS", "ASIANPAINT.NS",
            "BAJFINANCE.NS", "HCLTECH.NS", "WIPRO.NS", "ULTRACEMCO.NS", "NESTLEIND.NS"
        ]
    
    def _setup_logger(self):
        """Setup logging for the stocks manager."""
        logger = logging.getLogger("lumia.stocks_manager")
        logger.setLevel(logging.INFO)
        
        if not logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
            handler.setFormatter(formatter)
            logger.addHandler(handler)
        
        return logger
    
    def get_db_session(self) -> Session:
        """Get database session."""
        if not self.db:
            self.db = next(get_db())
        return self.db
    
    def close_db_session(self):
        """Close database session."""
        if self.db:
            self.db.close()
            self.db = None

    # ========================================
    # FUNCTION 1: DOWNLOAD STOCK LISTS
    # ========================================
    
    def download_nse_stocks(self) -> pd.DataFrame:
        """
        Download complete NSE stock list from official NSE website.
        
        Returns:
            DataFrame with NSE stocks data
        """
        self.logger.info("📥 Downloading NSE stocks from official source...")
        
        try:
            # Add headers to mimic browser request
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                'Accept-Language': 'en-US,en;q=0.5',
                'Accept-Encoding': 'gzip, deflate',
                'Connection': 'keep-alive',
                'Upgrade-Insecure-Requests': '1',
            }
            
            # Download NSE equity list with shorter timeout and retry logic
            response = requests.get(self.nse_url, headers=headers, timeout=15)
            response.raise_for_status()
            
            # Parse CSV data
            from io import StringIO
            df = pd.read_csv(StringIO(response.text))
            
            self.logger.info(f"✅ Downloaded {len(df)} NSE stocks")
            return df
            
        except (requests.exceptions.Timeout, requests.exceptions.ConnectionError) as e:
            self.logger.warning(f"⚠️ NSE server connection issue (expected): {str(e)}")
            self.logger.info("ℹ️ NSE blocks automated requests - this is normal. Continuing with US stocks only.")
            return pd.DataFrame()
        except Exception as e:
            self.logger.warning(f"⚠️ Error downloading NSE data: {str(e)}")
            self.logger.info("ℹ️ Continuing without NSE data - using US stocks only.")
            return pd.DataFrame()
    
    def download_bse_stocks(self) -> pd.DataFrame:
        """
        Download BSE stock list.
        Note: BSE API might require authentication, using backup method.
        
        Returns:
            DataFrame with BSE stocks data
        """
        self.logger.info("📥 Downloading BSE stocks...")
        
        try:
            # For now, we'll use a backup method or predefined list
            # This can be enhanced with proper BSE API integration
            self.logger.info("ℹ️ BSE download not implemented yet, using NSE data")
            return pd.DataFrame()
            
        except Exception as e:
            self.logger.error(f"❌ Error downloading BSE data: {str(e)}")
            return pd.DataFrame()
    
    def get_us_stocks_data(self) -> List[Dict]:
        """
        Get US stocks data using yfinance.
        Uses predefined list of major US stocks.
        
        Returns:
            List of dictionaries with US stock data
        """
        self.logger.info(f"📥 Getting data for {len(self.us_major_stocks)} US stocks...")
        
        us_stocks = []
        
        for symbol in self.us_major_stocks:
            try:
                self.logger.info(f"  Fetching {symbol}...")
                
                # Get stock info from yfinance
                ticker = yf.Ticker(symbol)
                info = ticker.info
                
                if info and 'shortName' in info:
                    stock_data = {
                        'symbol': symbol,
                        'name': info.get('shortName', info.get('longName', 'Unknown')),
                        'sector': info.get('sector', 'Unknown'),
                        'industry': info.get('industry', 'Unknown'),
                        'market_cap': info.get('marketCap', 0),
                        'exchange': self._get_us_exchange(info),
                        'country': 'US',
                        'currency': 'USD',
                        'type': 'stock'
                    }
                    us_stocks.append(stock_data)
                    
            except Exception as e:
                self.logger.warning(f"⚠️ Could not fetch {symbol}: {str(e)}")
                continue
        
        self.logger.info(f"✅ Successfully fetched {len(us_stocks)} US stocks")
        return us_stocks
    
    def _get_us_exchange(self, info: Dict) -> str:
        """Determine US exchange from stock info."""
        exchange = info.get('exchange', '').upper()
        if 'NASDAQ' in exchange:
            return 'NASDAQ'
        elif 'NYSE' in exchange:
            return 'NYSE'
        else:
            return 'NYSE'  # Default

    # ========================================
    # FUNCTION 2: CROSS-CHECK WITH DATABASE
    # ========================================
    
    def cross_check_stocks(self, new_stocks: List[Dict]) -> Tuple[List[Dict], List[Dict], List[Dict]]:
        """
        Cross-check downloaded stocks with existing database records.
        
        Args:
            new_stocks: List of stock data dictionaries
            
        Returns:
            Tuple of (stocks_to_add, stocks_to_update, stocks_unchanged)
        """
        self.logger.info("🔍 Cross-checking stocks with database...")
        
        db = self.get_db_session()
        
        # Get all existing stocks from database
        existing_stocks = db.query(Asset).filter(Asset.type == 'stock').all()
        existing_symbols = {stock.symbol: stock for stock in existing_stocks}
        
        stocks_to_add = []      # New stocks not in database
        stocks_to_update = []   # Existing stocks with changes
        stocks_unchanged = []   # Existing stocks with no changes
        
        for new_stock in new_stocks:
            symbol = new_stock['symbol']
            
            if symbol in existing_symbols:
                # Stock exists, check if update needed
                existing_stock = existing_symbols[symbol]
                
                if self._needs_update(existing_stock, new_stock):
                    stocks_to_update.append({
                        'existing': existing_stock,
                        'new_data': new_stock
                    })
                else:
                    stocks_unchanged.append(new_stock)
            else:
                # New stock, add to database
                stocks_to_add.append(new_stock)
        
        self.logger.info(f"📊 Cross-check results:")
        self.logger.info(f"  - New stocks to add: {len(stocks_to_add)}")
        self.logger.info(f"  - Stocks to update: {len(stocks_to_update)}")
        self.logger.info(f"  - Stocks unchanged: {len(stocks_unchanged)}")
        
        return stocks_to_add, stocks_to_update, stocks_unchanged
    
    def _needs_update(self, existing_stock: Asset, new_data: Dict) -> bool:
        """
        Check if existing stock record needs update.
        
        Args:
            existing_stock: Existing Asset record
            new_data: New stock data dictionary
            
        Returns:
            True if update needed, False otherwise
        """
        # Check key fields that might change
        fields_to_check = ['name', 'sector', 'industry', 'market_cap']
        
        for field in fields_to_check:
            if field in new_data:
                existing_value = getattr(existing_stock, field, None)
                new_value = new_data[field]
                
                # Handle None values and type differences
                if existing_value != new_value:
                    return True
        
        return False

    # ========================================
    # FUNCTION 3: UPDATE EXISTING STOCKS
    # ========================================
    
    def update_existing_stocks(self, stocks_to_update: List[Dict]):
        """
        Update existing stock records with new data.
        
        Args:
            stocks_to_update: List of stocks that need updating
        """
        if not stocks_to_update:
            self.logger.info("ℹ️ No stocks to update")
            return
        
        self.logger.info(f"🔄 Updating {len(stocks_to_update)} existing stocks...")
        
        db = self.get_db_session()
        updated_count = 0
        
        try:
            for update_info in stocks_to_update:
                existing_stock = update_info['existing']
                new_data = update_info['new_data']
                
                # Update fields
                existing_stock.name = new_data.get('name', existing_stock.name)
                existing_stock.sector = new_data.get('sector', existing_stock.sector)
                existing_stock.industry = new_data.get('industry', existing_stock.industry)
                existing_stock.market_cap = new_data.get('market_cap', existing_stock.market_cap)
                
                # Update timestamp
                existing_stock.last_updated = datetime.now()
                
                updated_count += 1
                self.logger.info(f"  ✅ Updated {existing_stock.symbol}")
            
            # Commit all updates
            db.commit()
            self.logger.info(f"✅ Successfully updated {updated_count} stocks")
            
        except Exception as e:
            self.logger.error(f"❌ Error updating stocks: {str(e)}")
            db.rollback()

    # ========================================
    # FUNCTION 4: ADD NEW STOCKS
    # ========================================
    
    def add_new_stocks(self, stocks_to_add: List[Dict]):
        """
        Add new stock records to database.
        
        Args:
            stocks_to_add: List of new stocks to add
        """
        if not stocks_to_add:
            self.logger.info("ℹ️ No new stocks to add")
            return
        
        self.logger.info(f"➕ Adding {len(stocks_to_add)} new stocks...")
        
        db = self.get_db_session()
        added_count = 0
        
        try:
            for stock_data in stocks_to_add:
                # Create new Asset record
                new_asset = Asset(
                    symbol=stock_data['symbol'],
                    name=stock_data['name'],
                    type='stock',
                    subtype='equity',
                    exchange=stock_data.get('exchange', 'Unknown'),
                    country=stock_data.get('country', 'Unknown'),
                    currency=stock_data.get('currency', 'USD'),
                    sector=stock_data.get('sector', 'Unknown'),
                    industry=stock_data.get('industry', 'Unknown'),
                    market_cap=stock_data.get('market_cap'),
                    is_active=True,
                    created_at=datetime.now(),
                    last_updated=datetime.now()
                )
                
                db.add(new_asset)
                added_count += 1
                self.logger.info(f"  ➕ Added {stock_data['symbol']}")
            
            # Commit all additions
            db.commit()
            self.logger.info(f"✅ Successfully added {added_count} new stocks")
            
        except Exception as e:
            self.logger.error(f"❌ Error adding stocks: {str(e)}")
            db.rollback()

    # ========================================
    # FUNCTION 5: MAIN ORCHESTRATOR
    # ========================================
    
    def sync_all_stocks(self):
        """
        Main function to sync all stocks.
        Downloads, cross-checks, updates, and adds stocks.
        """
        self.logger.info("🚀 Starting complete stocks synchronization...")
        
        try:
            # Step 1: Download stock data from all sources
            all_stocks = []
            
            # Get NSE stocks
            nse_df = self.download_nse_stocks()
            if not nse_df.empty:
                nse_stocks = self._convert_nse_data(nse_df)
                all_stocks.extend(nse_stocks)
            else:
                # Use fallback NSE stocks if API fails
                self.logger.info("📥 Using fallback NSE stock list...")
                nse_fallback_stocks = self._get_fallback_nse_stocks()
                all_stocks.extend(nse_fallback_stocks)
            
            # Get US stocks
            us_stocks = self.get_us_stocks_data()
            all_stocks.extend(us_stocks)
            
            self.logger.info(f"📊 Total stocks downloaded: {len(all_stocks)}")
            
            if not all_stocks:
                self.logger.warning("⚠️ No stock data downloaded, aborting sync")
                return
            
            # Step 2: Cross-check with database
            stocks_to_add, stocks_to_update, stocks_unchanged = self.cross_check_stocks(all_stocks)
            
            # Step 3: Update existing stocks
            self.update_existing_stocks(stocks_to_update)
            
            # Step 4: Add new stocks
            self.add_new_stocks(stocks_to_add)
            
            # Step 5: Summary
            self.logger.info("🎉 Stocks synchronization completed!")
            self.logger.info(f"📈 Summary:")
            self.logger.info(f"  - Total stocks processed: {len(all_stocks)}")
            self.logger.info(f"  - New stocks added: {len(stocks_to_add)}")
            self.logger.info(f"  - Existing stocks updated: {len(stocks_to_update)}")
            self.logger.info(f"  - Stocks unchanged: {len(stocks_unchanged)}")
            
        except Exception as e:
            self.logger.error(f"❌ Error in stocks synchronization: {str(e)}")
            raise
        
        finally:
            self.close_db_session()
    
    def _convert_nse_data(self, nse_df: pd.DataFrame) -> List[Dict]:
        """
        Convert NSE CSV data to our standard format.
        
        Args:
            nse_df: DataFrame from NSE
            
        Returns:
            List of stock dictionaries
        """
        stocks = []
        
        for _, row in nse_df.iterrows():
            try:
                # NSE CSV typically has: SYMBOL, NAME OF COMPANY, SERIES, etc.
                stock_data = {
                    'symbol': f"{row['SYMBOL']}.NS",  # Add .NS for NSE
                    'name': row['NAME OF COMPANY'].strip(),
                    'exchange': 'NSE',
                    'country': 'IN',
                    'currency': 'INR',
                    'type': 'stock',
                    'sector': 'Unknown',  # NSE CSV doesn't have sector info
                    'industry': 'Unknown'
                }
                stocks.append(stock_data)
                
            except Exception as e:
                self.logger.warning(f"⚠️ Error processing NSE row: {str(e)}")
                continue
        
        return stocks
    
    def _get_fallback_nse_stocks(self) -> List[Dict]:
        """
        Get fallback NSE stocks when API is unavailable.
        Uses predefined list of major Indian stocks.
        
        Returns:
            List of stock dictionaries
        """
        fallback_stocks = []
        
        for symbol in self.nse_fallback_stocks:
            try:
                self.logger.info(f"  Getting fallback data for {symbol}...")
                
                # Use yfinance to get basic info
                ticker = yf.Ticker(symbol)
                info = ticker.info
                
                if info and 'shortName' in info:
                    stock_data = {
                        'symbol': symbol,
                        'name': info.get('shortName', info.get('longName', 'Unknown')),
                        'sector': info.get('sector', 'Unknown'),
                        'industry': info.get('industry', 'Unknown'),
                        'market_cap': info.get('marketCap', 0),
                        'exchange': 'NSE',
                        'country': 'IN',
                        'currency': 'INR',
                        'type': 'stock'
                    }
                    fallback_stocks.append(stock_data)
                
                # Small delay
                time.sleep(0.2)
                
            except Exception as e:
                self.logger.warning(f"⚠️ Could not fetch fallback data for {symbol}: {str(e)}")
                continue
        
        self.logger.info(f"✅ Got {len(fallback_stocks)} fallback NSE stocks")
        return fallback_stocks


# ========================================
# CONVENIENCE FUNCTIONS FOR EASY USE
# ========================================

def sync_stocks():
    """Easy function to sync all stocks."""
    manager = StocksManager()
    manager.sync_all_stocks()

def sync_nse_only():
    """Sync only NSE stocks."""
    manager = StocksManager()
    nse_df = manager.download_nse_stocks()
    if not nse_df.empty:
        nse_stocks = manager._convert_nse_data(nse_df)
        stocks_to_add, stocks_to_update, _ = manager.cross_check_stocks(nse_stocks)
        manager.update_existing_stocks(stocks_to_update)
        manager.add_new_stocks(stocks_to_add)
    manager.close_db_session()

def sync_us_only():
    """Sync only US stocks."""
    manager = StocksManager()
    us_stocks = manager.get_us_stocks_data()
    stocks_to_add, stocks_to_update, _ = manager.cross_check_stocks(us_stocks)
    manager.update_existing_stocks(stocks_to_update)
    manager.add_new_stocks(stocks_to_add)
    manager.close_db_session()


# ========================================
# MAIN EXECUTION
# ========================================

if __name__ == "__main__":
    print("🎯 Lumia Stocks Manager")
    print("=" * 50)
    
    # You can run different functions:
    
    # Option 1: Sync everything
    sync_stocks()
    
    # Option 2: Sync only NSE
    # sync_nse_only()
    
    # Option 3: Sync only US
    # sync_us_only()