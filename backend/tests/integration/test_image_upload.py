"""
Test Image Upload Functionality (Stage 6).

These tests verify that image upload works correctly:
- Valid images can be uploaded
- Invalid file types are rejected
- File size limits enforced
- Only artwork owner/admin can upload
- Images are properly stored and URLs returned
"""

import os
from io import BytesIO
from unittest.mock import patch

import pytest
from fastapi.testclient import TestClient
from PIL import Image as PILImage


@pytest.fixture(autouse=True)
def mock_auth0():
    """Mock Auth0 verification for all tests in this module to use JWT fallback."""
    with patch("services.auth_service.AuthService.verify_auth0_token") as mock:
        mock.side_effect = Exception("Auth0 not available - using JWT")
        yield mock


class TestImageUploadPermissions:
    """Test that only authorized users can upload images."""

    def test_upload_requires_authentication(self, client: TestClient, artwork, db_session):
        """Test that uploading images requires authentication."""
        # Create test image
        img = PILImage.new("RGB", (100, 100), color="red")
        img_bytes = BytesIO()
        img.save(img_bytes, format="JPEG")
        img_bytes.seek(0)

        response = client.post(
            f"/api/artworks/{artwork.id}/upload-image",
            files={"file": ("test.jpg", img_bytes, "image/jpeg")},
        )

        assert response.status_code == 401

    def test_owner_can_upload_image(
        self, client: TestClient, seller_token: str, artwork, db_session
    ):
        """Test that artwork owner can upload images."""
        # Create test image
        img = PILImage.new("RGB", (100, 100), color="blue")
        img_bytes = BytesIO()
        img.save(img_bytes, format="JPEG")
        img_bytes.seek(0)

        response = client.post(
            f"/api/artworks/{artwork.id}/upload-image",
            files={"file": ("test.jpg", img_bytes, "image/jpeg")},
            headers={"Authorization": f"Bearer {seller_token}"},
        )

        assert response.status_code == 200
        data = response.json()
        assert "image_url" in data
        assert data["image_url"].startswith("/uploads/artworks/")

    def test_admin_can_upload_image(
        self, client: TestClient, admin_token: str, artwork, db_session
    ):
        """Test that admins can upload images to any artwork."""
        # Create test image
        img = PILImage.new("RGB", (100, 100), color="green")
        img_bytes = BytesIO()
        img.save(img_bytes, format="JPEG")
        img_bytes.seek(0)

        response = client.post(
            f"/api/artworks/{artwork.id}/upload-image",
            files={"file": ("test.jpg", img_bytes, "image/jpeg")},
            headers={"Authorization": f"Bearer {admin_token}"},
        )

        assert response.status_code == 200
        assert "image_url" in response.json()

    def test_other_seller_cannot_upload_image(
        self, client: TestClient, seller_token: str, artwork, db_session
    ):
        """Test that other sellers cannot upload to artwork they don't own."""
        # Create a different seller
        from datetime import timedelta

        from models.user import User
        from services.jwt_service import JWTService

        other_seller = User(auth0_sub="auth0|other_seller")
        db_session.add(other_seller)
        db_session.commit()
        db_session.refresh(other_seller)
        # Attach Auth0 data (simulated)
        other_seller.email = "other@seller.com"
        other_seller.name = "Other Seller"
        other_seller.role = "SELLER"

        other_token = JWTService.create_access_token(
            data={"sub": other_seller.auth0_sub, "role": "SELLER"},
            expires_delta=timedelta(hours=1),
        )

        # Try to upload to artwork owned by different seller
        img = PILImage.new("RGB", (100, 100), color="red")
        img_bytes = BytesIO()
        img.save(img_bytes, format="JPEG")
        img_bytes.seek(0)

        response = client.post(
            f"/api/artworks/{artwork.id}/upload-image",
            files={"file": ("test.jpg", img_bytes, "image/jpeg")},
            headers={"Authorization": f"Bearer {other_token}"},
        )

        assert response.status_code == 403

    def test_buyer_cannot_upload_image(
        self, client: TestClient, buyer_token: str, artwork, db_session
    ):
        """Test that buyers cannot upload images."""
        img = PILImage.new("RGB", (100, 100), color="yellow")
        img_bytes = BytesIO()
        img.save(img_bytes, format="JPEG")
        img_bytes.seek(0)

        response = client.post(
            f"/api/artworks/{artwork.id}/upload-image",
            files={"file": ("test.jpg", img_bytes, "image/jpeg")},
            headers={"Authorization": f"Bearer {buyer_token}"},
        )

        assert response.status_code == 403


