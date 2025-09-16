from pydantic import BaseModel
from typing import Optional, List

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_in: int

class AuthUser(BaseModel):
    sub: str
    email: str
    name: str
    picture: Optional[str] = None
    email_verified: bool = False
    roles: List[str] = []