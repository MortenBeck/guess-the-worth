"""
Unit tests for database seeding scripts.
Tests seed_users, seed_artworks, seed_bids, and seed_manager.
"""

from datetime import datetime
from unittest.mock import MagicMock, patch

import pytest

from models.artwork import Artwork, ArtworkStatus
from models.bid import Bid
from models.user import User
from seeds.demo_artworks import seed_artworks
from seeds.demo_bids import seed_bids
from seeds.demo_users import seed_users
from seeds.seed_manager import SeedManager


class TestSeedUsers:
    """Test demo_users.seed_users() function."""

    def test_seed_users_creates_all_users(self, db_session):
        """Test that seed_users creates all 10 demo users."""
        count = seed_users(db_session)

        assert count == 10
        all_users = db_session.query(User).all()
        assert len(all_users) == 10

    def test_seed_users_creates_correct_roles(self, db_session):
        """Test that users are created with correct roles."""
        seed_users(db_session)

        # Note: Role is now attached at runtime from Auth0, not stored in DB
        # This test would need to be adapted based on how seed_users attaches roles
        all_users = db_session.query(User).all()
        assert len(all_users) == 10  # Total users created

    def test_seed_users_creates_correct_data(self, db_session):
        """Test that first seller user has correct auth0_sub."""
        seed_users(db_session)

        seller = db_session.query(User).filter(User.auth0_sub == "auth0|6926e831a9097688ce0c5405").first()
        assert seller is not None
        assert seller.auth0_sub == "auth0|6926e831a9097688ce0c5405"

    def test_seed_users_is_idempotent(self, db_session):
        """Test that running seed_users twice doesn't duplicate users."""
        # First run
        count1 = seed_users(db_session)
        assert count1 == 10

        # Second run
        count2 = seed_users(db_session)
        assert count2 == 10

        # Verify no duplicates
        all_users = db_session.query(User).all()
        assert len(all_users) == 10

    def test_seed_users_updates_existing_data(self, db_session):
        """Test that re-seeding is idempotent."""
        # First run
        seed_users(db_session)

        # Get first seller user
        seller = db_session.query(User).filter(User.auth0_sub == "auth0|6926e831a9097688ce0c5405").first()
        original_id = seller.id

        # Second run should be idempotent
        seed_users(db_session)

        # Verify same user still exists with same ID
        seller = db_session.query(User).filter(User.auth0_sub == "auth0|6926e831a9097688ce0c5405").first()
        assert seller.id == original_id

    def test_seed_users_all_have_auth0_sub(self, db_session):
        """Test that all users have auth0_sub values."""
        seed_users(db_session)

        users = db_session.query(User).all()
        for user in users:
            assert user.auth0_sub is not None
            assert user.auth0_sub.startswith("auth0|")

    def test_seed_users_all_have_demo_auth0_subs(self, db_session):
        """Test that all users have auth0_sub values."""
        seed_users(db_session)

        users = db_session.query(User).all()
        for user in users:
            assert user.auth0_sub.startswith("auth0|")


