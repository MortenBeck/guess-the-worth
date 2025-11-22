import { config } from "../config/env";

// Create a fetch-based API client
const createApiClient = () => {
  const baseURL = `${config.API_BASE_URL}/api`;

  const request = async (endpoint, options = {}) => {
    const token = localStorage.getItem("access_token");

    const defaultHeaders = {
      "Content-Type": "application/json",
      ...(token && { Authorization: `Bearer ${token}` }),
    };

    const url = `${baseURL}${endpoint}`;
    const fetchOptions = {
      ...options,
      headers: {
        ...defaultHeaders,
        ...options.headers,
      },
    };

    try {
      const response = await fetch(url, fetchOptions);

      // Parse response body (try JSON, fallback to null)
      let responseData = null;
      try {
        responseData = await response.json();
      } catch {
        // Response body is not JSON or empty
        responseData = null;
      }

      if (!response.ok) {
        // Create detailed error object
        const error = new Error(
          responseData?.detail || `HTTP ${response.status}: ${response.statusText}`
        );
        error.status = response.status;
        error.data = responseData;

        // Handle specific status codes
        if (response.status === 401) {
          error.message = "Your session has expired. Please log in again.";
          localStorage.removeItem("access_token");
          // Don't redirect immediately - let the component handle it
        }

        if (response.status === 403) {
          error.message = responseData?.detail || "You do not have permission to perform this action";
        }

        if (response.status === 404) {
          error.message = responseData?.detail || "The requested resource was not found";
        }

        if (response.status === 400) {
          error.message = responseData?.detail || "Invalid request. Please check your input.";
        }

        if (response.status >= 500) {
          error.message = "Server error. Please try again later.";
        }

        throw error;
      }

      return { data: responseData };
    } catch (error) {
      // If error already has a status, it's an HTTP error we already handled
      if (error.status) {
        throw error;
      }

      // Handle network errors (backend offline, no internet, etc.)
      if (error instanceof TypeError && error.message === "Failed to fetch") {
        const networkError = new Error(
          "Unable to connect to server. Please check your internet connection."
        );
        networkError.isNetworkError = true;
        throw networkError;
      }

      // Re-throw other unexpected errors
      throw error;
    }
  };

  return {
    get: (endpoint, options = {}) => {
      const { params, ...restOptions } = options;
      const url = params ? `${endpoint}?${new URLSearchParams(params)}` : endpoint;
      return request(url, { method: "GET", ...restOptions });
    },
    post: (endpoint, data, options = {}) => {
      const isFormData = data instanceof FormData;
      return request(endpoint, {
        method: "POST",
        body: isFormData ? data : JSON.stringify(data),
        ...options,
        headers: isFormData
          ? options.headers
          : { "Content-Type": "application/json", ...options.headers },
      });
    },
    put: (endpoint, data, options = {}) =>
      request(endpoint, {
        method: "PUT",
        body: JSON.stringify(data),
        ...options,
      }),
    delete: (endpoint, options = {}) =>
      request(endpoint, {
        method: "DELETE",
        ...options,
      }),
  };
};

const api = createApiClient();

// API service functions
export const artworkService = {
  getAll: (params = {}) => api.get("/artworks/", { params }),
  getById: (id) => api.get(`/artworks/${id}`),
  getFeatured: () => api.get("/artworks/", { params: { limit: 6 } }), // Get first 6 as featured
  getMyArtworks: () => api.get("/artworks/my-artworks"),
  create: (data) => api.post("/artworks/", data),
  uploadImage: (id, file) => {
    const formData = new FormData();
    formData.append("file", file);
    return api.post(`/artworks/${id}/upload-image`, formData, {
      headers: {}, // Remove Content-Type to let browser set it for FormData
    });
  },
};

export const bidService = {
  getByArtwork: (artworkId) => api.get(`/bids/artwork/${artworkId}`),
  getMyBids: () => api.get("/bids/my-bids"),
  create: (data) => api.post("/bids/", data),
};

export const userService = {
  getAll: (params = {}) => api.get("/users/", { params }),
  getById: (id) => api.get(`/users/${id}`),
  getCurrentUser: () => api.get("/auth/me"), // Token automatically added by interceptor
  register: (data) => api.post("/auth/register", data),
  updateProfile: (data) => api.put("/users/me", data),
};

export const statsService = {
  getPlatformStats: async () => {
    // Since the platform stats endpoint doesn't exist yet, we'll fetch data and calculate stats
    try {
      const [artworksRes, usersRes] = await Promise.all([
        api.get("/artworks/", { params: { limit: 1000 } }),
        api.get("/users/", { params: { limit: 1000 } }),
      ]);

      const artworks = artworksRes.data;
      const users = usersRes.data;

      const totalBids = artworks.reduce(
        (sum, artwork) => sum + (artwork.current_highest_bid || 0),
        0
      );
      const activeArtworks = artworks.filter((a) => a.status === "active").length;
      const artists = users.filter((u) => u.role === "seller" || u.role === "admin").length;

      return {
        totalArtworks: activeArtworks,
        totalBids: Math.round(totalBids),
        totalArtists: artists,
        liveStatus: "24/7",
      };
    } catch {
      // Return mock data if API fails
      return {
        totalArtworks: 1247,
        totalBids: 89000,
        totalArtists: 156,
        liveStatus: "24/7",
      };
    }
  },

  getUserStats: () => api.get("/stats/user"),

  getSellerStats: () => api.get("/stats/seller"),
};

export default api;
