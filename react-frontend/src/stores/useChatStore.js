/**
 * Chat Store (Zustand)
 * ====================
 * Manages chat messages, loading state, and user identity.
 */

import { create } from 'zustand';
import { sendMessage as sendMessageApi } from '../services/api';

// Generate a persistent user ID
const getUserId = () => {
  let id = localStorage.getItem('grocery_user_id');
  if (!id) {
    id = `user-${Date.now().toString(36)}-${Math.random().toString(36).slice(2, 8)}`;
    localStorage.setItem('grocery_user_id', id);
  }
  return id;
};

const useChatStore = create((set, get) => ({
  messages: [],
  isLoading: false,
  userId: getUserId(),

  /**
   * Send a message to the AI service and append response.
   */
  sendMessage: async (text) => {
    const { userId, messages } = get();

    // Add user message
    const userMsg = {
      id: Date.now(),
      role: 'user',
      text,
      timestamp: new Date().toISOString(),
    };

    set({ messages: [...messages, userMsg], isLoading: true });

    try {
      const response = await sendMessageApi(text, userId);

      const botMsg = {
        id: Date.now() + 1,
        role: 'bot',
        text: response.text || 'I received your message.',
        intent: response.intent,
        products: response.products || [],
        actions: response.actions || [],
        cartItems: response.cart_items || [],
        showCart: response.show_cart || false,
        timestamp: new Date().toISOString(),
      };

      set((state) => ({
        messages: [...state.messages, botMsg],
        isLoading: false,
      }));

      return botMsg;
    } catch (error) {
      console.error('Chat error:', error);

      const errorMsg = {
        id: Date.now() + 1,
        role: 'bot',
        text: "Sorry, I'm having trouble connecting right now. Please make sure the AI service is running on port 5000.",
        intent: 'ERROR',
        products: [],
        actions: [],
        timestamp: new Date().toISOString(),
      };

      set((state) => ({
        messages: [...state.messages, errorMsg],
        isLoading: false,
      }));

      return errorMsg;
    }
  },

  /**
   * Add a quick action as if the user typed it.
   */
  sendQuickAction: async (actionLabel) => {
    return get().sendMessage(actionLabel);
  },

  clearMessages: () => set({ messages: [] }),
}));

export default useChatStore;
