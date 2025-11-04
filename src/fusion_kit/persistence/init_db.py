"""
Database initialization script for multi-agent framework.

Creates all tables and initializes the SQLite database.
"""

import asyncio
import logging
from pathlib import Path

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

from fusion_kit.persistence.models import Base

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

# Database configuration
DATABASE_URL = "sqlite+aiosqlite:///./fusion_kit.db"


async def init_db(database_url: str = DATABASE_URL) -> None:
    """
    Initialize the database by creating all tables.

    Args:
        database_url: Database connection URL (default: SQLite)

    Raises:
        Exception: If database initialization fails
    """
    logger.info(f"Initializing database: {database_url}")

    engine = create_async_engine(
        database_url,
        echo=True,
        future=True,
    )

    async with engine.begin() as conn:
        logger.info("Creating all tables...")
        await conn.run_sync(Base.metadata.create_all)
        logger.info("Database initialization complete!")

    await engine.dispose()
    logger.info("Database connection closed")


def get_async_session_factory(database_url: str = DATABASE_URL):
    """
    Get an async session factory for database operations.

    Args:
        database_url: Database connection URL

    Returns:
        AsyncSession factory function
    """
    engine = create_async_engine(
        database_url,
        echo=False,
        future=True,
    )

    return sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


async def verify_db(database_url: str = DATABASE_URL) -> bool:
    """
    Verify that database is initialized and accessible.

    Args:
        database_url: Database connection URL

    Returns:
        True if database is verified, False otherwise
    """
    try:
        engine = create_async_engine(database_url, echo=False, future=True)
        async with engine.begin() as conn:
            # Try to query system tables
            result = await conn.execute("SELECT name FROM sqlite_master WHERE type='table';")
            tables = result.fetchall()
            logger.info(f"Database verified. Found {len(tables)} tables.")
            return len(tables) > 0
    except Exception as e:
        logger.error(f"Database verification failed: {e}")
        return False
    finally:
        await engine.dispose()


if __name__ == "__main__":
    # Run initialization when executed directly
    asyncio.run(init_db())