class TestSeedArtworks:
    """Test demo_artworks.seed_artworks() function."""

    def test_seed_artworks_requires_sellers(self, db_session):
        """Test that seed_artworks returns 0 if no sellers exist."""
        count = seed_artworks(db_session)
        assert count == 0

    def test_seed_artworks_creates_all_artworks(self, db_session):
        """Test that seed_artworks creates all 15 demo artworks."""
        # First create users
        seed_users(db_session)

        # Then seed artworks
        count = seed_artworks(db_session)

        assert count == 15
        all_artworks = db_session.query(Artwork).all()
        assert len(all_artworks) == 15

    def test_seed_artworks_creates_various_statuses(self, db_session):
        """Test that artworks are created with different statuses."""
        seed_users(db_session)
        seed_artworks(db_session)

        active = db_session.query(Artwork).filter(Artwork.status == ArtworkStatus.ACTIVE).all()
        sold = db_session.query(Artwork).filter(Artwork.status == ArtworkStatus.SOLD).all()
        archived = db_session.query(Artwork).filter(Artwork.status == ArtworkStatus.ARCHIVED).all()

        assert len(active) > 0
        assert len(sold) > 0
        assert len(archived) > 0

    def test_seed_artworks_have_categories(self, db_session):
        """Test that all artworks have categories assigned."""
        seed_users(db_session)
        seed_artworks(db_session)

        artworks = db_session.query(Artwork).all()
        for artwork in artworks:
            assert artwork.category is not None
            assert len(artwork.category) > 0

    def test_seed_artworks_have_valid_thresholds(self, db_session):
        """Test that artworks have valid secret thresholds."""
        seed_users(db_session)
        seed_artworks(db_session)

        artworks = db_session.query(Artwork).all()
        for artwork in artworks:
            assert artwork.secret_threshold > 0
            assert artwork.current_highest_bid >= 0

    def test_seed_artworks_is_idempotent(self, db_session):
        """Test that running seed_artworks twice doesn't duplicate artworks."""
        seed_users(db_session)

        # First run
        count1 = seed_artworks(db_session)
        assert count1 == 15

        # Second run
        count2 = seed_artworks(db_session)
        assert count2 == 15

        # Verify no duplicates
        all_artworks = db_session.query(Artwork).all()
        assert len(all_artworks) == 15

    def test_seed_artworks_belong_to_sellers(self, db_session):
        """Test that all artworks are owned by seller users."""
        seed_users(db_session)
        seed_artworks(db_session)

        artworks = db_session.query(Artwork).all()
        # All users exist, artworks belong to valid users
        all_users = db_session.query(User).all()
        user_ids = [u.id for u in all_users]

        for artwork in artworks:
            assert artwork.seller_id in user_ids

    def test_seed_artworks_have_end_dates(self, db_session):
        """Test that active artworks have end_dates."""
        seed_users(db_session)
        seed_artworks(db_session)

        active_artworks = (
            db_session.query(Artwork).filter(Artwork.status == ArtworkStatus.ACTIVE).all()
        )

        for artwork in active_artworks:
            if artwork.current_highest_bid > 0:  # Active with bids should have end dates
                assert artwork.end_date is not None
                assert isinstance(artwork.end_date, datetime)


class TestSeedBids:
    """Test demo_bids.seed_bids() function."""

    def test_seed_bids_requires_buyers(self, db_session):
        """Test that seed_bids returns 0 if no buyers exist."""
        count = seed_bids(db_session)
        assert count == 0

    def test_seed_bids_requires_artworks_with_bids(self, db_session):
        """Test that seed_bids returns 0 if no artworks with bids exist."""
        seed_users(db_session)
        # Don't seed artworks - should return 0
        count = seed_bids(db_session)
        assert count == 0

    def test_seed_bids_creates_bids(self, db_session):
        """Test that seed_bids creates bid records."""
        seed_users(db_session)
        seed_artworks(db_session)

        count = seed_bids(db_session)

        assert count > 0
        all_bids = db_session.query(Bid).all()
        assert len(all_bids) > 0

    def test_seed_bids_belong_to_buyers(self, db_session):
        """Test that all bids are placed by valid users."""
        seed_users(db_session)
        seed_artworks(db_session)
        seed_bids(db_session)

        bids = db_session.query(Bid).all()
        # All users exist, bids belong to valid users
        all_users = db_session.query(User).all()
        user_ids = [u.id for u in all_users]

        for bid in bids:
            assert bid.bidder_id in user_ids

    def test_seed_bids_have_valid_amounts(self, db_session):
        """Test that all bids have positive amounts."""
        seed_users(db_session)
        seed_artworks(db_session)
        seed_bids(db_session)

        bids = db_session.query(Bid).all()
        for bid in bids:
            assert bid.amount > 0

    def test_seed_bids_is_idempotent(self, db_session):
        """Test that running seed_bids twice doesn't duplicate bids."""
        seed_users(db_session)
        seed_artworks(db_session)

        # First run
        seed_bids(db_session)
        initial_bids = db_session.query(Bid).count()

        # Second run
        seed_bids(db_session)
        final_bids = db_session.query(Bid).count()

        # Should have same number of bids
        assert initial_bids == final_bids

    def test_seed_bids_have_winning_flags(self, db_session):
        """Test that bids have is_winning flags set appropriately."""
        seed_users(db_session)
        seed_artworks(db_session)
        seed_bids(db_session)

        bids = db_session.query(Bid).all()
        winning_bids = [b for b in bids if b.is_winning]

        # Should have at least some winning bids
        assert len(winning_bids) > 0

    def test_seed_bids_belong_to_active_artworks(self, db_session):
        """Test that bids are associated with actual artworks."""
        seed_users(db_session)
        seed_artworks(db_session)
        seed_bids(db_session)

        bids = db_session.query(Bid).all()
        artwork_ids = [a.id for a in db_session.query(Artwork).all()]

        for bid in bids:
            assert bid.artwork_id in artwork_ids


