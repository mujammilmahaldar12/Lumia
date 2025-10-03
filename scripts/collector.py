#!/usr/bin/env python3
"""
🚀 LUMIA COLLECTOR ORCHESTRATOR 🚀

Master controller for all data collection activities in the Lumia financial system.
This script manages, schedules, monitors, and maintains all data collectors.

Features:
- 📋 Automatic collector discovery and registration
- ⏰ Smart scheduling with dependency management  
- 🔄 Retry logic and error handling
- 📊 Performance monitoring and health checks
- 🧹 Data maintenance and cleanup
- 📈 Detailed reporting and analytics

Usage:
    python collector.py                 # Run daily collection cycle
    python collector.py --full-refresh # Force full data refresh
    python collector.py --status       # Show collector status
    python collector.py --cleanup      # Run maintenance cleanup
"""

import os
import sys
import time
import uuid
import json
import psutil
import logging
import argparse
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from concurrent.futures import ThreadPoolExecutor, as_completed

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database import SessionLocal
from models.collector_run import CollectorRun
from collectors.stocks_manager import StocksManager
from collectors.etf_manager import ETFManager
from collectors.mutual_fund_manager import MutualFundManager
from collectors.crypto_manager import CryptoManager
from collectors.daily_price_collector import DailyPriceCollector
from collector_utilities import CollectorMaintenanceManager, CollectorReporter

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(f'collector_orchestrator_{datetime.now().strftime("%Y%m%d")}.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger('lumia.collector_orchestrator')

@dataclass
class CollectorConfig:
    """Configuration for a single collector"""
    name: str
    class_ref: type
    priority: int = 50
    max_retries: int = 3
    timeout_minutes: int = 60
    depends_on: List[str] = None
    run_daily: bool = True
    run_weekends: bool = True
    description: str = ""
    
    def __post_init__(self):
        if self.depends_on is None:
            self.depends_on = []

class CollectorOrchestrator:
    """
    🎯 Master orchestrator for all Lumia data collectors
    
    Manages execution, monitoring, and maintenance of all data collection tasks
    """
    
    def __init__(self):
        self.session = SessionLocal()
        self.collectors: Dict[str, CollectorConfig] = {}
        self.current_runs: Dict[str, str] = {}  # collector_name -> run_id
        
        # Performance tracking
        self.start_time = datetime.utcnow()
        self.process = psutil.Process()
        
        logger.info("[INIT] Initializing Lumia Collector Orchestrator")
        self._register_collectors()
        self._setup_database()
    
    def _register_collectors(self):
        """📋 Register all available collectors with their configurations"""
        logger.info("[SETUP] Registering data collectors...")
        
        # Asset collectors - run first to ensure base data exists
        self.collectors['stocks'] = CollectorConfig(
            name='stocks',
            class_ref=StocksManager,
            priority=10,  # High priority
            timeout_minutes=30,
            description="NSE/BSE stocks and equity securities collection"
        )
        
        self.collectors['etfs'] = CollectorConfig(
            name='etfs',
            class_ref=ETFManager,
            priority=10,
            timeout_minutes=20,
            description="Exchange Traded Funds (ETF) data collection"
        )
        
        self.collectors['mutual_funds'] = CollectorConfig(
            name='mutual_funds',
            class_ref=MutualFundManager,
            priority=15,
            timeout_minutes=45,
            description="Mutual funds and AMFI data synchronization"
        )
        
        self.collectors['cryptocurrencies'] = CollectorConfig(
            name='cryptocurrencies',
            class_ref=CryptoManager,
            priority=20,
            timeout_minutes=15,
            description="Cryptocurrency data from CoinGecko API"
        )
        
        # Price collectors - depend on assets being available first
        self.collectors['daily_prices'] = CollectorConfig(
            name='daily_prices',
            class_ref=DailyPriceCollector,
            priority=30,  # Lower priority, runs after assets
            depends_on=['stocks', 'etfs', 'cryptocurrencies'],
            timeout_minutes=120,  # Longer timeout for price collection
            description="Daily price data collection for all assets"
        )
        
        logger.info(f"[OK] Registered {len(self.collectors)} collectors")
        for name, config in self.collectors.items():
            deps = f" (depends on: {', '.join(config.depends_on)})" if config.depends_on else ""
            logger.info(f"   [COLLECTOR] {name}: Priority {config.priority}{deps}")
    
    def _setup_database(self):
        """🗄️ Ensure database tables are created"""
        try:
            from database import Base, engine
            Base.metadata.create_all(engine, tables=[CollectorRun.__table__])
            logger.info("[OK] Database tables verified")
        except Exception as e:
            logger.error(f"❌ Database setup failed: {e}")
            raise
    
    def get_collector_status(self) -> Dict:
        """📊 Get comprehensive status of all collectors"""
        status = {
            'orchestrator': {
                'uptime_seconds': (datetime.utcnow() - self.start_time).total_seconds(),
                'memory_usage_mb': self.process.memory_info().rss / 1024 / 1024,
                'cpu_percent': self.process.cpu_percent()
            },
            'collectors': {},
            'summary': {
                'total_collectors': len(self.collectors),
                'currently_running': len(self.current_runs),
                'last_24h_runs': 0,
                'success_rate_24h': 0.0
            }
        }
        
        # Get recent runs from database
        yesterday = datetime.utcnow() - timedelta(days=1)
        recent_runs = self.session.query(CollectorRun)\
            .filter(CollectorRun.started_at >= yesterday)\
            .all()
        
        status['summary']['last_24h_runs'] = len(recent_runs)
        if recent_runs:
            successful = len([r for r in recent_runs if r.is_completed])
            status['summary']['success_rate_24h'] = (successful / len(recent_runs)) * 100
        
        # Individual collector status
        for name, config in self.collectors.items():
            last_run = self.session.query(CollectorRun)\
                .filter(CollectorRun.collector_name == name)\
                .order_by(CollectorRun.started_at.desc())\
                .first()
            
            collector_status = {
                'config': {
                    'priority': config.priority,
                    'depends_on': config.depends_on,
                    'description': config.description
                },
                'last_run': None,
                'currently_running': name in self.current_runs
            }
            
            if last_run:
                collector_status['last_run'] = {
                    'status': last_run.status,
                    'started_at': last_run.started_at.isoformat(),
                    'duration_seconds': last_run.duration_seconds,
                    'records_processed': last_run.records_processed,
                    'success_rate': last_run.success_rate,
                    'error_message': last_run.error_message
                }
            
            status['collectors'][name] = collector_status
        
        return status
    
    def _create_run_record(self, collector_name: str, config: CollectorConfig, 
                          force_full_refresh: bool = False) -> CollectorRun:
        """📝 Create new collector run record"""
        run_id = str(uuid.uuid4())[:8]
        
        run_record = CollectorRun(
            collector_name=collector_name,
            run_id=f"{collector_name}_{run_id}",
            priority=config.priority,
            max_retries=config.max_retries,
            depends_on=config.depends_on,
            force_full_refresh=force_full_refresh,
            config_used={
                'timeout_minutes': config.timeout_minutes,
                'description': config.description,
                'force_full_refresh': force_full_refresh
            }
        )
        
        self.session.add(run_record)
        self.session.commit()
        return run_record
    
    def _check_dependencies(self, collector_name: str, config: CollectorConfig) -> Tuple[bool, List[str]]:
        """🔗 Check if all dependencies are satisfied"""
        if not config.depends_on:
            return True, []
        
        failed_deps = []
        for dep in config.depends_on:
            # Check if dependency has completed successfully recently
            recent_success = self.session.query(CollectorRun)\
                .filter(CollectorRun.collector_name == dep)\
                .filter(CollectorRun.status == 'completed')\
                .filter(CollectorRun.started_at >= datetime.utcnow() - timedelta(hours=25))\
                .first()
            
            if not recent_success:
                failed_deps.append(dep)
        
        return len(failed_deps) == 0, failed_deps
    
    def _execute_collector(self, collector_name: str, config: CollectorConfig, 
                          run_record: CollectorRun) -> bool:
        """🏃‍♂️ Execute a single collector with monitoring"""
        logger.info(f"[RUN] Starting collector: {collector_name}")
        
        # Track execution
        run_record.mark_started()
        self.session.commit()
        self.current_runs[collector_name] = run_record.run_id
        
        try:
            # Initialize collector instance
            collector_instance = config.class_ref()
            
            # Execute based on collector type
            if hasattr(collector_instance, 'synchronize_all'):
                # Asset collectors (stocks, ETFs, mutual funds, crypto)
                result = collector_instance.synchronize_all()
                
                # Update statistics
                if isinstance(result, dict):
                    run_record.update_stats(
                        processed=result.get('total_processed', 0),
                        added=result.get('new_added', 0),
                        updated=result.get('updated', 0),
                        failed=result.get('failed', 0)
                    )
                
            elif hasattr(collector_instance, 'download_all_prices'):
                # Price collector - use intelligent date parameters if available
                if (collector_name == 'daily_prices' and hasattr(self, '_current_analysis') 
                    and self._current_analysis and self._current_analysis.get('optimal_date_range')):
                    
                    date_range = self._current_analysis['optimal_date_range']
                    from_date = date_range['from_date'] 
                    to_date = date_range['to_date']
                    
                    logger.info(f"[SMART DATES] Price collection from {from_date} to {to_date}")
                    
                    # Try intelligent collection with date parameters
                    try:
                        import inspect
                        # Check if methods support date parameters
                        stock_sig = inspect.signature(collector_instance.download_stock_prices)
                        crypto_sig = inspect.signature(collector_instance.download_crypto_prices)
                        
                        if len(stock_sig.parameters) >= 2 and len(crypto_sig.parameters) >= 2:
                            stock_result = collector_instance.download_stock_prices(from_date, to_date)
                            crypto_result = collector_instance.download_crypto_prices(from_date, to_date)
                        else:
                            # Fallback to standard collection
                            stock_result = collector_instance.download_stock_prices()
                            crypto_result = collector_instance.download_crypto_prices()
                            
                    except Exception as e:
                        logger.warning(f"[FALLBACK] Smart date collection failed, using standard: {e}")
                        stock_result = collector_instance.download_stock_prices()
                        crypto_result = collector_instance.download_crypto_prices()
                else:
                    # Standard price collection
                    stock_result = collector_instance.download_stock_prices()
                    crypto_result = collector_instance.download_crypto_prices()
                
                # Combine results
                total_processed = stock_result.get('total', 0) + crypto_result.get('total', 0)
                total_success = stock_result.get('success', 0) + crypto_result.get('success', 0)
                
                run_record.update_stats(
                    processed=total_processed,
                    added=total_success,
                    failed=total_processed - total_success
                )
            
            # Mark as completed
            run_record.mark_completed()
            logger.info(f"[DONE] Completed collector: {collector_name} ({run_record.records_processed} records)")
            return True
            
        except Exception as e:
            error_msg = str(e)
            logger.error(f"[ERROR] Failed collector {collector_name}: {error_msg}")
            run_record.mark_failed(error_msg)
            return False
            
        finally:
            # Cleanup
            if collector_name in self.current_runs:
                del self.current_runs[collector_name]
            
            # Update resource usage
            run_record.memory_usage_mb = self.process.memory_info().rss / 1024 / 1024
            run_record.cpu_time_seconds = sum(self.process.cpu_times()[:2])
            
            self.session.commit()
    
    def _analyze_existing_data(self) -> Dict:
        """🔍 Analyze what data we already have and determine collection strategy"""
        from models.assets import Asset
        from models.daily_price import DailyPrice
        
        logger.info("[ANALYZE] Analyzing existing data to determine collection strategy...")
        
        analysis = {
            'asset_counts': {},
            'price_data_coverage': {},
            'recommendations': [],
            'is_first_run': False,
            'needs_full_collection': False,
            'optimal_date_range': None
        }
        
        # Check asset counts by type
        total_assets = self.session.query(Asset).count()
        analysis['asset_counts']['total'] = total_assets
        
        # Count by asset type (we'll check actual type distribution)
        crypto_count = self.session.query(Asset).filter(Asset.symbol.like('%-CRYPTO')).count()
        analysis['asset_counts']['crypto'] = crypto_count
        
        etf_count = self.session.query(Asset).filter(Asset.symbol.like('%.ETF')).count()
        analysis['asset_counts']['etf'] = etf_count
        
        # Remaining are stocks/mutual funds
        analysis['asset_counts']['stocks_mf'] = total_assets - crypto_count - etf_count
        
        # Check price data coverage
        total_price_records = self.session.query(DailyPrice).count()
        analysis['price_data_coverage']['total_records'] = total_price_records
        
        if total_price_records > 0:
            # Get latest price date
            latest_price = self.session.query(DailyPrice.date).order_by(DailyPrice.date.desc()).first()
            oldest_price = self.session.query(DailyPrice.date).order_by(DailyPrice.date.asc()).first()
            
            if latest_price and oldest_price:
                analysis['price_data_coverage']['latest_date'] = latest_price[0]
                analysis['price_data_coverage']['oldest_date'] = oldest_price[0]
                
                # Calculate days since last price update
                days_since_update = (datetime.utcnow().date() - latest_price[0]).days
                analysis['price_data_coverage']['days_since_update'] = days_since_update
        
        # Determine collection strategy - BE MORE AGGRESSIVE!
        if total_assets == 0:
            analysis['is_first_run'] = True
            analysis['needs_full_collection'] = True
            analysis['recommendations'].append("FIRST RUN: Collect all asset types")
            logger.info("[STRATEGY] First run detected - will collect all assets")
            
        elif total_assets < 1000:
            analysis['needs_full_collection'] = True
            analysis['recommendations'].append("LOW ASSET COUNT: Collect more assets")
            logger.info(f"[STRATEGY] Only {total_assets} assets found - will refresh asset collection")
            
        # CRITICAL: Check if we have insufficient price coverage
        elif total_price_records < (total_assets * 0.1):  # Less than 10% price coverage
            analysis['needs_full_collection'] = True
            analysis['recommendations'].append(f"INSUFFICIENT PRICE DATA: Only {total_price_records} prices for {total_assets} assets")
            logger.info(f"[STRATEGY] INSUFFICIENT PRICE COVERAGE - {total_price_records} prices for {total_assets} assets - FORCE COLLECTION")
            
        else:
            logger.info(f"[STRATEGY] {total_assets} assets found - incremental update mode")
        
        # Determine price collection strategy - AGGRESSIVE COLLECTION
        if total_price_records == 0:
            analysis['recommendations'].append("NO PRICES: Collect last 90 days of price data")
            # Set date range for initial price collection - LONGER RANGE
            from datetime import timedelta
            end_date = datetime.utcnow().date()
            start_date = end_date - timedelta(days=90)  # More historical data
            analysis['optimal_date_range'] = {
                'from_date': start_date.strftime('%Y-%m-%d'),
                'to_date': end_date.strftime('%Y-%m-%d'),
                'days_to_collect': 90
            }
        elif total_price_records < (total_assets * 0.1):  # Less than 10% coverage
            analysis['recommendations'].append(f"SEVERE PRICE GAP: Only {total_price_records} prices for {total_assets} assets - collecting 60 days")
            from datetime import timedelta
            end_date = datetime.utcnow().date()
            start_date = end_date - timedelta(days=60)
            analysis['optimal_date_range'] = {
                'from_date': start_date.strftime('%Y-%m-%d'),
                'to_date': end_date.strftime('%Y-%m-%d'),
                'days_to_collect': 60
            }
            
        elif 'days_since_update' in analysis['price_data_coverage'] and analysis['price_data_coverage']['days_since_update'] > 1:
            analysis['recommendations'].append(f"STALE PRICES: Update last {analysis['price_data_coverage']['days_since_update']} days")
            # Set date range from last update to today
            start_date = analysis['price_data_coverage']['latest_date']
            end_date = datetime.utcnow().date()
            analysis['optimal_date_range'] = {
                'from_date': start_date.strftime('%Y-%m-%d'),
                'to_date': end_date.strftime('%Y-%m-%d'),
                'days_to_collect': (end_date - start_date).days
            }
            
        else:
            analysis['recommendations'].append("PRICES CURRENT: Collect today's prices only")
            today = datetime.utcnow().date()
            analysis['optimal_date_range'] = {
                'from_date': today.strftime('%Y-%m-%d'),
                'to_date': today.strftime('%Y-%m-%d'),
                'days_to_collect': 1
            }
        
        # Log analysis results
        logger.info("[DATA] Current state analysis:")
        logger.info(f"   Assets: {analysis['asset_counts']['total']} total")
        logger.info(f"   Crypto: {analysis['asset_counts']['crypto']}")
        logger.info(f"   ETFs: {analysis['asset_counts']['etf']}")  
        logger.info(f"   Stocks/MF: {analysis['asset_counts']['stocks_mf']}")
        logger.info(f"   Price Records: {analysis['price_data_coverage']['total_records']}")
        
        logger.info("[STRATEGY] Collection recommendations:")
        for rec in analysis['recommendations']:
            logger.info(f"   • {rec}")
            
        return analysis

    def run_daily_collection(self, force_full_refresh: bool = False) -> Dict:
        """🎯 Execute intelligent data collection cycle"""
        logger.info("[START] Starting intelligent data collection cycle")
        logger.info(f"[DATE] {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        # Analyze existing data first
        data_analysis = self._analyze_existing_data()
        
        # Store analysis for use during collector execution
        self._current_analysis = data_analysis
        
        # Override strategy if force refresh requested
        if force_full_refresh:
            data_analysis['needs_full_collection'] = True
            logger.info("[MODE] FORCED FULL REFRESH - Collecting all data")
        else:
            mode = "Full Collection" if data_analysis['needs_full_collection'] else "Incremental Update"
            logger.info(f"[MODE] {mode}")
        
        results = {
            'started_at': datetime.utcnow(),
            'analysis': data_analysis,
            'collectors_run': {},
            'total_duration': 0,
            'success_count': 0,
            'failure_count': 0,
            'total_records': 0
        }
        
        # Determine which collectors to run based on analysis
        collectors_to_run = []
        
        if data_analysis['is_first_run'] or data_analysis['needs_full_collection'] or force_full_refresh:
            # Run all asset collectors first, then prices
            asset_collectors = ['stocks', 'etfs', 'mutual_funds', 'cryptocurrencies']
            price_collectors = ['daily_prices']
            collectors_to_run = asset_collectors + price_collectors
            logger.info("[STRATEGY] Running full collection: assets + prices")
            
        else:
            # Smart incremental collection - BUT ALWAYS RUN PRICES
            if data_analysis['asset_counts']['total'] > 10000 and not data_analysis['needs_full_collection']:
                # Skip asset collection if we have enough assets AND sufficient price coverage
                collectors_to_run = ['daily_prices']
                logger.info("[STRATEGY] Sufficient assets found - collecting prices only")
            else:
                # Run asset collectors + prices (MORE AGGRESSIVE)
                collectors_to_run = ['stocks', 'etfs', 'mutual_funds', 'cryptocurrencies', 'daily_prices'] 
                logger.info("[STRATEGY] Running full collection: assets + prices (FORCED DUE TO INSUFFICIENT DATA)")
        
        # Filter and sort collectors to run
        collectors_to_execute = [
            (name, config) for name, config in self.collectors.items() 
            if name in collectors_to_run
        ]
        collectors_to_execute.sort(key=lambda x: x[1].priority)
        
        logger.info(f"[PLAN] Will execute {len(collectors_to_execute)} collectors: {[c[0] for c in collectors_to_execute]}")
        
        # Show intelligent collection plan
        if data_analysis['optimal_date_range']:
            date_range = data_analysis['optimal_date_range']
            logger.info(f"[SMART PLAN] Price collection: {date_range['from_date']} to {date_range['to_date']} ({date_range['days_to_collect']} days)")
        
        if data_analysis['recommendations']:
            logger.info("[AI RECOMMENDATIONS]")
            for i, rec in enumerate(data_analysis['recommendations'], 1):
                logger.info(f"   {i}. {rec}")
        
        for collector_name, config in collectors_to_execute:
            logger.info(f"\n{'='*60}")
            logger.info(f"[PROCESS] {collector_name.upper()}")
            logger.info(f"[DESC] {config.description}")
            
            # Check dependencies
            deps_satisfied, failed_deps = self._check_dependencies(collector_name, config)
            if not deps_satisfied:
                logger.warning(f"[SKIP] {collector_name} - dependencies not met: {failed_deps}")
                results['collectors_run'][collector_name] = {
                    'status': 'skipped',
                    'reason': f'Dependencies not satisfied: {failed_deps}'
                }
                continue
            
            # Create run record
            run_record = self._create_run_record(collector_name, config, force_full_refresh)
            
            # Execute collector
            start_time = time.time()
            success = self._execute_collector(collector_name, config, run_record)
            duration = time.time() - start_time
            
            # Record results
            results['collectors_run'][collector_name] = {
                'status': 'success' if success else 'failed',
                'duration_seconds': duration,
                'records_processed': run_record.records_processed,
                'records_added': run_record.records_added,
                'records_updated': run_record.records_updated,
                'error_message': run_record.error_message
            }
            
            results['total_duration'] += duration
            results['total_records'] += run_record.records_processed
            
            if success:
                results['success_count'] += 1
            else:
                results['failure_count'] += 1
                
                # If this collector failed, consider if dependents should be skipped
                if run_record.retry_count >= run_record.max_retries:
                    logger.error(f"💀 {collector_name} failed after {run_record.max_retries} retries")
        
        results['completed_at'] = datetime.utcnow()
        
        # Summary
        logger.info(f"\n{'='*60}")
        logger.info("[SUMMARY] DAILY COLLECTION SUMMARY")
        logger.info(f"[SUCCESS] {results['success_count']} collectors completed")
        logger.info(f"[FAILED] {results['failure_count']} collectors failed")
        logger.info(f"[RECORDS] {results['total_records']:,} total records processed")
        logger.info(f"[TIME] {results['total_duration']:.1f}s total execution time")
        logger.info(f"[RATE] {(results['success_count']/(results['success_count']+results['failure_count'])*100):.1f}% success rate")
        
        # Show what the AI learned/decided
        if hasattr(self, '_current_analysis') and self._current_analysis:
            analysis = self._current_analysis
            if analysis['is_first_run']:
                logger.info("[AI INSIGHT] First-time setup - collected complete dataset")
            elif analysis['asset_counts']['total'] > 10000:
                logger.info("[AI INSIGHT] Asset database is mature - focused on price updates")
            else:
                logger.info("[AI INSIGHT] Asset database growing - collected assets + prices")
                
            if analysis['optimal_date_range'] and 'daily_prices' in collectors_to_run:
                days = analysis['optimal_date_range']['days_to_collect']
                logger.info(f"[AI EFFICIENCY] Optimized price collection to {days} days instead of full history")
        
        return results

def main():
    """🎬 Main entry point"""
    parser = argparse.ArgumentParser(description='Lumia Collector Orchestrator')
    parser.add_argument('--full-refresh', action='store_true', 
                       help='Force full data refresh instead of incremental update')
    parser.add_argument('--status', action='store_true',
                       help='Show collector status and exit')
    parser.add_argument('--cleanup', action='store_true',
                       help='Run maintenance cleanup tasks')
    parser.add_argument('--report', choices=['daily', 'weekly', 'assets'], 
                       help='Generate specific reports')
    parser.add_argument('--date', type=str,
                       help='Specific date for reports (YYYY-MM-DD)')
    
    args = parser.parse_args()
    
    try:
        orchestrator = CollectorOrchestrator()
        
        if args.status:
            # Show status
            status = orchestrator.get_collector_status()
            print(json.dumps(status, indent=2, default=str))
            
        elif args.cleanup:
            # Run maintenance cleanup
            maintenance_manager = CollectorMaintenanceManager()
            
            logger.info("[CLEANUP] Running maintenance cleanup...")
            
            # Clean old runs
            run_cleanup = maintenance_manager.cleanup_old_runs(days_to_keep=30)
            logger.info(f"[OK] Cleaned {run_cleanup['deleted_runs']} old collector runs")
            
            # Remove duplicate prices
            price_cleanup = maintenance_manager.cleanup_duplicate_prices()
            logger.info(f"[OK] Removed {price_cleanup['records_removed']} duplicate price records")
            
            # Validate data integrity
            integrity_check = maintenance_manager.validate_data_integrity()
            if integrity_check['issues_found'] > 0:
                logger.warning(f"[WARN] Found {integrity_check['issues_found']} data integrity issues:")
                for issue in integrity_check['issues']:
                    logger.warning(f"   - {issue['description']}")
            else:
                logger.info("[OK] No data integrity issues found")
            
            # Optimize database
            optimization = maintenance_manager.optimize_database()
            logger.info("[OK] Database optimization completed")
            
            # Generate cleanup report
            reporter = CollectorReporter()
            asset_summary = reporter.get_asset_summary()
            
            logger.info("\n[SUMMARY] POST-CLEANUP SUMMARY")
            logger.info(f"[ASSETS] Total: {asset_summary['assets']['total']:,}")
            logger.info(f"[STOCKS] {asset_summary['assets']['stocks']:,}")
            logger.info(f"[ETFS] {asset_summary['assets']['etfs']:,}")
            logger.info(f"[FUNDS] {asset_summary['assets']['mutual_funds']:,}")
            logger.info(f"[CRYPTO] {asset_summary['assets']['cryptocurrencies']:,}")
            logger.info(f"[PRICES] {asset_summary['price_data']['total_records']:,} records")
            
        elif args.report:
            # Generate reports
            reporter = CollectorReporter()
            
            if args.report == 'daily':
                report_date = None
                if args.date:
                    report_date = datetime.strptime(args.date, '%Y-%m-%d').date()
                
                daily_report = reporter.generate_daily_report(report_date)
                print(json.dumps(daily_report, indent=2, default=str))
                
            elif args.report == 'weekly':
                trends = reporter.get_performance_trends(days=7)
                print(json.dumps(trends, indent=2, default=str))
                
            elif args.report == 'assets':
                asset_summary = reporter.get_asset_summary()
                print(json.dumps(asset_summary, indent=2, default=str))
            
        else:
            # Run daily collection
            results = orchestrator.run_daily_collection(
                force_full_refresh=args.full_refresh
            )
            
            # Exit with appropriate code
            if results['failure_count'] > 0:
                sys.exit(1)
                
    except KeyboardInterrupt:
        logger.info("[STOP] Collection interrupted by user")
        sys.exit(130)
    except Exception as e:
        logger.error(f"[CRITICAL] {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()
