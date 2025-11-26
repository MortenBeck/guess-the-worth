"""
Unit tests for StripeService.
Tests payment intent creation, webhook handling, and error scenarios.
"""

from unittest.mock import MagicMock, patch
import pytest
from fastapi import HTTPException
from stripe._error import StripeError, CardError, InvalidRequestError, SignatureVerificationError

from models import Payment, Bid, User, Artwork
from models.payment import PaymentStatus
from models.artwork import ArtworkStatus
from services.stripe_service import StripeService


@pytest.fixture
def winning_bid(db_session, artwork, buyer_user) -> Bid:
    """Create a winning bid for payment testing."""
    bid = Bid(
        artwork_id=artwork.id,
        bidder_id=buyer_user.id,
        amount=100.0,
        is_winning=True
    )
    db_session.add(bid)
    db_session.commit()
    db_session.refresh(bid)
    return bid


@pytest.fixture
def mock_stripe_payment_intent():
    """Create a mock Stripe PaymentIntent object."""
    mock_intent = MagicMock()
    mock_intent.id = "pi_test123"
    mock_intent.client_secret = "pi_test123_secret_abc"
    mock_intent.amount = 10000  # $100.00 in cents
    mock_intent.currency = "usd"
    mock_intent.status = "requires_payment_method"
    mock_intent.charges.data = []
    return mock_intent


@pytest.fixture
def mock_stripe_charge():
    """Create a mock Stripe Charge object."""
    mock_charge = MagicMock()
    mock_charge.id = "ch_test123"
    return mock_charge


class TestStripeServiceCreatePaymentIntent:
    """Tests for StripeService.create_payment_intent."""

    @patch('stripe.PaymentIntent.create')
    def test_create_payment_intent_success(
        self,
        mock_stripe_create,
        db_session,
        winning_bid,
        buyer_user,
        mock_stripe_payment_intent
    ):
        """Test successful payment intent creation."""
        mock_stripe_create.return_value = mock_stripe_payment_intent

        result = StripeService.create_payment_intent(
            bid=winning_bid,
            buyer=buyer_user,
            db=db_session
        )

        # Verify Stripe API called with correct parameters
        mock_stripe_create.assert_called_once()
        call_args = mock_stripe_create.call_args
        assert call_args.kwargs['amount'] == 10000  # $100.00 in cents
        assert call_args.kwargs['currency'] == "usd"
        assert call_args.kwargs['payment_method_types'] == ["card"]
        assert str(winning_bid.id) in call_args.kwargs['metadata']['bid_id']

        # Verify result
        assert result['client_secret'] == "pi_test123_secret_abc"
        assert result['payment_intent_id'] == "pi_test123"
        assert result['amount'] == 100.0
        assert result['currency'] == "usd"
        assert 'payment_id' in result

        # Verify database record created
        payment = db_session.query(Payment).filter(
            Payment.stripe_payment_intent_id == "pi_test123"
        ).first()
        assert payment is not None
        assert payment.status == PaymentStatus.PENDING
        assert payment.amount == 100.0
        assert payment.bid_id == winning_bid.id

    @patch('stripe.PaymentIntent.create')
    def test_create_payment_intent_stripe_error(
        self,
        mock_stripe_create,
        db_session,
        winning_bid,
        buyer_user
    ):
        """Test handling of Stripe API errors."""
        mock_stripe_create.side_effect = CardError(
            message="Your card was declined",
            param="card",
            code="card_declined"
        )

        with pytest.raises(HTTPException) as exc_info:
            StripeService.create_payment_intent(
                bid=winning_bid,
                buyer=buyer_user,
                db=db_session
            )

        assert exc_info.value.status_code == 400
        assert "Stripe error" in exc_info.value.detail

        # Verify no payment record created
        payment_count = db_session.query(Payment).count()
        assert payment_count == 0

    @patch('stripe.PaymentIntent.create')
    def test_create_payment_intent_includes_metadata(
        self,
        mock_stripe_create,
        db_session,
        winning_bid,
        buyer_user,
        mock_stripe_payment_intent
    ):
        """Test that payment intent includes correct metadata."""
        mock_stripe_create.return_value = mock_stripe_payment_intent

        StripeService.create_payment_intent(
            bid=winning_bid,
            buyer=buyer_user,
            db=db_session
        )

        call_args = mock_stripe_create.call_args
        metadata = call_args.kwargs['metadata']

        assert metadata['bid_id'] == str(winning_bid.id)
        assert metadata['artwork_id'] == str(winning_bid.artwork.id)
        assert metadata['buyer_id'] == str(buyer_user.id)
        assert metadata['buyer_email'] == buyer_user.email
        assert metadata['artwork_title'] == winning_bid.artwork.title

    @patch('stripe.PaymentIntent.create')
    def test_create_payment_intent_invalid_request_error(
        self,
        mock_stripe_create,
        db_session,
        winning_bid,
        buyer_user
    ):
        """Test handling of InvalidRequestError from Stripe."""
        mock_stripe_create.side_effect = InvalidRequestError(
            message="Invalid currency",
            param="currency"
        )

        with pytest.raises(HTTPException) as exc_info:
            StripeService.create_payment_intent(
                bid=winning_bid,
                buyer=buyer_user,
                db=db_session
            )

        assert exc_info.value.status_code == 400
        assert "Stripe error" in exc_info.value.detail

    @patch('stripe.PaymentIntent.create')
    def test_create_payment_intent_includes_receipt_email(
        self,
        mock_stripe_create,
        db_session,
        winning_bid,
        buyer_user,
        mock_stripe_payment_intent
    ):
        """Test that payment intent includes receipt email."""
        mock_stripe_create.return_value = mock_stripe_payment_intent

        StripeService.create_payment_intent(
            bid=winning_bid,
            buyer=buyer_user,
            db=db_session
        )

        call_args = mock_stripe_create.call_args
        assert call_args.kwargs['receipt_email'] == buyer_user.email

    @patch('stripe.PaymentIntent.create')
    def test_create_payment_intent_amount_conversion(
        self,
        mock_stripe_create,
        db_session,
        winning_bid,
        buyer_user,
        mock_stripe_payment_intent
    ):
        """Test correct conversion of amount to cents."""
        winning_bid.amount = 123.45
        db_session.commit()

        mock_stripe_create.return_value = mock_stripe_payment_intent

        StripeService.create_payment_intent(
            bid=winning_bid,
            buyer=buyer_user,
            db=db_session
        )

        call_args = mock_stripe_create.call_args
        assert call_args.kwargs['amount'] == 12345  # 123.45 * 100


