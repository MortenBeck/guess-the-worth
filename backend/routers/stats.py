from fastapi import APIRouter, Depends
from sqlalchemy import func
from sqlalchemy.orm import Session

from database import get_db
from models import Artwork, Bid, User
from utils.auth import get_current_user, require_seller

router = APIRouter()


@router.get("/user")
async def get_user_stats(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Get current user's statistics.

    SECURITY: Only returns stats for the authenticated user.
    """
    # Count active bids (bids on active artworks)
    active_bids = (
        db.query(Bid)
        .join(Artwork)
        .filter(Bid.bidder_id == current_user.id, Artwork.status == "ACTIVE")
        .count()
    )

    # Count won auctions (winning bids on sold artworks)
    won_auctions = (
        db.query(Bid)
        .join(Artwork)
        .filter(
            Bid.bidder_id == current_user.id,
            Bid.is_winning == True,
            Artwork.status == "SOLD",
        )
        .count()
    )

    # Calculate total spent (sum of winning bids)
    total_spent = (
        db.query(func.sum(Bid.amount))
        .join(Artwork)
        .filter(
            Bid.bidder_id == current_user.id,
            Bid.is_winning == True,
            Artwork.status == "SOLD",
        )
        .scalar()
        or 0
    )

    return {
        "active_bids": active_bids,
        "won_auctions": won_auctions,
        "total_spent": float(total_spent),
    }


@router.get("/seller")
async def get_seller_stats(
    current_user: User = Depends(require_seller),
    db: Session = Depends(get_db),
):
    """
    Get seller statistics.

    SECURITY: Only returns stats for the authenticated seller.
    Requires SELLER or ADMIN role.
    """
    # Count total artworks
    total_artworks = (
        db.query(Artwork).filter(Artwork.seller_id == current_user.id).count()
    )

    # Count active auctions
    active_auctions = (
        db.query(Artwork)
        .filter(Artwork.seller_id == current_user.id, Artwork.status == "ACTIVE")
        .count()
    )

    # Count sold artworks
    sold_artworks = (
        db.query(Artwork)
        .filter(Artwork.seller_id == current_user.id, Artwork.status == "SOLD")
        .count()
    )

    # Calculate total earnings (sum of highest bids on sold artworks)
    total_earnings = (
        db.query(func.sum(Artwork.current_highest_bid))
        .filter(Artwork.seller_id == current_user.id, Artwork.status == "SOLD")
        .scalar()
        or 0
    )

    return {
        "total_artworks": total_artworks,
        "active_auctions": active_auctions,
        "sold_artworks": sold_artworks,
        "total_earnings": float(total_earnings),
    }


@router.get("/platform")
async def get_platform_stats(db: Session = Depends(get_db)):
    """
    Get public platform statistics.

    No authentication required - public endpoint.
    """
    # Count total artworks
    total_artworks = db.query(Artwork).count()

    # Count total users
    total_users = db.query(User).count()

    # Count total bids
    total_bids = db.query(Bid).count()

    # Count active auctions
    active_auctions = db.query(Artwork).filter(Artwork.status == "ACTIVE").count()

    return {
        "total_artworks": total_artworks,
        "total_users": total_users,
        "total_bids": total_bids,
        "active_auctions": active_auctions,
    }
