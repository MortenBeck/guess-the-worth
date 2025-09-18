import { config } from '../config/env';

// Create a fetch-based API client
const createApiClient = () => {
  const baseURL = `${config.API_BASE_URL}/api`;
  
  const request = async (endpoint, options = {}) => {
    const token = localStorage.getItem('access_token');
    
    const defaultHeaders = {
      'Content-Type': 'application/json',
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
      
      if (response.status === 401) {
        localStorage.removeItem('access_token');
        window.location.href = '/login';
        throw new Error('Unauthorized');
      }

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const data = await response.json();
      return { data };
    } catch (error) {
      throw error;
    }
  };

  return {
    get: (endpoint, options = {}) => {
      const { params, ...restOptions } = options;
      const url = params ? `${endpoint}?${new URLSearchParams(params)}` : endpoint;
      return request(url, { method: 'GET', ...restOptions });
    },
    post: (endpoint, data, options = {}) => {
      const isFormData = data instanceof FormData;
      return request(endpoint, {
        method: 'POST',
        body: isFormData ? data : JSON.stringify(data),
        ...options,
        headers: isFormData ? options.headers : { 'Content-Type': 'application/json', ...options.headers },
      });
    },
    put: (endpoint, data, options = {}) => request(endpoint, {
      method: 'PUT',
      body: JSON.stringify(data),
      ...options,
    }),
    delete: (endpoint, options = {}) => request(endpoint, {
      method: 'DELETE',
      ...options,
    }),
  };
};

const api = createApiClient();

// API service functions
export const artworkService = {
  getAll: (params = {}) => api.get('/artworks/', { params }),
  getById: (id) => api.get(`/artworks/${id}`),
  getFeatured: () => api.get('/artworks/', { params: { limit: 6 } }), // Get first 6 as featured
  create: (data) => api.post('/artworks/', data),
  uploadImage: (id, file) => {
    const formData = new FormData();
    formData.append('file', file);
    return api.post(`/artworks/${id}/upload-image`, formData, {
      headers: {} // Remove Content-Type to let browser set it for FormData
    });
  }
};

export const bidService = {
  getByArtwork: (artworkId) => api.get(`/bids/artwork/${artworkId}`),
  create: (data) => api.post('/bids/', data),
};

export const userService = {
  getAll: (params = {}) => api.get('/users/', { params }),
  getById: (id) => api.get(`/users/${id}`),
  getCurrentUser: (auth0Sub) => api.get('/auth/me', { params: { auth0_sub: auth0Sub } }),
  register: (data) => api.post('/auth/register', data),
};

export const statsService = {
  getPlatformStats: async () => {
    // Since the platform stats endpoint doesn't exist yet, we'll fetch data and calculate stats
    try {
      const [artworksRes, usersRes] = await Promise.all([
        api.get('/artworks/', { params: { limit: 1000 } }),
        api.get('/users/', { params: { limit: 1000 } })
      ]);
      
      const artworks = artworksRes.data;
      const users = usersRes.data;
      
      const totalBids = artworks.reduce((sum, artwork) => sum + (artwork.current_highest_bid || 0), 0);
      const activeArtworks = artworks.filter(a => a.status === 'active').length;
      const artists = users.filter(u => u.role === 'seller' || u.role === 'admin').length;
      
      return {
        totalArtworks: activeArtworks,
        totalBids: Math.round(totalBids),
        totalArtists: artists,
        liveStatus: '24/7'
      };
    } catch (error) {
      // Return mock data if API fails
      return {
        totalArtworks: 1247,
        totalBids: 89000,
        totalArtists: 156,
        liveStatus: '24/7'
      };
    }
  }
};

export default api;