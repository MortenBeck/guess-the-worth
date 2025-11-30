"""Seed demo bids for testing and demonstration.

Creates realistic bid history for artworks with active bidding.
"""

from datetime import UTC, datetime, timedelta

from models.artwork import Artwork, ArtworkStatus
from models.bid import Bid
from models.user import User
from sqlalchemy.orm import Session


def seed_bids(db: Session) -> int:
    """Seed demo bids for active artworks.

    This function is idempotent - safe to run multiple times.
    Bids are identified by unique combinations and won't be duplicated.

    NOTE: Users must be seeded first with matching auth0_sub values.

    Args:
        db: Database session

    Returns:
        Number of bids created or verified
    """
    # Get demo buyers by auth0_sub (buyer users)
    buyer_subs = [
        "auth0|6926e8c9d490f658706da21a",  # BuyerAlice
        "auth0|6926e8e9304088403bef3ee3",  # BuyerBella
        "auth0|6926e902cbec956206df1912",  # BuyerClaire
        "auth0|6926e91b4a5f2c59dd974374",  # BuyerDiana
        "auth0|6926e931ec0b07c94d935a66",  # BuyerElla
    ]
    buyers = db.query(User).filter(User.auth0_sub.in_(buyer_subs)).all()

    if not buyers:
        print("   ⚠️  No buyers found! Please seed users first.")
        return 0

    # Get artworks with existing bids
    artworks = (
        db.query(Artwork)
        .filter(
            Artwork.status == ArtworkStatus.ACTIVE,
            Artwork.current_highest_bid > 0,
        )
        .all()
    )

    if not artworks:
        print("   ⚠️  No artworks with bids found! Please seed artworks first.")
        return 0

    # Map buyers by auth0_sub for easy access
    buyer_map = {buyer.auth0_sub: buyer for buyer in buyers}

    # Create bids for artworks
    # We'll create a bid history that leads to the current_highest_bid
    demo_bids = [
        # Bids for "Sunset Over Mountains" (current: 1200)
        {
            "artwork_title": "Sunset Over Mountains",
            "bidder_sub": "auth0|6926e8c9d490f658706da21a",
            "amount": 800.00,
            "days_ago": 5,
            "is_winning": False,
        },
        {
            "artwork_title": "Sunset Over Mountains",
            "bidder_sub": "auth0|6926e8e9304088403bef3ee3",
            "amount": 950.00,
            "days_ago": 4,
            "is_winning": False,
        },
        {
            "artwork_title": "Sunset Over Mountains",
            "bidder_sub": "auth0|6926e902cbec956206df1912",
            "amount": 1100.00,
            "days_ago": 3,
            "is_winning": False,
        },
        {
            "artwork_title": "Sunset Over Mountains",
            "bidder_sub": "auth0|6926e8c9d490f658706da21a",
            "amount": 1200.00,
            "days_ago": 2,
            "is_winning": True,
        },
        # Bids for "Urban Dreams" (current: 600)
        {
            "artwork_title": "Urban Dreams",
            "bidder_sub": "auth0|6926e91b4a5f2c59dd974374",
            "amount": 400.00,
            "days_ago": 3,
            "is_winning": False,
        },
        {
            "artwork_title": "Urban Dreams",
            "bidder_sub": "auth0|6926e931ec0b07c94d935a66",
            "amount": 550.00,
            "days_ago": 2,
            "is_winning": False,
        },
        {
            "artwork_title": "Urban Dreams",
            "bidder_sub": "auth0|6926e8e9304088403bef3ee3",
            "amount": 600.00,
            "days_ago": 1,
            "is_winning": True,
        },
        # Bids for "The Dancer" (current: 1800)
        {
            "artwork_title": "The Dancer",
            "bidder_sub": "auth0|6926e902cbec956206df1912",
            "amount": 1500.00,
            "days_ago": 4,
            "is_winning": False,
        },
        {
            "artwork_title": "The Dancer",
            "bidder_sub": "auth0|6926e8c9d490f658706da21a",
            "amount": 1650.00,
            "days_ago": 3,
            "is_winning": False,
        },
        {
            "artwork_title": "The Dancer",
            "bidder_sub": "auth0|6926e931ec0b07c94d935a66",
            "amount": 1800.00,
            "days_ago": 1,
            "is_winning": True,
        },
        # Bids for "Ocean Waves" (current: 950)
        {
            "artwork_title": "Ocean Waves",
            "bidder_sub": "auth0|6926e8e9304088403bef3ee3",
            "amount": 700.00,
            "days_ago": 2,
            "is_winning": False,
        },
        {
            "artwork_title": "Ocean Waves",
            "bidder_sub": "auth0|6926e91b4a5f2c59dd974374",
            "amount": 850.00,
            "days_ago": 1,
            "is_winning": False,
        },
        {
            "artwork_title": "Ocean Waves",
            "bidder_sub": "auth0|6926e8c9d490f658706da21a",
            "amount": 950.00,
            "days_ago": 0,
            "is_winning": True,
        },
        # Bids for "Garden Bloom" (current: 450)
        {
            "artwork_title": "Garden Bloom",
            "bidder_sub": "auth0|6926e902cbec956206df1912",
            "amount": 350.00,
            "days_ago": 3,
            "is_winning": False,
        },
        {
            "artwork_title": "Garden Bloom",
            "bidder_sub": "auth0|6926e931ec0b07c94d935a66",
            "amount": 450.00,
            "days_ago": 1,
            "is_winning": True,
        },
        # Bids for "Midnight Sky" (current: 1500)
        {
            "artwork_title": "Midnight Sky",
            "bidder_sub": "auth0|6926e8c9d490f658706da21a",
            "amount": 1200.00,
            "days_ago": 2,
            "is_winning": False,
        },
        {
            "artwork_title": "Midnight Sky",
            "bidder_sub": "auth0|6926e91b4a5f2c59dd974374",
            "amount": 1350.00,
            "days_ago": 1,
            "is_winning": False,
        },
        {
            "artwork_title": "Midnight Sky",
            "bidder_sub": "auth0|6926e8e9304088403bef3ee3",
            "amount": 1500.00,
            "days_ago": 0,
            "is_winning": True,
        },
        # Bids for "City Lights" (current: 850)
        {
            "artwork_title": "City Lights",
            "bidder_sub": "auth0|6926e931ec0b07c94d935a66",
            "amount": 650.00,
            "days_ago": 2,
            "is_winning": False,
        },
        {
            "artwork_title": "City Lights",
            "bidder_sub": "auth0|6926e902cbec956206df1912",
            "amount": 750.00,
            "days_ago": 1,
            "is_winning": False,
        },
        {
            "artwork_title": "City Lights",
            "bidder_sub": "auth0|6926e8c9d490f658706da21a",
            "amount": 850.00,
            "days_ago": 0,
            "is_winning": True,
        },
        # Bids for "Desert Mirage" (current: 750)
        {
            "artwork_title": "Desert Mirage",
            "bidder_sub": "auth0|6926e8e9304088403bef3ee3",
            "amount": 600.00,
            "days_ago": 3,
            "is_winning": False,
        },
        {
            "artwork_title": "Desert Mirage",
            "bidder_sub": "auth0|6926e91b4a5f2c59dd974374",
            "amount": 750.00,
            "days_ago": 1,
            "is_winning": True,
        },
        # Bids for "Abstract Emotions" (current: 1100)
        {
            "artwork_title": "Abstract Emotions",
            "bidder_sub": "auth0|6926e8c9d490f658706da21a",
            "amount": 900.00,
            "days_ago": 2,
            "is_winning": False,
        },
        {
            "artwork_title": "Abstract Emotions",
            "bidder_sub": "auth0|6926e902cbec956206df1912",
            "amount": 1000.00,
            "days_ago": 1,
            "is_winning": False,
        },
        {
            "artwork_title": "Abstract Emotions",
            "bidder_sub": "auth0|6926e931ec0b07c94d935a66",
            "amount": 1100.00,
            "days_ago": 0,
            "is_winning": True,
        },
        # Bids for "Spring Meadow" (current: 500)
        {
            "artwork_title": "Spring Meadow",
            "bidder_sub": "auth0|6926e8e9304088403bef3ee3",
            "amount": 400.00,
            "days_ago": 2,
            "is_winning": False,
        },
        {
            "artwork_title": "Spring Meadow",
            "bidder_sub": "auth0|6926e91b4a5f2c59dd974374",
            "amount": 500.00,
            "days_ago": 1,
            "is_winning": True,
        },
    ]

    created_count = 0

    for bid_data in demo_bids:
        # Find artwork by title
        artwork = (
            db.query(Artwork).filter(Artwork.title == bid_data["artwork_title"]).first()
        )

        if not artwork:
            print(f"   ⚠️  Artwork not found: {bid_data['artwork_title']}")
            continue

        # Find bidder by auth0_sub
        bidder = buyer_map.get(bid_data["bidder_sub"])
        if not bidder:
            print(f"   ⚠️  Bidder not found: {bid_data['bidder_sub']}")
            continue

        # Check if bid already exists (idempotency)
        existing_bid = (
            db.query(Bid)
            .filter(
                Bid.artwork_id == artwork.id,
                Bid.bidder_id == bidder.id,
                Bid.amount == bid_data["amount"],
            )
            .first()
        )

        if existing_bid:
            # Update is_winning status if needed
            existing_bid.is_winning = bid_data["is_winning"]
            print(f"   ↻ Updated bid for {artwork.title} by {bid_data['bidder_sub']}")
        else:
            # Create new bid with adjusted timestamp
            created_at = datetime.now(UTC) - timedelta(days=bid_data["days_ago"])
            new_bid = Bid(
                artwork_id=artwork.id,
                bidder_id=bidder.id,
                amount=bid_data["amount"],
                is_winning=bid_data["is_winning"],
                created_at=created_at,
            )
            db.add(new_bid)
            print(f"   ✓ Created bid for {artwork.title} by {bid_data['bidder_sub']}")

        created_count += 1

    db.commit()
    return created_count


if __name__ == "__main__":
    """Allow running this seed script directly for testing."""
    import sys
    from pathlib import Path

    # Add backend directory to path
    backend_dir = Path(__file__).parent.parent
    sys.path.insert(0, str(backend_dir))

    from database import SessionLocal

    db = SessionLocal()
    try:
        count = seed_bids(db)
        print(f"\n✅ Seeded {count} bids successfully!")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        db.rollback()
        raise
    finally:
        db.close()
