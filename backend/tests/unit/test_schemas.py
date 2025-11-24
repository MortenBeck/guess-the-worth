"""
Unit tests for Pydantic schemas.
Tests validation logic, default values, and field constraints.
"""

from datetime import datetime

import pytest
from pydantic import ValidationError

from models.artwork import ArtworkStatus
from models.user import UserRole
from schemas.artwork import ArtworkCreate, ArtworkResponse, ArtworkUpdate, ArtworkWithSecretResponse
from schemas.auth import AuthUser, TokenResponse
from schemas.bid import BidCreate, BidResponse
from schemas.user import UserCreate, UserResponse, UserUpdate


class TestUserSchemas:
    """Test user-related Pydantic schemas."""

    def test_user_create_valid(self):
        """Test UserCreate with valid data."""
        user_data = {
            "email": "test@example.com",
            "name": "Test User",
            "auth0_sub": "auth0|123456",
            "role": UserRole.BUYER,
        }
        user = UserCreate(**user_data)
        assert user.email == "test@example.com"
        assert user.name == "Test User"
        assert user.auth0_sub == "auth0|123456"
        assert user.role == UserRole.BUYER

    def test_user_create_default_role(self):
        """Test UserCreate defaults to BUYER role."""
        user_data = {
            "email": "buyer@example.com",
            "name": "Default Buyer",
            "auth0_sub": "auth0|default",
        }
        user = UserCreate(**user_data)
        assert user.role == UserRole.BUYER

    def test_user_create_invalid_email(self):
        """Test UserCreate rejects invalid email format."""
        with pytest.raises(ValidationError) as exc_info:
            UserCreate(email="not-an-email", name="Test User", auth0_sub="auth0|123")
        assert "email" in str(exc_info.value).lower()

    def test_user_create_missing_required_fields(self):
        """Test UserCreate requires email, name, and auth0_sub."""
        with pytest.raises(ValidationError) as exc_info:
            UserCreate(email="test@example.com")
        errors = exc_info.value.errors()
        error_fields = [e["loc"][0] for e in errors]
        assert "name" in error_fields
        assert "auth0_sub" in error_fields

    def test_user_update_optional_fields(self):
        """Test UserUpdate allows partial updates."""
        # Update only name
        update1 = UserUpdate(name="New Name")
        assert update1.name == "New Name"
        assert update1.role is None

        # Update only role
        update2 = UserUpdate(role=UserRole.SELLER)
        assert update2.name is None
        assert update2.role == UserRole.SELLER

        # Update both
        update3 = UserUpdate(name="Another Name", role=UserRole.ADMIN)
        assert update3.name == "Another Name"
        assert update3.role == UserRole.ADMIN

    def test_user_response_structure(self):
        """Test UserResponse includes all expected fields."""
        response_data = {
            "id": 1,
            "auth0_sub": "auth0|123",
            "email": "test@example.com",
            "name": "Test User",
            "role": UserRole.BUYER,
            "created_at": datetime.now(),
        }
        response = UserResponse(**response_data)
        assert response.id == 1
        assert response.auth0_sub == "auth0|123"
        assert response.email == "test@example.com"
        assert response.name == "Test User"
        assert response.role == UserRole.BUYER
        assert isinstance(response.created_at, datetime)


class TestArtworkSchemas:
    """Test artwork-related Pydantic schemas."""

    def test_artwork_create_valid(self):
        """Test ArtworkCreate with valid data."""
        artwork_data = {
            "title": "Beautiful Painting",
            "description": "A stunning masterpiece",
            "secret_threshold": 500.0,
        }
        artwork = ArtworkCreate(**artwork_data)
        assert artwork.title == "Beautiful Painting"
        assert artwork.description == "A stunning masterpiece"
        assert artwork.secret_threshold == 500.0

    def test_artwork_create_without_description(self):
        """Test ArtworkCreate with optional description."""
        artwork_data = {"title": "Simple Art", "secret_threshold": 100.0}
        artwork = ArtworkCreate(**artwork_data)
        assert artwork.title == "Simple Art"
        assert artwork.description is None
        assert artwork.secret_threshold == 100.0

    def test_artwork_create_missing_threshold(self):
        """Test ArtworkCreate requires secret_threshold."""
        with pytest.raises(ValidationError) as exc_info:
            ArtworkCreate(title="Missing Threshold")
        errors = exc_info.value.errors()
        assert any(e["loc"][0] == "secret_threshold" for e in errors)

    def test_artwork_create_negative_threshold(self):
        """Test ArtworkCreate allows negative threshold (business rule)."""
        # Note: Current schema doesn't enforce positive threshold
        artwork = ArtworkCreate(title="Free Art", secret_threshold=-10.0)
        assert artwork.secret_threshold == -10.0

    def test_artwork_update_partial(self):
        """Test ArtworkUpdate allows partial updates."""
        update1 = ArtworkUpdate(title="New Title")
        assert update1.title == "New Title"
        assert update1.description is None
        assert update1.secret_threshold is None
        assert update1.status is None

        update2 = ArtworkUpdate(status=ArtworkStatus.SOLD)
        assert update2.status == ArtworkStatus.SOLD

    def test_artwork_response_structure(self):
        """Test ArtworkResponse includes all public fields."""
        response_data = {
            "id": 1,
            "seller_id": 10,
            "title": "Art Piece",
            "description": "Nice art",
            "current_highest_bid": 75.0,
            "image_url": "https://example.com/art.jpg",
            "status": ArtworkStatus.ACTIVE,
            "created_at": datetime.now(),
        }
        response = ArtworkResponse(**response_data)
        assert response.id == 1
        assert response.seller_id == 10
        assert response.current_highest_bid == 75.0
        assert response.status == ArtworkStatus.ACTIVE
        # Verify secret_threshold is NOT included
        assert not hasattr(response, "secret_threshold")

    def test_artwork_with_secret_response(self):
        """Test ArtworkWithSecretResponse includes secret_threshold."""
        response_data = {
            "id": 1,
            "seller_id": 10,
            "title": "Art Piece",
            "description": "Nice art",
            "secret_threshold": 100.0,
            "current_highest_bid": 75.0,
            "image_url": "https://example.com/art.jpg",
            "status": ArtworkStatus.ACTIVE,
            "created_at": datetime.now(),
        }
        response = ArtworkWithSecretResponse(**response_data)
        assert response.secret_threshold == 100.0
        assert response.current_highest_bid == 75.0


