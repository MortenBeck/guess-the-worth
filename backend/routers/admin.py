"""
Admin router for platform management.
Proof-of-concept implementation.
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import func, desc
from typing import List, Optional
from datetime import datetime, timedelta

from database import get_db
from models.user import User, UserRole
from models.artwork import Artwork, ArtworkStatus
from models.bid import Bid
from models.audit_log import AuditLog
from utils.auth import get_current_user
from services.audit_service import AuditService

router = APIRouter(prefix="/api/admin", tags=["admin"])


def require_admin(current_user: User = Depends(get_current_user)) -> User:
    """Ensure user is an admin."""
    if current_user.role != UserRole.ADMIN:
        raise HTTPException(status_code=403, detail="Admin access required")
    return current_user


# ============================================================================
# USER MANAGEMENT
# ============================================================================


@router.get("/users")
async def list_users(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, le=100),
    role: Optional[str] = None,
    search: Optional[str] = None,
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db),
):
    """
    List all users with optional filtering.
    POC: Basic implementation.
    """
    query = db.query(User)

    # Filter by role
    if role:
        query = query.filter(User.role == role)

    # Search by name or email
    if search:
        search_pattern = f"%{search}%"
        query = query.filter((User.name.ilike(search_pattern)) | (User.email.ilike(search_pattern)))

    # Get total count
    total = query.count()

    # Get paginated results
    users = query.offset(skip).limit(limit).all()

    return {
        "total": total,
        "users": [
            {
                "id": user.id,
                "name": user.name,
                "email": user.email,
                "role": user.role,
                "created_at": user.created_at.isoformat(),
                "is_active": True,  # POC: Always true
            }
            for user in users
        ],
        "skip": skip,
        "limit": limit,
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
        .filter(Bid.bidder_id == user_id, Bid.is_winning == True)
        .scalar()
        or 0
    )

    return {
        "id": user.id,
        "name": user.name,
        "email": user.email,
        "role": user.role,
        "created_at": user.created_at.isoformat(),
        "stats": {
            "artworks_created": artworks_count,
            "bids_placed": bids_count,
            "total_spent": float(total_spent),
        },
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

    if user.role == UserRole.ADMIN:
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
        .filter(Bid.is_winning == True)
        .order_by(desc(Bid.created_at))
        .offset(skip)
        .limit(limit)
        .all()
    )

    total = db.query(Bid).filter(Bid.is_winning == True).count()

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
        db.query(User).filter(User.created_at >= datetime.utcnow() - timedelta(days=30)).count()
    )

    # Artwork stats
    total_artworks = db.query(Artwork).count()
    active_auctions = db.query(Artwork).filter(Artwork.status == ArtworkStatus.ACTIVE).count()

    # Transaction stats
    total_transactions = db.query(Bid).filter(Bid.is_winning == True).count()

    total_revenue = db.query(func.sum(Bid.amount)).filter(Bid.is_winning == True).scalar() or 0

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
        db.query(Bid).filter(Bid.created_at >= datetime.utcnow() - timedelta(hours=1)).count()
    )

    recent_artworks = (
        db.query(Artwork)
        .filter(Artwork.created_at >= datetime.utcnow() - timedelta(hours=24))
        .count()
    )

    return {
        "status": "healthy" if db_status == "healthy" else "degraded",
        "database": db_status,
        "metrics": {
            "bids_last_hour": recent_bids,
            "artworks_last_24h": recent_artworks,
        },
        "timestamp": datetime.utcnow().isoformat(),
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