class TestStripeServiceGetPaymentIntent:
    """Tests for StripeService.get_payment_intent."""

    @patch('stripe.PaymentIntent.retrieve')
    def test_get_payment_intent_success(
        self,
        mock_stripe_retrieve,
        mock_stripe_payment_intent
    ):
        """Test successful payment intent retrieval."""
        mock_stripe_retrieve.return_value = mock_stripe_payment_intent

        result = StripeService.get_payment_intent("pi_test123")

        mock_stripe_retrieve.assert_called_once_with("pi_test123")
        assert result.id == "pi_test123"

    @patch('stripe.PaymentIntent.retrieve')
    def test_get_payment_intent_not_found(self, mock_stripe_retrieve):
        """Test handling of payment intent not found."""
        mock_stripe_retrieve.side_effect = InvalidRequestError(
            message="No such payment intent",
            param="id"
        )

        with pytest.raises(HTTPException) as exc_info:
            StripeService.get_payment_intent("pi_nonexistent")

        assert exc_info.value.status_code == 400
        assert "Failed to retrieve payment intent" in exc_info.value.detail


class TestStripeServiceHandlePaymentSucceeded:
    """Tests for StripeService.handle_payment_succeeded."""

    def test_handle_payment_succeeded(
        self,
        db_session,
        winning_bid,
        mock_stripe_payment_intent,
        mock_stripe_charge
    ):
        """Test successful payment webhook handling."""
        # Create payment record
        payment = Payment(
            bid_id=winning_bid.id,
            stripe_payment_intent_id="pi_test123",
            amount=100.0,
            currency="usd",
            status=PaymentStatus.PENDING
        )
        db_session.add(payment)
        db_session.commit()

        # Mock charge data
        mock_stripe_payment_intent.id = "pi_test123"
        mock_stripe_payment_intent.charges.data = [mock_stripe_charge]

        # Handle webhook
        result = StripeService.handle_payment_succeeded(
            mock_stripe_payment_intent,
            db_session
        )

        # Verify payment updated
        assert result.status == PaymentStatus.SUCCEEDED
        assert result.stripe_charge_id == "ch_test123"

        # Verify artwork marked as SOLD
        db_session.refresh(winning_bid.artwork)
        assert winning_bid.artwork.status == "SOLD"

    def test_handle_payment_succeeded_payment_not_found(
        self,
        db_session,
        mock_stripe_payment_intent
    ):
        """Test webhook for non-existent payment."""
        mock_stripe_payment_intent.id = "pi_nonexistent"

        with pytest.raises(HTTPException) as exc_info:
            StripeService.handle_payment_succeeded(
                mock_stripe_payment_intent,
                db_session
            )

        assert exc_info.value.status_code == 404
        assert "Payment not found" in exc_info.value.detail

    def test_handle_payment_succeeded_no_charges(
        self,
        db_session,
        winning_bid,
        mock_stripe_payment_intent
    ):
        """Test payment success with no charge data."""
        payment = Payment(
            bid_id=winning_bid.id,
            stripe_payment_intent_id="pi_test123",
            amount=100.0,
            currency="usd",
            status=PaymentStatus.PENDING
        )
        db_session.add(payment)
        db_session.commit()

        mock_stripe_payment_intent.id = "pi_test123"
        mock_stripe_payment_intent.charges.data = []

        result = StripeService.handle_payment_succeeded(
            mock_stripe_payment_intent,
            db_session
        )

        assert result.status == PaymentStatus.SUCCEEDED
        assert result.stripe_charge_id is None

    def test_handle_payment_succeeded_idempotent(
        self,
        db_session,
        winning_bid,
        mock_stripe_payment_intent,
        mock_stripe_charge
    ):
        """Test that handling payment succeeded is idempotent."""
        payment = Payment(
            bid_id=winning_bid.id,
            stripe_payment_intent_id="pi_test123",
            amount=100.0,
            currency="usd",
            status=PaymentStatus.PENDING
        )
        db_session.add(payment)
        db_session.commit()

        mock_stripe_payment_intent.id = "pi_test123"
        mock_stripe_payment_intent.charges.data = [mock_stripe_charge]

        # Process webhook twice
        result1 = StripeService.handle_payment_succeeded(
            mock_stripe_payment_intent,
            db_session
        )
        result2 = StripeService.handle_payment_succeeded(
            mock_stripe_payment_intent,
            db_session
        )

        # Should handle gracefully
        assert result1.status == PaymentStatus.SUCCEEDED
        assert result2.status == PaymentStatus.SUCCEEDED
        assert result1.id == result2.id


