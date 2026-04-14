/**
 * CartSummary Component
 * =====================
 * Cart total, item count, checkout and clear buttons.
 */

import useChatStore from '../../stores/useChatStore';
import useCartStore from '../../stores/useCartStore';

export default function CartSummary() {
  const userId = useChatStore((s) => s.userId);
  const total = useCartStore((s) => s.total);
  const itemCount = useCartStore((s) => s.itemCount);
  const clearCart = useCartStore((s) => s.clearCart);

  return (
    <div className="cart-summary">
      <div className="cart-summary__row">
        <span className="cart-summary__label">Total</span>
        <span className="cart-summary__value">₹{total}</span>
      </div>
      <span className="cart-summary__item-count">{itemCount} item{itemCount !== 1 ? 's' : ''} in cart</span>

      <div className="cart-summary__actions">
        <button className="cart-summary__checkout-btn">
          Proceed to Checkout
        </button>
        <button
          className="cart-summary__clear-btn"
          onClick={() => clearCart(userId)}
        >
          Clear
        </button>
      </div>
    </div>
  );
}
