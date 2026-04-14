/**
 * App Component
 * =============
 * Main layout — header + chat panel + cart sidebar.
 */

import { useEffect } from 'react';
import { IoCartOutline } from 'react-icons/io5';
import useChatStore from './stores/useChatStore';
import useCartStore from './stores/useCartStore';
import ChatContainer from './components/Chat/ChatContainer';
import CartSidebar from './components/Cart/CartSidebar';

export default function App() {
  const userId = useChatStore((s) => s.userId);
  const toggleCart = useCartStore((s) => s.toggleCart);
  const openCart = useCartStore((s) => s.openCart);
  const itemCount = useCartStore((s) => s.itemCount);
  const messages = useChatStore((s) => s.messages);

  // Fetch cart on mount
  useEffect(() => {
    useCartStore.getState().fetchCart(userId);
  }, [userId]);

  // Watch for bot messages that say show_cart = true
  useEffect(() => {
    const lastMsg = messages[messages.length - 1];
    if (lastMsg?.role === 'bot' && lastMsg.showCart) {
      openCart();
      // Refresh cart data
      useCartStore.getState().fetchCart(userId);
    }
  }, [messages, userId, openCart]);

  return (
    <div className="app">
      {/* ── Header ──────────────────────────────────────────────── */}
      <header className="app-header">
        <div className="app-header__brand">
          <span className="app-header__logo">🛒</span>
          <div>
            <div className="app-header__title">GroceryAI</div>
            <div className="app-header__subtitle">AI-Powered Grocery Shopping</div>
          </div>
        </div>

        <div className="app-header__actions">
          <button className="cart-toggle-btn" onClick={toggleCart} id="cart-toggle">
            <IoCartOutline size={18} />
            Cart
            {itemCount > 0 && (
              <span className="cart-toggle-btn__badge">{itemCount}</span>
            )}
          </button>
        </div>
      </header>

      {/* ── Main Content ────────────────────────────────────────── */}
      <main className="app-main">
        <ChatContainer />
        <CartSidebar />
      </main>
    </div>
  );
}