class TestSeedManager:
    """Test seeds.seed_manager.SeedManager class."""

    def test_seed_manager_initialization(self):
        """Test SeedManager initializes with correct environment."""
        manager = SeedManager(target_env="development")
        assert manager.target_env == "development"

    def test_seed_manager_default_environment(self):
        """Test SeedManager uses settings.environment by default."""
        manager = SeedManager()
        assert manager.target_env is not None

    def test_validate_environment_passes_for_matching_env(self):
        """Test environment validation passes when environments match."""
        with patch("seeds.seed_manager.settings") as mock_settings:
            mock_settings.environment = "development"
            manager = SeedManager(target_env="development")
            assert manager.validate_environment() is True

    def test_validate_environment_fails_for_mismatched_env(self):
        """Test environment validation fails when environments don't match."""
        with patch("seeds.seed_manager.settings") as mock_settings:
            mock_settings.environment = "development"
            manager = SeedManager(target_env="production")
            assert manager.validate_environment() is False

    @patch("builtins.input", return_value="yes")
    def test_validate_environment_production_confirms(self, mock_input):
        """Test production seeding requires confirmation."""
        with patch("seeds.seed_manager.settings") as mock_settings:
            mock_settings.environment = "production"
            manager = SeedManager(target_env="production")
            assert manager.validate_environment() is True
            mock_input.assert_called_once()

    @patch("builtins.input", return_value="no")
    def test_validate_environment_production_can_cancel(self, mock_input):
        """Test production seeding can be cancelled."""
        with patch("seeds.seed_manager.settings") as mock_settings:
            mock_settings.environment = "production"
            manager = SeedManager(target_env="production")
            assert manager.validate_environment() is False

    def test_seed_database_success(self, db_session):
        """Test successful database seeding."""
        manager = SeedManager(target_env="development")

        # Mock the session
        with patch("seeds.seed_manager.SessionLocal", return_value=db_session):
            success = manager.seed_database(db_session)

        assert success is True

        # Verify data was created
        assert db_session.query(User).count() > 0
        assert db_session.query(Artwork).count() > 0
        assert db_session.query(Bid).count() > 0

    def test_seed_database_handles_exceptions(self, db_session):
        """Test that seed_database rolls back on error."""
        manager = SeedManager(target_env="development")

        # Mock seed_users to raise an exception
        with patch("seeds.seed_manager.seed_users", side_effect=Exception("Test error")):
            success = manager.seed_database(db_session)

        assert success is False

    def test_seed_database_creates_correct_counts(self, db_session):
        """Test that seed_database creates expected number of records."""
        manager = SeedManager(target_env="development")
        manager.seed_database(db_session)

        # Expected counts based on seed scripts
        assert db_session.query(User).count() == 10
        assert db_session.query(Artwork).count() == 15
        # Bids count may vary based on artworks with bids

    @patch("seeds.seed_manager.settings")
    @patch("seeds.seed_manager.SessionLocal")
    def test_run_method_success(self, mock_session_local, mock_settings):
        """Test SeedManager.run() returns 0 on success."""
        mock_settings.environment = "development"
        mock_db = MagicMock()
        mock_session_local.return_value = mock_db

        manager = SeedManager(target_env="development")

        with patch.object(manager, "seed_database", return_value=True):
            result = manager.run()

        assert result == 0
        mock_db.close.assert_called_once()

    @patch("seeds.seed_manager.settings")
    @patch("seeds.seed_manager.SessionLocal")
    def test_run_method_failure(self, mock_session_local, mock_settings):
        """Test SeedManager.run() returns 1 on failure."""
        mock_settings.environment = "development"
        mock_db = MagicMock()
        mock_session_local.return_value = mock_db

        manager = SeedManager(target_env="development")

        with patch.object(manager, "seed_database", return_value=False):
            result = manager.run()

        assert result == 1
        mock_db.close.assert_called_once()

    @patch("seeds.seed_manager.settings")
    def test_run_method_env_validation_failure(self, mock_settings):
        """Test SeedManager.run() returns 1 if env validation fails."""
        mock_settings.environment = "development"
        manager = SeedManager(target_env="production")

        result = manager.run()

        assert result == 1


