import { create } from "zustand";

const useBiddingStore = create((set, get) => ({
  activeArtworks: new Map(),
  currentBids: new Map(),
  socketConnected: false,

  setSocketConnected: (connected) => set({ socketConnected: connected }),

  joinArtwork: (artworkId, artworkData) =>
    set((state) => {
      const newActiveArtworks = new Map(state.activeArtworks);
      newActiveArtworks.set(artworkId, artworkData);
      return { activeArtworks: newActiveArtworks };
    }),

  leaveArtwork: (artworkId) =>
    set((state) => {
      const newActiveArtworks = new Map(state.activeArtworks);
      const newCurrentBids = new Map(state.currentBids);
      newActiveArtworks.delete(artworkId);
      newCurrentBids.delete(artworkId);
      return {
        activeArtworks: newActiveArtworks,
        currentBids: newCurrentBids,
      };
    }),

  updateBid: (artworkId, bidData) =>
    set((state) => {
      const newCurrentBids = new Map(state.currentBids);
      const newActiveArtworks = new Map(state.activeArtworks);

      newCurrentBids.set(artworkId, bidData);

      // Update artwork's current highest bid
      if (newActiveArtworks.has(artworkId)) {
        const artwork = newActiveArtworks.get(artworkId);
        newActiveArtworks.set(artworkId, {
          ...artwork,
          current_highest_bid: bidData.amount,
        });
      }

      return {
        currentBids: newCurrentBids,
        activeArtworks: newActiveArtworks,
      };
    }),

  markArtworkSold: (artworkId) =>
    set((state) => {
      const newActiveArtworks = new Map(state.activeArtworks);
      if (newActiveArtworks.has(artworkId)) {
        const artwork = newActiveArtworks.get(artworkId);
        newActiveArtworks.set(artworkId, {
          ...artwork,
          status: "sold",
        });
      }
      return { activeArtworks: newActiveArtworks };
    }),

  clearAll: () =>
    set({
      activeArtworks: new Map(),
      currentBids: new Map(),
    }),
}));

export default useBiddingStore;
