from datetime import datetime
from typing import Optional

from pydantic import BaseModel

from models.artwork import ArtworkStatus


class ArtworkBase(BaseModel):
    title: str
    description: Optional[str] = None
    artist_name: Optional[str] = None
    category: Optional[str] = None


class ArtworkCreate(ArtworkBase):
    secret_threshold: float
    end_date: Optional[datetime] = None


class ArtworkUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    artist_name: Optional[str] = None
    category: Optional[str] = None
    secret_threshold: Optional[float] = None
    status: Optional[ArtworkStatus] = None
    end_date: Optional[datetime] = None


class ArtworkResponse(ArtworkBase):
    id: int
    seller_id: int
    current_highest_bid: float
    image_url: Optional[str] = None
    status: ArtworkStatus
    end_date: Optional[datetime] = None
    created_at: datetime

    class Config:
        from_attributes = True


class ArtworkWithSecretResponse(ArtworkResponse):
    secret_threshold: float
