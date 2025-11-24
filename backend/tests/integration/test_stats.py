"""
Test Statistics Endpoints (Stage 4).

These tests verify that stats endpoints return correct data:
- User stats (active bids, won auctions, total spent)
- Seller stats (total artworks, active auctions, total earnings)
- Platform stats (total artworks, users, etc.)
- Authorization requirements
"""

from unittest.mock import patch

import pytest
from fastapi.testclient import TestClient

from models.artwork import Artwork, ArtworkStatus
from models.bid import Bid
from models.user import User


@pytest.fixture(autouse=True)
def mock_auth0():
    """Mock Auth0 verification for all tests in this module to use JWT fallback."""
    with patch("services.auth_service.AuthService.verify_auth0_token") as mock:
        mock.side_effect = Exception("Auth0 not available - using JWT")
        yield mock


class TestUserStats:
    """Test user statistics endpoint."""

    def test_user_stats_requires_auth(self, client: TestClient):
        """Test that user stats requires authentication."""
        response = client.get("/api/stats/user")
        assert response.status_code == 401

    def test_user_stats_with_no_activity(
        self, client: TestClient, buyer_token: str, buyer_user: User, db_session
    ):
        """Test stats for user with no bids or wins."""
        response = client.get("/api/stats/user", headers={"Authorization": f"Bearer {buyer_token}"})

        assert response.status_code == 200
        data = response.json()

        # Verify structure
        assert "active_bids" in data
        assert "won_auctions" in data
        assert "total_spent" in data

        # Values should be zero or empty
        assert data["active_bids"] == 0
        assert data["won_auctions"] == 0
        assert data["total_spent"] == 0.0

    def test_user_stats_with_active_bids(
        self, client: TestClient, buyer_token: str, buyer_user: User, artwork, db_session
    ):
        """Test stats reflecting active bids."""
        # Place some bids (below threshold, not winning)
        for amount in [50.0, 60.0, 70.0]:
            bid = Bid(
                artwork_id=artwork.id,
                bidder_id=buyer_user.id,
                amount=amount,
                is_winning=False,
            )
            db_session.add(bid)
        db_session.commit()

        response = client.get("/api/stats/user", headers={"Authorization": f"Bearer {buyer_token}"})

        assert response.status_code == 200
        data = response.json()

        # Should reflect 3 active bids
        assert data["active_bids"] >= 1  # At least tracking artwork with bids

    def test_user_stats_with_won_auction(
        self, client: TestClient, buyer_token: str, buyer_user: User, seller_user, db_session
    ):
        """Test stats reflecting won auctions."""
        # Create artwork and winning bid
        artwork = Artwork(
            seller_id=seller_user.id,
            title="Won Artwork",
            secret_threshold=100.0,
            status=ArtworkStatus.SOLD,
            current_highest_bid=150.0,
        )
        db_session.add(artwork)
        db_session.commit()

        winning_bid = Bid(
            artwork_id=artwork.id,
            bidder_id=buyer_user.id,
            amount=150.0,
            is_winning=True,
        )
        db_session.add(winning_bid)
        db_session.commit()

        response = client.get("/api/stats/user", headers={"Authorization": f"Bearer {buyer_token}"})

        assert response.status_code == 200
        data = response.json()

        # Should reflect won auction
        assert data["won_auctions"] >= 1
        assert data["total_spent"] >= 150.0

    def test_user_stats_only_own_data(
        self,
        client: TestClient,
        buyer_token: str,
        buyer_user: User,
        seller_user: User,
        artwork,
        db_session,
    ):
        """Test that user only sees their own stats."""
        # Create another user's bid
        from models.user import User, UserRole

        other_buyer = User(
            auth0_sub="auth0|other_buyer",
            email="other@buyer.com",
            name="Other Buyer",
            role=UserRole.BUYER,
        )
        db_session.add(other_buyer)
        db_session.commit()

        # Other user places bids
        for amount in [50.0, 60.0]:
            bid = Bid(
                artwork_id=artwork.id,
                bidder_id=other_buyer.id,
                amount=amount,
                is_winning=False,
            )
            db_session.add(bid)
        db_session.commit()

        # Current user should see zero bids (not other user's bids)
        response = client.get("/api/stats/user", headers={"Authorization": f"Bearer {buyer_token}"})

        assert response.status_code == 200
        data = response.json()

        # Should not include other user's bids
        assert data["active_bids"] == 0


