"""
Unit tests for custom error classes.
Tests that each custom exception returns the correct status code and error message.
"""

import pytest
from fastapi import status

from utils.errors import (
    ArtworkNotActiveError,
    ArtworkNotFoundError,
    InvalidBidError,
    InvalidPaginationError,
    UnauthorizedError,
    UserNotFoundError,
    ValidationError,
)


class TestArtworkNotFoundError:
    """Test ArtworkNotFoundError exception."""

    def test_artwork_not_found_error_message(self):
        """Test error message includes artwork ID."""
        error = ArtworkNotFoundError(artwork_id=123)
        assert error.status_code == status.HTTP_404_NOT_FOUND
        assert "123" in error.detail
        assert "not found" in error.detail.lower()

    def test_artwork_not_found_error_status_code(self):
        """Test error has 404 status code."""
        error = ArtworkNotFoundError(artwork_id=1)
        assert error.status_code == 404


class TestUserNotFoundError:
    """Test UserNotFoundError exception."""

    def test_user_not_found_error_message(self):
        """Test error message includes user ID."""
        error = UserNotFoundError(user_id=456)
        assert error.status_code == status.HTTP_404_NOT_FOUND
        assert "456" in error.detail
        assert "not found" in error.detail.lower()

    def test_user_not_found_error_status_code(self):
        """Test error has 404 status code."""
        error = UserNotFoundError(user_id=1)
        assert error.status_code == 404


class TestUnauthorizedError:
    """Test UnauthorizedError exception."""

    def test_unauthorized_error_default_message(self):
        """Test default error message."""
        error = UnauthorizedError()
        assert error.status_code == status.HTTP_403_FORBIDDEN
        assert "not authorized" in error.detail.lower()

    def test_unauthorized_error_custom_message(self):
        """Test custom error message."""
        custom_msg = "You cannot access this resource"
        error = UnauthorizedError(message=custom_msg)
        assert error.status_code == status.HTTP_403_FORBIDDEN
        assert error.detail == custom_msg

    def test_unauthorized_error_status_code(self):
        """Test error has 403 status code."""
        error = UnauthorizedError()
        assert error.status_code == 403


class TestValidationError:
    """Test ValidationError exception."""

    def test_validation_error_with_field_and_message(self):
        """Test error includes field name and message."""
        error = ValidationError(field="email", message="Invalid email format")
        assert error.status_code == status.HTTP_400_BAD_REQUEST
        assert error.detail["field"] == "email"
        assert error.detail["message"] == "Invalid email format"

    def test_validation_error_status_code(self):
        """Test error has 400 status code."""
        error = ValidationError(field="amount", message="Must be positive")
        assert error.status_code == 400

    def test_validation_error_detail_structure(self):
        """Test error detail is a dict with field and message."""
        error = ValidationError(field="test_field", message="test message")
        assert isinstance(error.detail, dict)
        assert "field" in error.detail
        assert "message" in error.detail


class TestInvalidBidError:
    """Test InvalidBidError exception."""

    def test_invalid_bid_error_message(self):
        """Test error message is preserved."""
        msg = "Bid amount must be higher than current bid"
        error = InvalidBidError(message=msg)
        assert error.status_code == status.HTTP_400_BAD_REQUEST
        assert error.detail == msg

    def test_invalid_bid_error_status_code(self):
        """Test error has 400 status code."""
        error = InvalidBidError(message="Invalid bid")
        assert error.status_code == 400

    def test_invalid_bid_error_different_messages(self):
        """Test error handles different message types."""
        error1 = InvalidBidError(message="Artwork is not active")
        error2 = InvalidBidError(message="Bid too low")
        assert error1.detail == "Artwork is not active"
        assert error2.detail == "Bid too low"


class TestArtworkNotActiveError:
    """Test ArtworkNotActiveError exception."""

    def test_artwork_not_active_error_message(self):
        """Test error message includes artwork ID and status."""
        error = ArtworkNotActiveError(artwork_id=789, current_status="SOLD")
        assert error.status_code == status.HTTP_400_BAD_REQUEST
        assert "789" in error.detail
        assert "SOLD" in error.detail
        assert "not active" in error.detail.lower()

    def test_artwork_not_active_error_status_code(self):
        """Test error has 400 status code."""
        error = ArtworkNotActiveError(artwork_id=1, current_status="ARCHIVED")
        assert error.status_code == 400

    def test_artwork_not_active_error_different_statuses(self):
        """Test error works with different artwork statuses."""
        error1 = ArtworkNotActiveError(artwork_id=1, current_status="SOLD")
        error2 = ArtworkNotActiveError(artwork_id=2, current_status="ARCHIVED")
        error3 = ArtworkNotActiveError(artwork_id=3, current_status="PENDING")

        assert "SOLD" in error1.detail
        assert "ARCHIVED" in error2.detail
        assert "PENDING" in error3.detail


class TestInvalidPaginationError:
    """Test InvalidPaginationError exception."""

    def test_invalid_pagination_error_message(self):
        """Test error message is preserved."""
        msg = "Page number must be positive"
        error = InvalidPaginationError(message=msg)
        assert error.status_code == status.HTTP_400_BAD_REQUEST
        assert error.detail == msg

    def test_invalid_pagination_error_status_code(self):
        """Test error has 400 status code."""
        error = InvalidPaginationError(message="Invalid pagination")
        assert error.status_code == 400

    def test_invalid_pagination_error_different_messages(self):
        """Test error handles different pagination messages."""
        error1 = InvalidPaginationError(message="Skip must be non-negative")
        error2 = InvalidPaginationError(message="Limit exceeds maximum")
        assert error1.detail == "Skip must be non-negative"
        assert error2.detail == "Limit exceeds maximum"


class TestErrorInheritance:
    """Test that all custom errors inherit from HTTPException."""

    def test_all_errors_are_http_exceptions(self):
        """Test all custom errors can be raised as HTTPException."""
        from fastapi import HTTPException

        errors = [
            ArtworkNotFoundError(artwork_id=1),
            UserNotFoundError(user_id=1),
            UnauthorizedError(),
            ValidationError(field="test", message="test"),
            InvalidBidError(message="test"),
            ArtworkNotActiveError(artwork_id=1, current_status="SOLD"),
            InvalidPaginationError(message="test"),
        ]

        for error in errors:
            assert isinstance(error, HTTPException)
            assert hasattr(error, "status_code")
            assert hasattr(error, "detail")
