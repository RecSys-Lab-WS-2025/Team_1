"""
Database configuration and session management using SQLAlchemy.
"""
from __future__ import annotations
from contextlib import asynccontextmanager
from pathlib import Path
from typing import Optional

from sqlalchemy.engine import make_url
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase

from .settings import Settings, get_settings


class Base(DeclarativeBase):
    """Base class for all database models."""
    pass


# Global engine and session factory
_engine = None
_async_session_maker: Optional[async_sessionmaker[AsyncSession]] = None


def _ensure_sqlite_directory(url: str) -> None:
    """
    Ensure the parent directory for the SQLite database file exists.
    """
    parsed = make_url(url)
    if parsed.database:
        Path(parsed.database).parent.mkdir(parents=True, exist_ok=True)


def get_database_url(settings: Settings) -> str:
    """
    Construct the database URL from settings and normalize based on driver.
    """
    url = settings.database_url.strip()

    if url.startswith("sqlite+aiosqlite://"):
        _ensure_sqlite_directory(url)
        return url
    if url.startswith("sqlite:///"):
        normalized = url.replace("sqlite:///", "sqlite+aiosqlite:///", 1)
        _ensure_sqlite_directory(normalized)
        return normalized
    if url.startswith("sqlite://"):
        normalized = url.replace("sqlite://", "sqlite+aiosqlite://", 1)
        _ensure_sqlite_directory(normalized)
        return normalized

    if url.startswith("postgresql+asyncpg://"):
        return url
    if url.startswith("postgresql://"):
        return url.replace("postgresql://", "postgresql+asyncpg://", 1)
    if url.startswith("postgres://"):
        return url.replace("postgres://", "postgresql+asyncpg://", 1)

    raise ValueError(
        "Unsupported DATABASE_URL. Use sqlite+aiosqlite:///path/to/db.sqlite "
        "or supply a postgresql+asyncpg:// URL with the appropriate driver installed."
    )


def init_db(settings: Optional[Settings] = None) -> None:
    """
    Initialize the database engine and session factory.
    
    Parameters
    ----------
    settings:
        Optional Settings instance; if omitted the global application settings are used.
    """
    global _engine, _async_session_maker
    
    if settings is None:
        settings = get_settings()
    
    database_url = get_database_url(settings)
    
    engine_kwargs: dict[str, object] = {
        "echo": False,
        "future": True,
    }

    if database_url.startswith("sqlite+aiosqlite://"):
        engine_kwargs["pool_pre_ping"] = False
    else:
        engine_kwargs.update({"pool_pre_ping": True, "pool_size": 10, "max_overflow": 20})

    # Create async engine
    _engine = create_async_engine(database_url, **engine_kwargs)
    
    # Create session factory
    _async_session_maker = async_sessionmaker(
        _engine,
        class_=AsyncSession,
        expire_on_commit=False,
        autocommit=False,
        autoflush=False,
    )


async def close_db() -> None:
    """Close the database engine."""
    global _engine
    if _engine:
        await _engine.dispose()


async def get_db():
    """
    Dependency for getting a database session.
    
    Usage:
        @app.get("/items")
        async def get_items(db: AsyncSession = Depends(get_db)):
            ...
    """
    if _async_session_maker is None:
        init_db()
    
    async with _async_session_maker() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


async def get_db_session() -> AsyncSession:
    """
    Get a database session (alternative to context manager).
    Remember to close the session after use.
    """
    if _async_session_maker is None:
        init_db()
    
    return _async_session_maker()

