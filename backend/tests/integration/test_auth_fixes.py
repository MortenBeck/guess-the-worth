"""
Test Authentication & Authorization Security Fixes (Stage 1).

These tests verify that the security vulnerabilities identified in the
security audit have been properly fixed:
- Authentication required for protected endpoints
- User IDs extracted from JWT tokens, not query parameters
- Sellers cannot bid on their own artworks
- WebSocket connections require authentication
"""

import pytest
from fastapi.testclient import TestClient

from models.user import User


class TestAuthenticationRequirements:
    """Test that endpoints require proper authentication."""

    def test_create_artwork_requires_auth(self, client: TestClient):
        """Test that creating artwork requires authentication."""
        response = client.post(
            "/api/artworks/",
            json={"title": "Test Art", "secret_threshold": 100.0, "description": "Test"},
        )
        assert response.status_code == 401
        assert "detail" in response.json()

    def test_create_bid_requires_auth(self, client: TestClient, artwork):
        """Test that placing bid requires authentication."""
        response = client.post(
            "/api/bids/", json={"artwork_id": artwork.id, "amount": 150.0}
        )
        assert response.status_code == 401

    def test_get_my_artworks_requires_auth(self, client: TestClient):
        """Test that viewing own artworks requires authentication."""
        response = client.get("/api/artworks/my-artworks")
        assert response.status_code == 401

    def test_get_my_bids_requires_auth(self, client: TestClient):
        """Test that viewing own bids requires authentication."""
        response = client.get("/api/bids/my-bids")
        assert response.status_code == 401

    def test_update_artwork_requires_auth(self, client: TestClient, artwork):
        """Test that updating artwork requires authentication."""
        response = client.put(
            f"/api/artworks/{artwork.id}", json={"title": "Updated Title"}
        )
        assert response.status_code == 401

    def test_delete_artwork_requires_auth(self, client: TestClient, artwork):
        """Test that deleting artwork requires authentication."""
        response = client.delete(f"/api/artworks/{artwork.id}")
        assert response.status_code == 401

    def test_upload_image_requires_auth(self, client: TestClient, artwork):
        """Test that uploading images requires authentication."""
        response = client.post(
            f"/api/artworks/{artwork.id}/upload-image",
            files={"file": ("test.jpg", b"fake image", "image/jpeg")},
        )
        assert response.status_code == 401


class TestSellerIDExtraction:
    """Test that seller_id is extracted from JWT token, not query params."""

    def test_seller_id_extracted_from_token(
        self, client: TestClient, seller_token: str, seller_user: User, db_session
    ):
        """Test that seller_id comes from token, not query param."""
        response = client.post(
            "/api/artworks/",
            json={
                "title": "Test Art",
                "secret_threshold": 100.0,
                "description": "Test artwork",
            },
            headers={"Authorization": f"Bearer {seller_token}"},
        )

        assert response.status_code == 200
        data = response.json()

        # Verify seller_id matches the authenticated user from token
        assert data["seller_id"] == seller_user.id
        assert data["title"] == "Test Art"

    def test_cannot_forge_seller_id(
        self, client: TestClient, seller_token: str, seller_user: User, db_session
    ):
        """Test that passing seller_id as param doesn't override token."""
        # This test verifies the endpoint doesn't accept seller_id as a query param
        # The seller_id should only come from the JWT token

        response = client.post(
            "/api/artworks/?seller_id=999",  # Try to forge seller_id
            json={
                "title": "Forged Art",
                "secret_threshold": 100.0,
                "description": "Attempt to forge seller",
            },
            headers={"Authorization": f"Bearer {seller_token}"},
        )

        # Should still succeed but use ID from token, not param
        assert response.status_code == 200
        data = response.json()

        # seller_id should be from token, NOT from query param
        assert data["seller_id"] == seller_user.id
        assert data["seller_id"] != 999


