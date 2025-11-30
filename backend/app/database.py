"""
Database configuration and connection management
"""
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.pool import NullPool
from sqlalchemy import MetaData
from typing import AsyncGenerator

from app.core.config import settings

# SQLAlchemy metadata with naming convention for constraints
convention = {
    "ix": "ix_%(column_0_label)s",
    "uq": "uq_%(table_name)s_%(column_0_name)s",
    "ck": "ck_%(table_name)s_%(constraint_name)s",
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    "pk": "pk_%(table_name)s"
}

metadata = MetaData(naming_convention=convention)

# SQLAlchemy Base
Base = declarative_base(metadata=metadata)

# Create async engine with optimized settings
engine = create_async_engine(
    settings.DATABASE_URL,
    echo=settings.DEBUG,  # Enable SQL logging in debug mode
    pool_size=settings.DATABASE_POOL_SIZE,
    max_overflow=settings.DATABASE_MAX_OVERFLOW,
    pool_timeout=settings.DATABASE_POOL_TIMEOUT,
    pool_recycle=settings.DATABASE_POOL_RECYCLE,
    poolclass=NullPool if settings.is_testing else None,  # Disable pooling for tests
    future=True,
)

# Create async session factory
AsyncSessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)


# Backwards-compatible alias expected by some services
async def get_async_db() -> AsyncGenerator[AsyncSession, None]:
    """
    Dependency to get database session
    
    Yields:
        AsyncSession: Database session
    """
    async with AsyncSessionLocal() as session:
        try:
            yield session
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


# Preferred name used across the codebase
get_db = get_async_db


async def init_db() -> None:
    """
    Initialize database - create all tables
    """
    async with engine.begin() as conn:
        # Import all models to ensure they are registered
        from app.models import user, pet, adoption, notification, password_history  # noqa
        from app.models import chat_room, chat_message  # new chat models
        
        # Create all tables
        await conn.run_sync(Base.metadata.create_all)


async def close_db() -> None:
    """
    Close database connections
    """
    await engine.dispose()


# Health check function
async def check_database_connection() -> bool:
    """
    Check if database connection is healthy
    
    Returns:
        bool: True if connection is healthy, False otherwise
    """
    try:
        async with AsyncSessionLocal() as session:
            await session.execute("SELECT 1")
            return True
    except Exception:
        return False
