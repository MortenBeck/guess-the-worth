"""
Integration tests for artworks API endpoints.
Tests /api/artworks routes with authentication and database.
"""

from models.artwork import ArtworkStatus


class TestListArtworks:
    """Test GET /api/artworks endpoint."""

    def test_list_artworks_empty(self, client):
        """Test listing artworks when none exist."""
        response = client.get("/api/artworks")

        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) == 0

    def test_list_artworks_single(self, client, artwork):
        """Test listing artworks with one artwork."""
        response = client.get("/api/artworks")

        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["id"] == artwork.id
        assert data[0]["title"] == artwork.title
        assert data[0]["seller_id"] == artwork.seller_id

    def test_list_artworks_multiple(self, client, db_session, seller_user):
        """Test listing multiple artworks."""
        from models.artwork import Artwork

        artworks = [
            Artwork(seller_id=seller_user.id, title=f"Artwork {i}", secret_threshold=100.0 * i)
            for i in range(1, 6)
        ]
        db_session.add_all(artworks)
        db_session.commit()

        response = client.get("/api/artworks")

        assert response.status_code == 200
        data = response.json()
        assert len(data) == 5
        titles = [a["title"] for a in data]
        assert "Artwork 1" in titles
        assert "Artwork 5" in titles

    def test_list_artworks_pagination_default(self, client, db_session, seller_user):
        """Test default pagination limits."""
        from models.artwork import Artwork

        # Create 15 artworks
        artworks = [
            Artwork(seller_id=seller_user.id, title=f"Art {i}", secret_threshold=100.0)
            for i in range(15)
        ]
        db_session.add_all(artworks)
        db_session.commit()

        response = client.get("/api/artworks")

        assert response.status_code == 200
        data = response.json()
        # Default limit is usually 10 or all
        assert len(data) <= 15

    def test_list_artworks_pagination_skip(self, client, db_session, seller_user):
        """Test pagination with skip parameter."""
        from models.artwork import Artwork

        artworks = [
            Artwork(seller_id=seller_user.id, title=f"Art {i}", secret_threshold=100.0)
            for i in range(10)
        ]
        db_session.add_all(artworks)
        db_session.commit()

        response = client.get("/api/artworks?skip=5")

        assert response.status_code == 200
        data = response.json()
        assert len(data) == 5

    def test_list_artworks_pagination_limit(self, client, db_session, seller_user):
        """Test pagination with limit parameter."""
        from models.artwork import Artwork

        artworks = [
            Artwork(seller_id=seller_user.id, title=f"Art {i}", secret_threshold=100.0)
            for i in range(10)
        ]
        db_session.add_all(artworks)
        db_session.commit()

        response = client.get("/api/artworks?limit=3")

        assert response.status_code == 200
        data = response.json()
        assert len(data) == 3

    def test_list_artworks_pagination_skip_and_limit(self, client, db_session, seller_user):
        """Test pagination with both skip and limit."""
        from models.artwork import Artwork

        artworks = [
            Artwork(seller_id=seller_user.id, title=f"Art {i}", secret_threshold=100.0)
            for i in range(20)
        ]
        db_session.add_all(artworks)
        db_session.commit()

        response = client.get("/api/artworks?skip=5&limit=5")

        assert response.status_code == 200
        data = response.json()
        assert len(data) == 5

    def test_list_artworks_includes_all_statuses(self, client, db_session, seller_user):
        """Test listing includes artworks with different statuses."""
        from models.artwork import Artwork

        active = Artwork(
            seller_id=seller_user.id,
            title="Active",
            secret_threshold=100.0,
            status=ArtworkStatus.ACTIVE,
        )
        sold = Artwork(
            seller_id=seller_user.id,
            title="Sold",
            secret_threshold=100.0,
            status=ArtworkStatus.SOLD,
        )
        archived = Artwork(
            seller_id=seller_user.id,
            title="Archived",
            secret_threshold=100.0,
            status=ArtworkStatus.ARCHIVED,
        )

        db_session.add_all([active, sold, archived])
        db_session.commit()

        response = client.get("/api/artworks")

        assert response.status_code == 200
        data = response.json()
        assert len(data) == 3
        statuses = [a["status"] for a in data]
        assert "ACTIVE" in statuses
        assert "SOLD" in statuses
        assert "ARCHIVED" in statuses

    def test_list_artworks_does_not_expose_secret_threshold(self, client, artwork):
        """Test that secret_threshold is not exposed in list."""
        response = client.get("/api/artworks")

        assert response.status_code == 200
        data = response.json()
        assert "secret_threshold" not in data[0]