class TestStripeServiceHandlePaymentFailed:
    """Tests for StripeService.handle_payment_failed."""

    def test_handle_payment_failed(
        self,
        db_session,
        winning_bid,
        mock_stripe_payment_intent
    ):
        """Test failed payment webhook handling."""
        # Create payment record
        payment = Payment(
            bid_id=winning_bid.id,
            stripe_payment_intent_id="pi_test123",
            amount=100.0,
            currency="usd",
            status=PaymentStatus.PROCESSING
        )
        db_session.add(payment)

        # Update artwork to PENDING_PAYMENT
        winning_bid.artwork.status = "PENDING_PAYMENT"
        db_session.commit()

        # Mock payment error
        mock_error = MagicMock()
        mock_error.message = "Insufficient funds"
        mock_stripe_payment_intent.id = "pi_test123"
        mock_stripe_payment_intent.last_payment_error = mock_error

        # Handle webhook
        result = StripeService.handle_payment_failed(
            mock_stripe_payment_intent,
            db_session
        )

        # Verify payment updated
        assert result.status == PaymentStatus.FAILED
        assert result.failure_reason == "Insufficient funds"

        # Verify artwork returned to ACTIVE
        db_session.refresh(winning_bid.artwork)
        assert winning_bid.artwork.status == "ACTIVE"

        # Verify bid no longer winning
        db_session.refresh(winning_bid)
        assert winning_bid.is_winning is False

    def test_handle_payment_failed_unknown_error(
        self,
        db_session,
        winning_bid,
        mock_stripe_payment_intent
    ):
        """Test failed payment with no error message."""
        payment = Payment(
            bid_id=winning_bid.id,
            stripe_payment_intent_id="pi_test123",
            amount=100.0,
            currency="usd",
            status=PaymentStatus.PROCESSING
        )
        db_session.add(payment)
        db_session.commit()

        mock_stripe_payment_intent.id = "pi_test123"
        mock_stripe_payment_intent.last_payment_error = None

        result = StripeService.handle_payment_failed(
            mock_stripe_payment_intent,
            db_session
        )

        assert result.status == PaymentStatus.FAILED
        assert result.failure_reason == "Unknown error"

    def test_handle_payment_failed_payment_not_found(
        self,
        db_session,
        mock_stripe_payment_intent
    ):
        """Test webhook for non-existent payment."""
        mock_stripe_payment_intent.id = "pi_nonexistent"

        with pytest.raises(HTTPException) as exc_info:
            StripeService.handle_payment_failed(
                mock_stripe_payment_intent,
                db_session
            )

        assert exc_info.value.status_code == 404
        assert "Payment not found" in exc_info.value.detail

    def test_handle_payment_failed_idempotent(
        self,
        db_session,
        winning_bid,
        mock_stripe_payment_intent
    ):
        """Test that handling payment failed is idempotent."""
        payment = Payment(
            bid_id=winning_bid.id,
            stripe_payment_intent_id="pi_test123",
            amount=100.0,
            currency="usd",
            status=PaymentStatus.PROCESSING
        )
        db_session.add(payment)
        winning_bid.artwork.status = "PENDING_PAYMENT"
        db_session.commit()

        mock_error = MagicMock()
        mock_error.message = "Card declined"
        mock_stripe_payment_intent.id = "pi_test123"
        mock_stripe_payment_intent.last_payment_error = mock_error

        # Process webhook twice
        result1 = StripeService.handle_payment_failed(
            mock_stripe_payment_intent,
            db_session
        )
        result2 = StripeService.handle_payment_failed(
            mock_stripe_payment_intent,
            db_session
        )

        # Should handle gracefully
        assert result1.status == PaymentStatus.FAILED
        assert result2.status == PaymentStatus.FAILED
        assert result1.id == result2.id


