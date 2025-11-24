import api from "./api";

/**
 * Admin API service functions
 */
export const adminApi = {
  // Platform overview
  getPlatformOverview: async () => {
    const response = await api.get("/api/admin/stats/overview");
    return response.data;
  },

  // User management
  getUsers: async (params = {}) => {
    const response = await api.get("/api/admin/users", { params });
    return response.data;
  },

  getUserDetails: async (userId) => {
    const response = await api.get(`/api/admin/users/${userId}`);
    return response.data;
  },

  banUser: async (userId, reason) => {
    const response = await api.put(`/api/admin/users/${userId}/ban`, null, { params: { reason } });
    return response.data;
  },

  // Transactions
  getTransactions: async (params = {}) => {
    const response = await api.get("/api/admin/transactions", { params });
    return response.data;
  },

  // System health
  getSystemHealth: async () => {
    const response = await api.get("/api/admin/system/health");
    return response.data;
  },

  // Flagged auctions
  getFlaggedAuctions: async () => {
    const response = await api.get("/api/admin/flagged-auctions");
    return response.data;
  },

  // Audit logs
  getAuditLogs: async (params = {}) => {
    const response = await api.get("/api/admin/audit-logs", { params });
    return response.data;
  },
};

export default adminApi;
