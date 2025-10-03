"""
Master Asset Collector - Orchestrates all asset collection processes.
Runs stocks, mutual funds, ETFs, and crypto collectors in sequence.
"""

import logging
from datetime import datetime
from typing import Dict, Any
import asyncio

# Import all our collectors
from .stocks_manager import sync_stocks
from .mutual_fund_manager import sync_mutual_funds
from .etf_manager import sync_etfs
from .crypto_manager import sync_cryptos


class MasterAssetCollector:
    """
    Master collector that orchestrates all asset collection processes.
    Provides centralized control and monitoring of all data collection.
    """
    
    def __init__(self):
        self.logger = self._setup_logger()
        self.collectors = {
            'stocks': sync_stocks,
            'mutual_funds': sync_mutual_funds,
            'etfs': sync_etfs,
            'cryptos': sync_cryptos
        }
        self.collection_stats = {}
    
    def _setup_logger(self):
        """Setup logging for master collector."""
        logger = logging.getLogger("lumia.master_collector")
        logger.setLevel(logging.INFO)
        
        if not logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
            handler.setFormatter(formatter)
            logger.addHandler(handler)
        
        return logger
    
    def sync_all_assets(self):
        """
        Run all asset collectors in sequence.
        Collects stocks, mutual funds, ETFs, and cryptocurrencies.
        """
        start_time = datetime.now()
        self.logger.info("🚀 Starting MASTER ASSET COLLECTION")
        self.logger.info("=" * 60)
        
        total_success = 0
        total_failed = 0
        
        for asset_type, collector_func in self.collectors.items():
            try:
                self.logger.info(f"📊 Starting {asset_type.upper()} collection...")
                collector_start = datetime.now()
                
                # Run the collector
                collector_func()
                
                collector_end = datetime.now()
                duration = (collector_end - collector_start).total_seconds()
                
                self.collection_stats[asset_type] = {
                    'status': 'success',
                    'duration': duration,
                    'timestamp': collector_end
                }
                
                total_success += 1
                self.logger.info(f"✅ {asset_type.upper()} collection completed in {duration:.1f}s")
                
            except Exception as e:
                self.collection_stats[asset_type] = {
                    'status': 'failed',
                    'error': str(e),
                    'timestamp': datetime.now()
                }
                
                total_failed += 1
                self.logger.error(f"❌ {asset_type.upper()} collection failed: {str(e)}")
        
        # Final summary
        end_time = datetime.now()
        total_duration = (end_time - start_time).total_seconds()
        
        self.logger.info("=" * 60)
        self.logger.info("🎉 MASTER ASSET COLLECTION COMPLETED")
        self.logger.info(f"📈 Summary:")
        self.logger.info(f"  - Total duration: {total_duration:.1f} seconds")
        self.logger.info(f"  - Successful collectors: {total_success}")
        self.logger.info(f"  - Failed collectors: {total_failed}")
        self.logger.info("=" * 60)
        
        # Detailed stats
        for asset_type, stats in self.collection_stats.items():
            status = "✅" if stats['status'] == 'success' else "❌"
            if stats['status'] == 'success':
                self.logger.info(f"  {status} {asset_type}: {stats['duration']:.1f}s")
            else:
                self.logger.info(f"  {status} {asset_type}: {stats['error']}")
    
    def sync_specific_assets(self, asset_types: list):
        """
        Run collectors for specific asset types only.
        
        Args:
            asset_types: List of asset types to sync ['stocks', 'mutual_funds', 'etfs', 'cryptos']
        """
        self.logger.info(f"🎯 Starting targeted collection for: {', '.join(asset_types)}")
        
        for asset_type in asset_types:
            if asset_type in self.collectors:
                try:
                    self.logger.info(f"📊 Collecting {asset_type}...")
                    self.collectors[asset_type]()
                    self.logger.info(f"✅ {asset_type} collection completed")
                except Exception as e:
                    self.logger.error(f"❌ {asset_type} collection failed: {str(e)}")
            else:
                self.logger.warning(f"⚠️ Unknown asset type: {asset_type}")
    
    def get_collection_stats(self) -> Dict[str, Any]:
        """Get statistics from the last collection run."""
        return self.collection_stats


# ========================================
# CONVENIENCE FUNCTIONS FOR EASY USE
# ========================================

def sync_all_assets():
    """Easy function to sync all asset types."""
    collector = MasterAssetCollector()
    collector.sync_all_assets()

def sync_specific_assets(asset_types: list):
    """Easy function to sync specific asset types."""
    collector = MasterAssetCollector()
    collector.sync_specific_assets(asset_types)

def quick_sync():
    """Quick sync for testing - only stocks and top cryptos."""
    from .crypto_manager import sync_top_cryptos
    
    logger = logging.getLogger("lumia.quick_sync")
    logger.info("⚡ Starting QUICK SYNC (stocks + top 10 cryptos)")
    
    try:
        # Sync stocks
        logger.info("📊 Syncing stocks...")
        sync_stocks()
        
        # Sync top 10 cryptos
        logger.info("₿ Syncing top 10 cryptos...")
        sync_top_cryptos(10)
        
        logger.info("✅ Quick sync completed!")
        
    except Exception as e:
        logger.error(f"❌ Quick sync failed: {str(e)}")


# ========================================
# MAIN EXECUTION
# ========================================

if __name__ == "__main__":
    print("🎯 Lumia Master Asset Collector")
    print("=" * 60)
    
    # You can run different collection modes:
    
    # Option 1: Sync everything
    sync_all_assets()
    
    # Option 2: Sync specific assets
    # sync_specific_assets(['stocks', 'cryptos'])
    
    # Option 3: Quick sync for testing
    # quick_sync()