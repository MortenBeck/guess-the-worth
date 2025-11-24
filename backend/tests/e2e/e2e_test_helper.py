"""
Helper functions for E2E tests to create JWT tokens after user registration.
This ensures all E2E tests can properly authenticate API requests.
"""

from datetime import timedelta

from services.jwt_service import JWTService


def create_token_for_user(auth0_sub: str, role: str) -> str:
    """
    Create a JWT token for a user with the given auth0_sub and role.

    Args:
        auth0_sub: The Auth0 subject ID (e.g., "auth0|e2e_buyer")
        role: The user role (e.g., "BUYER", "SELLER", "ADMIN")

    Returns:
        JWT token string
    """
    return JWTService.create_access_token(
        data={"sub": auth0_sub, "role": role}, expires_delta=timedelta(hours=1)
    )


def register_user_with_token(client, email: str, name: str, auth0_sub: str, role: str):
    """
    Register a user and return both the user data and a JWT token.

    Args:
        client: FastAPI TestClient instance
        email: User email
        name: User name
        auth0_sub: Auth0 subject ID
        role: User role

    Returns:
        Tuple of (user_data dict, token string)
    """
    payload = {
        "email": email,
        "name": name,
        "auth0_sub": auth0_sub,
        "role": role,
    }
    response = client.post("/api/auth/register", json=payload)
    assert response.status_code == 200, f"Registration failed: {response.json()}"

    user_data = response.json()
    token = create_token_for_user(auth0_sub, role)

    return user_data, token


def create_auth_headers(token: str) -> dict:
    """
    Create Authorization headers for API requests.

    Args:
        token: JWT token

    Returns:
        Dict with Authorization header
    """
    return {"Authorization": f"Bearer {token}"}
