"""Stripe configuration validator and helper utilities."""

import sys
from typing import Dict, List, Tuple

import stripe

from config.settings import settings


class StripeValidator:
    """Validates Stripe configuration and provides helpful error messages."""

    @staticmethod
    def validate_configuration() -> Tuple[bool, List[str]]:
        """
        Validate Stripe configuration.

        Returns:
            Tuple of (is_valid, list_of_errors)
        """
        errors = []

        # Check if Stripe keys are configured
        if not settings.stripe_secret_key or settings.stripe_secret_key == "":
            errors.append(
                "❌ STRIPE_SECRET_KEY is not set in environment variables.\n"
                "   Get your key from: https://dashboard.stripe.com/test/apikeys\n"
                "   Add to backend/.env: STRIPE_SECRET_KEY=sk_test_...\n"
            )

        if not settings.stripe_publishable_key or settings.stripe_publishable_key == "":
            errors.append(
                "❌ STRIPE_PUBLISHABLE_KEY is not set in environment variables.\n"
                "   Get your key from: https://dashboard.stripe.com/test/apikeys\n"
                "   Add to backend/.env: STRIPE_PUBLISHABLE_KEY=pk_test_...\n"
            )

        # Check if keys have default/placeholder values
        if settings.stripe_secret_key and "your_stripe" in settings.stripe_secret_key.lower():
            errors.append(
                "❌ STRIPE_SECRET_KEY has a placeholder value.\n"
                "   Replace with actual key from: https://dashboard.stripe.com/test/apikeys\n"
            )

        if (
            settings.stripe_publishable_key
            and "your_stripe" in settings.stripe_publishable_key.lower()
        ):
            errors.append(
                "❌ STRIPE_PUBLISHABLE_KEY has a placeholder value.\n"
                "   Replace with actual key from: https://dashboard.stripe.com/test/apikeys\n"
            )

        # Check key format
        if settings.stripe_secret_key and not settings.stripe_secret_key.startswith("sk_"):
            errors.append(
                "❌ STRIPE_SECRET_KEY has invalid format.\n"
                "   Secret keys should start with 'sk_test_' (test) or 'sk_live_' (production)\n"
            )

        if settings.stripe_publishable_key and not settings.stripe_publishable_key.startswith(
            "pk_"
        ):
            errors.append(
                "❌ STRIPE_PUBLISHABLE_KEY has invalid format.\n"
                "   Publishable keys should start with 'pk_test_' (test) or "
                "'pk_live_' (production)\n"
            )

        # Check webhook secret
        if not settings.stripe_webhook_secret:
            errors.append(
                "⚠️  STRIPE_WEBHOOK_SECRET is not set.\n"
                "   Webhooks will fail signature verification!\n"
                "   For local dev: Run 'stripe listen --forward-to "
                "http://localhost:8000/api/payments/webhook'\n"
                "   For production: Configure webhook in "
                "https://dashboard.stripe.com/webhooks\n"
            )

        # Test Stripe API connection if keys are provided
        if (
            settings.stripe_secret_key
            and settings.stripe_secret_key.startswith("sk_")
            and "your_stripe" not in settings.stripe_secret_key.lower()
        ):
            try:
                stripe.api_key = settings.stripe_secret_key
                # Try to retrieve account info
                stripe.Account.retrieve()
                print("✅ Stripe API connection successful!")
            except stripe.error.AuthenticationError:
                errors.append(
                    "❌ STRIPE_SECRET_KEY is invalid (authentication failed).\n"
                    "   Verify your key at: https://dashboard.stripe.com/test/apikeys\n"
                )
            except Exception as e:
                errors.append(f"❌ Stripe API error: {str(e)}\n")

        return (len(errors) == 0, errors)

    @staticmethod
    def print_validation_report() -> bool:
        """
        Print validation report to console.

        Returns:
            True if configuration is valid, False otherwise
        """
        print("\n" + "=" * 80)
        print("🔷 STRIPE CONFIGURATION VALIDATION")
        print("=" * 80 + "\n")

        is_valid, errors = StripeValidator.validate_configuration()

        if is_valid:
            print("✅ All Stripe configuration checks passed!\n")
            print(f"   Environment: {settings.environment}")
            print(f"   Secret Key: {settings.stripe_secret_key[:20]}...")
            print(f"   Publishable Key: {settings.stripe_publishable_key[:20]}...")
            print(
                f"   Webhook Secret: {'Set ✅' if settings.stripe_webhook_secret else 'Not Set ⚠️'}"
            )
            print("\n" + "=" * 80 + "\n")
            return True
        else:
            print("❌ STRIPE CONFIGURATION ERRORS FOUND:\n")
            for error in errors:
                print(error)
            print("=" * 80)
            print("\n📚 For setup instructions, see: STRIPE_SETUP_GUIDE.md")
            print("=" * 80 + "\n")
            return False

    @staticmethod
    def get_stripe_status() -> Dict[str, any]:
        """
        Get Stripe configuration status as dictionary.

        Useful for health check endpoints.

        Returns:
            Dictionary with Stripe status information
        """
        is_valid, errors = StripeValidator.validate_configuration()

        return {
            "configured": is_valid,
            "secret_key_set": bool(
                settings.stripe_secret_key
                and settings.stripe_secret_key != ""
                and "your_stripe" not in settings.stripe_secret_key.lower()
            ),
            "publishable_key_set": bool(
                settings.stripe_publishable_key
                and settings.stripe_publishable_key != ""
                and "your_stripe" not in settings.stripe_publishable_key.lower()
            ),
            "webhook_secret_set": bool(settings.stripe_webhook_secret),
            "errors": errors if not is_valid else [],
        }


def check_stripe_config():
    """CLI command to validate Stripe configuration."""
    is_valid = StripeValidator.print_validation_report()
    sys.exit(0 if is_valid else 1)


if __name__ == "__main__":
    check_stripe_config()
