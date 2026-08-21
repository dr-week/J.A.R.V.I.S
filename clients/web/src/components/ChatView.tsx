import { useState } from 'react';
import {
  Activity,
  Send,
  Copy,
  Check,
  Volume2,
  Cpu,
  Wrench,
  Calendar,
  Mail,
  Newspaper,
  Camera,
  StickyNote,
  User,
  Sparkles,
  GitPullRequest,
  BookOpen,
  MessageSquare,
  Layers,
  Music,
  Workflow,
} from 'lucide-react';
import type { RefObject } from 'react';
import type { ChatMessage } from '../types/chat';
import { Tooltip, TooltipTrigger, TooltipContent } from './ui/tooltip';

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
    <div className="code-block-container my-2 overflow-hidden rounded-xl border border-white/10 bg-[#0a0a10]/95 shadow-md">
      <div className="code-block-header flex items-center justify-between border-b border-white/5 bg-white/[0.03] px-3.5 py-1.5 text-xs text-muted-foreground">
        <span className="code-lang font-mono text-[0.72rem] lowercase">{language || 'code'}</span>
        <Tooltip>
          <TooltipTrigger asChild>
            <button
              type="button"
              className="copy-btn inline-flex items-center gap-1.5 rounded-md px-2 py-1 text-xs text-muted-foreground transition hover:bg-white/10 hover:text-foreground focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-ring"
              onClick={handleCopy}
              aria-label={copied ? 'Copied to clipboard' : 'Copy code to clipboard'}
            >
              {copied ? <Check size={13} className="copy-icon-copied text-emerald-400" /> : <Copy size={13} />}
              <span>{copied ? 'Copied!' : 'Copy'}</span>
            </button>
          </TooltipTrigger>
          <TooltipContent side="top">
            <span>{copied ? 'Copied!' : 'Copy snippet'}</span>
          </TooltipContent>
        </Tooltip>
      </div>
      <pre className="code-block-content m-0 overflow-x-auto p-3.5 font-mono text-[0.82rem] leading-relaxed text-slate-200">
        <code>{code}</code>
      </pre>
    </div>
  );
}

function MessageContent({ text, role }: { text: string; role: string }) {
  if (role === 'system') {
    return (
      <div className="message-system-inner flex items-center gap-2">
        <Wrench size={14} className="shrink-0" />
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
          <span key={idx} className="whitespace-pre-wrap">
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
    { label: 'GitHub', prompt: 'List open issues on GitHub repository', icon: GitPullRequest },
    { label: 'Linear', prompt: 'List my open Linear project issues', icon: Layers },
    { label: 'Automation', prompt: 'List active automation tasks', icon: Workflow },
    { label: 'Notion', prompt: 'Search Notion workspace for project notes', icon: BookOpen },
    { label: 'Slack', prompt: 'List available Slack channels', icon: MessageSquare },
    { label: 'Spotify', prompt: 'Play music on Spotify', icon: Music },
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
      <main
        className="chat-container glass-panel flex-1 overflow-y-auto rounded-2xl p-5 md:p-6 flex flex-col gap-3.5 mb-2.5 border border-white/10"
        role="log"
        aria-live="polite"
        aria-label="Conversation history"
      >
        {messages.length === 0 && (
          <div className="empty-chat-welcome flex flex-col items-center justify-center my-auto text-center animate-fade-in py-12">
            <div className="welcome-avatar welcome-avatar-ring relative mb-4 flex h-16 w-16 items-center justify-center rounded-2xl bg-gradient-to-br from-[#0a84ff] to-[#7c3aed] text-white shadow-lg animate-pulse">
              <Sparkles size={32} />
            </div>
            <h3 className="text-xl font-semibold tracking-tight bg-gradient-to-r from-[#0a84ff] to-[#7c3aed] bg-clip-text text-transparent mb-1.5">
              Jarvis Central Mind
            </h3>
            <p className="text-sm text-muted-foreground max-w-xs leading-relaxed">
              Your personal AI assistant. Ask anything, or tap a quick action below.
            </p>
          </div>
        )}

        {messages.map((m) => (
          <div
            key={m.id}
            className={`message-bubble animate-slide-up message-${m.role}`}
            data-role={m.role}
          >
            <MessageContent text={m.text} role={m.role} />
          </div>
        ))}
        <div ref={chatEndRef} />
      </main>

      <div className="quick-actions-bar flex flex-wrap justify-center gap-2 py-1 shrink-0" role="toolbar" aria-label="Quick actions">
        {quickActions.map((action, idx) => {
          const Icon = action.icon;
          return (
            <Tooltip key={idx}>
              <TooltipTrigger asChild>
                <button
                  type="button"
                  className="quick-chip-btn inline-flex items-center gap-1.5 rounded-full border border-white/10 bg-white/[0.04] px-3.5 py-1.5 text-xs font-medium text-muted-foreground transition hover:border-primary/30 hover:bg-primary/10 hover:text-foreground active:scale-95 disabled:pointer-events-none disabled:opacity-35"
                  onClick={() => onInputChange(action.prompt)}
                  disabled={!isConnected || isBusy}
                  aria-label={action.label}
                >
                  <Icon size={14} />
                  <span>{action.label}</span>
                </button>
              </TooltipTrigger>
              <TooltipContent side="top">
                <span>"{action.prompt}"</span>
              </TooltipContent>
            </Tooltip>
          );
        })}
      </div>

      <div className="composer-container glass-panel flex items-center gap-2.5 rounded-full border border-white/10 px-4 py-2 shrink-0 transition focus-within:border-primary/40 focus-within:ring-2 focus-within:ring-primary/20">
        <input
          type="text"
          className="composer-input flex-1 bg-transparent py-1 text-sm text-foreground placeholder:text-muted-foreground/60 outline-none"
          value={input}
          onChange={(e) => onInputChange(e.target.value)}
          onKeyDown={(e) => e.key === 'Enter' && onSend()}
          placeholder="Message Jarvis..."
          disabled={!isConnected || isBusy}
          aria-label="Type a message"
        />
        <Tooltip>
          <TooltipTrigger asChild>
            <button
              type="button"
              className="composer-button flex h-9 w-9 shrink-0 items-center justify-center rounded-full bg-gradient-to-r from-[#0a84ff] to-[#7c3aed] text-white shadow-md transition hover:scale-105 hover:shadow-lg active:scale-95 disabled:pointer-events-none disabled:bg-muted-foreground/30 disabled:opacity-40"
              onClick={onSend}
              disabled={!input.trim() || !isConnected || isBusy}
              aria-label="Send message"
            >
              {isBusy ? <Activity size={16} className="animate-spin" /> : <Send size={16} />}
            </button>
          </TooltipTrigger>
          <TooltipContent side="top">
            <span>Send message</span>
          </TooltipContent>
        </Tooltip>
      </div>
    </>
  );
}
