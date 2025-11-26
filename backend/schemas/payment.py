"""Payment schemas for Stripe integration."""
from datetime import datetime
from decimal import Decimal
from typing import Optional

from pydantic import BaseModel, Field


class PaymentBase(BaseModel):
    """Base payment schema."""

    amount: Decimal = Field(..., gt=0, description="Payment amount in USD")
    currency: str = Field(default="usd", max_length=3)


class PaymentCreate(BaseModel):
    """Schema for creating a new payment intent."""

    bid_id: int = Field(..., description="ID of the winning bid")


class PaymentIntentResponse(BaseModel):
    """Response from creating a payment intent."""

    client_secret: str = Field(..., description="Stripe client secret for frontend")
    payment_intent_id: str = Field(..., description="Stripe Payment Intent ID")
    payment_id: int = Field(..., description="Database payment record ID")
    amount: Decimal = Field(..., description="Payment amount")
    currency: str = Field(default="usd")


class PaymentResponse(BaseModel):
    """Payment response schema."""

    id: int
    bid_id: int
    stripe_payment_intent_id: str
    stripe_charge_id: Optional[str] = None
    amount: Decimal
    currency: str
    status: str
    failure_reason: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
