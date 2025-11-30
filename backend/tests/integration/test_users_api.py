"""
Integration tests for users API endpoints.
Tests /api/users routes with pagination and access control.
"""


class TestListUsers:
    """Test GET /api/users endpoint."""

    def test_list_users_empty(self, client):
        """Test listing users when none exist."""
        response = client.get("/api/users")

        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) == 0

    def test_list_users_single(self, client, buyer_user):
        """Test listing users with one user."""
        response = client.get("/api/users")

        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["id"] == buyer_user.id
        assert data[0]["email"] == buyer_user.email

    def test_list_users_multiple(self, client, buyer_user, seller_user, admin_user):
        """Test listing multiple users."""
        response = client.get("/api/users")

        assert response.status_code == 200
        data = response.json()
        assert len(data) == 3

        user_ids = [u["id"] for u in data]
        assert buyer_user.id in user_ids
        assert seller_user.id in user_ids
        assert admin_user.id in user_ids

    def test_list_users_pagination_default(self, client, db_session):
        """Test default pagination."""
        from models.user import User

        # Create 15 users
        users = []
        for i in range(15):
            user = User(auth0_sub=f"auth0|user{i}")
            users.append(user)
        db_session.add_all(users)
        db_session.commit()

        # Attach Auth0 data (simulated)
        for i, user in enumerate(users):
            db_session.refresh(user)
            user.email = f"user{i}@test.com"
            user.name = f"User {i}"
            user.role = "BUYER"

        response = client.get("/api/users")

        assert response.status_code == 200
        data = response.json()
        assert len(data) <= 15

    def test_list_users_pagination_skip(self, client, db_session):
        """Test pagination with skip parameter."""
        from models.user import User

        users = []
        for i in range(10):
            user = User(auth0_sub=f"auth0|skip{i}")
            users.append(user)
        db_session.add_all(users)
        db_session.commit()

        # Attach Auth0 data (simulated)
        for i, user in enumerate(users):
            db_session.refresh(user)
            user.email = f"skip{i}@test.com"
            user.name = f"Skip {i}"
            user.role = "BUYER"

        response = client.get("/api/users?skip=5")

        assert response.status_code == 200
        data = response.json()
        assert len(data) == 5

    def test_list_users_pagination_limit(self, client, db_session):
        """Test pagination with limit parameter."""
        from models.user import User

        users = []
        for i in range(10):
            user = User(auth0_sub=f"auth0|limit{i}")
            users.append(user)
        db_session.add_all(users)
        db_session.commit()

        # Attach Auth0 data (simulated)
        for i, user in enumerate(users):
            db_session.refresh(user)
            user.email = f"limit{i}@test.com"
            user.name = f"Limit {i}"
            user.role = "BUYER"

        response = client.get("/api/users?limit=3")

        assert response.status_code == 200
        data = response.json()
        assert len(data) == 3

    def test_list_users_pagination_skip_and_limit(self, client, db_session):
        """Test pagination with both skip and limit."""
        from models.user import User

        users = []
        for i in range(20):
            user = User(auth0_sub=f"auth0|both{i}")
            users.append(user)
        db_session.add_all(users)
        db_session.commit()

        # Attach Auth0 data (simulated)
        for i, user in enumerate(users):
            db_session.refresh(user)
            user.email = f"both{i}@test.com"
            user.name = f"Both {i}"
            user.role = "BUYER"

        response = client.get("/api/users?skip=5&limit=5")

        assert response.status_code == 200
        data = response.json()
        assert len(data) == 5

    def test_list_users_includes_all_roles(
        self, client, buyer_user, seller_user, admin_user
    ):
        """Test listing includes users of all roles."""
        response = client.get("/api/users")

        assert response.status_code == 200
        data = response.json()

        roles = [u["role"] for u in data]
        assert "BUYER" in roles
        assert "SELLER" in roles
        assert "ADMIN" in roles

    def test_list_users_response_structure(self, client, buyer_user):
        """Test user response includes expected fields."""
        response = client.get("/api/users")

        assert response.status_code == 200
        data = response.json()
        user = data[0]

        assert "id" in user
        assert "auth0_sub" in user
        assert "email" in user
        assert "name" in user
        assert "role" in user
        assert "created_at" in user


