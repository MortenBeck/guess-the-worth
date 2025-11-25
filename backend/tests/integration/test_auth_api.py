"""
Integration tests for authentication API endpoints.
Tests /api/auth routes with database and Auth0 mocking.
"""

from unittest.mock import patch

from models.user import UserRole


class TestAuthRegistration:
    """Test POST /api/auth/register endpoint."""

    def test_register_new_user_success(self, client, db_session):
        """Test successful new user registration."""
        payload = {
            "email": "newuser@example.com",
            "name": "New User",
            "auth0_sub": "auth0|newuser123",
            "role": "BUYER",
        }

        response = client.post("/api/auth/register", json=payload)

        assert response.status_code == 200
        data = response.json()
        assert data["email"] == "newuser@example.com"
        assert data["name"] == "New User"
        assert data["auth0_sub"] == "auth0|newuser123"
        assert data["role"] == "BUYER"
        assert "id" in data
        assert "created_at" in data

    def test_register_duplicate_auth0_sub(self, client, buyer_user):
        """Test registering user with duplicate auth0_sub fails."""
        payload = {
            "email": "different@example.com",
            "name": "Different Name",
            "auth0_sub": buyer_user.auth0_sub,  # Duplicate
            "role": "BUYER",
        }

        response = client.post("/api/auth/register", json=payload)

        # Should fail due to unique constraint
        assert response.status_code == 400

    def test_register_duplicate_email(self, client, buyer_user):
        """Test registering user with duplicate email fails."""
        payload = {
            "email": buyer_user.email,  # Duplicate
            "name": "Different Name",
            "auth0_sub": "auth0|different123",
            "role": "BUYER",
        }

        response = client.post("/api/auth/register", json=payload)

        # Should fail due to unique constraint
        assert response.status_code == 400

    def test_register_invalid_email(self, client):
        """Test registration with invalid email format."""
        payload = {
            "email": "not-an-email",
            "name": "Test User",
            "auth0_sub": "auth0|test123",
            "role": "BUYER",
        }

        response = client.post("/api/auth/register", json=payload)

        assert response.status_code == 422  # Validation error

    def test_register_missing_required_fields(self, client):
        """Test registration with missing required fields."""
        # Missing name
        response = client.post(
            "/api/auth/register", json={"email": "test@example.com", "auth0_sub": "auth0|test"}
        )
        assert response.status_code == 422

        # Missing auth0_sub
        response = client.post(
            "/api/auth/register", json={"email": "test@example.com", "name": "Test User"}
        )
        assert response.status_code == 422

    def test_register_with_seller_role(self, client):
        """Test registering a seller user."""
        payload = {
            "email": "seller@example.com",
            "name": "Seller User",
            "auth0_sub": "auth0|seller123",
            "role": "SELLER",
        }

        response = client.post("/api/auth/register", json=payload)

        assert response.status_code == 200
        data = response.json()
        assert data["role"] == "SELLER"

    def test_register_with_admin_role(self, client):
        """Test registering an admin user."""
        payload = {
            "email": "admin@example.com",
            "name": "Admin User",
            "auth0_sub": "auth0|admin123",
            "role": "ADMIN",
        }

        response = client.post("/api/auth/register", json=payload)

        assert response.status_code == 200
        data = response.json()
        assert data["role"] == "ADMIN"

    def test_register_default_role(self, client):
        """Test registration defaults to BUYER role."""
        payload = {
            "email": "default@example.com",
            "name": "Default User",
            "auth0_sub": "auth0|default123",
        }

        response = client.post("/api/auth/register", json=payload)

        assert response.status_code == 200
        data = response.json()
        assert data["role"] == "BUYER"


