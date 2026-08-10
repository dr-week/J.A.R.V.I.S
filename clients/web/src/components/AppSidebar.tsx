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
        <Bot size={24} className="animate-pulse" color="var(--accent-color)" />
        Jarvis
        {open && (
          <button className="mobile-menu-btn" style={{ marginLeft: 'auto' }} onClick={onClose}>
            <X size={20} />
          </button>
        )}
      </div>
      <div className="sidebar-content">
        <div
          className={`sidebar-item ${activeTab === 'chat' ? 'active' : ''}`}
          onClick={() => onSelectTab('chat')}
        >
          <MessageSquare size={16} style={{ display: 'inline', marginRight: 8, verticalAlign: 'text-bottom' }} />
          Current Session
        </div>
        <div
          className={`sidebar-item ${activeTab === 'settings' ? 'active' : ''}`}
          onClick={() => onSelectTab('settings')}
        >
          <SettingsIcon size={16} style={{ display: 'inline', marginRight: 8, verticalAlign: 'text-bottom' }} />
          Settings
        </div>

        <div
          style={{
            marginTop: '24px',
            marginBottom: '8px',
            paddingLeft: '16px',
            fontSize: '0.75rem',
            textTransform: 'uppercase',
            color: 'var(--text-muted)',
            fontWeight: 600,
          }}
        >
          Recent Sessions
        </div>
        <div className="session-list">
          {sessions.map((s) => (
            <div
              key={s.id}
              className={`sidebar-item ${sessionId === s.id ? 'active' : ''}`}
              onClick={() => onLoadSession(s.id)}
              style={{
                display: 'flex',
                flexDirection: 'column',
                alignItems: 'flex-start',
                padding: '10px 16px',
              }}
            >
              <div
                style={{
                  fontWeight: 500,
                  fontSize: '0.9rem',
                  marginBottom: '4px',
                  whiteSpace: 'nowrap',
                  overflow: 'hidden',
                  textOverflow: 'ellipsis',
                  width: '100%',
                }}
              >
                {s.title || 'Untitled Session'}
              </div>
              <div
                style={{
                  fontSize: '0.75rem',
                  color: 'var(--text-muted)',
                  display: 'flex',
                  alignItems: 'center',
                }}
              >
                <Clock size={12} style={{ marginRight: 4 }} />
                {new Date(s.updated_at).toLocaleDateString()}{' '}
                {new Date(s.updated_at).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
              </div>
            </div>
          ))}
          {sessions.length === 0 && (
            <div style={{ padding: '8px 16px', fontSize: '0.85rem', color: 'var(--text-muted)' }}>
              No recent sessions
            </div>
          )}
        </div>
      </div>
    </aside>
  );
}
