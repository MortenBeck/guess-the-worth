"""
Admin router for platform management.
Proof-of-concept implementation.
"""

from datetime import UTC, datetime, timedelta
from typing import Optional

from database import get_db
from fastapi import APIRouter, Depends, HTTPException, Query
from models.artwork import Artwork, ArtworkStatus
from models.audit_log import AuditLog
from models.bid import Bid
from models.user import User
from services.audit_service import AuditService
from sqlalchemy import desc, func
from sqlalchemy.orm import Session, joinedload
from utils.auth import get_current_user

router = APIRouter(prefix="/api/admin", tags=["admin"])


def require_admin(current_user: User = Depends(get_current_user)) -> User:
    """Ensure user is an admin."""
    if not hasattr(current_user, "role") or current_user.role != "ADMIN":
        raise HTTPException(status_code=403, detail="Admin access required")
    return current_user


# ============================================================================
# USER MANAGEMENT
# ============================================================================


@router.get("/users")
async def list_users(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, le=100),
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db),
):
    """
    List all users.

    NOTE: This returns minimal user data from database.
    For full user details (email, name, role), query Auth0 Management API.
    """
    query = db.query(User)

    # Get total count
    total = query.count()

    # Get paginated results
    users = query.offset(skip).limit(limit).all()

    return {
        "total": total,
        "users": [
            {
                "id": user.id,
                "auth0_sub": user.auth0_sub,
                "created_at": user.created_at.isoformat(),
            }
            for user in users
        ],
        "skip": skip,
        "limit": limit,
        "note": "For full user details (email, name, role), query Auth0 Management API",
    }


@router.get("/users/{user_id}")
async def get_user_details(
    user_id: int,
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db),
):
    """Get detailed user information."""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # Get user statistics
    artworks_count = db.query(Artwork).filter(Artwork.seller_id == user_id).count()
    bids_count = db.query(Bid).filter(Bid.bidder_id == user_id).count()
    total_spent = (
        db.query(func.sum(Bid.amount))
        .filter(Bid.bidder_id == user_id, Bid.is_winning.is_(True))
        .scalar()
        or 0
    )

    return {
        "id": user.id,
        "auth0_sub": user.auth0_sub,
        "created_at": user.created_at.isoformat(),
        "stats": {
            "artworks_created": artworks_count,
            "bids_placed": bids_count,
            "total_spent": float(total_spent),
        },
        "note": "For email, name, and role, query Auth0 Management API",
    }


@router.put("/users/{user_id}/ban")
async def ban_user(
    user_id: int,
    reason: str = Query(..., min_length=10),
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db),
):
    """
    Ban a user (POC: just logs the action).
    Production would update user.is_active = False
    """
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    if hasattr(user, "role") and user.role == "ADMIN":
        raise HTTPException(status_code=400, detail="Cannot ban admin users")

    # POC: Just log the action (don't actually ban)
    AuditService.log_action(
        db=db,
        action="user_banned",
        resource_type="user",
        resource_id=user_id,
        user=current_user,
        details={"reason": reason},
    )

    return {
        "message": f"User {user.name} banned",
        "reason": reason,
    }


# ============================================================================
# TRANSACTION MONITORING
# ============================================================================


@router.get("/transactions")
async def list_transactions(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, le=100),
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db),
):
    """
    List recent transactions (sold artworks).
    POC: Returns winning bids.
    """
    # Get winning bids (representing transactions)
    transactions = (
        db.query(Bid)
        .options(joinedload(Bid.artwork), joinedload(Bid.bidder))
        .filter(Bid.is_winning.is_(True))
        .order_by(desc(Bid.created_at))
        .offset(skip)
        .limit(limit)
        .all()
    )

    total = db.query(Bid).filter(Bid.is_winning.is_(True)).count()

    return {
        "total": total,
        "transactions": [
            {
                "id": bid.id,
                "artwork_title": bid.artwork.title,
                "buyer": bid.bidder.name,
                "amount": float(bid.amount),
                "date": bid.created_at.isoformat(),
                "status": "completed",  # POC: Always completed
            }
            for bid in transactions
        ],
        "skip": skip,
        "limit": limit,
    }


# ============================================================================
# PLATFORM STATISTICS
# ============================================================================


@router.get("/stats/overview")
async def get_platform_overview(
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db),
):
    """Get comprehensive platform statistics."""
    # User stats
    total_users = db.query(User).count()
    users_last_30_days = (
        db.query(User)
        .filter(User.created_at >= datetime.now(UTC) - timedelta(days=30))
        .count()
    )

    # Artwork stats
    total_artworks = db.query(Artwork).count()
    active_auctions = (
        db.query(Artwork).filter(Artwork.status == ArtworkStatus.ACTIVE).count()
    )

    # Transaction stats
    total_transactions = db.query(Bid).filter(Bid.is_winning.is_(True)).count()

    total_revenue = (
        db.query(func.sum(Bid.amount)).filter(Bid.is_winning.is_(True)).scalar() or 0
    )

    # Platform fees (10% commission)
    platform_fees = float(total_revenue) * 0.10

    return {
        "users": {
            "total": total_users,
            "new_last_30_days": users_last_30_days,
        },
        "auctions": {
            "total": total_artworks,
            "active": active_auctions,
        },
        "transactions": {
            "total": total_transactions,
            "total_revenue": float(total_revenue),
            "platform_fees": platform_fees,
        },
    }


# ============================================================================
# FLAGGED CONTENT
# ============================================================================


