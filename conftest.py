from __future__ import annotations

from typing import AsyncGenerator

import httpx
import pytest_asyncio
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import close_all_sessions
from sqlalchemy.pool import StaticPool

from app.db.base import Base
from app.db.database import get_db
from app.main import app

# Test database: in‑memory SQLite
TEST_DB_URL = "sqlite+aiosqlite:///:memory:"

engine = create_async_engine(
    TEST_DB_URL,
    echo=False,
    future=True,
    poolclass=StaticPool,  # keeps the same conn for :memory:
)

TestingSessionLocal = async_sessionmaker(
    engine, expire_on_commit=False, class_=AsyncSession
)


# Session‑wide DB setup / teardown
@pytest_asyncio.fixture(scope="session", autouse=True)
async def _prepare_database() -> AsyncGenerator[None, None]:
    """Create all tables at session start, drop at the end."""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    yield

    close_all_sessions()
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


# Per‑test AsyncSession
@pytest_asyncio.fixture
async def db() -> AsyncGenerator[AsyncSession, None]:
    """
    Drop & recreate all tables before each test to ensure a blank slate.
    """
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)

    async with TestingSessionLocal() as session:
        yield session


# FastAPI test client (ASGI)
@pytest_asyncio.fixture
async def client(db: AsyncSession) -> AsyncGenerator[AsyncClient, None]:
    async def _get_test_db() -> AsyncGenerator[AsyncSession, None]:
        yield db

    # dependency override
    app.dependency_overrides[get_db] = _get_test_db

    async with AsyncClient(
        base_url="http://test",
        transport=httpx.ASGITransport(app),
    ) as ac:
        yield ac

    app.dependency_overrides.clear()
