"""
ETF Manager - Fetches Exchange Traded Fund information from various sources.
Handles Indian ETFs (NSE/BSE) and US ETFs (major exchanges).

Similar pattern to stocks_manager.py and mutual_fund_manager.py but specialized for ETFs.
"""

import requests
import pandas as pd
import yfinance as yf
from datetime import datetime, date
from typing import List, Dict, Tuple, Optional
import logging
from sqlalchemy.orm import Session
from sqlalchemy import and_

# Import our models
from models.assets import Asset
from database import get_db


class ETFManager:
    """
    Complete ETF management system.
    Handles downloading, cross-checking, updating ETF data from multiple sources.
    """
    
    def __init__(self):
        self.logger = self._setup_logger()
        self.db = None
        
        # Popular US ETFs from major providers
        self.us_etf_symbols = [
            # SPDR ETFs
            "SPY", "XLF", "XLE", "XLK", "XLV", "XLI", "XLP", "XLU", "XLB", "XLRE",
            # Vanguard ETFs
            "VTI", "VEA", "VWO", "BND", "VNQ", "VGT", "VHT", "VFH", "VDC", "VDE",
            # iShares ETFs
            "IWM", "EFA", "EEM", "AGG", "QQQ", "IYR", "IJR", "IJH", "IVV", "IVW",
            # Invesco ETFs
            "QQQ", "ARKK", "ARKQ", "ARKW", "ARKG", "ARKF",
            # Sector ETFs
            "GLD", "SLV", "USO", "TLT", "HYG", "LQD", "IEMG", "VGK", "VPL"
        ]
        
        # Indian ETFs (NSE symbols)
        self.indian_etf_symbols = [
            # Nifty ETFs
            "NIFTYBEES.NS", "JUNIORBEES.NS", "BANKBEES.NS", "ITBEES.NS",
            # Gold ETFs
            "GOLDSHARE.NS", "GOLDBEES.NS", "GOLDCASE.NS",
            # Other popular Indian ETFs
            "CPSEETF.NS", "INFRABEES.NS", "PSUBNKBEES.NS", "PHARMABEES.NS",
            "FMCGBEES.NS", "PVTBNKBEES.NS", "AUTOBEES.NS", "METALBEES.NS"
        ]
    
    def _setup_logger(self):
        """Setup logging for ETF manager."""
        logger = logging.getLogger("lumia.etf_manager")
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
    # FUNCTION 1: DOWNLOAD ETF LISTS
    # ========================================
    
    def download_us_etfs(self) -> List[Dict]:
        """
        Download US ETF data using yfinance.
        Uses predefined list of popular US ETFs.
        
        Returns:
            List of US ETF dictionaries
        """
        self.logger.info(f"📥 Getting data for {len(self.us_etf_symbols)} US ETFs...")
        
        us_etfs = []
        
        for symbol in self.us_etf_symbols:
            try:
                self.logger.info(f"  Fetching {symbol}...")
                
                # Get ETF info from yfinance
                ticker = yf.Ticker(symbol)
                info = ticker.info
                
                if info and 'shortName' in info:
                    etf_data = {
                        'symbol': symbol,
                        'name': info.get('shortName', info.get('longName', 'Unknown')),
                        'type': 'etf',
                        'subtype': self._classify_us_etf_type(symbol, info),
                        'exchange': self._get_us_exchange(info),
                        'country': 'US',
                        'currency': 'USD',
                        'sector': self._get_etf_sector(symbol, info),
                        'industry': 'Exchange Traded Funds',
                        'market_cap': info.get('totalAssets', 0),  # AUM for ETFs
                        'expense_ratio': info.get('annualReportExpenseRatio'),
                        'dividend_yield': info.get('yield', info.get('trailingAnnualDividendYield')),
                        'inception_date': info.get('fundInceptionDate'),
                        'is_active': True
                    }
                    us_etfs.append(etf_data)
                    
            except Exception as e:
                self.logger.warning(f"⚠️ Could not fetch {symbol}: {str(e)}")
                continue
        
        self.logger.info(f"✅ Successfully fetched {len(us_etfs)} US ETFs")
        return us_etfs
    
    def download_indian_etfs(self) -> List[Dict]:
        """
        Download Indian ETF data using yfinance.
        Uses predefined list of popular Indian ETFs.
        
        Returns:
            List of Indian ETF dictionaries
        """
        self.logger.info(f"📥 Getting data for {len(self.indian_etf_symbols)} Indian ETFs...")
        
        indian_etfs = []
        
        for symbol in self.indian_etf_symbols:
            try:
                self.logger.info(f"  Fetching {symbol}...")
                
                # Get ETF info from yfinance
                ticker = yf.Ticker(symbol)
                info = ticker.info
                
                if info and ('shortName' in info or 'longName' in info):
                    etf_data = {
                        'symbol': symbol,
                        'name': info.get('shortName', info.get('longName', symbol.replace('.NS', ''))),
                        'type': 'etf',
                        'subtype': self._classify_indian_etf_type(symbol),
                        'exchange': 'NSE',
                        'country': 'IN',
                        'currency': 'INR',
                        'sector': self._get_indian_etf_sector(symbol),
                        'industry': 'Exchange Traded Funds',
                        'market_cap': info.get('marketCap', 0),
                        'expense_ratio': info.get('annualReportExpenseRatio'),
                        'dividend_yield': info.get('trailingAnnualDividendYield'),
                        'is_active': True
                    }
                    indian_etfs.append(etf_data)
                    
            except Exception as e:
                self.logger.warning(f"⚠️ Could not fetch {symbol}: {str(e)}")
                continue
        
        self.logger.info(f"✅ Successfully fetched {len(indian_etfs)} Indian ETFs")
        return indian_etfs
    
    def _classify_us_etf_type(self, symbol: str, info: Dict) -> str:
        """
        Classify US ETF type based on symbol and info.
        
        Args:
            symbol: ETF symbol
            info: ETF info from yfinance
            
        Returns:
            ETF classification
        """
        category = info.get('category', '').lower()
        name = info.get('longName', '').lower()
        
        # Broad market ETFs
        if symbol in ['SPY', 'VTI', 'IVV', 'VOO']:
            return 'broad_market'
        # Technology ETFs
        elif symbol in ['QQQ', 'VGT', 'XLK'] or 'technology' in name:
            return 'technology'
        # Sector ETFs
        elif symbol.startswith('XL') or 'sector' in category:
            return 'sector'
        # International ETFs
        elif symbol in ['EFA', 'EEM', 'VEA', 'VWO'] or 'international' in name:
            return 'international'
        # Bond ETFs
        elif symbol in ['BND', 'AGG', 'TLT', 'HYG', 'LQD'] or 'bond' in name:
            return 'bond'
        # Commodity ETFs
        elif symbol in ['GLD', 'SLV', 'USO'] or 'commodity' in name:
            return 'commodity'
        # Real Estate ETFs
        elif symbol in ['VNQ', 'IYR', 'XLRE'] or 'real estate' in name:
            return 'real_estate'
        # ARK Innovation ETFs
        elif symbol.startswith('ARK'):
            return 'innovation'
        else:
            return 'other'
    
    def _classify_indian_etf_type(self, symbol: str) -> str:
        """
        Classify Indian ETF type based on symbol.
        
        Args:
            symbol: Indian ETF symbol
            
        Returns:
            ETF classification
        """
        if 'NIFTY' in symbol or 'BEES' in symbol:
            return 'index'
        elif 'GOLD' in symbol:
            return 'commodity'
        elif 'BANK' in symbol:
            return 'banking'
        elif 'IT' in symbol:
            return 'technology'
        elif 'INFRA' in symbol:
            return 'infrastructure'
        elif 'PHARMA' in symbol:
            return 'pharmaceutical'
        elif 'FMCG' in symbol:
            return 'fmcg'
        elif 'AUTO' in symbol:
            return 'automotive'
        elif 'METAL' in symbol:
            return 'metals'
        else:
            return 'other'
    
    def _get_us_exchange(self, info: Dict) -> str:
        """Determine US exchange from ETF info."""
        exchange = info.get('exchange', '').upper()
        if 'NYSE' in exchange:
            return 'NYSE Arca'
        elif 'NASDAQ' in exchange:
            return 'NASDAQ'
        else:
            return 'NYSE Arca'  # Most US ETFs trade on NYSE Arca
    
    def _get_etf_sector(self, symbol: str, info: Dict) -> str:
        """Get ETF sector based on symbol and info."""
        if symbol in ['SPY', 'VTI', 'QQQ']:
            return 'Broad Market'
        elif symbol.startswith('XL'):
            sector_map = {
                'XLF': 'Financial', 'XLE': 'Energy', 'XLK': 'Technology',
                'XLV': 'Healthcare', 'XLI': 'Industrial', 'XLP': 'Consumer Staples',
                'XLU': 'Utilities', 'XLB': 'Materials', 'XLRE': 'Real Estate'
            }
            return sector_map.get(symbol, 'Unknown')
        else:
            return info.get('sector', 'Mixed')
    
    def _get_indian_etf_sector(self, symbol: str) -> str:
        """Get Indian ETF sector based on symbol."""
        if 'BANK' in symbol:
            return 'Banking'
        elif 'IT' in symbol:
            return 'Information Technology'
        elif 'GOLD' in symbol:
            return 'Commodities'
        elif 'PHARMA' in symbol:
            return 'Pharmaceuticals'
        elif 'AUTO' in symbol:
            return 'Automotive'
        elif 'METAL' in symbol:
            return 'Metals & Mining'
        elif 'FMCG' in symbol:
            return 'Consumer Goods'
        else:
            return 'Mixed'

    # ========================================
    # FUNCTION 2: CROSS-CHECK WITH DATABASE
    # ========================================
    
    def cross_check_etfs(self, new_etfs: List[Dict]) -> Tuple[List[Dict], List[Dict], List[Dict]]:
        """
        Cross-check downloaded ETFs with existing database records.
        
        Args:
            new_etfs: List of ETF data dictionaries
            
        Returns:
            Tuple of (etfs_to_add, etfs_to_update, etfs_unchanged)
        """
        self.logger.info("🔍 Cross-checking ETFs with database...")
        
        db = self.get_db_session()
        
        # Get existing ETFs from database
        existing_etfs = db.query(Asset).filter(Asset.type == 'etf').all()
        existing_symbols = {etf.symbol: etf for etf in existing_etfs}
        
        etfs_to_add = []
        etfs_to_update = []
        etfs_unchanged = []
        
        for new_etf in new_etfs:
            symbol = new_etf['symbol']
            
            if symbol in existing_symbols:
                # ETF exists, check if update needed
                existing_etf = existing_symbols[symbol]
                
                if self._needs_update(existing_etf, new_etf):
                    etfs_to_update.append({
                        'existing': existing_etf,
                        'new_data': new_etf
                    })
                else:
                    etfs_unchanged.append(new_etf)
            else:
                # New ETF, add to database
                etfs_to_add.append(new_etf)
        
        self.logger.info(f"📊 Cross-check results:")
        self.logger.info(f"  - New ETFs to add: {len(etfs_to_add)}")
        self.logger.info(f"  - ETFs to update: {len(etfs_to_update)}")
        self.logger.info(f"  - ETFs unchanged: {len(etfs_unchanged)}")
        
        return etfs_to_add, etfs_to_update, etfs_unchanged
    
    def _needs_update(self, existing_etf: Asset, new_data: Dict) -> bool:
        """Check if existing ETF record needs update."""
        # Check key fields that might change for ETFs
        fields_to_check = ['name', 'market_cap', 'expense_ratio', 'dividend_yield']
        
        for field in fields_to_check:
            if field in new_data:
                existing_value = getattr(existing_etf, field, None)
                new_value = new_data[field]
                
                if existing_value != new_value:
                    return True
        
        return False

    # ========================================
    # FUNCTION 3: UPDATE EXISTING ETFS
    # ========================================
    
    def update_existing_etfs(self, etfs_to_update: List[Dict]):
        """Update existing ETF records with new data."""
        if not etfs_to_update:
            self.logger.info("ℹ️ No ETFs to update")
            return
        
        self.logger.info(f"🔄 Updating {len(etfs_to_update)} existing ETFs...")
        
        db = self.get_db_session()
        updated_count = 0
        
        try:
            for update_info in etfs_to_update:
                existing_etf = update_info['existing']
                new_data = update_info['new_data']
                
                # Update fields specific to ETFs
                existing_etf.name = new_data.get('name', existing_etf.name)
                existing_etf.market_cap = new_data.get('market_cap', existing_etf.market_cap)
                existing_etf.expense_ratio = new_data.get('expense_ratio', existing_etf.expense_ratio)
                existing_etf.dividend_yield = new_data.get('dividend_yield', existing_etf.dividend_yield)
                existing_etf.last_updated = datetime.now()
                
                updated_count += 1
                self.logger.info(f"  ✅ Updated {existing_etf.symbol}")
            
            db.commit()
            self.logger.info(f"✅ Successfully updated {updated_count} ETFs")
            
        except Exception as e:
            self.logger.error(f"❌ Error updating ETFs: {str(e)}")
            db.rollback()

    # ========================================
    # FUNCTION 4: ADD NEW ETFS
    # ========================================
    
    def add_new_etfs(self, etfs_to_add: List[Dict]):
        """Add new ETF records to database."""
        if not etfs_to_add:
            self.logger.info("ℹ️ No new ETFs to add")
            return
        
        self.logger.info(f"➕ Adding {len(etfs_to_add)} new ETFs...")
        
        db = self.get_db_session()
        added_count = 0
        
        try:
            for etf_data in etfs_to_add:
                # Create new Asset record for ETF
                new_asset = Asset(
                    symbol=etf_data['symbol'],
                    name=etf_data['name'],
                    type='etf',
                    subtype=etf_data.get('subtype', 'other'),
                    exchange=etf_data.get('exchange', 'Unknown'),
                    country=etf_data.get('country', 'Unknown'),
                    currency=etf_data.get('currency', 'USD'),
                    sector=etf_data.get('sector', 'Mixed'),
                    industry=etf_data.get('industry', 'Exchange Traded Funds'),
                    market_cap=etf_data.get('market_cap'),  # AUM for ETFs
                    expense_ratio=etf_data.get('expense_ratio'),
                    dividend_yield=etf_data.get('dividend_yield'),
                    is_active=True,
                    created_at=datetime.now(),
                    last_updated=datetime.now()
                )
                
                db.add(new_asset)
                added_count += 1
                self.logger.info(f"  ➕ Added {etf_data['symbol']}")
            
            db.commit()
            self.logger.info(f"✅ Successfully added {added_count} new ETFs")
            
        except Exception as e:
            self.logger.error(f"❌ Error adding ETFs: {str(e)}")
            db.rollback()

    # ========================================
    # FUNCTION 5: MAIN ORCHESTRATOR
    # ========================================
    
    def sync_all_etfs(self):
        """
        Main function to sync all ETFs.
        Downloads, cross-checks, updates, and adds ETFs.
        """
        self.logger.info("🚀 Starting ETF synchronization...")
        
        try:
            # Step 1: Download ETF data from all sources
            all_etfs = []
            
            # Get US ETFs
            us_etfs = self.download_us_etfs()
            all_etfs.extend(us_etfs)
            
            # Get Indian ETFs
            indian_etfs = self.download_indian_etfs()
            all_etfs.extend(indian_etfs)
            
            self.logger.info(f"📊 Total ETFs downloaded: {len(all_etfs)}")
            
            if not all_etfs:
                self.logger.warning("⚠️ No ETF data downloaded, aborting sync")
                return
            
            # Step 2: Cross-check with database
            etfs_to_add, etfs_to_update, etfs_unchanged = self.cross_check_etfs(all_etfs)
            
            # Step 3: Update existing ETFs
            self.update_existing_etfs(etfs_to_update)
            
            # Step 4: Add new ETFs
            self.add_new_etfs(etfs_to_add)
            
            # Step 5: Summary
            self.logger.info("🎉 ETF synchronization completed!")
            self.logger.info(f"📈 Summary:")
            self.logger.info(f"  - Total ETFs processed: {len(all_etfs)}")
            self.logger.info(f"  - New ETFs added: {len(etfs_to_add)}")
            self.logger.info(f"  - Existing ETFs updated: {len(etfs_to_update)}")
            self.logger.info(f"  - ETFs unchanged: {len(etfs_unchanged)}")
            
        except Exception as e:
            self.logger.error(f"❌ Error in ETF synchronization: {str(e)}")
            raise
        
        finally:
            self.close_db_session()


