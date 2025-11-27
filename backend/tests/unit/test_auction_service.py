"""
Unit tests for AuctionService.
Tests the auction expiration and closing logic.
"""

from datetime import datetime, timedelta

import pytest
from sqlalchemy.orm import Session

from models import Artwork
from models.artwork import ArtworkStatus
from models.bid import Bid
from models.user import User
from services.auction_service import AuctionService


@pytest.fixture
def expired_artwork_with_winner(
    db_session: Session,
    seller_user: User,
    buyer_user: User,
) -> Artwork:
    """Create an expired artwork with a winning bid."""
    artwork = Artwork(
        seller_id=seller_user.id,
        title="Expired Artwork with Winner",
        description="This auction has expired",
        secret_threshold=100.0,
        current_highest_bid=150.0,
        status=ArtworkStatus.ACTIVE,
        end_date=datetime.utcnow() - timedelta(hours=1),  # Expired 1 hour ago
    )
    db_session.add(artwork)
    db_session.commit()
    db_session.refresh(artwork)

    # Add winning bid
    winning_bid = Bid(
        artwork_id=artwork.id,
        bidder_id=buyer_user.id,
        amount=150.0,
        is_winning=True,
    )
    db_session.add(winning_bid)
    db_session.commit()

    return artwork


@pytest.fixture
def expired_artwork_without_winner(db_session: Session, seller_user: User) -> Artwork:
    """Create an expired artwork without a winning bid."""
    artwork = Artwork(
        seller_id=seller_user.id,
        title="Expired Artwork without Winner",
        description="This auction has expired with no winner",
        secret_threshold=100.0,
        current_highest_bid=50.0,
        status=ArtworkStatus.ACTIVE,
        end_date=datetime.utcnow() - timedelta(days=1),  # Expired 1 day ago
    )
    db_session.add(artwork)
    db_session.commit()
    db_session.refresh(artwork)
    return artwork


@pytest.fixture
def active_artwork_not_expired(db_session: Session, seller_user: User) -> Artwork:
    """Create an active artwork that hasn't expired yet."""
    artwork = Artwork(
        seller_id=seller_user.id,
        title="Active Artwork",
        description="This auction is still active",
        secret_threshold=100.0,
        current_highest_bid=75.0,
        status=ArtworkStatus.ACTIVE,
        end_date=datetime.utcnow() + timedelta(days=1),  # Expires in 1 day
    )
    db_session.add(artwork)
    db_session.commit()
    db_session.refresh(artwork)
    return artwork