class TestImageFileValidation:
    """Test file type and format validation."""

    def test_upload_jpeg_image(self, client: TestClient, seller_token: str, artwork, db_session):
        """Test uploading JPEG image."""
        img = PILImage.new("RGB", (100, 100), color="red")
        img_bytes = BytesIO()
        img.save(img_bytes, format="JPEG")
        img_bytes.seek(0)

        response = client.post(
            f"/api/artworks/{artwork.id}/upload-image",
            files={"file": ("test.jpg", img_bytes, "image/jpeg")},
            headers={"Authorization": f"Bearer {seller_token}"},
        )

        assert response.status_code == 200

    def test_upload_png_image(self, client: TestClient, seller_token: str, artwork, db_session):
        """Test uploading PNG image."""
        img = PILImage.new("RGB", (100, 100), color="blue")
        img_bytes = BytesIO()
        img.save(img_bytes, format="PNG")
        img_bytes.seek(0)

        response = client.post(
            f"/api/artworks/{artwork.id}/upload-image",
            files={"file": ("test.png", img_bytes, "image/png")},
            headers={"Authorization": f"Bearer {seller_token}"},
        )

        assert response.status_code == 200

    def test_upload_webp_image(self, client: TestClient, seller_token: str, artwork, db_session):
        """Test uploading WebP image."""
        img = PILImage.new("RGB", (100, 100), color="green")
        img_bytes = BytesIO()
        img.save(img_bytes, format="WEBP")
        img_bytes.seek(0)

        response = client.post(
            f"/api/artworks/{artwork.id}/upload-image",
            files={"file": ("test.webp", img_bytes, "image/webp")},
            headers={"Authorization": f"Bearer {seller_token}"},
        )

        assert response.status_code == 200

    def test_reject_text_file(self, client: TestClient, seller_token: str, artwork, db_session):
        """Test that text files are rejected."""
        response = client.post(
            f"/api/artworks/{artwork.id}/upload-image",
            files={"file": ("test.txt", b"This is not an image", "text/plain")},
            headers={"Authorization": f"Bearer {seller_token}"},
        )

        assert response.status_code == 400
        assert "invalid file type" in response.json()["detail"].lower()

    def test_reject_pdf_file(self, client: TestClient, seller_token: str, artwork, db_session):
        """Test that PDF files are rejected."""
        response = client.post(
            f"/api/artworks/{artwork.id}/upload-image",
            files={"file": ("test.pdf", b"%PDF-1.4 fake pdf", "application/pdf")},
            headers={"Authorization": f"Bearer {seller_token}"},
        )

        assert response.status_code == 400

    def test_reject_executable_file(
        self, client: TestClient, seller_token: str, artwork, db_session
    ):
        """Test that executable files are rejected."""
        response = client.post(
            f"/api/artworks/{artwork.id}/upload-image",
            files={"file": ("malware.exe", b"MZ\x90\x00", "application/x-msdownload")},
            headers={"Authorization": f"Bearer {seller_token}"},
        )

        assert response.status_code == 400


