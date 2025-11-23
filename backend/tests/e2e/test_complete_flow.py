"""
End-to-end tests for complete user flows.
Tests full workflows from registration through bidding to purchase.
"""

from unittest.mock import patch


class TestCompleteUserFlow:
    """Test complete user journey from registration to purchase."""

    @patch("services.auth_service.AuthService.verify_auth0_token")
    def test_buyer_registration_to_winning_bid_flow(
        self, mock_verify, client, db_session, mock_auth0_response
    ):
        """
        Complete flow:
        1. Buyer registers
        2. Seller registers
        3. Seller creates artwork
        4. Buyer places losing bid
        5. Buyer places winning bid
        6. Artwork is sold
        """
        # Step 1: Register buyer
        buyer_payload = {
            "email": "buyer@e2e.com",
            "name": "E2E Buyer",
            "auth0_sub": "auth0|e2e_buyer",
            "role": "BUYER",
        }
        buyer_response = client.post("/api/auth/register", json=buyer_payload)
        assert buyer_response.status_code == 200
        buyer_data = buyer_response.json()
        buyer_id = buyer_data["id"]

        # Step 2: Register seller
        seller_payload = {
            "email": "seller@e2e.com",
            "name": "E2E Seller",
            "auth0_sub": "auth0|e2e_seller",
            "role": "SELLER",
        }
        seller_response = client.post("/api/auth/register", json=seller_payload)
        assert seller_response.status_code == 200
        seller_data = seller_response.json()
        seller_id = seller_data["id"]

        # Step 3: Seller creates artwork
        artwork_payload = {
            "title": "E2E Masterpiece",
            "description": "Beautiful test artwork",
            "secret_threshold": 500.0,
        }
        artwork_response = client.post(f"/api/artworks?seller_id={seller_id}", json=artwork_payload)
        assert artwork_response.status_code == 200
        artwork_data = artwork_response.json()
        artwork_id = artwork_data["id"]
        assert artwork_data["status"] == "ACTIVE"
        assert artwork_data["current_highest_bid"] == 0.0

        # Step 4: Buyer places losing bid
        losing_bid_payload = {"artwork_id": artwork_id, "amount": 300.0}  # Below threshold
        losing_bid_response = client.post(
            f"/api/bids?bidder_id={buyer_id}", json=losing_bid_payload
        )
        assert losing_bid_response.status_code == 200
        losing_bid_data = losing_bid_response.json()
        assert losing_bid_data["is_winning"] is False
        assert losing_bid_data["amount"] == 300.0

        # Verify artwork still active
        artwork_check = client.get(f"/api/artworks/{artwork_id}")
        assert artwork_check.json()["status"] == "ACTIVE"

        # Step 5: Buyer places winning bid
        winning_bid_payload = {"artwork_id": artwork_id, "amount": 500.0}  # At threshold
        winning_bid_response = client.post(
            f"/api/bids?bidder_id={buyer_id}", json=winning_bid_payload
        )
        assert winning_bid_response.status_code == 200
        winning_bid_data = winning_bid_response.json()
        assert winning_bid_data["is_winning"] is True
        assert winning_bid_data["amount"] == 500.0

        # Step 6: Verify artwork is sold
        final_artwork = client.get(f"/api/artworks/{artwork_id}")
        assert final_artwork.status_code == 200
        final_artwork_data = final_artwork.json()
        assert final_artwork_data["status"] == "SOLD"
        assert final_artwork_data["current_highest_bid"] == 500.0

        # Verify all bids are recorded
        bids_response = client.get(f"/api/bids/artwork/{artwork_id}")
        assert bids_response.status_code == 200
        all_bids = bids_response.json()
        assert len(all_bids) == 2


