import { create } from "zustand";

const useFavoritesStore = create((set, get) => ({
  favorites: [],

  addToFavorites: (artwork) => {
    const currentFavorites = get().favorites;
    if (!currentFavorites.find((fav) => fav.id === artwork.id)) {
      set({
        favorites: [...currentFavorites, { ...artwork, dateAdded: new Date().toISOString() }],
      });
    }
  },

  removeFromFavorites: (artworkId) => {
    set({
      favorites: get().favorites.filter((fav) => fav.id !== artworkId),
    });
  },

  isFavorite: (artworkId) => {
    return get().favorites.some((fav) => fav.id === artworkId);
  },

  toggleFavorite: (artwork) => {
    const isFav = get().isFavorite(artwork.id);
    if (isFav) {
      get().removeFromFavorites(artwork.id);
    } else {
      get().addToFavorites(artwork);
    }
  },
}));

export default useFavoritesStore;