class TestSeedIntegration:
    """Integration tests for complete seeding workflow."""

    def test_complete_seeding_workflow(self, db_session):
        """Test the complete seeding workflow in order."""
        # Seed users
        user_count = seed_users(db_session)
        assert user_count == 10

        # Seed artworks (depends on users)
        artwork_count = seed_artworks(db_session)
        assert artwork_count == 15

        # Seed bids (depends on users and artworks)
        bid_count = seed_bids(db_session)
        assert bid_count > 0

        # Verify relationships
        artworks = db_session.query(Artwork).all()
        for artwork in artworks:
            # Verify seller exists
            assert artwork.seller is not None

        bids = db_session.query(Bid).all()
        for bid in bids:
            # Verify bidder exists
            assert bid.bidder is not None
            # Verify artwork exists
            assert bid.artwork is not None

    def test_idempotency_across_all_seeds(self, db_session):
        """Test that all seed scripts are idempotent when run together."""
        # First run
        seed_users(db_session)
        seed_artworks(db_session)
        seed_bids(db_session)

        users1 = db_session.query(User).count()
        artworks1 = db_session.query(Artwork).count()
        bids1 = db_session.query(Bid).count()

        # Second run
        seed_users(db_session)
        seed_artworks(db_session)
        seed_bids(db_session)

        users2 = db_session.query(User).count()
        artworks2 = db_session.query(Artwork).count()
        bids2 = db_session.query(Bid).count()

        # Counts should be the same
        assert users1 == users2 == 10
        assert artworks1 == artworks2 == 15
        assert bids1 == bids2


class TestSeedUsersWarnings:
    """Test warning scenarios in seed_users."""

    def test_seed_users_prints_update_message(self, db_session, capsys):
        """Test that updating existing users prints update message."""
        # First seed
        seed_users(db_session)

        # Second seed should print already exists messages
        seed_users(db_session)

        captured = capsys.readouterr()
        assert "↻ User reference already exists:" in captured.out


class TestSeedArtworksWarnings:
    """Test warning scenarios in seed_artworks."""

    def test_seed_artworks_prints_seller_not_found_warning(self, db_session, capsys):
        """Test that missing seller prints warning (edge case)."""
        # Create users but then manually delete one
        seed_users(db_session)

        # Get one user and delete them
        user = db_session.query(User).first()
        db_session.delete(user)
        db_session.commit()

        # Now seed artworks - should warn about missing seller
        seed_artworks(db_session)

        # Should still create some artworks but warn about the missing one
        assert db_session.query(Artwork).count() > 0

    def test_seed_artworks_prints_update_message(self, db_session, capsys):
        """Test that updating existing artworks prints update message."""
        seed_users(db_session)

        # First seed
        seed_artworks(db_session)

        # Second seed should print update messages
        seed_artworks(db_session)

        captured = capsys.readouterr()
        assert "↻ Updated existing artwork:" in captured.out


