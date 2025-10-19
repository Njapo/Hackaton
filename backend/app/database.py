"""
database.py - Database Configuration and Session Management

This file sets up the SQLAlchemy engine, session, and base class for ORM models.
It manages database connections and provides dependency injection for FastAPI routes.
"""

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Get database URL from environment variables
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./skinai.db")

# Create SQLAlchemy engine
# connect_args is only needed for SQLite to allow multiple threads
engine = create_engine(
    DATABASE_URL, 
    connect_args={"check_same_thread": False} if "sqlite" in DATABASE_URL else {}
)

# Create SessionLocal class for database sessions
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create Base class for ORM models
Base = declarative_base()


def get_db():
    """
    Database session dependency for FastAPI routes.
    
    Yields a database session and ensures it's closed after use.
    Usage in routes: db: Session = Depends(get_db)
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    """
    Initialize the database by creating all tables.
    
    This function should be called when the application starts.
    It creates all tables defined in models.py.
    """
    from . import models  # Import models to register them with Base
    Base.metadata.create_all(bind=engine)
