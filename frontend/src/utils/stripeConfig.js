/**
 * Stripe Configuration Utility
 * Validates Stripe environment variables and provides user-friendly error messages
 */

/**
 * Check if Stripe is properly configured
 * @returns {Object} Configuration status with errors if any
 */
export function checkStripeConfig() {
  const publishableKey = import.meta.env.VITE_STRIPE_PUBLISHABLE_KEY;
  const errors = [];

  if (!publishableKey) {
    errors.push("Missing VITE_STRIPE_PUBLISHABLE_KEY environment variable");
  } else if (!publishableKey.startsWith("pk_")) {
    errors.push("Invalid Stripe publishable key format (should start with 'pk_')");
  }

  return {
    configured: errors.length === 0,
    errors,
    publishableKey,
  };
}

/**
 * Get user-friendly error message for Stripe errors
 * @param {Error|Object} error - Stripe error object
 * @returns {string} User-friendly error message
 */
export function getStripeErrorMessage(error) {
  // Handle Stripe error objects
  if (error?.type) {
    switch (error.type) {
      case "card_error":
        return error.message || "Your card was declined. Please try a different payment method.";
      case "validation_error":
        return error.message || "Invalid payment information. Please check your details.";
      case "api_error":
        return "Payment processing error. Please try again later.";
      case "authentication_error":
        return "Payment authentication failed. Please try again.";
      case "rate_limit_error":
        return "Too many requests. Please wait a moment and try again.";
      case "invalid_request_error":
        return error.message || "Invalid payment request. Please refresh and try again.";
      default:
        return error.message || "An unexpected error occurred. Please try again.";
    }
  }

  // Handle generic errors
  if (error?.message) {
    return error.message;
  }

  // Fallback
  return "An unexpected error occurred. Please try again.";
}
