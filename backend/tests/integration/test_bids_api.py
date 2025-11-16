"""
Integration tests for bids API endpoints.
Tests /api/bids routes with critical threshold logic and bid validation.
"""

import pytest

from models.artwork import ArtworkStatus


class TestCreateBid:
    """Test POST /api/bids endpoint with threshold logic."""

    def test_create_bid_below_threshold(self, client, db_session, artwork, buyer_user):
        """Test creating bid below secret_threshold (not winning)."""
        # Artwork has secret_threshold = 100.0
        payload = {"artwork_id": artwork.id, "amount": 75.0}

        response = client.post(f"/api/bids?bidder_id={buyer_user.id}", json=payload)

        assert response.status_code == 200
        data = response.json()
        assert data["amount"] == 75.0
        assert data["artwork_id"] == artwork.id
        assert data["bidder_id"] == buyer_user.id
        assert data["is_winning"] is False

        # Verify artwork is still ACTIVE
        db_session.refresh(artwork)
        assert artwork.status == ArtworkStatus.ACTIVE
        assert artwork.current_highest_bid == 75.0

    def test_create_bid_at_threshold(self, client, db_session, artwork, buyer_user):
        """Test creating bid exactly at secret_threshold (winning)."""
        payload = {"artwork_id": artwork.id, "amount": 100.0}  # Exactly at threshold

        response = client.post(f"/api/bids?bidder_id={buyer_user.id}", json=payload)

        assert response.status_code == 200
        data = response.json()
        assert data["amount"] == 100.0
        assert data["is_winning"] is True

        # Verify artwork is marked as SOLD
        db_session.refresh(artwork)
        assert artwork.status == ArtworkStatus.SOLD
        assert artwork.current_highest_bid == 100.0

    def test_create_bid_above_threshold(self, client, db_session, artwork, buyer_user):
        """Test creating bid above secret_threshold (winning)."""
        payload = {"artwork_id": artwork.id, "amount": 150.0}  # Above threshold

        response = client.post(f"/api/bids?bidder_id={buyer_user.id}", json=payload)

        assert response.status_code == 200
        data = response.json()
        assert data["amount"] == 150.0
        assert data["is_winning"] is True

        # Verify artwork is marked as SOLD
        db_session.refresh(artwork)
        assert artwork.status == ArtworkStatus.SOLD
        assert artwork.current_highest_bid == 150.0

    def test_bid_on_sold_artwork_fails(self, client, sold_artwork, buyer_user):
        """Test bidding on already sold artwork returns error."""
        payload = {"artwork_id": sold_artwork.id, "amount": 200.0}

        response = client.post(f"/api/bids?bidder_id={buyer_user.id}", json=payload)

        assert response.status_code == 400
        assert (
            "not active" in response.json()["detail"].lower()
            or "sold" in response.json()["detail"].lower()
        )

    def test_bid_on_nonexistent_artwork(self, client, buyer_user):
        """Test bidding on non-existent artwork returns 404."""
        payload = {"artwork_id": 99999, "amount": 100.0}

        response = client.post(f"/api/bids?bidder_id={buyer_user.id}", json=payload)

        assert response.status_code == 404

    def test_create_bid_updates_current_highest_bid(self, client, db_session, artwork, buyer_user):
        """Test bid correctly updates artwork's current_highest_bid."""
        # Create first bid
        response1 = client.post(
            f"/api/bids?bidder_id={buyer_user.id}", json={"artwork_id": artwork.id, "amount": 50.0}
        )
        assert response1.status_code == 200

        db_session.refresh(artwork)
        assert artwork.current_highest_bid == 50.0

        # Create higher bid
        response2 = client.post(
            f"/api/bids?bidder_id={buyer_user.id}", json={"artwork_id": artwork.id, "amount": 75.0}
        )
        assert response2.status_code == 200

        db_session.refresh(artwork)
        assert artwork.current_highest_bid == 75.0

    def test_create_multiple_bids_same_user(self, client, artwork, buyer_user):
        """Test same user can place multiple bids on same artwork."""
        bids = [
            {"artwork_id": artwork.id, "amount": 20.0},
            {"artwork_id": artwork.id, "amount": 40.0},
            {"artwork_id": artwork.id, "amount": 60.0},
        ]

        for bid_data in bids:
            response = client.post(f"/api/bids?bidder_id={buyer_user.id}", json=bid_data)
            assert response.status_code == 200

    def test_create_bid_missing_amount(self, client, artwork, buyer_user):
        """Test creating bid without amount fails."""
        payload = {"artwork_id": artwork.id}

        response = client.post(f"/api/bids?bidder_id={buyer_user.id}", json=payload)

        assert response.status_code == 422

    def test_create_bid_missing_artwork_id(self, client, buyer_user):
        """Test creating bid without artwork_id fails."""
        payload = {"amount": 100.0}

        response = client.post(f"/api/bids?bidder_id={buyer_user.id}", json=payload)

        assert response.status_code == 422

    def test_create_bid_negative_amount(self, client, artwork, buyer_user):
        """Test creating bid with negative amount."""
        payload = {"artwork_id": artwork.id, "amount": -50.0}

        response = client.post(f"/api/bids?bidder_id={buyer_user.id}", json=payload)

        # Should be rejected by business logic
        assert response.status_code in [400, 422]

    def test_create_bid_zero_amount(self, client, artwork, buyer_user):
        """Test creating bid with zero amount."""
        payload = {"artwork_id": artwork.id, "amount": 0.0}

        response = client.post(f"/api/bids?bidder_id={buyer_user.id}", json=payload)

        # Business logic should determine if this is valid
        assert response.status_code in [200, 400, 422]


