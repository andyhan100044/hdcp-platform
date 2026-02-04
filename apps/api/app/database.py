"""
Database Configuration
Async SQLAlchemy setup for PostgreSQL
"""
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.pool import QueuePool, NullPool
from app.config.settings import settings

# Determine pool class based on environment
poolclass = NullPool if settings.environment == "testing" else QueuePool

# Create async engine with connection pooling
engine = create_async_engine(
    settings.database_url,
    poolclass=poolclass,
    pool_size=20,  # Base number of connections
    max_overflow=30,  # Additional connections when needed
    pool_timeout=30,  # Timeout waiting for connection
    pool_recycle=3600,  # Recycle connections every hour
    pool_pre_ping=True,  # Validate connections before use
    echo=settings.database_echo,
    future=True,
)

# Create async session factory
AsyncSessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False
)


async def get_db() -> AsyncSession:
    """
    Dependency to get database session
    Usage: async def endpoint(db: AsyncSession = Depends(get_db)):
    """
    async with AsyncSessionLocal() as session:
        try:
            yield session
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


async def init_db():
    """Initialize database connection"""
    from app.models import base  # Import all models
    from app.core.base import Base
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def close_db():
    """Close database connection"""
    await engine.dispose()
