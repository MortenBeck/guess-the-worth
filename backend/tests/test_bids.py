"""
Tests for bidding endpoints.
"""
import pytest
from fastapi import status
from models import User, Artwork, Bid


class TestBidEndpoints:
    """Test bid-related endpoints."""

    @pytest.fixture
    def created_user(self, db_session, sample_user_data):
        """Create a user in the database for testing."""
        user = User(**sample_user_data)
        db_session.add(user)
        db_session.commit()
        db_session.refresh(user)
        return user

    @pytest.fixture
    def created_artwork(self, db_session, created_user, sample_artwork_data):
        """Create an artwork in the database for testing."""
        artwork_data = sample_artwork_data.copy()
        artwork_data["seller_id"] = created_user.id
        artwork_data["status"] = "active"  # Make it biddable
        artwork = Artwork(**artwork_data)
        db_session.add(artwork)
        db_session.commit()
        db_session.refresh(artwork)
        return artwork

    def test_get_artwork_bids_empty(self, client, created_artwork):
        """Test getting bids for an artwork with no bids."""
        response = client.get(f"/api/bids/artwork/{created_artwork.id}")

        assert response.status_code == status.HTTP_200_OK
        assert response.json() == []

    def test_create_bid(self, client, created_user, created_artwork):
        """Test creating a new bid."""
        bid_data = {
            "artwork_id": created_artwork.id,
            "bidder_id": created_user.id,
            "amount": 150.00
        }

        response = client.post("/api/bids/", json=bid_data)

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["amount"] == bid_data["amount"]
        assert data["artwork_id"] == created_artwork.id
        assert data["bidder_id"] == created_user.id
        assert "id" in data

    def test_bid_on_nonexistent_artwork(self, client, created_user):
        """Test bidding on an artwork that doesn't exist."""
        bid_data = {
            "artwork_id": 99999,
            "bidder_id": created_user.id,
            "amount": 150.00
        }

        response = client.post("/api/bids/", json=bid_data)

        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert "not found" in response.json()["detail"].lower()

    def test_bid_on_inactive_artwork(self, client, created_user, db_session, sample_artwork_data):
        """Test bidding on an artwork that's not active."""
        # Create inactive artwork
        artwork_data = sample_artwork_data.copy()
        artwork_data["seller_id"] = created_user.id
        artwork_data["status"] = "draft"
        artwork = Artwork(**artwork_data)
        db_session.add(artwork)
        db_session.commit()

        bid_data = {
            "artwork_id": artwork.id,
            "bidder_id": created_user.id,
            "amount": 150.00
        }

        response = client.post("/api/bids/", json=bid_data)

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "not available" in response.json()["detail"].lower()

    def test_winning_bid_marks_artwork_sold(self, client, created_user, created_artwork, db_session):
        """Test that a bid meeting the secret threshold marks artwork as sold."""
        # Bid at or above the secret threshold
        bid_data = {
            "artwork_id": created_artwork.id,
            "bidder_id": created_user.id,
            "amount": created_artwork.secret_threshold
        }

        response = client.post("/api/bids/", json=bid_data)

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["is_winning"] is True

        # Check that artwork status is now "sold"
        db_session.refresh(created_artwork)
        assert created_artwork.status == "sold"

    def test_non_winning_bid_keeps_artwork_active(self, client, created_user, created_artwork, db_session):
        """Test that a bid below the secret threshold keeps artwork active."""
        # Bid below the secret threshold
        bid_data = {
            "artwork_id": created_artwork.id,
            "bidder_id": created_user.id,
            "amount": created_artwork.secret_threshold - 50
        }

        response = client.post("/api/bids/", json=bid_data)

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["is_winning"] is False

        # Check that artwork status is still "active"
        db_session.refresh(created_artwork)
        assert created_artwork.status == "active"

    def test_get_artwork_bids(self, client, created_user, created_artwork):
        """Test retrieving all bids for an artwork."""
        # Create multiple bids
        for amount in [150.00, 200.00, 250.00]:
            bid_data = {
                "artwork_id": created_artwork.id,
                "bidder_id": created_user.id,
                "amount": amount
            }
            client.post("/api/bids/", json=bid_data)

        # Get all bids
        response = client.get(f"/api/bids/artwork/{created_artwork.id}")

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert len(data) >= 3  # At least the bids we created
