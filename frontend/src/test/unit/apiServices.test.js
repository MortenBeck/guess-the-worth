/**
 * Unit tests for API service functions
 * Tests API client, artwork service, bid service, user service, and stats service
 */

import { describe, it, expect, beforeEach, afterEach, vi } from "vitest";
import { artworkService, bidService, userService, statsService } from "../../services/api";

// Mock fetch
globalThis.fetch = vi.fn();

// Mock localStorage
const localStorageMock = (() => {
  let store = {};
  return {
    getItem: (key) => store[key] || null,
    setItem: (key, value) => {
      store[key] = value.toString();
    },
    removeItem: (key) => {
      delete store[key];
    },
    clear: () => {
      store = {};
    },
  };
})();

globalThis.localStorage = localStorageMock;

describe("API Services", () => {
  beforeEach(() => {
    fetch.mockReset();
    localStorage.clear();
  });

  afterEach(() => {
    vi.restoreAllMocks();
  });

  describe("artworkService", () => {
    describe("getAll", () => {
      it("should fetch all artworks", async () => {
        const mockArtworks = [
          { id: 1, title: "Artwork 1", price: 100 },
          { id: 2, title: "Artwork 2", price: 200 },
        ];

        fetch.mockResolvedValueOnce({
          ok: true,
          status: 200,
          json: async () => mockArtworks,
        });

        const result = await artworkService.getAll();

        expect(fetch).toHaveBeenCalledTimes(1);
        expect(result.data).toEqual(mockArtworks);
      });

      it("should handle pagination parameters", async () => {
        fetch.mockResolvedValueOnce({
          ok: true,
          status: 200,
          json: async () => [],
        });

        await artworkService.getAll({ skip: 10, limit: 5 });

        expect(fetch).toHaveBeenCalledWith(expect.stringContaining("skip=10"), expect.any(Object));
        expect(fetch).toHaveBeenCalledWith(expect.stringContaining("limit=5"), expect.any(Object));
      });

      it("should include authorization header when token exists", async () => {
        localStorage.setItem("access_token", "test-token-123");

        fetch.mockResolvedValueOnce({
          ok: true,
          status: 200,
          json: async () => [],
        });

        await artworkService.getAll();

        expect(fetch).toHaveBeenCalledWith(
          expect.any(String),
          expect.objectContaining({
            headers: expect.objectContaining({
              Authorization: "Bearer test-token-123",
            }),
          })
        );
      });
    });

    describe("getById", () => {
      it("should fetch single artwork by ID", async () => {
        const mockArtwork = { id: 1, title: "Artwork 1", price: 100 };

        fetch.mockResolvedValueOnce({
          ok: true,
          status: 200,
          json: async () => mockArtwork,
        });

        const result = await artworkService.getById(1);

        expect(fetch).toHaveBeenCalledTimes(1);
        expect(fetch).toHaveBeenCalledWith(
          expect.stringContaining("/artworks/1"),
          expect.any(Object)
        );
        expect(result.data).toEqual(mockArtwork);
      });
    });

    describe("getFeatured", () => {
      it("should fetch first 6 artworks as featured", async () => {
        const mockArtworks = Array.from({ length: 6 }, (_, i) => ({
          id: i + 1,
          title: `Artwork ${i + 1}`,
        }));

        fetch.mockResolvedValueOnce({
          ok: true,
          status: 200,
          json: async () => mockArtworks,
        });

        const result = await artworkService.getFeatured();

        expect(fetch).toHaveBeenCalledWith(expect.stringContaining("limit=6"), expect.any(Object));
        expect(result.data.length).toBe(6);
      });
    });

    describe("create", () => {
      it("should create new artwork", async () => {
        const newArtwork = {
          title: "New Artwork",
          description: "Description",
          secret_threshold: 500,
        };

        const createdArtwork = { id: 1, ...newArtwork };

        fetch.mockResolvedValueOnce({
          ok: true,
          status: 200,
          json: async () => createdArtwork,
        });

        const result = await artworkService.create(newArtwork);

        expect(fetch).toHaveBeenCalledWith(
          expect.stringContaining("/artworks/"),
          expect.objectContaining({
            method: "POST",
            body: JSON.stringify(newArtwork),
          })
        );
        expect(result.data).toEqual(createdArtwork);
      });
    });

    describe("uploadImage", () => {
      it("should upload artwork image", async () => {
        const mockFile = new File(["content"], "test.jpg", { type: "image/jpeg" });
        const artworkId = 1;

        fetch.mockResolvedValueOnce({
          ok: true,
          status: 200,
          json: async () => ({ image_url: "http://example.com/test.jpg" }),
        });

        await artworkService.uploadImage(artworkId, mockFile);

        expect(fetch).toHaveBeenCalledWith(
          expect.stringContaining(`/artworks/${artworkId}/upload-image`),
          expect.objectContaining({
            method: "POST",
          })
        );
      });
    });
  });

  describe("bidService", () => {
    describe("getByArtwork", () => {
      it("should fetch bids for artwork", async () => {
        const artworkId = 1;
        const mockBids = [
          { id: 1, amount: 100, bidder_id: 5 },
          { id: 2, amount: 150, bidder_id: 6 },
        ];

        fetch.mockResolvedValueOnce({
          ok: true,
          status: 200,
          json: async () => mockBids,
        });

        const result = await bidService.getByArtwork(artworkId);

        expect(fetch).toHaveBeenCalledWith(
          expect.stringContaining(`/bids/artwork/${artworkId}`),
          expect.any(Object)
        );
        expect(result.data).toEqual(mockBids);
      });
    });

    describe("create", () => {
      it("should create new bid", async () => {
        const newBid = {
          artwork_id: 1,
          bidder_id: 5,
          amount: 150,
        };

        const createdBid = { id: 1, ...newBid, is_winning: false };

        fetch.mockResolvedValueOnce({
          ok: true,
          status: 200,
          json: async () => createdBid,
        });

        const result = await bidService.create(newBid);

        expect(fetch).toHaveBeenCalledWith(
          expect.stringContaining("/bids/"),
          expect.objectContaining({
            method: "POST",
            body: JSON.stringify(newBid),
          })
        );
        expect(result.data).toEqual(createdBid);
      });
    });
  });

  describe("userService", () => {
    describe("getAll", () => {
      it("should fetch all users", async () => {
        const mockUsers = [
          { id: 1, email: "user1@example.com", role: "buyer" },
          { id: 2, email: "user2@example.com", role: "seller" },
        ];

        fetch.mockResolvedValueOnce({
          ok: true,
          status: 200,
          json: async () => mockUsers,
        });

        const result = await userService.getAll();

        expect(fetch).toHaveBeenCalledTimes(1);
        expect(result.data).toEqual(mockUsers);
      });
    });

    describe("getById", () => {
      it("should fetch single user by ID", async () => {
        const mockUser = { id: 1, email: "test@example.com", role: "buyer" };

        fetch.mockResolvedValueOnce({
          ok: true,
          status: 200,
          json: async () => mockUser,
        });

        const result = await userService.getById(1);

        expect(fetch).toHaveBeenCalledWith(expect.stringContaining("/users/1"), expect.any(Object));
        expect(result.data).toEqual(mockUser);
      });
    });

    describe("getCurrentUser", () => {
      it("should fetch current user", async () => {
        const mockUser = { id: 1, auth0_sub: "auth0|user123", email: "test@example.com" };

        fetch.mockResolvedValueOnce({
          ok: true,
          status: 200,
          json: async () => mockUser,
        });

        const result = await userService.getCurrentUser();

        expect(fetch).toHaveBeenCalledWith(
          expect.stringContaining("/auth/me"),
          expect.objectContaining({
            method: "GET",
          })
        );
        expect(result.data).toEqual(mockUser);
      });
    });

    describe("register", () => {
      it("should register new user", async () => {
        const newUser = {
          email: "newuser@example.com",
          name: "New User",
          auth0_sub: "auth0|newuser",
        };

        const createdUser = { id: 1, ...newUser, role: "buyer" };

        fetch.mockResolvedValueOnce({
          ok: true,
          status: 200,
          json: async () => createdUser,
        });

        const result = await userService.register(newUser);

        expect(fetch).toHaveBeenCalledWith(
          expect.stringContaining("/auth/register"),
          expect.objectContaining({
            method: "POST",
            body: JSON.stringify(newUser),
          })
        );
        expect(result.data).toEqual(createdUser);
      });
    });
  });

  describe("statsService", () => {
    describe("getPlatformStats", () => {
      it("should fetch platform stats from backend", async () => {
        const mockStats = {
          total_artworks: 10,
          total_users: 25,
          total_bids: 150,
          active_auctions: 5,
        };

        fetch.mockResolvedValueOnce({
          ok: true,
          status: 200,
          json: async () => mockStats,
        });

        const result = await statsService.getPlatformStats();

        expect(fetch).toHaveBeenCalledTimes(1);
        expect(fetch).toHaveBeenCalledWith(
          expect.stringContaining("/stats/platform"),
          expect.any(Object)
        );
        expect(result.data).toEqual(mockStats);
      });

      it("should handle API errors", async () => {
        fetch.mockResolvedValueOnce({
          ok: false,
          status: 500,
          json: async () => ({ detail: "Server error" }),
        });

        await expect(statsService.getPlatformStats()).rejects.toThrow();
      });
    });
  });

  describe("Error Handling", () => {
    it("should throw error for 401 Unauthorized", async () => {
      fetch.mockResolvedValueOnce({
        ok: false,
        status: 401,
        json: async () => ({}),
      });

      await expect(artworkService.getAll()).rejects.toThrow(
        "Your session has expired. Please log in again."
      );
      expect(localStorage.getItem("access_token")).toBeNull();
    });

    it("should throw error for 403 Forbidden", async () => {
      fetch.mockResolvedValueOnce({
        ok: false,
        status: 403,
        json: async () => ({ detail: "Access denied" }),
      });

      await expect(artworkService.getAll()).rejects.toThrow("Access denied");
    });

    it("should throw error for 404 Not Found", async () => {
      fetch.mockResolvedValueOnce({
        ok: false,
        status: 404,
        json: async () => ({ detail: "Resource not found" }),
      });

      await expect(artworkService.getAll()).rejects.toThrow("Resource not found");
    });

    it("should throw error for 400 Bad Request", async () => {
      fetch.mockResolvedValueOnce({
        ok: false,
        status: 400,
        json: async () => ({ detail: "Invalid data" }),
      });

      await expect(artworkService.getAll()).rejects.toThrow("Invalid data");
    });

    it("should throw error for non-ok responses", async () => {
      fetch.mockResolvedValueOnce({
        ok: false,
        status: 500,
        json: async () => ({}),
      });

      await expect(artworkService.getAll()).rejects.toThrow(
        "Server error. Please try again later."
      );
    });

    it("should handle other status codes with detail from response", async () => {
      fetch.mockResolvedValueOnce({
        ok: false,
        status: 409,
        statusText: "Conflict",
        json: async () => ({ detail: "Resource conflict occurred" }),
      });

      await expect(artworkService.getAll()).rejects.toThrow("Resource conflict occurred");
    });

    it("should handle other status codes without detail from response", async () => {
      fetch.mockResolvedValueOnce({
        ok: false,
        status: 429,
        statusText: "Too Many Requests",
        json: async () => ({}),
      });

      await expect(artworkService.getAll()).rejects.toThrow("HTTP 429: Too Many Requests");
    });

    it("should throw error for network failures", async () => {
      fetch.mockRejectedValueOnce(new TypeError("Failed to fetch"));

      await expect(artworkService.getAll()).rejects.toThrow("Unable to connect to server");
    });

    it("should throw error for other fetch errors", async () => {
      fetch.mockRejectedValueOnce(new Error("Random error"));

      await expect(artworkService.getAll()).rejects.toThrow("Random error");
    });

    it("should handle response with no JSON body", async () => {
      fetch.mockResolvedValueOnce({
        ok: true,
        status: 200,
        json: async () => {
          throw new Error("No JSON");
        },
      });

      const result = await artworkService.getAll();
      expect(result.data).toBeNull();
    });
  });

  describe("API Methods", () => {
    it("should support PUT method", async () => {
      fetch.mockResolvedValueOnce({
        ok: true,
        status: 200,
        json: async () => ({ id: 1, title: "Updated" }),
      });

      const result = await userService.updateProfile({ name: "New Name" });

      expect(fetch).toHaveBeenCalledWith(
        expect.any(String),
        expect.objectContaining({
          method: "PUT",
        })
      );
      expect(result.data).toEqual({ id: 1, title: "Updated" });
    });
  });
});
