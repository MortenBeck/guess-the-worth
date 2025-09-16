import { create } from 'zustand';
import { persist } from 'zustand/middleware';

const useAuthStore = create(
  persist(
    (set, get) => ({
      user: null,
      token: null,
      isAuthenticated: false,
      isLoading: false,

      setAuth: (user, token) =>
        set({
          user,
          token,
          isAuthenticated: true,
          isLoading: false,
        }),

      clearAuth: () =>
        set({
          user: null,
          token: null,
          isAuthenticated: false,
          isLoading: false,
        }),

      setLoading: (isLoading) => set({ isLoading }),

      updateUser: (userData) =>
        set((state) => ({
          user: { ...state.user, ...userData },
        })),

      // Role helpers
      hasRole: (role) => {
        const state = get();
        return state.user?.role === role;
      },

      isAdmin: () => {
        const state = get();
        return state.user?.role === 'admin';
      },

      isSeller: () => {
        const state = get();
        return state.user?.role === 'seller' || state.user?.role === 'admin';
      },

      isBuyer: () => {
        const state = get();
        return ['buyer', 'seller', 'admin'].includes(state.user?.role);
      },
    }),
    {
      name: 'auth-storage',
      partialize: (state) => ({
        user: state.user,
        token: state.token,
        isAuthenticated: state.isAuthenticated,
      }),
    }
  )
);

export default useAuthStore;