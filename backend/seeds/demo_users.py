"""Seed demo users for testing and demonstration.

⚠️ DEPRECATED: This script should NOT be used in production with Auth0.

With Auth0 integration, user records are automatically created in the database
when users first log in through Auth0. This script is only useful for:
- Creating test user references for development without Auth0
- Pre-populating user IDs for testing seed scripts

PRODUCTION APPROACH:
1. Create users in Auth0 Dashboard
2. Assign roles (ADMIN, SELLER, BUYER) in Auth0
3. Have users log in through Auth0 (auto-creates minimal DB records)
4. Then run artwork/bid seed scripts

This script creates only minimal database references - actual user data
comes from Auth0.
"""

from models.user import User
from sqlalchemy.orm import Session


def seed_users(db: Session) -> int:
    """Seed demo users with Auth0 references.

    IMPORTANT: Before running this, you must:
    1. Create corresponding users in Auth0 Dashboard
    2. Assign them roles (ADMIN, SELLER, BUYER)
    3. Use the auth0_sub values from Auth0 here

    This function is idempotent - safe to run multiple times.

    Args:
        db: Database session

    Returns:
        Number of users created or verified
    """
    # These auth0_sub values must match users created in Auth0
    # Format: auth0|<user-id> or google-oauth2|<id> or other provider format
    demo_users = [
        # Seller accounts (5)
        {"auth0_sub": "auth0|6926e831a9097688ce0c5405"},  # SellerAdam
        {"auth0_sub": "auth0|6926e8dab9d364fc82c5472e"},  # SellerBrian
        {"auth0_sub": "auth0|6926e8f4c5c25e4533a50903"},  # SellerCharles
        {"auth0_sub": "auth0|6926e90fa9097688ce0c54f5"},  # SellerDaniel
        {"auth0_sub": "auth0|6926e926ec0b07c94d935a5b"},  # SellerEdward
        # Buyer accounts (5)
        {"auth0_sub": "auth0|6926e8c9d490f658706da21a"},  # BuyerAlice
        {"auth0_sub": "auth0|6926e8e9304088403bef3ee3"},  # BuyerBella
        {"auth0_sub": "auth0|6926e902cbec956206df1912"},  # BuyerClaire
        {"auth0_sub": "auth0|6926e91b4a5f2c59dd974374"},  # BuyerDiana
        {"auth0_sub": "auth0|6926e931ec0b07c94d935a66"},  # BuyerElla
    ]

    created_count = 0

    for user_data in demo_users:
        # Check if user already exists (idempotency)
        existing_user = db.query(User).filter(User.auth0_sub == user_data["auth0_sub"]).first()

        if not existing_user:
            # Create new user reference
            new_user = User(**user_data)
            db.add(new_user)
            print(f"   ✓ Created user reference: {user_data['auth0_sub']}")
        else:
            print(f"   ↻ User reference already exists: {user_data['auth0_sub']}")

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
        count = seed_users(db)
        print(f"\n✅ Seeded {count} users successfully!")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        db.rollback()
        raise
    finally:
        db.close()
