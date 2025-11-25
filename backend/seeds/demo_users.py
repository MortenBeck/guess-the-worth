"""Seed demo users for testing and demonstration.

Creates users with different roles for comprehensive testing.
All demo users have predictable auth0_sub values for easy identification.
"""

from sqlalchemy.orm import Session

from models.user import User, UserRole
from utils.auth import hash_password


def seed_users(db: Session) -> int:
    """Seed demo users with different roles.

    This function is idempotent - safe to run multiple times.
    Users are identified by their unique auth0_sub and won't be duplicated.

    Args:
        db: Database session

    Returns:
        Number of users created or verified
    """
    demo_users = [
        # Admin user with password for API seeding
        {
            "auth0_sub": "auth0|demo-admin-001",
            "email": "admin@guesstheworth.demo",
            "name": "Demo Admin",
            "role": UserRole.ADMIN,
            "password": "AdminPass123!",
        },
        # Seller users
        {
            "auth0_sub": "auth0|demo-seller-001",
            "email": "seller1@guesstheworth.demo",
            "name": "Alice Johnson (Demo Seller)",
            "role": UserRole.SELLER,
        },
        {
            "auth0_sub": "auth0|demo-seller-002",
            "email": "seller2@guesstheworth.demo",
            "name": "Bob Martinez (Demo Seller)",
            "role": UserRole.SELLER,
        },
        {
            "auth0_sub": "auth0|demo-seller-003",
            "email": "seller3@guesstheworth.demo",
            "name": "Carol Chen (Demo Seller)",
            "role": UserRole.SELLER,
        },
        # Buyer users
        {
            "auth0_sub": "auth0|demo-buyer-001",
            "email": "buyer1@guesstheworth.demo",
            "name": "David Smith (Demo Buyer)",
            "role": UserRole.BUYER,
        },
        {
            "auth0_sub": "auth0|demo-buyer-002",
            "email": "buyer2@guesstheworth.demo",
            "name": "Emma Wilson (Demo Buyer)",
            "role": UserRole.BUYER,
        },
        {
            "auth0_sub": "auth0|demo-buyer-003",
            "email": "buyer3@guesstheworth.demo",
            "name": "Frank Brown (Demo Buyer)",
            "role": UserRole.BUYER,
        },
        {
            "auth0_sub": "auth0|demo-buyer-004",
            "email": "buyer4@guesstheworth.demo",
            "name": "Grace Lee (Demo Buyer)",
            "role": UserRole.BUYER,
        },
        {
            "auth0_sub": "auth0|demo-buyer-005",
            "email": "buyer5@guesstheworth.demo",
            "name": "Henry Taylor (Demo Buyer)",
            "role": UserRole.BUYER,
        },
    ]

    created_count = 0

    for user_data in demo_users:
        # Extract password if provided (not part of User model directly)
        password = user_data.pop("password", None)

        # Check if user already exists (idempotency)
        existing_user = db.query(User).filter(User.auth0_sub == user_data["auth0_sub"]).first()

        if existing_user:
            # Update existing user data if needed
            existing_user.email = user_data["email"]
            existing_user.name = user_data["name"]
            existing_user.role = user_data["role"]
            if password:
                existing_user.password_hash = hash_password(password)
            print(f"   ↻ Updated existing user: {user_data['name']}")
        else:
            # Create new user
            new_user = User(**user_data)
            if password:
                new_user.password_hash = hash_password(password)
            db.add(new_user)
            print(f"   ✓ Created new user: {user_data['name']}")

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