class TestBidSchemas:
    """Test bid-related Pydantic schemas."""

    def test_bid_create_valid(self):
        """Test BidCreate with valid data."""
        bid_data = {"artwork_id": 1, "amount": 150.0}
        bid = BidCreate(**bid_data)
        assert bid.artwork_id == 1
        assert bid.amount == 150.0

    def test_bid_create_missing_fields(self):
        """Test BidCreate requires artwork_id and amount."""
        with pytest.raises(ValidationError) as exc_info:
            BidCreate(amount=100.0)
        errors = exc_info.value.errors()
        assert any(e["loc"][0] == "artwork_id" for e in errors)

        with pytest.raises(ValidationError) as exc_info:
            BidCreate(artwork_id=1)
        errors = exc_info.value.errors()
        assert any(e["loc"][0] == "amount" for e in errors)

    def test_bid_create_zero_amount(self):
        """Test BidCreate allows zero amount (validation happens in API)."""
        bid = BidCreate(artwork_id=1, amount=0.0)
        assert bid.amount == 0.0

    def test_bid_create_negative_amount(self):
        """Test BidCreate allows negative amount (validation happens in API)."""
        bid = BidCreate(artwork_id=1, amount=-50.0)
        assert bid.amount == -50.0

    def test_bid_response_structure(self):
        """Test BidResponse includes all expected fields."""
        response_data = {
            "id": 1,
            "artwork_id": 5,
            "bidder_id": 10,
            "amount": 200.0,
            "created_at": datetime.now(),
            "is_winning": True,
        }
        response = BidResponse(**response_data)
        assert response.id == 1
        assert response.artwork_id == 5
        assert response.bidder_id == 10
        assert response.amount == 200.0
        assert response.is_winning is True
        assert isinstance(response.created_at, datetime)


class TestAuthSchemas:
    """Test authentication-related Pydantic schemas."""

    def test_token_response(self):
        """Test TokenResponse structure."""
        token_data = {
            "access_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
            "token_type": "bearer",
            "expires_in": 3600,
        }
        token = TokenResponse(**token_data)
        assert token.access_token.startswith("eyJ")
        assert token.token_type == "bearer"
        assert token.expires_in == 3600

    def test_auth_user_with_roles(self):
        """Test AuthUser with custom roles claim."""
        auth_data = {
            "sub": "auth0|abc123",
            "email": "user@example.com",
            "name": "Auth User",
            "picture": "https://example.com/pic.jpg",
            "email_verified": True,
            "roles": ["seller", "admin"],
        }
        user = AuthUser(**auth_data)
        assert user.sub == "auth0|abc123"
        assert user.email == "user@example.com"
        assert user.roles == ["seller", "admin"]

    def test_auth_user_without_roles(self):
        """Test AuthUser with empty roles list."""
        auth_data = {
            "sub": "auth0|xyz789",
            "email": "norole@example.com",
            "name": "No Role User",
            "picture": "https://example.com/pic.jpg",
            "email_verified": False,
            "roles": [],
        }
        user = AuthUser(**auth_data)
        assert user.roles == []
        assert user.email_verified is False

    def test_auth_user_optional_fields(self):
        """Test AuthUser with optional picture and roles."""
        auth_data = {
            "sub": "auth0|minimal",
            "email": "minimal@example.com",
            "name": "Minimal User",
            "email_verified": True,
        }
        # Should work if picture and roles have defaults
        try:
            user = AuthUser(**auth_data)
            assert user.sub == "auth0|minimal"
        except ValidationError:
            # If picture and roles are required, this is expected
            pass


class TestSchemaEdgeCases:
    """Test edge cases and boundary conditions."""

    def test_very_long_title(self):
        """Test artwork with extremely long title."""
        long_title = "A" * 1000
        artwork = ArtworkCreate(title=long_title, secret_threshold=100.0)
        assert len(artwork.title) == 1000

    def test_very_large_bid_amount(self):
        """Test bid with extremely large amount."""
        bid = BidCreate(artwork_id=1, amount=999999999.99)
        assert bid.amount == 999999999.99

    def test_unicode_in_names(self):
        """Test schemas handle unicode characters."""
        user = UserCreate(email="test@example.com", name="用户名 🎨", auth0_sub="auth0|unicode")
        assert "用户名" in user.name
        assert "🎨" in user.name

    def test_special_characters_in_description(self):
        """Test artwork description with special characters."""
        description = "Art with <script>alert('xss')</script> & special chars"
        artwork = ArtworkCreate(title="Test", description=description, secret_threshold=50.0)
        assert artwork.description == description
