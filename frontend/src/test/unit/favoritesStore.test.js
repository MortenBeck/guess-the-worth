/**
 * Unit tests for favoritesStore (Zustand state management)
 * Tests favorites management and artwork bookmarking
 */

import { describe, it, expect, beforeEach } from "vitest";
import useFavoritesStore from "../../store/favoritesStore";

describe("favoritesStore", () => {
  beforeEach(() => {
    // Reset store state before each test
    useFavoritesStore.setState({
      favorites: [],
    });
  });

  describe("Initial State", () => {
    it("should have empty favorites array", () => {
      const state = useFavoritesStore.getState();
      expect(state.favorites).toEqual([]);
      expect(state.favorites.length).toBe(0);
    });
  });

  describe("addToFavorites", () => {
    it("should add artwork to favorites", () => {
      const artwork = {
        id: 1,
        title: "Beautiful Artwork",
        artist: "Test Artist",
      };

      useFavoritesStore.getState().addToFavorites(artwork);

      const state = useFavoritesStore.getState();
      expect(state.favorites.length).toBe(1);
      expect(state.favorites[0].id).toBe(1);
      expect(state.favorites[0].title).toBe("Beautiful Artwork");
    });

    it("should add dateAdded timestamp", () => {
      const artwork = { id: 1, title: "Artwork 1" };

      const beforeAdd = new Date().toISOString();
      useFavoritesStore.getState().addToFavorites(artwork);
      const afterAdd = new Date().toISOString();

      const state = useFavoritesStore.getState();
      const addedArtwork = state.favorites[0];

      expect(addedArtwork.dateAdded).toBeDefined();
      expect(addedArtwork.dateAdded >= beforeAdd).toBe(true);
      expect(addedArtwork.dateAdded <= afterAdd).toBe(true);
    });

    it("should not add duplicate artwork", () => {
      const artwork = { id: 1, title: "Artwork 1" };

      useFavoritesStore.getState().addToFavorites(artwork);
      useFavoritesStore.getState().addToFavorites(artwork);

      const state = useFavoritesStore.getState();
      expect(state.favorites.length).toBe(1);
    });

    it("should add multiple different artworks", () => {
      const artwork1 = { id: 1, title: "Artwork 1" };
      const artwork2 = { id: 2, title: "Artwork 2" };
      const artwork3 = { id: 3, title: "Artwork 3" };

      useFavoritesStore.getState().addToFavorites(artwork1);
      useFavoritesStore.getState().addToFavorites(artwork2);
      useFavoritesStore.getState().addToFavorites(artwork3);

      const state = useFavoritesStore.getState();
      expect(state.favorites.length).toBe(3);
    });

    it("should preserve original artwork properties", () => {
      const artwork = {
        id: 1,
        title: "Artwork 1",
        description: "Test description",
        price: 500,
        seller_id: 10,
      };

      useFavoritesStore.getState().addToFavorites(artwork);

      const state = useFavoritesStore.getState();
      const favorite = state.favorites[0];

      expect(favorite.title).toBe("Artwork 1");
      expect(favorite.description).toBe("Test description");
      expect(favorite.price).toBe(500);
      expect(favorite.seller_id).toBe(10);
    });
  });

  describe("removeFromFavorites", () => {
    it("should remove artwork from favorites", () => {
      const artwork = { id: 1, title: "Artwork 1" };

      useFavoritesStore.getState().addToFavorites(artwork);
      useFavoritesStore.getState().removeFromFavorites(1);

      const state = useFavoritesStore.getState();
      expect(state.favorites.length).toBe(0);
    });

    it("should only remove specified artwork", () => {
      const artwork1 = { id: 1, title: "Artwork 1" };
      const artwork2 = { id: 2, title: "Artwork 2" };
      const artwork3 = { id: 3, title: "Artwork 3" };

      useFavoritesStore.getState().addToFavorites(artwork1);
      useFavoritesStore.getState().addToFavorites(artwork2);
      useFavoritesStore.getState().addToFavorites(artwork3);

      useFavoritesStore.getState().removeFromFavorites(2);

      const state = useFavoritesStore.getState();
      expect(state.favorites.length).toBe(2);
      expect(state.favorites.find((f) => f.id === 1)).toBeDefined();
      expect(state.favorites.find((f) => f.id === 3)).toBeDefined();
      expect(state.favorites.find((f) => f.id === 2)).toBeUndefined();
    });

    it("should handle removing non-existent artwork gracefully", () => {
      const artwork = { id: 1, title: "Artwork 1" };
      useFavoritesStore.getState().addToFavorites(artwork);

      useFavoritesStore.getState().removeFromFavorites(999);

      const state = useFavoritesStore.getState();
      expect(state.favorites.length).toBe(1);
    });

    it("should handle removing from empty favorites", () => {
      useFavoritesStore.getState().removeFromFavorites(1);

      const state = useFavoritesStore.getState();
      expect(state.favorites.length).toBe(0);
    });
  });

  describe("isFavorite", () => {
    it("should return true for favorited artwork", () => {
      const artwork = { id: 1, title: "Artwork 1" };
      useFavoritesStore.getState().addToFavorites(artwork);

      const isFav = useFavoritesStore.getState().isFavorite(1);
      expect(isFav).toBe(true);
    });

    it("should return false for non-favorited artwork", () => {
      const artwork = { id: 1, title: "Artwork 1" };
      useFavoritesStore.getState().addToFavorites(artwork);

      const isFav = useFavoritesStore.getState().isFavorite(2);
      expect(isFav).toBe(false);
    });

    it("should return false for empty favorites", () => {
      const isFav = useFavoritesStore.getState().isFavorite(1);
      expect(isFav).toBe(false);
    });

    it("should correctly identify multiple favorites", () => {
      const artworks = [
        { id: 1, title: "Artwork 1" },
        { id: 2, title: "Artwork 2" },
        { id: 3, title: "Artwork 3" },
      ];

      artworks.forEach((artwork) => useFavoritesStore.getState().addToFavorites(artwork));

      expect(useFavoritesStore.getState().isFavorite(1)).toBe(true);
      expect(useFavoritesStore.getState().isFavorite(2)).toBe(true);
      expect(useFavoritesStore.getState().isFavorite(3)).toBe(true);
      expect(useFavoritesStore.getState().isFavorite(4)).toBe(false);
    });
  });

  describe("toggleFavorite", () => {
    it("should add artwork if not favorited", () => {
      const artwork = { id: 1, title: "Artwork 1" };

      useFavoritesStore.getState().toggleFavorite(artwork);

      const state = useFavoritesStore.getState();
      expect(state.favorites.length).toBe(1);
      expect(useFavoritesStore.getState().isFavorite(1)).toBe(true);
    });

    it("should remove artwork if already favorited", () => {
      const artwork = { id: 1, title: "Artwork 1" };

      useFavoritesStore.getState().addToFavorites(artwork);
      useFavoritesStore.getState().toggleFavorite(artwork);

      const state = useFavoritesStore.getState();
      expect(state.favorites.length).toBe(0);
      expect(useFavoritesStore.getState().isFavorite(1)).toBe(false);
    });

    it("should toggle multiple times correctly", () => {
      const artwork = { id: 1, title: "Artwork 1" };

      // Add
      useFavoritesStore.getState().toggleFavorite(artwork);
      expect(useFavoritesStore.getState().isFavorite(1)).toBe(true);

      // Remove
      useFavoritesStore.getState().toggleFavorite(artwork);
      expect(useFavoritesStore.getState().isFavorite(1)).toBe(false);

      // Add again
      useFavoritesStore.getState().toggleFavorite(artwork);
      expect(useFavoritesStore.getState().isFavorite(1)).toBe(true);
    });

    it("should not affect other favorites when toggling", () => {
      const artwork1 = { id: 1, title: "Artwork 1" };
      const artwork2 = { id: 2, title: "Artwork 2" };

      useFavoritesStore.getState().addToFavorites(artwork1);
      useFavoritesStore.getState().addToFavorites(artwork2);

      useFavoritesStore.getState().toggleFavorite(artwork1);

      const state = useFavoritesStore.getState();
      expect(state.favorites.length).toBe(1);
      expect(useFavoritesStore.getState().isFavorite(1)).toBe(false);
      expect(useFavoritesStore.getState().isFavorite(2)).toBe(true);
    });
  });

  describe("Complex Scenarios", () => {
    it("should handle rapid add/remove operations", () => {
      const artwork = { id: 1, title: "Artwork 1" };

      for (let i = 0; i < 10; i++) {
        useFavoritesStore.getState().toggleFavorite(artwork);
      }

      const state = useFavoritesStore.getState();
      // Should be removed after 10 toggles (even number)
      expect(state.favorites.length).toBe(0);
      expect(useFavoritesStore.getState().isFavorite(1)).toBe(false);
    });

    it("should handle favorites with complex data", () => {
      const artwork = {
        id: 1,
        title: "Complex Artwork",
        description: "A very detailed description",
        seller_id: 5,
        price: 1000,
        images: ["url1.jpg", "url2.jpg"],
        metadata: { category: "painting", year: 2024 },
      };

      useFavoritesStore.getState().addToFavorites(artwork);

      const state = useFavoritesStore.getState();
      const favorite = state.favorites[0];

      expect(favorite.title).toBe("Complex Artwork");
      expect(favorite.images).toEqual(["url1.jpg", "url2.jpg"]);
      expect(favorite.metadata.category).toBe("painting");
    });

    it("should maintain favorites order (FIFO)", () => {
      const artworks = [
        { id: 1, title: "Artwork 1" },
        { id: 2, title: "Artwork 2" },
        { id: 3, title: "Artwork 3" },
      ];

      artworks.forEach((artwork) => useFavoritesStore.getState().addToFavorites(artwork));

      const state = useFavoritesStore.getState();
      expect(state.favorites[0].id).toBe(1);
      expect(state.favorites[1].id).toBe(2);
      expect(state.favorites[2].id).toBe(3);
    });

    it("should handle edge case with artwork id 0", () => {
      const artwork = { id: 0, title: "Artwork Zero" };

      useFavoritesStore.getState().addToFavorites(artwork);

      expect(useFavoritesStore.getState().isFavorite(0)).toBe(true);
      expect(useFavoritesStore.getState().favorites.length).toBe(1);
    });
  });
});