class TestAuthGetCurrentUser:
    """Test GET /api/auth/me endpoint."""

    @patch("services.auth_service.AuthService.verify_auth0_token")
    def test_get_current_user_success(self, mock_verify, client, buyer_user, buyer_token):
        """Test retrieving current user with JWT token."""
        # Mock Auth0 to fallback to JWT
        mock_verify.side_effect = Exception("Auth0 not available")

        headers = {"Authorization": f"Bearer {buyer_token}"}
        response = client.get("/api/auth/me", headers=headers)

        assert response.status_code == 200
        data = response.json()
        assert data["id"] == buyer_user.id
        assert data["auth0_sub"] == buyer_user.auth0_sub
        assert data["email"] == buyer_user.email
        assert data["name"] == buyer_user.name
        assert data["role"] == buyer_user.role.value

    def test_get_current_user_not_found(self, client):
        """Test request without authentication returns 401."""
        response = client.get("/api/auth/me")

        assert response.status_code == 401
        assert "authentication" in response.json()["detail"].lower()

    @patch("services.auth_service.AuthService.verify_auth0_token")
    def test_get_current_user_missing_auth0_sub(self, mock_verify, client):
        """Test request with invalid token returns 401."""
        mock_verify.side_effect = Exception("Auth0 not available")

        headers = {"Authorization": "Bearer invalid.token"}
        response = client.get("/api/auth/me", headers=headers)

        assert response.status_code == 401

    def test_get_current_user_empty_auth0_sub(self, client):
        """Test request with missing Authorization header."""
        response = client.get("/api/auth/me")

        assert response.status_code == 401

    @patch("services.auth_service.AuthService.verify_auth0_token")
    def test_get_current_user_seller(self, mock_verify, client, seller_user, seller_token):
        """Test retrieving seller user with JWT."""
        mock_verify.side_effect = Exception("Auth0 not available")

        headers = {"Authorization": f"Bearer {seller_token}"}
        response = client.get("/api/auth/me", headers=headers)

        assert response.status_code == 200
        data = response.json()
        assert data["role"] == "SELLER"

    @patch("services.auth_service.AuthService.verify_auth0_token")
    def test_get_current_user_admin(self, mock_verify, client, admin_user, admin_token):
        """Test retrieving admin user with JWT."""
        mock_verify.side_effect = Exception("Auth0 not available")

        headers = {"Authorization": f"Bearer {admin_token}"}
        response = client.get("/api/auth/me", headers=headers)

        assert response.status_code == 200
        data = response.json()
        assert data["role"] == "ADMIN"


class TestAuthWithJWT:
    """Test authentication using JWT tokens."""

    @patch("services.auth_service.AuthService.verify_auth0_token")
    def test_protected_endpoint_with_jwt(self, mock_verify, client, buyer_user, buyer_token):
        """Test accessing protected endpoint with JWT token."""
        # Mock Auth0 verification to return None (fallback to JWT)
        mock_verify.side_effect = Exception("Auth0 not available")

        headers = {"Authorization": f"Bearer {buyer_token}"}
        response = client.get("/api/users", headers=headers)

        # Should work with JWT token
        assert response.status_code == 200

    def test_protected_endpoint_without_token(self, client):
        """Test accessing endpoint without token - allows public access."""
        response = client.get("/api/users")

        # Public endpoints allow access without authentication
        assert response.status_code == 200
        assert isinstance(response.json(), list)

    def test_protected_endpoint_invalid_token(self, client):
        """Test accessing protected endpoint with invalid token."""
        headers = {"Authorization": "Bearer invalid.token.here"}
        response = client.get("/api/users", headers=headers)

        assert response.status_code in [401, 403]

    @patch("services.auth_service.AuthService.verify_auth0_token")
    def test_protected_endpoint_expired_token(self, mock_verify, client):
        """Test accessing protected endpoint with expired JWT token."""
        from datetime import timedelta

        from services.jwt_service import JWTService

        # Create already-expired token
        expired_token = JWTService.create_access_token(
            data={"sub": "auth0|test"}, expires_delta=timedelta(seconds=-1)
        )

        mock_verify.side_effect = Exception("Auth0 not available")

        headers = {"Authorization": f"Bearer {expired_token}"}
        response = client.get("/api/users", headers=headers)

        assert response.status_code in [401, 403]


