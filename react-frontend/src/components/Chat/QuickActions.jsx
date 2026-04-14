/**
 * QuickActions Component
 * ======================
 * Renders actionable buttons from bot responses.
 */

import useChatStore from '../../stores/useChatStore';

export default function QuickActions({ actions }) {
  const sendMessage = useChatStore((s) => s.sendMessage);

  if (!actions || actions.length === 0) return null;

  const handleAction = (action) => {
    // Map action types to natural language commands
    const actionMessages = {
      ADD_ALL: 'Add all to cart',
      SHOW_ALTERNATIVES: 'Show alternatives',
      SHOW_PRODUCTS: 'Show products',
      ADD_TO_CART: 'Add to cart',
      GET_RECIPE: 'Cook something',
      BUDGET_MODE: 'Budget meal under ₹200',
      HELP: 'Help',
    };

    const message = actionMessages[action.action] || action.label;
    sendMessage(message);
  };

  return (
    <div className="quick-actions">
      {actions.map((action, i) => (
        <button
          key={i}
          className="quick-action-btn"
          onClick={() => handleAction(action)}
        >
          {action.label}
        </button>
      ))}
    </div>
  );
}
