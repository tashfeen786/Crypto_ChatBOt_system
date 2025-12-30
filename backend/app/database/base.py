"""
Database base configuration
SQLAlchemy Base and Session management
"""

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from typing import Generator
import logging

from app.config import settings

logger = logging.getLogger(__name__)

# Create SQLAlchemy engine
engine = create_engine(
    settings.DATABASE_URL,
    pool_pre_ping=True,  # Verify connections before using
    echo=settings.DEBUG,  # Log SQL queries in debug mode
    pool_size=10,         # Connection pool size
    max_overflow=20       # Maximum overflow connections
)

# Create SessionLocal class
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

# Create Base class for models
Base = declarative_base()


def get_db() -> Generator[Session, None, None]:
    """
    Dependency for getting database session
    Usage in FastAPI endpoints:
    
    @app.get("/users")
    def get_users(db: Session = Depends(get_db)):
        return db.query(User).all()
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    """
    Initialize database
    Create all tables
    """
    try:
        logger.info("🗄️  Initializing database...")
        Base.metadata.create_all(bind=engine)
        logger.info("✅ Database initialized successfully!")
    except Exception as e:
        logger.error(f"❌ Error initializing database: {e}")
        raise


def drop_db():
    """
    Drop all tables (use with caution!)
    """
    logger.warning("⚠️  Dropping all database tables...")
    Base.metadata.drop_all(bind=engine)
    logger.warning("✅ All tables dropped!")


def check_db_connection() -> bool:
    """
    Check if database connection is working
    """
    try:
        db = SessionLocal()
        db.execute("SELECT 1")
        db.close()
        return True
    except Exception as e:
        logger.error(f"❌ Database connection failed: {e}")
        return False