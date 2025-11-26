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
        // Handle specific status codes with proper message assignment
        let errorMessage;

        if (response.status === 401) {
          errorMessage = "Your session has expired. Please log in again.";
          localStorage.removeItem("access_token");
          // Don't redirect immediately - let the component handle it
        } else if (response.status === 403) {
          errorMessage = responseData?.detail || "You do not have permission to perform this action";
        } else if (response.status === 404) {
          errorMessage = responseData?.detail || "The requested resource was not found";
        } else if (response.status === 400) {
          errorMessage = responseData?.detail || "Invalid request. Please check your input.";
        } else if (response.status >= 500) {
          errorMessage = "Server error. Please try again later.";
        } else {
          errorMessage = responseData?.detail || `HTTP ${response.status}: ${response.statusText}`;
        }

        // Create detailed error object
        const error = new Error(errorMessage);
        error.status = response.status;
        error.data = responseData;

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
    try {
      // Fetch artworks and users data
      const [artworksResponse, usersResponse] = await Promise.all([
        api.get("/artworks/"),
        api.get("/users/")
      ]);

      const artworks = artworksResponse.data || [];
      const users = usersResponse.data || [];

      // Calculate stats from the data
      const activeArtworks = artworks.filter(a => a.status === "active");
      const totalBids = artworks.reduce((sum, a) => sum + (a.current_highest_bid || 0), 0);
      const artists = users.filter(u => u.role === "seller" || u.role === "admin");

      return {
        totalArtworks: activeArtworks.length,
        totalBids: totalBids,
        totalArtists: artists.length,
        liveStatus: "24/7"
      };
    } catch (error) {
      // Return mock data if API fails
      return {
        totalArtworks: 1247,
        totalBids: 89000,
        totalArtists: 156,
        liveStatus: "24/7"
      };
    }
  },
  getUserStats: () => api.get("/stats/user"),
  getSellerStats: () => api.get("/stats/seller"),
};

export default api;
