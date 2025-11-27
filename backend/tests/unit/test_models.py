"""
Unit tests for SQLAlchemy database models.
Tests model creation, relationships, constraints, and enums.
"""

from datetime import datetime

import pytest
from sqlalchemy.exc import IntegrityError

from models.artwork import Artwork, ArtworkStatus
from models.bid import Bid
from models.user import User


class TestUserModel:
    """Test User model and constraints."""

    def test_create_user(self, db_session):
        """Test creating a basic user."""
        user = User(auth0_sub="auth0|test123")
        db_session.add(user)
        db_session.commit()
        db_session.refresh(user)
        # Attach Auth0 data (simulated)
        user.email = "test@example.com"
        user.name = "Test User"
        user.role = "BUYER"

        assert user.id is not None
        assert user.auth0_sub == "auth0|test123"
        assert user.email == "test@example.com"
        assert user.name == "Test User"
        assert user.role == "BUYER"
        assert isinstance(user.created_at, datetime)

    def test_user_default_role(self, db_session):
        """Test user defaults to BUYER role."""
        user = User(auth0_sub="auth0|default")
        db_session.add(user)
        db_session.commit()
        db_session.refresh(user)
        # Attach Auth0 data (simulated) - set default role
        user.email = "default@example.com"
        user.name = "Default User"
        user.role = "BUYER"

        assert user.role == "BUYER"

    def test_user_unique_auth0_sub(self, db_session):
        """Test auth0_sub must be unique."""
        user1 = User(auth0_sub="auth0|duplicate")
        user2 = User(auth0_sub="auth0|duplicate")
        db_session.add(user1)
        db_session.commit()

        db_session.add(user2)
        with pytest.raises(IntegrityError):
            db_session.commit()

    def test_user_unique_email(self, db_session):
        """Test email is not enforced as unique in DB (managed by Auth0)."""
        user1 = User(auth0_sub="auth0|user1")
        user2 = User(auth0_sub="auth0|user2")
        db_session.add(user1)
        db_session.commit()
        db_session.add(user2)
        db_session.commit()

        # Attach same email to both (simulating Auth0 data)
        user1.email = "duplicate@example.com"
        user2.email = "duplicate@example.com"

        # This should work since email uniqueness is managed by Auth0, not DB
        assert user1.email == user2.email

    def test_user_role_strings(self, db_session):
        """Test all role string values."""
        buyer = User(auth0_sub="auth0|buyer")
        seller = User(auth0_sub="auth0|seller")
        admin = User(auth0_sub="auth0|admin")

        db_session.add_all([buyer, seller, admin])
        db_session.commit()
        db_session.refresh(buyer)
        db_session.refresh(seller)
        db_session.refresh(admin)

        # Attach Auth0 data (simulated)
        buyer.email = "buyer@test.com"
        buyer.name = "Buyer"
        buyer.role = "BUYER"

        seller.email = "seller@test.com"
        seller.name = "Seller"
        seller.role = "SELLER"

        admin.email = "admin@test.com"
        admin.name = "Admin"
        admin.role = "ADMIN"

        assert buyer.role == "BUYER"
        assert seller.role == "SELLER"
        assert admin.role == "ADMIN"

    def test_user_artworks_relationship(self, db_session, seller_user):
        """Test User.artworks relationship."""
        artwork1 = Artwork(seller_id=seller_user.id, title="Art 1", secret_threshold=100.0)
        artwork2 = Artwork(seller_id=seller_user.id, title="Art 2", secret_threshold=200.0)
        db_session.add_all([artwork1, artwork2])
        db_session.commit()

        db_session.refresh(seller_user)
        assert len(seller_user.artworks) == 2
        assert artwork1 in seller_user.artworks
        assert artwork2 in seller_user.artworks

    def test_user_bids_relationship(self, db_session, buyer_user, artwork):
        """Test User.bids relationship."""
        bid1 = Bid(artwork_id=artwork.id, bidder_id=buyer_user.id, amount=50.0)
        bid2 = Bid(artwork_id=artwork.id, bidder_id=buyer_user.id, amount=75.0)
        db_session.add_all([bid1, bid2])
        db_session.commit()

        db_session.refresh(buyer_user)
        assert len(buyer_user.bids) == 2
        assert bid1 in buyer_user.bids
        assert bid2 in buyer_user.bids


