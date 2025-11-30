"""Payment model for Stripe payment processing."""

from datetime import datetime
from enum import Enum

from models.base import Base
from sqlalchemy import (
    DECIMAL,
    JSON,
    Column,
    DateTime,
    ForeignKey,
    Index,
    Integer,
    String,
    Text,
)
from sqlalchemy.orm import relationship


class PaymentStatus(str, Enum):
    """Payment status enumeration."""

    PENDING = "PENDING"
    PROCESSING = "PROCESSING"
    SUCCEEDED = "SUCCEEDED"
    FAILED = "FAILED"
    CANCELED = "CANCELED"


class Payment(Base):
    """
    Payment model for tracking Stripe payments.

    Each payment is associated with a winning bid and tracks the complete
    payment lifecycle from creation through completion or failure.
    """

    __tablename__ = "payments"

    id = Column(Integer, primary_key=True, index=True)
    bid_id = Column(Integer, ForeignKey("bids.id"), unique=True, nullable=False)
    stripe_payment_intent_id = Column(String(255), unique=True, nullable=False)
    stripe_charge_id = Column(String(255), nullable=True)
    amount = Column(DECIMAL(10, 2), nullable=False)
    currency = Column(String(3), default="usd")
    status = Column(String(50), nullable=False, default=PaymentStatus.PENDING)
    failure_reason = Column(Text, nullable=True)
    payment_metadata = Column(
        JSON, nullable=True
    )  # 'metadata' is reserved in SQLAlchemy
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    bid = relationship("Bid", back_populates="payment")

    def __repr__(self):
        return (
            f"<Payment(id={self.id}, bid_id={self.bid_id}, "
            f"status={self.status}, amount={self.amount})>"
        )


# Create indexes for performance
Index("idx_payments_bid_id", Payment.bid_id)
Index("idx_payments_stripe_payment_intent_id", Payment.stripe_payment_intent_id)
Index("idx_payments_status", Payment.status)
Index("idx_payments_created_at", Payment.created_at)
