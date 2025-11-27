"""
Integration tests for audit logging.
Tests that security-critical actions are logged to the audit_logs table.
"""

from unittest.mock import patch

import pytest
from fastapi.testclient import TestClient
from models import Artwork
from models.audit_log import AuditLog
from sqlalchemy.orm import Session


@pytest.fixture(autouse=True)
def mock_auth0():
    """Mock Auth0 verification for all tests in this module to use JWT fallback."""
    with patch("services.auth_service.AuthService.verify_auth0_token") as mock:
        mock.side_effect = Exception("Auth0 not available - using JWT")
        yield mock


def test_bid_placement_creates_audit_log(
    client: TestClient, db_session: Session, artwork, buyer_user, buyer_token
):
    """Test that placing a bid creates an audit log entry."""
    headers = {"Authorization": f"Bearer {buyer_token}"}
    # Place a bid
    response = client.post(
        "/api/bids/",
        json={
            "artwork_id": artwork.id,
            "amount": 500,
        },
        headers=headers,
    )
    assert response.status_code == 200

    # Check that audit log was created
    audit_logs = (
        db_session.query(AuditLog).filter(AuditLog.action == "bid_placed").all()
    )

    assert len(audit_logs) > 0, "No audit log created for bid placement"

    # Verify the most recent audit log
    latest_log = audit_logs[-1]
    assert latest_log.action == "bid_placed"
    assert latest_log.resource_type == "bid"
    assert latest_log.user_id == buyer_user.id
    assert latest_log.details is not None
    assert "amount" in latest_log.details
    assert latest_log.details["amount"] == 500
    assert latest_log.details["artwork_id"] == artwork.id


def test_artwork_sold_creates_audit_log(
    client: TestClient, db_session: Session, artwork, buyer_user, buyer_token
):
    """Test that a winning bid creates an audit log for artwork sold."""
    headers = {"Authorization": f"Bearer {buyer_token}"}
    # Place a winning bid (at or above threshold)
    response = client.post(
        "/api/bids/",
        json={
            "artwork_id": artwork.id,
            "amount": artwork.secret_threshold,
        },
        headers=headers,
    )
    assert response.status_code == 200

    # Check that audit logs were created (both bid_placed and winning_bid_placed)
    bid_logs = db_session.query(AuditLog).filter(AuditLog.action == "bid_placed").all()
    assert len(bid_logs) > 0, "No audit log created for bid placement"

    winning_bid_logs = (
        db_session.query(AuditLog).filter(AuditLog.action == "winning_bid_placed").all()
    )
    assert len(winning_bid_logs) > 0, "No audit log created for winning bid"

    # Verify the winning_bid_placed audit log
    latest_winning_log = winning_bid_logs[-1]
    assert latest_winning_log.action == "winning_bid_placed"
    assert latest_winning_log.resource_type == "artwork"
    assert latest_winning_log.resource_id == artwork.id
    assert latest_winning_log.user_id == buyer_user.id
    assert latest_winning_log.details is not None
    assert "bid_amount" in latest_winning_log.details
    assert latest_winning_log.details["bid_amount"] == artwork.secret_threshold
    assert "seller_id" in latest_winning_log.details
    assert "buyer_id" in latest_winning_log.details
    assert "status" in latest_winning_log.details
    assert latest_winning_log.details["status"] == "PENDING_PAYMENT"


def test_audit_log_contains_request_metadata(
    client: TestClient, db_session: Session, artwork, buyer_user, buyer_token
):
    """Test that audit logs contain request metadata (IP, user agent)."""
    # Place a bid
    response = client.post(
        "/api/bids/",
        json={
            "artwork_id": artwork.id,
            "amount": 300,
        },
        headers={
            "User-Agent": "TestClient/1.0",
            "Authorization": f"Bearer {buyer_token}",
        },
    )
    assert response.status_code == 200

    # Get the latest audit log
    audit_log = (
        db_session.query(AuditLog)
        .filter(AuditLog.action == "bid_placed")
        .order_by(AuditLog.timestamp.desc())
        .first()
    )

    assert audit_log is not None
    # IP address should be captured (testclient uses testclient)
    assert audit_log.ip_address is not None
    # User agent should be captured
    assert audit_log.user_agent is not None