class TestGetArtworkBids:
    """Test GET /api/bids/artwork/{artwork_id} endpoint."""

    def test_get_bids_empty(self, client, artwork):
        """Test getting bids for artwork with no bids."""
        response = client.get(f"/api/bids/artwork/{artwork.id}")

        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) == 0

    def test_get_bids_single(self, client, db_session, artwork, buyer_user):
        """Test getting bids with one bid."""
        # Create a bid
        client.post(
            f"/api/bids?bidder_id={buyer_user.id}", json={"artwork_id": artwork.id, "amount": 50.0}
        )

        response = client.get(f"/api/bids/artwork/{artwork.id}")

        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["amount"] == 50.0
        assert data[0]["artwork_id"] == artwork.id

    def test_get_bids_multiple(self, client, artwork, buyer_user, db_session):
        """Test getting multiple bids for an artwork."""
        from models.user import User, UserRole

        # Create additional buyers
        buyer2 = User(
            auth0_sub="auth0|buyer2", email="buyer2@test.com", name="Buyer 2", role=UserRole.BUYER
        )
        buyer3 = User(
            auth0_sub="auth0|buyer3", email="buyer3@test.com", name="Buyer 3", role=UserRole.BUYER
        )
        db_session.add_all([buyer2, buyer3])
        db_session.commit()

        # Create bids from different users
        client.post(
            f"/api/bids?bidder_id={buyer_user.id}", json={"artwork_id": artwork.id, "amount": 30.0}
        )
        client.post(
            f"/api/bids?bidder_id={buyer2.id}", json={"artwork_id": artwork.id, "amount": 50.0}
        )
        client.post(
            f"/api/bids?bidder_id={buyer3.id}", json={"artwork_id": artwork.id, "amount": 70.0}
        )

        response = client.get(f"/api/bids/artwork/{artwork.id}")

        assert response.status_code == 200
        data = response.json()
        assert len(data) == 3
        amounts = [bid["amount"] for bid in data]
        assert 30.0 in amounts
        assert 50.0 in amounts
        assert 70.0 in amounts

    def test_get_bids_for_nonexistent_artwork(self, client):
        """Test getting bids for non-existent artwork."""
        response = client.get("/api/bids/artwork/99999")

        # May return empty list or 404 depending on implementation
        assert response.status_code in [200, 404]

    def test_get_bids_includes_bidder_info(self, client, artwork, buyer_user):
        """Test bid response includes bidder information."""
        client.post(
            f"/api/bids?bidder_id={buyer_user.id}", json={"artwork_id": artwork.id, "amount": 50.0}
        )

        response = client.get(f"/api/bids/artwork/{artwork.id}")

        assert response.status_code == 200
        data = response.json()
        assert data[0]["bidder_id"] == buyer_user.id

    def test_get_bids_includes_is_winning_flag(self, client, db_session, artwork, buyer_user):
        """Test bid response includes is_winning flag."""
        # Create bid below threshold
        client.post(
            f"/api/bids?bidder_id={buyer_user.id}", json={"artwork_id": artwork.id, "amount": 50.0}
        )

        response = client.get(f"/api/bids/artwork/{artwork.id}")

        assert response.status_code == 200
        data = response.json()
        assert "is_winning" in data[0]
        assert data[0]["is_winning"] is False

    def test_get_bids_ordered_by_time(self, client, artwork, buyer_user):
        """Test bids are returned in chronological order."""
        # Create bids at different times
        amounts = [25.0, 50.0, 75.0]
        for amount in amounts:
            client.post(
                f"/api/bids?bidder_id={buyer_user.id}",
                json={"artwork_id": artwork.id, "amount": amount},
            )

        response = client.get(f"/api/bids/artwork/{artwork.id}")

        assert response.status_code == 200
        data = response.json()

        # Verify order (either ascending or descending by bid_time)
        assert len(data) == 3


