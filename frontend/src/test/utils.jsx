import { render } from "@testing-library/react";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { BrowserRouter } from "react-router-dom";
import { Auth0Provider } from "@auth0/auth0-react";

/**
 * Create a custom render function that includes all necessary providers
 */
export function renderWithProviders(ui, options = {}) {
  const queryClient = new QueryClient({
    defaultOptions: {
      queries: {
        retry: false,
      },
    },
  });

  const mockAuth0Config = {
    domain: "test.auth0.com",
    clientId: "test-client-id",
    authorizationParams: {
      audience: "test-audience",
      redirect_uri: window.location.origin,
    },
  };

  function Wrapper({ children }) {
    return (
      <Auth0Provider {...mockAuth0Config}>
        <QueryClientProvider client={queryClient}>
          <BrowserRouter>{children}</BrowserRouter>
        </QueryClientProvider>
      </Auth0Provider>
    );
  }

  return render(ui, { wrapper: Wrapper, ...options });
}

/**
 * Mock user for testing
 */
export const mockUser = {
  id: 1,
  email: "test@example.com",
  name: "Test User",
  role: "BUYER",
  auth0_sub: "auth0|123456",
};

/**
 * Mock seller user for testing
 */
export const mockSeller = {
  id: 2,
  email: "seller@example.com",
  name: "Test Seller",
  role: "SELLER",
  auth0_sub: "auth0|789012",
};

/**
 * Mock artwork for testing
 */
export const mockArtwork = {
  id: 1,
  title: "Test Artwork",
  artist_name: "Test Artist",
  description: "Test description",
  category: "painting",
  starting_bid: 100,
  current_highest_bid: 150,
  status: "ACTIVE",
  image_url: "/test-image.jpg",
  seller_id: 2,
  created_at: "2024-01-01T00:00:00Z",
};

/**
 * Mock bid for testing
 */
export const mockBid = {
  id: 1,
  artwork_id: 1,
  bidder_id: 1,
  amount: 150,
  is_winning: false,
  bid_time: "2024-01-01T00:00:00Z",
};

/**
 * Mock platform stats for testing
 */
export const mockPlatformStats = {
  total_artworks: 1247,
  active_auctions: 89,
  total_bids: 3456,
  total_users: 1245,
};