# ========================================
# CONVENIENCE FUNCTIONS FOR EASY USE
# ========================================

def sync_etfs():
    """Easy function to sync all ETFs."""
    manager = ETFManager()
    manager.sync_all_etfs()

def sync_us_etfs_only():
    """Sync only US ETFs."""
    manager = ETFManager()
    us_etfs = manager.download_us_etfs()
    if us_etfs:
        etfs_to_add, etfs_to_update, _ = manager.cross_check_etfs(us_etfs)
        manager.update_existing_etfs(etfs_to_update)
        manager.add_new_etfs(etfs_to_add)
    manager.close_db_session()

def sync_indian_etfs_only():
    """Sync only Indian ETFs."""
    manager = ETFManager()
    indian_etfs = manager.download_indian_etfs()
    if indian_etfs:
        etfs_to_add, etfs_to_update, _ = manager.cross_check_etfs(indian_etfs)
        manager.update_existing_etfs(etfs_to_update)
        manager.add_new_etfs(etfs_to_add)
    manager.close_db_session()


# ========================================
# MAIN EXECUTION
# ========================================

if __name__ == "__main__":
    print("📊 Lumia ETF Manager")
    print("=" * 50)
    
    # You can run different functions:
    
    # Option 1: Sync everything
    sync_etfs()
    
    # Option 2: Sync only US ETFs
    # sync_us_etfs_only()
    
    # Option 3: Sync only Indian ETFs
    # sync_indian_etfs_only()