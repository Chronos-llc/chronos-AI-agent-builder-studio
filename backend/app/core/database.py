from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.pool import StaticPool

from app.core.config import settings

# Create async engine
engine = create_async_engine(
    settings.DATABASE_URL,
    echo=settings.DEBUG,
    poolclass=StaticPool,
    pool_pre_ping=True,
    connect_args={
        "check_same_thread": False,
    } if "sqlite" in settings.DATABASE_URL else {}
)

# Create session factory
SessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False
)

# Create base class for models
Base = declarative_base()


async def get_db() -> AsyncSession:
    """Dependency to get database session"""
    async with SessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()


async def create_db_and_tables():
    """Create database tables"""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def drop_db_and_tables():
    """Drop database tables (for development/testing)"""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)