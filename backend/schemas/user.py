from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, EmailStr

from models.user import UserRole


class UserBase(BaseModel):
    email: EmailStr
    name: str


class UserCreate(UserBase):
    auth0_sub: str
    role: UserRole = UserRole.BUYER


class UserUpdate(BaseModel):
    name: Optional[str] = None
    role: Optional[UserRole] = None


class UserResponse(UserBase):
    id: int
    auth0_sub: str
    role: UserRole
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