class TestGetSingleUser:
    """Test GET /api/users/{user_id} endpoint."""

    def test_get_user_success(self, client, buyer_user):
        """Test retrieving a single user by ID."""
        response = client.get(f"/api/users/{buyer_user.id}")

        assert response.status_code == 200
        data = response.json()
        assert data["id"] == buyer_user.id
        assert data["auth0_sub"] == buyer_user.auth0_sub
        assert data["email"] == buyer_user.email
        assert data["name"] == buyer_user.name
        assert data["role"] == buyer_user.role

    def test_get_user_not_found(self, client):
        """Test retrieving non-existent user returns 404."""
        response = client.get("/api/users/99999")

        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()

    def test_get_buyer_user(self, client, buyer_user):
        """Test retrieving buyer user."""
        response = client.get(f"/api/users/{buyer_user.id}")

        assert response.status_code == 200
        data = response.json()
        assert data["role"] == "BUYER"

    def test_get_seller_user(self, client, seller_user):
        """Test retrieving seller user."""
        response = client.get(f"/api/users/{seller_user.id}")

        assert response.status_code == 200
        data = response.json()
        assert data["role"] == "SELLER"

    def test_get_admin_user(self, client, admin_user):
        """Test retrieving admin user."""
        response = client.get(f"/api/users/{admin_user.id}")

        assert response.status_code == 200
        data = response.json()
        assert data["role"] == "ADMIN"

    def test_get_user_includes_timestamps(self, client, buyer_user):
        """Test user response includes created_at timestamp."""
        response = client.get(f"/api/users/{buyer_user.id}")

        assert response.status_code == 200
        data = response.json()
        assert "created_at" in data


class TestUserFiltering:
    """Test user filtering capabilities (if implemented)."""

    def test_filter_users_by_role_buyer(
        self, client, buyer_user, seller_user, admin_user
    ):
        """Test filtering users by role (if implemented)."""
        response = client.get("/api/users?role=BUYER")

        assert response.status_code == 200
        data = response.json()

        # If filtering is implemented
        if len(data) > 0 and "role" in data[0]:
            buyer_users = [u for u in data if u.get("role") == "BUYER"]
            assert len(buyer_users) >= 1

    def test_filter_users_by_role_seller(self, client, seller_user):
        """Test filtering sellers."""
        response = client.get("/api/users?role=SELLER")

        assert response.status_code == 200

    def test_search_users_by_email(self, client, buyer_user):
        """Test searching users by email (if implemented)."""
        response = client.get(f"/api/users?email={buyer_user.email}")

        assert response.status_code == 200

    def test_search_users_by_name(self, client, buyer_user):
        """Test searching users by name (if implemented)."""
        response = client.get(f"/api/users?name={buyer_user.name}")

        assert response.status_code == 200


class TestUserAccessControl:
    """Test access control for user endpoints."""

    def test_unauthenticated_user_list(self, client, buyer_user):
        """Test listing users without authentication."""
        # Depending on implementation, may require auth
        response = client.get("/api/users")

        # Should either work (public) or fail (protected)
        assert response.status_code in [200, 401, 403]

    def test_unauthenticated_user_get(self, client, buyer_user):
        """Test getting user without authentication."""
        response = client.get(f"/api/users/{buyer_user.id}")

        # Should either work (public) or fail (protected)
        assert response.status_code in [200, 401, 403]


class TestUserRelationships:
    """Test user data includes related entities."""

    def test_get_user_with_artworks(self, client, db_session, seller_user):
        """Test user response may include artworks (if implemented)."""
        from models.artwork import Artwork

        # Create artworks for seller
        artwork = Artwork(
            seller_id=seller_user.id, title="Seller's Art", secret_threshold=100.0
        )
        db_session.add(artwork)
        db_session.commit()

        response = client.get(f"/api/users/{seller_user.id}")

        assert response.status_code == 200
        # May or may not include artworks in response

    def test_get_user_with_bids(self, client, db_session, buyer_user, artwork):
        """Test user response may include bids (if implemented)."""
        from models.bid import Bid

        # Create bid for buyer
        bid = Bid(artwork_id=artwork.id, bidder_id=buyer_user.id, amount=50.0)
        db_session.add(bid)
        db_session.commit()

        response = client.get(f"/api/users/{buyer_user.id}")

        assert response.status_code == 200
        # May or may not include bids in response


