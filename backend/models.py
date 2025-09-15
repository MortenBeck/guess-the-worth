from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, ForeignKey, Enum
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum

Base = declarative_base()

class UserRole(str, enum.Enum):
    BUYER = "buyer"
    SELLER = "seller"
    ADMIN = "admin"

class ArtworkStatus(str, enum.Enum):
    ACTIVE = "active"
    SOLD = "sold"

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
    bids = relationship("Bid", back_populates="artwork")

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