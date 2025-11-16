/**
 * Unit tests for biddingStore (Zustand state management)
 * Tests real-time bidding state, artwork tracking, and WebSocket integration
 */

import { describe, it, expect, beforeEach } from "vitest";
import useBiddingStore from "../../store/biddingStore";

describe("biddingStore", () => {
  beforeEach(() => {
    // Reset store state before each test
    useBiddingStore.setState({
      activeArtworks: new Map(),
      currentBids: new Map(),
      socketConnected: false,
    });
  });

  describe("Initial State", () => {
    it("should have correct initial state", () => {
      const state = useBiddingStore.getState();
      expect(state.activeArtworks).toBeInstanceOf(Map);
      expect(state.activeArtworks.size).toBe(0);
      expect(state.currentBids).toBeInstanceOf(Map);
      expect(state.currentBids.size).toBe(0);
      expect(state.socketConnected).toBe(false);
    });
  });

  describe("setSocketConnected", () => {
    it("should set socket connected to true", () => {
      useBiddingStore.getState().setSocketConnected(true);
      expect(useBiddingStore.getState().socketConnected).toBe(true);
    });

    it("should set socket connected to false", () => {
      useBiddingStore.getState().setSocketConnected(true);
      useBiddingStore.getState().setSocketConnected(false);
      expect(useBiddingStore.getState().socketConnected).toBe(false);
    });
  });

  describe("joinArtwork", () => {
    it("should add artwork to activeArtworks", () => {
      const artworkId = 1;
      const artworkData = {
        id: 1,
        title: "Test Artwork",
        current_highest_bid: 100,
        status: "active",
      };

      useBiddingStore.getState().joinArtwork(artworkId, artworkData);

      const state = useBiddingStore.getState();
      expect(state.activeArtworks.size).toBe(1);
      expect(state.activeArtworks.get(artworkId)).toEqual(artworkData);
    });

    it("should handle multiple artworks", () => {
      const artwork1 = { id: 1, title: "Artwork 1", current_highest_bid: 100 };
      const artwork2 = { id: 2, title: "Artwork 2", current_highest_bid: 200 };

      useBiddingStore.getState().joinArtwork(1, artwork1);
      useBiddingStore.getState().joinArtwork(2, artwork2);

      const state = useBiddingStore.getState();
      expect(state.activeArtworks.size).toBe(2);
      expect(state.activeArtworks.get(1)).toEqual(artwork1);
      expect(state.activeArtworks.get(2)).toEqual(artwork2);
    });

    it("should update existing artwork if joined again", () => {
      const artwork1 = { id: 1, title: "Artwork 1", current_highest_bid: 100 };
      const artwork1Updated = { id: 1, title: "Artwork 1 Updated", current_highest_bid: 150 };

      useBiddingStore.getState().joinArtwork(1, artwork1);
      useBiddingStore.getState().joinArtwork(1, artwork1Updated);

      const state = useBiddingStore.getState();
      expect(state.activeArtworks.size).toBe(1);
      expect(state.activeArtworks.get(1).title).toBe("Artwork 1 Updated");
      expect(state.activeArtworks.get(1).current_highest_bid).toBe(150);
    });
  });

  describe("leaveArtwork", () => {
    it("should remove artwork from activeArtworks", () => {
      const artworkId = 1;
      const artworkData = { id: 1, title: "Test Artwork", current_highest_bid: 100 };

      useBiddingStore.getState().joinArtwork(artworkId, artworkData);
      useBiddingStore.getState().leaveArtwork(artworkId);

      const state = useBiddingStore.getState();
      expect(state.activeArtworks.size).toBe(0);
      expect(state.activeArtworks.has(artworkId)).toBe(false);
    });

    it("should remove corresponding bid from currentBids", () => {
      const artworkId = 1;
      const artworkData = { id: 1, title: "Test Artwork" };
      const bidData = { amount: 150, bidder_id: 5 };

      useBiddingStore.getState().joinArtwork(artworkId, artworkData);
      useBiddingStore.getState().updateBid(artworkId, bidData);
      useBiddingStore.getState().leaveArtwork(artworkId);

      const state = useBiddingStore.getState();
      expect(state.currentBids.has(artworkId)).toBe(false);
    });

    it("should handle leaving non-existent artwork gracefully", () => {
      useBiddingStore.getState().leaveArtwork(999);

      const state = useBiddingStore.getState();
      expect(state.activeArtworks.size).toBe(0);
      expect(state.currentBids.size).toBe(0);
    });

    it("should not affect other artworks when leaving one", () => {
      const artwork1 = { id: 1, title: "Artwork 1" };
      const artwork2 = { id: 2, title: "Artwork 2" };

      useBiddingStore.getState().joinArtwork(1, artwork1);
      useBiddingStore.getState().joinArtwork(2, artwork2);
      useBiddingStore.getState().leaveArtwork(1);

      const state = useBiddingStore.getState();
      expect(state.activeArtworks.size).toBe(1);
      expect(state.activeArtworks.has(2)).toBe(true);
      expect(state.activeArtworks.has(1)).toBe(false);
    });
  });

  describe("updateBid", () => {
    it("should add bid to currentBids", () => {
      const artworkId = 1;
      const bidData = { amount: 150, bidder_id: 5, is_winning: false };

      useBiddingStore.getState().updateBid(artworkId, bidData);

      const state = useBiddingStore.getState();
      expect(state.currentBids.size).toBe(1);
      expect(state.currentBids.get(artworkId)).toEqual(bidData);
    });

    it("should update artwork's current_highest_bid", () => {
      const artworkId = 1;
      const artworkData = { id: 1, title: "Test Artwork", current_highest_bid: 100 };
      const bidData = { amount: 150, bidder_id: 5 };

      useBiddingStore.getState().joinArtwork(artworkId, artworkData);
      useBiddingStore.getState().updateBid(artworkId, bidData);

      const state = useBiddingStore.getState();
      expect(state.activeArtworks.get(artworkId).current_highest_bid).toBe(150);
    });

    it("should handle bid update for non-tracked artwork", () => {
      const artworkId = 1;
      const bidData = { amount: 150, bidder_id: 5 };

      useBiddingStore.getState().updateBid(artworkId, bidData);

      const state = useBiddingStore.getState();
      expect(state.currentBids.get(artworkId)).toEqual(bidData);
      // Artwork should not be created if it doesn't exist
      expect(state.activeArtworks.has(artworkId)).toBe(false);
    });

    it("should update existing bid", () => {
      const artworkId = 1;
      const bid1 = { amount: 150, bidder_id: 5 };
      const bid2 = { amount: 200, bidder_id: 6 };

      useBiddingStore.getState().updateBid(artworkId, bid1);
      useBiddingStore.getState().updateBid(artworkId, bid2);

      const state = useBiddingStore.getState();
      expect(state.currentBids.size).toBe(1);
      expect(state.currentBids.get(artworkId).amount).toBe(200);
      expect(state.currentBids.get(artworkId).bidder_id).toBe(6);
    });

    it("should handle multiple bids on different artworks", () => {
      const bid1 = { amount: 150, bidder_id: 5 };
      const bid2 = { amount: 200, bidder_id: 6 };

      useBiddingStore.getState().updateBid(1, bid1);
      useBiddingStore.getState().updateBid(2, bid2);

      const state = useBiddingStore.getState();
      expect(state.currentBids.size).toBe(2);
      expect(state.currentBids.get(1).amount).toBe(150);
      expect(state.currentBids.get(2).amount).toBe(200);
    });
  });

  describe("markArtworkSold", () => {
    it("should update artwork status to sold", () => {
      const artworkId = 1;
      const artworkData = { id: 1, title: "Test Artwork", status: "active" };

      useBiddingStore.getState().joinArtwork(artworkId, artworkData);
      useBiddingStore.getState().markArtworkSold(artworkId);

      const state = useBiddingStore.getState();
      expect(state.activeArtworks.get(artworkId).status).toBe("sold");
    });

    it("should preserve other artwork properties", () => {
      const artworkId = 1;
      const artworkData = {
        id: 1,
        title: "Test Artwork",
        status: "active",
        current_highest_bid: 500,
        seller_id: 10,
      };

      useBiddingStore.getState().joinArtwork(artworkId, artworkData);
      useBiddingStore.getState().markArtworkSold(artworkId);

      const state = useBiddingStore.getState();
      const artwork = state.activeArtworks.get(artworkId);
      expect(artwork.title).toBe("Test Artwork");
      expect(artwork.current_highest_bid).toBe(500);
      expect(artwork.seller_id).toBe(10);
      expect(artwork.status).toBe("sold");
    });

    it("should handle marking non-existent artwork as sold", () => {
      useBiddingStore.getState().markArtworkSold(999);

      const state = useBiddingStore.getState();
      expect(state.activeArtworks.has(999)).toBe(false);
    });

    it("should not affect other artworks", () => {
      const artwork1 = { id: 1, title: "Artwork 1", status: "active" };
      const artwork2 = { id: 2, title: "Artwork 2", status: "active" };

      useBiddingStore.getState().joinArtwork(1, artwork1);
      useBiddingStore.getState().joinArtwork(2, artwork2);
      useBiddingStore.getState().markArtworkSold(1);

      const state = useBiddingStore.getState();
      expect(state.activeArtworks.get(1).status).toBe("sold");
      expect(state.activeArtworks.get(2).status).toBe("active");
    });
  });

  describe("clearAll", () => {
    it("should clear all artworks and bids", () => {
      const artwork1 = { id: 1, title: "Artwork 1" };
      const artwork2 = { id: 2, title: "Artwork 2" };
      const bid1 = { amount: 150, bidder_id: 5 };

      useBiddingStore.getState().joinArtwork(1, artwork1);
      useBiddingStore.getState().joinArtwork(2, artwork2);
      useBiddingStore.getState().updateBid(1, bid1);

      useBiddingStore.getState().clearAll();

      const state = useBiddingStore.getState();
      expect(state.activeArtworks.size).toBe(0);
      expect(state.currentBids.size).toBe(0);
    });

    it("should not affect socketConnected state", () => {
      useBiddingStore.getState().setSocketConnected(true);
      useBiddingStore.getState().clearAll();

      const state = useBiddingStore.getState();
      expect(state.socketConnected).toBe(true);
    });

    it("should handle clearing when already empty", () => {
      useBiddingStore.getState().clearAll();

      const state = useBiddingStore.getState();
      expect(state.activeArtworks.size).toBe(0);
      expect(state.currentBids.size).toBe(0);
    });
  });

  describe("Complex Scenarios", () => {
    it("should handle full bidding lifecycle", () => {
      const artworkId = 1;
      const artwork = { id: 1, title: "Rare Artwork", current_highest_bid: 100, status: "active" };

      // Join artwork
      useBiddingStore.getState().joinArtwork(artworkId, artwork);

      // Place first bid
      useBiddingStore.getState().updateBid(artworkId, { amount: 150, bidder_id: 5 });
      expect(useBiddingStore.getState().activeArtworks.get(artworkId).current_highest_bid).toBe(150);

      // Place higher bid
      useBiddingStore.getState().updateBid(artworkId, { amount: 200, bidder_id: 6 });
      expect(useBiddingStore.getState().activeArtworks.get(artworkId).current_highest_bid).toBe(200);

      // Mark as sold
      useBiddingStore.getState().markArtworkSold(artworkId);
      expect(useBiddingStore.getState().activeArtworks.get(artworkId).status).toBe("sold");

      // Leave artwork
      useBiddingStore.getState().leaveArtwork(artworkId);
      expect(useBiddingStore.getState().activeArtworks.has(artworkId)).toBe(false);
    });

    it("should handle multiple concurrent auctions", () => {
      const artworks = [
        { id: 1, title: "Artwork 1", current_highest_bid: 100, status: "active" },
        { id: 2, title: "Artwork 2", current_highest_bid: 200, status: "active" },
        { id: 3, title: "Artwork 3", current_highest_bid: 300, status: "active" },
      ];

      // Join all artworks
      artworks.forEach((artwork) => {
        useBiddingStore.getState().joinArtwork(artwork.id, artwork);
      });

      // Place bids on each
      useBiddingStore.getState().updateBid(1, { amount: 150, bidder_id: 5 });
      useBiddingStore.getState().updateBid(2, { amount: 250, bidder_id: 6 });
      useBiddingStore.getState().updateBid(3, { amount: 350, bidder_id: 7 });

      const state = useBiddingStore.getState();
      expect(state.activeArtworks.size).toBe(3);
      expect(state.currentBids.size).toBe(3);
      expect(state.activeArtworks.get(1).current_highest_bid).toBe(150);
      expect(state.activeArtworks.get(2).current_highest_bid).toBe(250);
      expect(state.activeArtworks.get(3).current_highest_bid).toBe(350);
    });
  });
});