class TestAuthWithAuth0:
    """Test authentication using Auth0 tokens."""

    @patch("services.auth_service.AuthService.verify_auth0_token")
    def test_auth0_token_creates_user_on_first_login(
        self, mock_verify, client, db_session, mock_auth0_response
    ):
        """Test Auth0 token creates user on first login via registration."""
        from datetime import timedelta

        from services.jwt_service import JWTService

        # Mock Auth0 response for new user
        new_user_data = mock_auth0_response(
            sub="auth0|firstlogin",
            email="firstlogin@example.com",
            name="First Login User",
            roles=["buyer"],
        )
        mock_verify.return_value = new_user_data

        # First, register the user (simulates first login)
        register_response = client.post(
            "/api/auth/register",
            json={
                "email": "firstlogin@example.com",
                "name": "First Login User",
                "auth0_sub": "auth0|firstlogin",
                "role": "BUYER",
            },
        )
        assert register_response.status_code == 200

        # Create token for the new user
        token = JWTService.create_access_token(
            data={"sub": "auth0|firstlogin", "role": "BUYER"}, expires_delta=timedelta(hours=1)
        )

        # Mock to fallback to JWT
        mock_verify.side_effect = Exception("Auth0 not available")

        # Then retrieve user info with JWT auth
        headers = {"Authorization": f"Bearer {token}"}
        response = client.get("/api/auth/me", headers=headers)

        # User should be found
        assert response.status_code == 200
        data = response.json()
        assert data["auth0_sub"] == "auth0|firstlogin"
        assert data["email"] == "firstlogin@example.com"

    @patch("services.auth_service.AuthService.verify_auth0_token")
    def test_auth0_token_updates_role(
        self, mock_verify, client, db_session, buyer_user, mock_auth0_response
    ):
        """Test Auth0 token updates user role if changed."""
        # Mock Auth0 response with updated role
        updated_user_data = mock_auth0_response(
            sub=buyer_user.auth0_sub,
            email=buyer_user.email,
            name=buyer_user.name,
            roles=["admin"],  # Changed from buyer to admin
        )
        mock_verify.return_value = updated_user_data

        # Trigger authentication (could be any protected endpoint)
        # For this test, we'll just verify the get_or_create_user logic
        from services.auth_service import AuthService

        user = AuthService.get_or_create_user(db_session, updated_user_data)

        assert user.id == buyer_user.id
        assert user.role == UserRole.ADMIN

    @patch("services.auth_service.AuthService.verify_auth0_token")
    @patch("services.auth_service.AuthService.get_or_create_user")
    def test_auth0_token_authentication_success(
        self, mock_get_or_create, mock_verify, client, buyer_user, mock_auth0_response
    ):
        """Test successful authentication with Auth0 token."""
        # Mock Auth0 verification to succeed
        auth0_user_data = mock_auth0_response(
            sub=buyer_user.auth0_sub,
            email=buyer_user.email,
            name=buyer_user.name,
            roles=["buyer"],
        )
        mock_verify.return_value = auth0_user_data
        mock_get_or_create.return_value = buyer_user

        # Use a fake Auth0 token
        headers = {"Authorization": "Bearer fake.auth0.token"}
        response = client.get("/api/auth/me", headers=headers)

        assert response.status_code == 200
        data = response.json()
        assert data["id"] == buyer_user.id
        assert data["email"] == buyer_user.email
        mock_verify.assert_called_once_with("fake.auth0.token")
        mock_get_or_create.assert_called_once()