class TestStripeServiceVerifyWebhookSignature:
    """Tests for StripeService.verify_webhook_signature."""

    @patch('stripe.Webhook.construct_event')
    def test_verify_webhook_signature_success(self, mock_construct_event):
        """Test successful webhook signature verification."""
        mock_event = MagicMock()
        mock_event.type = "payment_intent.succeeded"
        mock_construct_event.return_value = mock_event

        payload = b'{"type": "payment_intent.succeeded"}'
        signature = "t=123,v1=abc"
        secret = "whsec_test"

        result = StripeService.verify_webhook_signature(
            payload, signature, secret
        )

        mock_construct_event.assert_called_once_with(payload, signature, secret)
        assert result.type == "payment_intent.succeeded"

    @patch('stripe.Webhook.construct_event')
    def test_verify_webhook_signature_invalid_payload(self, mock_construct_event):
        """Test webhook with invalid payload."""
        mock_construct_event.side_effect = ValueError("Invalid payload")

        with pytest.raises(HTTPException) as exc_info:
            StripeService.verify_webhook_signature(
                b'invalid', "signature", "secret"
            )

        assert exc_info.value.status_code == 400
        assert exc_info.value.detail == "Invalid payload"

    @patch('stripe.Webhook.construct_event')
    def test_verify_webhook_signature_invalid_signature(self, mock_construct_event):
        """Test webhook with invalid signature."""
        mock_construct_event.side_effect = SignatureVerificationError(
            message="Invalid signature",
            sig_header="invalid"
        )

        with pytest.raises(HTTPException) as exc_info:
            StripeService.verify_webhook_signature(
                b'payload', "invalid_signature", "secret"
            )

        assert exc_info.value.status_code == 400
        assert exc_info.value.detail == "Invalid signature"
