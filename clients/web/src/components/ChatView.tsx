import { useState } from 'react';
import { Activity, Send, Copy, Check, Volume2, TestTube, Globe, Cpu, Wrench, Calendar, Mail, Newspaper, ClipboardPaste, Camera, FileText, StickyNote, User } from 'lucide-react';
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

function CodeBlock({ code, language }: { code: string; language?: string }) {
  const [copied, setCopied] = useState(false);

  const handleCopy = () => {
    navigator.clipboard.writeText(code);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  return (
    <div className="code-block-container">
      <div className="code-block-header">
        <span className="code-lang">{language || 'code'}</span>
        <button className="copy-btn" onClick={handleCopy} title="Copy code">
          {copied ? <Check size={13} className="copy-icon-copied" /> : <Copy size={13} />}
          <span>{copied ? 'Copied!' : 'Copy'}</span>
        </button>
      </div>
      <pre className="code-block-content">
        <code>{code}</code>
      </pre>
    </div>
  );
}

function MessageContent({ text, role }: { text: string; role: string }) {
  if (role === 'system') {
    return (
      <div className="message-system-inner">
        <Wrench size={13} style={{ flexShrink: 0 }} />
        <span>{text}</span>
      </div>
    );
  }

  // Parse code blocks demarcated by ```
  const codeBlockRegex = /```(\w*)\n([\s\S]*?)```/g;
  const parts = [];
  let lastIndex = 0;
  let match;

  while ((match = codeBlockRegex.exec(text)) !== null) {
    if (match.index > lastIndex) {
      parts.push({ type: 'text', content: text.slice(lastIndex, match.index) });
    }
    parts.push({ type: 'code', language: match[1], content: match[2].trim() });
    lastIndex = match.index + match[0].length;
  }

  if (lastIndex < text.length) {
    parts.push({ type: 'text', content: text.slice(lastIndex) });
  }

  if (parts.length === 0) {
    parts.push({ type: 'text', content: text });
  }

  return (
    <>
      {parts.map((part, idx) =>
        part.type === 'code' ? (
          <CodeBlock key={idx} code={part.content} language={part.language} />
        ) : (
          <span key={idx} style={{ whiteSpace: 'pre-wrap' }}>
            {part.content}
          </span>
        )
      )}
    </>
  );
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
  const quickActions = [
    { label: 'Calendar', prompt: 'Show my calendar for today', icon: Calendar },
    { label: 'Email', prompt: 'Check my inbox', icon: Mail },
    { label: 'News', prompt: 'Show me the latest headlines', icon: Newspaper },
    { label: 'Notes', prompt: 'List my recent notes', icon: StickyNote },
    { label: 'Volume', prompt: 'Mute the system volume', icon: Volume2 },
    { label: 'Screenshot', prompt: 'Take a screenshot and read the text', icon: Camera },
    { label: 'Vitals', prompt: 'Show system vitals', icon: Cpu },
    { label: 'Contacts', prompt: 'List my contacts', icon: User },
  ];

  return (
    <>
      <main className="chat-container glass-panel">
        {messages.length === 0 && (
          <div className="empty-chat-welcome">
            <div className="welcome-avatar">J</div>
            <h3>Jarvis Central Mind</h3>
            <p>Your personal AI assistant. Ask anything, or tap a quick action below.</p>
          </div>
        )}

        {messages.map((m) => (
          <div key={m.id} className={`message-bubble animate-slide-up message-${m.role}`}>
            <MessageContent text={m.text} role={m.role} />
          </div>
        ))}
        <div ref={chatEndRef} />
      </main>

      <div className="quick-actions-bar">
        {quickActions.map((action, idx) => {
          const Icon = action.icon;
          return (
            <button
              key={idx}
              className="quick-chip-btn"
              onClick={() => onInputChange(action.prompt)}
              disabled={!isConnected || isBusy}
              title={action.label}
            >
              <Icon size={14} />
              <span>{action.label}</span>
            </button>
          );
        })}
      </div>

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
          {isBusy ? <Activity size={16} className="animate-spin" /> : <Send size={16} />}
        </button>
      </div>
    </>
  );
}
