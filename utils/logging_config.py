"""
Logging configuration utilities for Lumia system.
Provides Unicode-safe logging setup for Windows environment.
"""

import logging
import logging.handlers
import sys
import os
from typing import Optional


class UnicodeFileHandler(logging.FileHandler):
    """File handler that explicitly uses UTF-8 encoding."""
    
    def __init__(self, filename, mode='a', encoding='utf-8', delay=False, errors='replace'):
        super().__init__(filename, mode, encoding, delay, errors)


class UnicodeStreamHandler(logging.StreamHandler):
    """Stream handler that safely handles Unicode characters."""
    
    def __init__(self, stream=None):
        super().__init__(stream)
        # Set encoding to UTF-8 for Windows console
        if hasattr(self.stream, 'reconfigure'):
            try:
                self.stream.reconfigure(encoding='utf-8', errors='replace')
            except Exception:
                pass
    
    def emit(self, record):
        try:
            msg = self.format(record)
            # Replace problematic Unicode characters for Windows console
            if sys.platform == 'win32':
                msg = self._safe_encode_for_windows(msg)
            
            stream = self.stream
            stream.write(msg + self.terminator)
            self.flush()
        except RecursionError:
            raise
        except Exception:
            self.handleError(record)
    
    def _safe_encode_for_windows(self, msg: str) -> str:
        """Replace Unicode characters that cause issues on Windows console."""
        # Map problematic Unicode characters to safe alternatives
        replacements = {
            '🚀': '[START]',
            '📊': '[DATA]',
            '✅': '[OK]',
            '❌': '[ERROR]',
            '⚠️': '[WARN]',
            '🎉': '[DONE]',
            '📈': '[SUMMARY]',
            'ℹ️': '[INFO]',
            '🔄': '[SYNC]',
            '💾': '[SAVE]',
            '🔍': '[SEARCH]',
            '📉': '[DOWN]',
            '📋': '[LIST]',
            '🌟': '[STAR]',
            '⭐': '[STAR]',
            '🔥': '[HOT]',
            '💡': '[IDEA]',
            '🎯': '[TARGET]',
            '🏆': '[WIN]',
            '📅': '[DATE]',
            '⏰': '[TIME]',
            '🔧': '[TOOL]',
            '📝': '[NOTE]',
            '💰': '[MONEY]',
            '📊': '[CHART]',
            '🚨': '[ALERT]',
            '🔔': '[NOTIFY]',
            '🌐': '[WEB]',
            '📡': '[SIGNAL]',
            '🎪': '[EVENT]',
        }
        
        for unicode_char, replacement in replacements.items():
            msg = msg.replace(unicode_char, replacement)
        
        # Handle any remaining Unicode characters
        try:
            msg.encode('cp1252')
            return msg
        except UnicodeEncodeError:
            # If there are still problematic characters, use ASCII-safe encoding
            return msg.encode('ascii', errors='replace').decode('ascii')


def setup_unicode_logging(
    name: str,
    level: str = 'INFO',
    log_file: Optional[str] = None,
    console: bool = True,
    max_bytes: int = 10485760,  # 10MB
    backup_count: int = 5
) -> logging.Logger:
    """
    Set up Unicode-safe logging for the application.
    
    Args:
        name: Logger name
        level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_file: Optional log file path
        console: Whether to log to console
        max_bytes: Maximum log file size before rotation
        backup_count: Number of backup files to keep
        
    Returns:
        Configured logger instance
    """
    # Create logger
    logger = logging.getLogger(name)
    logger.setLevel(getattr(logging, level.upper()))
    
    # Clear any existing handlers
    logger.handlers.clear()
    
    # Create formatter
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # Add console handler if requested
    if console:
        console_handler = UnicodeStreamHandler(sys.stdout)
        console_handler.setLevel(getattr(logging, level.upper()))
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)
    
    # Add file handler if log file specified
    if log_file:
        # Ensure log directory exists
        log_dir = os.path.dirname(log_file)
        if log_dir and not os.path.exists(log_dir):
            os.makedirs(log_dir, exist_ok=True)
        
        # Use rotating file handler with UTF-8 encoding
        file_handler = logging.handlers.RotatingFileHandler(
            log_file,
            maxBytes=max_bytes,
            backupCount=backup_count,
            encoding='utf-8',
            errors='replace'
        )
        file_handler.setLevel(getattr(logging, level.upper()))
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
    
    # Prevent duplicate logs from parent loggers
    logger.propagate = False
    
    return logger


def get_logger(name: str) -> logging.Logger:
    """Get or create a Unicode-safe logger."""
    if name not in logging.Logger.manager.loggerDict:
        return setup_unicode_logging(name)
    return logging.getLogger(name)


def configure_root_logging():
    """Configure root logging with Unicode safety."""
    # Configure root logger to use our Unicode-safe handlers
    root_logger = logging.getLogger()
    
    # Clear existing handlers
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)
    
    # Add our Unicode-safe console handler
    console_handler = UnicodeStreamHandler(sys.stdout)
    console_handler.setLevel(logging.INFO)
    formatter = logging.Formatter(
        '%(asctime)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    console_handler.setFormatter(formatter)
    root_logger.addHandler(console_handler)
    root_logger.setLevel(logging.INFO)


# Configure root logging when module is imported
configure_root_logging()