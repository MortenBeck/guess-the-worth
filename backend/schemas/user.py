from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, EmailStr

# Role type for validation (roles are managed in Auth0)
UserRole = Literal["ADMIN", "SELLER", "BUYER"]


class UserBase(BaseModel):
    """Base user schema - data from Auth0."""

    email: EmailStr
    name: str


class UserCreate(BaseModel):
    """Schema for creating minimal user reference."""

    auth0_sub: str


class UserUpdate(BaseModel):
    """User updates are managed in Auth0, not in our database."""

    pass


class UserResponse(UserBase):
    """User response includes Auth0 data attached at runtime."""

    id: int
    auth0_sub: str
    role: UserRole
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
