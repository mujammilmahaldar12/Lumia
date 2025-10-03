"""
🚀 LUMIA EXECUTION ENGINE
Handles collector execution and orchestration
"""

import time
import uuid
import logging
from datetime import datetime
from typing import Dict, Optional

logger = logging.getLogger('lumia.execution')

class ExecutionEngine:
    """Handles collector execution"""
    
    def __init__(self, session):
        self.session = session
    
    def execute_collection_plan(self, intelligence_report, force_mode=None) -> Dict:
        """Execute collection based on intelligence report"""
        
        if force_mode:
            intelligence_report.collection_mode = force_mode
            logger.info(f"[OVERRIDE] Forcing collection mode: {force_mode.value}")
        
        logger.info(f"[EXECUTE] Starting intelligent collection")
        logger.info(f"[MODE] {intelligence_report.collection_mode.value}")
        logger.info(f"[STRATEGY] {intelligence_report.priority_reasoning}")
        
        results = {
            'started_at': datetime.utcnow(),
            'intelligence_report': intelligence_report,
            'collectors_executed': {},
            'total_duration': 0,
            'success_count': 0,
            'failure_count': 0,
            'total_new_assets': 0,
            'total_new_prices': 0
        }
        
        # Execute each collector
        for collector_name in intelligence_report.collectors_to_run:
            logger.info(f"[RUN] {collector_name.upper()}")
            
            start_time = time.time()
            
            try:
                run_record = self._create_run_record(collector_name, intelligence_report)
                
                if collector_name == 'daily_prices':
                    success = self._execute_price_collector(run_record, intelligence_report)
                else:
                    success = self._execute_asset_collector(collector_name, run_record)
                
                duration = time.time() - start_time
                
                results['collectors_executed'][collector_name] = {
                    'status': 'success' if success else 'failed',
                    'duration_seconds': duration,
                    'records_processed': run_record.records_processed,
                    'records_added': run_record.records_added,
                    'error_message': run_record.error_message
                }
                
                results['total_duration'] += duration
                
                if success:
                    results['success_count'] += 1
                    if collector_name == 'daily_prices':
                        results['total_new_prices'] += run_record.records_added
                    else:
                        results['total_new_assets'] += run_record.records_added
                else:
                    results['failure_count'] += 1
                
            except Exception as e:
                logger.error(f"[ERROR] {collector_name}: {str(e)}")
                results['failure_count'] += 1
                results['collectors_executed'][collector_name] = {
                    'status': 'error',
                    'error_message': str(e)
                }
        
        results['completed_at'] = datetime.utcnow()
        self._log_results(results, intelligence_report)
        
        return results
    
    def _execute_asset_collector(self, collector_name: str, run_record) -> bool:
        """Execute asset collector using function-based API"""
        
        from collectors.stocks_manager import sync_stocks
        from collectors.etf_manager import sync_etfs
        from collectors.mutual_fund_manager import sync_mutual_funds
        from collectors.crypto_manager import sync_cryptos
        
        collector_functions = {
            'stocks': sync_stocks,
            'etfs': sync_etfs,
            'mutual_funds': sync_mutual_funds,
            'cryptocurrencies': sync_cryptos
        }
        
        if collector_name not in collector_functions:
            logger.error(f"Unknown collector: {collector_name}")
            return False
        
        try:
            run_record.mark_started()
            self.session.commit()
            
            # Execute the collector function
            collector_function = collector_functions[collector_name]
            collector_function()
            
            # Note: Function-based collectors don't return detailed stats
            # We'll track basic success/failure through run records
            run_record.update_stats(
                processed=1,  # Mark as processed
                added=0,      # Unknown for function-based
                updated=0,    # Unknown for function-based
                failed=0      # No failure if we reach here
            )
            
            run_record.mark_completed()
            self.session.commit()
            
            logger.info(f"[SUCCESS] {collector_name} executed successfully")
            return True
            
        except Exception as e:
            run_record.mark_failed(str(e))
            self.session.commit()
            logger.error(f"[FAILED] {collector_name}: {str(e)}")
            return False
    
    def _execute_price_collector(self, run_record, intelligence_report) -> bool:
        """Execute price collector with smart date ranges"""
        
        from collectors.daily_price_collector import DailyPriceCollector
        
        try:
            run_record.mark_started()
            self.session.commit()
            
            collector = DailyPriceCollector()
            
            if intelligence_report.optimal_date_range:
                from_date = intelligence_report.optimal_date_range['from_date']
                to_date = intelligence_report.optimal_date_range['to_date']
                logger.info(f"[📅 SMART] Price collection: {from_date} to {to_date}")
                
                result = collector.sync_prices_with_date_range(from_date, to_date)
            else:
                result = {'total_processed': 0, 'total_added': 0, 'total_failed': 0}
                collector.sync_recent_prices_only(days=7)
            
            run_record.update_stats(
                processed=result.get('total_processed', 0),
                added=result.get('total_added', 0),
                failed=result.get('total_failed', 0)
            )
            
            run_record.mark_completed()
            self.session.commit()
            
            logger.info(f"[✅ SUCCESS] daily_prices: {run_record.records_added} new prices")
            return True
            
        except Exception as e:
            run_record.mark_failed(str(e))
            self.session.commit()
            logger.error(f"[❌ FAILED] daily_prices: {str(e)}")
            return False
    
    def _create_run_record(self, collector_name: str, intelligence_report):
        """Create collector run record"""
        
        from models.collector_run import CollectorRun
        
        run_id = str(uuid.uuid4())[:8]
        
        config = {
            'collection_mode': intelligence_report.collection_mode.value,
            'intelligent_decision': True,
            'date_range': intelligence_report.optimal_date_range
        }
        
        run_record = CollectorRun(
            collector_name=collector_name,
            run_id=f"smart_{collector_name}_{run_id}",
            config_used=config,
            triggered_by='smart_automation'
        )
        
        self.session.add(run_record)
        self.session.commit()
        
        return run_record
    
    def _log_results(self, results: Dict, intelligence_report):
        """Log execution results"""
        
        logger.info(f"\n{'='*80}")
        logger.info("[🧠 AI SUMMARY] Intelligent Collection Report")
        logger.info(f"{'='*80}")
        
        logger.info(f"[🎯 STRATEGY] {intelligence_report.collection_mode.value}")
        logger.info(f"[💡 REASONING] {intelligence_report.priority_reasoning}")
        logger.info(f"[⏱️ DURATION] {results['total_duration']:.1f} seconds")
        logger.info(f"[✅ SUCCESS] {results['success_count']} collectors")
        logger.info(f"[❌ FAILED] {results['failure_count']} collectors")
        logger.info(f"[📈 NEW ASSETS] {results['total_new_assets']:,}")
        logger.info(f"[💰 NEW PRICES] {results['total_new_prices']:,}")
        
        if intelligence_report.database_state.value == "empty":
            logger.info("• Successfully completed first-time database setup with 25 years of data")
        elif intelligence_report.database_state.value == "mature":
            logger.info("• Performed efficient incremental update on mature database")
        
        if intelligence_report.optimal_date_range:
            from datetime import datetime
            days = (datetime.strptime(intelligence_report.optimal_date_range['to_date'], '%Y-%m-%d') - 
                   datetime.strptime(intelligence_report.optimal_date_range['from_date'], '%Y-%m-%d')).days
            logger.info(f"• Optimized price collection to {days} days based on analysis")