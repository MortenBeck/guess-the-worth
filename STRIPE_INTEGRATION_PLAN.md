# Stripe Payment Integration Plan (Test Mode)

**Project**: Guess The Worth - Secret Threshold Bidding Platform
**Branch**: `stripe-integration`
**Status**: Planning Phase
**Last Updated**: 2025-11-24

---

## Table of Contents

1. [Overview](#overview)
2. [Current State Analysis](#current-state-analysis)
3. [Architecture Design](#architecture-design)
4. [Phase-by-Phase Implementation](#phase-by-phase-implementation)
5. [Critical Considerations](#critical-considerations)
6. [Testing Strategy](#testing-strategy)
7. [Questions & Decisions Needed](#questions--decisions-needed)
8. [Success Criteria](#success-criteria)

---

## Overview

### Business Context

Guess The Worth uses a unique "secret threshold" bidding system where:

- Each artwork has a hidden price threshold set by the seller
- Buyers place bids without knowing the threshold
- When a bid meets or exceeds the threshold → **Artwork is sold**
- Payment must be processed to complete the transaction

### Integration Goal

Implement Stripe payment processing in **test mode** to handle payments when winning bids are placed, ensuring secure, PCI-compliant payment collection before finalizing artwork sales.

### Scope

- ✅ Test mode only (no production deployment)
- ✅ One-time payments (no subscriptions)
- ✅ Card payments via Payment Intents
- ✅ Webhook handling for payment confirmation
- ✅ 10-minute payment timeout window
- ✅ Block concurrent bids during payment
- ✅ Email notifications for payment events
- ❌ Refund capability (not needed for test mode)
- ❌ Marketplace/Connect (not needed - direct sales only)
- ❌ Subscription billing
- ❌ Multiple currencies (USD only for now)

---

## Current State Analysis

### ✅ Already Implemented

1. **Dependencies**
   - `stripe` package in [requirements.txt](backend/requirements.txt:10)
   - Ready to use, just needs configuration

2. **Configuration Infrastructure**
   - Settings class in [settings.py](backend/config/settings.py:27-30) has Stripe fields
   - Environment variables defined in [.env.example](backend/.env.example:19-23)

   ```python
   stripe_secret_key: str = ""
   stripe_publishable_key: str = ""
   stripe_webhook_secret: Optional[str] = None
   ```

3. **Bidding Logic**
   - Winning bid detection: [bids.py](backend/routers/bids.py:88-104)
   - Real-time Socket.IO events: [bids.py](backend/routers/bids.py:126-157)
   - Audit logging: [bids.py](backend/routers/bids.py:111-123)

4. **Database Schema**
   - Users, Artworks, Bids tables exist
   - Foreign key relationships established
   - Audit logs table for security tracking

5. **Authentication**
   - Auth0 + JWT authentication
   - Role-based access control (ADMIN, SELLER, BUYER)
   - Secure user identification

### ❌ Missing Components

1. **Payment Model** - No database table for payment records
2. **Payment Endpoints** - No API routes for payment operations
3. **Stripe Service** - No service layer for Stripe API interactions
4. **Frontend Payment UI** - No payment form or checkout flow
5. **Webhook Handler** - No endpoint to receive Stripe events
6. **Payment Status Flow** - No PENDING_PAYMENT status in artwork lifecycle

---

## Architecture Design

### Payment Flow Diagram

```
┌─────────────┐
│   User      │
│ Places Bid  │
└──────┬──────┘
       │
       ▼
┌──────────────────┐
│ Check if Winning │
│ (>= Threshold)   │
└──────┬───────────┘
       │
       ├─── No ──► Bid saved, status=OUTBID
       │
       └─── Yes ──►┌──────────────────────┐
                   │ Create Payment Intent │
                   │ (Stripe API)          │
                   └──────────┬────────────┘
                              │
                              ▼
                   ┌──────────────────────┐
                   │ Artwork Status:      │
                   │ PENDING_PAYMENT      │
                   └──────────┬────────────┘
                              │
                              ▼
                   ┌──────────────────────┐
                   │ Show Payment Modal   │
                   │ (Stripe Elements)    │
                   └──────────┬────────────┘
                              │
                 ┌────────────┴────────────┐
                 │                         │
                 ▼                         ▼
      ┌──────────────────┐     ┌──────────────────┐
      │ Payment Success  │     │ Payment Failed   │
      └────────┬─────────┘     └────────┬─────────┘
               │                         │
               ▼                         ▼
      ┌──────────────────┐     ┌──────────────────┐
      │ Webhook Event:   │     │ Release Artwork  │
      │ payment_intent   │     │ Back to ACTIVE   │
      │ .succeeded       │     │ Status           │
      └────────┬─────────┘     └──────────────────┘
               │
               ▼
      ┌──────────────────┐
      │ Artwork Status:  │
      │ SOLD             │
      │                  │
      │ Notify Buyer +   │
      │ Seller           │
      └──────────────────┘
```

### Database Schema Changes

#### New Table: `payments`

```sql
CREATE TABLE payments (
    id SERIAL PRIMARY KEY,
    bid_id INTEGER UNIQUE NOT NULL REFERENCES bids(id),
    stripe_payment_intent_id VARCHAR(255) UNIQUE NOT NULL,
    stripe_charge_id VARCHAR(255),
    amount DECIMAL(10, 2) NOT NULL,
    currency VARCHAR(3) DEFAULT 'usd',
    status VARCHAR(50) NOT NULL CHECK (status IN (
        'PENDING',
        'PROCESSING',
        'SUCCEEDED',
        'FAILED',
        'REFUNDED',
        'CANCELED'
    )),
    failure_reason TEXT,
    refund_amount DECIMAL(10, 2),
    refund_reason TEXT,
    metadata JSONB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_payments_bid_id ON payments(bid_id);
CREATE INDEX idx_payments_stripe_payment_intent_id ON payments(stripe_payment_intent_id);
CREATE INDEX idx_payments_status ON payments(status);
```

#### Update Artwork Status Enum

Add new status to [artwork.py](backend/models/artwork.py):

```python
class ArtworkStatus(str, Enum):
    ACTIVE = "ACTIVE"
    PENDING_PAYMENT = "PENDING_PAYMENT"  # NEW
    SOLD = "SOLD"
    EXPIRED = "EXPIRED"
    ARCHIVED = "ARCHIVED"
```

### API Endpoints

#### Payment Routes (`/api/payments`)

| Method | Endpoint                      | Auth         | Purpose                                                 |
| ------ | ----------------------------- | ------------ | ------------------------------------------------------- |
| POST   | `/create-intent`              | Buyer        | Create payment intent for winning bid                   |
| GET    | `/intent/{payment_intent_id}` | Buyer        | Get payment intent status                               |
| POST   | `/webhook`                    | Public\*     | Stripe webhook receiver (\*with signature verification) |
| GET    | `/my-payments`                | User         | List user's payment history                             |
| GET    | `/{id}`                       | User/Admin   | Get payment details                                     |
| POST   | `/{id}/refund`                | Admin        | Process refund                                          |
| GET    | `/artwork/{artwork_id}`       | Seller/Admin | Get payment for artwork                                 |

### Frontend Components

```
frontend/src/
├── components/
│   ├── Payment/
│   │   ├── PaymentModal.jsx          # Main payment container
│   │   ├── PaymentForm.jsx           # Stripe Elements form
│   │   ├── PaymentSuccess.jsx        # Success confirmation
│   │   ├── PaymentFailed.jsx         # Error handling
│   │   └── PaymentProcessing.jsx     # Loading state
│   └── ...
├── services/
│   ├── paymentService.js             # Payment API calls
│   └── ...
├── hooks/
│   ├── usePayment.js                 # Payment logic hook
│   └── ...
└── store/
    ├── paymentStore.js               # Payment state management
    └── ...
```

---

## Phase-by-Phase Implementation

### Phase 1: Backend Foundation (Day 1)

#### 1.1 Get Stripe Test Credentials

**Tasks:**

- [ ] Sign up for Stripe account (if needed)
- [ ] Navigate to [Stripe Dashboard](https://dashboard.stripe.com/test/apikeys)
- [ ] Copy test API keys:
  - Publishable key: `pk_test_...`
  - Secret key: `sk_test_...`
- [ ] Update `backend/.env`:
  ```env
  STRIPE_SECRET_KEY=sk_test_51...
  STRIPE_PUBLISHABLE_KEY=pk_test_51...
  ```

**Verification:**

```bash
cd backend
python -c "from config.settings import settings; print(f'Stripe key loaded: {settings.stripe_secret_key[:20]}...')"
```

#### 1.2 Create Payment Model

**File:** `backend/models/payment.py`

```python
from datetime import datetime
from enum import Enum
from sqlalchemy import Column, Integer, String, DECIMAL, DateTime, Text, ForeignKey, Index
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import relationship
from models.base import Base


class PaymentStatus(str, Enum):
    PENDING = "PENDING"
    PROCESSING = "PROCESSING"
    SUCCEEDED = "SUCCEEDED"
    FAILED = "FAILED"
    REFUNDED = "REFUNDED"
    CANCELED = "CANCELED"


class Payment(Base):
    __tablename__ = "payments"

    id = Column(Integer, primary_key=True, index=True)
    bid_id = Column(Integer, ForeignKey("bids.id"), unique=True, nullable=False)
    stripe_payment_intent_id = Column(String(255), unique=True, nullable=False)
    stripe_charge_id = Column(String(255), nullable=True)
    amount = Column(DECIMAL(10, 2), nullable=False)
    currency = Column(String(3), default="usd")
    status = Column(String(50), nullable=False, default=PaymentStatus.PENDING)
    failure_reason = Column(Text, nullable=True)
    refund_amount = Column(DECIMAL(10, 2), nullable=True)
    refund_reason = Column(Text, nullable=True)
    metadata = Column(JSONB, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    bid = relationship("Bid", back_populates="payment")

    def __repr__(self):
        return f"<Payment(id={self.id}, bid_id={self.bid_id}, status={self.status}, amount={self.amount})>"


# Add indexes
Index("idx_payments_bid_id", Payment.bid_id)
Index("idx_payments_stripe_payment_intent_id", Payment.stripe_payment_intent_id)
Index("idx_payments_status", Payment.status)
```

**File:** Update `backend/models/bid.py`

```python
# Add to Bid model
payment = relationship("Payment", back_populates="bid", uselist=False)
```

**File:** Update `backend/models/__init__.py`

```python
from models.payment import Payment, PaymentStatus

__all__ = [..., "Payment", "PaymentStatus"]
```

#### 1.3 Create Database Migration

**Commands:**

```bash
cd backend
alembic revision --autogenerate -m "add_payments_table"
alembic upgrade head
```

**Verification:**

```bash
# Connect to database and verify
psql $DATABASE_URL -c "\d payments"
```

#### 1.4 Create Payment Schemas

**File:** `backend/schemas/payment.py`

```python
from datetime import datetime
from decimal import Decimal
from typing import Optional
from pydantic import BaseModel, Field


class PaymentBase(BaseModel):
    amount: Decimal = Field(..., gt=0, description="Payment amount")
    currency: str = Field(default="usd", max_length=3)


class PaymentCreate(PaymentBase):
    bid_id: int = Field(..., description="ID of the winning bid")


class PaymentIntentResponse(BaseModel):
    client_secret: str
    payment_intent_id: str
    amount: Decimal
    currency: str


class PaymentResponse(BaseModel):
    id: int
    bid_id: int
    stripe_payment_intent_id: str
    amount: Decimal
    currency: str
    status: str
    failure_reason: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class RefundCreate(BaseModel):
    reason: str = Field(..., min_length=10, max_length=500)
    amount: Optional[Decimal] = Field(None, gt=0, description="Partial refund amount (optional)")
```

**File:** Update `backend/schemas/__init__.py`

```python
from schemas.payment import (
    PaymentCreate,
    PaymentResponse,
    PaymentIntentResponse,
    RefundCreate
)

__all__ = [..., "PaymentCreate", "PaymentResponse", "PaymentIntentResponse", "RefundCreate"]
```

---

### Phase 2: Stripe Service Layer (Day 1-2)

#### 2.1 Create Stripe Service

**File:** `backend/services/stripe_service.py`

```python
import stripe
from decimal import Decimal
from typing import Optional, Dict, Any
from sqlalchemy.orm import Session
from fastapi import HTTPException

from config.settings import settings
from models import Payment, Bid, Artwork, User
from models.payment import PaymentStatus

# Initialize Stripe
stripe.api_key = settings.stripe_secret_key


class StripeService:
    """Service for handling Stripe payment operations."""

    @staticmethod
    def create_payment_intent(
        bid: Bid,
        buyer: User,
        db: Session
    ) -> Dict[str, Any]:
        """
        Create a Stripe Payment Intent for a winning bid.

        Args:
            bid: The winning bid object
            buyer: The user making the payment
            db: Database session

        Returns:
            Dictionary with client_secret and payment_intent_id
        """
        # Convert amount to cents (Stripe uses smallest currency unit)
        amount_cents = int(bid.amount * 100)

        # Get artwork details for metadata
        artwork = bid.artwork

        try:
            # Create Payment Intent
            payment_intent = stripe.PaymentIntent.create(
                amount=amount_cents,
                currency="usd",
                payment_method_types=["card"],
                metadata={
                    "bid_id": str(bid.id),
                    "artwork_id": str(artwork.id),
                    "artwork_title": artwork.title,
                    "buyer_id": str(buyer.id),
                    "buyer_email": buyer.email,
                    "seller_id": str(artwork.seller_id),
                },
                description=f"Payment for artwork: {artwork.title}",
                receipt_email=buyer.email,
            )

            # Create Payment record in database
            payment = Payment(
                bid_id=bid.id,
                stripe_payment_intent_id=payment_intent.id,
                amount=bid.amount,
                currency="usd",
                status=PaymentStatus.PENDING,
                metadata={
                    "artwork_id": artwork.id,
                    "buyer_id": buyer.id,
                    "seller_id": artwork.seller_id,
                }
            )

            db.add(payment)
            db.commit()
            db.refresh(payment)

            return {
                "client_secret": payment_intent.client_secret,
                "payment_intent_id": payment_intent.id,
                "amount": bid.amount,
                "currency": "usd",
                "payment_id": payment.id,
            }

        except stripe.error.StripeError as e:
            db.rollback()
            raise HTTPException(
                status_code=400,
                detail=f"Stripe error: {str(e)}"
            )

    @staticmethod
    def get_payment_intent(payment_intent_id: str) -> Optional[stripe.PaymentIntent]:
        """Retrieve a Payment Intent from Stripe."""
        try:
            return stripe.PaymentIntent.retrieve(payment_intent_id)
        except stripe.error.StripeError as e:
            raise HTTPException(
                status_code=400,
                detail=f"Failed to retrieve payment intent: {str(e)}"
            )

    @staticmethod
    def handle_payment_succeeded(
        payment_intent: stripe.PaymentIntent,
        db: Session
    ) -> Payment:
        """
        Handle successful payment webhook event.

        Updates payment status and marks artwork as SOLD.
        """
        # Find payment record
        payment = db.query(Payment).filter(
            Payment.stripe_payment_intent_id == payment_intent.id
        ).first()

        if not payment:
            raise HTTPException(
                status_code=404,
                detail=f"Payment not found for intent: {payment_intent.id}"
            )

        # Update payment status
        payment.status = PaymentStatus.SUCCEEDED
        payment.stripe_charge_id = payment_intent.charges.data[0].id if payment_intent.charges.data else None

        # Get related bid and artwork
        bid = payment.bid
        artwork = bid.artwork

        # Mark artwork as SOLD
        artwork.status = "SOLD"

        db.commit()
        db.refresh(payment)

        return payment

    @staticmethod
    def handle_payment_failed(
        payment_intent: stripe.PaymentIntent,
        db: Session
    ) -> Payment:
        """
        Handle failed payment webhook event.

        Updates payment status and returns artwork to ACTIVE.
        """
        payment = db.query(Payment).filter(
            Payment.stripe_payment_intent_id == payment_intent.id
        ).first()

        if not payment:
            raise HTTPException(
                status_code=404,
                detail=f"Payment not found for intent: {payment_intent.id}"
            )

        # Update payment status
        payment.status = PaymentStatus.FAILED
        payment.failure_reason = payment_intent.last_payment_error.message if payment_intent.last_payment_error else "Unknown error"

        # Get related bid and artwork
        bid = payment.bid
        artwork = bid.artwork

        # Return artwork to ACTIVE status
        artwork.status = "ACTIVE"
        # Reset winning bid flag
        bid.is_winning = False

        db.commit()
        db.refresh(payment)

        return payment

    @staticmethod
    def create_refund(
        payment: Payment,
        reason: str,
        amount: Optional[Decimal] = None,
        db: Session = None
    ) -> stripe.Refund:
        """
        Create a refund for a payment.

        Args:
            payment: Payment object to refund
            reason: Reason for refund
            amount: Optional partial refund amount (full refund if None)
            db: Database session
        """
        try:
            refund_params = {
                "payment_intent": payment.stripe_payment_intent_id,
                "reason": "requested_by_customer",  # Stripe enum
            }

            # Partial refund if amount specified
            if amount:
                refund_params["amount"] = int(amount * 100)

            refund = stripe.Refund.create(**refund_params)

            # Update payment record
            if db:
                payment.status = PaymentStatus.REFUNDED
                payment.refund_amount = amount or payment.amount
                payment.refund_reason = reason
                db.commit()

            return refund

        except stripe.error.StripeError as e:
            if db:
                db.rollback()
            raise HTTPException(
                status_code=400,
                detail=f"Refund failed: {str(e)}"
            )

    @staticmethod
    def verify_webhook_signature(
        payload: bytes,
        signature: str,
        webhook_secret: str
    ) -> stripe.Event:
        """
        Verify webhook signature and construct event.

        Security: CRITICAL for webhook authenticity.
        """
        try:
            event = stripe.Webhook.construct_event(
                payload, signature, webhook_secret
            )
            return event
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid payload")
        except stripe.error.SignatureVerificationError:
            raise HTTPException(status_code=400, detail="Invalid signature")
```

---

### Phase 3: Payment Endpoints (Day 2)

#### 3.1 Create Payment Router

**File:** `backend/routers/payments.py`

```python
from typing import List
from fastapi import APIRouter, Depends, HTTPException, Request, Header
from sqlalchemy.orm import Session, joinedload

from database import get_db
from models import Payment, Bid, User, Artwork
from models.payment import PaymentStatus
from schemas import (
    PaymentCreate,
    PaymentResponse,
    PaymentIntentResponse,
    RefundCreate
)
from services.stripe_service import StripeService
from services.audit_service import AuditService
from utils.auth import get_current_user, require_role
from config.settings import settings

router = APIRouter()


@router.post("/create-intent", response_model=PaymentIntentResponse)
async def create_payment_intent(
    payment_data: PaymentCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    request: Request = None,
):
    """
    Create a Stripe Payment Intent for a winning bid.

    Security:
    - Only the bid owner can create payment for their bid
    - Bid must be winning
    - Payment intent can only be created once per bid
    """
    # Get bid with related data
    bid = db.query(Bid).options(
        joinedload(Bid.artwork),
        joinedload(Bid.bidder)
    ).filter(Bid.id == payment_data.bid_id).first()

    if not bid:
        raise HTTPException(status_code=404, detail="Bid not found")

    # Security: Verify bid belongs to current user
    if bid.bidder_id != current_user.id:
        raise HTTPException(
            status_code=403,
            detail="You can only create payment for your own bids"
        )

    # Verify bid is winning
    if not bid.is_winning:
        raise HTTPException(
            status_code=400,
            detail="Payment can only be created for winning bids"
        )

    # Check if payment already exists
    existing_payment = db.query(Payment).filter(
        Payment.bid_id == bid.id
    ).first()

    if existing_payment:
        # If payment already succeeded, don't allow recreation
        if existing_payment.status == PaymentStatus.SUCCEEDED:
            raise HTTPException(
                status_code=400,
                detail="Payment already completed for this bid"
            )
        # If payment is pending/processing, return existing client secret
        elif existing_payment.status in [PaymentStatus.PENDING, PaymentStatus.PROCESSING]:
            payment_intent = StripeService.get_payment_intent(
                existing_payment.stripe_payment_intent_id
            )
            return PaymentIntentResponse(
                client_secret=payment_intent.client_secret,
                payment_intent_id=payment_intent.id,
                amount=existing_payment.amount,
                currency=existing_payment.currency
            )

    # Create payment intent
    result = StripeService.create_payment_intent(
        bid=bid,
        buyer=current_user,
        db=db
    )

    # Update artwork status to PENDING_PAYMENT
    bid.artwork.status = "PENDING_PAYMENT"
    db.commit()

    # Audit log
    AuditService.log_action(
        db=db,
        action="payment_intent_created",
        resource_type="payment",
        resource_id=result["payment_id"],
        user=current_user,
        details={
            "bid_id": bid.id,
            "artwork_id": bid.artwork.id,
            "amount": float(bid.amount),
        },
        request=request,
    )

    return PaymentIntentResponse(**result)


@router.post("/webhook")
async def stripe_webhook(
    request: Request,
    stripe_signature: str = Header(None, alias="stripe-signature"),
    db: Session = Depends(get_db),
):
    """
    Handle Stripe webhook events.

    Security: Verifies webhook signature to ensure authenticity.
    Idempotency: Safe to process same event multiple times.
    """
    # Get raw body for signature verification
    payload = await request.body()

    # Verify webhook signature
    if not settings.stripe_webhook_secret:
        raise HTTPException(
            status_code=500,
            detail="Webhook secret not configured"
        )

    event = StripeService.verify_webhook_signature(
        payload=payload,
        signature=stripe_signature,
        webhook_secret=settings.stripe_webhook_secret
    )

    # Handle different event types
    if event.type == "payment_intent.succeeded":
        payment_intent = event.data.object
        payment = StripeService.handle_payment_succeeded(payment_intent, db)

        # Audit log
        AuditService.log_action(
            db=db,
            action="payment_succeeded",
            resource_type="payment",
            resource_id=payment.id,
            user=None,  # Webhook has no user context
            details={
                "payment_intent_id": payment_intent.id,
                "amount": float(payment.amount),
            },
            request=request,
        )

        # Emit socket event for real-time update
        from main import sio
        bid = payment.bid
        await sio.emit(
            "payment_completed",
            {
                "artwork_id": bid.artwork_id,
                "payment_id": payment.id,
                "status": "SOLD",
            },
            room=f"artwork_{bid.artwork_id}"
        )

    elif event.type == "payment_intent.payment_failed":
        payment_intent = event.data.object
        payment = StripeService.handle_payment_failed(payment_intent, db)

        # Audit log
        AuditService.log_action(
            db=db,
            action="payment_failed",
            resource_type="payment",
            resource_id=payment.id,
            user=None,
            details={
                "payment_intent_id": payment_intent.id,
                "failure_reason": payment.failure_reason,
            },
            request=request,
        )

        # Emit socket event
        from main import sio
        bid = payment.bid
        await sio.emit(
            "payment_failed",
            {
                "artwork_id": bid.artwork_id,
                "payment_id": payment.id,
                "reason": payment.failure_reason,
            },
            room=f"artwork_{bid.artwork_id}"
        )

    return {"status": "success"}


@router.get("/my-payments", response_model=List[PaymentResponse])
async def get_my_payments(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get all payments for the current user."""
    payments = db.query(Payment).join(Bid).filter(
        Bid.bidder_id == current_user.id
    ).order_by(Payment.created_at.desc()).all()

    return payments


@router.get("/{payment_id}", response_model=PaymentResponse)
async def get_payment(
    payment_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get payment details by ID."""
    payment = db.query(Payment).options(
        joinedload(Payment.bid).joinedload(Bid.artwork)
    ).filter(Payment.id == payment_id).first()

    if not payment:
        raise HTTPException(status_code=404, detail="Payment not found")

    # Security: Only buyer, seller, or admin can view payment
    bid = payment.bid
    artwork = bid.artwork

    is_authorized = (
        current_user.id == bid.bidder_id or  # Buyer
        current_user.id == artwork.seller_id or  # Seller
        current_user.role == "ADMIN"  # Admin
    )

    if not is_authorized:
        raise HTTPException(
            status_code=403,
            detail="You don't have permission to view this payment"
        )

    return payment


@router.post("/{payment_id}/refund")
@require_role("ADMIN")
async def refund_payment(
    payment_id: int,
    refund_data: RefundCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    request: Request = None,
):
    """
    Process a refund for a payment (Admin only).
    """
    payment = db.query(Payment).filter(Payment.id == payment_id).first()

    if not payment:
        raise HTTPException(status_code=404, detail="Payment not found")

    if payment.status != PaymentStatus.SUCCEEDED:
        raise HTTPException(
            status_code=400,
            detail="Can only refund succeeded payments"
        )

    # Create refund via Stripe
    refund = StripeService.create_refund(
        payment=payment,
        reason=refund_data.reason,
        amount=refund_data.amount,
        db=db
    )

    # Update artwork status back to ACTIVE if full refund
    if not refund_data.amount or refund_data.amount >= payment.amount:
        bid = payment.bid
        artwork = bid.artwork
        artwork.status = "ACTIVE"
        db.commit()

    # Audit log
    AuditService.log_action(
        db=db,
        action="payment_refunded",
        resource_type="payment",
        resource_id=payment.id,
        user=current_user,
        details={
            "refund_id": refund.id,
            "amount": float(refund_data.amount or payment.amount),
            "reason": refund_data.reason,
        },
        request=request,
    )

    return {
        "status": "success",
        "refund_id": refund.id,
        "amount": float(refund_data.amount or payment.amount)
    }


@router.get("/artwork/{artwork_id}", response_model=PaymentResponse)
async def get_artwork_payment(
    artwork_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Get payment for an artwork (Seller/Admin only).
    """
    artwork = db.query(Artwork).filter(Artwork.id == artwork_id).first()

    if not artwork:
        raise HTTPException(status_code=404, detail="Artwork not found")

    # Security check
    is_authorized = (
        current_user.id == artwork.seller_id or
        current_user.role == "ADMIN"
    )

    if not is_authorized:
        raise HTTPException(
            status_code=403,
            detail="Only the seller or admin can view artwork payments"
        )

    # Find payment through bid
    payment = db.query(Payment).join(Bid).filter(
        Bid.artwork_id == artwork_id,
        Payment.status == PaymentStatus.SUCCEEDED
    ).first()

    if not payment:
        raise HTTPException(
            status_code=404,
            detail="No completed payment found for this artwork"
        )

    return payment
```

#### 3.2 Register Router in Main App

**File:** Update `backend/main.py`

```python
# Add import
from routers import payments

# Register router
app.include_router(payments.router, prefix="/api/payments", tags=["payments"])
```

---

### Phase 4: Update Bid Logic (Day 2)

#### 4.1 Modify Bid Creation Flow

**File:** Update `backend/routers/bids.py`

Replace lines 102-104:

```python
# OLD CODE:
# If winning bid, mark artwork as sold
if is_winning:
    artwork.status = "SOLD"
```

With:

```python
# NEW CODE:
# If winning bid, mark artwork as PENDING_PAYMENT
# Actual SOLD status will be set after payment confirmation
if is_winning:
    artwork.status = "PENDING_PAYMENT"
```

Update socket event at line 148:

```python
# If winning bid, emit payment_required event
if is_winning:
    await sio.emit(
        "payment_required",  # Changed from "artwork_sold"
        {
            "artwork_id": artwork.id,
            "winning_bid": float(db_bid.amount),
            "bid_id": db_bid.id,
            "requires_payment": True,
        },
        room=f"artwork_{artwork.id}",
    )
```

---

### Phase 5: Frontend Integration (Day 3-4)

#### 5.1 Install Dependencies

```bash
cd frontend
npm install @stripe/stripe-js @stripe/react-stripe-js
```

#### 5.2 Create Stripe Configuration

**File:** `frontend/src/config/stripe.js`

```javascript
import { loadStripe } from "@stripe/stripe-js";

// Load Stripe publishable key from environment
const stripePromise = loadStripe(import.meta.env.VITE_STRIPE_PUBLISHABLE_KEY);

export { stripePromise };
```

**File:** Update `frontend/.env.example`

```env
VITE_STRIPE_PUBLISHABLE_KEY=pk_test_your_publishable_key
```

#### 5.3 Create Payment Service

**File:** `frontend/src/services/paymentService.js`

```javascript
import api from "./api";

export const paymentService = {
  /**
   * Create a payment intent for a winning bid
   */
  async createPaymentIntent(bidId) {
    const response = await api.post("/api/payments/create-intent", {
      bid_id: bidId,
      amount: 0, // Amount comes from bid on backend
    });
    return response.data;
  },

  /**
   * Get payment status
   */
  async getPayment(paymentId) {
    const response = await api.get(`/api/payments/${paymentId}`);
    return response.data;
  },

  /**
   * Get my payment history
   */
  async getMyPayments() {
    const response = await api.get("/api/payments/my-payments");
    return response.data;
  },

  /**
   * Request refund (admin only)
   */
  async requestRefund(paymentId, reason, amount = null) {
    const response = await api.post(`/api/payments/${paymentId}/refund`, {
      reason,
      amount,
    });
    return response.data;
  },
};
```

#### 5.4 Create Payment Store

**File:** `frontend/src/store/paymentStore.js`

```javascript
import { create } from "zustand";

const usePaymentStore = create((set, get) => ({
  // State
  currentPayment: null,
  clientSecret: null,
  paymentStatus: null,
  isProcessing: false,
  error: null,

  // Actions
  setCurrentPayment: (payment) => set({ currentPayment: payment }),

  setClientSecret: (clientSecret) => set({ clientSecret }),

  setPaymentStatus: (status) => set({ paymentStatus: status }),

  setProcessing: (isProcessing) => set({ isProcessing }),

  setError: (error) => set({ error }),

  resetPayment: () =>
    set({
      currentPayment: null,
      clientSecret: null,
      paymentStatus: null,
      isProcessing: false,
      error: null,
    }),
}));

export default usePaymentStore;
```

#### 5.5 Create Payment Modal Component

**File:** `frontend/src/components/Payment/PaymentModal.jsx`

```javascript
import React, { useEffect, useState } from "react";
import {
  Modal,
  ModalOverlay,
  ModalContent,
  ModalHeader,
  ModalBody,
  ModalCloseButton,
  VStack,
  Text,
  Box,
  Image,
  Divider,
} from "@chakra-ui/react";
import { Elements } from "@stripe/react-stripe-js";
import { stripePromise } from "../../config/stripe";
import PaymentForm from "./PaymentForm";
import PaymentProcessing from "./PaymentProcessing";
import PaymentSuccess from "./PaymentSuccess";
import PaymentFailed from "./PaymentFailed";
import { paymentService } from "../../services/paymentService";
import usePaymentStore from "../../store/paymentStore";

const PaymentModal = ({ isOpen, onClose, bid, artwork }) => {
  const {
    clientSecret,
    setClientSecret,
    paymentStatus,
    setPaymentStatus,
    setProcessing,
    setError,
    resetPayment,
  } = usePaymentStore();

  const [loading, setLoading] = useState(false);

  useEffect(() => {
    if (isOpen && bid && !clientSecret) {
      // Create payment intent when modal opens
      createPaymentIntent();
    }
  }, [isOpen, bid]);

  const createPaymentIntent = async () => {
    setLoading(true);
    setError(null);

    try {
      const response = await paymentService.createPaymentIntent(bid.id);
      setClientSecret(response.client_secret);
    } catch (error) {
      console.error("Failed to create payment intent:", error);
      setError(error.response?.data?.detail || "Failed to initialize payment");
    } finally {
      setLoading(false);
    }
  };

  const handleClose = () => {
    resetPayment();
    onClose();
  };

  const renderContent = () => {
    if (loading) {
      return <PaymentProcessing message="Initializing payment..." />;
    }

    if (paymentStatus === "succeeded") {
      return <PaymentSuccess artwork={artwork} onClose={handleClose} />;
    }

    if (paymentStatus === "failed") {
      return (
        <PaymentFailed onRetry={createPaymentIntent} onClose={handleClose} />
      );
    }

    return clientSecret ? (
      <Elements stripe={stripePromise} options={{ clientSecret }}>
        <PaymentForm
          artwork={artwork}
          amount={bid.amount}
          onSuccess={() => setPaymentStatus("succeeded")}
          onError={() => setPaymentStatus("failed")}
        />
      </Elements>
    ) : null;
  };

  return (
    <Modal
      isOpen={isOpen}
      onClose={handleClose}
      size="lg"
      closeOnOverlayClick={false}
    >
      <ModalOverlay />
      <ModalContent>
        <ModalHeader>Complete Payment</ModalHeader>
        <ModalCloseButton />
        <ModalBody pb={6}>
          <VStack spacing={4} align="stretch">
            {/* Artwork Summary */}
            <Box>
              <Image
                src={artwork?.image_url || "/placeholder.jpg"}
                alt={artwork?.title}
                borderRadius="md"
                maxH="200px"
                objectFit="cover"
                w="100%"
              />
              <Text fontWeight="bold" mt={2}>
                {artwork?.title}
              </Text>
              <Text fontSize="sm" color="gray.600">
                by {artwork?.artist_name}
              </Text>
              <Text fontSize="2xl" fontWeight="bold" color="green.500" mt={2}>
                ${bid?.amount?.toFixed(2)}
              </Text>
            </Box>

            <Divider />

            {/* Payment Form */}
            {renderContent()}
          </VStack>
        </ModalBody>
      </ModalContent>
    </Modal>
  );
};

export default PaymentModal;
```

#### 5.6 Create Payment Form Component

**File:** `frontend/src/components/Payment/PaymentForm.jsx`

```javascript
import React, { useState } from "react";
import { Button, VStack, Text, Alert, AlertIcon, Box } from "@chakra-ui/react";
import {
  PaymentElement,
  useStripe,
  useElements,
} from "@stripe/react-stripe-js";
import usePaymentStore from "../../store/paymentStore";

const PaymentForm = ({ artwork, amount, onSuccess, onError }) => {
  const stripe = useStripe();
  const elements = useElements();
  const { setProcessing, setError } = usePaymentStore();

  const [message, setMessage] = useState(null);
  const [isLoading, setIsLoading] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();

    if (!stripe || !elements) {
      return;
    }

    setIsLoading(true);
    setProcessing(true);
    setMessage(null);

    const { error } = await stripe.confirmPayment({
      elements,
      confirmParams: {
        return_url: `${window.location.origin}/payment/success`,
      },
      redirect: "if_required",
    });

    if (error) {
      setMessage(error.message);
      setError(error.message);
      setIsLoading(false);
      setProcessing(false);
      onError();
    } else {
      // Payment succeeded
      onSuccess();
      setIsLoading(false);
      setProcessing(false);
    }
  };

  return (
    <form onSubmit={handleSubmit}>
      <VStack spacing={4} align="stretch">
        <Box>
          <Text fontSize="sm" color="gray.600" mb={2}>
            Enter your payment details
          </Text>
          <PaymentElement />
        </Box>

        {message && (
          <Alert status="error">
            <AlertIcon />
            {message}
          </Alert>
        )}

        <Button
          type="submit"
          colorScheme="blue"
          size="lg"
          isLoading={isLoading}
          isDisabled={!stripe || !elements}
          loadingText="Processing..."
        >
          Pay ${amount?.toFixed(2)}
        </Button>

        <Text fontSize="xs" color="gray.500" textAlign="center">
          Your payment is secure and encrypted. Test mode - use card: 4242 4242
          4242 4242
        </Text>
      </VStack>
    </form>
  );
};

export default PaymentForm;
```

#### 5.7 Create Success/Failure Components

**File:** `frontend/src/components/Payment/PaymentSuccess.jsx`

```javascript
import React from "react";
import { VStack, Text, Icon, Button } from "@chakra-ui/react";
import { CheckCircleIcon } from "@chakra-ui/icons";

const PaymentSuccess = ({ artwork, onClose }) => {
  return (
    <VStack spacing={4} py={6}>
      <Icon as={CheckCircleIcon} boxSize={16} color="green.500" />
      <Text fontSize="2xl" fontWeight="bold">
        Payment Successful!
      </Text>
      <Text textAlign="center" color="gray.600">
        Congratulations! You've successfully purchased "{artwork?.title}". The
        seller will be notified.
      </Text>
      <Button colorScheme="green" onClick={onClose}>
        Done
      </Button>
    </VStack>
  );
};

export default PaymentSuccess;
```

**File:** `frontend/src/components/Payment/PaymentFailed.jsx`

```javascript
import React from "react";
import { VStack, Text, Icon, Button, HStack } from "@chakra-ui/react";
import { WarningIcon } from "@chakra-ui/icons";

const PaymentFailed = ({ onRetry, onClose }) => {
  return (
    <VStack spacing={4} py={6}>
      <Icon as={WarningIcon} boxSize={16} color="red.500" />
      <Text fontSize="2xl" fontWeight="bold">
        Payment Failed
      </Text>
      <Text textAlign="center" color="gray.600">
        We couldn't process your payment. Please try again or use a different
        payment method.
      </Text>
      <HStack spacing={3}>
        <Button variant="outline" onClick={onClose}>
          Cancel
        </Button>
        <Button colorScheme="blue" onClick={onRetry}>
          Try Again
        </Button>
      </HStack>
    </VStack>
  );
};

export default PaymentFailed;
```

**File:** `frontend/src/components/Payment/PaymentProcessing.jsx`

```javascript
import React from "react";
import { VStack, Spinner, Text } from "@chakra-ui/react";

const PaymentProcessing = ({ message = "Processing payment..." }) => {
  return (
    <VStack spacing={4} py={8}>
      <Spinner size="xl" color="blue.500" thickness="4px" />
      <Text fontSize="lg" color="gray.600">
        {message}
      </Text>
    </VStack>
  );
};

export default PaymentProcessing;
```

#### 5.8 Integrate with Artwork Detail Page

**File:** Update where bid is placed (e.g., `frontend/src/pages/ArtworkDetailPage.jsx`)

```javascript
import { useState } from "react";
import PaymentModal from "../components/Payment/PaymentModal";

// In your component:
const [showPaymentModal, setShowPaymentModal] = useState(false);
const [winningBid, setWinningBid] = useState(null);

// Listen for winning bid via socket
useEffect(() => {
  socket.on("payment_required", (data) => {
    if (data.artwork_id === artworkId) {
      setWinningBid({
        id: data.bid_id,
        amount: data.winning_bid,
      });
      setShowPaymentModal(true);
    }
  });

  return () => {
    socket.off("payment_required");
  };
}, [artworkId]);

// In your JSX:
<PaymentModal
  isOpen={showPaymentModal}
  onClose={() => setShowPaymentModal(false)}
  bid={winningBid}
  artwork={artwork}
/>;
```

---

### Phase 6: Webhook Setup (Day 4)

#### 6.1 Install Stripe CLI

**Windows:**

```powershell
# Using Scoop
scoop install stripe

# Or download from https://github.com/stripe/stripe-cli/releases
```

**Verify installation:**

```bash
stripe --version
```

#### 6.2 Login to Stripe CLI

```bash
stripe login
```

#### 6.3 Forward Webhooks to Local Server

```bash
# Start your backend server first
cd backend
uvicorn main:socket_app --reload

# In a new terminal, forward webhooks
stripe listen --forward-to localhost:8000/api/payments/webhook
```

**Copy the webhook signing secret** from the output:

```
> Ready! Your webhook signing secret is whsec_xxxxxxxxxxxxx
```

**Add to backend/.env:**

```env
STRIPE_WEBHOOK_SECRET=whsec_xxxxxxxxxxxxx
```

#### 6.4 Test Webhook Events

```bash
# Trigger test payment success event
stripe trigger payment_intent.succeeded

# Trigger test payment failure event
stripe trigger payment_intent.payment_failed
```

---

### Phase 7: Testing (Day 5)

#### 7.1 Backend Unit Tests

**File:** `backend/tests/unit/test_stripe_service.py`

```python
import pytest
from unittest.mock import Mock, patch
from services.stripe_service import StripeService
from models import Bid, Artwork, User, Payment


@pytest.fixture
def mock_bid(db):
    user = User(id=1, email="buyer@test.com", name="Buyer")
    artwork = Artwork(
        id=1,
        title="Test Art",
        seller_id=2,
        secret_threshold=100.0
    )
    bid = Bid(
        id=1,
        artwork_id=1,
        bidder_id=1,
        amount=150.0,
        is_winning=True
    )
    bid.artwork = artwork
    bid.bidder = user
    return bid


@patch('services.stripe_service.stripe.PaymentIntent.create')
def test_create_payment_intent_success(mock_create, db, mock_bid):
    """Test successful payment intent creation."""
    mock_create.return_value = Mock(
        id="pi_test_123",
        client_secret="pi_test_123_secret"
    )

    result = StripeService.create_payment_intent(
        bid=mock_bid,
        buyer=mock_bid.bidder,
        db=db
    )

    assert result["payment_intent_id"] == "pi_test_123"
    assert result["client_secret"] == "pi_test_123_secret"
    assert result["amount"] == 150.0

    # Verify payment record created
    payment = db.query(Payment).first()
    assert payment is not None
    assert payment.bid_id == 1
    assert payment.stripe_payment_intent_id == "pi_test_123"


@patch('services.stripe_service.stripe.PaymentIntent.create')
def test_create_payment_intent_stripe_error(mock_create, db, mock_bid):
    """Test handling of Stripe API errors."""
    import stripe
    mock_create.side_effect = stripe.error.CardError(
        "Card declined",
        "param",
        "code"
    )

    with pytest.raises(HTTPException) as exc:
        StripeService.create_payment_intent(
            bid=mock_bid,
            buyer=mock_bid.bidder,
            db=db
        )

    assert exc.value.status_code == 400
    assert "Stripe error" in exc.value.detail
```

#### 7.2 Integration Tests

**File:** `backend/tests/integration/test_payment_endpoints.py`

```python
import pytest
from fastapi.testclient import TestClient


def test_create_payment_intent_authenticated(client, auth_headers, db):
    """Test creating payment intent as authenticated buyer."""
    # Setup: Create winning bid
    # ... (setup code)

    response = client.post(
        "/api/payments/create-intent",
        json={"bid_id": 1, "amount": 150.0},
        headers=auth_headers
    )

    assert response.status_code == 200
    data = response.json()
    assert "client_secret" in data
    assert "payment_intent_id" in data


def test_create_payment_intent_unauthorized(client, db):
    """Test creating payment intent without authentication."""
    response = client.post(
        "/api/payments/create-intent",
        json={"bid_id": 1, "amount": 150.0}
    )

    assert response.status_code == 401


def test_webhook_valid_signature(client, db):
    """Test webhook with valid Stripe signature."""
    # Mock webhook payload and signature
    payload = b'{"type": "payment_intent.succeeded", ...}'
    signature = "valid_signature"

    with patch('services.stripe_service.StripeService.verify_webhook_signature'):
        response = client.post(
            "/api/payments/webhook",
            data=payload,
            headers={"stripe-signature": signature}
        )

    assert response.status_code == 200
```

#### 7.3 Frontend Component Tests

**File:** `frontend/src/components/Payment/__tests__/PaymentForm.test.jsx`

```javascript
import { render, screen, fireEvent, waitFor } from "@testing-library/react";
import { Elements } from "@stripe/react-stripe-js";
import { loadStripe } from "@stripe/stripe-js";
import PaymentForm from "../PaymentForm";

const stripePromise = loadStripe("pk_test_fake");

describe("PaymentForm", () => {
  it("renders payment form", () => {
    render(
      <Elements stripe={stripePromise}>
        <PaymentForm
          artwork={{ title: "Test Art" }}
          amount={100.0}
          onSuccess={jest.fn()}
          onError={jest.fn()}
        />
      </Elements>,
    );

    expect(screen.getByText(/Enter your payment details/i)).toBeInTheDocument();
    expect(
      screen.getByRole("button", { name: /Pay \$100.00/i }),
    ).toBeInTheDocument();
  });

  it("shows test card hint", () => {
    render(
      <Elements stripe={stripePromise}>
        <PaymentForm
          artwork={{ title: "Test Art" }}
          amount={100.0}
          onSuccess={jest.fn()}
          onError={jest.fn()}
        />
      </Elements>,
    );

    expect(screen.getByText(/4242 4242 4242 4242/i)).toBeInTheDocument();
  });
});
```

#### 7.4 Manual Testing Checklist

**Setup:**

- [ ] Stripe test keys configured in backend/.env
- [ ] Stripe publishable key in frontend/.env
- [ ] Webhook secret configured
- [ ] Stripe CLI forwarding webhooks
- [ ] Backend and frontend servers running

**Test Scenarios:**

1. **Successful Payment Flow**
   - [ ] Place winning bid on artwork
   - [ ] Payment modal appears automatically
   - [ ] Enter test card: `4242 4242 4242 4242`
   - [ ] Expiry: Any future date (e.g., 12/34)
   - [ ] CVC: Any 3 digits (e.g., 123)
   - [ ] ZIP: Any 5 digits (e.g., 12345)
   - [ ] Click "Pay"
   - [ ] Success message displays
   - [ ] Artwork status changes to SOLD
   - [ ] Payment record created in database
   - [ ] Webhook received and processed

2. **Declined Card**
   - [ ] Place winning bid
   - [ ] Use declined test card: `4000 0000 0000 0002`
   - [ ] Payment fails with error message
   - [ ] Artwork returns to ACTIVE status
   - [ ] Can place new bid

3. **3D Secure Authentication**
   - [ ] Place winning bid
   - [ ] Use 3DS test card: `4000 0025 0000 3155`
   - [ ] 3D Secure challenge appears
   - [ ] Complete authentication
   - [ ] Payment succeeds

4. **Insufficient Funds**
   - [ ] Use card: `4000 0000 0000 9995`
   - [ ] Payment fails with "insufficient funds" error

5. **Payment Timeout** (if implemented)
   - [ ] Place winning bid
   - [ ] Wait 15 minutes without paying
   - [ ] Artwork automatically returns to ACTIVE

6. **Admin Refund**
   - [ ] Complete a payment
   - [ ] Login as admin
   - [ ] Navigate to payments section
   - [ ] Issue refund with reason
   - [ ] Verify refund in Stripe dashboard
   - [ ] Artwork status updates appropriately

7. **Concurrent Bids** (if lock implemented)
   - [ ] User A places winning bid
   - [ ] User B tries to bid during payment
   - [ ] User B blocked or queued

8. **Socket.IO Real-time Updates**
   - [ ] Open artwork in two browser windows
   - [ ] Place winning bid in window 1
   - [ ] Verify payment modal shows in window 1
   - [ ] Verify status updates in window 2

---

## Critical Considerations

### 🔒 Security

1. **PCI Compliance**
   - ✅ Never handle raw card data on your server
   - ✅ Use Stripe.js/Elements for card input
   - ✅ All card data goes directly to Stripe
   - ✅ Only receive tokenized payment methods

2. **Webhook Security**
   - ✅ ALWAYS verify webhook signatures
   - ✅ Use `stripe.Webhook.construct_event()`
   - ✅ Protect against replay attacks
   - ✅ Store webhook events for audit

3. **Authentication**
   - ✅ Verify user owns bid before creating payment
   - ✅ Prevent sellers from paying for own artwork
   - ✅ Admin-only refund endpoints

4. **Idempotency**
   - ✅ Check for existing payment before creating new intent
   - ✅ Safe to process same webhook event multiple times
   - ✅ Use database transactions

### 💰 Financial

1. **Amount Handling**
   - ⚠️ Stripe uses cents (multiply by 100)
   - ⚠️ Never use floats for money calculations
   - ✅ Use Decimal type in database
   - ✅ Validate amounts server-side

2. **Currency**
   - Currently hardcoded to USD
   - Consider multi-currency support later

3. **Fees**
   - Stripe charges 2.9% + $0.30 per transaction
   - Consider who pays fees (buyer vs seller)
   - Add fee calculation if needed

### 🔄 State Management

1. **Artwork Status Flow**

   ```
   ACTIVE → (winning bid) → PENDING_PAYMENT → (payment success) → SOLD
                                            → (payment failed) → ACTIVE
                                            → (timeout) → ACTIVE
   ```

2. **Payment Status Flow**

   ```
   PENDING → PROCESSING → SUCCEEDED
                       → FAILED
                       → CANCELED
   SUCCEEDED → REFUNDED
   ```

3. **Race Conditions**
   - Lock artwork during payment processing
   - Prevent multiple payment intents for same bid
   - Handle concurrent bid attempts

### 📊 Monitoring

1. **Metrics to Track**
   - Payment success rate
   - Average time to payment
   - Payment failures by reason
   - Refund rate
   - Revenue tracking

2. **Alerts**
   - Spike in failed payments
   - Webhook delivery failures
   - Unusual refund requests

### 🧪 Testing

1. **Test Cards**

   ```
   Success: 4242 4242 4242 4242
   Decline: 4000 0000 0000 0002
   3D Secure: 4000 0025 0000 3155
   Insufficient: 4000 0000 0000 9995
   ```

2. **Webhook Testing**
   - Use Stripe CLI for local testing
   - Test all event types
   - Verify idempotency

---

## Questions & Decisions Needed

### Business Logic Questions ✅ DECIDED

1. **Payment Timeout**
   - ✅ **10 minutes** - Users have 10 minutes to complete payment
   - ✅ What happens to artwork after timeout? → Return to ACTIVE
   - ✅ Notify user of timeout? → Yes, via email

2. **Concurrent Bids**
   - ✅ **YES - Block new bids during payment processing**
   - ✅ Prevent any new bids while status is PENDING_PAYMENT

3. **Fees**
   - ✅ **Buyer pays fees** - Stripe fees included in bid amount
   - ✅ No separate fee display needed (test environment only)

4. **Refunds**
   - ✅ **NO REFUNDS** - Refund functionality will NOT be implemented
   - ✅ Simplifies implementation significantly
   - ✅ Can be added later if needed in production

5. **Notifications**
   - ✅ **Email notifications enabled**
   - ✅ Email buyer when payment required
   - ✅ Email seller when payment received
   - ✅ Email buyer on payment failure

### Technical Decisions ✅ DECIDED

1. **Payment Flow**
   - ✅ **Payment Intents** (more control, better for our use case)

2. **Frontend Architecture**
   - ✅ **Modal with Stripe Elements** (better UX)

3. **Payment Window**
   - ✅ **10-minute timeout with background job**
   - ✅ Use database query + cron job to check expired payments

4. **Error Handling**
   - ✅ **Unlimited retry attempts** (user can try again with different card)
   - ✅ No cool-down period (test mode, low risk)

---

## Success Criteria

### Phase 1-3 (Backend)

- [ ] Payment model created and migrated
- [ ] StripeService implemented with core methods
- [ ] Payment endpoints created and registered
- [ ] Bid logic updated to use PENDING_PAYMENT
- [ ] Webhook endpoint created with signature verification
- [ ] All backend unit tests passing

### Phase 4-5 (Frontend)

- [ ] Stripe packages installed
- [ ] Payment modal component created
- [ ] Payment form with Stripe Elements
- [ ] Success/failure UI components
- [ ] Payment service integrated with backend API
- [ ] Socket.IO listening for payment events

### Phase 6 (Webhook Testing)

- [ ] Stripe CLI installed and configured
- [ ] Webhooks forwarding to local server
- [ ] Payment success webhook tested
- [ ] Payment failure webhook tested
- [ ] Webhook signing secret configured

### Phase 7 (Testing)

- [ ] All test scenarios completed successfully
- [ ] Backend tests passing (unit + integration)
- [ ] Frontend component tests passing
- [ ] Manual end-to-end flow verified
- [ ] Edge cases handled (timeouts, concurrent bids, etc.)

### Documentation

- [ ] Environment setup documented
- [ ] Test process documented
- [ ] Known issues listed
- [ ] Deployment notes added

---

## Next Steps After This Plan

1. **Review this plan** - Does it align with business requirements?
2. **Answer questions** - Make decisions on open questions
3. **Get Stripe account** - Set up test mode account
4. **Start Phase 1** - Begin with backend implementation
5. **Iterate** - Adjust plan based on learnings

---

## Appendix: Useful Resources

- [Stripe API Docs](https://stripe.com/docs/api)
- [Stripe Payment Intents](https://stripe.com/docs/payments/payment-intents)
- [Stripe Webhooks](https://stripe.com/docs/webhooks)
- [Stripe Testing](https://stripe.com/docs/testing)
- [Stripe CLI](https://stripe.com/docs/stripe-cli)
- [@stripe/react-stripe-js](https://stripe.com/docs/stripe-js/react)

---

**End of Plan**

This is a living document. Update as implementation progresses and new requirements emerge.
