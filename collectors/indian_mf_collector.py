#!/usr/bin/env python3
"""
Indian Mutual Fund Price Collector
Collects NAV (Net Asset Value) data for Indian mutual funds using AMFI API

AMFI (Association of Mutual Funds in India) provides daily NAV data for all Indian mutual funds.

Author: Lumia Team
"""

import requests
import pandas as pd
import sys
import os
from datetime import datetime, date, timedelta
from typing import List, Dict, Optional
import time
import re

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from models.assets import Asset
from models.daily_price import DailyPrice
from database import get_db
from utils.logging_config import setup_unicode_logging

class IndianMutualFundCollector:
    """
    Collector for Indian Mutual Fund NAV data using AMFI and MFApi.
    
    Data Sources:
    1. AMFI (Primary): https://www.amfiindia.com/spages/NAVAll.txt
    2. MFApi (Backup): https://api.mfapi.in/mf/{scheme_code}
    """
    
    def __init__(self):
        self.logger = self._setup_logger()
        self.db = None
        
        # AMFI URLs
        self.amfi_url = "https://www.amfiindia.com/spages/NAVAll.txt"
        self.amfi_historical_url = "https://portal.amfiindia.com/DownloadNAVHistoryReport_Po.aspx"
        
        # MFApi URLs (Backup)
        self.mfapi_base_url = "https://api.mfapi.in/mf"
        
        # Rate limiting
        self.request_delay = 0.5  # 500ms between requests
        self.last_request_time = 0
    
    def _setup_logger(self):
        """Setup logging"""
        return setup_unicode_logging(
            "lumia.indian_mf_collector",
            level='INFO',
            console=True
        )
    
    def get_db_session(self):
        """Get database session"""
        if not self.db:
            self.db = next(get_db())
        return self.db
    
    def close_db_session(self):
        """Close database session"""
        if self.db:
            self.db.close()
            self.db = None
    
    def _rate_limit(self):
        """Implement rate limiting"""
        current_time = time.time()
        time_since_last = current_time - self.last_request_time
        
        if time_since_last < self.request_delay:
            time.sleep(self.request_delay - time_since_last)
        
        self.last_request_time = time.time()
    
    def _extract_scheme_code(self, symbol: str) -> Optional[str]:
        """
        Extract AMFI scheme code from symbol.
        
        Args:
            symbol: Asset symbol (e.g., "IN-MF-142812" or "142812")
            
        Returns:
            Scheme code as string or None
        """
        if not symbol:
            return None
        
        # Pattern: IN-MF-XXXXXX or just XXXXXX
        match = re.search(r'(\d{6})', symbol)
        if match:
            return match.group(1)
        
        return None
    
    def fetch_latest_nav_from_amfi(self) -> Dict[str, Dict]:
        """
        Fetch latest NAV for all mutual funds from AMFI.
        
        Returns:
            Dictionary mapping scheme_code -> {date, nav, name}
        """
        self.logger.info("[AMFI] Fetching latest NAV data from AMFI...")
        
        try:
            self._rate_limit()
            response = requests.get(self.amfi_url, timeout=30)
            response.raise_for_status()
            
            # Parse the text file
            lines = response.text.split('\n')
            
            nav_data = {}
            
            for line in lines:
                line = line.strip()
                
                # Skip empty lines and headers
                if not line or 'Scheme Code' in line or 'Scheme Name' in line:
                    continue
                
                # Skip section headers (like "Open Ended Schemes...")
                if not ';' in line:
                    continue
                
                # Parse NAV line: Scheme Code;ISIN;ISIN;Scheme Name;NAV;Date
                parts = line.split(';')
                
                if len(parts) >= 6:
                    scheme_code = parts[0].strip()
                    scheme_name = parts[3].strip()
                    nav_str = parts[4].strip()
                    date_str = parts[5].strip()
                    
                    # Skip if not a valid scheme code (must be numeric)
                    if not scheme_code.isdigit():
                        continue
                    
                    try:
                        nav = float(nav_str)
                        # Parse date in format: 07-Oct-2025
                        nav_date = datetime.strptime(date_str, '%d-%b-%Y').date()
                        
                        nav_data[scheme_code] = {
                            'date': nav_date,
                            'nav': nav,
                            'name': scheme_name
                        }
                    except (ValueError, IndexError):
                        continue
            
            self.logger.info(f"[AMFI] Successfully parsed {len(nav_data):,} mutual fund NAVs")
            return nav_data
            
        except Exception as e:
            self.logger.error(f"[AMFI] Error fetching data: {str(e)}")
            return {}
    
    def fetch_historical_nav_from_mfapi(self, scheme_code: str, from_date: date = None) -> List[Dict]:
        """
        Fetch historical NAV data from MFApi.
        
        Args:
            scheme_code: AMFI scheme code (e.g., "142812")
            from_date: Start date for historical data
            
        Returns:
            List of {date, nav} dictionaries
        """
        try:
            self._rate_limit()
            url = f"{self.mfapi_base_url}/{scheme_code}"
            response = requests.get(url, timeout=15)
            response.raise_for_status()
            
            data = response.json()
            
            if data.get('status') != 'SUCCESS':
                return []
            
            # Parse historical data
            historical_data = []
            nav_history = data.get('data', [])
            
            for entry in nav_history:
                try:
                    nav_date = datetime.strptime(entry['date'], '%d-%m-%Y').date()
                    nav_value = float(entry['nav'])
                    
                    # Filter by from_date if provided
                    if from_date and nav_date < from_date:
                        continue
                    
                    historical_data.append({
                        'date': nav_date,
                        'nav': nav_value
                    })
                except (KeyError, ValueError):
                    continue
            
            return historical_data
            
        except Exception as e:
            self.logger.warning(f"[MFApi] Error fetching {scheme_code}: {str(e)}")
            return []
    
    def download_indian_mf_prices(
        self, 
        funds: List[Asset], 
        from_date: str = None, 
        to_date: str = None,
        use_latest_only: bool = False
    ) -> List[Dict]:
        """
        Download NAV data for Indian mutual funds.
        
        Args:
            funds: List of Indian mutual fund Asset objects
            from_date: Start date (YYYY-MM-DD)
            to_date: End date (YYYY-MM-DD)
            use_latest_only: If True, only fetch latest NAV from AMFI
            
        Returns:
            List of price data dictionaries
        """
        self.logger.info(f"[INDIAN MF] Downloading NAV data for {len(funds)} Indian mutual funds...")
        
        # Determine date range
        if from_date and to_date:
            start_date = datetime.strptime(from_date, '%Y-%m-%d').date()
            end_date = datetime.strptime(to_date, '%Y-%m-%d').date()
            self.logger.info(f"[DATE] Range: {start_date} to {end_date}")
        else:
            start_date = date.today() - timedelta(days=25*365)  # 25 years
            end_date = date.today()
            self.logger.info(f"[DATE] Default range: {start_date} to {end_date} (25 years)")
        
        all_price_data = []
        successful_downloads = 0
        
        # Strategy 1: Fetch latest NAV from AMFI (fast)
        if use_latest_only:
            self.logger.info("[STRATEGY] Using AMFI latest NAV only...")
            latest_navs = self.fetch_latest_nav_from_amfi()
            
            for fund in funds:
                scheme_code = self._extract_scheme_code(fund.symbol)
                
                if not scheme_code:
                    self.logger.warning(f"  ⚠️ Invalid symbol format: {fund.symbol}")
                    continue
                
                if scheme_code in latest_navs:
                    nav_data = latest_navs[scheme_code]
                    
                    price_data = {
                        'asset_id': fund.id,
                        'date': nav_data['date'],
                        'open_price': nav_data['nav'],
                        'high_price': nav_data['nav'],
                        'low_price': nav_data['nav'],
                        'close_price': nav_data['nav'],
                        'adj_close': nav_data['nav'],
                        'volume': 0,  # Not applicable for mutual funds
                        'dividends': 0.0,
                        'stock_splits': 0.0
                    }
                    
                    all_price_data.append(price_data)
                    successful_downloads += 1
                    self.logger.info(f"  ✅ {fund.symbol}: NAV {nav_data['nav']} on {nav_data['date']}")
                else:
                    self.logger.warning(f"  ⚠️ No NAV found for {fund.symbol} (code: {scheme_code})")
        
        # Strategy 2: Fetch historical data from MFApi (slower but comprehensive)
        else:
            self.logger.info("[STRATEGY] Using MFApi for historical NAV...")
            
            for i, fund in enumerate(funds, 1):
                scheme_code = self._extract_scheme_code(fund.symbol)
                
                if not scheme_code:
                    self.logger.warning(f"  ⚠️ [{i}/{len(funds)}] Invalid symbol: {fund.symbol}")
                    continue
                
                self.logger.info(f"  [{i}/{len(funds)}] Fetching {fund.symbol} (code: {scheme_code})...")
                
                # Fetch historical data
                historical_navs = self.fetch_historical_nav_from_mfapi(scheme_code, start_date)
                
                if historical_navs:
                    for nav_entry in historical_navs:
                        # Filter by date range
                        if nav_entry['date'] < start_date or nav_entry['date'] > end_date:
                            continue
                        
                        price_data = {
                            'asset_id': fund.id,
                            'date': nav_entry['date'],
                            'open_price': nav_entry['nav'],
                            'high_price': nav_entry['nav'],
                            'low_price': nav_entry['nav'],
                            'close_price': nav_entry['nav'],
                            'adj_close': nav_entry['nav'],
                            'volume': 0,
                            'dividends': 0.0,
                            'stock_splits': 0.0
                        }
                        
                        all_price_data.append(price_data)
                    
                    successful_downloads += 1
                    self.logger.info(f"    ✅ Got {len(historical_navs)} NAV records")
                else:
                    self.logger.warning(f"    ⚠️ No historical data found")
                
                # Progress update every 100 funds
                if i % 100 == 0:
                    self.logger.info(f"  [PROGRESS] {i}/{len(funds)} funds processed ({successful_downloads} successful)")
        
        self.logger.info(f"[SUCCESS] Downloaded NAV data for {successful_downloads}/{len(funds)} mutual funds")
        self.logger.info(f"[TOTAL] {len(all_price_data):,} NAV records collected")
        
        return all_price_data
    
    def sync_indian_mf_prices(self, latest_only: bool = False):
        """
        Main function to sync Indian mutual fund prices.
        
        Args:
            latest_only: If True, only fetch latest NAV (faster)
        """
        self.logger.info("🚀 Starting Indian Mutual Fund NAV synchronization...")
        
        try:
            db = self.get_db_session()
            
            # Get all Indian mutual funds
            indian_funds = db.query(Asset).filter(
                Asset.type == 'mutual_fund',
                Asset.symbol.like('IN-MF-%'),
                Asset.is_active == True
            ).all()
            
            self.logger.info(f"📊 Found {len(indian_funds):,} Indian mutual funds")
            
            if not indian_funds:
                self.logger.warning("⚠️ No Indian mutual funds found in database")
                return
            
            # Download NAV data
            nav_data = self.download_indian_mf_prices(
                indian_funds,
                use_latest_only=latest_only
            )
            
            if not nav_data:
                self.logger.warning("⚠️ No NAV data downloaded")
                return
            
            # Import price collector to reuse cross-check and add functions
            from collectors.daily_price_collector import DailyPriceCollector
            price_collector = DailyPriceCollector()
            
            # Cross-check and add prices
            prices_to_add, _ = price_collector.cross_check_prices(nav_data)
            price_collector.add_new_prices(prices_to_add)
            
            # Summary
            self.logger.info("🎉 Indian Mutual Fund NAV sync completed!")
            self.logger.info(f"📊 Total NAV records: {len(nav_data):,}")
            self.logger.info(f"📈 New records added: {len(prices_to_add):,}")
            
        except Exception as e:
            self.logger.error(f"❌ Error syncing Indian MF prices: {str(e)}")
            raise
        finally:
            self.close_db_session()


# Convenience functions
def sync_indian_mf_latest():
    """Quick function to sync latest NAV only (fast)"""
    collector = IndianMutualFundCollector()
    collector.sync_indian_mf_prices(latest_only=True)

def sync_indian_mf_historical():
    """Sync full historical NAV data (slow but comprehensive)"""
    collector = IndianMutualFundCollector()
    collector.sync_indian_mf_prices(latest_only=False)


if __name__ == "__main__":
    print("💼 Indian Mutual Fund NAV Collector")
    print("=" * 60)
    
    import argparse
    parser = argparse.ArgumentParser(description='Collect Indian Mutual Fund NAV data')
    parser.add_argument('--latest-only', action='store_true', 
                       help='Only fetch latest NAV (faster)')
    parser.add_argument('--historical', action='store_true',
                       help='Fetch full historical data (slower)')
    
    args = parser.parse_args()
    
    collector = IndianMutualFundCollector()
    
    if args.historical:
        print("\n📊 Fetching HISTORICAL NAV data (may take 1-2 hours)...")
        collector.sync_indian_mf_prices(latest_only=False)
    else:
        print("\n📊 Fetching LATEST NAV data only (fast)...")
        collector.sync_indian_mf_prices(latest_only=True)