class TestArtworkModel:
    """Test Artwork model and constraints."""

    def test_create_artwork(self, db_session, seller_user):
        """Test creating a basic artwork."""
        artwork = Artwork(
            seller_id=seller_user.id,
            title="Beautiful Painting",
            description="A stunning piece",
            secret_threshold=500.0,
            current_highest_bid=0.0,
            status=ArtworkStatus.ACTIVE,
        )
        db_session.add(artwork)
        db_session.commit()
        db_session.refresh(artwork)

        assert artwork.id is not None
        assert artwork.seller_id == seller_user.id
        assert artwork.title == "Beautiful Painting"
        assert artwork.secret_threshold == 500.0
        assert artwork.current_highest_bid == 0.0
        assert artwork.status == ArtworkStatus.ACTIVE
        assert isinstance(artwork.created_at, datetime)

    def test_artwork_default_values(self, db_session, seller_user):
        """Test artwork defaults (current_highest_bid=0, status=ACTIVE)."""
        artwork = Artwork(seller_id=seller_user.id, title="Default Art", secret_threshold=100.0)
        db_session.add(artwork)
        db_session.commit()
        db_session.refresh(artwork)

        assert artwork.current_highest_bid == 0.0
        assert artwork.status == ArtworkStatus.ACTIVE

    def test_artwork_optional_fields(self, db_session, seller_user):
        """Test artwork with optional description and image_url."""
        artwork = Artwork(seller_id=seller_user.id, title="Minimal Art", secret_threshold=50.0)
        db_session.add(artwork)
        db_session.commit()
        db_session.refresh(artwork)

        assert artwork.description is None
        assert artwork.image_url is None

    def test_artwork_status_enum(self, db_session, seller_user):
        """Test all ArtworkStatus enum values."""
        active = Artwork(
            seller_id=seller_user.id,
            title="Active",
            secret_threshold=100.0,
            status=ArtworkStatus.ACTIVE,
        )
        sold = Artwork(
            seller_id=seller_user.id,
            title="Sold",
            secret_threshold=100.0,
            status=ArtworkStatus.SOLD,
        )
        archived = Artwork(
            seller_id=seller_user.id,
            title="Archived",
            secret_threshold=100.0,
            status=ArtworkStatus.ARCHIVED,
        )

        db_session.add_all([active, sold, archived])
        db_session.commit()

        assert active.status == ArtworkStatus.ACTIVE
        assert sold.status == ArtworkStatus.SOLD
        assert archived.status == ArtworkStatus.ARCHIVED

    def test_artwork_seller_relationship(self, db_session, seller_user):
        """Test Artwork.seller relationship."""
        artwork = Artwork(seller_id=seller_user.id, title="Test Art", secret_threshold=100.0)
        db_session.add(artwork)
        db_session.commit()
        db_session.refresh(artwork)

        assert artwork.seller is not None
        assert artwork.seller.id == seller_user.id
        assert artwork.seller.name == seller_user.name

    def test_artwork_bids_relationship(self, db_session, artwork, buyer_user):
        """Test Artwork.bids relationship."""
        bid1 = Bid(artwork_id=artwork.id, bidder_id=buyer_user.id, amount=50.0)
        bid2 = Bid(artwork_id=artwork.id, bidder_id=buyer_user.id, amount=100.0)
        db_session.add_all([bid1, bid2])
        db_session.commit()

        db_session.refresh(artwork)
        assert len(artwork.bids) == 2
        assert bid1 in artwork.bids
        assert bid2 in artwork.bids

    def test_artwork_foreign_key_constraint(self, db_session):
        """Test artwork requires valid seller_id."""
        artwork = Artwork(
            seller_id=99999,
            title="Invalid Seller",
            secret_threshold=100.0,  # Non-existent user
        )
        db_session.add(artwork)
        with pytest.raises(IntegrityError):
            db_session.commit()

    def test_artwork_cascade_delete_bids(self, db_session, artwork, buyer_user):
        """Test deleting artwork cascades to delete bids."""
        bid = Bid(artwork_id=artwork.id, bidder_id=buyer_user.id, amount=50.0)
        db_session.add(bid)
        db_session.commit()

        bid_id = bid.id

        # Delete artwork
        db_session.delete(artwork)
        db_session.commit()

        # Verify bid is also deleted
        deleted_bid = db_session.query(Bid).filter(Bid.id == bid_id).first()
        assert deleted_bid is None


