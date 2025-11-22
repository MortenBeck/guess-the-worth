"""
Test Database Schema Migrations (Stage 2).

These tests verify that database schema updates have been applied correctly:
- New fields added to Artwork model (artist_name, category, end_date)
- Database indexes created for performance
- Foreign key relationships work correctly
"""

from datetime import datetime, timedelta

import pytest
from sqlalchemy import inspect

from models.artwork import Artwork, ArtworkStatus
from models.bid import Bid
from models.user import User, UserRole


class TestArtworkNewFields:
    """Test that artwork model has new fields from migration."""

    def test_artwork_has_artist_name_field(self, db_session, seller_user):
        """Test that artwork model has artist_name field."""
        artwork = Artwork(
            seller_id=seller_user.id,
            title="Test Art",
            secret_threshold=100.0,
            artist_name="Test Artist",  # New field from Stage 2
            status=ArtworkStatus.ACTIVE,
        )
        db_session.add(artwork)
        db_session.commit()
        db_session.refresh(artwork)

        assert hasattr(artwork, "artist_name")
        assert artwork.artist_name == "Test Artist"

    def test_artwork_has_category_field(self, db_session, seller_user):
        """Test that artwork model has category field."""
        artwork = Artwork(
            seller_id=seller_user.id,
            title="Test Art",
            secret_threshold=100.0,
            category="Painting",  # New field from Stage 2
            status=ArtworkStatus.ACTIVE,
        )
        db_session.add(artwork)
        db_session.commit()
        db_session.refresh(artwork)

        assert hasattr(artwork, "category")
        assert artwork.category == "Painting"

    def test_artwork_has_end_date_field(self, db_session, seller_user):
        """Test that artwork model has end_date field."""
        end_date = datetime.utcnow() + timedelta(days=7)
        artwork = Artwork(
            seller_id=seller_user.id,
            title="Test Art",
            secret_threshold=100.0,
            end_date=end_date,  # New field from Stage 2
            status=ArtworkStatus.ACTIVE,
        )
        db_session.add(artwork)
        db_session.commit()
        db_session.refresh(artwork)

        assert hasattr(artwork, "end_date")
        assert artwork.end_date is not None
        assert isinstance(artwork.end_date, datetime)

    def test_artwork_with_all_new_fields(self, db_session, seller_user):
        """Test creating artwork with all new fields together."""
        end_date = datetime.utcnow() + timedelta(days=7)
        artwork = Artwork(
            seller_id=seller_user.id,
            title="Complete Test",
            secret_threshold=100.0,
            artist_name="Complete Artist",
            category="Digital Art",
            end_date=end_date,
            description="Test description",
            status=ArtworkStatus.ACTIVE,
        )
        db_session.add(artwork)
        db_session.commit()
        db_session.refresh(artwork)

        # Verify all new fields are present and correct
        assert artwork.artist_name == "Complete Artist"
        assert artwork.category == "Digital Art"
        assert artwork.end_date == end_date
        assert artwork.description == "Test description"

    def test_new_fields_are_optional(self, db_session, seller_user):
        """Test that new fields are optional (can be None)."""
        artwork = Artwork(
            seller_id=seller_user.id,
            title="Minimal Art",
            secret_threshold=100.0,
            status=ArtworkStatus.ACTIVE,
            # artist_name, category, end_date all omitted
        )
        db_session.add(artwork)
        db_session.commit()
        db_session.refresh(artwork)

        # Should succeed with None/null values
        assert artwork.artist_name is None
        assert artwork.category is None
        assert artwork.end_date is None


