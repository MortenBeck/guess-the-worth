"""
Tests for authentication endpoints.
"""
import pytest
from fastapi import status


class TestAuthEndpoints:
    """Test authentication-related endpoints."""

    def test_register_new_user(self, client, sample_user_data):
        """Test registering a new user."""
        response = client.post("/api/auth/register", json=sample_user_data)

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["email"] == sample_user_data["email"]
        assert data["name"] == sample_user_data["name"]
        assert data["auth0_sub"] == sample_user_data["auth0_sub"]
        assert "id" in data
        assert "created_at" in data

    def test_register_duplicate_user(self, client, sample_user_data):
        """Test that registering the same user twice fails."""
        # First registration should succeed
        response1 = client.post("/api/auth/register", json=sample_user_data)
        assert response1.status_code == status.HTTP_200_OK

        # Second registration should fail
        response2 = client.post("/api/auth/register", json=sample_user_data)
        assert response2.status_code == status.HTTP_400_BAD_REQUEST
        assert "already registered" in response2.json()["detail"].lower()

    def test_register_invalid_email(self, client, sample_user_data):
        """Test registration with invalid email."""
        invalid_data = sample_user_data.copy()
        invalid_data["email"] = "not-an-email"

        response = client.post("/api/auth/register", json=invalid_data)
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    def test_get_current_user(self, client, sample_user_data):
        """Test getting current user information."""
        # First register a user
        client.post("/api/auth/register", json=sample_user_data)

        # Then try to get the user
        response = client.get(
            "/api/auth/me",
            params={"auth0_sub": sample_user_data["auth0_sub"]}
        )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["email"] == sample_user_data["email"]

    def test_get_nonexistent_user(self, client):
        """Test getting a user that doesn't exist."""
        response = client.get(
            "/api/auth/me",
            params={"auth0_sub": "nonexistent|user"}
        )

        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert "not found" in response.json()["detail"].lower()
