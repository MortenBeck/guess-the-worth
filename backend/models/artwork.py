import enum

from sqlalchemy import Column, DateTime, Enum, Float, ForeignKey, Integer, String
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from .base import Base


class ArtworkStatus(str, enum.Enum):
    ACTIVE = "ACTIVE"
    SOLD = "SOLD"
    ARCHIVED = "ARCHIVED"


class Artwork(Base):
    __tablename__ = "artworks"

    id = Column(Integer, primary_key=True, index=True)
    seller_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    title = Column(String, nullable=False)
    secret_threshold = Column(Float, nullable=False)
    current_highest_bid = Column(Float, default=0.0)
    description = Column(String)
    image_url = Column(String)
    status = Column(Enum(ArtworkStatus), default=ArtworkStatus.ACTIVE, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    seller = relationship("User", back_populates="artworks")
    bids = relationship("Bid", back_populates="artwork", cascade="all, delete-orphan")
