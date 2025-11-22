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
    """
    # Validate pagination parameters
    if skip < 0:
        raise HTTPException(
            status_code=400,
            detail="Skip parameter must be non-negative"
        )

    if limit < 1:
        raise HTTPException(
            status_code=400,
            detail="Limit parameter must be at least 1"
        )

    # Enforce maximum limit to prevent resource exhaustion
    if limit > 100:
        raise HTTPException(
            status_code=400,
            detail="Limit cannot exceed 100"
        )

    # If credentials provided, validate them
    if credentials:
        # This will raise HTTPException if token is invalid
        await get_current_user(credentials, db)

    users = db.query(User).offset(skip).limit(limit).all()
    return users


@router.get("/{user_id}", response_model=UserResponse)
async def get_user(user_id: int, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


@router.put("/me", response_model=UserResponse)
async def update_current_user(
    user_update: UserUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Update current user's profile.

    SECURITY: Can only update own profile, not other users.
    """
    # Update only provided fields
    for field, value in user_update.dict(exclude_unset=True).items():
        setattr(current_user, field, value)

    db.commit()
    db.refresh(current_user)
    return current_user
