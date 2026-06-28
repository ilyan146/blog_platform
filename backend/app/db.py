"""Async database engine, session factory, and FastAPI dependency."""

from collections.abc import AsyncIterator

from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from app.config import settings
from app.models.orm import Base

# One engine per process. It owns the connection pool.
engine = create_async_engine(
    settings.database_url,
    pool_pre_ping=True,  # drop stale connections instead of erroring
    future=True,
)

SessionLocal = async_sessionmaker(
    bind=engine,
    expire_on_commit=False,  # let us read attributes after commit
    autoflush=False,
)


async def init_db() -> None:
    """Create any missing tables. Called once at startup.

    For production schema changes, swap this for Alembic migrations.
    """
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def get_db() -> AsyncIterator[AsyncSession]:
    """FastAPI dependency: yields a session and always closes it."""
    async with SessionLocal() as session:
        yield session
