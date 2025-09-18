import httpx
from typing import Optional, Dict, Any, List
from sqlalchemy.orm import Session
from models.user import User, UserRole
from schemas.auth import AuthUser
from config.settings import settings

class AuthService:
    @staticmethod
    async def verify_auth0_token(token: str) -> Optional[AuthUser]:
        """Verify Auth0 token and return user info with roles"""
        try:
            userinfo_url = f"https://{settings.auth0_domain}/userinfo"

            async with httpx.AsyncClient() as client:
                headers = {"Authorization": f"Bearer {token}"}
                response = await client.get(userinfo_url, headers=headers)

                if response.status_code == 200:
                    user_data = response.json()
                    auth0_roles = user_data.get(f"https://api.guesstheworth.com/roles", [])

                    return AuthUser(
                        sub=user_data.get("sub"),
                        email=user_data.get("email"),
                        name=user_data.get("name"),
                        picture=user_data.get("picture"),
                        email_verified=user_data.get("email_verified", False),
                        roles=auth0_roles
                    )
                return None
        except Exception:
            return None

    @staticmethod
    def map_auth0_role_to_user_role(auth0_roles: List[str]) -> UserRole:
        """Map Auth0 roles to our UserRole enum"""
        if not auth0_roles:
            return UserRole.BUYER

        if "admin" in auth0_roles:
            return UserRole.ADMIN
        elif "seller" in auth0_roles:
            return UserRole.SELLER
        else:
            return UserRole.BUYER

    @staticmethod
    def get_or_create_user(db: Session, auth_user: AuthUser) -> User:
        """Get existing user or create new one from Auth0 data with role assignment"""
        user = db.query(User).filter(User.auth0_sub == auth_user.sub).first()
        user_role = AuthService.map_auth0_role_to_user_role(auth_user.roles)

        if not user:
            user = User(
                auth0_sub=auth_user.sub,
                email=auth_user.email,
                name=auth_user.name,
                role=user_role
            )
            db.add(user)
            db.commit()
            db.refresh(user)
        else:
            if user.role != user_role:
                user.role = user_role
                db.commit()
                db.refresh(user)

        return user

    @staticmethod
    def get_user_by_auth0_sub(db: Session, auth0_sub: str) -> Optional[User]:
        """Get user by Auth0 subject ID"""
        return db.query(User).filter(User.auth0_sub == auth0_sub).first()