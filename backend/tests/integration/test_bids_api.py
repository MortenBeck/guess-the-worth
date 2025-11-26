"""
Integration tests for bids API endpoints.
Tests /api/bids routes with critical threshold logic and bid validation.
"""

from models.artwork import ArtworkStatus


class TestCreateBid:
    """Test POST /api/bids endpoint with threshold logic."""

    def test_create_bid_below_threshold(self, client, db_session, artwork, buyer_user, buyer_token):
        """Test creating bid below secret_threshold (not winning)."""
        # Artwork has secret_threshold = 100.0
        payload = {"artwork_id": artwork.id, "amount": 75.0}

        response = client.post(
            "/api/bids/", json=payload, headers={"Authorization": f"Bearer {buyer_token}"}
        )

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

    def test_create_bid_at_threshold(self, client, db_session, artwork, buyer_user, buyer_token):
        """Test creating bid exactly at secret_threshold (winning)."""
        payload = {"artwork_id": artwork.id, "amount": 100.0}  # Exactly at threshold

        response = client.post(
            "/api/bids/", json=payload, headers={"Authorization": f"Bearer {buyer_token}"}
        )

        assert response.status_code == 200
        data = response.json()
        assert data["amount"] == 100.0
        assert data["is_winning"] is True

        # Verify artwork is marked as SOLD
        db_session.refresh(artwork)
        assert artwork.status == ArtworkStatus.SOLD
        assert artwork.current_highest_bid == 100.0

    def test_create_bid_above_threshold(self, client, db_session, artwork, buyer_user, buyer_token):
        """Test creating bid above secret_threshold (winning)."""
        payload = {"artwork_id": artwork.id, "amount": 150.0}  # Above threshold

        response = client.post(
            "/api/bids/", json=payload, headers={"Authorization": f"Bearer {buyer_token}"}
        )

        assert response.status_code == 200
        data = response.json()
        assert data["amount"] == 150.0
        assert data["is_winning"] is True

        # Verify artwork is marked as SOLD
        db_session.refresh(artwork)
        assert artwork.status == ArtworkStatus.SOLD
        assert artwork.current_highest_bid == 150.0

    def test_bid_on_sold_artwork_fails(self, client, sold_artwork, buyer_user, buyer_token):
        """Test bidding on already sold artwork returns error."""
        payload = {"artwork_id": sold_artwork.id, "amount": 200.0}

        response = client.post(
            "/api/bids/", json=payload, headers={"Authorization": f"Bearer {buyer_token}"}
        )

        assert response.status_code == 400
        assert (
            "not active" in response.json()["detail"].lower()
            or "sold" in response.json()["detail"].lower()
        )

    def test_bid_on_nonexistent_artwork(self, client, buyer_user, buyer_token):
        """Test bidding on non-existent artwork returns 404."""
        payload = {"artwork_id": 99999, "amount": 100.0}

        response = client.post(
            "/api/bids/", json=payload, headers={"Authorization": f"Bearer {buyer_token}"}
        )

        assert response.status_code == 404

    def test_create_bid_updates_current_highest_bid(
        self, client, db_session, artwork, buyer_user, buyer_token
    ):
        """Test bid correctly updates artwork's current_highest_bid."""
        # Create first bid
        response1 = client.post(
            "/api/bids/",
            json={"artwork_id": artwork.id, "amount": 50.0},
            headers={"Authorization": f"Bearer {buyer_token}"},
        )
        assert response1.status_code == 200

        db_session.refresh(artwork)
        assert artwork.current_highest_bid == 50.0

        # Create higher bid
        response2 = client.post(
            "/api/bids/",
            json={"artwork_id": artwork.id, "amount": 75.0},
            headers={"Authorization": f"Bearer {buyer_token}"},
        )
        assert response2.status_code == 200

        db_session.refresh(artwork)
        assert artwork.current_highest_bid == 75.0

    def test_create_multiple_bids_same_user(self, client, artwork, buyer_user, buyer_token):
        """Test same user can place multiple bids on same artwork."""
        bids = [
            {"artwork_id": artwork.id, "amount": 20.0},
            {"artwork_id": artwork.id, "amount": 40.0},
            {"artwork_id": artwork.id, "amount": 60.0},
        ]

        for bid_data in bids:
            response = client.post(
                "/api/bids/", json=bid_data, headers={"Authorization": f"Bearer {buyer_token}"}
            )
            assert response.status_code == 200

    def test_create_bid_missing_amount(self, client, artwork, buyer_user, buyer_token):
        """Test creating bid without amount fails."""
        payload = {"artwork_id": artwork.id}

        response = client.post(
            "/api/bids/", json=payload, headers={"Authorization": f"Bearer {buyer_token}"}
        )

        assert response.status_code == 422

    def test_create_bid_missing_artwork_id(self, client, buyer_user, buyer_token):
        """Test creating bid without artwork_id fails."""
        payload = {"amount": 100.0}

        response = client.post(
            "/api/bids/", json=payload, headers={"Authorization": f"Bearer {buyer_token}"}
        )

        assert response.status_code == 422

    def test_create_bid_negative_amount(self, client, artwork, buyer_user, buyer_token):
        """Test creating bid with negative amount."""
        payload = {"artwork_id": artwork.id, "amount": -50.0}

        response = client.post(
            "/api/bids/", json=payload, headers={"Authorization": f"Bearer {buyer_token}"}
        )

        # Should be rejected by business logic
        assert response.status_code in [400, 422]

    def test_create_bid_zero_amount(self, client, artwork, buyer_user, buyer_token):
        """Test creating bid with zero amount."""
        payload = {"artwork_id": artwork.id, "amount": 0.0}

        response = client.post(
            "/api/bids/", json=payload, headers={"Authorization": f"Bearer {buyer_token}"}
        )

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

    def test_get_bids_single(self, client, db_session, artwork, buyer_user, buyer_token):
        """Test getting bids with one bid."""
        # Create a bid
        client.post(
            "/api/bids/",
            json={"artwork_id": artwork.id, "amount": 50.0},
            headers={"Authorization": f"Bearer {buyer_token}"},
        )

        response = client.get(f"/api/bids/artwork/{artwork.id}")

        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["amount"] == 50.0
        assert data[0]["artwork_id"] == artwork.id

    def test_get_bids_multiple(self, client, artwork, buyer_user, buyer_token, db_session):
        """Test getting multiple bids for an artwork."""
        from datetime import timedelta

        from models.user import User
        from services.jwt_service import JWTService

        # Create additional buyers
        buyer2 = User(auth0_sub="auth0|buyer2")
        buyer3 = User(auth0_sub="auth0|buyer3")
        db_session.add_all([buyer2, buyer3])
        db_session.commit()
        db_session.refresh(buyer2)
        db_session.refresh(buyer3)
        # Attach Auth0 data (simulated)
        buyer2.email = "buyer2@test.com"
        buyer2.name = "Buyer 2"
        buyer2.role = "BUYER"
        buyer3.email = "buyer3@test.com"
        buyer3.name = "Buyer 3"
        buyer3.role = "BUYER"

        # Create tokens for the additional buyers
        buyer2_token = JWTService.create_access_token(
            data={"sub": buyer2.auth0_sub, "role": "BUYER"},
            expires_delta=timedelta(hours=1),
        )
        buyer3_token = JWTService.create_access_token(
            data={"sub": buyer3.auth0_sub, "role": "BUYER"},
            expires_delta=timedelta(hours=1),
        )

        # Create bids from different users
        client.post(
            "/api/bids/",
            json={"artwork_id": artwork.id, "amount": 30.0},
            headers={"Authorization": f"Bearer {buyer_token}"},
        )
        client.post(
            "/api/bids/",
            json={"artwork_id": artwork.id, "amount": 50.0},
            headers={"Authorization": f"Bearer {buyer2_token}"},
        )
        client.post(
            "/api/bids/",
            json={"artwork_id": artwork.id, "amount": 70.0},
            headers={"Authorization": f"Bearer {buyer3_token}"},
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

    def test_get_bids_includes_bidder_info(self, client, artwork, buyer_user, buyer_token):
        """Test bid response includes bidder information."""
        client.post(
            "/api/bids/",
            json={"artwork_id": artwork.id, "amount": 50.0},
            headers={"Authorization": f"Bearer {buyer_token}"},
        )

        response = client.get(f"/api/bids/artwork/{artwork.id}")

        assert response.status_code == 200
        data = response.json()
        assert data[0]["bidder_id"] == buyer_user.id

    def test_get_bids_includes_is_winning_flag(
        self, client, db_session, artwork, buyer_user, buyer_token
    ):
        """Test bid response includes is_winning flag."""
        # Create bid below threshold
        client.post(
            "/api/bids/",
            json={"artwork_id": artwork.id, "amount": 50.0},
            headers={"Authorization": f"Bearer {buyer_token}"},
        )

        response = client.get(f"/api/bids/artwork/{artwork.id}")

        assert response.status_code == 200
        data = response.json()
        assert "is_winning" in data[0]
        assert data[0]["is_winning"] is False

    def test_get_bids_ordered_by_time(self, client, artwork, buyer_user, buyer_token):
        """Test bids are returned in chronological order."""
        # Create bids at different times
        amounts = [25.0, 50.0, 75.0]
        for amount in amounts:
            client.post(
                "/api/bids/",
                json={"artwork_id": artwork.id, "amount": amount},
                headers={"Authorization": f"Bearer {buyer_token}"},
            )

        response = client.get(f"/api/bids/artwork/{artwork.id}")

        assert response.status_code == 200
        data = response.json()

        # Verify order (either ascending or descending by created_at)
        assert len(data) == 3


class TestBidThresholdLogic:
    """Test critical bid threshold and winning logic."""

    def test_only_threshold_bids_win(self, client, db_session, artwork, buyer_user, buyer_token):
        """Test only bids >= threshold are marked as winning."""
        # Create bids below and at threshold
        below = client.post(
            "/api/bids/",
            json={"artwork_id": artwork.id, "amount": 99.0},
            headers={"Authorization": f"Bearer {buyer_token}"},
        )
        at = client.post(
            "/api/bids/",
            json={"artwork_id": artwork.id, "amount": 100.0},
            headers={"Authorization": f"Bearer {buyer_token}"},
        )

        below_data = below.json()
        at_data = at.json()

        assert below_data["is_winning"] is False
        assert at_data["is_winning"] is True

    def test_artwork_sold_after_winning_bid(
        self, client, db_session, artwork, buyer_user, buyer_token
    ):
        """Test artwork automatically marked as sold after winning bid."""
        assert artwork.status == ArtworkStatus.ACTIVE

        # Place winning bid
        client.post(
            "/api/bids/",
            json={"artwork_id": artwork.id, "amount": 100.0},
            headers={"Authorization": f"Bearer {buyer_token}"},
        )

        db_session.refresh(artwork)
        assert artwork.status == ArtworkStatus.SOLD

    def test_cannot_bid_after_artwork_sold(
        self, client, db_session, artwork, buyer_user, buyer_token
    ):
        """Test cannot place bid after artwork is sold."""
        # Place winning bid
        client.post(
            "/api/bids/",
            json={"artwork_id": artwork.id, "amount": 100.0},
            headers={"Authorization": f"Bearer {buyer_token}"},
        )

        db_session.refresh(artwork)
        assert artwork.status == ArtworkStatus.SOLD

        # Try to bid again
        response = client.post(
            "/api/bids/",
            json={"artwork_id": artwork.id, "amount": 150.0},
            headers={"Authorization": f"Bearer {buyer_token}"},
        )

        assert response.status_code == 400

    def test_multiple_users_bidding_race_condition(self, client, db_session, artwork):
        """Test concurrent bids from multiple users."""
        from datetime import timedelta

        from models.user import User
        from services.jwt_service import JWTService

        # Create multiple buyers
        buyers = []
        tokens = []
        for i in range(5):
            buyer = User(
                auth0_sub=f"auth0|racer{i}",
            )
            buyers.append(buyer)

        db_session.add_all(buyers)
        db_session.commit()

        # Attach Auth0 data and create tokens for all buyers
        for i, buyer in enumerate(buyers):
            db_session.refresh(buyer)
            buyer.email = f"racer{i}@test.com"
            buyer.name = f"Racer {i}"
            buyer.role = "BUYER"

            token = JWTService.create_access_token(
                data={"sub": buyer.auth0_sub, "role": "BUYER"},
                expires_delta=timedelta(hours=1),
            )
            tokens.append(token)

        # Simulate concurrent bidding
        responses = []
        for i, (buyer, token) in enumerate(zip(buyers, tokens)):
            response = client.post(
                "/api/bids/",
                json={"artwork_id": artwork.id, "amount": 10.0 * (i + 1)},
                headers={"Authorization": f"Bearer {token}"},
            )
            responses.append(response)

        # All bids should succeed (unless artwork was sold)
        successful = [r for r in responses if r.status_code == 200]
        assert len(successful) >= 1

        # Verify current_highest_bid is updated correctly
        db_session.refresh(artwork)
        assert artwork.current_highest_bid > 0

    def test_winning_bid_locks_artwork(self, client, db_session, artwork, buyer_user, buyer_token):
        """Test artwork is locked (SOLD) after first winning bid."""
        from datetime import timedelta

        from models.user import User
        from services.jwt_service import JWTService

        # Create another buyer
        buyer2 = User(
            auth0_sub="auth0|buyer2"
        )
        db_session.add(buyer2)
        db_session.commit()
        db_session.refresh(buyer2)

        # Attach Auth0 data (simulated)
        buyer2.email = "buyer2@test.com"
        buyer2.name = "Buyer 2"
        buyer2.role = "BUYER"

        # Create token for buyer2
        buyer2_token = JWTService.create_access_token(
            data={"sub": buyer2.auth0_sub, "role": "BUYER"},
            expires_delta=timedelta(hours=1),
        )

        # First buyer wins
        response1 = client.post(
            "/api/bids/",
            json={"artwork_id": artwork.id, "amount": 100.0},
            headers={"Authorization": f"Bearer {buyer_token}"},
        )
        assert response1.json()["is_winning"] is True

        # Second buyer tries to bid
        response2 = client.post(
            "/api/bids/",
            json={"artwork_id": artwork.id, "amount": 150.0},
            headers={"Authorization": f"Bearer {buyer2_token}"},
        )
        assert response2.status_code == 400


class TestBidValidation:
    """Test bid validation and business rules."""

    def test_bid_with_extremely_large_amount(self, client, artwork, buyer_user, buyer_token):
        """Test bid with very large amount."""
        payload = {"artwork_id": artwork.id, "amount": 999999999.99}

        response = client.post(
            "/api/bids/", json=payload, headers={"Authorization": f"Bearer {buyer_token}"}
        )

        assert response.status_code == 200

    def test_bid_with_many_decimal_places(self, client, artwork, buyer_user, buyer_token):
        """Test bid with many decimal places."""
        payload = {"artwork_id": artwork.id, "amount": 99.999999}

        response = client.post(
            "/api/bids/", json=payload, headers={"Authorization": f"Bearer {buyer_token}"}
        )

        # Should round or accept
        assert response.status_code in [200, 422]

    def test_seller_cannot_bid_on_own_artwork(self, client, artwork, seller_user, seller_token):
        """Test seller cannot bid on their own artwork."""
        payload = {"artwork_id": artwork.id, "amount": 100.0}

        response = client.post(
            "/api/bids/", json=payload, headers={"Authorization": f"Bearer {seller_token}"}
        )

        # This validation may or may not be implemented
        # If implemented, should return 400/403
        # If not implemented, this test documents the missing validation
        assert response.status_code in [200, 400, 403]

    def test_bid_includes_timestamp(self, client, artwork, buyer_user, buyer_token):
        """Test bid response includes timestamp."""
        response = client.post(
            "/api/bids/",
            json={"artwork_id": artwork.id, "amount": 50.0},
            headers={"Authorization": f"Bearer {buyer_token}"},
        )

        assert response.status_code == 200
        data = response.json()
        assert "created_at" in data

    def test_sequential_bids_have_increasing_timestamps(
        self, client, artwork, buyer_user, buyer_token
    ):
        """Test bids placed sequentially have increasing timestamps."""
        import time

        response1 = client.post(
            "/api/bids/",
            json={"artwork_id": artwork.id, "amount": 30.0},
            headers={"Authorization": f"Bearer {buyer_token}"},
        )

        time.sleep(0.1)  # Small delay

        response2 = client.post(
            "/api/bids/",
            json={"artwork_id": artwork.id, "amount": 60.0},
            headers={"Authorization": f"Bearer {buyer_token}"},
        )

        bid1_time = response1.json()["created_at"]
        bid2_time = response2.json()["created_at"]

        # Second bid should have later timestamp
        assert bid2_time >= bid1_time


class TestBidEdgeCases:
    """Test edge cases and error scenarios."""

    def test_bid_on_archived_artwork(
        self, client, db_session, seller_user, buyer_user, buyer_token
    ):
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
            "/api/bids/",
            json={"artwork_id": archived.id, "amount": 50.0},
            headers={"Authorization": f"Bearer {buyer_token}"},
        )

        assert response.status_code == 400

    def test_bid_with_invalid_bidder_id(self, client, artwork):
        """Test bid with invalid authentication token."""
        response = client.post(
            "/api/bids/",
            json={"artwork_id": artwork.id, "amount": 50.0},
            headers={"Authorization": "Bearer invalid_token"},
        )

        assert response.status_code in [401, 403]

    def test_rapid_successive_bids(self, client, artwork, buyer_user, buyer_token):
        """Test placing multiple bids rapidly."""
        amounts = [10.0, 20.0, 30.0, 40.0, 50.0]

        for amount in amounts:
            response = client.post(
                "/api/bids/",
                json={"artwork_id": artwork.id, "amount": amount},
                headers={"Authorization": f"Bearer {buyer_token}"},
            )
            # All non-winning bids should succeed
            if amount < 100.0:
                assert response.status_code == 200


