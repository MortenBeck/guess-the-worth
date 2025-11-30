from typing import Optional

import requests
from sqlalchemy.orm import Session

from config.settings import settings
from models.user import User
from schemas.auth import AuthUser


class AuthService:
    @staticmethod
    def verify_auth0_token(token: str) -> Optional[AuthUser]:
        """Verify Auth0 token and return user info with roles"""
        try:
            userinfo_url = f"https://{settings.auth0_domain}/userinfo"
            headers = {"Authorization": f"Bearer {token}"}
            response = requests.get(userinfo_url, headers=headers, timeout=10)

            if response.status_code == 200:
                user_data = response.json()
                # Updated to use the correct namespace
                auth0_roles = user_data.get("https://guesstheworth.demo/roles", [])

                return AuthUser(
                    sub=user_data.get("sub"),
                    email=user_data.get("email"),
                    name=user_data.get("name"),
                    picture=user_data.get("picture"),
                    email_verified=user_data.get("email_verified", False),
                    roles=auth0_roles,
                )
            else:
                raise ValueError("Invalid Auth0 token")
        except requests.RequestException as e:
            raise ValueError(f"Auth0 verification failed: {str(e)}")

    @staticmethod
    def get_or_create_user(db: Session, auth_user: AuthUser) -> User:
        """Get existing user or create new one from Auth0 data.

        User data (email, name, role) is attached to the user object at runtime
        from Auth0 data, not stored in the database.
        """
        user = db.query(User).filter(User.auth0_sub == auth_user.sub).first()

        if not user:
            # Create minimal user record
            user = User(auth0_sub=auth_user.sub)
            db.add(user)
            db.commit()
            db.refresh(user)

        # Attach Auth0 data to user object (not stored in DB)
        user.email = auth_user.email or ""
        user.name = auth_user.name or ""

        # Extract role from Auth0 roles
        user.role = AuthService.extract_primary_role(auth_user.roles)

        return user

    @staticmethod
    def extract_primary_role(auth0_roles: list[str]) -> str:
        """Extract primary role from Auth0 roles list.

        Returns the highest priority role: ADMIN > SELLER > BUYER
        """
        if not auth0_roles:
            return "BUYER"

        # Convert to uppercase for comparison
        roles_upper = [role.upper() for role in auth0_roles]

        if "ADMIN" in roles_upper:
            return "ADMIN"
        elif "SELLER" in roles_upper:
            return "SELLER"
        else:
            return "BUYER"

    @staticmethod
    def map_auth0_role_to_user_role(auth0_roles: list[str]) -> str:
        """Map Auth0 roles to user role (alias for extract_primary_role).

        Returns the highest priority role: ADMIN > SELLER > BUYER
        """
        return AuthService.extract_primary_role(auth0_roles)

    @staticmethod
    def get_user_by_auth0_sub(db: Session, auth0_sub: str) -> Optional[User]:
        """Get user by Auth0 subject ID"""
        return db.query(User).filter(User.auth0_sub == auth0_sub).first()