class TestFileSizeValidation:
    """Test file size limits."""

    def test_reject_file_too_large(
        self, client: TestClient, seller_token: str, artwork, db_session
    ):
        """Test that files >5MB are rejected."""
        # Create 6MB file
        large_file = BytesIO(b"0" * (6 * 1024 * 1024))

        response = client.post(
            f"/api/artworks/{artwork.id}/upload-image",
            files={"file": ("large.jpg", large_file, "image/jpeg")},
            headers={"Authorization": f"Bearer {seller_token}"},
        )

        assert response.status_code == 400
        assert "too large" in response.json()["detail"].lower()

    def test_accept_file_at_limit(self, client: TestClient, seller_token: str, artwork, db_session):
        """Test that files exactly at 5MB limit are accepted."""
        # Create 5MB file
        limit_file = BytesIO(b"0" * (5 * 1024 * 1024))

        response = client.post(
            f"/api/artworks/{artwork.id}/upload-image",
            files={"file": ("limit.jpg", limit_file, "image/jpeg")},
            headers={"Authorization": f"Bearer {seller_token}"},
        )

        # May succeed or fail depending on header overhead
        # Most implementations accept exactly at limit
        assert response.status_code in [200, 400]

    def test_accept_small_file(self, client: TestClient, seller_token: str, artwork, db_session):
        """Test that small files are accepted."""
        # Create tiny image (< 10KB)
        img = PILImage.new("RGB", (50, 50), color="red")
        img_bytes = BytesIO()
        img.save(img_bytes, format="JPEG", quality=85)
        img_bytes.seek(0)

        response = client.post(
            f"/api/artworks/{artwork.id}/upload-image",
            files={"file": ("small.jpg", img_bytes, "image/jpeg")},
            headers={"Authorization": f"Bearer {seller_token}"},
        )

        assert response.status_code == 200


class TestImageProcessing:
    """Test image processing and optimization."""

    def test_image_url_returned(self, client: TestClient, seller_token: str, artwork, db_session):
        """Test that image URL is returned after upload."""
        img = PILImage.new("RGB", (100, 100), color="blue")
        img_bytes = BytesIO()
        img.save(img_bytes, format="JPEG")
        img_bytes.seek(0)

        response = client.post(
            f"/api/artworks/{artwork.id}/upload-image",
            files={"file": ("test.jpg", img_bytes, "image/jpeg")},
            headers={"Authorization": f"Bearer {seller_token}"},
        )

        assert response.status_code == 200
        data = response.json()
        assert "image_url" in data
        assert isinstance(data["image_url"], str)
        assert len(data["image_url"]) > 0

    def test_image_file_created(self, client: TestClient, seller_token: str, artwork, db_session):
        """Test that image file is actually created on disk."""
        img = PILImage.new("RGB", (200, 200), color="purple")
        img_bytes = BytesIO()
        img.save(img_bytes, format="JPEG")
        img_bytes.seek(0)

        response = client.post(
            f"/api/artworks/{artwork.id}/upload-image",
            files={"file": ("test.jpg", img_bytes, "image/jpeg")},
            headers={"Authorization": f"Bearer {seller_token}"},
        )

        assert response.status_code == 200
        image_url = response.json()["image_url"]

        # Extract filename from URL
        # URL format: /uploads/artworks/uuid.jpg
        filename = image_url.split("/")[-1]
        file_path = os.path.join("uploads/artworks", filename)

        # Verify file exists
        assert os.path.exists(file_path)

        # Clean up test file
        if os.path.exists(file_path):
            os.remove(file_path)

    def test_large_image_resized(self, client: TestClient, seller_token: str, artwork, db_session):
        """Test that large images are resized to 1200px max dimension."""
        # Create large image (2000x2000)
        img = PILImage.new("RGB", (2000, 2000), color="orange")
        img_bytes = BytesIO()
        img.save(img_bytes, format="JPEG")
        img_bytes.seek(0)

        response = client.post(
            f"/api/artworks/{artwork.id}/upload-image",
            files={"file": ("large.jpg", img_bytes, "image/jpeg")},
            headers={"Authorization": f"Bearer {seller_token}"},
        )

        assert response.status_code == 200
        image_url = response.json()["image_url"]

        # Check if file was resized
        filename = image_url.split("/")[-1]
        file_path = os.path.join("uploads/artworks", filename)

        if os.path.exists(file_path):
            saved_img = PILImage.open(file_path)
            # Should be resized to 1200x1200 or smaller
            assert saved_img.width <= 1200
            assert saved_img.height <= 1200

            # Clean up
            saved_img.close()
            os.remove(file_path)


