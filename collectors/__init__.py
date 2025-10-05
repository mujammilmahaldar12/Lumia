"""
Collectors package for Lumia Financial Analytics System.

This package contains all data collectors that fetch information from external sources:
- Stock assets information (Indian NSE/BSE and US markets)
- Mutual fund data (Indian AMFI and US funds)
- ETF data (Indian and US ETFs)
- Cryptocurrency data (CoinGecko API)

Each collector follows the same 5-function pattern:
1. Download data from external sources
2. Cross-check with existing database records  
3. Update existing records
4. Add new records
5. Main orchestrator function

All collectors inherit error handling, logging, and database management patterns.
"""

# Import all collector classes
from .stocks_manager import StocksManager, sync_stocks, sync_nse_only, sync_us_only
from .mutual_fund_manager import MutualFundManager, sync_mutual_funds, sync_indian_funds_only, sync_us_funds_only
from .etf_manager import ETFManager, sync_etfs, sync_us_etfs_only, sync_indian_etfs_only
from .crypto_manager import CryptoManager, sync_cryptos, sync_top_cryptos
from .master_collector import MasterAssetCollector, sync_all_assets, sync_specific_assets, quick_sync
from .fundamentals_collector import FundamentalsCollector, collect_all_fundamentals, update_stale_fundamentals, collect_for_symbol

# Export all classes and convenience functions
__all__ = [
    # Manager Classes
    'StocksManager',
    'MutualFundManager', 
    'ETFManager',
    'CryptoManager',
    'MasterAssetCollector',
    'FundamentalsCollector',
    
    # Individual Collector Functions
    'sync_stocks',
    'sync_nse_only',
    'sync_us_only',
    'sync_mutual_funds',
    'sync_indian_funds_only',
    'sync_us_funds_only',
    'sync_etfs',
    'sync_us_etfs_only', 
    'sync_indian_etfs_only',
    'sync_cryptos',
    'sync_top_cryptos',
    
    # Fundamentals Collection
    'collect_all_fundamentals',
    'update_stale_fundamentals',
    'collect_for_symbol',
    
    # Master Collection Functions
    'sync_all_assets',
    'sync_specific_assets',
    'quick_sync'
]

# Version info
__version__ = '1.0.0'

# Package metadata
__author__ = 'Mujammil Mahaldar'
__description__ = 'Financial asset data collectors for stocks, mutual funds, ETFs, and cryptocurrencies and this is created by mujammil mahaldar'