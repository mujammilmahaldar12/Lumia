"""
Fundamentals Collector - Fetches quarterly fundamental data for stocks
Downloads financial metrics like P/E ratio, ROE, revenue, margins, debt ratios

This collector populates the quarterly_fundamentals table which is used by
the recommendation engine for 30% of the stock scoring.

Data sources:
- yfinance for US stocks
- Yahoo Finance for international stocks
"""

import yfinance as yf
import pandas as pd
from datetime import datetime, date, timedelta
from typing import List, Dict, Optional
import logging
import sys
import os
from sqlalchemy.orm import Session
from sqlalchemy import and_

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import our models
from models.assets import Asset
from models.quarterly_fundamental import QuarterlyFundamental
from database import get_db
from utils.logging_config import setup_unicode_logging


class FundamentalsCollector:
    """
    Collects and manages quarterly fundamental data for stocks.
    Fetches financial metrics critical for fundamental analysis.
    """
    
    def __init__(self):
        self.logger = self._setup_logger()
        self.db = None
    
    def _setup_logger(self):
        """Setup Unicode-safe logging."""
        return setup_unicode_logging(
            "lumia.fundamentals_collector",
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
    # FUNCTION 1: FETCH FUNDAMENTALS FROM API
    # ========================================
    
    def fetch_stock_fundamentals(self, symbol: str) -> Optional[Dict]:
        """
        Fetch fundamental data for a single stock using yfinance.
        
        Args:
            symbol: Stock ticker symbol
            
        Returns:
            Dictionary with fundamental metrics or None if failed
        """
        try:
            ticker = yf.Ticker(symbol)
            info = ticker.info
            
            # Get quarterly financials
            quarterly_financials = ticker.quarterly_financials
            quarterly_balance_sheet = ticker.quarterly_balance_sheet
            quarterly_cashflow = ticker.quarterly_cashflow
            
            if quarterly_financials.empty:
                self.logger.warning(f"⚠️ No quarterly data for {symbol}")
                return None
            
            # Get most recent quarter
            latest_quarter = quarterly_financials.columns[0]
            
            # Extract key metrics
            fundamentals = {
                'report_date': latest_quarter.date(),
                
                # Valuation metrics
                'price_to_earnings_ratio': info.get('trailingPE'),
                'price_to_book_ratio': info.get('priceToBook'),
                'price_to_sales_ratio': info.get('priceToSalesTrailing12Months'),
                'peg_ratio': info.get('pegRatio'),
                
                # Profitability metrics
                'return_on_equity': info.get('returnOnEquity'),
                'return_on_assets': info.get('returnOnAssets'),
                'profit_margin': info.get('profitMargins'),
                'operating_margin': info.get('operatingMargins'),
                'gross_margin': info.get('grossMargins'),
                
                # Income statement
                'total_revenue': self._get_value(quarterly_financials, 'Total Revenue', latest_quarter),
                'cost_of_revenue': self._get_value(quarterly_financials, 'Cost Of Revenue', latest_quarter),
                'gross_profit': self._get_value(quarterly_financials, 'Gross Profit', latest_quarter),
                'operating_income': self._get_value(quarterly_financials, 'Operating Income', latest_quarter),
                'net_income': self._get_value(quarterly_financials, 'Net Income', latest_quarter),
                'ebitda': info.get('ebitda'),
                
                # Per share metrics
                'earnings_per_share': info.get('trailingEps'),
                'book_value_per_share': info.get('bookValue'),
                'revenue_per_share': info.get('revenuePerShare'),
                
                # Balance sheet
                'total_assets': self._get_value(quarterly_balance_sheet, 'Total Assets', latest_quarter),
                'total_liabilities': self._get_value(quarterly_balance_sheet, 'Total Liabilities Net Minority Interest', latest_quarter),
                'total_equity': self._get_value(quarterly_balance_sheet, 'Total Equity Gross Minority Interest', latest_quarter),
                'total_debt': self._get_value(quarterly_balance_sheet, 'Total Debt', latest_quarter),
                'cash_and_equivalents': self._get_value(quarterly_balance_sheet, 'Cash And Cash Equivalents', latest_quarter),
                
                # Debt metrics
                'debt_to_equity_ratio': info.get('debtToEquity'),
                'current_ratio': info.get('currentRatio'),
                'quick_ratio': info.get('quickRatio'),
                
                # Cash flow
                'operating_cash_flow': self._get_value(quarterly_cashflow, 'Operating Cash Flow', latest_quarter),
                'free_cash_flow': info.get('freeCashflow'),
                'capital_expenditure': self._get_value(quarterly_cashflow, 'Capital Expenditure', latest_quarter),
                
                # Growth metrics
                'revenue_growth': info.get('revenueGrowth'),
                'earnings_growth': info.get('earningsGrowth'),
                
                # Other metrics
                'shares_outstanding': info.get('sharesOutstanding'),
                'market_cap': info.get('marketCap'),
                'enterprise_value': info.get('enterpriseValue'),
            }
            
            return fundamentals
            
        except Exception as e:
            self.logger.error(f"❌ Error fetching fundamentals for {symbol}: {str(e)}")
            return None
    
    def _get_value(self, df: pd.DataFrame, key: str, column) -> Optional[float]:
        """
        Safely extract value from DataFrame.
        
        Args:
            df: DataFrame to extract from
            key: Row key to look for
            column: Column to extract
            
        Returns:
            Float value or None
        """
        try:
            if df.empty or key not in df.index:
                return None
            return float(df.loc[key, column])
        except:
            return None

    # ========================================
    # FUNCTION 2: SAVE TO DATABASE
    # ========================================
    
    def save_fundamentals(self, asset_id: int, fundamentals_data: Dict) -> bool:
        """
        Save fundamental data to database.
        
        Args:
            asset_id: Asset ID from assets table
            fundamentals_data: Dictionary with fundamental metrics
            
        Returns:
            True if saved successfully, False otherwise
        """
        db = self.get_db_session()
        
        try:
            # Check if fundamental already exists for this quarter
            existing = db.query(QuarterlyFundamental).filter(
                and_(
                    QuarterlyFundamental.asset_id == asset_id,
                    QuarterlyFundamental.report_date == fundamentals_data['report_date']
                )
            ).first()
            
            if existing:
                # Update existing record
                for key, value in fundamentals_data.items():
                    if key != 'report_date':
                        setattr(existing, key, value)
                existing.last_updated = datetime.now()
                self.logger.info(f"  🔄 Updated existing fundamental record")
            else:
                # Create new record
                new_fundamental = QuarterlyFundamental(
                    asset_id=asset_id,
                    **fundamentals_data
                )
                db.add(new_fundamental)
                self.logger.info(f"  ➕ Added new fundamental record")
            
            db.commit()
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Error saving fundamentals: {str(e)}")
            db.rollback()
            return False

    # ========================================
    # FUNCTION 3: COLLECT FOR SINGLE STOCK
    # ========================================
    
    def collect_for_stock(self, asset: Asset) -> bool:
        """
        Collect and save fundamentals for a single stock.
        
        Args:
            asset: Asset object from database
            
        Returns:
            True if successful, False otherwise
        """
        self.logger.info(f"📊 Collecting fundamentals for {asset.symbol}...")
        
        # Fetch fundamentals
        fundamentals_data = self.fetch_stock_fundamentals(asset.symbol)
        
        if not fundamentals_data:
            self.logger.warning(f"⚠️ No fundamental data available for {asset.symbol}")
            return False
        
        # Save to database
        success = self.save_fundamentals(asset.id, fundamentals_data)
        
        if success:
            self.logger.info(f"✅ Successfully collected fundamentals for {asset.symbol}")
        
        return success

    # ========================================
    # FUNCTION 4: BATCH COLLECTION
    # ========================================
    
    def collect_for_all_stocks(self, limit: Optional[int] = None) -> Dict:
        """
        Collect fundamentals for all stocks in database.
        
        Args:
            limit: Optional limit on number of stocks to process
            
        Returns:
            Dictionary with collection statistics
        """
        self.logger.info("🚀 Starting fundamental data collection for all stocks...")
        
        db = self.get_db_session()
        
        # Get all stocks
        query = db.query(Asset).filter(
            Asset.type == 'stock',
            Asset.is_active == True
        )
        
        if limit:
            query = query.limit(limit)
        
        stocks = query.all()
        
        self.logger.info(f"📊 Found {len(stocks)} stocks to process")
        
        stats = {
            'total': len(stocks),
            'success': 0,
            'failed': 0,
            'skipped': 0
        }
        
        for i, stock in enumerate(stocks, 1):
            self.logger.info(f"[{i}/{len(stocks)}] Processing {stock.symbol}...")
            
            try:
                success = self.collect_for_stock(stock)
                
                if success:
                    stats['success'] += 1
                else:
                    stats['skipped'] += 1
                
                # Rate limiting - don't hammer Yahoo Finance
                if i % 10 == 0:
                    self.logger.info(f"  ⏸️ Pausing for rate limiting...")
                    import time
                    time.sleep(2)
                    
            except Exception as e:
                self.logger.error(f"❌ Error processing {stock.symbol}: {str(e)}")
                stats['failed'] += 1
                continue
        
        # Summary
        self.logger.info("🎉 Fundamental data collection completed!")
        self.logger.info(f"📈 Summary:")
        self.logger.info(f"  - Total stocks: {stats['total']}")
        self.logger.info(f"  - Successful: {stats['success']}")
        self.logger.info(f"  - Skipped: {stats['skipped']}")
        self.logger.info(f"  - Failed: {stats['failed']}")
        
        return stats

    # ========================================
    # FUNCTION 5: UPDATE STALE DATA
    # ========================================
    
    def update_stale_fundamentals(self, days_old: int = 90) -> Dict:
        """
        Update fundamental data that's older than specified days.
        
        Args:
            days_old: Update records older than this many days
            
        Returns:
            Dictionary with update statistics
        """
        self.logger.info(f"🔄 Updating fundamentals older than {days_old} days...")
        
        db = self.get_db_session()
        cutoff_date = datetime.now() - timedelta(days=days_old)
        
        # Get stocks with old fundamentals or no fundamentals
        stocks_with_old_data = db.query(Asset).outerjoin(QuarterlyFundamental).filter(
            Asset.type == 'stock',
            Asset.is_active == True
        ).filter(
            (QuarterlyFundamental.last_updated < cutoff_date) |
            (QuarterlyFundamental.last_updated == None)
        ).all()
        
        self.logger.info(f"📊 Found {len(stocks_with_old_data)} stocks needing update")
        
        stats = {
            'total': len(stocks_with_old_data),
            'success': 0,
            'failed': 0
        }
        
        for stock in stocks_with_old_data:
            try:
                if self.collect_for_stock(stock):
                    stats['success'] += 1
                else:
                    stats['failed'] += 1
            except Exception as e:
                self.logger.error(f"❌ Error updating {stock.symbol}: {str(e)}")
                stats['failed'] += 1
        
        self.logger.info(f"✅ Updated {stats['success']}/{stats['total']} stocks")
        
        return stats


# ========================================
# CONVENIENCE FUNCTIONS
# ========================================

def collect_all_fundamentals():
    """Easy function to collect fundamentals for all stocks."""
    collector = FundamentalsCollector()
    try:
        return collector.collect_for_all_stocks()
    finally:
        collector.close_db_session()

def update_stale_fundamentals(days_old: int = 90):
    """Update fundamentals older than specified days."""
    collector = FundamentalsCollector()
    try:
        return collector.update_stale_fundamentals(days_old)
    finally:
        collector.close_db_session()

def collect_for_symbol(symbol: str):
    """Collect fundamentals for a specific stock symbol."""
    collector = FundamentalsCollector()
    db = collector.get_db_session()
    
    try:
        asset = db.query(Asset).filter(Asset.symbol == symbol).first()
        if not asset:
            print(f"❌ Stock {symbol} not found in database")
            return False
        
        return collector.collect_for_stock(asset)
    finally:
        collector.close_db_session()


# ========================================
# MAIN EXECUTION
# ========================================

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='Lumia Fundamentals Collector')
    parser.add_argument('--symbol', type=str, help='Collect for specific symbol')
    parser.add_argument('--limit', type=int, help='Limit number of stocks to process')
    parser.add_argument('--update-stale', action='store_true', help='Update stale data only')
    parser.add_argument('--days', type=int, default=90, help='Days old for stale data')
    
    args = parser.parse_args()
    
    print("📊 Lumia Fundamentals Collector")
    print("=" * 50)
    
    if args.symbol:
        # Collect for specific symbol
        collect_for_symbol(args.symbol)
    elif args.update_stale:
        # Update stale data
        update_stale_fundamentals(args.days)
    else:
        # Collect for all stocks
        collect_all_fundamentals()
