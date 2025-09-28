# database.py

import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy.pool import StaticPool

# Get database URL from environment or use default
DATABASE_URL = os.getenv(
    'DATABASE_URL', 
    "postgresql+psycopg2://postgres:root@localhost/lumia"
)

# Create engine with connection pooling
engine = create_engine(
    DATABASE_URL,
    echo=os.getenv('DEBUG_MODE', 'False').lower() == 'true',
    pool_pre_ping=True,  # Verify connections before use
    pool_recycle=3600,   # Recycle connections every hour
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# This is now the single source of truth for your Base.
Base = declarative_base()


def get_db():
    """
    Dependency to get database session.
    
    Yields:
        Session: SQLAlchemy database session
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def create_tables():
    """Create all tables defined by models."""
    Base.metadata.create_all(bind=engine)


def drop_tables():
    """Drop all tables (use with caution!)."""
    Base.metadata.drop_all(bind=engine)