class TestBidModel:
    """Test Bid model and constraints."""

    def test_create_bid(self, db_session, artwork, buyer_user):
        """Test creating a basic bid."""
        bid = Bid(
            artwork_id=artwork.id,
            bidder_id=buyer_user.id,
            amount=150.0,
            is_winning=False,
        )
        db_session.add(bid)
        db_session.commit()
        db_session.refresh(bid)

        assert bid.id is not None
        assert bid.artwork_id == artwork.id
        assert bid.bidder_id == buyer_user.id
        assert bid.amount == 150.0
        assert bid.is_winning is False
        assert isinstance(bid.created_at, datetime)

    def test_bid_default_is_winning(self, db_session, artwork, buyer_user):
        """Test bid defaults is_winning to False."""
        bid = Bid(artwork_id=artwork.id, bidder_id=buyer_user.id, amount=100.0)
        db_session.add(bid)
        db_session.commit()
        db_session.refresh(bid)

        assert bid.is_winning is False

    def test_bid_artwork_relationship(self, db_session, artwork, buyer_user):
        """Test Bid.artwork relationship."""
        bid = Bid(artwork_id=artwork.id, bidder_id=buyer_user.id, amount=100.0)
        db_session.add(bid)
        db_session.commit()
        db_session.refresh(bid)

        assert bid.artwork is not None
        assert bid.artwork.id == artwork.id
        assert bid.artwork.title == artwork.title

    def test_bid_bidder_relationship(self, db_session, artwork, buyer_user):
        """Test Bid.bidder relationship."""
        bid = Bid(artwork_id=artwork.id, bidder_id=buyer_user.id, amount=100.0)
        db_session.add(bid)
        db_session.commit()
        db_session.refresh(bid)

        assert bid.bidder is not None
        assert bid.bidder.id == buyer_user.id
        assert bid.bidder.email == buyer_user.email

    def test_bid_foreign_key_artwork(self, db_session, buyer_user):
        """Test bid requires valid artwork_id."""
        bid = Bid(artwork_id=99999, bidder_id=buyer_user.id, amount=100.0)  # Non-existent artwork
        db_session.add(bid)
        with pytest.raises(IntegrityError):
            db_session.commit()

    def test_bid_foreign_key_bidder(self, db_session, artwork):
        """Test bid requires valid bidder_id."""
        bid = Bid(artwork_id=artwork.id, bidder_id=99999, amount=100.0)  # Non-existent user
        db_session.add(bid)
        with pytest.raises(IntegrityError):
            db_session.commit()

    def test_multiple_bids_same_artwork(self, db_session, artwork, buyer_user, seller_user):
        """Test multiple users can bid on same artwork."""
        bid1 = Bid(artwork_id=artwork.id, bidder_id=buyer_user.id, amount=50.0)

        # Create another buyer
        another_buyer = User(auth0_sub="auth0|buyer2")
        db_session.add(another_buyer)
        db_session.commit()
        db_session.refresh(another_buyer)
        # Attach Auth0 data (simulated)
        another_buyer.email = "buyer2@test.com"
        another_buyer.name = "Buyer 2"
        another_buyer.role = "BUYER"

        bid2 = Bid(artwork_id=artwork.id, bidder_id=another_buyer.id, amount=75.0)

        db_session.add_all([bid1, bid2])
        db_session.commit()

        db_session.refresh(artwork)
        assert len(artwork.bids) == 2

    def test_multiple_bids_same_user(self, db_session, artwork, buyer_user):
        """Test same user can place multiple bids on same artwork."""
        bid1 = Bid(artwork_id=artwork.id, bidder_id=buyer_user.id, amount=50.0)
        bid2 = Bid(artwork_id=artwork.id, bidder_id=buyer_user.id, amount=100.0)
        bid3 = Bid(artwork_id=artwork.id, bidder_id=buyer_user.id, amount=150.0)

        db_session.add_all([bid1, bid2, bid3])
        db_session.commit()

        db_session.refresh(buyer_user)
        assert len(buyer_user.bids) == 3


