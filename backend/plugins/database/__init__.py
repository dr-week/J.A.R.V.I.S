'''Backend plugin providing a thin wrapper around SQLModel for CRUD operations.

Provides:
- `engine` – SQLModel engine using SQLite (or PostgreSQL if DATABASE_URL env var set).
- `get_session` – FastAPI dependency yielding an async session.
- Helper functions `create`, `read`, `update`, `delete` for generic models.
''' 

import os
from typing import Any, Optional, Type

from sqlmodel import SQLModel, select
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlalchemy.ext.asyncio import create_async_engine

# Determine DB URL – default to SQLite file defined in config.DB_PATH
from ...app import config

def database_url() -> str:
    """Resolve the URL at call time so tests and workers can configure it safely."""
    return os.getenv("DATABASE_URL", f"sqlite+aiosqlite:///{config.DB_PATH}")


engine = create_async_engine(database_url(), echo=False, future=True)


def _current_engine():
    """Return the configured engine, rebuilding it when an environment override changes."""
    global engine
    configured = database_url()
    if str(engine.url) != configured:
        engine = create_async_engine(configured, echo=False, future=True)
    return engine

async def get_session() -> AsyncSession:
    """FastAPI dependency that yields an async session."""
    async with AsyncSession(_current_engine()) as session:
        yield session

# Generic CRUD helpers – operate on SQLModel subclasses
async def create(session: AsyncSession, obj: SQLModel) -> SQLModel:
    session.add(obj)
    await session.commit()
    await session.refresh(obj)
    return obj

async def read(session: AsyncSession, model: Type[SQLModel], where_clause: Any) -> Optional[SQLModel]:
    result = await session.exec(select(model).where(where_clause))
    return result.first()

async def update(session: AsyncSession, obj: SQLModel) -> SQLModel:
    session.add(obj)
    await session.commit()
    await session.refresh(obj)
    return obj

async def delete(session: AsyncSession, obj: SQLModel) -> None:
    await session.delete(obj)
    await session.commit()

async def init_db() -> None:
    """Create tables for all SQLModel models that inherit from `SQLModel`.
    Called from the FastAPI lifespan event.
    """
    async with _current_engine().begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)
