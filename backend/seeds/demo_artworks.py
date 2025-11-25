"""Seed demo artworks for testing and demonstration.

Creates a variety of artworks with different categories, statuses, and price points.
"""

from datetime import UTC, datetime, timedelta

from sqlalchemy.orm import Session

from models.artwork import Artwork, ArtworkStatus
from models.user import User, UserRole


def seed_artworks(db: Session) -> int:
    """Seed demo artworks with various configurations.

    This function is idempotent - safe to run multiple times.
    Artworks are identified by a combination of seller and title.

    Args:
        db: Database session

    Returns:
        Number of artworks created or verified
    """
    # Get demo sellers
    sellers = db.query(User).filter(User.role == UserRole.SELLER).all()

    if not sellers:
        print("   ⚠️  No sellers found! Please seed users first.")
        return 0

    # Map sellers by email for easy access
    seller_map = {seller.email: seller for seller in sellers}

    # Calculate dates for auctions
    now = datetime.now(UTC)
    future_7_days = now + timedelta(days=7)
    future_3_days = now + timedelta(days=3)
    future_1_day = now + timedelta(days=1)
    past_date = now - timedelta(days=1)

    demo_artworks = [
        # Alice Johnson's artworks (seller1)
        {
            "seller_email": "seller1@guesstheworth.demo",
            "title": "Sunset Over Mountains",
            "artist_name": "Alice Johnson",
            "category": "Landscape",
            "description": (
                "A breathtaking view of sunset casting golden hues over mountain peaks. "
                "Oil on canvas."
            ),
            "secret_threshold": 1500.00,
            "current_highest_bid": 1200.00,
            "status": ArtworkStatus.ACTIVE,
            "end_date": future_7_days,
            "image_url": None,
        },
        {
            "seller_email": "seller1@guesstheworth.demo",
            "title": "Urban Dreams",
            "artist_name": "Alice Johnson",
            "category": "Abstract",
            "description": (
                "An abstract interpretation of city life with bold colors and " "geometric shapes."
            ),
            "secret_threshold": 800.00,
            "current_highest_bid": 600.00,
            "status": ArtworkStatus.ACTIVE,
            "end_date": future_3_days,
            "image_url": None,
        },
        {
            "seller_email": "seller1@guesstheworth.demo",
            "title": "Morning Coffee",
            "artist_name": "Alice Johnson",
            "category": "Still Life",
            "description": "A cozy still life capturing the essence of a perfect morning.",
            "secret_threshold": 500.00,
            "current_highest_bid": 500.00,
            "status": ArtworkStatus.SOLD,
            "end_date": past_date,
            "image_url": None,
        },
        # Bob Martinez's artworks (seller2)
        {
            "seller_email": "seller2@guesstheworth.demo",
            "title": "The Dancer",
            "artist_name": "Bob Martinez",
            "category": "Portrait",
            "description": "A graceful dancer captured in motion. Acrylic on canvas.",
            "secret_threshold": 2000.00,
            "current_highest_bid": 1800.00,
            "status": ArtworkStatus.ACTIVE,
            "end_date": future_7_days,
            "image_url": None,
        },
        {
            "seller_email": "seller2@guesstheworth.demo",
            "title": "Ocean Waves",
            "artist_name": "Bob Martinez",
            "category": "Seascape",
            "description": "Dynamic representation of powerful ocean waves crashing on rocks.",
            "secret_threshold": 1200.00,
            "current_highest_bid": 950.00,
            "status": ArtworkStatus.ACTIVE,
            "end_date": future_3_days,
            "image_url": None,
        },
        {
            "seller_email": "seller2@guesstheworth.demo",
            "title": "Jazz Night",
            "artist_name": "Bob Martinez",
            "category": "Abstract",
            "description": "Abstract piece inspired by jazz music and nightlife energy.",
            "secret_threshold": 900.00,
            "current_highest_bid": 0.00,
            "status": ArtworkStatus.ACTIVE,
            "end_date": future_7_days,
            "image_url": None,
        },
        # Carol Chen's artworks (seller3)
        {
            "seller_email": "seller3@guesstheworth.demo",
            "title": "Garden Bloom",
            "artist_name": "Carol Chen",
            "category": "Floral",
            "description": (
                "Vibrant flowers in full bloom, celebrating nature's beauty. " "Watercolor."
            ),
            "secret_threshold": 600.00,
            "current_highest_bid": 450.00,
            "status": ArtworkStatus.ACTIVE,
            "end_date": future_7_days,
            "image_url": None,
        },
        {
            "seller_email": "seller3@guesstheworth.demo",
            "title": "Midnight Sky",
            "artist_name": "Carol Chen",
            "category": "Landscape",
            "description": "A serene night sky filled with stars and the Milky Way.",
            "secret_threshold": 1800.00,
            "current_highest_bid": 1500.00,
            "status": ArtworkStatus.ACTIVE,
            "end_date": future_1_day,
            "image_url": None,
        },
        {
            "seller_email": "seller3@guesstheworth.demo",
            "title": "City Lights",
            "artist_name": "Carol Chen",
            "category": "Urban",
            "description": "Dazzling city skyline at night with vibrant neon lights.",
            "secret_threshold": 1000.00,
            "current_highest_bid": 850.00,
            "status": ArtworkStatus.ACTIVE,
            "end_date": future_3_days,
            "image_url": None,
        },
        {
            "seller_email": "seller3@guesstheworth.demo",
            "title": "Autumn Forest",
            "artist_name": "Carol Chen",
            "category": "Landscape",
            "description": "A peaceful forest path covered in autumn leaves.",
            "secret_threshold": 700.00,
            "current_highest_bid": 0.00,
            "status": ArtworkStatus.ACTIVE,
            "end_date": future_7_days,
            "image_url": None,
        },
        {
            "seller_email": "seller3@guesstheworth.demo",
            "title": "Vintage Portrait",
            "artist_name": "Carol Chen",
            "category": "Portrait",
            "description": "A classic portrait study in the style of old masters.",
            "secret_threshold": 2500.00,
            "current_highest_bid": 0.00,
            "status": ArtworkStatus.ARCHIVED,
            "end_date": None,
            "image_url": None,
        },
        # Additional artworks for variety
        {
            "seller_email": "seller1@guesstheworth.demo",
            "title": "Desert Mirage",
            "artist_name": "Alice Johnson",
            "category": "Landscape",
            "description": "Mystical desert landscape with shimmering heat waves.",
            "secret_threshold": 1100.00,
            "current_highest_bid": 750.00,
            "status": ArtworkStatus.ACTIVE,
            "end_date": future_3_days,
            "image_url": None,
        },
        {
            "seller_email": "seller2@guesstheworth.demo",
            "title": "Winter Wonderland",
            "artist_name": "Bob Martinez",
            "category": "Landscape",
            "description": "Snow-covered landscape with peaceful winter atmosphere.",
            "secret_threshold": 950.00,
            "current_highest_bid": 0.00,
            "status": ArtworkStatus.ACTIVE,
            "end_date": future_7_days,
            "image_url": None,
        },
        {
            "seller_email": "seller3@guesstheworth.demo",
            "title": "Abstract Emotions",
            "artist_name": "Carol Chen",
            "category": "Abstract",
            "description": "Bold abstract piece expressing raw human emotions.",
            "secret_threshold": 1300.00,
            "current_highest_bid": 1100.00,
            "status": ArtworkStatus.ACTIVE,
            "end_date": future_1_day,
            "image_url": None,
        },
        {
            "seller_email": "seller1@guesstheworth.demo",
            "title": "Spring Meadow",
            "artist_name": "Alice Johnson",
            "category": "Floral",
            "description": "Cheerful spring meadow filled with wildflowers.",
            "secret_threshold": 650.00,
            "current_highest_bid": 500.00,
            "status": ArtworkStatus.ACTIVE,
            "end_date": future_7_days,
            "image_url": None,
        },
    ]

    created_count = 0

    for artwork_data in demo_artworks:
        # Get seller
        seller_email = artwork_data.pop("seller_email")
        seller = seller_map.get(seller_email)

        if not seller:
            print(f"   ⚠️  Seller not found: {seller_email}")
            continue

        # Check if artwork already exists (idempotency)
        existing_artwork = (
            db.query(Artwork)
            .filter(
                Artwork.seller_id == seller.id,
                Artwork.title == artwork_data["title"],
            )
            .first()
        )

        if existing_artwork:
            # Update existing artwork (except for certain fields)
            existing_artwork.description = artwork_data["description"]
            existing_artwork.category = artwork_data["category"]
            existing_artwork.artist_name = artwork_data["artist_name"]
            # Note: We don't update bids, status, or dates to preserve history
            print(f"   ↻ Updated existing artwork: {artwork_data['title']}")
        else:
            # Create new artwork
            new_artwork = Artwork(seller_id=seller.id, **artwork_data)
            db.add(new_artwork)
            print(f"   ✓ Created new artwork: {artwork_data['title']}")

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
        count = seed_artworks(db)
        print(f"\n✅ Seeded {count} artworks successfully!")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        db.rollback()
        raise
    finally:
        db.close()