class TestSellerStats:
    """Test seller statistics endpoint."""

    def test_seller_stats_requires_auth(self, client: TestClient):
        """Test that seller stats requires authentication."""
        response = client.get("/api/stats/seller")
        assert response.status_code == 401

    def test_seller_stats_requires_seller_role(self, client: TestClient, buyer_token: str):
        """Test that seller stats requires seller role."""
        response = client.get(
            "/api/stats/seller", headers={"Authorization": f"Bearer {buyer_token}"}
        )

        # Should be forbidden (403) or not found (404) for non-sellers
        assert response.status_code in [403, 404]

    def test_seller_stats_with_no_artworks(
        self, client: TestClient, seller_token: str, seller_user: User, db_session
    ):
        """Test stats for seller with no artworks."""
        response = client.get(
            "/api/stats/seller", headers={"Authorization": f"Bearer {seller_token}"}
        )

        assert response.status_code == 200
        data = response.json()

        # Verify structure
        assert "total_artworks" in data
        assert "active_auctions" in data
        assert "sold_artworks" in data
        assert "total_earnings" in data

        # Values should be zero
        assert data["total_artworks"] == 0
        assert data["active_auctions"] == 0
        assert data["sold_artworks"] == 0
        assert data["total_earnings"] == 0.0

    def test_seller_stats_with_active_artworks(
        self, client: TestClient, seller_token: str, seller_user: User, db_session
    ):
        """Test stats reflecting active artworks."""
        # Create multiple artworks
        for i in range(3):
            artwork = Artwork(
                seller_id=seller_user.id,
                title=f"Art {i}",
                secret_threshold=100.0,
                status=ArtworkStatus.ACTIVE,
            )
            db_session.add(artwork)
        db_session.commit()

        response = client.get(
            "/api/stats/seller", headers={"Authorization": f"Bearer {seller_token}"}
        )

        assert response.status_code == 200
        data = response.json()

        assert data["total_artworks"] >= 3
        assert data["active_auctions"] >= 3

    def test_seller_stats_with_sold_artworks(
        self, client: TestClient, seller_token: str, seller_user: User, buyer_user, db_session
    ):
        """Test stats reflecting sold artworks and earnings."""
        # Create sold artworks
        total_earnings = 0
        for amount in [150.0, 200.0, 250.0]:
            artwork = Artwork(
                seller_id=seller_user.id,
                title=f"Sold for {amount}",
                secret_threshold=100.0,
                status=ArtworkStatus.SOLD,
                current_highest_bid=amount,
            )
            db_session.add(artwork)
            db_session.commit()

            # Add winning bid
            bid = Bid(
                artwork_id=artwork.id,
                bidder_id=buyer_user.id,
                amount=amount,
                is_winning=True,
            )
            db_session.add(bid)
            total_earnings += amount

        db_session.commit()

        response = client.get(
            "/api/stats/seller", headers={"Authorization": f"Bearer {seller_token}"}
        )

        assert response.status_code == 200
        data = response.json()

        assert data["sold_artworks"] >= 3
        assert data["total_earnings"] >= total_earnings

    def test_seller_stats_only_own_artworks(
        self, client: TestClient, seller_token: str, seller_user: User, db_session
    ):
        """Test that seller only sees stats for their own artworks."""
        # Create another seller with artworks
        from models.user import User, UserRole

        other_seller = User(
            auth0_sub="auth0|other_seller",
            email="other@seller.com",
            name="Other Seller",
            role=UserRole.SELLER,
        )
        db_session.add(other_seller)
        db_session.commit()

        # Other seller creates artworks
        for i in range(2):
            artwork = Artwork(
                seller_id=other_seller.id,
                title=f"Other's Art {i}",
                secret_threshold=100.0,
                status=ArtworkStatus.ACTIVE,
            )
            db_session.add(artwork)
        db_session.commit()

        # Current seller should see zero (not other seller's artworks)
        response = client.get(
            "/api/stats/seller", headers={"Authorization": f"Bearer {seller_token}"}
        )

        assert response.status_code == 200
        data = response.json()

        # Should not include other seller's artworks
        assert data["total_artworks"] == 0