@router.get("/flagged-auctions")
async def list_flagged_auctions(
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db),
):
    """
    List flagged/reported auctions.
    POC: Returns empty list (no flag system implemented).
    """
    # POC: Return empty list
    # Production would query a 'reports' table
    return {
        "total": 0,
        "flagged_auctions": [],
        "message": "No flagged auctions (feature not implemented in POC)",
    }


# ============================================================================
# SYSTEM HEALTH
# ============================================================================


@router.get("/system/health")
async def get_system_health(
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db),
):
    """
    Get system health metrics.
    POC: Basic database connectivity check.
    """
    try:
        # Test database connection
        db.execute("SELECT 1")
        db_status = "healthy"
    except Exception as e:
        db_status = f"unhealthy: {str(e)}"

    # Get recent activity
    recent_bids = (
        db.query(Bid)
        .filter(Bid.created_at >= datetime.now(UTC) - timedelta(hours=1))
        .count()
    )

    recent_artworks = (
        db.query(Artwork)
        .filter(Artwork.created_at >= datetime.now(UTC) - timedelta(hours=24))
        .count()
    )

    return {
        "status": "healthy" if db_status == "healthy" else "degraded",
        "database": db_status,
        "metrics": {
            "bids_last_hour": recent_bids,
            "artworks_last_24h": recent_artworks,
        },
        "timestamp": datetime.now(UTC).isoformat(),
    }


# ============================================================================
# AUDIT LOGS
# ============================================================================


@router.get("/audit-logs")
async def get_audit_logs(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, le=500),
    action: Optional[str] = None,
    user_id: Optional[int] = None,
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db),
):
    """Get audit logs for security monitoring."""
    query = db.query(AuditLog).options(joinedload(AuditLog.user))

    if action:
        query = query.filter(AuditLog.action == action)

    if user_id:
        query = query.filter(AuditLog.user_id == user_id)

    total = query.count()

    logs = query.order_by(desc(AuditLog.timestamp)).offset(skip).limit(limit).all()

    return {
        "total": total,
        "logs": [
            {
                "id": log.id,
                "action": log.action,
                "user": log.user.name if log.user else "system",
                "resource_type": log.resource_type,
                "resource_id": log.resource_id,
                "details": log.details,
                "ip_address": log.ip_address,
                "timestamp": log.timestamp.isoformat(),
            }
            for log in logs
        ],
        "skip": skip,
        "limit": limit,
    }


# ============================================================================
# DATABASE MIGRATIONS
# ============================================================================


@router.post("/stamp-migrations")
async def stamp_migrations(
    revision: str = Query(
        ..., description="Migration revision to stamp (e.g., 'b2d54a525fd0')"
    ),
    current_user: User = Depends(require_admin),
):
    """
    Stamp the database with a specific migration revision without running migrations.
    Use this when the database schema already matches a migration version.
    Requires admin authentication.
    """
    try:
        import subprocess

        # Run alembic stamp to mark database at specific revision
        result = subprocess.run(
            ["alembic", "stamp", revision],
            capture_output=True,
            text=True,
            cwd="/app",  # Azure app directory
        )

        if result.returncode != 0:
            raise Exception(f"Stamp failed: {result.stderr}")

        return {
            "success": True,
            "message": f"Database stamped at revision {revision}",
            "output": result.stdout,
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Stamp failed: {str(e)}")


@router.post("/run-migrations")
async def run_migrations(
    current_user: User = Depends(require_admin),
):
    """
    Run database migrations (alembic upgrade head).
    Requires admin authentication.
    """
    try:
        import subprocess

        # Run alembic upgrade head
        result = subprocess.run(
            ["alembic", "upgrade", "head"],
            capture_output=True,
            text=True,
            cwd="/app",  # Azure app directory
        )

        if result.returncode != 0:
            raise Exception(f"Migration failed: {result.stderr}")

        return {
            "success": True,
            "message": "Migrations completed successfully",
            "output": result.stdout,
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Migration failed: {str(e)}")


# ============================================================================
# DATABASE SEEDING
# ============================================================================


@router.post("/seed-database")
async def seed_database(
    confirm: str = Query(..., description="Must be 'yes' to confirm"),
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db),
):
    """
    Seed the production database with demo data.

    ⚠️ IMPORTANT: Before running this endpoint with Auth0:
    1. Create demo users in Auth0 Dashboard with matching auth0_sub values
    2. Assign appropriate roles (ADMIN, SELLER, BUYER) in Auth0
    3. Have those users log in at least once (creates minimal DB records)
    4. Then run this seeding endpoint

    This endpoint seeds artworks and bids. User creation is handled by Auth0.
    Requires admin authentication and explicit confirmation.
    Safe to run multiple times (idempotent).
    """
    if confirm.lower() != "yes":
        raise HTTPException(
            status_code=400,
            detail="Must confirm with 'yes' query parameter to proceed with seeding",
        )

    try:
        # Import seed functions
        from seeds.demo_artworks import seed_artworks
        from seeds.demo_bids import seed_bids
        from seeds.demo_users import seed_users

        # Execute seeding
        user_count = seed_users(db)
        artwork_count = seed_artworks(db)
        bid_count = seed_bids(db)

        # Log the seeding action
        AuditService.log_action(
            db=db,
            action="database_seeded",
            resource_type="system",
            resource_id=0,
            user=current_user,
            details={
                "users": user_count,
                "artworks": artwork_count,
                "bids": bid_count,
            },
        )

        return {
            "success": True,
            "message": "Database seeded successfully",
            "summary": {
                "users": user_count,
                "artworks": artwork_count,
                "bids": bid_count,
            },
        }

    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Seeding failed: {str(e)}")
