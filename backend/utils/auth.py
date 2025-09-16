from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from typing import Optional
from database import get_db
from services.auth_service import AuthService
from services.jwt_service import JWTService
from models.user import User, UserRole

security = HTTPBearer()

async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
) -> User:
    """Get current authenticated user"""
    token = credentials.credentials

    # Try Auth0 token first
    auth_user = await AuthService.verify_auth0_token(token)
    if auth_user:
        user = AuthService.get_or_create_user(db, auth_user)
        return user

    # Fallback to JWT token
    payload = JWTService.verify_token(token)
    if payload:
        auth0_sub = payload.get("sub")
        if auth0_sub:
            user = AuthService.get_user_by_auth0_sub(db, auth0_sub)
            if user:
                return user

    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid authentication credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

async def get_current_active_user(
    current_user: User = Depends(get_current_user)
) -> User:
    """Get current active user"""
    return current_user

def require_role(*allowed_roles: UserRole):
    """Decorator to require specific roles"""
    def role_checker(current_user: User = Depends(get_current_active_user)) -> User:
        if current_user.role not in allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient permissions"
            )
        return current_user
    return role_checker

# Role-specific dependencies
require_admin = require_role(UserRole.ADMIN)
require_seller = require_role(UserRole.SELLER, UserRole.ADMIN)
require_buyer = require_role(UserRole.BUYER, UserRole.SELLER, UserRole.ADMIN)