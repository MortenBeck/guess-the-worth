from typing import List

from database import get_db
from fastapi import APIRouter, Depends, HTTPException, Request
from middleware.rate_limit import limiter
from models import Artwork, Bid
from models.user import User
from schemas import BidCreate, BidResponse
from services.audit_service import AuditService
from sqlalchemy.orm import Session, joinedload
from utils.auth import get_current_user

router = APIRouter()


# Import socket.io server for real-time events
# This import is placed after router definition to avoid circular imports
def get_sio():
    from main import sio

    return sio


@router.get("/artwork/{artwork_id}", response_model=List[BidResponse])
async def get_artwork_bids(artwork_id: int, db: Session = Depends(get_db)):
    """
    Get all bids for a specific artwork.

    Performance: Uses eager loading to prevent N+1 queries.
    """
    # Use eager loading to prevent N+1 queries
    bids = (
        db.query(Bid)
        .options(joinedload(Bid.artwork), joinedload(Bid.bidder))
        .filter(Bid.artwork_id == artwork_id)
        .all()
    )
    return bids


@router.post("/", response_model=BidResponse)
@limiter.limit("20/minute")  # Max 20 bids per minute per user
async def create_bid(
    request: Request,
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
    # Validate bid amount is positive
    if bid.amount <= 0:
        raise HTTPException(status_code=400, detail="Bid amount must be greater than zero")

    # Validate bid amount is reasonable (prevent overflow/ridiculous values)
    MAX_BID_AMOUNT = 1_000_000_000  # 1 billion
    if bid.amount > MAX_BID_AMOUNT:
        raise HTTPException(status_code=400, detail=f"Bid amount cannot exceed ${MAX_BID_AMOUNT:,}")

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
        raise HTTPException(status_code=403, detail="You cannot bid on your own artwork")

    # Validate bid is higher than current highest bid (if any)
    # Use 0.0 as default if current_highest_bid is None
    current_bid = artwork.current_highest_bid or 0.0
    if current_bid > 0 and bid.amount <= current_bid:
        raise HTTPException(
            status_code=400,
            detail=f"Bid must be higher than current highest bid (${current_bid})",
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

    # Update artwork current highest bid (handle None safely)
    if bid.amount > current_bid:
        artwork.current_highest_bid = bid.amount

    # If winning bid, mark artwork as PENDING_PAYMENT
    # Actual SOLD status will be set after payment confirmation
    if is_winning:
        artwork.status = "PENDING_PAYMENT"

    db.add(db_bid)
    db.commit()
    db.refresh(db_bid)

    # Add audit log for bid placement
    AuditService.log_action(
        db=db,
        action="bid_placed",
        resource_type="bid",
        resource_id=db_bid.id,
        user=current_user,
        details={
            "amount": float(bid.amount),
            "artwork_id": bid.artwork_id,
            "is_winning": db_bid.is_winning,
        },
        request=request,
    )

    # Emit socket event for real-time bidding
    # Wrapped in try-except to ensure HTTP response is sent even if socket fails
    try:
        sio = get_sio()
        await sio.emit(
            "new_bid",
            {
                "bid": {
                    "id": db_bid.id,
                    "artwork_id": db_bid.artwork_id,
                    "bidder_id": db_bid.bidder_id,
                    "amount": float(db_bid.amount),
                    "is_winning": db_bid.is_winning,
                    "created_at": db_bid.created_at.isoformat(),
                },
                "artwork": {
                    "id": artwork.id,
                    "current_highest_bid": float(artwork.current_highest_bid or 0.0),
                    "status": artwork.status.value,
                },
            },
            room=f"artwork_{artwork.id}",
        )

        # If winning bid, emit payment_required event
        if is_winning:
            await sio.emit(
                "payment_required",
                {
                    "artwork_id": artwork.id,
                    "winning_bid": float(db_bid.amount),
                    "bid_id": db_bid.id,
                    "winner_id": current_user.id,
                    "requires_payment": True,
                },
                room=f"artwork_{artwork.id}",
            )

            # Add audit log for winning bid (payment required)
            AuditService.log_action(
                db=db,
                action="winning_bid_placed",
                resource_type="artwork",
                resource_id=artwork.id,
                user=current_user,
                details={
                    "bid_amount": float(bid.amount),
                    "seller_id": artwork.seller_id,
                    "buyer_id": current_user.id,
                    "status": "PENDING_PAYMENT",
                },
                request=request,
            )
    except Exception as socket_error:
        # Log socket error but don't fail the bid request
        # The bid was already committed to the database successfully
        print(f"Socket emit failed for bid {db_bid.id}: {socket_error}")
        import traceback

        traceback.print_exc()

    return db_bid


@router.get("/my-bids", response_model=List[BidResponse])
async def get_my_bids(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Get all bids placed by the authenticated user.

    SECURITY: Only returns bids where bidder_id matches the authenticated user.
    Performance: Uses eager loading to prevent N+1 queries.
    """
    # Use eager loading to prevent N+1 queries
    bids = (
        db.query(Bid)
        .options(joinedload(Bid.artwork))
        .filter(Bid.bidder_id == current_user.id)
        .order_by(Bid.created_at.desc())
        .all()
    )
    return bids
