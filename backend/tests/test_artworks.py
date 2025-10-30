"""
Tests for artwork endpoints.
"""
import pytest
from fastapi import status
from models import User, Artwork


class TestArtworkEndpoints:
    """Test artwork-related endpoints."""

    @pytest.fixture
    def created_user(self, db_session, sample_user_data):
        """Create a user in the database for testing."""
        user = User(**sample_user_data)
        db_session.add(user)
        db_session.commit()
        db_session.refresh(user)
        return user

    def test_get_artworks_empty(self, client):
        """Test getting artworks when none exist."""
        response = client.get("/api/artworks/")
        assert response.status_code == status.HTTP_200_OK
        assert response.json() == []

    def test_create_artwork(self, client, created_user, sample_artwork_data):
        """Test creating a new artwork."""
        artwork_data = sample_artwork_data.copy()
        artwork_data["seller_id"] = created_user.id

        response = client.post("/api/artworks/", json=artwork_data)

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["title"] == artwork_data["title"]
        assert data["artist"] == artwork_data["artist"]
        assert data["starting_price"] == artwork_data["starting_price"]
        assert "id" in data

    def test_get_artwork_by_id(self, client, created_user, sample_artwork_data):
        """Test retrieving a specific artwork by ID."""
        # Create artwork first
        artwork_data = sample_artwork_data.copy()
        artwork_data["seller_id"] = created_user.id
        create_response = client.post("/api/artworks/", json=artwork_data)
        artwork_id = create_response.json()["id"]

        # Get the artwork
        response = client.get(f"/api/artworks/{artwork_id}")

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["id"] == artwork_id
        assert data["title"] == artwork_data["title"]

    def test_get_nonexistent_artwork(self, client):
        """Test getting an artwork that doesn't exist."""
        response = client.get("/api/artworks/99999")

        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert "not found" in response.json()["detail"].lower()

    def test_get_artworks_with_pagination(self, client, created_user, sample_artwork_data):
        """Test pagination of artworks list."""
        # Create multiple artworks
        artwork_data = sample_artwork_data.copy()
        artwork_data["seller_id"] = created_user.id

        for i in range(5):
            data = artwork_data.copy()
            data["title"] = f"Artwork {i}"
            client.post("/api/artworks/", json=data)

        # Test pagination
        response = client.get("/api/artworks/?skip=2&limit=2")

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert len(data) == 2

    def test_create_artwork_missing_required_fields(self, client):
        """Test creating artwork with missing required fields."""
        incomplete_data = {
            "title": "Test Artwork"
            # Missing other required fields
        }

        response = client.post("/api/artworks/", json=incomplete_data)
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