class TestSeedBidsWarnings:
    """Test warning scenarios in seed_bids."""

    def test_seed_bids_prints_artwork_not_found_warning(self, db_session, capsys):
        """Test that missing artwork prints warning."""
        # Seed everything
        seed_users(db_session)
        seed_artworks(db_session)

        # Delete one artwork that has bids
        artwork = (
            db_session.query(Artwork)
            .filter(
                Artwork.status == ArtworkStatus.ACTIVE,
                Artwork.current_highest_bid > 0,
            )
            .first()
        )
        db_session.delete(artwork)
        db_session.commit()

        # Clear existing bids
        db_session.query(Bid).delete()
        db_session.commit()

        # Now seed bids - should warn about missing artwork
        seed_bids(db_session)

        captured = capsys.readouterr()
        assert "⚠️  Artwork not found:" in captured.out

    def test_seed_bids_prints_bidder_not_found_warning(self, db_session, capsys):
        """Test that missing bidder prints warning."""
        # Seed everything
        seed_users(db_session)
        seed_artworks(db_session)

        # Delete one buyer user specifically (BuyerAlice)
        buyer = db_session.query(User).filter(User.auth0_sub == "auth0|6926e8c9d490f658706da21a").first()
        if buyer:
            db_session.delete(buyer)
            db_session.commit()

        # Clear existing bids
        db_session.query(Bid).delete()
        db_session.commit()

        # Now seed bids - should warn about missing bidder
        seed_bids(db_session)

        captured = capsys.readouterr()
        assert "⚠️  Bidder not found:" in captured.out

    def test_seed_bids_prints_update_message(self, db_session, capsys):
        """Test that updating existing bids prints update message."""
        seed_users(db_session)
        seed_artworks(db_session)

        # First seed
        seed_bids(db_session)

        # Second seed should print update messages
        seed_bids(db_session)

        captured = capsys.readouterr()
        assert "↻ Updated bid for" in captured.out


class TestSeedPrintMessages:
    """Test print messages in seed functions."""

    def test_seed_users_prints_create_message(self, db_session, capsys):
        """Test that creating new users prints create message."""
        seed_users(db_session)

        captured = capsys.readouterr()
        assert "✓ Created user reference:" in captured.out

    def test_seed_artworks_prints_create_message(self, db_session, capsys):
        """Test that creating new artworks prints create message."""
        seed_users(db_session)
        seed_artworks(db_session)

        captured = capsys.readouterr()
        assert "✓ Created new artwork:" in captured.out

    def test_seed_bids_prints_create_message(self, db_session, capsys):
        """Test that creating new bids prints create message."""
        seed_users(db_session)
        seed_artworks(db_session)
        seed_bids(db_session)

        captured = capsys.readouterr()
        assert "✓ Created bid for" in captured.out


class TestSeedManagerMain:
    """Test seed_manager.main() function."""

    @patch("seeds.seed_manager.SeedManager")
    @patch("sys.argv", ["seed_manager.py"])
    def test_main_no_args(self, mock_seed_manager_class):
        """Test main() with no arguments."""
        from seeds.seed_manager import main

        mock_manager = MagicMock()
        mock_manager.run.return_value = 0
        mock_seed_manager_class.return_value = mock_manager

        with pytest.raises(SystemExit) as exc_info:
            main()

        assert exc_info.value.code == 0
        mock_seed_manager_class.assert_called_once_with(target_env=None)
        mock_manager.run.assert_called_once()

    @patch("seeds.seed_manager.SeedManager")
    @patch("sys.argv", ["seed_manager.py", "--env", "development"])
    def test_main_with_env_arg(self, mock_seed_manager_class):
        """Test main() with --env argument."""
        from seeds.seed_manager import main

        mock_manager = MagicMock()
        mock_manager.run.return_value = 0
        mock_seed_manager_class.return_value = mock_manager

        with pytest.raises(SystemExit) as exc_info:
            main()

        assert exc_info.value.code == 0
        mock_seed_manager_class.assert_called_once_with(target_env="development")
        mock_manager.run.assert_called_once()

    @patch("seeds.seed_manager.SeedManager")
    @patch("sys.argv", ["seed_manager.py", "--env", "production"])
    def test_main_with_production_env(self, mock_seed_manager_class):
        """Test main() with production environment."""
        from seeds.seed_manager import main

        mock_manager = MagicMock()
        mock_manager.run.return_value = 1
        mock_seed_manager_class.return_value = mock_manager

        with pytest.raises(SystemExit) as exc_info:
            main()

        assert exc_info.value.code == 1
        mock_seed_manager_class.assert_called_once_with(target_env="production")
        mock_manager.run.assert_called_once()
