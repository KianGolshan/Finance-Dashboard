import os
os.environ["DATABASE_URL"] = "sqlite+aiosqlite://"
os.environ["DATABASE_URL_SYNC"] = "sqlite://"

import asyncio
import pytest
import pytest_asyncio
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.database import Base, get_db
from app.main import app

engine = create_async_engine("sqlite+aiosqlite://", echo=False)
test_session = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


@pytest.fixture(scope="session")
def event_loop():
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()


@pytest_asyncio.fixture(autouse=True)
async def setup_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest_asyncio.fixture
async def db():
    async with test_session() as session:
        yield session


@pytest_asyncio.fixture
async def client():
    # Use a single connection for all requests in a test so writes are visible to reads
    async with engine.connect() as conn:
        async with conn.begin():
            session = AsyncSession(bind=conn, expire_on_commit=False)

            async def override_db():
                yield session

            app.dependency_overrides[get_db] = override_db
            transport = ASGITransport(app=app)
            async with AsyncClient(transport=transport, base_url="http://test") as ac:
                yield ac

            app.dependency_overrides.clear()