class TestDatabaseIndexes:
    """Test that database indexes were created for performance."""

    def test_artwork_seller_id_index_exists(self, db_session):
        """Test that index exists on artworks.seller_id."""
        inspector = inspect(db_session.bind)
        artwork_indexes = inspector.get_indexes("artworks")
        index_names = [idx["name"] for idx in artwork_indexes]

        # Check for seller_id index (name may vary by database)
        # Look for index containing seller_id in column list
        seller_id_indexed = any(
            "seller_id" in idx.get("column_names", []) for idx in artwork_indexes
        )

        assert (
            seller_id_indexed or "ix_artworks_seller_id" in index_names
        ), "seller_id should be indexed"

    def test_artwork_status_index_exists(self, db_session):
        """Test that index exists on artworks.status."""
        inspector = inspect(db_session.bind)
        artwork_indexes = inspector.get_indexes("artworks")

        # Check for status index
        status_indexed = any(
            "status" in idx.get("column_names", []) for idx in artwork_indexes
        )

        assert (
            status_indexed or "ix_artworks_status" in [idx["name"] for idx in artwork_indexes]
        ), "status should be indexed"

    def test_bid_artwork_id_index_exists(self, db_session):
        """Test that index exists on bids.artwork_id."""
        inspector = inspect(db_session.bind)
        bid_indexes = inspector.get_indexes("bids")

        # Check for artwork_id index
        artwork_id_indexed = any(
            "artwork_id" in idx.get("column_names", []) for idx in bid_indexes
        )

        assert (
            artwork_id_indexed or "ix_bids_artwork_id" in [idx["name"] for idx in bid_indexes]
        ), "artwork_id should be indexed"

    def test_bid_bidder_id_index_exists(self, db_session):
        """Test that index exists on bids.bidder_id."""
        inspector = inspect(db_session.bind)
        bid_indexes = inspector.get_indexes("bids")

        # Check for bidder_id index
        bidder_id_indexed = any(
            "bidder_id" in idx.get("column_names", []) for idx in bid_indexes
        )

        assert (
            bidder_id_indexed or "ix_bids_bidder_id" in [idx["name"] for idx in bid_indexes]
        ), "bidder_id should be indexed"


class TestForeignKeyRelationships:
    """Test that foreign key relationships work correctly."""

    def test_artwork_seller_relationship(self, db_session, seller_user):
        """Test that artwork.seller relationship works."""
        artwork = Artwork(
            seller_id=seller_user.id,
            title="Test Art",
            secret_threshold=100.0,
            status=ArtworkStatus.ACTIVE,
        )
        db_session.add(artwork)
        db_session.commit()
        db_session.refresh(artwork)

        # Access relationship
        assert artwork.seller is not None
        assert artwork.seller.id == seller_user.id
        assert artwork.seller.email == seller_user.email

    def test_bid_artwork_relationship(self, db_session, artwork, buyer_user):
        """Test that bid.artwork relationship works."""
        bid = Bid(
            artwork_id=artwork.id, bidder_id=buyer_user.id, amount=50.0, is_winning=False
        )
        db_session.add(bid)
        db_session.commit()
        db_session.refresh(bid)

        # Access relationship
        assert bid.artwork is not None
        assert bid.artwork.id == artwork.id
        assert bid.artwork.title == artwork.title

    def test_bid_bidder_relationship(self, db_session, artwork, buyer_user):
        """Test that bid.bidder relationship works."""
        bid = Bid(
            artwork_id=artwork.id, bidder_id=buyer_user.id, amount=50.0, is_winning=False
        )
        db_session.add(bid)
        db_session.commit()
        db_session.refresh(bid)

        # Access relationship
        assert bid.bidder is not None
        assert bid.bidder.id == buyer_user.id
        assert bid.bidder.email == buyer_user.email

    def test_artwork_bids_collection(self, db_session, artwork, buyer_user):
        """Test that artwork.bids collection relationship works."""
        # Create multiple bids
        bid1 = Bid(
            artwork_id=artwork.id, bidder_id=buyer_user.id, amount=50.0, is_winning=False
        )
        bid2 = Bid(
            artwork_id=artwork.id, bidder_id=buyer_user.id, amount=75.0, is_winning=False
        )
        db_session.add_all([bid1, bid2])
        db_session.commit()

        # Refresh artwork to load bids
        db_session.refresh(artwork)

        # Access bids collection
        assert len(artwork.bids) == 2
        assert all(isinstance(bid, Bid) for bid in artwork.bids)

    def test_user_artworks_collection(self, db_session, seller_user):
        """Test that user.artworks collection relationship works."""
        # Create multiple artworks
        artwork1 = Artwork(
            seller_id=seller_user.id,
            title="Art 1",
            secret_threshold=100.0,
            status=ArtworkStatus.ACTIVE,
        )
        artwork2 = Artwork(
            seller_id=seller_user.id,
            title="Art 2",
            secret_threshold=150.0,
            status=ArtworkStatus.ACTIVE,
        )
        db_session.add_all([artwork1, artwork2])
        db_session.commit()

        # Refresh user to load artworks
        db_session.refresh(seller_user)

        # Access artworks collection
        assert len(seller_user.artworks) == 2
        assert all(isinstance(art, Artwork) for art in seller_user.artworks)


