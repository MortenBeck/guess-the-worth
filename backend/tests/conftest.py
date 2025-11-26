"""
Test configuration and fixtures for backend tests.
Provides database, client, and authentication mocks.
"""

from datetime import timedelta
from typing import Generator
from unittest.mock import patch

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from database import get_db
from main import app
from models.artwork import Artwork, ArtworkStatus
from models.base import Base
from models.bid import Bid
from models.user import User
from schemas.auth import AuthUser
from services.jwt_service import JWTService

# Test database setup with SQLite in-memory
SQLALCHEMY_TEST_DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(
    SQLALCHEMY_TEST_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)

# Enable foreign key constraints for SQLite


@event.listens_for(engine, "connect")
def set_sqlite_pragma(dbapi_conn, connection_record):
    cursor = dbapi_conn.cursor()
    cursor.execute("PRAGMA foreign_keys=ON")
    cursor.close()


TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(autouse=True)
def reset_rate_limiter():
    """Reset rate limiter state between tests to prevent interference."""
    try:
        from middleware.rate_limit import limiter

        # Clear the rate limiter storage before each test
        limiter.reset()
    except Exception:
        # If limiter doesn't have reset or isn't initialized, just pass
        pass
    yield


@pytest.fixture(scope="function")
def db_session() -> Generator:
    """
    Create a fresh database session for each test.
    Database is created and torn down for each test function.
    """
    Base.metadata.create_all(bind=engine)
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()
        Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="function")
def client(db_session) -> TestClient:
    """
    Create a test client with overridden database dependency.
    """

    def override_get_db():
        try:
            yield db_session
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db

    # Override the database engine used in startup event
    import database

    original_engine = database.engine
    database.engine = engine

    # Also patch the engine in main module
    import main

    original_main_engine = main.engine
    main.engine = engine

    try:
        with TestClient(app) as test_client:
            yield test_client
    finally:
        # Restore original engines
        database.engine = original_engine
        main.engine = original_main_engine
        app.dependency_overrides.clear()


# User fixtures
@pytest.fixture
def buyer_user(db_session) -> User:
    """Create a test buyer user."""
    user = User(auth0_sub="auth0|buyer123")
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    # Attach Auth0 data (simulated)
    user.email = "buyer@test.com"
    user.name = "Test Buyer"
    user.role = "BUYER"
    return user


@pytest.fixture
def seller_user(db_session) -> User:
    """Create a test seller user."""
    user = User(auth0_sub="auth0|seller123")
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    # Attach Auth0 data (simulated)
    user.email = "seller@test.com"
    user.name = "Test Seller"
    user.role = "SELLER"
    return user


@pytest.fixture
def admin_user(db_session) -> User:
    """Create a test admin user."""
    user = User(auth0_sub="auth0|admin123")
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    # Attach Auth0 data (simulated)
    user.email = "admin@test.com"
    user.name = "Test Admin"
    user.role = "ADMIN"
    return user


@pytest.fixture
def artwork(db_session, seller_user) -> Artwork:
    """Create a test artwork."""
    artwork = Artwork(
        seller_id=seller_user.id,
        title="Test Artwork",
        description="A beautiful test piece",
        secret_threshold=100.0,
        current_highest_bid=0.0,
        status=ArtworkStatus.ACTIVE,
    )
    db_session.add(artwork)
    db_session.commit()
    db_session.refresh(artwork)
    return artwork


@pytest.fixture
def sold_artwork(db_session, seller_user) -> Artwork:
    """Create a sold artwork for testing edge cases."""
    artwork = Artwork(
        seller_id=seller_user.id,
        title="Sold Artwork",
        description="Already sold",
        secret_threshold=100.0,
        current_highest_bid=150.0,
        status=ArtworkStatus.SOLD,
    )
    db_session.add(artwork)
    db_session.commit()
    db_session.refresh(artwork)
    return artwork


@pytest.fixture
def bid(db_session, artwork, buyer_user) -> Bid:
    """Create a test bid."""
    bid = Bid(artwork_id=artwork.id, bidder_id=buyer_user.id, amount=50.0, is_winning=False)
    db_session.add(bid)
    db_session.commit()
    db_session.refresh(bid)
    return bid


# JWT and Auth0 mocking fixtures
@pytest.fixture
def buyer_token(buyer_user) -> str:
    """Generate a valid JWT token for buyer user."""
    return JWTService.create_access_token(
        data={
            "sub": buyer_user.auth0_sub,
            "email": buyer_user.email,
            "name": buyer_user.name,
            "role": "BUYER",
        },
        expires_delta=timedelta(hours=1),
    )


@pytest.fixture
def seller_token(seller_user) -> str:
    """Generate a valid JWT token for seller user."""
    return JWTService.create_access_token(
        data={
            "sub": seller_user.auth0_sub,
            "email": seller_user.email,
            "name": seller_user.name,
            "role": "SELLER",
        },
        expires_delta=timedelta(hours=1),
    )


@pytest.fixture
def admin_token(admin_user) -> str:
    """Generate a valid JWT token for admin user."""
    return JWTService.create_access_token(
        data={
            "sub": admin_user.auth0_sub,
            "email": admin_user.email,
            "name": admin_user.name,
            "role": "ADMIN",
        },
        expires_delta=timedelta(hours=1),
    )


@pytest.fixture
def mock_auth0_response():
    """
    Mock Auth0 /userinfo endpoint response.
    Returns a factory function to create different Auth0 users.
    """

    def _create_auth0_user(
        sub: str = "auth0|test123",
        email: str = "test@example.com",
        name: str = "Test User",
        roles: list[str] = None,
    ) -> AuthUser:
        if roles is None:
            roles = ["buyer"]
        return AuthUser(
            sub=sub,
            email=email,
            name=name,
            picture="https://example.com/avatar.jpg",
            email_verified=True,
            roles=roles,
        )

    return _create_auth0_user


@pytest.fixture
def mock_auth0_service(mock_auth0_response):
    """
    Mock the auth_service.AuthService.verify_auth0_token function.
    Use this to avoid actual Auth0 API calls in tests.
    """
    with patch("services.auth_service.AuthService.verify_auth0_token") as mock:
        mock.return_value = mock_auth0_response()
        yield mock


# Helper functions for tests
def create_auth_header(token: str) -> dict:
    """Helper to create Authorization header."""
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def auth_headers(buyer_token):
    """Default authorization headers with buyer token."""
    return create_auth_header(buyer_token)
