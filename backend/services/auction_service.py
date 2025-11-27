from datetime import UTC, datetime

from sqlalchemy.orm import Session

from models import Artwork, Bid


class AuctionService:
    @staticmethod
    def check_expired_auctions(db: Session) -> int:
        """
        Check and close expired auctions.

        Finds all active artworks past their end_date and updates their status:
        - SOLD if there's a winning bid
        - ARCHIVED if there's no winning bid

        Returns the number of auctions closed.
        """
        now = datetime.now(UTC)

        # Find active artworks past end_date
        expired_artworks = (
            db.query(Artwork).filter(Artwork.status == "ACTIVE", Artwork.end_date < now).all()
        )

        for artwork in expired_artworks:
            # Find winning bid
            winning_bid = (
                db.query(Bid).filter(Bid.artwork_id == artwork.id, Bid.is_winning.is_(True)).first()
            )

            if winning_bid:
                # Mark as sold
                artwork.status = "SOLD"
            else:
                # No winner, mark as archived
                artwork.status = "ARCHIVED"

        if expired_artworks:
            db.commit()

        return len(expired_artworks)