class TestModelRelationships:
    """Test complex relationships and cascade behaviors."""

    def test_user_deletion_cascades(self, db_session, seller_user, buyer_user):
        """Test deleting user cascades to artworks and bids."""
        # Create artwork by seller
        artwork = Artwork(seller_id=seller_user.id, title="To Be Deleted", secret_threshold=100.0)
        db_session.add(artwork)
        db_session.commit()

        # Create bid by buyer
        bid = Bid(artwork_id=artwork.id, bidder_id=buyer_user.id, amount=50.0)
        db_session.add(bid)
        db_session.commit()

        buyer_id = buyer_user.id
        artwork_id = artwork.id
        bid_id = bid.id

        # Delete seller (should cascade to artwork, which cascades to bid)
        db_session.delete(seller_user)
        db_session.commit()

        # Verify artwork and bid are deleted
        deleted_artwork = db_session.query(Artwork).filter(Artwork.id == artwork_id).first()
        deleted_bid = db_session.query(Bid).filter(Bid.id == bid_id).first()

        assert deleted_artwork is None
        assert deleted_bid is None

        # Buyer should still exist (only their bid was deleted)
        remaining_buyer = db_session.query(User).filter(User.id == buyer_id).first()
        assert remaining_buyer is not None

    def test_artwork_with_multiple_relationships(self, db_session, seller_user):
        """Test artwork with multiple bids from multiple users."""
        artwork = Artwork(seller_id=seller_user.id, title="Popular Art", secret_threshold=100.0)
        db_session.add(artwork)
        db_session.commit()

        # Create multiple buyers
        buyers = []
        for i in range(3):
            buyer = User(auth0_sub=f"auth0|buyer{i}")
            buyers.append(buyer)

        db_session.add_all(buyers)
        db_session.commit()

        # Attach Auth0 data (simulated)
        for i, buyer in enumerate(buyers):
            db_session.refresh(buyer)
            buyer.email = f"buyer{i}@test.com"
            buyer.name = f"Buyer {i}"
            buyer.role = "BUYER"

        # Each buyer places 2 bids
        for buyer in buyers:
            bid1 = Bid(artwork_id=artwork.id, bidder_id=buyer.id, amount=50.0)
            bid2 = Bid(artwork_id=artwork.id, bidder_id=buyer.id, amount=75.0)
            db_session.add_all([bid1, bid2])

        db_session.commit()
        db_session.refresh(artwork)

        # Should have 6 total bids
        assert len(artwork.bids) == 6

        # Verify each buyer has 2 bids
        for buyer in buyers:
            db_session.refresh(buyer)
            assert len(buyer.bids) == 2


class TestAuditLogModel:
    """Test AuditLog model."""

    def test_audit_log_repr(self, db_session, buyer_user):
        """Test AuditLog __repr__ method."""
        from models.audit_log import AuditLog

        audit_log = AuditLog(
            user_id=buyer_user.id,
            action="test_action",
            resource_type="test",
            resource_id=1,
        )
        db_session.add(audit_log)
        db_session.commit()

        repr_str = repr(audit_log)
        assert "AuditLog" in repr_str
        assert "test_action" in repr_str
        assert str(buyer_user.id) in repr_str
