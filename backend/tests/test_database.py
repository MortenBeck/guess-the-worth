"""
Tests for database models and operations.
"""
import pytest
from models import User, Artwork, Bid
from models.user import UserRole


class TestUserModel:
    """Test User model."""

    def test_create_user(self, db_session, sample_user_data):
        """Test creating a user."""
        user = User(**sample_user_data)
        db_session.add(user)
        db_session.commit()

        assert user.id is not None
        assert user.email == sample_user_data["email"]
        assert user.auth0_sub == sample_user_data["auth0_sub"]
        assert user.created_at is not None

    def test_user_role_default(self, db_session):
        """Test that user role defaults to buyer."""
        user = User(
            auth0_sub="auth0|test",
            email="test@example.com",
            name="Test User"
        )
        db_session.add(user)
        db_session.commit()

        assert user.role == UserRole.BUYER

    def test_user_unique_email(self, db_session, sample_user_data):
        """Test that email must be unique."""
        user1 = User(**sample_user_data)
        db_session.add(user1)
        db_session.commit()

        # Try to create another user with same email
        user2_data = sample_user_data.copy()
        user2_data["auth0_sub"] = "auth0|different"
        user2 = User(**user2_data)
        db_session.add(user2)

        with pytest.raises(Exception):  # SQLAlchemy will raise an integrity error
            db_session.commit()


class TestArtworkModel:
    """Test Artwork model."""

    def test_create_artwork(self, db_session, created_user, sample_artwork_data):
        """Test creating an artwork."""
        artwork_data = sample_artwork_data.copy()
        artwork_data["seller_id"] = created_user.id
        artwork = Artwork(**artwork_data)
        db_session.add(artwork)
        db_session.commit()

        assert artwork.id is not None
        assert artwork.title == sample_artwork_data["title"]
        assert artwork.seller_id == created_user.id

    def test_artwork_seller_relationship(self, db_session, created_user, sample_artwork_data):
        """Test the relationship between artwork and seller."""
        artwork_data = sample_artwork_data.copy()
        artwork_data["seller_id"] = created_user.id
        artwork = Artwork(**artwork_data)
        db_session.add(artwork)
        db_session.commit()

        # Test the relationship
        assert artwork.seller.id == created_user.id
        assert len(created_user.artworks) > 0

    @pytest.fixture
    def created_user(self, db_session, sample_user_data):
        """Create a user for testing."""
        user = User(**sample_user_data)
        db_session.add(user)
        db_session.commit()
        db_session.refresh(user)
        return user


class TestBidModel:
    """Test Bid model."""

    @pytest.fixture
    def created_user(self, db_session, sample_user_data):
        """Create a user for testing."""
        user = User(**sample_user_data)
        db_session.add(user)
        db_session.commit()
        db_session.refresh(user)
        return user

    @pytest.fixture
    def created_artwork(self, db_session, created_user, sample_artwork_data):
        """Create an artwork for testing."""
        artwork_data = sample_artwork_data.copy()
        artwork_data["seller_id"] = created_user.id
        artwork = Artwork(**artwork_data)
        db_session.add(artwork)
        db_session.commit()
        db_session.refresh(artwork)
        return artwork

    def test_create_bid(self, db_session, created_user, created_artwork):
        """Test creating a bid."""
        bid = Bid(
            artwork_id=created_artwork.id,
            bidder_id=created_user.id,
            amount=150.00,
            is_winning=False
        )
        db_session.add(bid)
        db_session.commit()

        assert bid.id is not None
        assert bid.amount == 150.00
        assert bid.created_at is not None

    def test_bid_relationships(self, db_session, created_user, created_artwork):
        """Test bid relationships with user and artwork."""
        bid = Bid(
            artwork_id=created_artwork.id,
            bidder_id=created_user.id,
            amount=150.00,
            is_winning=False
        )
        db_session.add(bid)
        db_session.commit()

        # Test relationships
        assert bid.bidder.id == created_user.id
        assert bid.artwork.id == created_artwork.id
        assert len(created_user.bids) > 0
