import enum

from sqlalchemy import Column, DateTime, Enum, Integer, String
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from .base import Base


class UserRole(str, enum.Enum):
    BUYER = "BUYER"
    SELLER = "SELLER"
    ADMIN = "ADMIN"


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    auth0_sub = Column(String, unique=True, index=True, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    name = Column(String, nullable=False)
    role = Column(Enum(UserRole), default=UserRole.BUYER, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    artworks = relationship("Artwork", back_populates="seller", cascade="all, delete-orphan")
    bids = relationship("Bid", back_populates="bidder", cascade="all, delete-orphan")
