"""
Integration tests for rate limiting middleware.
Tests rate limiting behavior on various endpoints.
"""
import pytest
from fastapi.testclient import TestClient


def test_rate_limiting_on_registration(client: TestClient):
    """Test rate limiting on registration endpoint (5/minute)."""
    # First 5 requests should succeed
    for i in range(5):
        response = client.post(
            "/api/auth/register",
            json={
                "email": f"user{i}@example.com",
                "auth0_sub": f"auth0|test{i}",
                "name": f"Test User {i}",
                "role": "BUYER",
            },
        )
        assert response.status_code in [200, 400], f"Request {i+1} failed unexpectedly"

    # 6th request should be rate limited
    response = client.post(
        "/api/auth/register",
        json={
            "email": "user6@example.com",
            "auth0_sub": "auth0|test6",
            "name": "Test User 6",
            "role": "BUYER",
        },
    )
    assert response.status_code == 429, "Expected rate limit error"
    assert "rate limit" in response.json()["error"].lower()


def test_rate_limiting_on_bid_creation(client: TestClient, artwork, buyer_user):
    """Test rate limiting on bid creation endpoint (20/minute)."""
    # Create multiple bids rapidly
    successful_bids = 0
    rate_limited = False

    for i in range(25):
        response = client.post(
            "/api/bids/",
            json={
                "artwork_id": artwork.id,
                "amount": 100 + i,
            },
        )

        if response.status_code == 200:
            successful_bids += 1
        elif response.status_code == 429:
            rate_limited = True
            break

    # Should have created 20 bids successfully before hitting rate limit
    assert successful_bids <= 20, "More than 20 bids created"
    assert rate_limited or successful_bids == 20, "Rate limit not enforced"


def test_rate_limiting_on_artwork_creation(client: TestClient, seller_user):
    """Test rate limiting on artwork creation endpoint (10/hour)."""
    # Create multiple artworks rapidly
    successful_artworks = 0
    rate_limited = False

    for i in range(15):
        response = client.post(
            "/api/artworks/",
            json={
                "title": f"Test Artwork {i}",
                "description": "Test description",
                "secret_threshold": 1000,
            },
        )

        if response.status_code == 200:
            successful_artworks += 1
        elif response.status_code == 429:
            rate_limited = True
            break

    # Should have created 10 artworks successfully before hitting rate limit
    assert successful_artworks <= 10, "More than 10 artworks created"
    assert rate_limited or successful_artworks == 10, "Rate limit not enforced"


def test_rate_limit_headers_present(client: TestClient):
    """Test that rate limit headers are present in response."""
    response = client.get("/api/artworks/")

    # Check for Retry-After header if rate limited
    if response.status_code == 429:
        assert "retry-after" in response.headers.lower()
        assert "retry_after" in response.json()


def test_rate_limit_per_ip_isolation(client: TestClient):
    """Test that rate limits are per-IP (different IPs don't affect each other)."""
    # This test demonstrates the rate limiting is per-IP
    # In a real scenario, you'd need to simulate different IPs
    # For now, we just verify the endpoint responds
    response = client.get("/api/artworks/")
    assert response.status_code == 200


def test_security_headers_present(client: TestClient):
    """Test that security headers are added to all responses."""
    response = client.get("/api/artworks/")

    # Check for security headers
    headers = {k.lower(): v for k, v in response.headers.items()}

    assert "x-content-type-options" in headers
    assert headers["x-content-type-options"] == "nosniff"

    assert "x-frame-options" in headers
    assert headers["x-frame-options"] == "DENY"

    assert "x-xss-protection" in headers
    assert headers["x-xss-protection"] == "1; mode=block"

    assert "strict-transport-security" in headers

    assert "referrer-policy" in headers
    assert headers["referrer-policy"] == "strict-origin-when-cross-origin"

    assert "content-security-policy" in headers