class TestDatabaseConstraints:
    """Test database constraints and data integrity."""

    def test_artwork_requires_seller_id(self, db_session):
        """Test that artwork requires a valid seller_id."""
        artwork = Artwork(
            seller_id=9999,  # Non-existent user
            title="Invalid Art",
            secret_threshold=100.0,
            status=ArtworkStatus.ACTIVE,
        )
        db_session.add(artwork)

        with pytest.raises(Exception):  # Foreign key constraint violation
            db_session.commit()

        db_session.rollback()

    def test_bid_requires_valid_artwork_id(self, db_session, buyer_user):
        """Test that bid requires a valid artwork_id."""
        bid = Bid(
            artwork_id=9999,  # Non-existent artwork
            bidder_id=buyer_user.id,
            amount=100.0,
            is_winning=False,
        )
        db_session.add(bid)

        with pytest.raises(Exception):  # Foreign key constraint violation
            db_session.commit()

        db_session.rollback()

    def test_bid_requires_valid_bidder_id(self, db_session, artwork):
        """Test that bid requires a valid bidder_id."""
        bid = Bid(
            artwork_id=artwork.id,
            bidder_id=9999,  # Non-existent user
            amount=100.0,
            is_winning=False,
        )
        db_session.add(bid)

        with pytest.raises(Exception):  # Foreign key constraint violation
            db_session.commit()

        db_session.rollback()

    def test_user_email_uniqueness(self, db_session, buyer_user):
        """Test that user emails must be unique."""
        duplicate_user = User(
            auth0_sub="auth0|different",
            email=buyer_user.email,  # Duplicate email
            name="Duplicate",
            role=UserRole.BUYER,
        )
        db_session.add(duplicate_user)

        with pytest.raises(Exception):  # Unique constraint violation
            db_session.commit()

        db_session.rollback()

    def test_user_auth0_sub_uniqueness(self, db_session, buyer_user):
        """Test that auth0_sub must be unique."""
        duplicate_user = User(
            auth0_sub=buyer_user.auth0_sub,  # Duplicate auth0_sub
            email="different@test.com",
            name="Duplicate",
            role=UserRole.BUYER,
        )
        db_session.add(duplicate_user)

        with pytest.raises(Exception):  # Unique constraint violation
            db_session.commit()

        db_session.rollback()


class TestSchemaEvolution:
    """Test that schema can evolve without breaking existing data."""

    def test_old_artworks_work_with_new_schema(self, db_session, seller_user):
        """Test that artworks without new fields still work."""
        # Simulate old artwork (without new fields)
        old_artwork = Artwork(
            seller_id=seller_user.id,
            title="Legacy Artwork",
            secret_threshold=100.0,
            status=ArtworkStatus.ACTIVE,
            # No artist_name, category, or end_date
        )
        db_session.add(old_artwork)
        db_session.commit()
        db_session.refresh(old_artwork)

        # Should work fine with None values
        assert old_artwork.id is not None
        assert old_artwork.title == "Legacy Artwork"
        assert old_artwork.artist_name is None
        assert old_artwork.category is None
        assert old_artwork.end_date is None

    def test_can_update_old_artwork_with_new_fields(self, db_session, seller_user):
        """Test that old artworks can be updated with new fields."""
        # Create old artwork
        artwork = Artwork(
            seller_id=seller_user.id,
            title="Old Art",
            secret_threshold=100.0,
            status=ArtworkStatus.ACTIVE,
        )
        db_session.add(artwork)
        db_session.commit()
        db_session.refresh(artwork)

        # Update with new fields
        artwork.artist_name = "Updated Artist"
        artwork.category = "Updated Category"
        artwork.end_date = datetime.utcnow() + timedelta(days=7)
        db_session.commit()
        db_session.refresh(artwork)

        # Verify updates
        assert artwork.artist_name == "Updated Artist"
        assert artwork.category == "Updated Category"
        assert artwork.end_date is not None
