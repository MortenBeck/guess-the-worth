"""Payment endpoints for Stripe integration."""

from typing import Any, Dict, List

from fastapi import APIRouter, Depends, Header, HTTPException, Request
from sqlalchemy.orm import Session, joinedload

from config.settings import settings
from database import get_db
from models import Artwork, Bid, Payment, User
from models.payment import PaymentStatus
from schemas import PaymentCreate, PaymentIntentResponse, PaymentResponse
from services.audit_service import AuditService
from services.stripe_service import StripeService
from utils.auth import get_current_user
from utils.stripe_validator import StripeValidator

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
    # Validate Stripe is configured
    stripe_status = StripeValidator.get_stripe_status()
    if not stripe_status["configured"]:
        raise HTTPException(
            status_code=503,
            detail=(
                "Payment processing is not configured. "
                "Please contact support. "
                f"Errors: {', '.join(stripe_status['errors'][:2])}"
            ),
        )

    # Get bid with related data
    bid = (
        db.query(Bid)
        .options(joinedload(Bid.artwork), joinedload(Bid.bidder))
        .filter(Bid.id == payment_data.bid_id)
        .first()
    )

    if not bid:
        raise HTTPException(status_code=404, detail="Bid not found")

    # Security: Verify bid belongs to current user
    if bid.bidder_id != current_user.id:
        raise HTTPException(status_code=403, detail="You can only create payment for your own bids")

    # Verify bid is winning
    if not bid.is_winning:
        raise HTTPException(status_code=400, detail="Payment can only be created for winning bids")

    # Check if payment already exists
    existing_payment = db.query(Payment).filter(Payment.bid_id == bid.id).first()

    if existing_payment:
        # If payment already succeeded, don't allow recreation
        if existing_payment.status == PaymentStatus.SUCCEEDED:
            raise HTTPException(status_code=400, detail="Payment already completed for this bid")
        # If payment is pending/processing, return existing client secret
        elif existing_payment.status in [
            PaymentStatus.PENDING,
            PaymentStatus.PROCESSING,
        ]:
            payment_intent = StripeService.get_payment_intent(
                existing_payment.stripe_payment_intent_id
            )
            return PaymentIntentResponse(
                client_secret=payment_intent.client_secret,
                payment_intent_id=payment_intent.id,
                payment_id=existing_payment.id,
                amount=existing_payment.amount,
                currency=existing_payment.currency,
            )

    # Create payment intent
    result = StripeService.create_payment_intent(bid=bid, buyer=current_user, db=db)

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
        raise HTTPException(status_code=500, detail="Webhook secret not configured")

    event = StripeService.verify_webhook_signature(
        payload=payload,
        signature=stripe_signature,
        webhook_secret=settings.stripe_webhook_secret,
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
        try:
            from main import sio

            bid = payment.bid
            await sio.emit(
                "payment_completed",
                {
                    "artwork_id": bid.artwork_id,
                    "payment_id": payment.id,
                    "status": "SOLD",
                },
                room=f"artwork_{bid.artwork_id}",
            )
        except Exception as e:
            # Log but don't fail webhook if socket emission fails
            print(f"Socket emission failed: {e}")

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
        try:
            from main import sio

            bid = payment.bid
            await sio.emit(
                "payment_failed",
                {
                    "artwork_id": bid.artwork_id,
                    "payment_id": payment.id,
                    "reason": payment.failure_reason,
                },
                room=f"artwork_{bid.artwork_id}",
            )
        except Exception as e:
            print(f"Socket emission failed: {e}")

    return {"status": "success"}


@router.get("/my-payments", response_model=List[PaymentResponse])
async def get_my_payments(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get all payments for the current user."""
    payments = (
        db.query(Payment)
        .join(Bid)
        .filter(Bid.bidder_id == current_user.id)
        .order_by(Payment.created_at.desc())
        .all()
    )

    return payments


@router.get("/{payment_id}", response_model=PaymentResponse)
async def get_payment(
    payment_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get payment details by ID."""
    payment = (
        db.query(Payment)
        .options(joinedload(Payment.bid).joinedload(Bid.artwork))
        .filter(Payment.id == payment_id)
        .first()
    )

    if not payment:
        raise HTTPException(status_code=404, detail="Payment not found")

    # Security: Only buyer, seller, or admin can view payment
    bid = payment.bid
    artwork = bid.artwork

    is_authorized = (
        current_user.id == bid.bidder_id  # Buyer
        or current_user.id == artwork.seller_id  # Seller
        or current_user.role == "ADMIN"  # Admin
    )

    if not is_authorized:
        raise HTTPException(
            status_code=403, detail="You don't have permission to view this payment"
        )

    return payment


@router.get("/artwork/{artwork_id}", response_model=PaymentResponse)
async def get_artwork_payment(
    artwork_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Get payment for an artwork.

    Authorized users:
    - Buyer (user with winning bid) - can view their own payment (any status)
    - Seller - can view completed payments only
    - Admin - can view all payments
    """
    artwork = db.query(Artwork).filter(Artwork.id == artwork_id).first()

    if not artwork:
        raise HTTPException(status_code=404, detail="Artwork not found")

    # Find payment through bid (eagerly load bid to check bidder)
    payment = (
        db.query(Payment)
        .options(joinedload(Payment.bid))
        .join(Bid)
        .filter(Bid.artwork_id == artwork_id)
        .first()
    )

    if not payment:
        raise HTTPException(status_code=404, detail="No payment found for this artwork")

    # Security check - determine if user is authorized
    is_buyer = current_user.id == payment.bid.bidder_id
    is_seller = current_user.id == artwork.seller_id
    is_admin = current_user.role == "ADMIN"

    # Buyers can see their own payment in any status
    if is_buyer:
        return payment

    # Sellers and admins can only see completed payments
    if (is_seller or is_admin) and payment.status == PaymentStatus.SUCCEEDED:
        return payment

    # If user is seller/admin but payment is not succeeded yet, deny access
    if is_seller or is_admin:
        raise HTTPException(status_code=404, detail="No completed payment found for this artwork")

    # User is not authorized at all
    raise HTTPException(
        status_code=403,
        detail="You don't have permission to view this payment",
    )


@router.get("/health", response_model=Dict[str, Any])
async def stripe_health_check():
    """
    Health check endpoint for Stripe configuration.

    Returns Stripe configuration status without exposing sensitive keys.
    Useful for debugging and monitoring.

    Public endpoint - no authentication required.
    """
    status = StripeValidator.get_stripe_status()

    return {
        "stripe_configured": status["configured"],
        "keys_configured": {
            "secret_key": status["secret_key_set"],
            "publishable_key": status["publishable_key_set"],
            "webhook_secret": status["webhook_secret_set"],
        },
        "ready_for_payments": status["configured"],
        "errors": status["errors"] if not status["configured"] else [],
        "help": "See STRIPE_SETUP_GUIDE.md for configuration instructions",
    }