class TestMultipleUsersCompetingFlow:
    """Test flow with multiple buyers competing for artwork."""

    def test_multiple_buyers_bidding_competition(self, client, db_session):
        """
        Flow:
        1. Seller creates artwork
        2. Multiple buyers register
        3. Buyers compete with bids
        4. Highest bidder wins
        """
        # Step 1: Register seller
        seller_payload = {
            "email": "seller@compete.com",
            "name": "Competition Seller",
            "auth0_sub": "auth0|compete_seller",
            "role": "SELLER",
        }
        seller_response = client.post("/api/auth/register", json=seller_payload)
        seller_id = seller_response.json()["id"]

        # Create artwork
        artwork_payload = {"title": "Competitive Art", "secret_threshold": 1000.0}
        artwork_response = client.post(f"/api/artworks?seller_id={seller_id}", json=artwork_payload)
        artwork_id = artwork_response.json()["id"]

        # Step 2: Register 3 buyers
        buyers = []
        for i in range(1, 4):
            buyer_payload = {
                "email": f"buyer{i}@compete.com",
                "name": f"Buyer {i}",
                "auth0_sub": f"auth0|compete_buyer{i}",
                "role": "BUYER",
            }
            response = client.post("/api/auth/register", json=buyer_payload)
            buyers.append(response.json()["id"])

        # Step 3: Buyers place increasing bids
        bid_amounts = [
            (buyers[0], 200.0),  # Buyer 1: 200
            (buyers[1], 400.0),  # Buyer 2: 400
            (buyers[0], 600.0),  # Buyer 1: 600 (outbids Buyer 2)
            (buyers[2], 800.0),  # Buyer 3: 800 (outbids Buyer 1)
        ]

        for buyer_id, amount in bid_amounts:
            bid_response = client.post(
                f"/api/bids?bidder_id={buyer_id}", json={"artwork_id": artwork_id, "amount": amount}
            )
            assert bid_response.status_code == 200

        # Verify current highest bid
        artwork_check = client.get(f"/api/artworks/{artwork_id}")
        assert artwork_check.json()["current_highest_bid"] == 800.0
        assert artwork_check.json()["status"] == "ACTIVE"  # Still below threshold

        # Step 4: Buyer 3 places winning bid
        winning_response = client.post(
            f"/api/bids?bidder_id={buyers[2]}", json={"artwork_id": artwork_id, "amount": 1000.0}
        )
        assert winning_response.status_code == 200
        assert winning_response.json()["is_winning"] is True

        # Verify artwork sold
        final_artwork = client.get(f"/api/artworks/{artwork_id}")
        assert final_artwork.json()["status"] == "SOLD"

        # Verify Buyer 1 and Buyer 2 cannot bid anymore
        late_bid = client.post(
            f"/api/bids?bidder_id={buyers[0]}", json={"artwork_id": artwork_id, "amount": 1500.0}
        )
        assert late_bid.status_code == 400


class TestSellerMultipleArtworksFlow:
    """Test seller creating and managing multiple artworks."""

    def test_seller_creates_multiple_artworks_different_outcomes(self, client):
        """
        Flow:
        1. Seller creates multiple artworks
        2. Some get sold, some remain active
        3. Verify seller's artworks
        """
        # Register seller
        seller_payload = {
            "email": "multi@seller.com",
            "name": "Multi Seller",
            "auth0_sub": "auth0|multi_seller",
            "role": "SELLER",
        }
        seller_response = client.post("/api/auth/register", json=seller_payload)
        seller_id = seller_response.json()["id"]

        # Register buyer
        buyer_payload = {
            "email": "multi@buyer.com",
            "name": "Multi Buyer",
            "auth0_sub": "auth0|multi_buyer",
            "role": "BUYER",
        }
        buyer_response = client.post("/api/auth/register", json=buyer_payload)
        buyer_id = buyer_response.json()["id"]

        # Create 3 artworks
        artworks = []
        for i in range(1, 4):
            artwork_payload = {"title": f"Artwork {i}", "secret_threshold": 100.0 * i}
            response = client.post(f"/api/artworks?seller_id={seller_id}", json=artwork_payload)
            artworks.append(response.json())

        # Buy first artwork (threshold = 100)
        client.post(
            f"/api/bids?bidder_id={buyer_id}",
            json={"artwork_id": artworks[0]["id"], "amount": 100.0},
        )

        # Bid on second but don't reach threshold (threshold = 200)
        client.post(
            f"/api/bids?bidder_id={buyer_id}",
            json={"artwork_id": artworks[1]["id"], "amount": 150.0},
        )

        # Don't bid on third

        # Verify artwork statuses
        artwork1 = client.get(f"/api/artworks/{artworks[0]['id']}")
        assert artwork1.json()["status"] == "SOLD"

        artwork2 = client.get(f"/api/artworks/{artworks[1]['id']}")
        assert artwork2.json()["status"] == "ACTIVE"

        artwork3 = client.get(f"/api/artworks/{artworks[2]['id']}")
        assert artwork3.json()["status"] == "ACTIVE"


