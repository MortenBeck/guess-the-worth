"""
Integration tests for payment API endpoints.
Tests complete payment workflows, authentication, and edge cases.
"""

from unittest.mock import MagicMock, patch

import pytest
from fastapi.testclient import TestClient

from models import Bid, Payment
from models.payment import PaymentStatus
from tests.conftest import create_auth_header


@pytest.fixture
def winning_bid(db_session, artwork, buyer_user):
    """Create a winning bid for payment testing."""
    bid = Bid(artwork_id=artwork.id, bidder_id=buyer_user.id, amount=100.0, is_winning=True)
    db_session.add(bid)
    db_session.commit()
    db_session.refresh(bid)
    return bid


@pytest.fixture
def non_winning_bid(db_session, artwork, buyer_user):
    """Create a non-winning bid."""
    bid = Bid(artwork_id=artwork.id, bidder_id=buyer_user.id, amount=50.0, is_winning=False)
    db_session.add(bid)
    db_session.commit()
    db_session.refresh(bid)
    return bid


@pytest.fixture
def existing_payment(db_session, winning_bid):
    """Create an existing payment record."""
    payment = Payment(
        bid_id=winning_bid.id,
        stripe_payment_intent_id="pi_existing123",
        amount=100.0,
        currency="usd",
        status=PaymentStatus.PENDING,
    )
    db_session.add(payment)
    db_session.commit()
    db_session.refresh(payment)
    return payment


@pytest.fixture
def mock_stripe_payment_intent():
    """Mock Stripe PaymentIntent."""
    mock_intent = MagicMock()
    mock_intent.id = "pi_test123"
    mock_intent.client_secret = "pi_test123_secret_abc"
    mock_intent.amount = 10000
    mock_intent.currency = "usd"
    mock_intent.charges.data = []
    return mock_intent


