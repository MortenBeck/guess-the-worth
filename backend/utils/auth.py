import bcrypt
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from database import get_db
from models.user import User, UserRole
from services.auth_service import AuthService
from services.jwt_service import JWTService

security = HTTPBearer(auto_error=False)


def hash_password(password: str) -> str:
    """Hash a password using bcrypt."""
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password.encode("utf-8"), salt)
    return hashed.decode("utf-8")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against a bcrypt hash."""
    return bcrypt.checkpw(plain_password.encode("utf-8"), hashed_password.encode("utf-8"))


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security), db: Session = Depends(get_db)
) -> User:
    """Get current authenticated user"""
    if not credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

    token = credentials.credentials

    # Try Auth0 token first
    try:
        auth_user = AuthService.verify_auth0_token(token)
        if auth_user:
            user = AuthService.get_or_create_user(db, auth_user)
            return user
    except (ValueError, Exception):
        # Auth0 verification failed, try JWT token
        pass

    # Fallback to JWT token
    try:
        payload = JWTService.verify_token(token)
        if payload:
            user_sub = payload.get("sub")
            if user_sub:
                # TEMPORARY: Handle hardcoded admin (ID 999999)
                if user_sub == "999999":
                    # Create a temporary User object for hardcoded admin
                    temp_admin = User(
                        id=999999,
                        email=payload.get("email", "superadmin@temp.local"),
                        name="Temporary Super Admin",
                        role=UserRole.ADMIN,
                        auth0_sub="temp|hardcoded-admin",
                    )
                    return temp_admin

                # Try to parse as integer user ID first (for password-based auth)
                try:
                    user_id = int(user_sub)
                    user = db.query(User).filter(User.id == user_id).first()
                    if user:
                        return user
                except (ValueError, TypeError):
                    # Not an integer, try as auth0_sub
                    user = AuthService.get_user_by_auth0_sub(db, user_sub)
                    if user:
                        return user
    except Exception:
        # JWT verification failed
        pass

    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid authentication credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )


async def get_current_active_user(current_user: User = Depends(get_current_user)) -> User:
    """Get current active user"""
    return current_user


def require_role(*allowed_roles: UserRole):
    """Decorator to require specific roles"""

    def role_checker(current_user: User = Depends(get_current_active_user)) -> User:
        if current_user.role not in allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN, detail="Insufficient permissions"
            )
        return current_user

    return role_checker


# Role-specific dependencies
require_admin = require_role(UserRole.ADMIN)
require_seller = require_role(UserRole.SELLER, UserRole.ADMIN)
require_buyer = require_role(UserRole.BUYER, UserRole.SELLER, UserRole.ADMIN)