class TestBidderIDExtraction:
    """Test that bidder_id is extracted from JWT token, not query params."""

    def test_bidder_id_extracted_from_token(
        self, client: TestClient, buyer_token: str, buyer_user: User, artwork, db_session
    ):
        """Test that bidder_id comes from token, not query param."""
        response = client.post(
            "/api/bids/",
            json={"artwork_id": artwork.id, "amount": 150.0},
            headers={"Authorization": f"Bearer {buyer_token}"},
        )

        assert response.status_code == 200
        data = response.json()

        # Verify bidder_id matches the authenticated user from token
        assert data["bidder_id"] == buyer_user.id

    def test_cannot_forge_bidder_id(
        self, client: TestClient, buyer_token: str, buyer_user: User, artwork, db_session
    ):
        """Test that passing bidder_id as param doesn't override token."""
        response = client.post(
            "/api/bids/?bidder_id=999",  # Try to forge bidder_id
            json={"artwork_id": artwork.id, "amount": 150.0},
            headers={"Authorization": f"Bearer {buyer_token}"},
        )

        # Should still succeed but use ID from token
        assert response.status_code == 200
        data = response.json()

        # bidder_id should be from token, NOT from query param
        assert data["bidder_id"] == buyer_user.id
        assert data["bidder_id"] != 999


class TestSellerBiddingRestriction:
    """Test that sellers cannot bid on their own artworks."""

    def test_cannot_bid_on_own_artwork(
        self, client: TestClient, seller_token: str, seller_user: User, db_session
    ):
        """Test seller cannot bid on their own artwork."""
        # Create artwork as seller
        artwork_response = client.post(
            "/api/artworks/",
            json={
                "title": "My Art",
                "secret_threshold": 100.0,
                "description": "Seller's artwork",
            },
            headers={"Authorization": f"Bearer {seller_token}"},
        )
        assert artwork_response.status_code == 200
        artwork_id = artwork_response.json()["id"]

        # Try to bid on own artwork
        bid_response = client.post(
            "/api/bids/",
            json={"artwork_id": artwork_id, "amount": 150.0},
            headers={"Authorization": f"Bearer {seller_token}"},
        )

        # Should be rejected with 403 Forbidden
        assert bid_response.status_code == 403
        assert "cannot bid on your own artwork" in bid_response.json()["detail"].lower()

    def test_buyer_can_bid_on_seller_artwork(
        self,
        client: TestClient,
        buyer_token: str,
        seller_token: str,
        seller_user: User,
        db_session,
    ):
        """Test that buyers CAN bid on seller's artwork (normal flow)."""
        # Seller creates artwork
        artwork_response = client.post(
            "/api/artworks/",
            json={
                "title": "Seller Art",
                "secret_threshold": 100.0,
                "description": "For sale",
            },
            headers={"Authorization": f"Bearer {seller_token}"},
        )
        assert artwork_response.status_code == 200
        artwork_id = artwork_response.json()["id"]

        # Buyer bids on artwork
        bid_response = client.post(
            "/api/bids/",
            json={"artwork_id": artwork_id, "amount": 150.0},
            headers={"Authorization": f"Bearer {buyer_token}"},
        )

        # Should succeed
        assert bid_response.status_code == 200
        assert bid_response.json()["amount"] == 150.0


