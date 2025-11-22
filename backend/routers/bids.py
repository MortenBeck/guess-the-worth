from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from database import get_db
from models import Artwork, Bid
from models.user import User
from schemas import BidCreate, BidResponse
from utils.auth import get_current_user

router = APIRouter()


@router.get("/artwork/{artwork_id}", response_model=List[BidResponse])
async def get_artwork_bids(artwork_id: int, db: Session = Depends(get_db)):
    bids = db.query(Bid).filter(Bid.artwork_id == artwork_id).all()
    return bids


@router.post("/", response_model=BidResponse)
async def create_bid(
    bid: BidCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Create a new bid on an artwork.

    SECURITY: bidder_id is extracted from the authenticated user's JWT token.
    This prevents bid creation with forged bidder_id.
    Sellers cannot bid on their own artworks.
    """
    # Validate bid amount
    if bid.amount < 0:
        raise HTTPException(status_code=400, detail="Bid amount must be non-negative")

    # Get artwork to check threshold and ownership
    artwork = db.query(Artwork).filter(Artwork.id == bid.artwork_id).first()
    if not artwork:
        raise HTTPException(status_code=404, detail="Artwork not found")

    if artwork.status != "ACTIVE":
        raise HTTPException(
            status_code=400, detail=f"Artwork is not active (status: {artwork.status})"
        )

    # SECURITY: Prevent seller from bidding on their own artwork
    if artwork.seller_id == current_user.id:
        raise HTTPException(
            status_code=403, detail="You cannot bid on your own artwork"
        )

    # Check if bid meets threshold
    is_winning = bid.amount >= artwork.secret_threshold

    # Create bid with authenticated user's ID
    db_bid = Bid(
        artwork_id=bid.artwork_id,
        bidder_id=current_user.id,
        amount=bid.amount,
        is_winning=is_winning,
    )

    # Update artwork current highest bid
    if bid.amount > artwork.current_highest_bid:
        artwork.current_highest_bid = bid.amount

    # If winning bid, mark artwork as sold
    if is_winning:
        artwork.status = "SOLD"

    db.add(db_bid)
    db.commit()
    db.refresh(db_bid)

    # TODO: Emit socket event for real-time bidding
    # await sio.emit("new_bid", {"bid": db_bid, "artwork_id": artwork.id},
    #                room=f"artwork_{artwork.id}")

    return db_bid


@router.get("/my-bids", response_model=List[BidResponse])
async def get_my_bids(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Get all bids placed by the authenticated user.

    SECURITY: Only returns bids where bidder_id matches the authenticated user.
    """
    bids = (
        db.query(Bid)
        .filter(Bid.bidder_id == current_user.id)
        .order_by(Bid.created_at.desc())
        .all()
    )
    return bids