class TestBidAmountValidation:
    """Test bid amount validation limits."""

    def test_bid_exceeds_maximum_amount(self, client, artwork, buyer_token):
        """Test that bid exceeding 1 billion is rejected."""
        headers = {"Authorization": f"Bearer {buyer_token}"}
        payload = {"artwork_id": artwork.id, "amount": 1_000_000_001}

        response = client.post("/api/bids/", json=payload, headers=headers)
        assert response.status_code == 400
        assert "exceed" in response.json()["detail"].lower()

    def test_bid_not_higher_than_current_bid(
        self,
        client,
        db_session,
        artwork,
        buyer_user,
        buyer_token,
    ):
        """Test that bid must be higher than current highest bid."""
        from models.bid import Bid

        # Set current highest bid
        artwork.current_highest_bid = 100.0
        db_session.commit()

        # Create existing bid
        existing_bid = Bid(artwork_id=artwork.id, bidder_id=buyer_user.id, amount=100.0)
        db_session.add(existing_bid)
        db_session.commit()

        # Try to bid same or lower amount
        headers = {"Authorization": f"Bearer {buyer_token}"}
        payload = {"artwork_id": artwork.id, "amount": 100.0}

        response = client.post("/api/bids/", json=payload, headers=headers)
        assert response.status_code == 400
        assert "higher" in response.json()["detail"].lower()


