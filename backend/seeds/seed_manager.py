#!/usr/bin/env python3
"""Database seed manager for Guess The Worth.

This script manages database seeding with environment awareness and idempotency.
Safe to run multiple times without duplicating data.

Usage:
    python seeds/seed_manager.py [--env ENV]

Arguments:
    --env ENV    Environment to seed (default: from .env ENVIRONMENT variable)

Examples:
    python seeds/seed_manager.py --env development
    python seeds/seed_manager.py --env production
"""

import argparse
import sys
from pathlib import Path

# Add backend directory to path for imports
backend_dir = Path(__file__).parent.parent
sys.path.insert(0, str(backend_dir))

from config.settings import settings  # noqa: E402
from database import SessionLocal  # noqa: E402
from seeds.demo_artworks import seed_artworks  # noqa: E402
from seeds.demo_bids import seed_bids  # noqa: E402
from seeds.demo_users import seed_users  # noqa: E402
# Import after path modification (noqa: E402)
from sqlalchemy.orm import Session  # noqa: E402


class SeedManager:
    """Manages database seeding with safety checks and environment awareness."""

    def __init__(self, target_env: str = None):
        """Initialize seed manager.

        Args:
            target_env: Target environment (development/production).
                Defaults to settings.environment.
        """
        self.target_env = target_env or settings.environment
        self.current_env = settings.environment

    def validate_environment(self) -> bool:
        """Validate that it's safe to seed in the target environment.

        Returns:
            True if validation passes, False otherwise.
        """
        # Check if target environment matches current environment
        if self.target_env != self.current_env:
            print(
                f"❌ Error: Target environment '{self.target_env}' does not match "
                f"current environment '{self.current_env}'"
            )
            print(
                f"   Update your .env file ENVIRONMENT variable to '{self.target_env}'"
            )
            return False

        # Warn if seeding production
        if self.target_env == "production":
            print("⚠️  WARNING: You are about to seed the PRODUCTION database!")
            print("   This will add demo data to your production environment.")
            response = input("   Type 'yes' to continue: ")
            if response.lower() != "yes":
                print("❌ Seeding cancelled.")
                return False

        return True

    def seed_database(self, db: Session) -> bool:
        """Execute all seed scripts in order.

        Args:
            db: Database session

        Returns:
            True if seeding was successful, False otherwise.
        """
        print(f"\n🌱 Starting database seeding for environment: {self.target_env}")
        print("=" * 60)

        try:
            # Seed users first (required for foreign keys)
            print("\n1️⃣  Seeding users...")
            user_count = seed_users(db)
            print(f"   ✅ Created/verified {user_count} users")

            # Seed artworks (requires users)
            print("\n2️⃣  Seeding artworks...")
            artwork_count = seed_artworks(db)
            print(f"   ✅ Created/verified {artwork_count} artworks")

            # Seed bids (requires users and artworks)
            print("\n3️⃣  Seeding bids...")
            bid_count = seed_bids(db)
            print(f"   ✅ Created/verified {bid_count} bids")

            print("\n" + "=" * 60)
            print("✅ Database seeding completed successfully!")
            print("\nSummary:")
            print(f"  - Users: {user_count}")
            print(f"  - Artworks: {artwork_count}")
            print(f"  - Bids: {bid_count}")
            print("\nSee README.md for demo account credentials.")

            return True

        except Exception as e:
            print(f"\n❌ Error during seeding: {str(e)}")
            db.rollback()
            import traceback

            traceback.print_exc()
            return False

    def run(self) -> int:
        """Run the seeding process.

        Returns:
            0 if successful, 1 if failed.
        """
        # Validate environment
        if not self.validate_environment():
            return 1

        # Create database session
        db = SessionLocal()
        try:
            success = self.seed_database(db)
            return 0 if success else 1
        finally:
            db.close()


def main():
    """Main entry point for seed manager."""
    parser = argparse.ArgumentParser(
        description="Seed the database with demo data",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    parser.add_argument(
        "--env",
        type=str,
        choices=["development", "production"],
        help="Target environment (default: from .env ENVIRONMENT variable)",
    )

    args = parser.parse_args()

    manager = SeedManager(target_env=args.env)
    sys.exit(manager.run())


if __name__ == "__main__":
    main()
