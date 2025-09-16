from sqlalchemy import Column, Integer, Float, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from .base import Base

class Bid(Base):
    __tablename__ = "bids"

    id = Column(Integer, primary_key=True, index=True)
    artwork_id = Column(Integer, ForeignKey("artworks.id"), nullable=False)
    bidder_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    amount = Column(Float, nullable=False)
    bid_time = Column(DateTime(timezone=True), server_default=func.now())
    is_winning = Column(Boolean, default=False)

    # Relationships
    artwork = relationship("Artwork", back_populates="bids")
    bidder = relationship("User", back_populates="bids")