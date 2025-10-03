
"""
Mutual Fund Collector - Fetches mutual fund information from various sources.
Handles Indian mutual funds (AMFI data) and US mutual funds.

Similar to stocks_manager.py but specialized for mutual funds.
"""

import requests
import pandas as pd
import yfinance as yf
from datetime import datetime, date
from typing import List, Dict, Tuple, Optional
import logging
import sys
import os
from sqlalchemy.orm import Session
from sqlalchemy import and_

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import our models
from models.assets import Asset
from database import get_db
from utils.logging_config import setup_unicode_logging


class MutualFundManager:
    """
    Complete mutual fund management system.
    Similar to StocksManager but handles mutual fund specific data.
    """
    
    def __init__(self):
        self.logger = self._setup_logger()
        self.db = None
        
        # Data sources for mutual funds
        self.amfi_url = "https://www.amfiindia.com/spages/NAVAll.txt"  # Indian MF data
        
        # Popular US mutual fund families (we'll use yfinance for these)
        self.us_fund_symbols = [
            # Vanguard funds
            "VTSAX", "VTIAX", "VBTLX", "VTBLX", "VGTSX",
            # Fidelity funds  
            "FXAIX", "FTIHX", "FXNAX", "FDVV", "FSKAX",
            # Charles Schwab funds
            "SWTSX", "SWISX", "SWAGX", "SWLGX", "SWMGX"
        ]
    
    def _setup_logger(self):
        """Setup Unicode-safe logging for mutual fund manager."""
        return setup_unicode_logging(
            "lumia.mutual_fund_manager",
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
    # FUNCTION 1: DOWNLOAD MUTUAL FUND LISTS
    # ========================================
    
    def download_indian_mutual_funds(self) -> List[Dict]:
        """
        Download Indian mutual funds from AMFI (Association of Mutual Funds in India).
        
        Returns:
            List of Indian mutual fund dictionaries
        """
        self.logger.info("📥 Downloading Indian Mutual Funds from AMFI...")
        
        try:
            # Download AMFI NAV data (contains all Indian mutual funds)
            response = requests.get(self.amfi_url, timeout=30)
            response.raise_for_status()
            
            # Parse the text data
            lines = response.text.strip().split('\n')
            mutual_funds = []
            
            current_amc = ""  # Asset Management Company
            
            for line in lines:
                line = line.strip()
                
                # Skip header and empty lines
                if not line or line.startswith('Scheme Code'):
                    continue
                
                # Check if this is an AMC header (no semicolon, all caps)
                if ';' not in line and line.isupper():
                    current_amc = line
                    continue
                
                # Parse mutual fund data
                parts = line.split(';')
                if len(parts) >= 6:
                    try:
                        fund_data = {
                            'symbol': f"IN-MF-{parts[0]}",  # Scheme code with prefix
                            'name': parts[3].strip(),        # Scheme name
                            'type': 'mutual_fund',
                            'subtype': self._classify_fund_type(parts[3]),
                            'exchange': 'AMFI',
                            'country': 'IN',
                            'currency': 'INR',
                            'sector': 'Financial Services',
                            'industry': 'Mutual Funds',
                            'amc_name': current_amc,         # Asset Management Company
                            'nav': float(parts[4]) if parts[4] and parts[4] != 'N.A.' else None,
                            'is_active': True
                        }
                        mutual_funds.append(fund_data)
                        
                    except (ValueError, IndexError) as e:
                        self.logger.warning(f"⚠️ Could not parse line: {line}")
                        continue
            
            self.logger.info(f"✅ Downloaded {len(mutual_funds)} Indian mutual funds")
            return mutual_funds
            
        except Exception as e:
            self.logger.error(f"❌ Error downloading Indian MF data: {str(e)}")
            return []
    
    def download_us_mutual_funds(self) -> List[Dict]:
        """
        Download US mutual funds using yfinance.
        Uses predefined list of popular US mutual funds.
        
        Returns:
            List of US mutual fund dictionaries
        """
        self.logger.info(f"📥 Getting data for {len(self.us_fund_symbols)} US mutual funds...")
        
        us_funds = []
        
        for symbol in self.us_fund_symbols:
            try:
                self.logger.info(f"  Fetching {symbol}...")
                
                # Get fund info from yfinance
                ticker = yf.Ticker(symbol)
                info = ticker.info
                
                if info and 'shortName' in info:
                    fund_data = {
                        'symbol': symbol,
                        'name': info.get('shortName', info.get('longName', 'Unknown')),
                        'type': 'mutual_fund',
                        'subtype': self._classify_us_fund_type(info),
                        'exchange': 'US-MF',
                        'country': 'US',
                        'currency': 'USD',
                        'sector': 'Financial Services', 
                        'industry': 'Mutual Funds',
                        'market_cap': info.get('totalAssets', 0),  # For funds, this is AUM
                        'expense_ratio': info.get('annualReportExpenseRatio'),
                        'nav': info.get('navPrice', info.get('regularMarketPrice')),
                        'is_active': True
                    }
                    us_funds.append(fund_data)
                    
            except Exception as e:
                self.logger.warning(f"⚠️ Could not fetch {symbol}: {str(e)}")
                continue
        
        self.logger.info(f"✅ Successfully fetched {len(us_funds)} US mutual funds")
        return us_funds
    
    def _classify_fund_type(self, fund_name: str) -> str:
        """
        Classify Indian mutual fund type based on name.
        
        Args:
            fund_name: Name of the mutual fund
            
        Returns:
            Fund classification (equity, debt, hybrid, etc.)
        """
        name_lower = fund_name.lower()
        
        if any(word in name_lower for word in ['equity', 'growth', 'largecap', 'midcap', 'smallcap']):
            return 'equity'
        elif any(word in name_lower for word in ['debt', 'bond', 'gilt', 'liquid', 'income']):
            return 'debt'
        elif any(word in name_lower for word in ['hybrid', 'balanced', 'conservative']):
            return 'hybrid'
        elif 'index' in name_lower:
            return 'index'
        elif 'elss' in name_lower:
            return 'elss'
        else:
            return 'other'
    
    def _classify_us_fund_type(self, info: Dict) -> str:
        """
        Classify US mutual fund type based on info.
        
        Args:
            info: Fund info from yfinance
            
        Returns:
            Fund classification
        """
        category = info.get('category', '').lower()
        fund_name = info.get('longName', '').lower()
        
        if 'equity' in category or 'stock' in category:
            return 'equity'
        elif 'bond' in category or 'fixed' in category:
            return 'bond'
        elif 'index' in fund_name or 'index' in category:
            return 'index'
        elif 'target' in fund_name:
            return 'target_date'
        else:
            return 'other'

    # ========================================
    # FUNCTION 2: CROSS-CHECK WITH DATABASE
    # ========================================
    
    def cross_check_funds(self, new_funds: List[Dict]) -> Tuple[List[Dict], List[Dict], List[Dict]]:
        """
        Cross-check downloaded funds with existing database records.
        Same logic as stocks but for mutual funds.
        
        Args:
            new_funds: List of mutual fund data dictionaries
            
        Returns:
            Tuple of (funds_to_add, funds_to_update, funds_unchanged)
        """
        self.logger.info("🔍 Cross-checking mutual funds with database...")
        
        db = self.get_db_session()
        
        # Get existing mutual funds from database
        existing_funds = db.query(Asset).filter(Asset.type == 'mutual_fund').all()
        existing_symbols = {fund.symbol: fund for fund in existing_funds}
        
        funds_to_add = []
        funds_to_update = []
        funds_unchanged = []
        
        for new_fund in new_funds:
            symbol = new_fund['symbol']
            
            if symbol in existing_symbols:
                # Fund exists, check if update needed
                existing_fund = existing_symbols[symbol]
                
                if self._needs_update(existing_fund, new_fund):
                    funds_to_update.append({
                        'existing': existing_fund,
                        'new_data': new_fund
                    })
                else:
                    funds_unchanged.append(new_fund)
            else:
                # New fund, add to database
                funds_to_add.append(new_fund)
        
        self.logger.info(f"📊 Cross-check results:")
        self.logger.info(f"  - New funds to add: {len(funds_to_add)}")
        self.logger.info(f"  - Funds to update: {len(funds_to_update)}")
        self.logger.info(f"  - Funds unchanged: {len(funds_unchanged)}")
        
        return funds_to_add, funds_to_update, funds_unchanged
    
    def _needs_update(self, existing_fund: Asset, new_data: Dict) -> bool:
        """Check if existing fund record needs update."""
        # Check key fields that might change for mutual funds
        fields_to_check = ['name', 'nav', 'expense_ratio', 'market_cap']
        
        for field in fields_to_check:
            if field in new_data:
                existing_value = getattr(existing_fund, field, None)
                new_value = new_data[field]
                
                if existing_value != new_value:
                    return True
        
        return False

    # ========================================
    # FUNCTION 3: UPDATE EXISTING FUNDS
    # ========================================
    
    def update_existing_funds(self, funds_to_update: List[Dict]):
        """Update existing mutual fund records with new data."""
        if not funds_to_update:
            self.logger.info("ℹ️ No funds to update")
            return
        
        self.logger.info(f"🔄 Updating {len(funds_to_update)} existing funds...")
        
        db = self.get_db_session()
        updated_count = 0
        
        try:
            for update_info in funds_to_update:
                existing_fund = update_info['existing']
                new_data = update_info['new_data']
                
                # Update fields specific to mutual funds
                existing_fund.name = new_data.get('name', existing_fund.name)
                existing_fund.market_cap = new_data.get('market_cap', existing_fund.market_cap)
                existing_fund.expense_ratio = new_data.get('expense_ratio', existing_fund.expense_ratio)
                existing_fund.updated_at = datetime.now()
                
                updated_count += 1
                self.logger.info(f"  ✅ Updated {existing_fund.symbol}")
            
            db.commit()
            self.logger.info(f"✅ Successfully updated {updated_count} funds")
            
        except Exception as e:
            self.logger.error(f"❌ Error updating funds: {str(e)}")
            db.rollback()

    # ========================================
    # FUNCTION 4: ADD NEW FUNDS
    # ========================================
    
    def add_new_funds(self, funds_to_add: List[Dict]):
        """Add new mutual fund records to database."""
        if not funds_to_add:
            self.logger.info("ℹ️ No new funds to add")
            return
        
        self.logger.info(f"➕ Adding {len(funds_to_add)} new funds...")
        
        db = self.get_db_session()
        added_count = 0
        
        try:
            for fund_data in funds_to_add:
                # Create new Asset record for mutual fund
                new_asset = Asset(
                    symbol=fund_data['symbol'],
                    name=fund_data['name'],
                    type='mutual_fund',
                    subtype=fund_data.get('subtype', 'other'),
                    exchange=fund_data.get('exchange', 'Unknown'),
                    country=fund_data.get('country', 'Unknown'),
                    currency=fund_data.get('currency', 'USD'),
                    sector=fund_data.get('sector', 'Financial Services'),
                    industry=fund_data.get('industry', 'Mutual Funds'),
                    market_cap=fund_data.get('market_cap'),  # AUM for funds
                    expense_ratio=fund_data.get('expense_ratio'),
                    is_active=True,
                    created_at=datetime.now(),
                    last_updated=datetime.now()
                )
                
                db.add(new_asset)
                added_count += 1
                self.logger.info(f"  ➕ Added {fund_data['symbol']}")
            
            db.commit()
            self.logger.info(f"✅ Successfully added {added_count} new funds")
            
        except Exception as e:
            self.logger.error(f"❌ Error adding funds: {str(e)}")
            db.rollback()

    # ========================================
    # FUNCTION 5: MAIN ORCHESTRATOR
    # ========================================
    
    def sync_all_mutual_funds(self):
        """
        Main function to sync all mutual funds.
        Downloads, cross-checks, updates, and adds funds.
        """
        self.logger.info("🚀 Starting mutual funds synchronization...")
        
        try:
            # Step 1: Download fund data from all sources
            all_funds = []
            
            # Get Indian mutual funds
            indian_funds = self.download_indian_mutual_funds()
            all_funds.extend(indian_funds)
            
            # Get US mutual funds
            us_funds = self.download_us_mutual_funds()
            all_funds.extend(us_funds)
            
            self.logger.info(f"📊 Total funds downloaded: {len(all_funds)}")
            
            if not all_funds:
                self.logger.warning("⚠️ No fund data downloaded, aborting sync")
                return
            
            # Step 2: Cross-check with database
            funds_to_add, funds_to_update, funds_unchanged = self.cross_check_funds(all_funds)
            
            # Step 3: Update existing funds
            self.update_existing_funds(funds_to_update)
            
            # Step 4: Add new funds
            self.add_new_funds(funds_to_add)
            
            # Step 5: Summary
            self.logger.info("🎉 Mutual funds synchronization completed!")
            self.logger.info(f"📈 Summary:")
            self.logger.info(f"  - Total funds processed: {len(all_funds)}")
            self.logger.info(f"  - New funds added: {len(funds_to_add)}")
            self.logger.info(f"  - Existing funds updated: {len(funds_to_update)}")
            self.logger.info(f"  - Funds unchanged: {len(funds_unchanged)}")
            
        except Exception as e:
            self.logger.error(f"❌ Error in mutual funds synchronization: {str(e)}")
            raise
        
        finally:
            self.close_db_session()


# ========================================
# CONVENIENCE FUNCTIONS FOR EASY USE
# ========================================

def sync_mutual_funds():
    """Easy function to sync all mutual funds."""
    manager = MutualFundManager()
    manager.sync_all_mutual_funds()

def sync_indian_funds_only():
    """Sync only Indian mutual funds."""
    manager = MutualFundManager()
    indian_funds = manager.download_indian_mutual_funds()
    if indian_funds:
        funds_to_add, funds_to_update, _ = manager.cross_check_funds(indian_funds)
        manager.update_existing_funds(funds_to_update)
        manager.add_new_funds(funds_to_add)
    manager.close_db_session()

def sync_us_funds_only():
    """Sync only US mutual funds."""
    manager = MutualFundManager()
    us_funds = manager.download_us_mutual_funds()
    if us_funds:
        funds_to_add, funds_to_update, _ = manager.cross_check_funds(us_funds)
        manager.update_existing_funds(funds_to_update)
        manager.add_new_funds(funds_to_add)
    manager.close_db_session()


# ========================================
# MAIN EXECUTION
# ========================================

if __name__ == "__main__":
    print("🏦 Lumia Mutual Fund Manager")
    print("=" * 50)
    
    # You can run different functions:
    
    # Option 1: Sync everything
    sync_mutual_funds()
    
    # Option 2: Sync only Indian funds
    # sync_indian_funds_only()
    
    # Option 3: Sync only US funds
    # sync_us_funds_only()