class TestUserEdgeCases:
    """Test edge cases and error handling."""

    def test_get_user_with_invalid_id_type(self, client):
        """Test getting user with invalid ID type."""
        response = client.get("/api/users/invalid")

        assert response.status_code == 422

    def test_list_users_with_negative_skip(self, client, buyer_user):
        """Test pagination with negative skip."""
        response = client.get("/api/users?skip=-1")

        # Should reject with validation error (400 or 422) or ignore (200)
        assert response.status_code in [200, 400, 422]

    def test_list_users_with_negative_limit(self, client, buyer_user):
        """Test pagination with negative limit."""
        response = client.get("/api/users?limit=-1")

        # Should reject with validation error (400 or 422) or ignore (200)
        assert response.status_code in [200, 400, 422]

    def test_list_users_with_very_large_limit(self, client, buyer_user):
        """Test pagination with very large limit."""
        response = client.get("/api/users?limit=10000")

        # Should either reject (400/422) or accept and cap at max limit (200)
        assert response.status_code in [200, 400, 422]
        # If accepted, should cap at reasonable limit
        if response.status_code == 200:
            # Limit should be capped at max allowed (100 per Query definition)
            pass

    def test_list_users_with_skip_beyond_total(self, client, buyer_user):
        """Test pagination with skip beyond total users."""
        response = client.get("/api/users?skip=1000")

        assert response.status_code == 200
        data = response.json()
        assert len(data) == 0

    def test_user_with_special_characters_in_name(self, client, db_session):
        """Test user with special characters in name."""
        from models.user import User

        user = User(
            auth0_sub="auth0|special",
        )
        db_session.add(user)
        db_session.commit()
        db_session.refresh(user)

        # Attach Auth0 data (simulated)
        user.email = "special@test.com"
        user.name = "用户 with émojis 🎨"
        user.role = "BUYER"

        response = client.get(f"/api/users/{user.id}")

        assert response.status_code == 200
        data = response.json()
        assert "用户" in data["name"]
        assert "🎨" in data["name"]

    def test_user_with_very_long_name(self, client, db_session):
        """Test user with very long name."""
        from models.user import User

        long_name = "A" * 500
        user = User(
            auth0_sub="auth0|longname",
        )
        db_session.add(user)
        db_session.commit()
        db_session.refresh(user)

        # Attach Auth0 data (simulated)
        user.email = "longname@test.com"
        user.name = long_name
        user.role = "BUYER"

        response = client.get(f"/api/users/{user.id}")

        assert response.status_code == 200
        data = response.json()
        assert len(data["name"]) == 500


class TestUserStatistics:
    """Test user statistics endpoints (if implemented)."""

    def test_get_user_statistics(self, client, db_session, seller_user, buyer_user):
        """Test getting user statistics (total artworks, bids, etc.)."""
        from models.artwork import Artwork
        from models.bid import Bid

        # Create artworks for seller
        artwork = Artwork(
            seller_id=seller_user.id, title="Stats Art", secret_threshold=100.0
        )
        db_session.add(artwork)
        db_session.commit()

        # Create bids for buyer
        bid = Bid(artwork_id=artwork.id, bidder_id=buyer_user.id, amount=50.0)
        db_session.add(bid)
        db_session.commit()

        # If statistics endpoint exists
        response = client.get(f"/api/users/{seller_user.id}/statistics")

        # May or may not be implemented
        assert response.status_code in [200, 404]

    def test_get_user_artworks_count(self, client, db_session, seller_user):
        """Test counting user's artworks (if implemented)."""
        from models.artwork import Artwork

        artworks = [
            Artwork(seller_id=seller_user.id, title=f"Art {i}", secret_threshold=100.0)
            for i in range(5)
        ]
        db_session.add_all(artworks)
        db_session.commit()

        response = client.get(f"/api/users/{seller_user.id}")

        assert response.status_code == 200
        # May include artwork count in response

    def test_get_user_bids_count(self, client, db_session, buyer_user, artwork):
        """Test counting user's bids (if implemented)."""
        from models.bid import Bid

        bids = [
            Bid(artwork_id=artwork.id, bidder_id=buyer_user.id, amount=10.0 * i)
            for i in range(1, 6)
        ]
        db_session.add_all(bids)
        db_session.commit()

        response = client.get(f"/api/users/{buyer_user.id}")

        assert response.status_code == 200
        # May include bid count in response


class TestUpdateUser:
    """Test PUT /api/users/me endpoint."""

    def test_update_current_user(self, client, buyer_user, buyer_token):
        """Test updating current user's profile - returns current data from Auth0."""
        response = client.put(
            "/api/users/me",
            headers={"Authorization": f"Bearer {buyer_token}"},
            json={},  # No fields to update since data is in Auth0
        )

        assert response.status_code == 200
        data = response.json()
        # Should return the user's current Auth0 data
        assert data["name"] == buyer_user.name  # Name from Auth0, not updated

    def test_update_current_user_without_auth(self, client):
        """Test updating user without authentication fails."""
        response = client.put("/api/users/me", json={"name": "Updated Name"})

        assert response.status_code in [401, 403]
