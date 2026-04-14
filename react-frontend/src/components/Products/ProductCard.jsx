/**
 * ProductCard Component
 * =====================
 * Displays a grocery product with price, stock, match badge, and add-to-cart.
 */

import { IoCartOutline } from 'react-icons/io5';
import useChatStore from '../../stores/useChatStore';
import useCartStore from '../../stores/useCartStore';

export default function ProductCard({ product }) {
  const userId = useChatStore((s) => s.userId);
  const addItem = useCartStore((s) => s.addItem);

  const matchType = product.match_type || 'exact';

  const handleAdd = () => {
    if (product.id) {
      addItem(userId, product.id, 1);
    }
  };

  return (
    <div className="product-card">
      {/* Match type badge */}
      <span className={`product-card__badge product-card__badge--${matchType}`}>
        {matchType === 'substitute' ? `↔ ${product.substitute_for || 'substitute'}` : matchType}
      </span>

      {/* Product name */}
      <span className="product-card__name">{product.name}</span>

      {/* Price and stock */}
      <div className="product-card__details">
        <span className="product-card__price">₹{product.price}</span>
        <span className="product-card__stock">
          {product.stock > 0 ? `${product.stock} in stock` : 'Out of stock'}
        </span>
      </div>

      {/* Add to cart button */}
      {product.stock > 0 && (
        <button className="product-card__add-btn" onClick={handleAdd}>
          <IoCartOutline />
          Add to Cart
        </button>
      )}
    </div>
  );
}
