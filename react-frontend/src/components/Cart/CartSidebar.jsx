/**
 * CartSidebar Component
 * =====================
 * Slide-out cart panel with items, summary, and actions.
 */

import { IoClose } from 'react-icons/io5';
import useCartStore from '../../stores/useCartStore';
import useChatStore from '../../stores/useChatStore';
import CartItemRow from './CartItem';
import CartSummary from './CartSummary';

export default function CartSidebar() {
  const isOpen = useCartStore((s) => s.isOpen);
  const closeCart = useCartStore((s) => s.closeCart);
  const items = useCartStore((s) => s.items);

  return (
    <aside className={`cart-sidebar ${!isOpen ? 'cart-sidebar--hidden' : ''}`}>
      <div className="cart-sidebar__header">
        <h2 className="cart-sidebar__title">
          🛒 Your Cart
        </h2>
        <button className="cart-sidebar__close" onClick={closeCart} aria-label="Close cart">
          <IoClose />
        </button>
      </div>

      <div className="cart-sidebar__items">
        {items.length === 0 ? (
          <div className="cart-sidebar__empty">
            <div className="cart-sidebar__empty-icon">🛒</div>
            <p className="cart-sidebar__empty-text">
              Your cart is empty.<br />
              Ask me to cook something to get started!
            </p>
          </div>
        ) : (
          items.map((item) => (
            <CartItemRow key={item.id} item={item} />
          ))
        )}
      </div>

      {items.length > 0 && <CartSummary />}
    </aside>
  );
}
