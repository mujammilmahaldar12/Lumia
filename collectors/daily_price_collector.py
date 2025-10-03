"""
Daily Price Collector - Complete historical price data management
Downloads and manages daily price data for all assets (stocks, mutual funds, ETFs, crypto)

Author: Lumia Team
Purpose: Collect historical price data from asset creation date to present
"""

import yfinance as yf
import requests
import pandas as pd
from datetime import datetime, date, timedelta
from typing import List, Dict, Tuple, Optional
import logging
from sqlalchemy.orm import Session
from sqlalchemy import and_, func
import time

# Import our models
from models.assets import Asset
from models.daily_price import DailyPrice
from database import get_db


class DailyPriceCollector:
    """
    Complete daily price collection system.
    Downloads historical price data for all asset types.
    """
    
    def __init__(self):
        self.logger = self._setup_logger()
        self.db = None
        
        # CoinGecko settings for crypto (enhanced rate limiting)
        self.coingecko_base_url = "https://api.coingecko.com/api/v3"
        self.crypto_rate_limit = 2.5  # increased base delay between requests
        self.last_crypto_request = 0
    
    def _setup_logger(self):
        """Setup logging for the price collector."""
        logger = logging.getLogger("lumia.daily_price_collector")
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
    # FUNCTION 1: DOWNLOAD STOCK PRICES
    # ========================================
    
    def download_stock_prices(self, stocks: List[Asset]) -> List[Dict]:
        """
        Download historical stock price data using yfinance.
        
        Args:
            stocks: List of stock Asset objects
            
        Returns:
            List of price data dictionaries
        """
        self.logger.info(f"📈 Downloading price data for {len(stocks)} stocks...")
        
        all_price_data = []
        successful_downloads = 0
        
        for stock in stocks:
            try:
                self.logger.info(f"  Fetching prices for {stock.symbol}...")
                
                # Get date range (from creation or 1 year ago, whichever is more recent)
                start_date = max(
                    stock.created_at.date() if stock.created_at else date.today() - timedelta(days=365),
                    date.today() - timedelta(days=365)  # Max 1 year for initial load
                )
                end_date = date.today()
                
                # Download using yfinance
                ticker = yf.Ticker(stock.symbol)
                hist = ticker.history(start=start_date, end=end_date)
                
                if not hist.empty:
                    # Convert to our format
                    for date_idx, row in hist.iterrows():
                        price_data = {
                            'asset_id': stock.id,
                            'date': date_idx.date(),
                            'open_price': float(row['Open']),
                            'high_price': float(row['High']),
                            'low_price': float(row['Low']),
                            'close_price': float(row['Close']),
                            'adj_close': float(row.get('Adj Close', row['Close'])),
                            'volume': int(row.get('Volume', 0)),
                            'dividends': float(row.get('Dividends', 0)),
                            'stock_splits': float(row.get('Stock Splits', 0))
                        }
                        all_price_data.append(price_data)
                    
                    successful_downloads += 1
                    self.logger.info(f"    ✅ Got {len(hist)} price records for {stock.symbol}")
                else:
                    self.logger.warning(f"    ⚠️ No price data for {stock.symbol}")
                
                # Small delay to respect API limits
                time.sleep(0.1)
                
            except Exception as e:
                self.logger.error(f"    ❌ Error downloading {stock.symbol}: {str(e)}")
                continue
        
        self.logger.info(f"✅ Successfully downloaded prices for {successful_downloads}/{len(stocks)} stocks")
        return all_price_data
    
    # ========================================
    # FUNCTION 2: DOWNLOAD MUTUAL FUND PRICES
    # ========================================
    
    def download_mutual_fund_prices(self, mutual_funds: List[Asset]) -> List[Dict]:
        """
        Download historical mutual fund price data.
        
        Args:
            mutual_funds: List of mutual fund Asset objects
            
        Returns:
            List of price data dictionaries
        """
        self.logger.info(f"📊 Downloading price data for {len(mutual_funds)} mutual funds...")
        
        all_price_data = []
        successful_downloads = 0
        
        for fund in mutual_funds:
            try:
                self.logger.info(f"  Fetching prices for {fund.symbol}...")
                
                # For Indian mutual funds, we might need to use different approach
                # For now, try yfinance (works for US mutual funds)
                if fund.country == 'US':
                    # US mutual funds can use yfinance
                    ticker = yf.Ticker(fund.symbol)
                    
                    start_date = max(
                        fund.created_at.date() if fund.created_at else date.today() - timedelta(days=365),
                        date.today() - timedelta(days=365)
                    )
                    
                    hist = ticker.history(start=start_date, end=date.today())
                    
                    if not hist.empty:
                        for date_idx, row in hist.iterrows():
                            price_data = {
                                'asset_id': fund.id,
                                'date': date_idx.date(),
                                'open_price': float(row['Open']),
                                'high_price': float(row['High']),
                                'low_price': float(row['Low']),
                                'close_price': float(row['Close']),
                                'adj_close': float(row.get('Adj Close', row['Close'])),
                                'volume': int(row.get('Volume', 0)),
                                'dividends': float(row.get('Dividends', 0)),
                                'stock_splits': float(row.get('Stock Splits', 0))
                            }
                            all_price_data.append(price_data)
                        
                        successful_downloads += 1
                        self.logger.info(f"    ✅ Got {len(hist)} price records for {fund.symbol}")
                    else:
                        self.logger.warning(f"    ⚠️ No price data for {fund.symbol}")
                
                else:
                    # Indian mutual funds - would need AMFI NAV data
                    # For now, we'll skip but this can be implemented with AMFI API
                    self.logger.info(f"    ℹ️ Indian MF price collection not implemented yet: {fund.symbol}")
                
                time.sleep(0.1)
                
            except Exception as e:
                self.logger.error(f"    ❌ Error downloading {fund.symbol}: {str(e)}")
                continue
        
        self.logger.info(f"✅ Successfully downloaded prices for {successful_downloads}/{len(mutual_funds)} mutual funds")
        return all_price_data
    
    # ========================================
    # FUNCTION 3: DOWNLOAD ETF PRICES
    # ========================================
    
    def download_etf_prices(self, etfs: List[Asset]) -> List[Dict]:
        """
        Download historical ETF price data.
        
        Args:
            etfs: List of ETF Asset objects
            
        Returns:
            List of price data dictionaries
        """
        self.logger.info(f"📈 Downloading price data for {len(etfs)} ETFs...")
        
        all_price_data = []
        successful_downloads = 0
        
        for etf in etfs:
            try:
                self.logger.info(f"  Fetching prices for {etf.symbol}...")
                
                # ETFs work well with yfinance
                ticker = yf.Ticker(etf.symbol)
                
                start_date = max(
                    etf.created_at.date() if etf.created_at else date.today() - timedelta(days=365),
                    date.today() - timedelta(days=365)
                )
                
                hist = ticker.history(start=start_date, end=date.today())
                
                if not hist.empty:
                    for date_idx, row in hist.iterrows():
                        price_data = {
                            'asset_id': etf.id,
                            'date': date_idx.date(),
                            'open_price': float(row['Open']),
                            'high_price': float(row['High']),
                            'low_price': float(row['Low']),
                            'close_price': float(row['Close']),
                            'adj_close': float(row.get('Adj Close', row['Close'])),
                            'volume': int(row.get('Volume', 0)),
                            'dividends': float(row.get('Dividends', 0)),
                            'stock_splits': float(row.get('Stock Splits', 0))
                        }
                        all_price_data.append(price_data)
                    
                    successful_downloads += 1
                    self.logger.info(f"    ✅ Got {len(hist)} price records for {etf.symbol}")
                else:
                    self.logger.warning(f"    ⚠️ No price data for {etf.symbol}")
                
                time.sleep(0.1)
                
            except Exception as e:
                self.logger.error(f"    ❌ Error downloading {etf.symbol}: {str(e)}")
                continue
        
        self.logger.info(f"✅ Successfully downloaded prices for {successful_downloads}/{len(etfs)} ETFs")
        return all_price_data
    
    # ========================================
    # FUNCTION 4: DOWNLOAD CRYPTO PRICES
    # ========================================
    
    def download_crypto_prices(self, cryptos: List[Asset]) -> List[Dict]:
        """
        Download historical cryptocurrency price data using CoinGecko.
        
        Args:
            cryptos: List of crypto Asset objects
            
        Returns:
            List of price data dictionaries
        """
        self.logger.info(f"₿ Downloading price data for {len(cryptos)} cryptocurrencies...")
        
        all_price_data = []
        successful_downloads = 0
        failed_cryptos = []
        
        for crypto in cryptos:
            success = False
            max_retries = 3
            base_delay = 2.0  # Base delay for rate limiting
            
            for attempt in range(max_retries):
                try:
                    if attempt == 0:
                        self.logger.info(f"  Fetching prices for {crypto.symbol}...")
                    else:
                        self.logger.info(f"  Retry {attempt}/{max_retries-1} for {crypto.symbol}...")
                    
                    # Enhanced rate limiting with exponential backoff on retries
                    delay = base_delay * (2 ** attempt) if attempt > 0 else base_delay
                    self._rate_limit_crypto(delay)
                    
                    # Get crypto ID mapping
                    crypto_id = self._get_crypto_id_mapping(crypto.symbol)
                    
                    # Calculate date range (last 30 days for initial load to respect free API limits)
                    start_date = date.today() - timedelta(days=30)
                    
                    # CoinGecko historical prices endpoint
                    url = f"{self.coingecko_base_url}/coins/{crypto_id}/market_chart"
                    
                    params = {
                        'vs_currency': 'usd',
                        'days': '30',  # Last 30 days
                        'interval': 'daily'
                    }
                    
                    # Add headers to look more like a browser
                    headers = {
                        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
                        'Accept': 'application/json',
                        'Accept-Language': 'en-US,en;q=0.9'
                    }
                    
                    response = requests.get(url, params=params, headers=headers, timeout=15)
                    
                    if response.status_code == 200:
                        data = response.json()
                        
                        if 'prices' in data and data['prices']:
                            prices = data['prices']
                            volumes = data.get('total_volumes', [])
                            
                            crypto_price_data = []
                            for i, price_point in enumerate(prices):
                                # price_point is [timestamp, price]
                                timestamp = price_point[0]
                                price = price_point[1]
                                volume = volumes[i][1] if i < len(volumes) else 0
                                
                                # Convert timestamp to date
                                price_date = datetime.fromtimestamp(timestamp / 1000).date()
                                
                                price_data = {
                                    'asset_id': crypto.id,
                                    'date': price_date,
                                    'open_price': float(price),  # CoinGecko gives us close price
                                    'high_price': float(price),  # Would need OHLC endpoint for true OHLC
                                    'low_price': float(price),
                                    'close_price': float(price),
                                    'adj_close': float(price),
                                    'volume': int(volume),
                                    'dividends': 0.0,
                                    'stock_splits': 0.0
                                }
                                crypto_price_data.append(price_data)
                            
                            all_price_data.extend(crypto_price_data)
                            successful_downloads += 1
                            self.logger.info(f"    ✅ Got {len(prices)} price records for {crypto.symbol}")
                            success = True
                            break
                        else:
                            self.logger.warning(f"    ⚠️ No price data in response for {crypto.symbol}")
                            break  # No point retrying if there's no data
                    
                    elif response.status_code == 429:
                        # Rate limited - exponential backoff
                        retry_delay = base_delay * (3 ** (attempt + 1))  # 6s, 18s, 54s
                        self.logger.warning(f"    ⚠️ Rate limited for {crypto.symbol}. Waiting {retry_delay:.1f}s before retry...")
                        time.sleep(retry_delay)
                        continue
                    
                    elif response.status_code == 404:
                        self.logger.warning(f"    ⚠️ Crypto ID '{crypto_id}' not found for {crypto.symbol}")
                        break  # No point retrying 404s
                    
                    else:
                        self.logger.warning(f"    ⚠️ API error for {crypto.symbol}: {response.status_code}")
                        if attempt < max_retries - 1:
                            time.sleep(delay)
                        continue
                
                except requests.exceptions.Timeout:
                    self.logger.warning(f"    ⚠️ Timeout for {crypto.symbol} (attempt {attempt + 1})")
                    if attempt < max_retries - 1:
                        time.sleep(base_delay * (2 ** attempt))
                    continue
                    
                except Exception as e:
                    self.logger.error(f"    ❌ Error downloading {crypto.symbol}: {str(e)}")
                    if attempt < max_retries - 1:
                        time.sleep(base_delay)
                    continue
            
            if not success:
                failed_cryptos.append(crypto.symbol)
        
        # Report results
        if failed_cryptos:
            self.logger.warning(f"⚠️ Failed to download prices for: {', '.join(failed_cryptos)}")
        
        self.logger.info(f"✅ Successfully downloaded prices for {successful_downloads}/{len(cryptos)} cryptocurrencies")
        return all_price_data
    
    def _rate_limit_crypto(self, delay: float = None):
        """Implement enhanced rate limiting for CoinGecko API."""
        current_time = time.time()
        time_since_last = current_time - self.last_crypto_request
        
        # Use custom delay or default rate limit
        min_delay = delay if delay is not None else self.crypto_rate_limit
        
        if time_since_last < min_delay:
            sleep_time = min_delay - time_since_last
            time.sleep(sleep_time)
        
        self.last_crypto_request = time.time()
    
    def _get_crypto_id_mapping(self, symbol: str) -> str:
        """Map crypto symbols to CoinGecko IDs."""
        # Common mappings for CoinGecko API
        symbol_map = {
            'bitcoin': 'bitcoin',
            'ethereum': 'ethereum', 
            'tether': 'tether',
            'binancecoin': 'binancecoin',
            'solana': 'solana',
            'usd-coin': 'usd-coin',
            'dogecoin': 'dogecoin',
            'tron': 'tron',
            'cardano': 'cardano',
            'chainlink': 'chainlink',
            'wrapped-bitcoin': 'wrapped-bitcoin',
            'avalanche-2': 'avalanche-2',
            'bitcoin-cash': 'bitcoin-cash',
            'litecoin': 'litecoin',
            'shiba-inu': 'shiba-inu',
            'polkadot': 'polkadot',
            'uniswap': 'uniswap',
            'dai': 'dai',
            'aave': 'aave',
            'pepe': 'pepe',
            'near': 'near',
            'arbitrum': 'arbitrum',
            'bonk': 'bonk',
            'optimism': 'optimism',
            'floki': 'floki',
            'frax': 'frax',
            'yearn-finance': 'yearn-finance',
            'compound-ether': 'compound-ether',
            'sushi': 'sushi',
            'loopring': 'loopring',
            'terrausd': 'terrausd',
            'matic-network': 'matic-network',
            'maker': 'maker'
        }
        
        # Try direct mapping first
        symbol_lower = symbol.lower()
        if symbol_lower in symbol_map:
            return symbol_map[symbol_lower]
        
        # Fallback: use symbol as-is
        return symbol_lower

    # ========================================
    # FUNCTION 5: CROSS-CHECK WITH DATABASE
    # ========================================
    
    def cross_check_prices(self, new_prices: List[Dict]) -> Tuple[List[Dict], List[Dict]]:
        """
        Cross-check downloaded prices with existing database records.
        
        Args:
            new_prices: List of price data dictionaries
            
        Returns:
            Tuple of (prices_to_add, prices_to_update)
        """
        self.logger.info(f"🔍 Cross-checking {len(new_prices)} price records with database...")
        
        db = self.get_db_session()
        
        prices_to_add = []
        prices_to_update = []
        
        # Group by asset_id for efficient querying
        prices_by_asset = {}
        for price in new_prices:
            asset_id = price['asset_id']
            if asset_id not in prices_by_asset:
                prices_by_asset[asset_id] = []
            prices_by_asset[asset_id].append(price)
        
        for asset_id, asset_prices in prices_by_asset.items():
            # Get existing prices for this asset
            existing_prices = db.query(DailyPrice).filter(
                DailyPrice.asset_id == asset_id
            ).all()
            
            existing_dates = {price.date: price for price in existing_prices}
            
            for new_price in asset_prices:
                price_date = new_price['date']
                
                if price_date in existing_dates:
                    # Price exists, check if update needed
                    existing_price = existing_dates[price_date]
                    
                    if self._price_needs_update(existing_price, new_price):
                        prices_to_update.append({
                            'existing': existing_price,
                            'new_data': new_price
                        })
                else:
                    # New price record
                    prices_to_add.append(new_price)
        
        self.logger.info(f"📊 Cross-check results:")
        self.logger.info(f"  - New price records to add: {len(prices_to_add)}")
        self.logger.info(f"  - Price records to update: {len(prices_to_update)}")
        
        return prices_to_add, prices_to_update
    
    def _price_needs_update(self, existing_price: DailyPrice, new_data: Dict) -> bool:
        """
        Check if existing price record needs update.
        
        Args:
            existing_price: Existing DailyPrice record
            new_data: New price data dictionary
            
        Returns:
            True if update needed, False otherwise
        """
        # Check if any price fields have changed significantly (more than 0.1% difference)
        price_fields = ['open_price', 'high_price', 'low_price', 'close_price', 'volume']
        
        for field in price_fields:
            if field in new_data:
                existing_value = getattr(existing_price, field, 0) or 0
                new_value = new_data[field] or 0
                
                if existing_value != 0:
                    percentage_diff = abs(existing_value - new_value) / existing_value
                    if percentage_diff > 0.001:  # 0.1% difference threshold
                        return True
                elif new_value != 0:
                    return True
        
        return False

    # ========================================
    # FUNCTION 6: ADD NEW PRICE RECORDS
    # ========================================
    
    def add_new_prices(self, prices_to_add: List[Dict]):
        """
        Add new price records to database.
        
        Args:
            prices_to_add: List of new price records to add
        """
        if not prices_to_add:
            self.logger.info("ℹ️ No new price records to add")
            return
        
        self.logger.info(f"➕ Adding {len(prices_to_add)} new price records...")
        
        db = self.get_db_session()
        added_count = 0
        batch_size = 1000  # Process in batches for better performance
        
        try:
            for i in range(0, len(prices_to_add), batch_size):
                batch = prices_to_add[i:i + batch_size]
                
                for price_data in batch:
                    new_price = DailyPrice(
                        asset_id=price_data['asset_id'],
                        date=price_data['date'],
                        open_price=price_data['open_price'],
                        high_price=price_data['high_price'],
                        low_price=price_data['low_price'],
                        close_price=price_data['close_price'],
                        adj_close=price_data['adj_close'],
                        volume=price_data['volume'],
                        dividends=price_data['dividends'],
                        stock_splits=price_data['stock_splits']
                    )
                    
                    db.add(new_price)
                    added_count += 1
                
                # Commit each batch
                db.commit()
                self.logger.info(f"  ✅ Added batch {i//batch_size + 1}: {len(batch)} records")
            
            self.logger.info(f"✅ Successfully added {added_count} new price records")
            
        except Exception as e:
            self.logger.error(f"❌ Error adding price records: {str(e)}")
            db.rollback()

    # ========================================
    # FUNCTION 7: MAIN ORCHESTRATOR
    # ========================================
    
    def sync_all_daily_prices(self):
        """
        Main function to sync all daily prices.
        Downloads historical prices for all asset types.
        """
        self.logger.info("🚀 Starting complete daily price synchronization...")
        
        try:
            db = self.get_db_session()
            
            # Get all assets from database
            stocks = db.query(Asset).filter(Asset.type == 'stock', Asset.is_active == True).all()
            mutual_funds = db.query(Asset).filter(Asset.type == 'mutual_fund', Asset.is_active == True).all()
            etfs = db.query(Asset).filter(Asset.type == 'etf', Asset.is_active == True).all()
            cryptos = db.query(Asset).filter(Asset.type == 'crypto', Asset.is_active == True).all()
            
            self.logger.info(f"📊 Found assets to process:")
            self.logger.info(f"  - Stocks: {len(stocks)}")
            self.logger.info(f"  - Mutual Funds: {len(mutual_funds)}")
            self.logger.info(f"  - ETFs: {len(etfs)}")
            self.logger.info(f"  - Cryptocurrencies: {len(cryptos)}")
            
            all_price_data = []
            
            # Download prices for each asset type
            if stocks:
                stock_prices = self.download_stock_prices(stocks)
                all_price_data.extend(stock_prices)
            
            if mutual_funds:
                mf_prices = self.download_mutual_fund_prices(mutual_funds)
                all_price_data.extend(mf_prices)
            
            if etfs:
                etf_prices = self.download_etf_prices(etfs)
                all_price_data.extend(etf_prices)
            
            if cryptos:
                crypto_prices = self.download_crypto_prices(cryptos)
                all_price_data.extend(crypto_prices)
            
            self.logger.info(f"📊 Total price records downloaded: {len(all_price_data)}")
            
            if not all_price_data:
                self.logger.warning("⚠️ No price data downloaded, aborting sync")
                return
            
            # Cross-check and add new prices
            prices_to_add, prices_to_update = self.cross_check_prices(all_price_data)
            
            # Add new price records
            self.add_new_prices(prices_to_add)
            
            # Summary
            self.logger.info("🎉 Daily price synchronization completed!")
            self.logger.info(f"📈 Summary:")
            self.logger.info(f"  - Total price records processed: {len(all_price_data)}")
            self.logger.info(f"  - New price records added: {len(prices_to_add)}")
            self.logger.info(f"  - Price records that could be updated: {len(prices_to_update)}")
            
        except Exception as e:
            self.logger.error(f"❌ Error in daily price synchronization: {str(e)}")
            raise
        
        finally:
            self.close_db_session()

    def sync_recent_prices_only(self, days: int = 7):
        """
        Sync only recent prices (last N days).
        Faster for daily updates.
        
        Args:
            days: Number of recent days to sync
        """
        self.logger.info(f"🚀 Starting recent price synchronization (last {days} days)...")
        
        try:
            db = self.get_db_session()
            
            # Get assets that need recent price updates
            cutoff_date = date.today() - timedelta(days=days)
            
            # Get assets that don't have recent prices
            assets_needing_update = db.query(Asset).filter(
                Asset.is_active == True,
                ~Asset.id.in_(
                    db.query(DailyPrice.asset_id).filter(
                        DailyPrice.date > cutoff_date
                    ).distinct()
                )
            ).all()
            
            self.logger.info(f"📊 Found {len(assets_needing_update)} assets needing recent price updates")
            
            # Group by type and process
            stocks = [a for a in assets_needing_update if a.type == 'stock']
            mutual_funds = [a for a in assets_needing_update if a.type == 'mutual_fund']
            etfs = [a for a in assets_needing_update if a.type == 'etf']
            cryptos = [a for a in assets_needing_update if a.type == 'crypto']
            
            all_price_data = []
            
            if stocks:
                stock_prices = self.download_stock_prices(stocks)
                all_price_data.extend(stock_prices)
            
            if etfs:
                etf_prices = self.download_etf_prices(etfs)
                all_price_data.extend(etf_prices)
            
            if cryptos:
                crypto_prices = self.download_crypto_prices(cryptos)
                all_price_data.extend(crypto_prices)
            
            # Add only new prices (no need to check for updates in recent sync)
            if all_price_data:
                prices_to_add, _ = self.cross_check_prices(all_price_data)
                self.add_new_prices(prices_to_add)
                
                self.logger.info(f"✅ Recent price sync completed: {len(prices_to_add)} new records added")
            else:
                self.logger.info("✅ All assets have recent price data")
            
        except Exception as e:
            self.logger.error(f"❌ Error in recent price synchronization: {str(e)}")
            raise
        
        finally:
            self.close_db_session()


