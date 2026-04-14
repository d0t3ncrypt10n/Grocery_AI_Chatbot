/**
 * Cart Store (Zustand)
 * ====================
 * Manages cart state, syncs with Node.js backend.
 */

import { create } from 'zustand';
import {
  getCart as getCartApi,
  addToCart as addToCartApi,
  addAllToCart as addAllToCartApi,
  removeFromCart as removeFromCartApi,
  updateCartQuantity as updateCartQuantityApi,
  clearCart as clearCartApi,
} from '../services/api';

const useCartStore = create((set, get) => ({
  items: [],
  total: 0,
  itemCount: 0,
  isOpen: false,
  isLoading: false,

  /**
   * Toggle cart sidebar visibility.
   */
  toggleCart: () => set((state) => ({ isOpen: !state.isOpen })),
  openCart: () => set({ isOpen: true }),
  closeCart: () => set({ isOpen: false }),

  /**
   * Fetch cart from backend.
   */
  fetchCart: async (userId) => {
    try {
      const data = await getCartApi(userId);
      set({
        items: data.items || [],
        total: data.total || 0,
        itemCount: data.item_count || 0,
      });
    } catch (error) {
      console.error('Fetch cart error:', error);
    }
  },

  /**
   * Add a single item to cart.
   */
  addItem: async (userId, productId, quantity = 1) => {
    set({ isLoading: true });
    try {
      const data = await addToCartApi(userId, productId, quantity);
      set({
        items: data.items || [],
        total: data.total || 0,
        itemCount: data.item_count || 0,
        isOpen: true,
        isLoading: false,
      });
      return data;
    } catch (error) {
      console.error('Add to cart error:', error);
      set({ isLoading: false });
      return null;
    }
  },

  /**
   * Batch add items to cart.
   */
  addAllItems: async (userId, products) => {
    set({ isLoading: true });
    try {
      const data = await addAllToCartApi(userId, products);
      set({
        items: data.items || [],
        total: data.total || 0,
        itemCount: data.item_count || 0,
        isOpen: true,
        isLoading: false,
      });
      return data;
    } catch (error) {
      console.error('Add all error:', error);
      set({ isLoading: false });
      return null;
    }
  },

  /**
   * Remove item from cart.
   */
  removeItem: async (userId, itemId) => {
    try {
      const data = await removeFromCartApi(userId, itemId);
      set({
        items: data.items || [],
        total: data.total || 0,
        itemCount: data.item_count || 0,
      });
    } catch (error) {
      console.error('Remove error:', error);
    }
  },

  /**
   * Update item quantity.
   */
  updateQuantity: async (userId, itemId, quantity) => {
    try {
      const data = await updateCartQuantityApi(userId, itemId, quantity);
      set({
        items: data.items || [],
        total: data.total || 0,
        itemCount: data.item_count || 0,
      });
    } catch (error) {
      console.error('Update qty error:', error);
    }
  },

  /**
   * Clear entire cart.
   */
  clearCart: async (userId) => {
    try {
      await clearCartApi(userId);
      set({ items: [], total: 0, itemCount: 0 });
    } catch (error) {
      console.error('Clear cart error:', error);
    }
  },

  /**
   * Update cart from bot response (when show_cart is true).
   */
  syncFromResponse: (cartData) => {
    if (cartData && Array.isArray(cartData)) {
      // Refresh from backend when we get cart items in a response
      const userId = localStorage.getItem('grocery_user_id');
      if (userId) {
        get().fetchCart(userId);
      }
    }
  },
}));

export default useCartStore;