def test_audit_log_timestamps_are_set(
    client: TestClient, db_session: Session, artwork, buyer_user, buyer_token
):
    """Test that audit logs have timestamps set automatically."""
    headers = {"Authorization": f"Bearer {buyer_token}"}
    # Place a bid
    response = client.post(
        "/api/bids/",
        json={
            "artwork_id": artwork.id,
            "amount": 400,
        },
        headers=headers,
    )
    assert response.status_code == 200

    # Get the latest audit log
    audit_log = (
        db_session.query(AuditLog)
        .filter(AuditLog.action == "bid_placed")
        .order_by(AuditLog.timestamp.desc())
        .first()
    )

    assert audit_log is not None
    assert audit_log.timestamp is not None


def test_losing_bid_does_not_create_artwork_sold_log(
    client: TestClient, db_session: Session, artwork, buyer_user, buyer_token
):
    """Test that a losing bid does not create an artwork_sold audit log."""
    headers = {"Authorization": f"Bearer {buyer_token}"}
    # Get initial count of artwork_sold logs
    initial_sold_count = (
        db_session.query(AuditLog).filter(AuditLog.action == "artwork_sold").count()
    )

    # Place a losing bid (below threshold)
    # Use half the threshold to ensure it's above zero but below the winning amount
    losing_amount = artwork.secret_threshold / 2
    response = client.post(
        "/api/bids/",
        json={
            "artwork_id": artwork.id,
            "amount": losing_amount,
        },
        headers=headers,
    )
    assert response.status_code == 200

    # Verify artwork is still active
    artwork = db_session.query(Artwork).filter(Artwork.id == artwork.id).first()
    assert artwork.status.value == "ACTIVE"

    # Check that no new artwork_sold log was created
    final_sold_count = (
        db_session.query(AuditLog).filter(AuditLog.action == "artwork_sold").count()
    )

    assert (
        final_sold_count == initial_sold_count
    ), "Artwork_sold log should not be created for losing bid"

    # But bid_placed log should exist
    bid_logs = db_session.query(AuditLog).filter(AuditLog.action == "bid_placed").all()
    assert len(bid_logs) > 0, "Bid_placed log should be created even for losing bid"


def test_audit_log_queryable_by_user(db_session: Session, buyer_user):
    """Test that audit logs can be queried by user_id."""
    # Create some test audit logs
    from services.audit_service import AuditService

    AuditService.log_action(
        db=db_session,
        action="test_action",
        resource_type="test",
        resource_id=1,
        user=buyer_user,
        details={"test": "data"},
        request=None,
    )

    # Query logs by user
    user_logs = (
        db_session.query(AuditLog).filter(AuditLog.user_id == buyer_user.id).all()
    )

    assert len(user_logs) > 0, "Should be able to query audit logs by user"


def test_audit_log_queryable_by_action(db_session: Session, buyer_user):
    """Test that audit logs can be queried by action type."""
    # Create some test audit logs
    from services.audit_service import AuditService

    AuditService.log_action(
        db=db_session,
        action="specific_test_action",
        resource_type="test",
        resource_id=1,
        user=buyer_user,
        details={"test": "data"},
        request=None,
    )

    # Query logs by action
    action_logs = (
        db_session.query(AuditLog)
        .filter(AuditLog.action == "specific_test_action")
        .all()
    )

    assert len(action_logs) > 0, "Should be able to query audit logs by action"


def test_audit_service_handles_database_errors_gracefully(
    db_session: Session, buyer_user
):
    """Test that AuditService returns None when database errors occur without crashing."""
    from unittest.mock import MagicMock

    from services.audit_service import AuditService

    # Mock db.add to raise an exception
    original_add = db_session.add
    db_session.add = MagicMock(side_effect=Exception("Database connection error"))

    # Call log_action - should not raise exception
    result = AuditService.log_action(
        db=db_session,
        action="test_action",
        resource_type="test",
        resource_id=1,
        user=buyer_user,
        details={"test": "data"},
        request=None,
    )

    # Restore original add method
    db_session.add = original_add

    # Should return None when error occurs
    assert result is None, "AuditService should return None when database errors occur"

    # Verify no audit log was created
    logs = db_session.query(AuditLog).filter(AuditLog.action == "test_action").all()
    assert len(logs) == 0, "No audit log should be created when error occurs"