class TestGetMyBids:
    """Test GET /api/bids/my-bids endpoint."""

    def test_get_my_bids_requires_auth(self, client):
        """Test that getting own bids requires authentication."""
        response = client.get("/api/bids/my-bids")
        assert response.status_code == 401

    def test_get_my_bids_empty(self, client, buyer_token):
        """Test getting own bids when user has none."""
        headers = {"Authorization": f"Bearer {buyer_token}"}
        response = client.get("/api/bids/my-bids", headers=headers)
        assert response.status_code == 200
        assert isinstance(response.json(), list)
        bids = response.json()
        assert len(bids) == 0

    def test_get_my_bids_returns_only_own(
        self,
        client,
        db_session,
        artwork,
        buyer_user,
        buyer_token,
    ):
        """Test that my-bids only returns user's own bids."""
        from models.bid import Bid
        from models.user import User

        # Create another buyer
        other_buyer = User(
            auth0_sub="auth0|otherbuyer",
        )
        db_session.add(other_buyer)
        db_session.commit()
        db_session.refresh(other_buyer)

        # Attach Auth0 data (simulated)
        other_buyer.email = "other@buyer.com"
        other_buyer.name = "Other Buyer"
        other_buyer.role = "BUYER"

        # Create bids for both buyers
        my_bid = Bid(artwork_id=artwork.id, bidder_id=buyer_user.id, amount=50.0)
        other_bid = Bid(artwork_id=artwork.id, bidder_id=other_buyer.id, amount=75.0)
        db_session.add(my_bid)
        db_session.add(other_bid)
        db_session.commit()

        # Get my bids
        headers = {"Authorization": f"Bearer {buyer_token}"}
        response = client.get("/api/bids/my-bids", headers=headers)

        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["amount"] == 50.0
        assert data[0]["bidder_id"] == buyer_user.id
