import { useState, useEffect } from 'react';
import { loadStripe } from '@stripe/stripe-js';
import {
  Elements,
  PaymentElement,
  useStripe,
  useElements,
} from '@stripe/react-stripe-js';
import paymentService from '../services/paymentService';

// Initialize Stripe with publishable key
const stripePromise = loadStripe(import.meta.env.VITE_STRIPE_PUBLISHABLE_KEY);

/**
 * Payment form component (must be inside Elements provider)
 */
function PaymentForm({ clientSecret, onSuccess, onError, amount, artworkTitle }) {
  const stripe = useStripe();
  const elements = useElements();
  const [isProcessing, setIsProcessing] = useState(false);
  const [errorMessage, setErrorMessage] = useState(null);

  const handleSubmit = async (e) => {
    e.preventDefault();

    if (!stripe || !elements) {
      return;
    }

    setIsProcessing(true);
    setErrorMessage(null);

    try {
      const { error, paymentIntent } = await stripe.confirmPayment({
        elements,
        confirmParams: {
          return_url: `${window.location.origin}/payment-success`,
        },
        redirect: 'if_required', // Stay on page if no redirect needed
      });

      if (error) {
        setErrorMessage(error.message);
        onError(error);
      } else if (paymentIntent && paymentIntent.status === 'succeeded') {
        onSuccess(paymentIntent);
      }
    } catch (err) {
      setErrorMessage('Payment failed. Please try again.');
      onError(err);
    } finally {
      setIsProcessing(false);
    }
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-4">
      <div className="mb-4">
        <h3 className="text-lg font-semibold mb-2">Payment Details</h3>
        <p className="text-sm text-gray-600 mb-1">
          Artwork: <span className="font-medium">{artworkTitle}</span>
        </p>
        <p className="text-sm text-gray-600">
          Amount: <span className="font-medium">${parseFloat(amount).toFixed(2)}</span>
        </p>
      </div>

      <PaymentElement />

      {errorMessage && (
        <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded">
          {errorMessage}
        </div>
      )}

      <button
        type="submit"
        disabled={!stripe || isProcessing}
        className="w-full bg-blue-600 hover:bg-blue-700 disabled:bg-gray-400 text-white font-semibold py-3 px-4 rounded transition duration-200"
      >
        {isProcessing ? 'Processing...' : `Pay $${parseFloat(amount).toFixed(2)}`}
      </button>

      <p className="text-xs text-gray-500 text-center">
        Powered by Stripe • Your payment information is secure
      </p>
    </form>
  );
}

/**
 * Payment Modal Component
 * Shows when user wins a bid and needs to complete payment
 */
function PaymentModal({ isOpen, onClose, bidId, amount, artworkTitle }) {
  const [clientSecret, setClientSecret] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    if (isOpen && bidId) {
      createPaymentIntent();
    }
  }, [isOpen, bidId]);

  const createPaymentIntent = async () => {
    setLoading(true);
    setError(null);

    try {
      const data = await paymentService.createPaymentIntent(bidId);
      setClientSecret(data.client_secret);
    } catch (err) {
      console.error('Failed to create payment intent:', err);
      setError(
        err.response?.data?.detail || 'Failed to initialize payment. Please try again.'
      );
    } finally {
      setLoading(false);
    }
  };

  const handleSuccess = (paymentIntent) => {
    console.log('Payment successful!', paymentIntent);
    alert('Payment successful! The artwork is now yours.');
    onClose();
  };

  const handleError = (error) => {
    console.error('Payment error:', error);
  };

  if (!isOpen) return null;

  const stripeOptions = clientSecret
    ? {
        clientSecret,
        appearance: {
          theme: 'stripe',
          variables: {
            colorPrimary: '#2563eb',
          },
        },
      }
    : null;

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
      <div className="bg-white rounded-lg shadow-xl max-w-md w-full p-6">
        <div className="flex justify-between items-center mb-4">
          <h2 className="text-2xl font-bold">Complete Payment</h2>
          <button
            onClick={onClose}
            className="text-gray-500 hover:text-gray-700 text-2xl leading-none"
            aria-label="Close"
          >
            ×
          </button>
        </div>

        {loading && (
          <div className="text-center py-8">
            <div className="inline-block animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
            <p className="mt-4 text-gray-600">Initializing payment...</p>
          </div>
        )}

        {error && (
          <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded mb-4">
            {error}
            <button
              onClick={createPaymentIntent}
              className="block mt-2 text-sm underline"
            >
              Try again
            </button>
          </div>
        )}

        {!loading && !error && clientSecret && stripeOptions && (
          <Elements stripe={stripePromise} options={stripeOptions}>
            <PaymentForm
              clientSecret={clientSecret}
              onSuccess={handleSuccess}
              onError={handleError}
              amount={amount}
              artworkTitle={artworkTitle}
            />
          </Elements>
        )}
      </div>
    </div>
  );
}

export default PaymentModal;
