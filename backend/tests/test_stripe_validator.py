"""Tests for Stripe configuration validator."""

from unittest.mock import patch
import stripe

from utils.stripe_validator import StripeValidator


class TestStripeValidator:
    """Test StripeValidator class."""

    @patch("utils.stripe_validator.settings")
    def test_validate_configuration_all_valid(self, mock_settings):
        """Test validation with all valid settings."""
        mock_settings.stripe_secret_key = "sk_test_valid_key"
        mock_settings.stripe_publishable_key = "pk_test_valid_key"
        mock_settings.stripe_webhook_secret = "whsec_valid_secret"
        mock_settings.environment = "test"

        with patch("stripe.Account.retrieve"):
            is_valid, errors = StripeValidator.validate_configuration()

        assert is_valid is True
        assert len(errors) == 0

    @patch("utils.stripe_validator.settings")
    def test_validate_configuration_missing_secret_key(self, mock_settings):
        """Test validation with missing secret key."""
        mock_settings.stripe_secret_key = ""
        mock_settings.stripe_publishable_key = "pk_test_valid_key"
        mock_settings.stripe_webhook_secret = "whsec_valid_secret"

        is_valid, errors = StripeValidator.validate_configuration()

        assert is_valid is False
        assert len(errors) > 0
        assert any("STRIPE_SECRET_KEY is not set" in error for error in errors)

    @patch("utils.stripe_validator.settings")
    def test_validate_configuration_missing_publishable_key(self, mock_settings):
        """Test validation with missing publishable key."""
        mock_settings.stripe_secret_key = "sk_test_valid_key"
        mock_settings.stripe_publishable_key = ""
        mock_settings.stripe_webhook_secret = "whsec_valid_secret"

        is_valid, errors = StripeValidator.validate_configuration()

        assert is_valid is False
        assert len(errors) > 0
        assert any("STRIPE_PUBLISHABLE_KEY is not set" in error for error in errors)

    @patch("utils.stripe_validator.settings")
    def test_validate_configuration_placeholder_values(self, mock_settings):
        """Test validation with placeholder values."""
        mock_settings.stripe_secret_key = "your_stripe_secret_key"
        mock_settings.stripe_publishable_key = "your_stripe_publishable_key"
        mock_settings.stripe_webhook_secret = "whsec_valid_secret"

        is_valid, errors = StripeValidator.validate_configuration()

        assert is_valid is False
        assert len(errors) >= 2
        assert any("placeholder" in error.lower() for error in errors)

    @patch("utils.stripe_validator.settings")
    def test_validate_configuration_invalid_key_format(self, mock_settings):
        """Test validation with invalid key formats."""
        mock_settings.stripe_secret_key = "invalid_secret_key"
        mock_settings.stripe_publishable_key = "invalid_publishable_key"
        mock_settings.stripe_webhook_secret = "whsec_valid_secret"

        is_valid, errors = StripeValidator.validate_configuration()

        assert is_valid is False
        assert len(errors) >= 2
        assert any("invalid format" in error.lower() for error in errors)

    @patch("utils.stripe_validator.settings")
    def test_validate_configuration_missing_webhook_secret(self, mock_settings):
        """Test validation with missing webhook secret."""
        mock_settings.stripe_secret_key = "sk_test_valid_key"
        mock_settings.stripe_publishable_key = "pk_test_valid_key"
        mock_settings.stripe_webhook_secret = None
        mock_settings.environment = "test"

        with patch("stripe.Account.retrieve"):
            is_valid, errors = StripeValidator.validate_configuration()

        assert is_valid is False
        assert len(errors) == 1
        assert any("STRIPE_WEBHOOK_SECRET is not set" in error for error in errors)

    @patch("utils.stripe_validator.settings")
    def test_get_stripe_status_configured(self, mock_settings):
        """Test get_stripe_status with valid configuration."""
        mock_settings.stripe_secret_key = "sk_test_valid_key"
        mock_settings.stripe_publishable_key = "pk_test_valid_key"
        mock_settings.stripe_webhook_secret = "whsec_valid_secret"
        mock_settings.environment = "test"

        with patch("stripe.Account.retrieve"):
            status = StripeValidator.get_stripe_status()

        assert status["configured"] is True
        assert status["secret_key_set"] is True
        assert status["publishable_key_set"] is True
        assert status["webhook_secret_set"] is True
        assert len(status["errors"]) == 0

    @patch("utils.stripe_validator.settings")
    def test_get_stripe_status_not_configured(self, mock_settings):
        """Test get_stripe_status with invalid configuration."""
        mock_settings.stripe_secret_key = ""
        mock_settings.stripe_publishable_key = ""
        mock_settings.stripe_webhook_secret = None

        status = StripeValidator.get_stripe_status()

        assert status["configured"] is False
        assert status["secret_key_set"] is False
        assert status["publishable_key_set"] is False
        assert status["webhook_secret_set"] is False
        assert len(status["errors"]) > 0

    @patch("utils.stripe_validator.settings")
    @patch("stripe.Account.retrieve")
    def test_validate_configuration_stripe_auth_error(self, mock_retrieve, mock_settings):
        """Test validation with Stripe authentication error."""
        mock_settings.stripe_secret_key = "sk_test_invalid"
        mock_settings.stripe_publishable_key = "pk_test_valid_key"
        mock_settings.stripe_webhook_secret = "whsec_secret"
        mock_retrieve.side_effect = stripe.error.AuthenticationError("Invalid key")

        is_valid, errors = StripeValidator.validate_configuration()

        assert is_valid is False
        assert any("authentication failed" in error.lower() for error in errors)

    @patch("utils.stripe_validator.settings")
    @patch("stripe.Account.retrieve")
    def test_validate_configuration_stripe_generic_error(self, mock_retrieve, mock_settings):
        """Test validation with generic Stripe error."""
        mock_settings.stripe_secret_key = "sk_test_valid_key"
        mock_settings.stripe_publishable_key = "pk_test_valid_key"
        mock_settings.stripe_webhook_secret = "whsec_secret"
        mock_retrieve.side_effect = Exception("Network error")

        is_valid, errors = StripeValidator.validate_configuration()

        assert is_valid is False
        assert any("Network error" in error for error in errors)

    @patch("utils.stripe_validator.settings")
    @patch("builtins.print")
    def test_print_validation_report_valid(self, mock_print, mock_settings):
        """Test print_validation_report with valid configuration."""
        mock_settings.stripe_secret_key = "sk_test_valid_key_long_enough"
        mock_settings.stripe_publishable_key = "pk_test_valid_key_long_enough"
        mock_settings.stripe_webhook_secret = "whsec_secret"
        mock_settings.environment = "test"

        with patch("stripe.Account.retrieve"):
            result = StripeValidator.print_validation_report()

        assert result is True
        mock_print.assert_called()

    @patch("utils.stripe_validator.settings")
    @patch("builtins.print")
    def test_print_validation_report_invalid(self, mock_print, mock_settings):
        """Test print_validation_report with invalid configuration."""
        mock_settings.stripe_secret_key = ""
        mock_settings.stripe_publishable_key = ""
        mock_settings.stripe_webhook_secret = None

        result = StripeValidator.print_validation_report()

        assert result is False
        mock_print.assert_called()

    @patch("utils.stripe_validator.settings")
    def test_validate_none_keys(self, mock_settings):
        """Test validation with None values."""
        mock_settings.stripe_secret_key = None
        mock_settings.stripe_publishable_key = None
        mock_settings.stripe_webhook_secret = None

        is_valid, errors = StripeValidator.validate_configuration()

        assert is_valid is False
        assert len(errors) >= 3
