/**
 * CartItem Component
 * ==================
 * Single cart item row with quantity controls and remove button.
 */

import { IoAdd, IoRemove, IoTrashOutline } from 'react-icons/io5';
import useChatStore from '../../stores/useChatStore';
import useCartStore from '../../stores/useCartStore';

export default function CartItemRow({ item }) {
  const userId = useChatStore((s) => s.userId);
  const updateQuantity = useCartStore((s) => s.updateQuantity);
  const removeItem = useCartStore((s) => s.removeItem);

  const handleDecrease = () => {
    if (item.quantity <= 1) {
      removeItem(userId, item.id);
    } else {
      updateQuantity(userId, item.id, item.quantity - 1);
    }
  };

  const handleIncrease = () => {
    updateQuantity(userId, item.id, item.quantity + 1);
  };

  return (
    <div className="cart-item">
      <div className="cart-item__info">
        <div className="cart-item__name">{item.name}</div>
        <div className="cart-item__price">
          ₹{item.price} × {item.quantity} = ₹{item.subtotal}
        </div>
      </div>

      <div className="cart-item__controls">
        <button
          className="cart-item__qty-btn"
          onClick={handleDecrease}
          aria-label="Decrease quantity"
        >
          <IoRemove />
        </button>
        <span className="cart-item__qty">{item.quantity}</span>
        <button
          className="cart-item__qty-btn"
          onClick={handleIncrease}
          aria-label="Increase quantity"
        >
          <IoAdd />
        </button>
      </div>

      <button
        className="cart-item__remove"
        onClick={() => removeItem(userId, item.id)}
        aria-label="Remove item"
      >
        <IoTrashOutline />
      </button>
    </div>
  );
}
