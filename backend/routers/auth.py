from fastapi import APIRouter, Depends, HTTPException, Request
from pydantic import BaseModel
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from database import get_db
from middleware.rate_limit import limiter
from models import User
from schemas import UserCreate, UserResponse
from services.jwt_service import JWTService
from utils.auth import get_current_user, verify_password

router = APIRouter()


class LoginRequest(BaseModel):
    """Login request schema for email/password authentication."""

    email: str
    password: str


class LoginResponse(BaseModel):
    """Login response with JWT access token."""

    access_token: str
    token_type: str = "bearer"


@router.post("/login", response_model=LoginResponse)
@limiter.limit("10/minute")  # 10 login attempts per minute per IP
async def login(request: Request, login_data: LoginRequest, db: Session = Depends(get_db)):
    """
    Login with email and password.
    Returns a JWT access token for subsequent API calls.

    This endpoint is primarily for demo users and testing.
    Production users should use Auth0 OAuth2 flow.
    """
    # Find user by email
    user = db.query(User).filter(User.email == login_data.email).first()
    if not user:
        raise HTTPException(status_code=401, detail="Invalid email or password")

    # Verify password
    if not user.password_hash:
        raise HTTPException(
            status_code=401,
            detail="This account uses OAuth2. Please login through the authentication provider.",
        )

    if not verify_password(login_data.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Invalid email or password")

    # Generate JWT token
    access_token = JWTService.create_access_token(
        data={"sub": str(user.id), "email": user.email, "role": user.role}
    )

    return LoginResponse(access_token=access_token)


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
