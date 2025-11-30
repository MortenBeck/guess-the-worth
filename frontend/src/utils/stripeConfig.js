/**
 * Stripe Configuration Utilities
 *
 * Validates Stripe configuration and provides helpful error messages
 */

/**
 * Check if Stripe is properly configured
 * @returns {Object} Configuration status
 */
export const checkStripeConfig = () => {
  const publishableKey = import.meta.env.VITE_STRIPE_PUBLISHABLE_KEY;

  const errors = [];
  const warnings = [];

  // Check if publishable key is set
  if (!publishableKey || publishableKey === "") {
    errors.push(
      "VITE_STRIPE_PUBLISHABLE_KEY is not set in environment variables. " +
        "Add it to frontend/.env file."
    );
  }

  // Check if key has placeholder value
  if (publishableKey && publishableKey.includes("your_stripe")) {
    errors.push(
      "VITE_STRIPE_PUBLISHABLE_KEY has a placeholder value. " +
        "Replace with actual key from https://dashboard.stripe.com/test/apikeys"
    );
  }

  // Check key format
  if (publishableKey && !publishableKey.startsWith("pk_")) {
    errors.push(
      "VITE_STRIPE_PUBLISHABLE_KEY has invalid format. " +
        "Publishable keys should start with 'pk_test_' or 'pk_live_'"
    );
  }

  // Warn if using test key in production
  if (publishableKey && publishableKey.startsWith("pk_test_") && import.meta.env.PROD) {
    warnings.push(
      "Using Stripe TEST key in production mode. " +
        "Switch to live key (pk_live_...) for production."
    );
  }

  return {
    configured: errors.length === 0,
    publishableKey: publishableKey ? publishableKey.substring(0, 20) + "..." : null,
    errors,
    warnings,
  };
};

/**
 * Log Stripe configuration status to console
 */
export const logStripeStatus = () => {
  const status = checkStripeConfig();

  console.group("🔷 Stripe Configuration");

  if (status.configured) {
    console.log("✅ Stripe is properly configured");
    console.log(`   Publishable Key: ${status.publishableKey}`);

    if (status.warnings.length > 0) {
      console.warn("⚠️  Warnings:");
      status.warnings.forEach((warning) => console.warn(`   - ${warning}`));
    }
  } else {
    console.error("❌ Stripe configuration errors:");
    status.errors.forEach((error) => console.error(`   - ${error}`));
    console.log("\n📚 See STRIPE_SETUP_GUIDE.md for setup instructions");
  }

  console.groupEnd();

  return status;
};

/**
 * Get user-friendly error message for Stripe errors
 * @param {Error} error - Stripe error object
 * @returns {string} User-friendly error message
 */
export const getStripeErrorMessage = (error) => {
  // Handle Stripe-specific errors
  if (error?.type) {
    switch (error.type) {
      case "card_error":
        return error.message || "Your card was declined. Please try a different card.";

      case "validation_error":
        return "Invalid payment information. Please check your card details.";

      case "invalid_request_error":
        return "Payment request failed. Please try again or contact support.";

      case "api_error":
      case "api_connection_error":
        return "Unable to process payment. Please check your internet connection and try again.";

      case "authentication_error":
        return "Payment authentication failed. Please contact support.";

      case "rate_limit_error":
        return "Too many payment attempts. Please wait a moment and try again.";

      default:
        return error.message || "Payment failed. Please try again.";
    }
  }

  // Handle network errors
  if (error?.response?.status === 503) {
    return (
      "Payment processing is temporarily unavailable. " +
      "Our team has been notified. Please try again later."
    );
  }

  if (error?.response?.status === 500) {
    return "Payment server error. Please try again or contact support.";
  }

  // Handle API errors
  if (error?.response?.data?.detail) {
    return error.response.data.detail;
  }

  // Generic error
  return error?.message || "Payment failed. Please try again.";
};

/**
 * Format amount for display (cents to dollars)
 * @param {number} cents - Amount in cents
 * @returns {string} Formatted amount (e.g., "$12.34")
 */
export const formatAmount = (cents) => {
  const dollars = cents / 100;
  return `$${dollars.toFixed(2)}`;
};

/**
 * Convert dollars to cents for Stripe
 * @param {number} dollars - Amount in dollars
 * @returns {number} Amount in cents
 */
export const toCents = (dollars) => {
  return Math.round(dollars * 100);
};

/**
 * Validate credit card number format (basic Luhn check)
 * @param {string} cardNumber - Card number
 * @returns {boolean} True if valid format
 */
export const validateCardNumber = (cardNumber) => {
  // Remove spaces and dashes
  const cleaned = cardNumber.replace(/[\s-]/g, "");

  // Check if it's all digits and 13-19 characters
  if (!/^\d{13,19}$/.test(cleaned)) {
    return false;
  }

  // Luhn algorithm
  let sum = 0;
  let isEven = false;

  for (let i = cleaned.length - 1; i >= 0; i--) {
    let digit = parseInt(cleaned[i], 10);

    if (isEven) {
      digit *= 2;
      if (digit > 9) {
        digit -= 9;
      }
    }

    sum += digit;
    isEven = !isEven;
  }

  return sum % 10 === 0;
};

export default {
  checkStripeConfig,
  logStripeStatus,
  getStripeErrorMessage,
  formatAmount,
  toCents,
  validateCardNumber,
};
