"""
Background automation scheduler for Lumia financial system.

Handles scheduled execution of:
- News collection (hourly)
- Sentiment processing (hourly) 
- Signal generation (daily at market close)
"""

import asyncio
import logging
import os
import subprocess
import sys
from datetime import datetime, time
from pathlib import Path
from typing import Optional

from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.triggers.cron import CronTrigger
from apscheduler.events import EVENT_JOB_ERROR, EVENT_JOB_EXECUTED, EVENT_JOB_MISSED


def setup_logging():
    """Configure logging for scheduler."""
    log_level = os.getenv('SCHEDULER_LOG_LEVEL', 'INFO').upper()
    
    logging.basicConfig(
        level=getattr(logging, log_level),
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(),
            logging.FileHandler('logs/scheduler.log', mode='a')
        ]
    )
    
    return logging.getLogger(__name__)


class SchedulerService:
    """Background task scheduler for financial data processing."""
    
    def __init__(self):
        self.logger = setup_logging()
        self.scheduler = BlockingScheduler()
        self.scripts_dir = Path(__file__).parent / "scripts"
        
        # Load configuration
        self.news_collection_interval = int(os.getenv('NEWS_COLLECTION_INTERVAL_HOURS', '1'))
        self.sentiment_processing_interval = int(os.getenv('SENTIMENT_PROCESSING_INTERVAL_HOURS', '1'))
        self.market_close_hour = int(os.getenv('MARKET_CLOSE_HOUR', '16'))  # 4 PM EST
        self.market_close_minute = int(os.getenv('MARKET_CLOSE_MINUTE', '0'))
        self.timezone = os.getenv('SCHEDULER_TIMEZONE', 'America/New_York')
        
        # Register event listeners
        self.scheduler.add_listener(self._job_listener, EVENT_JOB_EXECUTED | EVENT_JOB_ERROR | EVENT_JOB_MISSED)
        
        self.logger.info("SchedulerService initialized")
    
    def _job_listener(self, event):
        """Handle job execution events."""
        if event.exception:
            self.logger.error(f"Job {event.job_id} crashed: {event.exception}")
        else:
            self.logger.info(f"Job {event.job_id} executed successfully")
    
    def _run_script(self, script_name: str, args: list = None) -> bool:
        """Execute a Python script with error handling."""
        try:
            script_path = self.scripts_dir / script_name
            if not script_path.exists():
                self.logger.error(f"Script not found: {script_path}")
                return False
            
            # Build command
            cmd = [sys.executable, str(script_path)]
            if args:
                cmd.extend(args)
            
            self.logger.info(f"Executing: {' '.join(cmd)}")
            
            # Run script
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=3600  # 1 hour timeout
            )
            
            if result.returncode == 0:
                self.logger.info(f"Script {script_name} completed successfully")
                if result.stdout.strip():
                    self.logger.debug(f"Script output: {result.stdout.strip()}")
                return True
            else:
                self.logger.error(f"Script {script_name} failed with code {result.returncode}")
                if result.stderr:
                    self.logger.error(f"Script error: {result.stderr.strip()}")
                return False
                
        except subprocess.TimeoutExpired:
            self.logger.error(f"Script {script_name} timed out after 1 hour")
            return False
        except Exception as e:
            self.logger.error(f"Failed to execute script {script_name}: {e}")
            return False
    
    def collect_news_job(self):
        """Scheduled job for news collection."""
        self.logger.info("Starting scheduled news collection...")
        
        # Collect news for all active assets
        success = self._run_script('collect_news.py', [
            '--all-assets',
            '--days', '1',  # Only collect last 24 hours of news
            '--limit', '50',  # Limit per symbol to avoid hitting API limits
            '--min-match-score', '0.7'  # Higher confidence for automated processing
        ])
        
        if success:
            self.logger.info("News collection completed successfully")
        else:
            self.logger.error("News collection failed")
        
        return success
    
    def process_sentiment_job(self):
        """Scheduled job for sentiment processing."""
        self.logger.info("Starting scheduled sentiment processing...")
        
        # Process all unprocessed articles with moderate batch size
        success = self._run_script('process_sentiment.py', [
            '--unprocessed',
            '--batch-size', '25',  # Conservative batch size for stability
            '--max-articles', '200'  # Limit to prevent overload
        ])
        
        if success:
            self.logger.info("Sentiment processing completed successfully")
        else:
            self.logger.error("Sentiment processing failed")
        
        return success
    
    def generate_signals_job(self):
        """Scheduled job for signal generation."""
        self.logger.info("Starting scheduled signal generation...")
        
        # Generate signals for all assets for today
        success = self._run_script('generate_signals.py', [
            '--all',
            '--force'  # Regenerate to ensure latest data
        ])
        
        if success:
            self.logger.info("Signal generation completed successfully")
        else:
            self.logger.error("Signal generation failed")
        
        return success
    
    def weekend_maintenance_job(self):
        """Weekend maintenance and cleanup job."""
        self.logger.info("Starting weekend maintenance...")
        
        try:
            # Show statistics
            self._run_script('process_sentiment.py', ['--stats'])
            self._run_script('generate_signals.py', ['--stats'])
            
            # Cleanup old logs (optional)
            self._cleanup_old_logs()
            
            self.logger.info("Weekend maintenance completed")
            return True
            
        except Exception as e:
            self.logger.error(f"Weekend maintenance failed: {e}")
            return False
    
    def _cleanup_old_logs(self, days_to_keep: int = 30):
        """Clean up old log files."""
        try:
            logs_dir = Path('logs')
            if not logs_dir.exists():
                return
            
            cutoff_date = datetime.now().timestamp() - (days_to_keep * 24 * 3600)
            
            for log_file in logs_dir.glob('*.log'):
                if log_file.stat().st_mtime < cutoff_date:
                    log_file.unlink()
                    self.logger.info(f"Deleted old log file: {log_file}")
                    
        except Exception as e:
            self.logger.warning(f"Log cleanup failed: {e}")
    
    def emergency_recovery_job(self):
        """Emergency recovery job for when main jobs fail."""
        self.logger.info("Running emergency recovery...")
        
        try:
            # Try to process any unprocessed articles from the last 3 days
            self._run_script('process_sentiment.py', [
                '--unprocessed',
                '--batch-size', '10',  # Very conservative
                '--max-articles', '50'
            ])
            
            # Generate signals for critical assets only
            critical_symbols = os.getenv('CRITICAL_SYMBOLS', 'SPY,QQQ,AAPL,MSFT,TSLA').split(',')
            if critical_symbols:
                self._run_script('generate_signals.py', [
                    '--symbols', ','.join(critical_symbols),
                    '--force'
                ])
            
            self.logger.info("Emergency recovery completed")
            
        except Exception as e:
            self.logger.error(f"Emergency recovery failed: {e}")
    
    def add_jobs(self):
        """Add all scheduled jobs to the scheduler."""
        
        # News collection - every hour during market hours (9 AM - 6 PM EST)
        self.scheduler.add_job(
            func=self.collect_news_job,
            trigger=CronTrigger(
                hour='9-18',
                minute='0',
                timezone=self.timezone,
                day_of_week='mon-fri'
            ),
            id='collect_news',
            name='News Collection',
            max_instances=1,
            coalesce=True,
            misfire_grace_time=300  # 5 minutes grace period
        )
        
        # Sentiment processing - every hour, offset by 30 minutes
        self.scheduler.add_job(
            func=self.process_sentiment_job,
            trigger=CronTrigger(
                hour='9-18',
                minute='30',
                timezone=self.timezone,
                day_of_week='mon-fri'
            ),
            id='process_sentiment',
            name='Sentiment Processing',
            max_instances=1,
            coalesce=True,
            misfire_grace_time=300
        )
        
        # Signal generation - daily at market close
        # Calculate the correct time (30 minutes after market close)
        signal_hour = self.market_close_hour
        signal_minute = self.market_close_minute + 30
        if signal_minute >= 60:
            signal_hour += 1
            signal_minute -= 60
        
        self.scheduler.add_job(
            func=self.generate_signals_job,
            trigger=CronTrigger(
                hour=signal_hour,
                minute=signal_minute,  # 30 minutes after close
                timezone=self.timezone,
                day_of_week='mon-fri'
            ),
            id='generate_signals',
            name='Signal Generation',
            max_instances=1,
            coalesce=True,
            misfire_grace_time=600  # 10 minutes grace period
        )
        
        # Weekend maintenance - Saturday at 2 AM
        self.scheduler.add_job(
            func=self.weekend_maintenance_job,
            trigger=CronTrigger(
                hour='2',
                minute='0',
                day_of_week='sat',
                timezone=self.timezone
            ),
            id='weekend_maintenance',
            name='Weekend Maintenance',
            max_instances=1
        )
        
        # Emergency recovery - twice daily at off-hours
        self.scheduler.add_job(
            func=self.emergency_recovery_job,
            trigger=CronTrigger(
                hour='7,19',  # 7 AM and 7 PM
                minute='0',
                timezone=self.timezone
            ),
            id='emergency_recovery',
            name='Emergency Recovery',
            max_instances=1
        )
        
        self.logger.info("All scheduled jobs added successfully")
    
    def start(self):
        """Start the scheduler."""
        try:
            # Ensure logs directory exists
            Path('logs').mkdir(exist_ok=True)
            
            self.logger.info("Starting Lumia automation scheduler...")
            self.logger.info(f"Configuration:")
            self.logger.info(f"  - News collection: Every {self.news_collection_interval} hour(s)")
            self.logger.info(f"  - Sentiment processing: Every {self.sentiment_processing_interval} hour(s)")
            self.logger.info(f"  - Signal generation: Daily at {self.market_close_hour}:{self.market_close_minute:02d}")
            self.logger.info(f"  - Timezone: {self.timezone}")
            
            self.add_jobs()
            
            # Print next run times
            self.logger.info("Next scheduled jobs:")
            for job in self.scheduler.get_jobs():
                try:
                    next_run = getattr(job, 'next_run_time', 'Not scheduled')
                    self.logger.info(f"  - {job.name}: {next_run}")
                except Exception as e:
                    self.logger.info(f"  - {job.name}: Unable to get next run time ({e})")
            
            # Start the scheduler
            self.scheduler.start()
            
        except KeyboardInterrupt:
            self.logger.info("Scheduler interrupted by user")
            self.shutdown()
        except Exception as e:
            self.logger.error(f"Scheduler failed to start: {e}")
            raise
    
    def shutdown(self):
        """Gracefully shutdown the scheduler."""
        self.logger.info("Shutting down scheduler...")
        self.scheduler.shutdown(wait=True)
        self.logger.info("Scheduler shutdown complete")


def main():
    """Main function to run the scheduler."""
    scheduler_service = SchedulerService()
    scheduler_service.start()


if __name__ == '__main__':
    main()