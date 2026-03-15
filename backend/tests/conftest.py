"""Shared pytest fixtures for Health1ERP test suite.

Uses an in-memory SQLite database (via aiosqlite) to avoid requiring
a real PostgreSQL instance during CI.
"""

import asyncio
import uuid
from datetime import date, datetime, timezone
from typing import AsyncGenerator

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy import event
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.core.database import Base, get_db
from app.core.security import create_access_token, get_password_hash
from app.main import app
from app.models.user import User, UserRole


# Use in-memory SQLite for tests (no Postgres needed)
TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"

engine = create_async_engine(TEST_DATABASE_URL, echo=False)
TestSessionLocal = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


@pytest.fixture(scope="session")
def event_loop():
    """Create a session-scoped event loop."""
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()


@pytest_asyncio.fixture(autouse=True)
async def setup_database():
    """Create all tables before each test and drop after."""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest_asyncio.fixture
async def db_session() -> AsyncGenerator[AsyncSession, None]:
    """Provide a transactional database session for tests."""
    async with TestSessionLocal() as session:
        yield session


@pytest_asyncio.fixture
async def client(db_session: AsyncSession) -> AsyncGenerator[AsyncClient, None]:
    """Provide an async HTTP test client with overridden DB dependency."""

    async def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac

    app.dependency_overrides.clear()


# ── User factory fixtures ──────────────────────────────────────────


async def _create_user(
    db: AsyncSession, role: UserRole, email: str | None = None
) -> User:
    """Helper to create a user in the test database."""
    user = User(
        id=uuid.uuid4(),
        email=email or f"{role.value.lower()}_{uuid.uuid4().hex[:6]}@test.com",
        phone=f"+1{uuid.uuid4().int % 10**10:010d}",
        password_hash=get_password_hash("TestPass123!"),
        first_name="Test",
        last_name=role.value,
        role=role,
        is_active=True,
    )
    db.add(user)
    await db.flush()
    await db.refresh(user)
    return user


@pytest_asyncio.fixture
async def admin_user(db_session: AsyncSession) -> User:
    return await _create_user(db_session, UserRole.Admin)


@pytest_asyncio.fixture
async def doctor_user(db_session: AsyncSession) -> User:
    return await _create_user(db_session, UserRole.Doctor)


@pytest_asyncio.fixture
async def nurse_user(db_session: AsyncSession) -> User:
    return await _create_user(db_session, UserRole.Nurse)


@pytest_asyncio.fixture
async def receptionist_user(db_session: AsyncSession) -> User:
    return await _create_user(db_session, UserRole.Receptionist)


@pytest_asyncio.fixture
async def pharmacist_user(db_session: AsyncSession) -> User:
    return await _create_user(db_session, UserRole.Pharmacist)


@pytest_asyncio.fixture
async def labtech_user(db_session: AsyncSession) -> User:
    return await _create_user(db_session, UserRole.LabTech)


@pytest_asyncio.fixture
async def accountant_user(db_session: AsyncSession) -> User:
    return await _create_user(db_session, UserRole.Accountant)


@pytest_asyncio.fixture
async def superadmin_user(db_session: AsyncSession) -> User:
    return await _create_user(db_session, UserRole.SuperAdmin)


# ── Auth header helpers ────────────────────────────────────────────


def auth_headers(user: User) -> dict[str, str]:
    """Return Authorization header dict for a given user."""
    token = create_access_token(user.id, user.role.value)
    return {"Authorization": f"Bearer {token}"}
