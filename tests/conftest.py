"""
Pytest configuration and fixtures
"""
import pytest
import asyncio
from sqlalchemy import create_engine
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from httpx import AsyncClient
from api.main import app
from database.database import Base, get_db
from models.user import User, Organization, APIKey, PlanType, UserRole
from auth.jwt_handler import get_password_hash
import hashlib
import secrets

# Test database URL
TEST_DATABASE_URL = "sqlite+aiosqlite:///./test.db"

# Create test engine
test_engine = create_async_engine(TEST_DATABASE_URL, echo=False)
TestAsyncSessionLocal = sessionmaker(
    test_engine, class_=AsyncSession, expire_on_commit=False
)


@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
async def db_session():
    """Create a test database session."""
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    async with TestAsyncSessionLocal() as session:
        yield session
    
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest.fixture
async def client(db_session):
    """Create a test client."""
    async def override_get_db():
        yield db_session
    
    app.dependency_overrides[get_db] = override_get_db
    
    async with AsyncClient(app=app, base_url="http://test") as ac:
        yield ac
    
    app.dependency_overrides.clear()


@pytest.fixture
async def test_organization(db_session):
    """Create a test organization."""
    org = Organization(
        name="Test Organization",
        slug="test-org",
        plan_type=PlanType.FREE,
        monthly_request_limit=1000,
        monthly_token_limit=50000
    )
    db_session.add(org)
    await db_session.commit()
    await db_session.refresh(org)
    return org


@pytest.fixture
async def test_user(db_session, test_organization):
    """Create a test user."""
    user = User(
        email="test@example.com",
        full_name="Test User",
        hashed_password=get_password_hash("testpassword123"),
        organization_id=test_organization.id,
        role=UserRole.OWNER,
        is_active=True,
        is_verified=True
    )
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)
    return user


@pytest.fixture
async def test_api_key(db_session, test_user, test_organization):
    """Create a test API key."""
    key_string = secrets.token_hex(32)
    key_hash = hashlib.sha256(key_string.encode()).hexdigest()
    
    api_key = APIKey(
        name="Test API Key",
        key_hash=key_hash,
        key_prefix=f"llm_...{key_string[-8:]}",
        user_id=test_user.id,
        organization_id=test_organization.id,
        rate_limit_per_minute=60,
        rate_limit_per_hour=1000,
        rate_limit_per_day=10000
    )
    db_session.add(api_key)
    await db_session.commit()
    await db_session.refresh(api_key)
    
    # Return both the API key object and the raw key for testing
    return api_key, f"llm_{key_string}"


@pytest.fixture
async def authenticated_client(client, test_user):
    """Create an authenticated test client."""
    # Login to get token
    response = await client.post("/api/auth/login", data={
        "username": test_user.email,
        "password": "testpassword123"
    })
    assert response.status_code == 200
    
    token = response.json()["access_token"]
    client.headers.update({"Authorization": f"Bearer {token}"})
    
    return client