class TestCreatePaymentIntent:
    """Tests for POST /payments/create-intent endpoint."""

    @patch("services.stripe_service.StripeService.create_payment_intent")
    @patch("services.audit_service.AuditService.log_action")
    def test_create_payment_intent_success(
        self,
        mock_audit_log,
        mock_create_intent,
        client: TestClient,
        db_session,
        winning_bid,
        buyer_user,
        buyer_token,
    ):
        """Test successful payment intent creation."""
        mock_create_intent.return_value = {
            "client_secret": "pi_test123_secret_abc",
            "payment_intent_id": "pi_test123",
            "amount": 100.0,
            "currency": "usd",
            "payment_id": 1,
        }

        response = client.post(
            "/api/payments/create-intent",
            json={"bid_id": winning_bid.id},
            headers=create_auth_header(buyer_token),
        )

        assert response.status_code == 200
        data = response.json()
        assert data["client_secret"] == "pi_test123_secret_abc"
        assert data["payment_intent_id"] == "pi_test123"
        assert float(data["amount"]) == 100.0
        assert data["currency"] == "usd"

        # Verify artwork status updated
        db_session.refresh(winning_bid.artwork)
        assert winning_bid.artwork.status == "PENDING_PAYMENT"

        # Verify audit log called
        mock_audit_log.assert_called_once()
        call_args = mock_audit_log.call_args
        assert call_args.kwargs["action"] == "payment_intent_created"
        assert call_args.kwargs["resource_type"] == "payment"

    def test_create_payment_intent_unauthorized(self, client: TestClient, winning_bid):
        """Test payment intent creation without authentication."""
        response = client.post("/api/payments/create-intent", json={"bid_id": winning_bid.id})

        assert response.status_code == 401

    def test_create_payment_intent_wrong_user(self, client: TestClient, winning_bid, seller_token):
        """Test payment intent creation by non-bid owner."""
        response = client.post(
            "/api/payments/create-intent",
            json={"bid_id": winning_bid.id},
            headers=create_auth_header(seller_token),
        )

        assert response.status_code == 403
        assert "your own bids" in response.json()["detail"]

    def test_create_payment_intent_bid_not_found(self, client: TestClient, buyer_token):
        """Test payment intent creation for non-existent bid."""
        response = client.post(
            "/api/payments/create-intent",
            json={"bid_id": 99999},
            headers=create_auth_header(buyer_token),
        )

        assert response.status_code == 404
        assert "Bid not found" in response.json()["detail"]

    def test_create_payment_intent_not_winning(
        self, client: TestClient, non_winning_bid, buyer_token
    ):
        """Test payment intent creation for non-winning bid."""
        response = client.post(
            "/api/payments/create-intent",
            json={"bid_id": non_winning_bid.id},
            headers=create_auth_header(buyer_token),
        )

        assert response.status_code == 400
        assert "winning bids" in response.json()["detail"]

    @patch("services.stripe_service.StripeService.get_payment_intent")
    def test_create_payment_intent_already_exists_pending(
        self,
        mock_get_intent,
        client: TestClient,
        winning_bid,
        buyer_token,
        existing_payment,
        mock_stripe_payment_intent,
    ):
        """Test payment intent creation when payment already exists (pending)."""
        mock_get_intent.return_value = mock_stripe_payment_intent

        response = client.post(
            "/api/payments/create-intent",
            json={"bid_id": winning_bid.id},
            headers=create_auth_header(buyer_token),
        )

        assert response.status_code == 200
        data = response.json()
        # Should return existing payment intent
        assert data["payment_id"] == existing_payment.id

    @patch("services.stripe_service.StripeService.get_payment_intent")
    def test_create_payment_intent_already_exists_processing(
        self,
        mock_get_intent,
        client: TestClient,
        db_session,
        winning_bid,
        buyer_token,
        mock_stripe_payment_intent,
    ):
        """Test payment intent creation when payment in PROCESSING status."""
        # Create payment with PROCESSING status
        payment = Payment(
            bid_id=winning_bid.id,
            stripe_payment_intent_id="pi_processing123",
            amount=100.0,
            currency="usd",
            status=PaymentStatus.PROCESSING,
        )
        db_session.add(payment)
        db_session.commit()

        mock_get_intent.return_value = mock_stripe_payment_intent

        response = client.post(
            "/api/payments/create-intent",
            json={"bid_id": winning_bid.id},
            headers=create_auth_header(buyer_token),
        )

        assert response.status_code == 200
        data = response.json()
        # Should return existing payment intent
        assert data["payment_id"] == payment.id

    def test_create_payment_intent_already_succeeded(
        self, client: TestClient, winning_bid, buyer_token, db_session
    ):
        """Test payment intent creation when payment already completed."""
        # Create succeeded payment
        payment = Payment(
            bid_id=winning_bid.id,
            stripe_payment_intent_id="pi_succeeded123",
            amount=100.0,
            currency="usd",
            status=PaymentStatus.SUCCEEDED,
        )
        db_session.add(payment)
        db_session.commit()

        response = client.post(
            "/api/payments/create-intent",
            json={"bid_id": winning_bid.id},
            headers=create_auth_header(buyer_token),
        )

        assert response.status_code == 400
        assert "already completed" in response.json()["detail"]


