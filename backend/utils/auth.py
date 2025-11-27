from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from database import get_db
from models.user import User
from services.auth_service import AuthService
from services.jwt_service import JWTService

security = HTTPBearer(auto_error=False)


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db),
) -> User:
    """Get current authenticated user from Auth0 token.

    User data (email, name, role) is extracted from the Auth0 JWT token
    and attached to the user object at runtime.
    """
    if not credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

    token = credentials.credentials
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid authentication credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    # Try Auth0 token verification first
    try:
        auth_user = AuthService.verify_auth0_token(token)
        if auth_user:
            user = AuthService.get_or_create_user(db, auth_user)
            return user
    except (ValueError, Exception):
        # Auth0 verification failed, try JWT token
        pass

    # Fallback to JWT token (for API-only access or testing)
    try:
        payload = JWTService.verify_token(token)
        if payload:
            user_sub = payload.get("sub")

            # Get user from database
            user = None
            try:
                # Try as integer ID first (backward compatibility)
                user_id = int(user_sub)
                user = db.query(User).filter(User.id == user_id).first()
            except (ValueError, TypeError):
                # Try as auth0_sub
                user = db.query(User).filter(User.auth0_sub == user_sub).first()

            if user:
                # Attach data from JWT payload (not in DB)
                user.email = payload.get("email", "")
                user.name = payload.get("name", "")
                user.role = payload.get("role", "BUYER")
                return user

    except Exception:
        # JWT verification failed
        pass

    raise credentials_exception


async def get_current_active_user(
    current_user: User = Depends(get_current_user),
) -> User:
    """Get current active user"""
    return current_user


def require_role(*allowed_roles: str):
    """Decorator to require specific roles.

    Args:
        allowed_roles: Role strings like "ADMIN", "SELLER", "BUYER"
    """

    def role_checker(current_user: User = Depends(get_current_active_user)) -> User:
        if not hasattr(current_user, "role") or current_user.role not in allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN, detail="Insufficient permissions"
            )
        return current_user

    return role_checker


# Role-specific dependencies
require_admin = require_role("ADMIN")
require_seller = require_role("SELLER", "ADMIN")
require_buyer = require_role("BUYER", "SELLER", "ADMIN")
