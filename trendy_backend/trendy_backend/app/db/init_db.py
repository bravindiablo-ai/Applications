"""
Database initialization and table creation script.
Handles both initial setup and migrations using Alembic.
"""
import logging
from sqlalchemy import inspect
from app.db.base import Base
from app.db.session import engine
from app.core.config import get_settings
from alembic.config import Config
from alembic import command

logger = logging.getLogger(__name__)

def init_db() -> None:
    """Initialize database, create tables if they don't exist, and run migrations."""
    settings = get_settings()
    
    # Check if any tables exist
    inspector = inspect(engine)
    tables = inspector.get_table_names()
    
    if not tables:
        logger.info("No tables found. Creating initial schema...")
        # Create all tables
        Base.metadata.create_all(bind=engine)
        logger.info("Initial schema created successfully")
        
        # Stamp the database with the current migration version
        alembic_cfg = Config("alembic.ini")
        command.stamp(alembic_cfg, "head")
        logger.info("Database stamped with current migration version")
    else:
        logger.info("Tables already exist. Running any pending migrations...")
        # Run any pending migrations
        alembic_cfg = Config("alembic.ini")
        command.upgrade(alembic_cfg, "head")
        logger.info("Migrations complete")

if __name__ == "__main__":
    init_db()