class TestAuctionServiceCheckExpiredAuctions:
    """Test AuctionService.check_expired_auctions method."""

    def test_closes_expired_auction_with_winner_as_sold(
        self, db_session: Session, expired_artwork_with_winner: Artwork
    ):
        """Test that expired auction with winning bid is marked as SOLD."""
        # Verify initial state
        assert expired_artwork_with_winner.status == ArtworkStatus.ACTIVE

        # Run the service
        count = AuctionService.check_expired_auctions(db_session)

        # Verify the auction was closed
        assert count == 1

        # Refresh and check status
        db_session.refresh(expired_artwork_with_winner)
        assert expired_artwork_with_winner.status == ArtworkStatus.SOLD

    def test_closes_expired_auction_without_winner_as_archived(
        self, db_session: Session, expired_artwork_without_winner: Artwork
    ):
        """Test that expired auction without winning bid is marked as ARCHIVED."""
        # Verify initial state
        assert expired_artwork_without_winner.status == ArtworkStatus.ACTIVE

        # Run the service
        count = AuctionService.check_expired_auctions(db_session)

        # Verify the auction was closed
        assert count == 1

        # Refresh and check status
        db_session.refresh(expired_artwork_without_winner)
        assert expired_artwork_without_winner.status == ArtworkStatus.ARCHIVED

    def test_does_not_close_active_auctions(
        self, db_session: Session, active_artwork_not_expired: Artwork
    ):
        """Test that active auctions that haven't expired are not closed."""
        # Verify initial state
        assert active_artwork_not_expired.status == ArtworkStatus.ACTIVE

        # Run the service
        count = AuctionService.check_expired_auctions(db_session)

        # Verify no auctions were closed
        assert count == 0

        # Refresh and check status is still active
        db_session.refresh(active_artwork_not_expired)
        assert active_artwork_not_expired.status == ArtworkStatus.ACTIVE

    def test_handles_multiple_expired_auctions(
        self,
        db_session: Session,
        expired_artwork_with_winner: Artwork,
        expired_artwork_without_winner: Artwork,
    ):
        """Test that multiple expired auctions are all closed correctly."""
        # Run the service
        count = AuctionService.check_expired_auctions(db_session)

        # Verify both auctions were closed
        assert count == 2

        # Refresh and check statuses
        db_session.refresh(expired_artwork_with_winner)
        db_session.refresh(expired_artwork_without_winner)

        assert expired_artwork_with_winner.status == ArtworkStatus.SOLD
        assert expired_artwork_without_winner.status == ArtworkStatus.ARCHIVED

    def test_handles_mix_of_expired_and_active_auctions(
        self,
        db_session: Session,
        expired_artwork_with_winner: Artwork,
        active_artwork_not_expired: Artwork,
    ):
        """Test that only expired auctions are closed when there are mixed statuses."""
        # Run the service
        count = AuctionService.check_expired_auctions(db_session)

        # Verify only expired auction was closed
        assert count == 1

        # Refresh and check statuses
        db_session.refresh(expired_artwork_with_winner)
        db_session.refresh(active_artwork_not_expired)

        assert expired_artwork_with_winner.status == ArtworkStatus.SOLD
        assert active_artwork_not_expired.status == ArtworkStatus.ACTIVE

    def test_returns_zero_when_no_expired_auctions(
        self, db_session: Session, active_artwork_not_expired: Artwork
    ):
        """Test that service returns 0 when no auctions have expired."""
        count = AuctionService.check_expired_auctions(db_session)
        assert count == 0

    def test_returns_zero_when_no_auctions_exist(self, db_session: Session):
        """Test that service returns 0 when database has no auctions."""
        count = AuctionService.check_expired_auctions(db_session)
        assert count == 0

    def test_does_not_affect_already_sold_artwork(self, db_session: Session, sold_artwork: Artwork):
        """Test that already sold artworks are not affected."""
        # Make the sold artwork expired
        sold_artwork.end_date = datetime.utcnow() - timedelta(hours=1)
        db_session.commit()

        # Run the service
        count = AuctionService.check_expired_auctions(db_session)

        # Verify no auctions were closed (sold artwork is not ACTIVE)
        assert count == 0

        # Refresh and check status is still SOLD
        db_session.refresh(sold_artwork)
        assert sold_artwork.status == ArtworkStatus.SOLD

    def test_expired_auction_with_multiple_bids_but_no_winner(
        self, db_session: Session, seller_user: User, buyer_user: User
    ):
        """Test expired auction with bids but no winning bid is archived."""
        # Create expired artwork
        artwork = Artwork(
            seller_id=seller_user.id,
            title="Expired with bids",
            description="Has bids but no winner",
            secret_threshold=200.0,
            current_highest_bid=150.0,
            status=ArtworkStatus.ACTIVE,
            end_date=datetime.utcnow() - timedelta(hours=2),
        )
        db_session.add(artwork)
        db_session.commit()
        db_session.refresh(artwork)

        # Add non-winning bids
        bid1 = Bid(
            artwork_id=artwork.id,
            bidder_id=buyer_user.id,
            amount=100.0,
            is_winning=False,
        )
        bid2 = Bid(
            artwork_id=artwork.id,
            bidder_id=buyer_user.id,
            amount=150.0,
            is_winning=False,
        )
        db_session.add(bid1)
        db_session.add(bid2)
        db_session.commit()

        # Run the service
        count = AuctionService.check_expired_auctions(db_session)

        # Should be archived (no winning bid)
        assert count == 1
        db_session.refresh(artwork)
        assert artwork.status == ArtworkStatus.ARCHIVED

    def test_expired_auction_exactly_at_end_date(self, db_session: Session, seller_user: User):
        """Test that auction expiring right now is considered expired."""
        # Create artwork expiring in the past (even by 1 second)
        artwork = Artwork(
            seller_id=seller_user.id,
            title="Just Expired",
            description="Expiring now",
            secret_threshold=100.0,
            current_highest_bid=0.0,
            status=ArtworkStatus.ACTIVE,
            end_date=datetime.utcnow() - timedelta(seconds=1),
        )
        db_session.add(artwork)
        db_session.commit()

        # Run the service
        count = AuctionService.check_expired_auctions(db_session)

        # Should be closed
        assert count == 1
        db_session.refresh(artwork)
        assert artwork.status == ArtworkStatus.ARCHIVED