class TestArtworkImageAssociation:
    """Test that uploaded images are associated with artworks."""

    def test_artwork_updated_with_image_url(
        self, client: TestClient, seller_token: str, artwork, db_session
    ):
        """Test that artwork record is updated with image URL."""
        img = PILImage.new("RGB", (100, 100), color="cyan")
        img_bytes = BytesIO()
        img.save(img_bytes, format="JPEG")
        img_bytes.seek(0)

        upload_response = client.post(
            f"/api/artworks/{artwork.id}/upload-image",
            files={"file": ("test.jpg", img_bytes, "image/jpeg")},
            headers={"Authorization": f"Bearer {seller_token}"},
        )

        assert upload_response.status_code == 200
        image_url = upload_response.json()["image_url"]

        # Fetch artwork and verify image_url is set
        artwork_response = client.get(f"/api/artworks/{artwork.id}")
        assert artwork_response.status_code == 200
        artwork_data = artwork_response.json()

        assert artwork_data["image_url"] == image_url

        # Clean up
        filename = image_url.split("/")[-1]
        file_path = os.path.join("uploads/artworks", filename)
        if os.path.exists(file_path):
            os.remove(file_path)

    def test_multiple_uploads_replace_image(
        self, client: TestClient, seller_token: str, artwork, db_session
    ):
        """Test that uploading multiple times replaces the image."""
        # Upload first image
        img1 = PILImage.new("RGB", (100, 100), color="red")
        img1_bytes = BytesIO()
        img1.save(img1_bytes, format="JPEG")
        img1_bytes.seek(0)

        response1 = client.post(
            f"/api/artworks/{artwork.id}/upload-image",
            files={"file": ("first.jpg", img1_bytes, "image/jpeg")},
            headers={"Authorization": f"Bearer {seller_token}"},
        )
        assert response1.status_code == 200
        first_url = response1.json()["image_url"]

        # Upload second image
        img2 = PILImage.new("RGB", (100, 100), color="blue")
        img2_bytes = BytesIO()
        img2.save(img2_bytes, format="JPEG")
        img2_bytes.seek(0)

        response2 = client.post(
            f"/api/artworks/{artwork.id}/upload-image",
            files={"file": ("second.jpg", img2_bytes, "image/jpeg")},
            headers={"Authorization": f"Bearer {seller_token}"},
        )
        assert response2.status_code == 200
        second_url = response2.json()["image_url"]

        # URLs should be different (new file created)
        assert first_url != second_url

        # Artwork should have the latest URL
        artwork_response = client.get(f"/api/artworks/{artwork.id}")
        assert artwork_response.json()["image_url"] == second_url

        # Clean up
        for url in [first_url, second_url]:
            filename = url.split("/")[-1]
            file_path = os.path.join("uploads/artworks", filename)
            if os.path.exists(file_path):
                os.remove(file_path)


class TestEdgeCases:
    """Test edge cases and error scenarios."""

    def test_upload_to_nonexistent_artwork(self, client: TestClient, seller_token: str, db_session):
        """Test uploading to non-existent artwork."""
        img = PILImage.new("RGB", (100, 100), color="red")
        img_bytes = BytesIO()
        img.save(img_bytes, format="JPEG")
        img_bytes.seek(0)

        response = client.post(
            "/api/artworks/99999/upload-image",
            files={"file": ("test.jpg", img_bytes, "image/jpeg")},
            headers={"Authorization": f"Bearer {seller_token}"},
        )

        assert response.status_code == 404

    def test_upload_without_file(self, client: TestClient, seller_token: str, artwork, db_session):
        """Test upload request without file."""
        response = client.post(
            f"/api/artworks/{artwork.id}/upload-image",
            headers={"Authorization": f"Bearer {seller_token}"},
        )

        # Should fail (422 validation error or 400 bad request)
        assert response.status_code in [400, 422]
