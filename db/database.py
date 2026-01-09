"""
Async Database Configuration

Uses SQLAlchemy 2.0 async engine and session for non-blocking database operations.
- create_async_engine: Creates async database connection pool
- async_sessionmaker: Factory for creating AsyncSession instances
- get_db: Async dependency that yields database sessions for FastAPI routes
"""

from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import (
    create_async_engine,
    async_sessionmaker,
    AsyncSession,
)
from sqlalchemy.orm import declarative_base
from sqlalchemy.orm import declarative_base
from core.config import settings

# Get sync DATABASE_URL and convert to async driver
# postgresql://... -> postgresql+asyncpg://...
# sqlite:///... -> sqlite+aiosqlite:///...
SYNC_DATABASE_URL = settings.DATABASE_URL

if SYNC_DATABASE_URL.startswith("postgresql://"):
    DATABASE_URL = SYNC_DATABASE_URL.replace("postgresql://", "postgresql+asyncpg://", 1)
elif SYNC_DATABASE_URL.startswith("sqlite:///"):
    DATABASE_URL = SYNC_DATABASE_URL.replace("sqlite:///", "sqlite+aiosqlite:///", 1)
else:
    # Assume already async-compatible or other driver
    DATABASE_URL = SYNC_DATABASE_URL

# Async engine with connection pooling
engine = create_async_engine(
    DATABASE_URL,
    echo=False,
    future=True,
)

# Async session factory
AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autoflush=False,
    autocommit=False,
)

# Base class for ORM models (unchanged for Alembic compatibility)
Base = declarative_base()


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """
    Async dependency that yields a database session.
    Properly closes session after request completes.
    """
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()