from sqlalchemy import Column, Integer, String, DateTime, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum
from .base import Base

class UserRole(str, enum.Enum):
    BUYER = "buyer"
    SELLER = "seller"
    ADMIN = "admin"

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    auth0_sub = Column(String, unique=True, index=True, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    name = Column(String, nullable=False)
    role = Column(Enum(UserRole), default=UserRole.BUYER, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    artworks = relationship("Artwork", back_populates="seller")
    bids = relationship("Bid", back_populates="bidder")