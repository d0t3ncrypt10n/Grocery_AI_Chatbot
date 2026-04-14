/**
 * ChatContainer Component
 * =======================
 * Main chat panel — renders messages, welcome screen, and auto-scrolls.
 */

import { useEffect, useRef } from 'react';
import useChatStore from '../../stores/useChatStore';
import useCartStore from '../../stores/useCartStore';
import MessageBubble from './MessageBubble';
import ChatInput from './ChatInput';

export default function ChatContainer() {
  const messages = useChatStore((s) => s.messages);
  const isLoading = useChatStore((s) => s.isLoading);
  const messagesEndRef = useRef(null);

  // Auto-scroll to bottom on new messages
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages, isLoading]);

  return (
    <div className="chat-container">
      <div className="chat-messages">
        {messages.length === 0 && (
          <div className="chat-welcome">
            <div className="chat-welcome__icon">🛒</div>
            <h1 className="chat-welcome__title">Welcome to GroceryAI</h1>
            <p className="chat-welcome__text">
              Tell me what you'd like to cook, and I'll find all the ingredients for you.
              Or search for specific products — I'm here to help!
            </p>
            <WelcomeActions />
          </div>
        )}

        {messages.map((msg) => (
          <MessageBubble key={msg.id} message={msg} />
        ))}

        {isLoading && (
          <div className="message message--bot">
            <div className="message__avatar">🤖</div>
            <div className="message__content">
              <div className="typing-indicator">
                <div className="typing-indicator__dot" />
                <div className="typing-indicator__dot" />
                <div className="typing-indicator__dot" />
              </div>
            </div>
          </div>
        )}

        <div ref={messagesEndRef} />
      </div>

      <ChatInput />
    </div>
  );
}

function WelcomeActions() {
  const sendMessage = useChatStore((s) => s.sendMessage);

  const suggestions = [
    { label: '🍳 Make Butter Chicken', msg: 'Make butter chicken for 4 people' },
    { label: '🍝 Cook Pasta', msg: 'How to make pasta?' },
    { label: '🥘 Biryani Recipe', msg: 'Make chicken biryani for 3 people' },
    { label: '💰 Budget Meal', msg: 'Make a meal under ₹200' },
  ];

  return (
    <div className="quick-actions" style={{ justifyContent: 'center', marginTop: '8px' }}>
      {suggestions.map((s, i) => (
        <button
          key={i}
          className="quick-action-btn"
          onClick={() => sendMessage(s.msg)}
        >
          {s.label}
        </button>
      ))}
    </div>
  );
}
