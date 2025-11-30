"""Stripe payment service for handling payment operations."""

from typing import Any, Dict

import stripe
from config.settings import settings
from fastapi import HTTPException
from models import Bid, Payment, User
from models.payment import PaymentStatus
from sqlalchemy.orm import Session
from stripe._error import SignatureVerificationError, StripeError

# Initialize Stripe with API key from settings
stripe.api_key = settings.stripe_secret_key


class StripeService:
    """Service for handling Stripe payment operations."""

    @staticmethod
    def create_payment_intent(bid: Bid, buyer: User, db: Session) -> Dict[str, Any]:
        """
        Create a Stripe Payment Intent for a winning bid.

        Args:
            bid: The winning bid object
            buyer: The user making the payment
            db: Database session

        Returns:
            Dictionary with client_secret, payment_intent_id, and payment_id

        Raises:
            HTTPException: If Stripe API call fails
        """
        # Convert amount to cents (Stripe uses smallest currency unit)
        amount_cents = int(bid.amount * 100)

        # Get artwork details for metadata
        artwork = bid.artwork

        try:
            # Create Payment Intent via Stripe API
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
                payment_metadata={
                    "artwork_id": artwork.id,
                    "buyer_id": buyer.id,
                    "seller_id": artwork.seller_id,
                },
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

        except StripeError as e:
            db.rollback()
            raise HTTPException(status_code=400, detail=f"Stripe error: {str(e)}")

    @staticmethod
    def get_payment_intent(payment_intent_id: str) -> stripe.PaymentIntent:
        """
        Retrieve a Payment Intent from Stripe.

        Args:
            payment_intent_id: The Stripe Payment Intent ID

        Returns:
            Stripe PaymentIntent object

        Raises:
            HTTPException: If retrieval fails
        """
        try:
            return stripe.PaymentIntent.retrieve(payment_intent_id)
        except StripeError as e:
            raise HTTPException(
                status_code=400, detail=f"Failed to retrieve payment intent: {str(e)}"
            )

    @staticmethod
    def handle_payment_succeeded(
        payment_intent: stripe.PaymentIntent, db: Session
    ) -> Payment:
        """
        Handle successful payment webhook event.

        Updates payment status to SUCCEEDED and marks artwork as SOLD.

        Args:
            payment_intent: Stripe PaymentIntent object from webhook
            db: Database session

        Returns:
            Updated Payment object

        Raises:
            HTTPException: If payment not found
        """
        # Find payment record
        payment = (
            db.query(Payment)
            .filter(Payment.stripe_payment_intent_id == payment_intent.id)
            .first()
        )

        if not payment:
            raise HTTPException(
                status_code=404,
                detail=f"Payment not found for intent: {payment_intent.id}",
            )

        # Update payment status
        payment.status = PaymentStatus.SUCCEEDED
        payment.stripe_charge_id = (
            payment_intent.charges.data[0].id if payment_intent.charges.data else None
        )

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
        payment_intent: stripe.PaymentIntent, db: Session
    ) -> Payment:
        """
        Handle failed payment webhook event.

        Updates payment status to FAILED and returns artwork to ACTIVE.

        Args:
            payment_intent: Stripe PaymentIntent object from webhook
            db: Database session

        Returns:
            Updated Payment object

        Raises:
            HTTPException: If payment not found
        """
        payment = (
            db.query(Payment)
            .filter(Payment.stripe_payment_intent_id == payment_intent.id)
            .first()
        )

        if not payment:
            raise HTTPException(
                status_code=404,
                detail=f"Payment not found for intent: {payment_intent.id}",
            )

        # Update payment status
        payment.status = PaymentStatus.FAILED
        payment.failure_reason = (
            payment_intent.last_payment_error.message
            if payment_intent.last_payment_error
            else "Unknown error"
        )

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
    def verify_webhook_signature(
        payload: bytes, signature: str, webhook_secret: str
    ) -> stripe.Event:
        """
        Verify webhook signature and construct event.

        SECURITY: CRITICAL for webhook authenticity. Always verify signatures.

        Args:
            payload: Raw request body bytes
            signature: Stripe-Signature header value
            webhook_secret: Webhook secret from Stripe Dashboard

        Returns:
            Verified Stripe Event object

        Raises:
            HTTPException: If verification fails
        """
        try:
            event = stripe.Webhook.construct_event(payload, signature, webhook_secret)
            return event
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid payload")
        except SignatureVerificationError:
            raise HTTPException(status_code=400, detail="Invalid signature")