class TestStripeWebhook:
    """
    Tests for POST /payments/webhook endpoint.

    Note: Webhook handler logic (handle_payment_succeeded, handle_payment_failed,
    verify_webhook_signature) is comprehensively tested in test_stripe_service.py
    unit tests. Integration testing webhooks with mocks is complex due to async
    handling, so we focus on basic endpoint validation here.
    """

    def test_webhook_no_secret_configured(self, client: TestClient):
        """Test webhook when webhook secret not configured."""
        with patch("config.settings.settings") as mock_settings:
            mock_settings.stripe_webhook_secret = None

            response = client.post(
                "/api/payments/webhook",
                json={"type": "payment_intent.succeeded"},
                headers={"stripe-signature": "test_signature"},
            )

            assert response.status_code == 500
            assert "not configured" in response.json()["detail"]

    @patch("services.stripe_service.StripeService.verify_webhook_signature")
    @patch("services.stripe_service.StripeService.handle_payment_succeeded")
    @patch("services.audit_service.AuditService.log_action")
    def test_webhook_payment_succeeded(
        self,
        mock_audit_log,
        mock_handle_succeeded,
        mock_verify_webhook,
        client: TestClient,
        db_session,
        winning_bid,
    ):
        """Test webhook handling for payment_intent.succeeded event."""
        # Create mock payment with bid relationship
        payment = Payment(
            bid_id=winning_bid.id,
            stripe_payment_intent_id="pi_test123",
            amount=100.0,
            currency="usd",
            status=PaymentStatus.SUCCEEDED,
        )
        db_session.add(payment)
        db_session.commit()
        db_session.refresh(payment)

        # Load relationships
        payment.bid = winning_bid
        mock_handle_succeeded.return_value = payment

        # Mock webhook event
        mock_event = MagicMock()
        mock_event.type = "payment_intent.succeeded"
        mock_payment_intent = MagicMock()
        mock_payment_intent.id = "pi_test123"
        mock_event.data.object = mock_payment_intent
        mock_verify_webhook.return_value = mock_event

        with patch("config.settings.settings.stripe_webhook_secret", "whsec_test123"):
            with patch("main.sio"):
                response = client.post(
                    "/api/payments/webhook",
                    json={"type": "payment_intent.succeeded"},
                    headers={"stripe-signature": "test_sig"},
                )

        assert response.status_code == 200
        assert response.json()["status"] == "success"
        mock_handle_succeeded.assert_called_once_with(mock_payment_intent, db_session)
        mock_audit_log.assert_called_once()

        # Verify audit log details
        call_args = mock_audit_log.call_args
        assert call_args.kwargs["action"] == "payment_succeeded"
        assert call_args.kwargs["resource_type"] == "payment"
        assert call_args.kwargs["resource_id"] == payment.id

    @patch("services.stripe_service.StripeService.verify_webhook_signature")
    @patch("services.stripe_service.StripeService.handle_payment_succeeded")
    @patch("services.audit_service.AuditService.log_action")
    def test_webhook_payment_succeeded_with_socket_emission(
        self,
        mock_audit_log,
        mock_handle_succeeded,
        mock_verify_webhook,
        client: TestClient,
        db_session,
        winning_bid,
    ):
        """Test webhook with successful socket emission."""
        payment = Payment(
            bid_id=winning_bid.id,
            stripe_payment_intent_id="pi_test123",
            amount=100.0,
            currency="usd",
            status=PaymentStatus.SUCCEEDED,
        )
        db_session.add(payment)
        db_session.commit()
        db_session.refresh(payment)

        payment.bid = winning_bid
        mock_handle_succeeded.return_value = payment

        mock_event = MagicMock()
        mock_event.type = "payment_intent.succeeded"
        mock_payment_intent = MagicMock()
        mock_payment_intent.id = "pi_test123"
        mock_event.data.object = mock_payment_intent
        mock_verify_webhook.return_value = mock_event

        with patch("config.settings.settings.stripe_webhook_secret", "whsec_test123"):
            with patch("main.sio") as mock_sio:
                mock_sio.emit = MagicMock()

                response = client.post(
                    "/api/payments/webhook",
                    json={"type": "payment_intent.succeeded"},
                    headers={"stripe-signature": "test_sig"},
                )

                # Verify socket emission was called
                mock_sio.emit.assert_called_once()
                call_args = mock_sio.emit.call_args
                assert call_args[0][0] == "payment_completed"
                assert call_args[0][1]["artwork_id"] == winning_bid.artwork_id
                assert call_args[0][1]["payment_id"] == payment.id
                assert call_args[0][1]["status"] == "SOLD"

        assert response.status_code == 200

    @patch("services.stripe_service.StripeService.verify_webhook_signature")
    @patch("services.stripe_service.StripeService.handle_payment_succeeded")
    @patch("services.audit_service.AuditService.log_action")
    def test_webhook_payment_succeeded_socket_emission_fails(
        self,
        mock_audit_log,
        mock_handle_succeeded,
        mock_verify_webhook,
        client: TestClient,
        db_session,
        winning_bid,
    ):
        """Test webhook when socket emission fails - should still succeed."""
        payment = Payment(
            bid_id=winning_bid.id,
            stripe_payment_intent_id="pi_test123",
            amount=100.0,
            currency="usd",
            status=PaymentStatus.SUCCEEDED,
        )
        db_session.add(payment)
        db_session.commit()
        db_session.refresh(payment)

        payment.bid = winning_bid
        mock_handle_succeeded.return_value = payment

        mock_event = MagicMock()
        mock_event.type = "payment_intent.succeeded"
        mock_payment_intent = MagicMock()
        mock_payment_intent.id = "pi_test123"
        mock_event.data.object = mock_payment_intent
        mock_verify_webhook.return_value = mock_event

        with patch("config.settings.settings.stripe_webhook_secret", "whsec_test123"):
            with patch("main.sio") as mock_sio:
                # Make socket emission fail
                mock_sio.emit.side_effect = Exception("Socket error")

                response = client.post(
                    "/api/payments/webhook",
                    json={"type": "payment_intent.succeeded"},
                    headers={"stripe-signature": "test_sig"},
                )

        # Should still return success even if socket fails
        assert response.status_code == 200
        mock_handle_succeeded.assert_called_once()
        mock_audit_log.assert_called_once()

    @patch("services.stripe_service.StripeService.verify_webhook_signature")
    @patch("services.stripe_service.StripeService.handle_payment_failed")
    @patch("services.audit_service.AuditService.log_action")
    def test_webhook_payment_failed(
        self,
        mock_audit_log,
        mock_handle_failed,
        mock_verify_webhook,
        client: TestClient,
        db_session,
        winning_bid,
    ):
        """Test webhook handling for payment_intent.payment_failed event."""
        payment = Payment(
            bid_id=winning_bid.id,
            stripe_payment_intent_id="pi_test123",
            amount=100.0,
            currency="usd",
            status=PaymentStatus.FAILED,
            failure_reason="card_declined",
        )
        db_session.add(payment)
        db_session.commit()
        db_session.refresh(payment)

        payment.bid = winning_bid
        mock_handle_failed.return_value = payment

        mock_event = MagicMock()
        mock_event.type = "payment_intent.payment_failed"
        mock_payment_intent = MagicMock()
        mock_payment_intent.id = "pi_test123"
        mock_event.data.object = mock_payment_intent
        mock_verify_webhook.return_value = mock_event

        with patch("config.settings.settings.stripe_webhook_secret", "whsec_test123"):
            with patch("main.sio"):
                response = client.post(
                    "/api/payments/webhook",
                    json={"type": "payment_intent.payment_failed"},
                    headers={"stripe-signature": "test_sig"},
                )

        assert response.status_code == 200
        assert response.json()["status"] == "success"
        mock_handle_failed.assert_called_once_with(mock_payment_intent, db_session)
        mock_audit_log.assert_called_once()

        # Verify audit log details
        call_args = mock_audit_log.call_args
        assert call_args.kwargs["action"] == "payment_failed"
        assert call_args.kwargs["resource_type"] == "payment"
        assert call_args.kwargs["resource_id"] == payment.id

    @patch("services.stripe_service.StripeService.verify_webhook_signature")
    @patch("services.stripe_service.StripeService.handle_payment_failed")
    @patch("services.audit_service.AuditService.log_action")
    def test_webhook_payment_failed_with_socket_emission(
        self,
        mock_audit_log,
        mock_handle_failed,
        mock_verify_webhook,
        client: TestClient,
        db_session,
        winning_bid,
    ):
        """Test webhook failed event with successful socket emission."""
        payment = Payment(
            bid_id=winning_bid.id,
            stripe_payment_intent_id="pi_test123",
            amount=100.0,
            currency="usd",
            status=PaymentStatus.FAILED,
            failure_reason="insufficient_funds",
        )
        db_session.add(payment)
        db_session.commit()
        db_session.refresh(payment)

        payment.bid = winning_bid
        mock_handle_failed.return_value = payment

        mock_event = MagicMock()
        mock_event.type = "payment_intent.payment_failed"
        mock_payment_intent = MagicMock()
        mock_payment_intent.id = "pi_test123"
        mock_event.data.object = mock_payment_intent
        mock_verify_webhook.return_value = mock_event

        with patch("config.settings.settings.stripe_webhook_secret", "whsec_test123"):
            with patch("main.sio") as mock_sio:
                mock_sio.emit = MagicMock()

                response = client.post(
                    "/api/payments/webhook",
                    json={"type": "payment_intent.payment_failed"},
                    headers={"stripe-signature": "test_sig"},
                )

                # Verify socket emission was called
                mock_sio.emit.assert_called_once()
                call_args = mock_sio.emit.call_args
                assert call_args[0][0] == "payment_failed"
                assert call_args[0][1]["artwork_id"] == winning_bid.artwork_id
                assert call_args[0][1]["payment_id"] == payment.id
                assert call_args[0][1]["reason"] == "insufficient_funds"

        assert response.status_code == 200

    @patch("services.stripe_service.StripeService.verify_webhook_signature")
    @patch("services.stripe_service.StripeService.handle_payment_failed")
    @patch("services.audit_service.AuditService.log_action")
    def test_webhook_payment_failed_socket_emission_fails(
        self,
        mock_audit_log,
        mock_handle_failed,
        mock_verify_webhook,
        client: TestClient,
        db_session,
        winning_bid,
    ):
        """Test webhook failed event when socket emission fails -
        should still succeed."""
        payment = Payment(
            bid_id=winning_bid.id,
            stripe_payment_intent_id="pi_test123",
            amount=100.0,
            currency="usd",
            status=PaymentStatus.FAILED,
            failure_reason="card_declined",
        )
        db_session.add(payment)
        db_session.commit()
        db_session.refresh(payment)

        payment.bid = winning_bid
        mock_handle_failed.return_value = payment

        mock_event = MagicMock()
        mock_event.type = "payment_intent.payment_failed"
        mock_payment_intent = MagicMock()
        mock_payment_intent.id = "pi_test123"
        mock_event.data.object = mock_payment_intent
        mock_verify_webhook.return_value = mock_event

        with patch("config.settings.settings.stripe_webhook_secret", "whsec_test123"):
            with patch("main.sio") as mock_sio:
                # Make socket emission fail
                mock_sio.emit.side_effect = Exception("Socket connection lost")

                response = client.post(
                    "/api/payments/webhook",
                    json={"type": "payment_intent.payment_failed"},
                    headers={"stripe-signature": "test_sig"},
                )

        # Should still return success even if socket fails
        assert response.status_code == 200
        mock_handle_failed.assert_called_once()
        mock_audit_log.assert_called_once()


