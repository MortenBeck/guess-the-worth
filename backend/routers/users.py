from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from database import get_db
from models import User
from schemas import UserResponse, UserUpdate
from utils.auth import get_current_user

router = APIRouter()
# Optional authentication - validates token if provided, but doesn't require it
security = HTTPBearer(auto_error=False)


@router.get("/", response_model=List[UserResponse])
async def get_users(
    skip: int = 0,
    limit: int = 20,
    db: Session = Depends(get_db),
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security),
):
    """
    Get list of users with pagination.

    Query parameters:
    - skip: Number of records to skip (default: 0)
    - limit: Maximum number of records to return (default: 20, max: 100)

    NOTE: This endpoint returns minimal user data. Full user profiles (email, name)
    are managed in Auth0 and not available through this endpoint.
    """
    # Validate pagination parameters
    if skip < 0:
        raise HTTPException(status_code=400, detail="Skip parameter must be non-negative")

    if limit < 1:
        raise HTTPException(status_code=400, detail="Limit parameter must be at least 1")

    # Enforce maximum limit to prevent resource exhaustion
    if limit > 100:
        raise HTTPException(status_code=400, detail="Limit cannot exceed 100")

    # If credentials provided, validate them
    if credentials:
        # This will raise HTTPException if token is invalid
        await get_current_user(credentials, db)

    users = db.query(User).offset(skip).limit(limit).all()

    # Attach default Auth0 data for response validation
    # (Real user data is in Auth0, not our database)
    for user in users:
        if not hasattr(user, "email"):
            user.email = f"user-{user.id}@auth0.placeholder"
        if not hasattr(user, "name"):
            user.name = f"User {user.id}"
        if not hasattr(user, "role"):
            user.role = "BUYER"

    return users


@router.get("/{user_id}", response_model=UserResponse)
async def get_user(user_id: int, db: Session = Depends(get_db)):
    """
    Get a single user by ID.

    NOTE: This endpoint returns minimal user data. Full user profiles (email, name)
    are managed in Auth0 and not available through this endpoint.
    """
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # Attach default Auth0 data for response validation
    # (Real user data is in Auth0, not our database)
    if not hasattr(user, "email"):
        user.email = f"user-{user.id}@auth0.placeholder"
    if not hasattr(user, "name"):
        user.name = f"User {user.id}"
    if not hasattr(user, "role"):
        user.role = "BUYER"

    return user


@router.put("/me", response_model=UserResponse)
async def update_current_user(
    user_update: UserUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Update current user's profile.

    NOTE: User profile data (email, name, role) is managed in Auth0.
    This endpoint exists for compatibility but cannot update any fields.
    To update user profile, use the Auth0 Management API or Auth0 Dashboard.

    SECURITY: Can only update own profile, not other users.
    """
    # User data is managed in Auth0, so there are no fields to update in our database
    # Just return the current user with Auth0 data attached
    return current_user
