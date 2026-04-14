/**
 * MessageBubble Component
 * =======================
 * Renders a single chat message — user or bot.
 * Bot messages can include product cards and action buttons.
 */

import useChatStore from '../../stores/useChatStore';
import useCartStore from '../../stores/useCartStore';
import QuickActions from './QuickActions';
import ProductCard from '../Products/ProductCard';

export default function MessageBubble({ message }) {
  const isUser = message.role === 'user';

  // Parse bold **text** in bot messages
  const formatText = (text) => {
    if (!text) return '';
    const parts = text.split(/(\*\*[^*]+\*\*)/g);
    return parts.map((part, i) => {
      if (part.startsWith('**') && part.endsWith('**')) {
        return <strong key={i}>{part.slice(2, -2)}</strong>;
      }
      return part;
    });
  };

  return (
    <div className={`message message--${isUser ? 'user' : 'bot'}`}>
      <div className="message__avatar">
        {isUser ? '👤' : '🤖'}
      </div>
      <div className="message__content">
        <div className="message__bubble">
          {formatText(message.text)}
        </div>

        {/* Product cards */}
        {!isUser && message.products && message.products.length > 0 && (
          <div className="products-grid">
            {message.products.map((product, i) => (
              <ProductCard key={product.id || i} product={product} />
            ))}
          </div>
        )}

        {/* Quick actions */}
        {!isUser && message.actions && message.actions.length > 0 && (
          <QuickActions actions={message.actions} />
        )}
      </div>
    </div>
  );
}