class TestGetMyPayments:
    """Tests for GET /payments/my-payments endpoint."""

    def test_get_my_payments_success(
        self, client: TestClient, db_session, buyer_user, buyer_token, winning_bid
    ):
        """Test retrieving user's payments."""
        # Create payments
        payment1 = Payment(
            bid_id=winning_bid.id,
            stripe_payment_intent_id="pi_1",
            amount=100.0,
            currency="usd",
            status=PaymentStatus.SUCCEEDED,
        )
        db_session.add(payment1)
        db_session.commit()

        response = client.get("/api/payments/my-payments", headers=create_auth_header(buyer_token))

        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["amount"] == "100.00"

    def test_get_my_payments_empty(self, client: TestClient, buyer_token):
        """Test retrieving payments when user has none."""
        response = client.get("/api/payments/my-payments", headers=create_auth_header(buyer_token))

        assert response.status_code == 200
        assert response.json() == []

    def test_get_my_payments_unauthorized(self, client: TestClient):
        """Test retrieving payments without authentication."""
        response = client.get("/api/payments/my-payments")

        assert response.status_code == 401


class TestGetPaymentById:
    """Tests for GET /payments/{payment_id} endpoint."""

    def test_get_payment_as_buyer(self, client: TestClient, db_session, winning_bid, buyer_token):
        """Test buyer retrieving their payment."""
        payment = Payment(
            bid_id=winning_bid.id,
            stripe_payment_intent_id="pi_test123",
            amount=100.0,
            currency="usd",
            status=PaymentStatus.SUCCEEDED,
        )
        db_session.add(payment)
        db_session.commit()

        response = client.get(
            f"/api/payments/{payment.id}", headers=create_auth_header(buyer_token)
        )

        assert response.status_code == 200
        data = response.json()
        assert data["id"] == payment.id
        assert data["amount"] == "100.00"

    def test_get_payment_as_seller(self, client: TestClient, db_session, winning_bid, seller_token):
        """Test seller retrieving payment for their artwork."""
        payment = Payment(
            bid_id=winning_bid.id,
            stripe_payment_intent_id="pi_test123",
            amount=100.0,
            currency="usd",
            status=PaymentStatus.SUCCEEDED,
        )
        db_session.add(payment)
        db_session.commit()

        response = client.get(
            f"/api/payments/{payment.id}", headers=create_auth_header(seller_token)
        )

        assert response.status_code == 200

    def test_get_payment_as_admin(self, client: TestClient, db_session, winning_bid, admin_token):
        """Test admin retrieving any payment."""
        payment = Payment(
            bid_id=winning_bid.id,
            stripe_payment_intent_id="pi_test123",
            amount=100.0,
            currency="usd",
            status=PaymentStatus.SUCCEEDED,
        )
        db_session.add(payment)
        db_session.commit()

        response = client.get(
            f"/api/payments/{payment.id}", headers=create_auth_header(admin_token)
        )

        assert response.status_code == 200

    def test_get_payment_unauthorized_user(self, client: TestClient, db_session, winning_bid):
        """Test unauthorized user cannot view payment."""
        from models.user import User

        # Create another user
        other_user = User(auth0_sub="auth0|other123")
        other_user.email = "other@test.com"
        other_user.name = "Other User"
        other_user.role = "BUYER"
        db_session.add(other_user)

        payment = Payment(
            bid_id=winning_bid.id,
            stripe_payment_intent_id="pi_test123",
            amount=100.0,
            currency="usd",
            status=PaymentStatus.SUCCEEDED,
        )
        db_session.add(payment)
        db_session.commit()

        # Generate token for other user
        from datetime import timedelta

        from services.jwt_service import JWTService

        other_token = JWTService.create_access_token(
            data={
                "sub": other_user.auth0_sub,
                "email": other_user.email,
                "name": other_user.name,
                "role": "BUYER",
            },
            expires_delta=timedelta(hours=1),
        )

        response = client.get(
            f"/api/payments/{payment.id}", headers=create_auth_header(other_token)
        )

        assert response.status_code == 403

    def test_get_payment_not_found(self, client: TestClient, buyer_token):
        """Test retrieving non-existent payment."""
        response = client.get("/api/payments/99999", headers=create_auth_header(buyer_token))

        assert response.status_code == 404


