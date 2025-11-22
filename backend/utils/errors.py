"""
Custom error classes for consistent error handling across the API.

These custom exceptions provide more descriptive error messages and
consistent status codes for common error scenarios.
"""

from fastapi import HTTPException, status


class ArtworkNotFoundError(HTTPException):
    """Raised when an artwork with the given ID is not found."""

    def __init__(self, artwork_id: int):
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Artwork with id {artwork_id} not found",
        )


class UserNotFoundError(HTTPException):
    """Raised when a user with the given ID is not found."""

    def __init__(self, user_id: int):
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with id {user_id} not found",
        )


class UnauthorizedError(HTTPException):
    """Raised when a user is not authorized to perform an action."""

    def __init__(self, message: str = "Not authorized to perform this action"):
        super().__init__(status_code=status.HTTP_403_FORBIDDEN, detail=message)


class ValidationError(HTTPException):
    """Raised when input validation fails."""

    def __init__(self, field: str, message: str):
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"field": field, "message": message},
        )


class InvalidBidError(HTTPException):
    """Raised when a bid is invalid (e.g., amount too low, artwork not active)."""

    def __init__(self, message: str):
        super().__init__(status_code=status.HTTP_400_BAD_REQUEST, detail=message)


class ArtworkNotActiveError(HTTPException):
    """Raised when attempting to bid on a non-active artwork."""

    def __init__(self, artwork_id: int, current_status: str):
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Artwork {artwork_id} is not active (status: {current_status})",
        )


class InvalidPaginationError(HTTPException):
    """Raised when pagination parameters are invalid."""

    def __init__(self, message: str):
        super().__init__(status_code=status.HTTP_400_BAD_REQUEST, detail=message)