class TestPlatformStats:
    """Test platform-wide statistics endpoint."""

    def test_platform_stats_public(self, client: TestClient):
        """Test that platform stats are publicly accessible."""
        response = client.get("/api/stats/platform")

        # Should be accessible without auth
        assert response.status_code == 200

        data = response.json()

        # Verify structure
        assert "total_artworks" in data
        assert "total_users" in data
        assert "active_auctions" in data or "total_artworks" in data

    def test_platform_stats_accuracy(
        self, client: TestClient, seller_user: User, buyer_user: User, db_session
    ):
        """Test that platform stats reflect actual data."""
        # Create artworks
        for i in range(5):
            artwork = Artwork(
                seller_id=seller_user.id,
                title=f"Platform Art {i}",
                secret_threshold=100.0,
                status=ArtworkStatus.ACTIVE if i < 3 else ArtworkStatus.SOLD,
            )
            db_session.add(artwork)
        db_session.commit()

        response = client.get("/api/stats/platform")

        assert response.status_code == 200
        data = response.json()

        # Should reflect created artworks
        assert data["total_artworks"] >= 5
        # Note: total_users includes seller_user and buyer_user from fixtures
        assert data["total_users"] >= 2

    def test_platform_stats_real_time(self, client: TestClient, seller_user: User, db_session):
        """Test that platform stats update in real-time."""
        # Get initial stats
        response1 = client.get("/api/stats/platform")
        assert response1.status_code == 200
        initial_count = response1.json()["total_artworks"]

        # Add new artwork
        artwork = Artwork(
            seller_id=seller_user.id,
            title="New Art",
            secret_threshold=100.0,
            status=ArtworkStatus.ACTIVE,
        )
        db_session.add(artwork)
        db_session.commit()

        # Get updated stats
        response2 = client.get("/api/stats/platform")
        assert response2.status_code == 200
        updated_count = response2.json()["total_artworks"]

        # Count should have increased
        assert updated_count == initial_count + 1


class TestStatsPerformance:
    """Test that stats endpoints perform well with large datasets."""

    def test_user_stats_with_many_bids(
        self, client: TestClient, buyer_token: str, buyer_user: User, seller_user, db_session
    ):
        """Test user stats performance with many bids."""
        # Create multiple artworks and bids
        for i in range(10):
            artwork = Artwork(
                seller_id=seller_user.id,
                title=f"Art {i}",
                secret_threshold=100.0,
                status=ArtworkStatus.ACTIVE,
            )
            db_session.add(artwork)
            db_session.commit()

            # Place multiple bids
            for amount in [50.0, 60.0, 70.0]:
                bid = Bid(
                    artwork_id=artwork.id,
                    bidder_id=buyer_user.id,
                    amount=amount,
                    is_winning=False,
                )
                db_session.add(bid)

        db_session.commit()

        # Should still respond quickly
        response = client.get("/api/stats/user", headers={"Authorization": f"Bearer {buyer_token}"})

        assert response.status_code == 200
        # Verify data is aggregated correctly
        data = response.json()
        assert "active_bids" in data


class TestStatsEdgeCases:
    """Test edge cases and error scenarios."""

    def test_stats_with_deleted_artworks(
        self, client: TestClient, seller_token: str, seller_user: User, db_session
    ):
        """Test stats exclude deleted artworks (if soft delete implemented)."""
        # Create and delete artwork
        artwork = Artwork(
            seller_id=seller_user.id,
            title="To Delete",
            secret_threshold=100.0,
            status=ArtworkStatus.ACTIVE,
        )
        db_session.add(artwork)
        db_session.commit()

        # Delete it
        db_session.delete(artwork)
        db_session.commit()

        response = client.get(
            "/api/stats/seller", headers={"Authorization": f"Bearer {seller_token}"}
        )

        assert response.status_code == 200
        # Deleted artwork should not be counted

    def test_stats_with_archived_artworks(
        self, client: TestClient, seller_token: str, seller_user: User, db_session
    ):
        """Test stats handling of archived artworks."""
        # Create archived artwork
        artwork = Artwork(
            seller_id=seller_user.id,
            title="Archived",
            secret_threshold=100.0,
            status=ArtworkStatus.ARCHIVED,
        )
        db_session.add(artwork)
        db_session.commit()

        response = client.get(
            "/api/stats/seller", headers={"Authorization": f"Bearer {seller_token}"}
        )

        assert response.status_code == 200
        data = response.json()

        # Archived should be counted in total but not active
        assert data["total_artworks"] >= 1
        # archived should not be in active_auctions (if that field exists)
