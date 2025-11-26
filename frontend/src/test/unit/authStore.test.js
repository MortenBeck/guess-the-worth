/**
 * Unit tests for authStore (Zustand state management)
 * Tests authentication state, user management, and role checks
 */

import { describe, it, expect, beforeEach } from "vitest";
import useAuthStore from "../../store/authStore";

describe("authStore", () => {
  beforeEach(() => {
    // Reset store state before each test
    useAuthStore.setState({
      user: null,
      token: null,
      isAuthenticated: false,
      isLoading: false,
    });
  });

  describe("Initial State", () => {
    it("should have correct initial state", () => {
      const state = useAuthStore.getState();
      expect(state.user).toBeNull();
      expect(state.token).toBeNull();
      expect(state.isAuthenticated).toBe(false);
      expect(state.isLoading).toBe(false);
    });
  });

  describe("setAuth", () => {
    it("should set user and token correctly", () => {
      const mockUser = {
        id: 1,
        email: "test@example.com",
        name: "Test User",
        role: "BUYER",
      };
      const mockToken = "test-token-123";

      useAuthStore.getState().setAuth(mockUser, mockToken);

      const state = useAuthStore.getState();
      expect(state.user).toEqual(mockUser);
      expect(state.token).toBe(mockToken);
      expect(state.isAuthenticated).toBe(true);
      expect(state.isLoading).toBe(false);
    });

    it("should handle seller user", () => {
      const sellerUser = {
        id: 2,
        email: "seller@example.com",
        name: "Seller User",
        role: "SELLER",
      };

      useAuthStore.getState().setAuth(sellerUser, "seller-token");

      const state = useAuthStore.getState();
      expect(state.user.role).toBe("SELLER");
      expect(state.isAuthenticated).toBe(true);
    });

    it("should handle admin user", () => {
      const adminUser = {
        id: 3,
        email: "admin@example.com",
        name: "Admin User",
        role: "ADMIN",
      };

      useAuthStore.getState().setAuth(adminUser, "admin-token");

      const state = useAuthStore.getState();
      expect(state.user.role).toBe("ADMIN");
      expect(state.isAuthenticated).toBe(true);
    });
  });

  describe("clearAuth", () => {
    it("should clear all auth data", () => {
      // First set some auth data
      const mockUser = { id: 1, email: "test@example.com", role: "BUYER" };
      useAuthStore.getState().setAuth(mockUser, "test-token");

      // Then clear it
      useAuthStore.getState().clearAuth();

      const state = useAuthStore.getState();
      expect(state.user).toBeNull();
      expect(state.token).toBeNull();
      expect(state.isAuthenticated).toBe(false);
      expect(state.isLoading).toBe(false);
    });

    it("should handle clearing when already empty", () => {
      useAuthStore.getState().clearAuth();

      const state = useAuthStore.getState();
      expect(state.user).toBeNull();
      expect(state.token).toBeNull();
      expect(state.isAuthenticated).toBe(false);
    });
  });

  describe("setLoading", () => {
    it("should set loading to true", () => {
      useAuthStore.getState().setLoading(true);
      expect(useAuthStore.getState().isLoading).toBe(true);
    });

    it("should set loading to false", () => {
      useAuthStore.getState().setLoading(true);
      useAuthStore.getState().setLoading(false);
      expect(useAuthStore.getState().isLoading).toBe(false);
    });
  });

  describe("updateUser", () => {
    it("should update user data partially", () => {
      const initialUser = {
        id: 1,
        email: "test@example.com",
        name: "Test User",
        role: "BUYER",
      };

      useAuthStore.getState().setAuth(initialUser, "token");

      useAuthStore.getState().updateUser({ name: "Updated Name" });

      const state = useAuthStore.getState();
      expect(state.user.name).toBe("Updated Name");
      expect(state.user.id).toBe(1); // Other fields unchanged
      expect(state.user.email).toBe("test@example.com");
    });

    it("should update multiple fields", () => {
      const initialUser = {
        id: 1,
        email: "test@example.com",
        name: "Test User",
        role: "BUYER",
      };

      useAuthStore.getState().setAuth(initialUser, "token");

      useAuthStore.getState().updateUser({
        name: "New Name",
        email: "newemail@example.com",
      });

      const state = useAuthStore.getState();
      expect(state.user.name).toBe("New Name");
      expect(state.user.email).toBe("newemail@example.com");
      expect(state.user.role).toBe("BUYER"); // Unchanged
    });
  });

  describe("hasRole", () => {
    it("should return true for matching role", () => {
      const user = { id: 1, email: "test@example.com", role: "BUYER" };
      useAuthStore.getState().setAuth(user, "token");

      const hasRole = useAuthStore.getState().hasRole("BUYER");
      expect(hasRole).toBe(true);
    });

    it("should return false for non-matching role", () => {
      const user = { id: 1, email: "test@example.com", role: "BUYER" };
      useAuthStore.getState().setAuth(user, "token");

      const hasRole = useAuthStore.getState().hasRole("ADMIN");
      expect(hasRole).toBe(false);
    });

    it("should return false when user is null", () => {
      const hasRole = useAuthStore.getState().hasRole("BUYER");
      expect(hasRole).toBe(false);
    });
  });

  describe("isAdmin", () => {
    it("should return true for admin user", () => {
      const user = { id: 1, email: "admin@example.com", role: "ADMIN" };
      useAuthStore.getState().setAuth(user, "token");

      expect(useAuthStore.getState().isAdmin()).toBe(true);
    });

    it("should return false for non-admin user", () => {
      const user = { id: 1, email: "buyer@example.com", role: "BUYER" };
      useAuthStore.getState().setAuth(user, "token");

      expect(useAuthStore.getState().isAdmin()).toBe(false);
    });

    it("should return false when not authenticated", () => {
      expect(useAuthStore.getState().isAdmin()).toBe(false);
    });
  });

  describe("isSeller", () => {
    it("should return true for seller role", () => {
      const user = { id: 1, email: "seller@example.com", role: "SELLER" };
      useAuthStore.getState().setAuth(user, "token");

      expect(useAuthStore.getState().isSeller()).toBe(true);
    });

    it("should return true for admin role (admin can sell)", () => {
      const user = { id: 1, email: "admin@example.com", role: "ADMIN" };
      useAuthStore.getState().setAuth(user, "token");

      expect(useAuthStore.getState().isSeller()).toBe(true);
    });

    it("should return false for buyer role", () => {
      const user = { id: 1, email: "buyer@example.com", role: "BUYER" };
      useAuthStore.getState().setAuth(user, "token");

      expect(useAuthStore.getState().isSeller()).toBe(false);
    });

    it("should return false when not authenticated", () => {
      expect(useAuthStore.getState().isSeller()).toBe(false);
    });
  });

  describe("isBuyer", () => {
    it("should return true for buyer role", () => {
      const user = { id: 1, email: "buyer@example.com", role: "BUYER" };
      useAuthStore.getState().setAuth(user, "token");

      expect(useAuthStore.getState().isBuyer()).toBe(true);
    });

    it("should return true for seller role (seller can buy)", () => {
      const user = { id: 1, email: "seller@example.com", role: "SELLER" };
      useAuthStore.getState().setAuth(user, "token");

      expect(useAuthStore.getState().isBuyer()).toBe(true);
    });

    it("should return true for admin role (admin can buy)", () => {
      const user = { id: 1, email: "admin@example.com", role: "ADMIN" };
      useAuthStore.getState().setAuth(user, "token");

      expect(useAuthStore.getState().isBuyer()).toBe(true);
    });

    it("should return false when not authenticated", () => {
      expect(useAuthStore.getState().isBuyer()).toBe(false);
    });
  });

  describe("Edge Cases", () => {
    it("should handle user with missing role", () => {
      const userWithoutRole = { id: 1, email: "test@example.com" };
      useAuthStore.getState().setAuth(userWithoutRole, "token");

      expect(useAuthStore.getState().isAdmin()).toBe(false);
      expect(useAuthStore.getState().isSeller()).toBe(false);
      expect(useAuthStore.getState().isBuyer()).toBe(false);
    });

    it("should handle empty token", () => {
      const user = { id: 1, email: "test@example.com", role: "BUYER" };
      useAuthStore.getState().setAuth(user, "");

      const state = useAuthStore.getState();
      expect(state.token).toBe("");
      expect(state.isAuthenticated).toBe(true);
    });

    it("should handle updateUser when user is null", () => {
      useAuthStore.getState().updateUser({ name: "New Name" });

      const state = useAuthStore.getState();
      expect(state.user).toEqual({ name: "New Name" });
    });
  });
});
