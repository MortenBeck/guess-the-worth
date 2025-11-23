from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from database import get_db
from models import User
from schemas import UserCreate, UserResponse
from utils.auth import get_current_user
from middleware.rate_limit import limiter

router = APIRouter()


@router.post("/register", response_model=UserResponse)
@limiter.limit("5/minute")  # Only 5 registrations per minute per IP
async def register_user(request: Request, user: UserCreate, db: Session = Depends(get_db)):
    # Check for duplicate auth0_sub
    db_user = db.query(User).filter(User.auth0_sub == user.auth0_sub).first()
    if db_user:
        raise HTTPException(status_code=400, detail="User already registered")

    # Check for duplicate email
    db_user = db.query(User).filter(User.email == user.email).first()
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")

    try:
        db_user = User(**user.dict())
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
        return db_user
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=400, detail="User registration failed due to constraint violation"
        )


@router.get("/me", response_model=UserResponse)
async def get_current_user_endpoint(current_user: User = Depends(get_current_user)):
    """
    Get the current authenticated user from JWT token.

    SECURITY: User ID is extracted from the Bearer token, not from query parameters.
    This prevents user impersonation attacks.
    """
    return current_user