class TestErrorRecoveryFlow:
    """Test error handling and recovery scenarios."""

    def test_invalid_bid_then_valid_bid_flow(self, client):
        """
        Flow:
        1. User tries invalid bid (should fail)
        2. User corrects and places valid bid
        3. Bid succeeds
        """
        # Setup: Register users and create artwork
        seller_payload = {
            "email": "error@seller.com",
            "name": "Error Seller",
            "auth0_sub": "auth0|error_seller",
            "role": "SELLER",
        }
        seller_response = client.post("/api/auth/register", json=seller_payload)
        seller_id = seller_response.json()["id"]

        buyer_payload = {
            "email": "error@buyer.com",
            "name": "Error Buyer",
            "auth0_sub": "auth0|error_buyer",
            "role": "BUYER",
        }
        buyer_response = client.post("/api/auth/register", json=buyer_payload)
        buyer_id = buyer_response.json()["id"]

        artwork_payload = {"title": "Error Test Art", "secret_threshold": 100.0}
        artwork_response = client.post(f"/api/artworks?seller_id={seller_id}", json=artwork_payload)
        artwork_id = artwork_response.json()["id"]

        # Step 1: Try invalid bid (negative amount)
        invalid_bid = client.post(
            f"/api/bids?bidder_id={buyer_id}", json={"artwork_id": artwork_id, "amount": -50.0}
        )
        assert invalid_bid.status_code in [400, 422]

        # Step 2: Try valid bid
        valid_bid = client.post(
            f"/api/bids?bidder_id={buyer_id}", json={"artwork_id": artwork_id, "amount": 75.0}
        )
        assert valid_bid.status_code == 200

        # Verify bid was recorded
        bids = client.get(f"/api/bids/artwork/{artwork_id}")
        assert len(bids.json()) == 1

    def test_attempt_duplicate_registration(self, client):
        """
        Flow:
        1. User registers
        2. User tries to register again (should fail)
        3. User can still use original account
        """
        # First registration
        user_payload = {
            "email": "duplicate@test.com",
            "name": "Duplicate User",
            "auth0_sub": "auth0|duplicate",
            "role": "BUYER",
        }
        first_response = client.post("/api/auth/register", json=user_payload)
        assert first_response.status_code == 200
        user_id = first_response.json()["id"]

        # Attempt duplicate registration
        second_response = client.post("/api/auth/register", json=user_payload)
        assert second_response.status_code == 400

        # Verify original account still accessible
        user_check = client.get(f"/api/users/{user_id}")
        assert user_check.status_code == 200