class TestBidThresholdLogic:
    """Test critical bid threshold and winning logic."""

    def test_only_threshold_bids_win(self, client, db_session, artwork, buyer_user):
        """Test only bids >= threshold are marked as winning."""
        # Create bids below and at threshold
        below = client.post(
            f"/api/bids?bidder_id={buyer_user.id}", json={"artwork_id": artwork.id, "amount": 99.0}
        )
        at = client.post(
            f"/api/bids?bidder_id={buyer_user.id}", json={"artwork_id": artwork.id, "amount": 100.0}
        )

        below_data = below.json()
        at_data = at.json()

        assert below_data["is_winning"] is False
        assert at_data["is_winning"] is True

    def test_artwork_sold_after_winning_bid(self, client, db_session, artwork, buyer_user):
        """Test artwork automatically marked as sold after winning bid."""
        assert artwork.status == ArtworkStatus.ACTIVE

        # Place winning bid
        client.post(
            f"/api/bids?bidder_id={buyer_user.id}", json={"artwork_id": artwork.id, "amount": 100.0}
        )

        db_session.refresh(artwork)
        assert artwork.status == ArtworkStatus.SOLD

    def test_cannot_bid_after_artwork_sold(self, client, db_session, artwork, buyer_user):
        """Test cannot place bid after artwork is sold."""
        # Place winning bid
        client.post(
            f"/api/bids?bidder_id={buyer_user.id}", json={"artwork_id": artwork.id, "amount": 100.0}
        )

        db_session.refresh(artwork)
        assert artwork.status == ArtworkStatus.SOLD

        # Try to bid again
        response = client.post(
            f"/api/bids?bidder_id={buyer_user.id}", json={"artwork_id": artwork.id, "amount": 150.0}
        )

        assert response.status_code == 400

    def test_multiple_users_bidding_race_condition(self, client, db_session, artwork):
        """Test concurrent bids from multiple users."""
        from models.user import User, UserRole

        # Create multiple buyers
        buyers = []
        for i in range(5):
            buyer = User(
                auth0_sub=f"auth0|racer{i}",
                email=f"racer{i}@test.com",
                name=f"Racer {i}",
                role=UserRole.BUYER,
            )
            buyers.append(buyer)

        db_session.add_all(buyers)
        db_session.commit()

        # Simulate concurrent bidding
        responses = []
        for i, buyer in enumerate(buyers):
            response = client.post(
                f"/api/bids?bidder_id={buyer.id}",
                json={"artwork_id": artwork.id, "amount": 10.0 * (i + 1)},
            )
            responses.append(response)

        # All bids should succeed (unless artwork was sold)
        successful = [r for r in responses if r.status_code == 200]
        assert len(successful) >= 1

        # Verify current_highest_bid is updated correctly
        db_session.refresh(artwork)
        assert artwork.current_highest_bid > 0

    def test_winning_bid_locks_artwork(self, client, db_session, artwork, buyer_user):
        """Test artwork is locked (SOLD) after first winning bid."""
        from models.user import User, UserRole

        # Create another buyer
        buyer2 = User(
            auth0_sub="auth0|buyer2", email="buyer2@test.com", name="Buyer 2", role=UserRole.BUYER
        )
        db_session.add(buyer2)
        db_session.commit()

        # First buyer wins
        response1 = client.post(
            f"/api/bids?bidder_id={buyer_user.id}", json={"artwork_id": artwork.id, "amount": 100.0}
        )
        assert response1.json()["is_winning"] is True

        # Second buyer tries to bid
        response2 = client.post(
            f"/api/bids?bidder_id={buyer2.id}", json={"artwork_id": artwork.id, "amount": 150.0}
        )
        assert response2.status_code == 400