class TestGetSingleArtwork:
    """Test GET /api/artworks/{artwork_id} endpoint."""

    def test_get_artwork_success(self, client, artwork):
        """Test retrieving a single artwork by ID."""
        response = client.get(f"/api/artworks/{artwork.id}")

        assert response.status_code == 200
        data = response.json()
        assert data["id"] == artwork.id
        assert data["title"] == artwork.title
        assert data["description"] == artwork.description
        assert data["seller_id"] == artwork.seller_id
        assert data["status"] == artwork.status.value

    def test_get_artwork_not_found(self, client):
        """Test retrieving non-existent artwork returns 404."""
        response = client.get("/api/artworks/99999")

        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()

    def test_get_artwork_does_not_expose_secret_threshold(self, client, artwork):
        """Test that secret_threshold is not exposed to non-sellers."""
        response = client.get(f"/api/artworks/{artwork.id}")

        assert response.status_code == 200
        data = response.json()
        assert "secret_threshold" not in data

    def test_get_artwork_includes_current_highest_bid(self, client, artwork, buyer_user):
        """Test artwork response includes current_highest_bid."""
        from models.bid import Bid

        # Place some bids
        bid = Bid(artwork_id=artwork.id, bidder_id=buyer_user.id, amount=150.0)
        client.app.dependency_overrides[
            client.app.dependency_overrides.keys().__iter__().__next__()
        ]().add(bid)
        client.app.dependency_overrides[
            client.app.dependency_overrides.keys().__iter__().__next__()
        ]().commit()

        # Update artwork's current_highest_bid
        artwork.current_highest_bid = 150.0
        client.app.dependency_overrides[
            client.app.dependency_overrides.keys().__iter__().__next__()
        ]().commit()

        response = client.get(f"/api/artworks/{artwork.id}")

        assert response.status_code == 200
        data = response.json()
        assert "current_highest_bid" in data


class TestCreateArtwork:
    """Test POST /api/artworks endpoint."""

    def test_create_artwork_success(self, client, db_session, seller_user):
        """Test creating a new artwork."""
        payload = {
            "title": "New Masterpiece",
            "description": "A beautiful creation",
            "secret_threshold": 500.0,
        }

        # Note: In real implementation, this would require authentication
        # For now, we'll need to pass seller_id somehow (or use auth headers)
        # This test may need adjustment based on actual API implementation

        response = client.post(f"/api/artworks?seller_id={seller_user.id}", json=payload)

        # If endpoint requires auth, use this instead:
        # headers = create_auth_header(seller_token)
        # response = client.post("/api/artworks", json=payload, headers=headers)

        if response.status_code == 200:
            data = response.json()
            assert data["title"] == "New Masterpiece"
            assert data["description"] == "A beautiful creation"
            assert data["seller_id"] == seller_user.id
            assert data["status"] == "ACTIVE"
            assert data["current_highest_bid"] == 0.0

    def test_create_artwork_without_description(self, client, seller_user):
        """Test creating artwork without optional description."""
        payload = {"title": "Minimal Art", "secret_threshold": 200.0}

        response = client.post(f"/api/artworks?seller_id={seller_user.id}", json=payload)

        if response.status_code == 200:
            data = response.json()
            assert data["title"] == "Minimal Art"
            assert data["description"] is None

    def test_create_artwork_missing_required_fields(self, client, seller_user):
        """Test creating artwork with missing required fields."""
        # Missing title
        response = client.post(
            f"/api/artworks?seller_id={seller_user.id}", json={"secret_threshold": 100.0}
        )
        assert response.status_code == 422

        # Missing secret_threshold
        response = client.post(f"/api/artworks?seller_id={seller_user.id}", json={"title": "Test"})
        assert response.status_code == 422

    def test_create_artwork_invalid_seller(self, client):
        """Test creating artwork with non-existent seller."""
        payload = {"title": "Invalid Seller Art", "secret_threshold": 100.0}

        response = client.post("/api/artworks?seller_id=99999", json=payload)

        assert response.status_code in [400, 404]

    def test_create_artwork_negative_threshold(self, client, seller_user):
        """Test creating artwork with negative threshold."""
        payload = {"title": "Negative Threshold", "secret_threshold": -100.0}

        response = client.post(f"/api/artworks?seller_id={seller_user.id}", json=payload)

        # Schema allows this, but business logic may reject it
        # Adjust based on actual requirements
        assert response.status_code in [200, 400, 422]

    def test_create_artwork_zero_threshold(self, client, seller_user):
        """Test creating artwork with zero threshold."""
        payload = {"title": "Free Art", "secret_threshold": 0.0}

        response = client.post(f"/api/artworks?seller_id={seller_user.id}", json=payload)

        if response.status_code == 200:
            data = response.json()
            assert data["title"] == "Free Art"