class TestGetArtworkPayment:
    """Tests for GET /payments/artwork/{artwork_id} endpoint."""

    def test_get_artwork_payment_as_buyer_succeeded(
        self, client: TestClient, db_session, artwork, winning_bid, buyer_token
    ):
        """Test buyer retrieving their own completed payment."""
        payment = Payment(
            bid_id=winning_bid.id,
            stripe_payment_intent_id="pi_test123",
            amount=100.0,
            currency="usd",
            status=PaymentStatus.SUCCEEDED,
        )
        db_session.add(payment)
        db_session.commit()

        response = client.get(
            f"/api/payments/artwork/{artwork.id}",
            headers=create_auth_header(buyer_token),
        )

        assert response.status_code == 200
        data = response.json()
        assert data["amount"] == "100.00"
        assert data["status"] == "SUCCEEDED"

    def test_get_artwork_payment_as_buyer_pending(
        self, client: TestClient, db_session, artwork, winning_bid, buyer_token
    ):
        """Test buyer retrieving their own pending payment."""
        payment = Payment(
            bid_id=winning_bid.id,
            stripe_payment_intent_id="pi_test123",
            amount=100.0,
            currency="usd",
            status=PaymentStatus.PENDING,
        )
        db_session.add(payment)
        db_session.commit()

        response = client.get(
            f"/api/payments/artwork/{artwork.id}",
            headers=create_auth_header(buyer_token),
        )

        assert response.status_code == 200
        data = response.json()
        assert data["amount"] == "100.00"
        assert data["status"] == "PENDING"

    def test_get_artwork_payment_as_buyer_failed(
        self, client: TestClient, db_session, artwork, winning_bid, buyer_token
    ):
        """Test buyer retrieving their own failed payment."""
        payment = Payment(
            bid_id=winning_bid.id,
            stripe_payment_intent_id="pi_test123",
            amount=100.0,
            currency="usd",
            status=PaymentStatus.FAILED,
            failure_reason="card_declined",
        )
        db_session.add(payment)
        db_session.commit()

        response = client.get(
            f"/api/payments/artwork/{artwork.id}",
            headers=create_auth_header(buyer_token),
        )

        assert response.status_code == 200
        data = response.json()
        assert data["amount"] == "100.00"
        assert data["status"] == "FAILED"
        assert data["failure_reason"] == "card_declined"

    def test_get_artwork_payment_as_seller_succeeded(
        self, client: TestClient, db_session, artwork, winning_bid, seller_token
    ):
        """Test seller retrieving completed payment for their artwork."""
        payment = Payment(
            bid_id=winning_bid.id,
            stripe_payment_intent_id="pi_test123",
            amount=100.0,
            currency="usd",
            status=PaymentStatus.SUCCEEDED,
        )
        db_session.add(payment)
        db_session.commit()

        response = client.get(
            f"/api/payments/artwork/{artwork.id}",
            headers=create_auth_header(seller_token),
        )

        assert response.status_code == 200
        data = response.json()
        assert data["amount"] == "100.00"

    def test_get_artwork_payment_as_seller_pending(
        self, client: TestClient, db_session, artwork, winning_bid, seller_token
    ):
        """Test seller cannot view pending payment for their artwork."""
        payment = Payment(
            bid_id=winning_bid.id,
            stripe_payment_intent_id="pi_test123",
            amount=100.0,
            currency="usd",
            status=PaymentStatus.PENDING,
        )
        db_session.add(payment)
        db_session.commit()

        response = client.get(
            f"/api/payments/artwork/{artwork.id}",
            headers=create_auth_header(seller_token),
        )

        assert response.status_code == 404
        assert "No completed payment" in response.json()["detail"]

    def test_get_artwork_payment_as_admin(
        self, client: TestClient, db_session, artwork, winning_bid, admin_token
    ):
        """Test admin retrieving completed artwork payment."""
        payment = Payment(
            bid_id=winning_bid.id,
            stripe_payment_intent_id="pi_test123",
            amount=100.0,
            currency="usd",
            status=PaymentStatus.SUCCEEDED,
        )
        db_session.add(payment)
        db_session.commit()

        response = client.get(
            f"/api/payments/artwork/{artwork.id}",
            headers=create_auth_header(admin_token),
        )

        assert response.status_code == 200

    def test_get_artwork_payment_unauthorized_user(
        self, client: TestClient, db_session, artwork, winning_bid
    ):
        """Test unauthorized user cannot view artwork payment."""
        from datetime import timedelta

        from models.user import User
        from services.jwt_service import JWTService

        # Create another user who is not the buyer or seller
        other_user = User(auth0_sub="auth0|other123")
        other_user.email = "other@test.com"
        other_user.name = "Other User"
        other_user.role = "BUYER"
        db_session.add(other_user)

        payment = Payment(
            bid_id=winning_bid.id,
            stripe_payment_intent_id="pi_test123",
            amount=100.0,
            currency="usd",
            status=PaymentStatus.SUCCEEDED,
        )
        db_session.add(payment)
        db_session.commit()

        # Generate token for other user
        other_token = JWTService.create_access_token(
            data={
                "sub": other_user.auth0_sub,
                "email": other_user.email,
                "name": other_user.name,
                "role": "BUYER",
            },
            expires_delta=timedelta(hours=1),
        )

        response = client.get(
            f"/api/payments/artwork/{artwork.id}",
            headers=create_auth_header(other_token),
        )

        assert response.status_code == 403
        assert "permission" in response.json()["detail"]

    def test_get_artwork_payment_not_found(self, client: TestClient, seller_token):
        """Test retrieving payment for non-existent artwork."""
        response = client.get(
            "/api/payments/artwork/99999", headers=create_auth_header(seller_token)
        )

        assert response.status_code == 404
        assert "Artwork not found" in response.json()["detail"]

    def test_get_artwork_payment_no_payment(self, client: TestClient, artwork, seller_token):
        """Test retrieving payment when artwork has no payment."""
        response = client.get(
            f"/api/payments/artwork/{artwork.id}",
            headers=create_auth_header(seller_token),
        )

        assert response.status_code == 404
        assert "No payment found" in response.json()["detail"]
