"""
Collector Run Model - Tracks execution history of all data collectors

This model stores metadata about each collector run including:
- Execution status and timing
- Performance metrics 
- Error handling and retry information
- Data collection statistics
"""

from sqlalchemy import Column, Integer, String, DateTime, Float, Text, JSON, Boolean
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from database import Base

class CollectorRun(Base):
    __tablename__ = 'collector_runs'

    # Primary identification
    id = Column(Integer, primary_key=True)
    collector_name = Column(String(100), nullable=False, index=True)
    run_id = Column(String(50), nullable=False, unique=True)  # UUID for this specific run
    
    # Execution tracking
    status = Column(String(20), nullable=False, default='pending')  # pending, running, completed, failed, cancelled
    started_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    completed_at = Column(DateTime, nullable=True)
    duration_seconds = Column(Float, nullable=True)
    
    # Performance metrics
    records_processed = Column(Integer, default=0)
    records_added = Column(Integer, default=0)
    records_updated = Column(Integer, default=0)
    records_failed = Column(Integer, default=0)
    
    # Error handling
    error_message = Column(Text, nullable=True)
    retry_count = Column(Integer, default=0)
    max_retries = Column(Integer, default=3)
    
    # Configuration and metadata
    config_used = Column(JSON, nullable=True)  # Store the configuration parameters used
    version = Column(String(20), nullable=True)  # Collector version
    triggered_by = Column(String(50), default='scheduled')  # scheduled, manual, dependency
    
    # Dependencies and scheduling
    depends_on = Column(JSON, nullable=True)  # List of collector runs this depends on
    priority = Column(Integer, default=50)  # 0=highest, 100=lowest priority
    
    # Health and monitoring
    memory_usage_mb = Column(Float, nullable=True)
    cpu_time_seconds = Column(Float, nullable=True)
    api_calls_made = Column(Integer, default=0)
    rate_limit_hits = Column(Integer, default=0)
    
    # Data quality metrics
    data_quality_score = Column(Float, nullable=True)  # 0.0 to 100.0
    validation_errors = Column(JSON, nullable=True)
    
    # Flags
    is_incremental = Column(Boolean, default=True)
    force_full_refresh = Column(Boolean, default=False)
    
    # Audit trail
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f"<CollectorRun(id={self.id}, name='{self.collector_name}', status='{self.status}', records={self.records_processed})>"
    
    @property
    def success_rate(self):
        """Calculate success rate for processed records"""
        if self.records_processed == 0:
            return 0.0
        return ((self.records_added + self.records_updated) / self.records_processed) * 100
    
    @property
    def is_running(self):
        """Check if collector is currently running"""
        return self.status == 'running'
    
    @property
    def is_completed(self):
        """Check if collector completed successfully"""
        return self.status == 'completed'
    
    @property
    def is_failed(self):
        """Check if collector failed"""
        return self.status == 'failed'
    
    def mark_started(self):
        """Mark collector as started"""
        self.status = 'running'
        self.started_at = datetime.utcnow()
    
    def mark_completed(self, duration=None):
        """Mark collector as completed successfully"""
        self.status = 'completed'
        self.completed_at = datetime.utcnow()
        if duration:
            self.duration_seconds = duration
        elif self.started_at:
            self.duration_seconds = (self.completed_at - self.started_at).total_seconds()
    
    def mark_failed(self, error_message=None, duration=None):
        """Mark collector as failed"""
        self.status = 'failed'
        self.completed_at = datetime.utcnow()
        if error_message:
            self.error_message = error_message
        if duration:
            self.duration_seconds = duration
        elif self.started_at:
            self.duration_seconds = (self.completed_at - self.started_at).total_seconds()
    
    def increment_retry(self):
        """Increment retry counter"""
        self.retry_count += 1
        return self.retry_count <= self.max_retries
    
    def update_stats(self, processed=0, added=0, updated=0, failed=0, api_calls=0, rate_limits=0):
        """Update performance statistics"""
        self.records_processed += processed
        self.records_added += added
        self.records_updated += updated
        self.records_failed += failed
        self.api_calls_made += api_calls
        self.rate_limit_hits += rate_limits