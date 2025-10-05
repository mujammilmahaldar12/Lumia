"""
Database Helper for Streamlit Integration

This module provides database connection management for the Streamlit app,
handling SQLAlchemy sessions properly in Streamlit's caching context.

Why this is needed:
- Streamlit caches function results across reruns
- SQLAlchemy sessions need proper lifecycle management
- Prevents database connection leaks
- Provides clean database access patterns
"""

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from contextlib import contextmanager
import os
from typing import Generator
import streamlit as st

# Import database URL from parent directory
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))

from database import SQLALCHEMY_DATABASE_URL, Base

# Create engine (connection pool)
# pool_pre_ping=True ensures connections are alive before use
# pool_recycle=3600 recycles connections after 1 hour
engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    pool_pre_ping=True,
    pool_recycle=3600,
    echo=False  # Set to True for SQL debugging
)

# Create session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@contextmanager
def get_db_session() -> Generator[Session, None, None]:
    """
    Context manager for database sessions.
    
    Usage in Streamlit:
    ```python
    with get_db_session() as db:
        results = db.query(Asset).all()
    ```
    
    Why context manager:
    - Automatically closes session after use
    - Handles exceptions gracefully
    - Prevents connection leaks
    - Works well with Streamlit caching
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def get_db() -> Session:
    """
    Simple database session getter (for non-context manager usage).
    
    Usage:
    ```python
    db = get_db()
    try:
        results = db.query(Asset).all()
    finally:
        db.close()
    ```
    
    Note: Prefer get_db_session() context manager when possible.
    """
    return SessionLocal()


@st.cache_resource
def init_database():
    """
    Initialize database connection (cached by Streamlit).
    
    Why @st.cache_resource:
    - Runs only once when app starts
    - Reuses engine across all sessions
    - Prevents creating multiple connection pools
    - Improves performance
    
    Returns:
        Engine: SQLAlchemy engine instance
    """
    return engine


def check_database_connection() -> tuple[bool, str]:
    """
    Check if database connection is working.
    
    Returns:
        tuple: (is_connected: bool, message: str)
        
    Example:
    ```python
    is_connected, message = check_database_connection()
    if not is_connected:
        st.error(f"Database error: {message}")
    ```
    """
    try:
        with get_db_session() as db:
            # Try a simple query
            db.execute("SELECT 1")
        return True, "Database connection successful"
    except Exception as e:
        return False, f"Database connection failed: {str(e)}"


def get_asset_count() -> int:
    """
    Get total number of assets in database.
    
    This is useful for:
    - Checking if database has data
    - Displaying statistics in UI
    - Validating data availability
    
    Returns:
        int: Number of assets
    """
    try:
        with get_db_session() as db:
            from models.assets import Asset
            count = db.query(Asset).count()
            return count
    except Exception as e:
        print(f"Error getting asset count: {e}")
        return 0


def get_available_sectors() -> list[str]:
    """
    Get list of unique sectors from database.
    
    Used for:
    - Populating sector exclusion dropdown in UI
    - Showing available sectors to users
    - Filtering assets by sector
    
    Returns:
        list[str]: List of sector names
    """
    try:
        with get_db_session() as db:
            from models.assets import Asset
            from sqlalchemy import distinct
            
            sectors = db.query(distinct(Asset.sector)).filter(
                Asset.sector.isnot(None)
            ).all()
            
            return sorted([s[0] for s in sectors if s[0]])
    except Exception as e:
        print(f"Error getting sectors: {e}")
        return []


def get_available_industries() -> list[str]:
    """
    Get list of unique industries from database.
    
    Similar to get_available_sectors() but more granular.
    
    Returns:
        list[str]: List of industry names
    """
    try:
        with get_db_session() as db:
            from models.assets import Asset
            from sqlalchemy import distinct
            
            industries = db.query(distinct(Asset.industry)).filter(
                Asset.industry.isnot(None)
            ).all()
            
            return sorted([i[0] for i in industries if i[0]])
    except Exception as e:
        print(f"Error getting industries: {e}")
        return []


# Database health check on import
if __name__ != "__main__":
    # Only run check when imported (not when run directly)
    is_connected, message = check_database_connection()
    if not is_connected:
        print(f"⚠️  {message}")
    else:
        asset_count = get_asset_count()
        print(f"✅ Database connected: {asset_count} assets available")