# ========================================
# CONVENIENCE FUNCTIONS FOR EASY USE
# ========================================

def sync_all_daily_prices():
    """Easy function to sync all historical daily prices."""
    collector = DailyPriceCollector()
    collector.sync_all_daily_prices()

def sync_recent_prices(days: int = 7):
    """Easy function to sync recent daily prices only."""
    collector = DailyPriceCollector()
    collector.sync_recent_prices_only(days)

def sync_stock_prices_only():
    """Sync only stock prices."""
    collector = DailyPriceCollector()
    db = collector.get_db_session()
    
    stocks = db.query(Asset).filter(Asset.type == 'stock', Asset.is_active == True).all()
    stock_prices = collector.download_stock_prices(stocks)
    
    if stock_prices:
        prices_to_add, _ = collector.cross_check_prices(stock_prices)
        collector.add_new_prices(prices_to_add)
    
    collector.close_db_session()

def sync_crypto_prices_only():
    """Sync only crypto prices."""
    collector = DailyPriceCollector()
    db = collector.get_db_session()
    
    cryptos = db.query(Asset).filter(Asset.type == 'crypto', Asset.is_active == True).all()
    crypto_prices = collector.download_crypto_prices(cryptos)
    
    if crypto_prices:
        prices_to_add, _ = collector.cross_check_prices(crypto_prices)
        collector.add_new_prices(prices_to_add)
    
    collector.close_db_session()


# ========================================
# MAIN EXECUTION
# ========================================

if __name__ == "__main__":
    print("📈 Lumia Daily Price Collector")
    print("=" * 50)
    
    # Choose your collection method:
    
    # Option 1: Sync all historical prices (comprehensive but slower)
    # sync_all_daily_prices()
    
    # Option 2: Sync only recent prices (faster for daily updates)
    sync_recent_prices(days=7)
    
    # Option 3: Sync specific asset types only
    # sync_stock_prices_only()
    # sync_crypto_prices_only()