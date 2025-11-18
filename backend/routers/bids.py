from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from database import get_db
from models import Artwork, Bid
from schemas import BidCreate, BidResponse

router = APIRouter()


@router.get("/artwork/{artwork_id}", response_model=List[BidResponse])
async def get_artwork_bids(artwork_id: int, db: Session = Depends(get_db)):
    bids = db.query(Bid).filter(Bid.artwork_id == artwork_id).all()
    return bids


@router.post("/", response_model=BidResponse)
async def create_bid(bid: BidCreate, bidder_id: int, db: Session = Depends(get_db)):
    # Validate bid amount
    if bid.amount < 0:
        raise HTTPException(status_code=400, detail="Bid amount must be non-negative")

    # Verify bidder exists
    from models.user import User
    bidder = db.query(User).filter(User.id == bidder_id).first()
    if not bidder:
        raise HTTPException(status_code=404, detail="Bidder not found")

    # Get artwork to check threshold
    artwork = db.query(Artwork).filter(Artwork.id == bid.artwork_id).first()
    if not artwork:
        raise HTTPException(status_code=404, detail="Artwork not found")

    if artwork.status != "ACTIVE":
        raise HTTPException(status_code=400, detail=f"Artwork is not active (status: {artwork.status})")

    # Check if bid meets threshold
    is_winning = bid.amount >= artwork.secret_threshold

    # Create bid
    db_bid = Bid(
        artwork_id=bid.artwork_id,
        bidder_id=bidder_id,
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
