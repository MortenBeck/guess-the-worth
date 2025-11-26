from fastapi import APIRouter, Depends

from models import User
from schemas import UserResponse
from utils.auth import get_current_user

router = APIRouter()


@router.get("/me", response_model=UserResponse)
async def get_current_user_endpoint(current_user: User = Depends(get_current_user)):
    """
    Get the current authenticated user from Auth0 JWT token.

    User data (email, name, role) is extracted from the Auth0 token
    and attached to the user object at runtime.

    SECURITY: User identity is verified through Auth0 token validation.
    """
    return current_user
