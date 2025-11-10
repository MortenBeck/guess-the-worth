from datetime import datetime
from typing import Optional

from pydantic import BaseModel

from models.artwork import ArtworkStatus


class ArtworkBase(BaseModel):
    title: str
    description: Optional[str] = None


class ArtworkCreate(ArtworkBase):
    secret_threshold: float


class ArtworkUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    secret_threshold: Optional[float] = None
    status: Optional[ArtworkStatus] = None


class ArtworkResponse(ArtworkBase):
    id: int
    seller_id: int
    current_highest_bid: float
    image_url: Optional[str] = None
    status: ArtworkStatus
    created_at: datetime

    class Config:
        from_attributes = True


class ArtworkWithSecretResponse(ArtworkResponse):
    secret_threshold: float
