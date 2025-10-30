"""
Pytest configuration and fixtures for testing.
"""
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from database import get_db
from models.base import Base
from main import app


# Create in-memory SQLite database for testing
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(scope="function")
def db_session():
    """Create a fresh database session for each test."""
    Base.metadata.create_all(bind=engine)
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()
        Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="function")
def client(db_session):
    """Create a test client with database dependency override."""
    def override_get_db():
        try:
            yield db_session
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


@pytest.fixture
def sample_user_data():
    """Sample user data for testing."""
    return {
        "auth0_sub": "auth0|test123456",
        "email": "test@example.com",
        "name": "Test User",
        "role": "buyer"
    }


@pytest.fixture
def sample_artwork_data():
    """Sample artwork data for testing."""
    return {
        "title": "Test Artwork",
        "description": "A beautiful test piece",
        "artist": "Test Artist",
        "year": 2024,
        "image_url": "https://example.com/image.jpg",
        "starting_price": 100.00,
        "secret_threshold": 500.00,
        "current_price": 100.00,
        "status": "draft"
    }


@pytest.fixture
def sample_bid_data():
    """Sample bid data for testing."""
    return {
        "amount": 150.00,
        "bidder_id": 1,
        "artwork_id": 1
    }
