"""Tests for authentication utilities."""

from unittest.mock import MagicMock, patch

import pytest
from fastapi import HTTPException

from models.user import User
from utils.auth import get_current_user, require_role


class TestGetCurrentUser:
    """Test get_current_user authentication function."""

    @pytest.mark.asyncio
    async def test_get_current_user_missing_credentials(self, db_session):
        """Test get_current_user with missing credentials."""
        with pytest.raises(HTTPException) as exc_info:
            await get_current_user(credentials=None, db=db_session)

        assert exc_info.value.status_code == 401
        assert "Missing authentication credentials" in exc_info.value.detail

    @pytest.mark.asyncio
    @patch("utils.auth.AuthService.verify_auth0_token")
    async def test_get_current_user_auth0_success(self, mock_verify, db_session):
        """Test successful Auth0 authentication."""
        from schemas.auth import AuthUser

        # Mock Auth0 user
        mock_auth_user = AuthUser(
            sub="auth0|test123",
            email="test@example.com",
            name="Test User",
            picture="",
            email_verified=True,
            roles=["BUYER"],
        )
        mock_verify.return_value = mock_auth_user

        # Create mock credentials
        mock_creds = MagicMock()
        mock_creds.credentials = "valid_auth0_token"

        # Create or get user in DB
        user = User(auth0_sub="auth0|test123")
        user.email = "test@example.com"
        user.name = "Test User"
        user.role = "BUYER"
        db_session.add(user)
        db_session.commit()

        with patch("utils.auth.AuthService.get_or_create_user") as mock_get_user:
            mock_get_user.return_value = user
            result = await get_current_user(credentials=mock_creds, db=db_session)

        assert result.auth0_sub == "auth0|test123"
        assert result.email == "test@example.com"

    @pytest.mark.asyncio
    @patch("utils.auth.AuthService.verify_auth0_token")
    @patch("utils.auth.JWTService.verify_token")
    async def test_get_current_user_auth0_fails_jwt_succeeds(
        self, mock_jwt_verify, mock_auth0_verify, db_session
    ):
        """Test fallback to JWT when Auth0 fails."""
        # Auth0 fails
        mock_auth0_verify.side_effect = ValueError("Invalid Auth0 token")

        # JWT succeeds
        user = User(auth0_sub="auth0|jwt123")
        user.email = "jwt@example.com"
        user.name = "JWT User"
        user.role = "SELLER"
        db_session.add(user)
        db_session.commit()

        mock_jwt_verify.return_value = {
            "sub": "auth0|jwt123",
            "email": "jwt@example.com",
            "name": "JWT User",
            "role": "SELLER",
        }

        mock_creds = MagicMock()
        mock_creds.credentials = "valid_jwt_token"

        result = await get_current_user(credentials=mock_creds, db=db_session)

        assert result.auth0_sub == "auth0|jwt123"
        assert result.email == "jwt@example.com"
        assert result.role == "SELLER"

    @pytest.mark.asyncio
    @patch("utils.auth.AuthService.verify_auth0_token")
    @patch("utils.auth.JWTService.verify_token")
    async def test_get_current_user_jwt_by_user_id(
        self, mock_jwt_verify, mock_auth0_verify, db_session
    ):
        """Test JWT authentication with integer user ID (backward compatibility)."""
        # Auth0 fails
        mock_auth0_verify.side_effect = ValueError("Invalid Auth0 token")

        # Create user with integer ID
        user = User(auth0_sub="auth0|old123")
        user.email = "old@example.com"
        user.name = "Old User"
        user.role = "BUYER"
        db_session.add(user)
        db_session.commit()
        db_session.refresh(user)

        # JWT returns integer ID
        mock_jwt_verify.return_value = {
            "sub": str(user.id),
            "email": "old@example.com",
            "name": "Old User",
            "role": "BUYER",
        }

        mock_creds = MagicMock()
        mock_creds.credentials = "valid_jwt_token"

        result = await get_current_user(credentials=mock_creds, db=db_session)

        assert result.id == user.id
        assert result.email == "old@example.com"

    @pytest.mark.asyncio
    @patch("utils.auth.AuthService.verify_auth0_token")
    @patch("utils.auth.JWTService.verify_token")
    async def test_get_current_user_jwt_user_not_found(
        self, mock_jwt_verify, mock_auth0_verify, db_session
    ):
        """Test JWT authentication when user not in database."""
        # Auth0 fails
        mock_auth0_verify.side_effect = ValueError("Invalid Auth0 token")

        # JWT succeeds but user doesn't exist
        mock_jwt_verify.return_value = {
            "sub": "auth0|nonexistent",
            "email": "none@example.com",
            "name": "None User",
            "role": "BUYER",
        }

        mock_creds = MagicMock()
        mock_creds.credentials = "valid_jwt_token"

        with pytest.raises(HTTPException) as exc_info:
            await get_current_user(credentials=mock_creds, db=db_session)

        assert exc_info.value.status_code == 401
        assert "Invalid authentication credentials" in exc_info.value.detail

    @pytest.mark.asyncio
    @patch("utils.auth.AuthService.verify_auth0_token")
    @patch("utils.auth.JWTService.verify_token")
    async def test_get_current_user_all_methods_fail(
        self, mock_jwt_verify, mock_auth0_verify, db_session
    ):
        """Test when both Auth0 and JWT authentication fail."""
        # Auth0 fails
        mock_auth0_verify.side_effect = ValueError("Invalid Auth0 token")

        # JWT fails
        mock_jwt_verify.side_effect = Exception("Invalid JWT")

        mock_creds = MagicMock()
        mock_creds.credentials = "invalid_token"

        with pytest.raises(HTTPException) as exc_info:
            await get_current_user(credentials=mock_creds, db=db_session)

        assert exc_info.value.status_code == 401
        assert "Invalid authentication credentials" in exc_info.value.detail


class TestRequireRole:
    """Test role-based access control."""

    @pytest.mark.asyncio
    async def test_require_role_valid(self):
        """Test require_role with valid role."""
        user = MagicMock()
        user.role = "ADMIN"

        role_checker = require_role("ADMIN", "SELLER")
        result = role_checker(current_user=user)

        assert result == user

    @pytest.mark.asyncio
    async def test_require_role_invalid(self):
        """Test require_role with invalid role."""
        user = MagicMock()
        user.role = "BUYER"

        role_checker = require_role("ADMIN")

        with pytest.raises(HTTPException) as exc_info:
            role_checker(current_user=user)

        assert exc_info.value.status_code == 403
        assert "Insufficient permissions" in exc_info.value.detail

    @pytest.mark.asyncio
    async def test_require_role_no_role_attribute(self):
        """Test require_role when user has no role attribute."""
        user = MagicMock(spec=[])  # User without role attribute

        role_checker = require_role("BUYER")

        with pytest.raises(HTTPException) as exc_info:
            role_checker(current_user=user)

        assert exc_info.value.status_code == 403
