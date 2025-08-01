"""
Database configuration and session management.
"""
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import StaticPool
import logging
from typing import Generator

from app.core.config import settings

logger = logging.getLogger(__name__)

# SQLAlchemy engine
engine = create_engine(
    settings.DATABASE_URL,
    pool_pre_ping=True,
    pool_recycle=300,
    pool_size=10,
    max_overflow=20,
)

# Session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class for models
Base = declarative_base()

def get_db() -> Generator[Session, None, None]:
    """
    Database session dependency.
    Use this in FastAPI path operations to get a database session.
    """
    try:
        db = SessionLocal()
        yield db
    finally:
        db.close()

def init_db() -> None:
    """
    Initialize database.
    Create all tables defined in models.
    """
    try:
        # Import all models here to ensure they are registered with SQLAlchemy
        from app.models import user, team, project, sprint, standup, backlog_item
        
        # Create all tables
        Base.metadata.create_all(bind=engine)
        logger.info("Database initialized successfully")
        
    except Exception as e:
        logger.error(f"Failed to initialize database: {e}")
        raise

def check_db_connection() -> bool:
    """
    Check if database connection is working.
    """
    try:
        with engine.connect() as connection:
            connection.execute("SELECT 1")
        return True
    except Exception as e:
        logger.error(f"Database connection failed: {e}")
        return False

# Database health check function
async def get_db_health() -> dict:
    """
    Get database health status.
    """
    try:
        is_connected = check_db_connection()
        return {
            "status": "healthy" if is_connected else "unhealthy",
            "database": "postgresql",
            "connection": is_connected
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "database": "postgresql", 
            "connection": False,
            "error": str(e)
        }