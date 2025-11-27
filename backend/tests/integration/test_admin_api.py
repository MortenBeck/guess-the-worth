"""
Tests for admin API endpoints.
"""

from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from models.user import User


def test_list_users_requires_admin(client: TestClient, buyer_token: str):
    """Non-admin users cannot access user list."""
    response = client.get("/api/admin/users", headers={"Authorization": f"Bearer {buyer_token}"})
    assert response.status_code == 403


def test_list_users_as_admin(client: TestClient, admin_token: str, db_session: Session):
    """Admin can list users."""
    response = client.get("/api/admin/users", headers={"Authorization": f"Bearer {admin_token}"})
    assert response.status_code == 200
    data = response.json()
    assert "users" in data
    assert "total" in data


def test_get_user_details(client: TestClient, admin_token: str, buyer_user: User):
    """Admin can get user details."""
    response = client.get(
        f"/api/admin/users/{buyer_user.id}",
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == buyer_user.id
    assert "stats" in data


def test_ban_user(client: TestClient, admin_token: str, buyer_user: User):
    """Admin can ban users."""
    response = client.put(
        f"/api/admin/users/{buyer_user.id}/ban",
        headers={"Authorization": f"Bearer {admin_token}"},
        params={"reason": "Violated terms of service multiple times"},
    )
    assert response.status_code == 200
    assert "banned" in response.json()["message"].lower()


def test_cannot_ban_admin(client: TestClient, admin_token: str, admin_user: User):
    """Cannot ban admin users."""
    response = client.put(
        f"/api/admin/users/{admin_user.id}/ban",
        headers={"Authorization": f"Bearer {admin_token}"},
        params={"reason": "Testing admin protection"},
    )
    assert response.status_code == 400


def test_get_platform_overview(client: TestClient, admin_token: str):
    """Admin can get platform statistics."""
    response = client.get(
        "/api/admin/stats/overview", headers={"Authorization": f"Bearer {admin_token}"}
    )
    assert response.status_code == 200
    data = response.json()
    assert "users" in data
    assert "auctions" in data
    assert "transactions" in data


def test_get_transactions(client: TestClient, admin_token: str):
    """Admin can view transactions."""
    response = client.get(
        "/api/admin/transactions", headers={"Authorization": f"Bearer {admin_token}"}
    )
    assert response.status_code == 200
    data = response.json()
    assert "transactions" in data
    assert "total" in data


def test_get_system_health(client: TestClient, admin_token: str):
    """Admin can check system health."""
    response = client.get(
        "/api/admin/system/health", headers={"Authorization": f"Bearer {admin_token}"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["status"] in ["healthy", "degraded"]
    assert "database" in data


def test_get_audit_logs(client: TestClient, admin_token: str):
    """Admin can view audit logs."""
    response = client.get(
        "/api/admin/audit-logs", headers={"Authorization": f"Bearer {admin_token}"}
    )
    assert response.status_code == 200
    data = response.json()
    assert "logs" in data
    assert "total" in data


def test_list_users_with_role_filter(client: TestClient, admin_token: str, buyer_user: User):
    """Admin can filter users by role."""
    response = client.get(
        "/api/admin/users?role=BUYER",
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert response.status_code == 200
    data = response.json()
    assert "users" in data


def test_list_users_with_search(client: TestClient, admin_token: str, buyer_user: User):
    """Admin can search users by name or email."""
    response = client.get(
        f"/api/admin/users?search={buyer_user.name}",
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert response.status_code == 200
    data = response.json()
    assert "users" in data


def test_get_user_details_not_found(client: TestClient, admin_token: str):
    """Getting details for non-existent user returns 404."""
    response = client.get(
        "/api/admin/users/99999", headers={"Authorization": f"Bearer {admin_token}"}
    )
    assert response.status_code == 404


def test_ban_user_not_found(client: TestClient, admin_token: str):
    """Banning non-existent user returns 404."""
    response = client.put(
        "/api/admin/users/99999/ban",
        headers={"Authorization": f"Bearer {admin_token}"},
        params={"reason": "Testing not found case"},
    )
    assert response.status_code == 404


def test_get_flagged_auctions(client: TestClient, admin_token: str):
    """Admin can view flagged auctions."""
    response = client.get(
        "/api/admin/flagged-auctions",
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert response.status_code == 200
    data = response.json()
    assert "total" in data
    assert "flagged_auctions" in data


def test_get_audit_logs_with_filters(client: TestClient, admin_token: str, buyer_user: User):
    """Admin can filter audit logs by action and user."""
    response = client.get(
        f"/api/admin/audit-logs?action=user_banned&user_id={buyer_user.id}",
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert response.status_code == 200
    data = response.json()
    assert "logs" in data


def test_seed_database_requires_admin(client: TestClient, buyer_token: str):
    """Non-admin users cannot seed the database."""
    response = client.post(
        "/api/admin/seed-database?confirm=yes",
        headers={"Authorization": f"Bearer {buyer_token}"},
    )
    assert response.status_code == 403


def test_seed_database_requires_confirmation(client: TestClient, admin_token: str):
    """Seeding without confirmation returns 400."""
    response = client.post(
        "/api/admin/seed-database?confirm=no",
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert response.status_code == 400
    assert "confirm" in response.json()["detail"].lower()


def test_seed_database_success(client: TestClient, admin_token: str, db_session: Session):
    """Admin can successfully seed the database."""
    response = client.post(
        "/api/admin/seed-database?confirm=yes",
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert "message" in data
    assert "summary" in data
    assert "users" in data["summary"]
    assert "artworks" in data["summary"]
    assert "bids" in data["summary"]
    # Verify counts are reasonable
    assert data["summary"]["users"] > 0
    assert data["summary"]["artworks"] > 0
    assert data["summary"]["bids"] >= 0


def test_seed_database_is_idempotent(client: TestClient, admin_token: str):
    """Seeding can be run multiple times without errors."""
    # First seeding
    response1 = client.post(
        "/api/admin/seed-database?confirm=yes",
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert response1.status_code == 200

    # Second seeding (should not fail)
    response2 = client.post(
        "/api/admin/seed-database?confirm=yes",
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert response2.status_code == 200
    assert response2.json()["success"] is True


def test_seed_database_creates_audit_log(client: TestClient, admin_token: str, db_session: Session):
    """Seeding creates an audit log entry."""
    # Seed the database
    response = client.post(
        "/api/admin/seed-database?confirm=yes",
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert response.status_code == 200

    # Check audit logs for the seeding action
    logs_response = client.get(
        "/api/admin/audit-logs?action=database_seeded",
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert logs_response.status_code == 200
    logs = logs_response.json()["logs"]
    assert len(logs) > 0
    assert logs[0]["action"] == "database_seeded"
    assert "users" in logs[0]["details"]
    assert "artworks" in logs[0]["details"]
    assert "bids" in logs[0]["details"]


def test_seed_database_handles_errors(client: TestClient, admin_token: str, monkeypatch):
    """Seeding handles database errors gracefully."""

    # Mock seed_users to raise an exception
    def mock_seed_users(db):
        raise Exception("Simulated database error")

    import seeds.demo_users

    monkeypatch.setattr(seeds.demo_users, "seed_users", mock_seed_users)

    response = client.post(
        "/api/admin/seed-database?confirm=yes",
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert response.status_code == 500
    assert "failed" in response.json()["detail"].lower()