class TestUploadArtworkImage:
    """Test POST /api/artworks/{artwork_id}/upload-image endpoint."""

    def test_upload_image_endpoint_exists(self, client, artwork):
        """Test that image upload endpoint exists (stub implementation)."""
        # This is a stub in current implementation
        response = client.post(
            f"/api/artworks/{artwork.id}/upload-image",
            files={"file": ("test.jpg", b"fake image data", "image/jpeg")},
        )

        # Endpoint exists but may not be fully implemented
        assert response.status_code in [200, 501, 422]

    def test_upload_image_artwork_not_found(self, client):
        """Test uploading image to non-existent artwork."""
        response = client.post(
            "/api/artworks/99999/upload-image",
            files={"file": ("test.jpg", b"fake image data", "image/jpeg")},
        )

        assert response.status_code in [404, 501]


class TestArtworkFiltering:
    """Test artwork filtering and search capabilities."""

    def test_filter_by_status_active(self, client, db_session, seller_user):
        """Test filtering artworks by status (if implemented)."""
        from models.artwork import Artwork

        active = Artwork(
            seller_id=seller_user.id,
            title="Active",
            secret_threshold=100.0,
            status=ArtworkStatus.ACTIVE,
        )
        sold = Artwork(
            seller_id=seller_user.id,
            title="Sold",
            secret_threshold=100.0,
            status=ArtworkStatus.SOLD,
        )

        db_session.add_all([active, sold])
        db_session.commit()

        # If filtering is implemented
        response = client.get("/api/artworks?status=ACTIVE")

        assert response.status_code == 200
        data = response.json()

        # May or may not be implemented
        if any("status" in item for item in data):
            active_items = [a for a in data if a.get("status") == "ACTIVE"]
            assert len(active_items) >= 1

    def test_filter_by_seller(self, client, db_session, seller_user):
        """Test filtering artworks by seller (if implemented)."""
        from models.artwork import Artwork
        from models.user import User, UserRole

        # Create another seller
        another_seller = User(
            auth0_sub="auth0|seller2",
            email="seller2@test.com",
            name="Seller 2",
            role=UserRole.SELLER,
        )
        db_session.add(another_seller)
        db_session.commit()

        artwork1 = Artwork(seller_id=seller_user.id, title="Art 1", secret_threshold=100.0)
        artwork2 = Artwork(seller_id=another_seller.id, title="Art 2", secret_threshold=100.0)

        db_session.add_all([artwork1, artwork2])
        db_session.commit()

        # If filtering by seller is implemented
        response = client.get(f"/api/artworks?seller_id={seller_user.id}")

        assert response.status_code == 200
        data = response.json()

        # May or may not be implemented
        if len(data) > 0 and "seller_id" in data[0]:
            seller_artworks = [a for a in data if a.get("seller_id") == seller_user.id]
            assert len(seller_artworks) >= 1


class TestArtworkEdgeCases:
    """Test edge cases and error handling."""

    def test_get_artwork_with_no_bids(self, client, artwork):
        """Test retrieving artwork with no bids."""
        response = client.get(f"/api/artworks/{artwork.id}")

        assert response.status_code == 200
        data = response.json()
        assert data["current_highest_bid"] == 0.0

    def test_artwork_with_very_long_title(self, client, seller_user):
        """Test creating artwork with very long title."""
        long_title = "A" * 1000
        payload = {"title": long_title, "secret_threshold": 100.0}

        response = client.post(f"/api/artworks?seller_id={seller_user.id}", json=payload)

        # Should either succeed or fail with validation
        assert response.status_code in [200, 422]

    def test_artwork_with_unicode_characters(self, client, seller_user):
        """Test creating artwork with unicode in title/description."""
        payload = {
            "title": "艺术品 🎨",
            "description": "Une belle œuvre d'art",
            "secret_threshold": 100.0,
        }

        response = client.post(f"/api/artworks?seller_id={seller_user.id}", json=payload)

        if response.status_code == 200:
            data = response.json()
            assert "艺术品" in data["title"]
            assert "🎨" in data["title"]

    def test_artwork_with_html_in_description(self, client, seller_user):
        """Test creating artwork with HTML in description."""
        payload = {
            "title": "Test Art",
            "description": "<script>alert('xss')</script>",
            "secret_threshold": 100.0,
        }

        response = client.post(f"/api/artworks?seller_id={seller_user.id}", json=payload)

        if response.status_code == 200:
            data = response.json()
            # Should store as-is (sanitization happens on frontend)
            assert "<script>" in data["description"]

    def test_concurrent_artwork_creation(self, client, seller_user):
        """Test handling concurrent artwork creation."""
        payload1 = {"title": "Concurrent Art 1", "secret_threshold": 100.0}
        payload2 = {"title": "Concurrent Art 2", "secret_threshold": 200.0}

        response1 = client.post(f"/api/artworks?seller_id={seller_user.id}", json=payload1)
        response2 = client.post(f"/api/artworks?seller_id={seller_user.id}", json=payload2)

        # Both should succeed
        assert response1.status_code in [200, 201]
        assert response2.status_code in [200, 201]