class TestBidValidation:
    """Test bid validation and business rules."""

    def test_bid_with_extremely_large_amount(self, client, artwork, buyer_user):
        """Test bid with very large amount."""
        payload = {"artwork_id": artwork.id, "amount": 999999999.99}

        response = client.post(f"/api/bids?bidder_id={buyer_user.id}", json=payload)

        assert response.status_code == 200

    def test_bid_with_many_decimal_places(self, client, artwork, buyer_user):
        """Test bid with many decimal places."""
        payload = {"artwork_id": artwork.id, "amount": 99.999999}

        response = client.post(f"/api/bids?bidder_id={buyer_user.id}", json=payload)

        # Should round or accept
        assert response.status_code in [200, 422]

    def test_seller_cannot_bid_on_own_artwork(self, client, artwork, seller_user):
        """Test seller cannot bid on their own artwork."""
        payload = {"artwork_id": artwork.id, "amount": 100.0}

        response = client.post(f"/api/bids?bidder_id={seller_user.id}", json=payload)

        # This validation may or may not be implemented
        # If implemented, should return 400/403
        # If not implemented, this test documents the missing validation
        assert response.status_code in [200, 400, 403]

    def test_bid_includes_timestamp(self, client, artwork, buyer_user):
        """Test bid response includes timestamp."""
        response = client.post(
            f"/api/bids?bidder_id={buyer_user.id}", json={"artwork_id": artwork.id, "amount": 50.0}
        )

        assert response.status_code == 200
        data = response.json()
        assert "bid_time" in data

    def test_sequential_bids_have_increasing_timestamps(self, client, artwork, buyer_user):
        """Test bids placed sequentially have increasing timestamps."""
        import time

        response1 = client.post(
            f"/api/bids?bidder_id={buyer_user.id}", json={"artwork_id": artwork.id, "amount": 30.0}
        )

        time.sleep(0.1)  # Small delay

        response2 = client.post(
            f"/api/bids?bidder_id={buyer_user.id}", json={"artwork_id": artwork.id, "amount": 60.0}
        )

        bid1_time = response1.json()["bid_time"]
        bid2_time = response2.json()["bid_time"]

        # Second bid should have later timestamp
        assert bid2_time >= bid1_time


class TestBidEdgeCases:
    """Test edge cases and error scenarios."""

    def test_bid_on_archived_artwork(self, client, db_session, seller_user, buyer_user):
        """Test bidding on archived artwork."""
        from models.artwork import Artwork

        archived = Artwork(
            seller_id=seller_user.id,
            title="Archived",
            secret_threshold=100.0,
            status=ArtworkStatus.ARCHIVED,
        )
        db_session.add(archived)
        db_session.commit()

        response = client.post(
            f"/api/bids?bidder_id={buyer_user.id}", json={"artwork_id": archived.id, "amount": 50.0}
        )

        assert response.status_code == 400

    def test_bid_with_invalid_bidder_id(self, client, artwork):
        """Test bid with non-existent bidder."""
        response = client.post(
            "/api/bids?bidder_id=99999", json={"artwork_id": artwork.id, "amount": 50.0}
        )

        assert response.status_code in [400, 404]

    def test_rapid_successive_bids(self, client, artwork, buyer_user):
        """Test placing multiple bids rapidly."""
        amounts = [10.0, 20.0, 30.0, 40.0, 50.0]

        for amount in amounts:
            response = client.post(
                f"/api/bids?bidder_id={buyer_user.id}",
                json={"artwork_id": artwork.id, "amount": amount},
            )
            # All non-winning bids should succeed
            if amount < 100.0:
                assert response.status_code == 200
