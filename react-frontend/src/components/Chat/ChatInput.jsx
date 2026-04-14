/**
 * ChatInput Component
 * ===================
 * Message input with send button.
 */

import { useState } from 'react';
import { IoSend } from 'react-icons/io5';
import useChatStore from '../../stores/useChatStore';

export default function ChatInput() {
  const [text, setText] = useState('');
  const sendMessage = useChatStore((s) => s.sendMessage);
  const isLoading = useChatStore((s) => s.isLoading);

  const handleSubmit = (e) => {
    e.preventDefault();
    const trimmed = text.trim();
    if (!trimmed || isLoading) return;

    sendMessage(trimmed);
    setText('');
  };

  const handleKeyDown = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSubmit(e);
    }
  };

  return (
    <div className="chat-input-container">
      <form className="chat-input-wrapper" onSubmit={handleSubmit}>
        <input
          className="chat-input"
          type="text"
          value={text}
          onChange={(e) => setText(e.target.value)}
          onKeyDown={handleKeyDown}
          placeholder="Ask me to cook something, or search for products..."
          disabled={isLoading}
          autoFocus
          id="chat-input"
        />
        <button
          className="chat-input-send"
          type="submit"
          disabled={!text.trim() || isLoading}
          aria-label="Send message"
          id="send-button"
        >
          <IoSend />
        </button>
      </form>
    </div>
  );
}