class TestCompleteMarketplaceFlow:
    """Test comprehensive marketplace scenario."""

    def test_complete_marketplace_scenario(self, client):
        """
        Complete marketplace flow:
        1. Multiple sellers create artworks
        2. Multiple buyers browse and bid
        3. Some artworks sold, some remain
        4. Verify marketplace state
        """
        # Setup: Create 2 sellers, 3 buyers
        sellers = []
        for i in range(1, 3):
            payload = {
                "email": f"market_seller{i}@test.com",
                "name": f"Market Seller {i}",
                "auth0_sub": f"auth0|market_seller{i}",
                "role": "SELLER",
            }
            response = client.post("/api/auth/register", json=payload)
            sellers.append(response.json()["id"])

        buyers = []
        for i in range(1, 4):
            payload = {
                "email": f"market_buyer{i}@test.com",
                "name": f"Market Buyer {i}",
                "auth0_sub": f"auth0|market_buyer{i}",
                "role": "BUYER",
            }
            response = client.post("/api/auth/register", json=payload)
            buyers.append(response.json()["id"])

        # Each seller creates 2 artworks
        artworks = []
        for seller_id in sellers:
            for j in range(1, 3):
                payload = {
                    "title": f"Market Art S{sellers.index(seller_id)+1}-A{j}",
                    "secret_threshold": 100.0 * j,
                }
                response = client.post(f"/api/artworks?seller_id={seller_id}", json=payload)
                artworks.append(response.json())

        # Buyers bid on various artworks
        # Buyer 1 wins artwork 1
        client.post(
            f"/api/bids?bidder_id={buyers[0]}",
            json={"artwork_id": artworks[0]["id"], "amount": 100.0},
        )

        # Buyer 2 and 3 compete on artwork 2
        client.post(
            f"/api/bids?bidder_id={buyers[1]}",
            json={"artwork_id": artworks[1]["id"], "amount": 150.0},
        )
        client.post(
            f"/api/bids?bidder_id={buyers[2]}",
            json={"artwork_id": artworks[1]["id"], "amount": 200.0},
        )

        # Buyer 3 bids on artwork 3 but doesn't win
        client.post(
            f"/api/bids?bidder_id={buyers[2]}",
            json={"artwork_id": artworks[2]["id"], "amount": 50.0},
        )

        # Verify marketplace state
        all_artworks = client.get("/api/artworks")
        assert all_artworks.status_code == 200
        artwork_list = all_artworks.json()
        assert len(artwork_list) == 4

        # Count sold vs active
        sold_count = sum(1 for a in artwork_list if a["status"] == "SOLD")
        active_count = sum(1 for a in artwork_list if a["status"] == "ACTIVE")

        assert sold_count >= 1  # At least artwork 1 is sold
        assert active_count >= 2  # At least 2 remain active

        # Verify all users exist
        all_users = client.get("/api/users")
        assert len(all_users.json()) == 5  # 2 sellers + 3 buyers


class TestEdgeCaseFlows:
    """Test edge case scenarios."""

    def test_immediate_purchase_at_threshold(self, client):
        """
        Flow: Buyer immediately purchases by bidding at threshold.
        """
        # Setup
        seller = client.post(
            "/api/auth/register",
            json={
                "email": "instant@seller.com",
                "name": "Instant Seller",
                "auth0_sub": "auth0|instant_seller",
                "role": "SELLER",
            },
        ).json()

        buyer = client.post(
            "/api/auth/register",
            json={
                "email": "instant@buyer.com",
                "name": "Instant Buyer",
                "auth0_sub": "auth0|instant_buyer",
                "role": "BUYER",
            },
        ).json()

        artwork = client.post(
            f"/api/artworks?seller_id={seller['id']}",
            json={"title": "Instant Buy", "secret_threshold": 250.0},
        ).json()

        # Immediate purchase
        bid = client.post(
            f"/api/bids?bidder_id={buyer['id']}",
            json={"artwork_id": artwork["id"], "amount": 250.0},
        )

        assert bid.status_code == 200
        assert bid.json()["is_winning"] is True

        # Verify sold immediately
        final_artwork = client.get(f"/api/artworks/{artwork['id']}")
        assert final_artwork.json()["status"] == "SOLD"
        assert final_artwork.json()["current_highest_bid"] == 250.0

    def test_zero_threshold_artwork(self, client):
        """
        Flow: Artwork with threshold of 0 (free or any bid wins).
        """
        seller = client.post(
            "/api/auth/register",
            json={
                "email": "free@seller.com",
                "name": "Free Seller",
                "auth0_sub": "auth0|free_seller",
                "role": "SELLER",
            },
        ).json()

        buyer = client.post(
            "/api/auth/register",
            json={
                "email": "free@buyer.com",
                "name": "Free Buyer",
                "auth0_sub": "auth0|free_buyer",
                "role": "BUYER",
            },
        ).json()

        # Create free artwork
        artwork = client.post(
            f"/api/artworks?seller_id={seller['id']}",
            json={"title": "Free Art", "secret_threshold": 0.0},
        )

        if artwork.status_code == 200:
            artwork_id = artwork.json()["id"]

            # Any bid should win
            bid = client.post(
                f"/api/bids?bidder_id={buyer['id']}",
                json={"artwork_id": artwork_id, "amount": 0.01},
            )

            if bid.status_code == 200:
                assert bid.json()["is_winning"] is True


