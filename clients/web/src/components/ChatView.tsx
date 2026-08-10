import { Activity, Send } from 'lucide-react';
import type { RefObject } from 'react';
import type { ChatMessage } from '../types/chat';

interface ChatViewProps {
  messages: ChatMessage[];
  input: string;
  onInputChange: (value: string) => void;
  onSend: () => void;
  isBusy: boolean;
  isConnected: boolean;
  chatEndRef: RefObject<HTMLDivElement | null>;
}

export function ChatView({
  messages,
  input,
  onInputChange,
  onSend,
  isBusy,
  isConnected,
  chatEndRef,
}: ChatViewProps) {
  return (
    <>
      <main className="chat-container glass-panel">
        {messages.map((m) => (
          <div key={m.id} className={`message-bubble animate-slide-up message-${m.role}`}>
            {m.text}
          </div>
        ))}
        <div ref={chatEndRef} />
      </main>

      <div className="composer-container glass-panel">
        <input
          type="text"
          className="composer-input"
          value={input}
          onChange={(e) => onInputChange(e.target.value)}
          onKeyDown={(e) => e.key === 'Enter' && onSend()}
          placeholder="Message Jarvis..."
          disabled={!isConnected || isBusy}
        />
        <button
          className="composer-button"
          onClick={onSend}
          disabled={!input.trim() || !isConnected || isBusy}
        >
          {isBusy ? <Activity size={18} className="animate-spin" /> : <Send size={18} />}
        </button>
      </div>
    </>
  );
}
