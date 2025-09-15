from pydantic import BaseModel, EmailStr
from typing import Optional, List
from datetime import datetime
from models import UserRole, ArtworkStatus

# User schemas
class UserBase(BaseModel):
    email: EmailStr
    name: str
    role: UserRole = UserRole.BUYER

class UserCreate(UserBase):
    auth0_sub: str

class UserResponse(UserBase):
    id: int
    auth0_sub: str
    created_at: datetime

    class Config:
        orm_mode = True

# Artwork schemas
class ArtworkBase(BaseModel):
    title: str
    description: Optional[str] = None

class ArtworkCreate(ArtworkBase):
    seller_id: int
    secret_threshold: float

class ArtworkResponse(ArtworkBase):
    id: int
    seller_id: int
    current_highest_bid: float
    image_url: Optional[str] = None
    status: ArtworkStatus
    created_at: datetime

    class Config:
        orm_mode = True

# Bid schemas
class BidBase(BaseModel):
    amount: float

class BidCreate(BidBase):
    artwork_id: int
    bidder_id: int

class BidResponse(BidBase):
    id: int
    artwork_id: int
    bidder_id: int
    bid_time: datetime
    is_winning: bool

    class Config:
        orm_mode = True