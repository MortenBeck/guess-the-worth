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
        f"/api/admin/users/{buyer_user.id}", headers={"Authorization": f"Bearer {admin_token}"}
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
