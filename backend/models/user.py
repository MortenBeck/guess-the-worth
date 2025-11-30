from datetime import UTC, datetime

from sqlalchemy import Column, DateTime, Integer, String
from sqlalchemy.orm import relationship

from .base import Base


class User(Base):
    """User model - minimal reference to Auth0 user.

    User data (email, name, role) is managed in Auth0 and attached
    to the user object at runtime from the JWT token.
    """

    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    auth0_sub = Column(String, unique=True, nullable=False, index=True)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(UTC))

    artworks = relationship(
        "Artwork", back_populates="seller", cascade="all, delete-orphan"
    )
    bids = relationship("Bid", back_populates="bidder", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<User(id={self.id}, auth0_sub='{self.auth0_sub}')>"
