import { Bot, Clock, MessageSquare, Settings as SettingsIcon, X } from 'lucide-react';
import type { SessionInfo } from '../api/brainApi';

interface AppSidebarProps {
  open: boolean;
  onClose: () => void;
  activeTab: 'chat' | 'settings';
  onSelectTab: (tab: 'chat' | 'settings') => void;
  sessions: SessionInfo[];
  sessionId: string;
  onLoadSession: (id: string) => void;
}

export function AppSidebar({
  open,
  onClose,
  activeTab,
  onSelectTab,
  sessions,
  sessionId,
  onLoadSession,
}: AppSidebarProps) {
  return (
    <aside className={`sidebar ${open ? 'open' : ''}`}>
      <div className="sidebar-header">
        <Bot size={22} className="animate-pulse" color="var(--accent-color)" />
        <span>Jarvis</span>
        {open && (
          <button className="mobile-menu-btn" style={{ marginLeft: 'auto' }} onClick={onClose} title="Close navigation">
            <X size={20} />
          </button>
        )}
      </div>
      <div className="sidebar-content">
        <div
          className={`sidebar-item ${activeTab === 'chat' ? 'active' : ''}`}
          onClick={() => onSelectTab('chat')}
        >
          <MessageSquare size={16} />
          <span>Current Session</span>
        </div>
        <div
          className={`sidebar-item ${activeTab === 'settings' ? 'active' : ''}`}
          onClick={() => onSelectTab('settings')}
        >
          <SettingsIcon size={16} />
          <span>Settings</span>
        </div>

        <div className="session-section-header">Recent Sessions</div>
        <div className="session-list">
          {sessions.map((s) => (
            <div
              key={s.id}
              className={`session-item ${sessionId === s.id ? 'active' : ''}`}
              onClick={() => onLoadSession(s.id)}
            >
              <div className="session-item-title">{s.title || 'Untitled Session'}</div>
              <div className="session-item-meta">
                <Clock size={12} />
                <span>
                  {new Date(s.updated_at).toLocaleDateString()}{' '}
                  {new Date(s.updated_at).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                </span>
              </div>
            </div>
          ))}
          {sessions.length === 0 && (
            <div style={{ padding: '8px 14px', fontSize: '0.82rem', color: 'var(--text-muted)' }}>
              No recent sessions
            </div>
          )}
        </div>
      </div>
    </aside>
  );
}
