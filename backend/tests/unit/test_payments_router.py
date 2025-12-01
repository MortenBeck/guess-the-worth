"""Unit tests for payments router functions."""

from unittest.mock import patch

import pytest


class TestStripeHealthCheckEndpoint:
    """Test the Stripe health check endpoint logic."""

    @pytest.mark.asyncio
    @patch("routers.payments.StripeValidator.get_stripe_status")
    async def test_stripe_health_check_configured(self, mock_get_status):
        """Test health check logic when Stripe is configured."""
        from routers.payments import stripe_health_check

        mock_get_status.return_value = {
            "configured": True,
            "secret_key_set": True,
            "publishable_key_set": True,
            "webhook_secret_set": True,
            "errors": [],
        }

        result = await stripe_health_check()

        assert result["stripe_configured"] is True
        assert result["keys_configured"]["secret_key"] is True
        assert result["keys_configured"]["publishable_key"] is True
        assert result["keys_configured"]["webhook_secret"] is True
        assert result["ready_for_payments"] is True
        assert len(result["errors"]) == 0
        assert "help" in result

    @pytest.mark.asyncio
    @patch("routers.payments.StripeValidator.get_stripe_status")
    async def test_stripe_health_check_not_configured(self, mock_get_status):
        """Test health check logic when Stripe is not configured."""
        from routers.payments import stripe_health_check

        mock_get_status.return_value = {
            "configured": False,
            "secret_key_set": False,
            "publishable_key_set": False,
            "webhook_secret_set": False,
            "errors": ["STRIPE_SECRET_KEY is not set"],
        }

        result = await stripe_health_check()

        assert result["stripe_configured"] is False
        assert result["keys_configured"]["secret_key"] is False
        assert result["ready_for_payments"] is False
        assert len(result["errors"]) == 1
        assert "STRIPE_SECRET_KEY is not set" in result["errors"]
