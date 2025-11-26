import api from './api';

/**
 * Payment Service - Stripe payment integration
 */
const paymentService = {
  /**
   * Create a payment intent for a winning bid
   * @param {number} bidId - The ID of the winning bid
   * @returns {Promise<Object>} Payment intent data with client_secret
   */
  async createPaymentIntent(bidId) {
    try {
      const response = await api.post('/api/payments/create-intent', {
        bid_id: bidId,
        amount: 0, // Amount is fetched from the bid on the backend
      });
      return response.data;
    } catch (error) {
      console.error('Error creating payment intent:', error);
      throw error;
    }
  },

  /**
   * Get all payments for the current user
   * @returns {Promise<Array>} List of payments
   */
  async getMyPayments() {
    try {
      const response = await api.get('/api/payments/my-payments');
      return response.data;
    } catch (error) {
      console.error('Error fetching payments:', error);
      throw error;
    }
  },

  /**
   * Get a specific payment by ID
   * @param {number} paymentId - The payment ID
   * @returns {Promise<Object>} Payment details
   */
  async getPayment(paymentId) {
    try {
      const response = await api.get(`/api/payments/${paymentId}`);
      return response.data;
    } catch (error) {
      console.error('Error fetching payment:', error);
      throw error;
    }
  },

  /**
   * Get payment for an artwork (seller/admin only)
   * @param {number} artworkId - The artwork ID
   * @returns {Promise<Object>} Payment details
   */
  async getArtworkPayment(artworkId) {
    try {
      const response = await api.get(`/api/payments/artwork/${artworkId}`);
      return response.data;
    } catch (error) {
      console.error('Error fetching artwork payment:', error);
      throw error;
    }
  },
};

export default paymentService;
