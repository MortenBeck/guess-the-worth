"""
Unit tests for authentication services.
Tests Auth0 integration, JWT operations, and role mapping.
"""

from datetime import datetime, timedelta
from unittest.mock import Mock, patch

import jwt
import pytest
from jwt import DecodeError, ExpiredSignatureError
from settings import Settings

from models.user import UserRole
from schemas.auth import AuthUser
from services.auth_service import AuthService
from services.jwt_service import JWTService


class TestAuth0Service:
    """Test Auth0-related service functions."""

    @patch("services.auth_service.requests.get")
    def test_verify_auth0_token_success(self, mock_get):
        """Test successful Auth0 token verification."""
        # Mock Auth0 /userinfo response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "sub": "auth0|test123",
            "email": "test@example.com",
            "name": "Test User",
            "picture": "https://example.com/pic.jpg",
            "email_verified": True,
            "https://guesstheworth.com/roles": ["buyer"],
        }
        mock_get.return_value = mock_response

        result = AuthService.verify_auth0_token("valid_token")

        assert isinstance(result, AuthUser)
        assert result.sub == "auth0|test123"
        assert result.email == "test@example.com"
        assert result.name == "Test User"
        assert result.roles == ["buyer"]
        mock_get.assert_called_once()

    @patch("services.auth_service.requests.get")
    def test_verify_auth0_token_invalid(self, mock_get):
        """Test Auth0 token verification with invalid token."""
        mock_response = Mock()
        mock_response.status_code = 401
        mock_get.return_value = mock_response

        with pytest.raises(ValueError, match="Invalid Auth0 token"):
            AuthService.verify_auth0_token("invalid_token")

    @patch("services.auth_service.requests.get")
    def test_verify_auth0_token_network_error(self, mock_get):
        """Test Auth0 token verification with network error."""
        mock_get.side_effect = Exception("Network error")

        with pytest.raises(Exception):
            AuthService.verify_auth0_token("token")

    @patch("services.auth_service.requests.get")
    def test_verify_auth0_token_no_roles(self, mock_get):
        """Test Auth0 token with missing roles claim."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "sub": "auth0|noroles",
            "email": "noroles@example.com",
            "name": "No Roles User",
            "picture": "https://example.com/pic.jpg",
            "email_verified": True,
        }
        mock_get.return_value = mock_response

        result = AuthService.verify_auth0_token("token")

        assert result.roles == []

    def test_map_auth0_role_to_user_role_buyer(self):
        """Test mapping Auth0 buyer role."""
        assert AuthService.map_auth0_role_to_user_role(["buyer"]) == UserRole.BUYER
        assert AuthService.map_auth0_role_to_user_role([]) == UserRole.BUYER  # Default

    def test_map_auth0_role_to_user_role_seller(self):
        """Test mapping Auth0 seller role."""
        assert AuthService.map_auth0_role_to_user_role(["seller"]) == UserRole.SELLER
        assert AuthService.map_auth0_role_to_user_role(["buyer", "seller"]) == UserRole.SELLER

    def test_map_auth0_role_to_user_role_admin(self):
        """Test mapping Auth0 admin role (highest priority)."""
        assert AuthService.map_auth0_role_to_user_role(["admin"]) == UserRole.ADMIN
        assert (
            AuthService.map_auth0_role_to_user_role(["buyer", "seller", "admin"]) == UserRole.ADMIN
        )
        assert AuthService.map_auth0_role_to_user_role(["admin", "seller"]) == UserRole.ADMIN

    def test_map_auth0_role_to_user_role_case_insensitive(self):
        """Test role mapping is case-insensitive."""
        assert AuthService.map_auth0_role_to_user_role(["ADMIN"]) == UserRole.ADMIN
        assert AuthService.map_auth0_role_to_user_role(["Seller"]) == UserRole.SELLER
        assert AuthService.map_auth0_role_to_user_role(["BuYeR"]) == UserRole.BUYER

    def test_map_auth0_role_unknown(self):
        """Test mapping unknown role defaults to BUYER."""
        assert AuthService.map_auth0_role_to_user_role(["unknown"]) == UserRole.BUYER
        assert AuthService.map_auth0_role_to_user_role(["moderator", "viewer"]) == UserRole.BUYER

    def test_get_user_by_auth0_sub_exists(self, db_session, buyer_user):
        """Test retrieving existing user by auth0_sub."""
        user = AuthService.get_user_by_auth0_sub(db_session, buyer_user.auth0_sub)
        assert user is not None
        assert user.id == buyer_user.id
        assert user.auth0_sub == buyer_user.auth0_sub

    def test_get_user_by_auth0_sub_not_exists(self, db_session):
        """Test retrieving non-existent user returns None."""
        user = AuthService.get_user_by_auth0_sub(db_session, "auth0|nonexistent")
        assert user is None

    def test_get_or_create_user_new_user(self, db_session):
        """Test creating new user from Auth0 data."""
        auth_user = AuthUser(
            sub="auth0|new123",
            email="newuser@example.com",
            name="New User",
            picture="https://example.com/pic.jpg",
            email_verified=True,
            roles=["seller"],
        )

        user = AuthService.get_or_create_user(db_session, auth_user)

        assert user.auth0_sub == "auth0|new123"
        assert user.email == "newuser@example.com"
        assert user.name == "New User"
        assert user.role == UserRole.SELLER

        # Verify user was persisted
        db_user = AuthService.get_user_by_auth0_sub(db_session, "auth0|new123")
        assert db_user is not None
        assert db_user.id == user.id

    def test_get_or_create_user_existing_user(self, db_session, buyer_user):
        """Test retrieving existing user without modification."""
        auth_user = AuthUser(
            sub=buyer_user.auth0_sub,
            email=buyer_user.email,
            name=buyer_user.name,
            picture="https://example.com/pic.jpg",
            email_verified=True,
            roles=["buyer"],
        )

        user = AuthService.get_or_create_user(db_session, auth_user)

        assert user.id == buyer_user.id
        assert user.role == UserRole.BUYER

    def test_get_or_create_user_role_update(self, db_session, buyer_user):
        """Test updating user role when Auth0 role changes."""
        auth_user = AuthUser(
            sub=buyer_user.auth0_sub,
            email=buyer_user.email,
            name=buyer_user.name,
            picture="https://example.com/pic.jpg",
            email_verified=True,
            roles=["admin"],  # Changed from buyer to admin
        )

        user = AuthService.get_or_create_user(db_session, auth_user)

        assert user.id == buyer_user.id
        assert user.role == UserRole.ADMIN  # Role should be updated

        # Verify persistence
        db_session.refresh(buyer_user)
        assert buyer_user.role == UserRole.ADMIN


class TestJWTService:
    """Test JWT token creation and verification."""

    def test_create_access_token_default_expiration(self):
        """Test creating JWT token with default expiration."""
        data = {"sub": "auth0|test123", "role": "buyer"}
        token = JWTService.create_access_token(data)

        assert token is not None
        assert isinstance(token, str)

        # Decode and verify
        settings = Settings()
        payload = jwt.decode(token, settings.jwt_secret_key, algorithms=["HS256"])
        assert payload["sub"] == "auth0|test123"
        assert payload["role"] == "buyer"
        assert "exp" in payload

    def test_create_access_token_custom_expiration(self):
        """Test creating JWT token with custom expiration."""
        data = {"sub": "auth0|test123"}
        expires_delta = timedelta(minutes=30)
        token = JWTService.create_access_token(data, expires_delta)

        settings = Settings()
        payload = jwt.decode(token, settings.jwt_secret_key, algorithms=["HS256"])

        # Verify expiration is approximately 30 minutes from now
        exp_time = datetime.utcfromtimestamp(payload["exp"])
        expected_time = datetime.utcnow() + timedelta(minutes=30)
        time_diff = abs((exp_time - expected_time).total_seconds())
        assert time_diff < 5  # Within 5 seconds tolerance

    def test_create_access_token_additional_claims(self):
        """Test creating JWT token with additional claims."""
        data = {"sub": "auth0|test123", "role": "seller", "custom_claim": "custom_value"}
        token = JWTService.create_access_token(data)

        settings = Settings()
        payload = jwt.decode(token, settings.jwt_secret_key, algorithms=["HS256"])
        assert payload["sub"] == "auth0|test123"
        assert payload["role"] == "seller"
        assert payload["custom_claim"] == "custom_value"

    def test_verify_token_valid(self):
        """Test verifying valid JWT token."""
        data = {"sub": "auth0|test123", "role": "buyer"}
        token = JWTService.create_access_token(data)

        payload = JWTService.verify_token(token)
        assert payload["sub"] == "auth0|test123"
        assert payload["role"] == "buyer"

    def test_verify_token_invalid_signature(self):
        """Test verifying token with invalid signature."""
        # Create token with wrong secret
        data = {"sub": "auth0|test123"}
        to_encode = data.copy()
        expire = datetime.utcnow() + timedelta(hours=1)
        to_encode.update({"exp": expire})
        fake_token = jwt.encode(to_encode, "wrong_secret", algorithm="HS256")

        with pytest.raises(DecodeError):
            JWTService.verify_token(fake_token)

    def test_verify_token_expired(self):
        """Test verifying expired JWT token."""
        data = {"sub": "auth0|test123"}
        expires_delta = timedelta(seconds=-1)  # Already expired
        token = JWTService.create_access_token(data, expires_delta)

        with pytest.raises(ExpiredSignatureError):
            JWTService.verify_token(token)

    def test_verify_token_malformed(self):
        """Test verifying malformed token."""
        with pytest.raises(DecodeError):
            JWTService.verify_token("not.a.valid.jwt.token")

    def test_decode_token_without_verification(self):
        """Test decoding token without verification."""
        data = {"sub": "auth0|test123", "role": "admin"}
        token = JWTService.create_access_token(data)

        payload = JWTService.decode_token(token)
        assert payload["sub"] == "auth0|test123"
        assert payload["role"] == "admin"

    def test_decode_token_expired_still_works(self):
        """Test decode_token works on expired tokens (no verification)."""
        data = {"sub": "auth0|expired"}
        expires_delta = timedelta(seconds=-1)
        token = JWTService.create_access_token(data, expires_delta)

        # verify_token should fail
        with pytest.raises(ExpiredSignatureError):
            JWTService.verify_token(token)

        # But decode_token should work (no verification)
        payload = JWTService.decode_token(token)
        assert payload["sub"] == "auth0|expired"


class TestAuthIntegration:
    """Integration tests for auth service components."""

    @patch("services.auth_service.requests.get")
    def test_full_auth0_to_database_flow(self, mock_get, db_session):
        """Test complete flow from Auth0 verification to user creation."""
        # Mock Auth0 response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "sub": "auth0|integration123",
            "email": "integration@test.com",
            "name": "Integration User",
            "picture": "https://example.com/pic.jpg",
            "email_verified": True,
            "https://guesstheworth.com/roles": ["seller"],
        }
        mock_get.return_value = mock_response

        # Verify token
        auth_user = AuthService.verify_auth0_token("mock_token")

        # Create user in database
        db_user = AuthService.get_or_create_user(db_session, auth_user)

        # Verify user was created correctly
        assert db_user.auth0_sub == "auth0|integration123"
        assert db_user.email == "integration@test.com"
        assert db_user.role == UserRole.SELLER

        # Verify user can be retrieved
        retrieved_user = AuthService.get_user_by_auth0_sub(db_session, "auth0|integration123")
        assert retrieved_user.id == db_user.id

    def test_jwt_and_database_integration(self, db_session, seller_user):
        """Test JWT token contains correct user data from database."""
        # Create JWT token
        token_data = {
            "sub": seller_user.auth0_sub,
            "role": seller_user.role.value,
            "email": seller_user.email,
        }
        token = JWTService.create_access_token(token_data)

        # Verify token
        payload = JWTService.verify_token(token)

        # Retrieve user from database using token data
        db_user = AuthService.get_user_by_auth0_sub(db_session, payload["sub"])

        assert db_user.id == seller_user.id
        assert db_user.role.value == payload["role"]
        assert db_user.email == payload["email"]

    @patch("services.auth_service.requests.get")
    def test_role_promotion_flow(self, mock_get, db_session):
        """Test user role promotion when Auth0 role changes."""
        # Initial user creation as buyer
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "sub": "auth0|promoted",
            "email": "promoted@test.com",
            "name": "Promoted User",
            "picture": "https://example.com/pic.jpg",
            "email_verified": True,
            "https://guesstheworth.com/roles": ["buyer"],
        }
        mock_get.return_value = mock_response

        auth_user1 = AuthService.verify_auth0_token("token1")
        user = AuthService.get_or_create_user(db_session, auth_user1)
        assert user.role == UserRole.BUYER

        # User gets promoted to seller in Auth0
        mock_response.json.return_value["https://guesstheworth.com/roles"] = ["seller"]
        auth_user2 = AuthService.verify_auth0_token("token2")
        updated_user = AuthService.get_or_create_user(db_session, auth_user2)

        # Same user, updated role
        assert updated_user.id == user.id
        assert updated_user.role == UserRole.SELLER