class TestAdminOversightFlow:
    """Test admin monitoring and oversight of platform activity."""

    def test_complete_auction_with_admin_oversight(
        self, client, seller_user, buyer_user, admin_user, seller_token, buyer_token, admin_token
    ):
        """
        Complete flow with admin oversight:
        1. Seller creates artwork
        2. Buyer places bids
        3. Artwork is sold
        4. Admin views transaction
        5. Admin verifies audit logs
        """
        # Step 1: Seller creates artwork
        artwork_payload = {
            "title": "Admin Oversight Test",
            "description": "Testing admin monitoring",
            "artist_name": "Test Artist",
            "category": "painting",
            "secret_threshold": 500.0,
        }
        artwork_response = client.post(
            "/api/artworks/",
            json=artwork_payload,
            headers={"Authorization": f"Bearer {seller_token}"},
        )
        assert artwork_response.status_code == 200
        artwork = artwork_response.json()
        artwork_id = artwork["id"]

        # Step 2: Buyer places losing bid
        losing_bid_response = client.post(
            "/api/bids/",
            json={"artwork_id": artwork_id, "amount": 200.0},
            headers={"Authorization": f"Bearer {buyer_token}"},
        )
        assert losing_bid_response.status_code == 200
        assert losing_bid_response.json()["is_winning"] is False

        # Step 3: Buyer places winning bid
        winning_bid_response = client.post(
            "/api/bids/",
            json={"artwork_id": artwork_id, "amount": 600.0},
            headers={"Authorization": f"Bearer {buyer_token}"},
        )
        assert winning_bid_response.status_code == 200
        assert winning_bid_response.json()["is_winning"] is True

        # Step 4: Admin views transactions
        transactions_response = client.get(
            "/api/admin/transactions",
            headers={"Authorization": f"Bearer {admin_token}"},
        )
        assert transactions_response.status_code == 200
        transactions = transactions_response.json()
        assert len(transactions) > 0
        # Verify our transaction is in the list
        assert any(
            t.get("artwork_id") == artwork_id or t.get("title") == "Admin Oversight Test"
            for t in transactions
        )

        # Step 5: Admin views audit logs
        audit_logs_response = client.get(
            "/api/admin/audit-logs",
            headers={"Authorization": f"Bearer {admin_token}"},
        )
        assert audit_logs_response.status_code == 200
        logs = audit_logs_response.json()
        assert len(logs) > 0
        # Verify bid-related audit logs exist
        assert any(log.get("action") in ["bid_placed", "artwork_sold"] for log in logs)

        # Step 6: Admin views platform stats
        stats_response = client.get(
            "/api/admin/stats/overview",
            headers={"Authorization": f"Bearer {admin_token}"},
        )
        assert stats_response.status_code == 200
        stats = stats_response.json()
        assert "total_users" in stats
        assert "total_artworks" in stats

    def test_admin_user_management(self, client, buyer_user, admin_user, buyer_token, admin_token):
        """Test admin user management capabilities."""
        # Step 1: Admin lists all users
        users_response = client.get(
            "/api/admin/users", headers={"Authorization": f"Bearer {admin_token}"}
        )
        assert users_response.status_code == 200
        users = users_response.json()
        assert len(users) >= 2  # At least buyer and admin

        # Step 2: Admin gets specific user details
        user_details_response = client.get(
            f"/api/admin/users/{buyer_user.id}",
            headers={"Authorization": f"Bearer {admin_token}"},
        )
        assert user_details_response.status_code == 200
        user_details = user_details_response.json()
        assert user_details["id"] == buyer_user.id
        assert "stats" in user_details

        # Step 3: Verify non-admin cannot access admin endpoints
        unauthorized_response = client.get(
            "/api/admin/users", headers={"Authorization": f"Bearer {buyer_token}"}
        )
        assert unauthorized_response.status_code == 403

    def test_admin_system_health_monitoring(self, client, admin_token):
        """Test admin can monitor system health."""
        health_response = client.get(
            "/api/admin/system/health",
            headers={"Authorization": f"Bearer {admin_token}"},
        )
        assert health_response.status_code == 200
        health = health_response.json()
        assert "database" in health
        assert "status" in health