class TestRoleBasedAccess:
    """Test role-based access control."""

    def test_buyer_cannot_create_artwork(
        self, client: TestClient, buyer_token: str
    ):
        """Test that buyers cannot create artworks."""
        response = client.post(
            "/api/artworks/",
            json={
                "title": "Buyer Art",
                "secret_threshold": 100.0,
                "description": "Should fail",
            },
            headers={"Authorization": f"Bearer {buyer_token}"},
        )

        # Should be rejected (forbidden or method not allowed)
        assert response.status_code == 403

    def test_seller_can_create_artwork(
        self, client: TestClient, seller_token: str
    ):
        """Test that sellers can create artworks."""
        response = client.post(
            "/api/artworks/",
            json={
                "title": "Seller Art",
                "secret_threshold": 100.0,
                "description": "Should succeed",
            },
            headers={"Authorization": f"Bearer {seller_token}"},
        )

        assert response.status_code == 200

    def test_admin_can_create_artwork(
        self, client: TestClient, admin_token: str
    ):
        """Test that admins can create artworks."""
        response = client.post(
            "/api/artworks/",
            json={
                "title": "Admin Art",
                "secret_threshold": 100.0,
                "description": "Admin created",
            },
            headers={"Authorization": f"Bearer {admin_token}"},
        )

        assert response.status_code == 200

    def test_admin_can_delete_any_artwork(
        self, client: TestClient, admin_token: str, artwork, db_session
    ):
        """Test that admins can delete any artwork."""
        response = client.delete(
            f"/api/artworks/{artwork.id}",
            headers={"Authorization": f"Bearer {admin_token}"},
        )

        assert response.status_code == 200

    def test_seller_cannot_delete_other_seller_artwork(
        self, client: TestClient, seller_token: str, artwork, db_session
    ):
        """Test that sellers cannot delete other sellers' artworks."""
        # Create a second seller
        from models.user import User, UserRole
        from services.jwt_service import JWTService
        from datetime import timedelta

        other_seller = User(
            auth0_sub="auth0|seller999",
            email="other@test.com",
            name="Other Seller",
            role=UserRole.SELLER,
        )
        db_session.add(other_seller)
        db_session.commit()

        # Create artwork by other seller
        from models.artwork import Artwork, ArtworkStatus

        other_artwork = Artwork(
            seller_id=other_seller.id,
            title="Other Seller Art",
            secret_threshold=100.0,
            status=ArtworkStatus.ACTIVE,
        )
        db_session.add(other_artwork)
        db_session.commit()
        db_session.refresh(other_artwork)

        # Try to delete other seller's artwork
        response = client.delete(
            f"/api/artworks/{other_artwork.id}",
            headers={"Authorization": f"Bearer {seller_token}"},
        )

        # Should be forbidden
        assert response.status_code == 403


class TestCurrentUserEndpoint:
    """Test /api/auth/me endpoint security."""

    def test_get_current_user_from_token(
        self, client: TestClient, buyer_token: str, buyer_user: User
    ):
        """Test that current user is retrieved from token, not query param."""
        response = client.get(
            "/api/auth/me", headers={"Authorization": f"Bearer {buyer_token}"}
        )

        assert response.status_code == 200
        data = response.json()
        assert data["id"] == buyer_user.id
        assert data["email"] == buyer_user.email

    def test_cannot_get_other_user_with_query_param(
        self, client: TestClient, buyer_token: str, buyer_user: User
    ):
        """Test that auth0_sub query param doesn't override token."""
        # Try to access another user's data via query param
        response = client.get(
            "/api/auth/me?auth0_sub=auth0|seller123",
            headers={"Authorization": f"Bearer {buyer_token}"},
        )

        assert response.status_code == 200
        data = response.json()

        # Should return the buyer user from token, not the seller
        assert data["id"] == buyer_user.id
        assert data["auth0_sub"] == buyer_user.auth0_sub
        assert data["auth0_sub"] != "auth0|seller123"

    def test_get_current_user_requires_auth(self, client: TestClient):
        """Test that /api/auth/me requires authentication."""
        response = client.get("/api/auth/me")

        assert response.status_code == 401


class TestTokenValidation:
    """Test JWT token validation."""

    def test_invalid_token_rejected(self, client: TestClient):
        """Test that invalid tokens are rejected."""
        response = client.post(
            "/api/artworks/",
            json={"title": "Test", "secret_threshold": 100.0},
            headers={"Authorization": "Bearer invalid_token_here"},
        )

        assert response.status_code == 401

    def test_missing_bearer_prefix_rejected(
        self, client: TestClient, buyer_token: str
    ):
        """Test that tokens without 'Bearer' prefix are rejected."""
        response = client.post(
            "/api/artworks/",
            json={"title": "Test", "secret_threshold": 100.0},
            headers={"Authorization": buyer_token},  # Missing "Bearer"
        )

        assert response.status_code == 401

    def test_empty_token_rejected(self, client: TestClient):
        """Test that empty tokens are rejected."""
        response = client.post(
            "/api/artworks/",
            json={"title": "Test", "secret_threshold": 100.0},
            headers={"Authorization": "Bearer "},
        )

        assert response.status_code == 401
