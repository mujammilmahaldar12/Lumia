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
import sys
import os

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import our models
from models.assets import Asset
from models.daily_price import DailyPrice
from database import get_db
from utils.logging_config import setup_unicode_logging


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
        """Setup Unicode-safe logging for the price collector."""
        return setup_unicode_logging(
            "lumia.daily_price_collector",
            level='INFO',
            console=True
        )
    
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
    
    def download_stock_prices_progressive(self, stocks: List[Asset], from_date: str = None, to_date: str = None, batch_size: int = 50) -> Dict:
        """
        Download historical stock price data with progressive database commits.
        
        Args:
            stocks: List of stock Asset objects
            from_date: Start date for price collection (YYYY-MM-DD format)
            to_date: End date for price collection (YYYY-MM-DD format)
            batch_size: Number of stocks to process before committing to database
            
        Returns:
            Dictionary with collection results
        """
        self.logger.info(f"[PRICES] Downloading price data for {len(stocks)} stocks (progressive mode)...")
        
        total_processed = 0
        total_added = 0
        total_failed = 0
        
        # Determine date range
        if from_date and to_date:
            start_date = datetime.strptime(from_date, '%Y-%m-%d').date()
            end_date = datetime.strptime(to_date, '%Y-%m-%d').date()
            self.logger.info(f"[DATE] Using specified date range: {start_date} to {end_date}")
        else:
            # Use default range - 25 years of history
            start_date = date.today() - timedelta(days=25*365)  # 25 years
            end_date = date.today()
            self.logger.info(f"[DATE] Using default date range: {start_date} to {end_date} (25 years)")
        
        # Process stocks in batches
        for i in range(0, len(stocks), batch_size):
            batch = stocks[i:i + batch_size]
            batch_price_data = []
            
            self.logger.info(f"[BATCH] Processing batch {i//batch_size + 1}/{(len(stocks) + batch_size - 1)//batch_size} ({len(batch)} stocks)...")
            
            for stock in batch:
                try:
                    self.logger.info(f"  Fetching prices for {stock.symbol}...")
                    
                    # For historical data collection, always use the requested start date
                    actual_start_date = start_date
                    
                    # Download using yfinance
                    ticker = yf.Ticker(stock.symbol)
                    hist = ticker.history(start=actual_start_date, end=end_date)
                    
                    if not hist.empty:
                        # Convert to our format
                        stock_prices = []
                        for date_idx, row in hist.iterrows():
                            price_data = {
                                'asset_id': stock.id,
                                'date': date_idx.date(),
                                'open_price': float(row['Open']),
                                'high_price': float(row['High']),
                                'low_price': float(row['Low']),
                                'close_price': float(row['Close']),
                                'adj_close': float(row.get('Adj Close', row['Close'])),  # Use Close if Adj Close not available
                                'volume': int(row['Volume']),
                                'dividends': float(row.get('Dividends', 0.0)),
                                'stock_splits': float(row.get('Stock Splits', 0.0))
                            }
                            stock_prices.append(price_data)
                        
                        batch_price_data.extend(stock_prices)
                        self.logger.info(f"    [SUCCESS] Got {len(stock_prices)} price records for {stock.symbol}")
                        total_processed += 1
                        
                    else:
                        self.logger.warning(f"    [WARNING] No price data for {stock.symbol}")
                        total_failed += 1
                        
                except Exception as e:
                    self.logger.warning(f"    [ERROR] Failed to download {stock.symbol}: {str(e)}")
                    total_failed += 1
            
            # Process and save this batch immediately
            if batch_price_data:
                self.logger.info(f"[COMMIT] Processing {len(batch_price_data)} price records for batch...")
                prices_to_add, _ = self.cross_check_prices(batch_price_data)
                
                if prices_to_add:
                    self.add_new_prices(prices_to_add)
                    total_added += len(prices_to_add)
                    self.logger.info(f"[COMMIT] ✅ Saved {len(prices_to_add)} new price records to database")
                else:
                    self.logger.info(f"[COMMIT] No new prices to add for this batch")
            
            # Progress update
            progress = ((i + len(batch)) / len(stocks)) * 100
            self.logger.info(f"[PROGRESS] {progress:.1f}% complete ({i + len(batch)}/{len(stocks)} stocks processed)")
        
        return {
            'total': total_processed,
            'success': total_processed,
            'failed': total_failed,
            'records_added': total_added
        }

    def download_stock_prices(self, stocks: List[Asset], from_date: str = None, to_date: str = None) -> Dict:
        """
        Download historical stock price data using yfinance.
        
        Args:
            stocks: List of stock Asset objects
            from_date: Start date for price collection (YYYY-MM-DD format)
            to_date: End date for price collection (YYYY-MM-DD format)
            
        Returns:
            Dictionary with collection results and price data list
        """
        self.logger.info(f"[PRICES] Downloading price data for {len(stocks)} stocks...")
        
        all_price_data = []
        successful_downloads = 0
        failed_downloads = 0
        
        # Determine date range
        if from_date and to_date:
            start_date = datetime.strptime(from_date, '%Y-%m-%d').date()
            end_date = datetime.strptime(to_date, '%Y-%m-%d').date()
            self.logger.info(f"[DATE] Using specified date range: {start_date} to {end_date}")
        else:
            # Use default range - 25 years of history
            start_date = date.today() - timedelta(days=25*365)  # 25 years
            end_date = date.today()
            self.logger.info(f"[DATE] Using default date range: {start_date} to {end_date} (25 years)")
        
        for stock in stocks:
            try:
                self.logger.info(f"  Fetching prices for {stock.symbol}...")
                
                # For historical data collection, always use the requested start date
                # Asset creation date is irrelevant for historical price data
                actual_start_date = start_date
                
                # Download using yfinance
                ticker = yf.Ticker(stock.symbol)
                hist = ticker.history(start=actual_start_date, end=end_date)
                
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
                    self.logger.info(f"    [SUCCESS] Got {len(hist)} price records for {stock.symbol}")
                else:
                    self.logger.warning(f"    [WARNING] No price data for {stock.symbol}")
                    failed_downloads += 1
                
                # Small delay to respect API limits
                time.sleep(0.1)
                
            except Exception as e:
                self.logger.error(f"    [ERROR] Error downloading {stock.symbol}: {str(e)}")
                failed_downloads += 1
                continue
        
        self.logger.info(f"[SUCCESS] Successfully downloaded prices for {successful_downloads}/{len(stocks)} stocks")
        
        return {
            'price_data': all_price_data,
            'total': len(stocks),
            'success': successful_downloads,
            'failed': failed_downloads,
            'records_count': len(all_price_data)
        }
    
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
        self.logger.info(f"[MUTUAL FUNDS] Downloading price data for {len(mutual_funds)} mutual funds...")
        
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
                        self.logger.info(f"    [SUCCESS] Got {len(hist)} price records for {fund.symbol}")
                    else:
                        self.logger.warning(f"    [WARNING] No price data for {fund.symbol}")
                
                else:
                    # Indian mutual funds - would need AMFI NAV data
                    # For now, we'll skip but this can be implemented with AMFI API
                    self.logger.info(f"    [INFO] Indian MF price collection not implemented yet: {fund.symbol}")
                
                time.sleep(0.1)
                
            except Exception as e:
                self.logger.error(f"    [ERROR] Error downloading {fund.symbol}: {str(e)}")
                continue
        
        self.logger.info(f"[SUCCESS] Successfully downloaded prices for {successful_downloads}/{len(mutual_funds)} mutual funds")
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
        self.logger.info(f"[ETFS] Downloading price data for {len(etfs)} ETFs...")
        
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
                    self.logger.info(f"    [SUCCESS] Got {len(hist)} price records for {etf.symbol}")
                else:
                    self.logger.warning(f"    [WARNING] No price data for {etf.symbol}")
                
                time.sleep(0.1)
                
            except Exception as e:
                self.logger.error(f"    [ERROR] Error downloading {etf.symbol}: {str(e)}")
                continue
        
        self.logger.info(f"[SUCCESS] Successfully downloaded prices for {successful_downloads}/{len(etfs)} ETFs")
        return all_price_data
    
    # ========================================
    # FUNCTION 4: DOWNLOAD CRYPTO PRICES
    # ========================================
    
    def download_crypto_prices(self, cryptos: List[Asset], from_date: str = None, to_date: str = None) -> Dict:
        """
        Download historical cryptocurrency price data using CoinGecko.
        
        Args:
            cryptos: List of crypto Asset objects
            from_date: Start date for price collection (YYYY-MM-DD format)
            to_date: End date for price collection (YYYY-MM-DD format)
            
        Returns:
            Dictionary with collection results and price data
        """
        self.logger.info(f"[CRYPTO] Downloading price data for {len(cryptos)} cryptocurrencies...")
        
        all_price_data = []
        successful_downloads = 0
        failed_cryptos = []
        
        # Determine date range and API parameters
        if from_date and to_date:
            start_date = datetime.strptime(from_date, '%Y-%m-%d').date()
            end_date = datetime.strptime(to_date, '%Y-%m-%d').date()
            days_requested = (end_date - start_date).days
            self.logger.info(f"[DATE] Using specified date range: {start_date} to {end_date} ({days_requested} days)")
        else:
            # Default: last 30 days for API limits
            start_date = date.today() - timedelta(days=30)
            end_date = date.today()
            days_requested = 30
            self.logger.info(f"[DATE] Using default range: {start_date} to {end_date} (30 days)")
        
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
                    
                    # CoinGecko historical prices endpoint
                    url = f"{self.coingecko_base_url}/coins/{crypto_id}/market_chart"
                    
                    # Use smart days parameter based on date range
                    if days_requested <= 1:
                        interval = 'hourly'
                        days_param = '1'
                    elif days_requested <= 90:
                        interval = 'daily'
                        days_param = str(min(days_requested, 90))  # CoinGecko free limit
                    else:
                        interval = 'daily'
                        days_param = '90'  # Maximum for free API
                    
                    params = {
                        'vs_currency': 'usd',
                        'days': days_param,
                        'interval': interval
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
                            self.logger.info(f"    [SUCCESS] Got {len(prices)} price records for {crypto.symbol}")
                            success = True
                            break
                        else:
                            self.logger.warning(f"    [WARNING] No price data in response for {crypto.symbol}")
                            break  # No point retrying if there's no data
                    
                    elif response.status_code == 429:
                        # Rate limited - exponential backoff
                        retry_delay = base_delay * (3 ** (attempt + 1))  # 6s, 18s, 54s
                        self.logger.warning(f"    [WARNING] Rate limited for {crypto.symbol}. Waiting {retry_delay:.1f}s before retry...")
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
        
        return {
            'price_data': all_price_data,
            'total': len(cryptos),
            'success': successful_downloads,
            'failed': len(failed_cryptos),
            'failed_symbols': failed_cryptos,
            'records_count': len(all_price_data)
        }
    
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
        self.logger.info(f"[SEARCH] Cross-checking {len(new_prices)} price records with database...")
        
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
        
        self.logger.info(f"[RESULTS] Cross-check results:")
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
        Add new price records to database with duplicate handling.
        
        Args:
            prices_to_add: List of new price records to add
        """
        if not prices_to_add:
            self.logger.info("ℹ️ No new price records to add")
            return
        
        self.logger.info(f"[ADD] Adding {len(prices_to_add)} new price records with duplicate protection...")
        
        db = self.get_db_session()
        total_inserted = 0
        batch_size = 1000  # Process in batches for better performance
        
        # Import text for SQL execution
        from sqlalchemy import text
        
        try:
            for i in range(0, len(prices_to_add), batch_size):
                batch = prices_to_add[i:i + batch_size]
                
                try:
                    # Prepare batch data for PostgreSQL array format
                    asset_ids = [price_data['asset_id'] for price_data in batch]
                    dates = [price_data['date'] for price_data in batch]
                    open_prices = [float(price_data['open_price']) for price_data in batch]
                    high_prices = [float(price_data['high_price']) for price_data in batch]
                    low_prices = [float(price_data['low_price']) for price_data in batch]
                    close_prices = [float(price_data['close_price']) for price_data in batch]
                    adj_closes = [float(price_data['adj_close']) for price_data in batch]
                    volumes = [int(price_data['volume']) for price_data in batch]
                    dividends = [float(price_data['dividends']) for price_data in batch]
                    stock_splits = [float(price_data['stock_splits']) for price_data in batch]
                    
                    # Use our batch insert function that handles duplicates
                    result = db.execute(text("""
                        SELECT batch_insert_daily_prices(
                            :asset_ids, :dates, :open_prices, :high_prices, :low_prices,
                            :close_prices, :adj_closes, :volumes, :dividends, :stock_splits
                        )
                    """), {
                        'asset_ids': asset_ids,
                        'dates': dates,
                        'open_prices': open_prices,
                        'high_prices': high_prices,
                        'low_prices': low_prices,
                        'close_prices': close_prices,
                        'adj_closes': adj_closes,
                        'volumes': volumes,
                        'dividends': dividends,
                        'stock_splits': stock_splits
                    })
                    
                    batch_inserted = result.scalar()
                    total_inserted += batch_inserted
                    
                    db.commit()
                    
                    self.logger.info(f"  [BATCH {i//batch_size + 1}] Inserted {batch_inserted}/{len(batch)} records (duplicates skipped)")
                    
                except Exception as batch_error:
                    db.rollback()
                    self.logger.warning(f"[BATCH {i//batch_size + 1}] Batch insert failed: {batch_error}")
                    
                    # Fall back to individual inserts for this batch
                    batch_fallback_inserted = 0
                    for price_data in batch:
                        try:
                            result = db.execute(text("""
                                SELECT upsert_daily_prices(
                                    :asset_id, :date, :open_price, :high_price, :low_price,
                                    :close_price, :adj_close, :volume, :dividends, :stock_splits
                                )
                            """), {
                                'asset_id': price_data['asset_id'],
                                'date': price_data['date'],
                                'open_price': float(price_data['open_price']),
                                'high_price': float(price_data['high_price']),
                                'low_price': float(price_data['low_price']),
                                'close_price': float(price_data['close_price']),
                                'adj_close': float(price_data['adj_close']),
                                'volume': int(price_data['volume']),
                                'dividends': float(price_data['dividends']),
                                'stock_splits': float(price_data['stock_splits'])
                            })
                            db.commit()
                            batch_fallback_inserted += 1
                            
                        except Exception as individual_error:
                            db.rollback()
                            self.logger.debug(f"[SKIP] Failed to insert {price_data['asset_id']}:{price_data['date']} - {individual_error}")
                    
                    total_inserted += batch_fallback_inserted
                    self.logger.info(f"  [FALLBACK] Individually inserted {batch_fallback_inserted}/{len(batch)} records")
            
            self.logger.info(f"[SUCCESS] Successfully inserted {total_inserted}/{len(prices_to_add)} new price records (duplicates gracefully handled)")
            
        except Exception as e:
            self.logger.error(f"❌ Critical error adding price records: {str(e)}")
            db.rollback()

    # ========================================
    # FUNCTION 7: MAIN ORCHESTRATOR
    # ========================================
    
    def sync_prices_with_date_range(self, from_date: str, to_date: str) -> Dict:
        """
        Intelligent price synchronization with specific date range.
        Used by smart collector for optimized data collection.
        
        Args:
            from_date: Start date (YYYY-MM-DD)
            to_date: End date (YYYY-MM-DD)
            
        Returns:
            Dictionary with detailed collection results
        """
        self.logger.info(f"🧠 Starting intelligent price sync: {from_date} to {to_date}")
        
        try:
            db = self.get_db_session()
            
            # Get active assets
            stocks = db.query(Asset).filter(Asset.type == 'stock', Asset.is_active == True).all()
            cryptos = db.query(Asset).filter(Asset.type == 'crypto', Asset.is_active == True).all()
            etfs = db.query(Asset).filter(Asset.type == 'etf', Asset.is_active == True).all()
            
            self.logger.info(f"📊 Assets to process: {len(stocks)} stocks, {len(cryptos)} cryptos, {len(etfs)} ETFs")
            
            all_results = {
                'total_processed': 0,
                'total_added': 0,
                'total_failed': 0,
                'by_type': {}
            }
            
            # Process each asset type with progressive commits
            if stocks:
                self.logger.info("📈 Processing stocks with progressive commits...")
                stock_result = self.download_stock_prices_progressive(stocks, from_date, to_date, batch_size=50)
                
                all_results['by_type']['stocks'] = stock_result
                all_results['total_processed'] += stock_result['total']
                all_results['total_added'] += stock_result.get('records_added', 0)
                all_results['total_failed'] += stock_result['failed']
            
            if cryptos:
                self.logger.info("[CRYPTO] Processing cryptocurrencies with date range...")
                crypto_result = self.download_crypto_prices(cryptos, from_date, to_date)
                
                if crypto_result['price_data']:
                    prices_to_add, _ = self.cross_check_prices(crypto_result['price_data'])
                    self.add_new_prices(prices_to_add)
                    
                all_results['by_type']['crypto'] = crypto_result
                all_results['total_processed'] += crypto_result['total']
                all_results['total_added'] += len(prices_to_add) if 'prices_to_add' in locals() else 0
                all_results['total_failed'] += crypto_result['failed']
            
            if etfs:
                self.logger.info("📊 Processing ETFs with date range...")
                etf_result = self.download_etf_prices(etfs)  # ETF method doesn't have date params yet
                
                if etf_result:
                    prices_to_add, _ = self.cross_check_prices(etf_result)
                    self.add_new_prices(prices_to_add)
            
            self.logger.info(f"🎉 Intelligent price sync completed!")
            self.logger.info(f"📊 Total: {all_results['total_processed']} processed, {all_results['total_added']} added")
            
            return all_results
            
        except Exception as e:
            self.logger.error(f"❌ Error in intelligent price sync: {str(e)}")
            raise
        finally:
            self.close_db_session()

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
                result = self.download_stock_prices(stocks)
                all_price_data.extend(result['price_data'])
            
            if etfs:
                etf_prices = self.download_etf_prices(etfs)  # Returns list directly
                all_price_data.extend(etf_prices)
            
            if cryptos:
                result = self.download_crypto_prices(cryptos)
                all_price_data.extend(result['price_data'])
            
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