class TestAuthLogin:
    """Test POST /api/auth/login endpoint."""

    def test_login_success(self, client, db_session):
        """Test successful login with email and password."""
        from seeds.demo_users import seed_users

        # Seed demo users (admin has password)
        seed_users(db_session)

        payload = {"email": "admin@guesstheworth.demo", "password": "AdminPass123!"}

        response = client.post("/api/auth/login", json=payload)

        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"
        assert len(data["access_token"]) > 0

    def test_login_invalid_email(self, client, db_session):
        """Test login with non-existent email."""
        payload = {"email": "nonexistent@example.com", "password": "SomePassword123!"}

        response = client.post("/api/auth/login", json=payload)

        assert response.status_code == 401
        assert "Invalid email or password" in response.json()["detail"]

    def test_login_invalid_password(self, client, db_session):
        """Test login with incorrect password."""
        from seeds.demo_users import seed_users

        seed_users(db_session)

        payload = {"email": "admin@guesstheworth.demo", "password": "WrongPassword123!"}

        response = client.post("/api/auth/login", json=payload)

        assert response.status_code == 401
        assert "Invalid email or password" in response.json()["detail"]

    def test_login_oauth_user_without_password(self, client, buyer_user):
        """Test login attempt on OAuth user (no password hash)."""
        # buyer_user doesn't have a password_hash
        payload = {"email": buyer_user.email, "password": "AnyPassword123!"}

        response = client.post("/api/auth/login", json=payload)

        assert response.status_code == 401
        assert "OAuth2" in response.json()["detail"]

    def test_login_returns_valid_jwt(self, client, db_session):
        """Test that login returns a valid JWT that can be used for authentication."""
        from seeds.demo_users import seed_users

        seed_users(db_session)

        # Login
        login_response = client.post(
            "/api/auth/login", json={"email": "admin@guesstheworth.demo", "password": "AdminPass123!"}
        )
        assert login_response.status_code == 200
        token = login_response.json()["access_token"]

        # Use the token to access a protected endpoint
        headers = {"Authorization": f"Bearer {token}"}
        me_response = client.get("/api/auth/me", headers=headers)

        assert me_response.status_code == 200
        user_data = me_response.json()
        assert user_data["email"] == "admin@guesstheworth.demo"
        assert user_data["role"] == "ADMIN"


class TestAuthEdgeCases:
    """Test edge cases and error handling."""

    def test_register_with_special_characters_in_name(self, client):
        """Test registration with special characters in name."""
        payload = {
            "email": "special@example.com",
            "name": "User with émojis 🎨 and spëcial çhars",
            "auth0_sub": "auth0|special123",
            "role": "BUYER",
        }

        response = client.post("/api/auth/register", json=payload)

        assert response.status_code == 200
        data = response.json()
        assert "émojis" in data["name"]
        assert "🎨" in data["name"]

    def test_register_with_very_long_name(self, client):
        """Test registration with very long name."""
        long_name = "A" * 500
        payload = {
            "email": "longname@example.com",
            "name": long_name,
            "auth0_sub": "auth0|longname123",
            "role": "BUYER",
        }

        response = client.post("/api/auth/register", json=payload)

        # Should either succeed or fail with validation error
        assert response.status_code in [200, 422]

    def test_concurrent_registrations(self, client):
        """Test handling concurrent registration attempts."""
        payload = {
            "email": "concurrent@example.com",
            "name": "Concurrent User",
            "auth0_sub": "auth0|concurrent123",
            "role": "BUYER",
        }

        # Simulate concurrent requests
        response1 = client.post("/api/auth/register", json=payload)
        response2 = client.post("/api/auth/register", json=payload)

        # One should succeed, one should fail
        status_codes = [response1.status_code, response2.status_code]
        assert 200 in status_codes
        assert 400 in status_codes

    def test_register_integrity_error_handling(self, client, db_session, monkeypatch):
        """Test that IntegrityError during registration is handled properly."""
        from sqlalchemy.exc import IntegrityError

        # Mock the session.commit to raise IntegrityError
        original_commit = db_session.commit

        def mock_commit():
            raise IntegrityError("mock", "mock", "mock")

        monkeypatch.setattr(db_session, "commit", mock_commit)

        payload = {
            "email": "integrity@example.com",
            "name": "Integrity User",
            "auth0_sub": "auth0|integrity123",
            "role": "BUYER",
        }

        response = client.post("/api/auth/register", json=payload)

        # Should handle IntegrityError and return 400
        assert response.status_code == 400
        assert "constraint violation" in response.json()["detail"].lower()
