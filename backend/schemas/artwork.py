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
    """
    Public artwork response schema.

    Performance optimizations:
    - Optional fields (image_url, end_date) only included when present
    - Excludes sensitive fields like secret_threshold
    - Minimal response size for list endpoints
    """

    id: int
    seller_id: int
    current_highest_bid: float
    image_url: Optional[str] = None
    status: ArtworkStatus
    end_date: Optional[datetime] = None
    created_at: datetime

    class Config:
        from_attributes = True
        # Ensure minimal response size by using efficient serialization
        use_enum_values = True  # Serialize enums as strings, not objects


class ArtworkWithSecretResponse(ArtworkResponse):
    """
    Artwork response with secret threshold (seller/admin only).

    This schema extends ArtworkResponse to include the secret_threshold
    field which should only be exposed to the artwork owner or admins.
    """

    secret_threshold: float
