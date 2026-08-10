import { Menu, Trash2 } from 'lucide-react';
import { Settings } from './components/Settings';
import { AppSidebar } from './components/AppSidebar';
import { ChatView } from './components/ChatView';
import { useJarvisApp } from './hooks/useJarvisApp';
import './App.css';

function App() {
  const app = useJarvisApp();

  return (
    <div className="app-layout">
      <AppSidebar
        open={app.sidebarOpen}
        onClose={() => app.setSidebarOpen(false)}
        activeTab={app.activeTab}
        onSelectTab={(tab) => {
          app.setActiveTab(tab);
          app.setSidebarOpen(false);
        }}
        sessions={app.sessions}
        sessionId={app.sessionId}
        onLoadSession={app.handleLoadSession}
      />

      <div className="app-container">
        <header className="header glass-panel" style={{ justifyContent: 'space-between' }}>
          <div className="header-title" style={{ gap: '0', display: 'flex', alignItems: 'center' }}>
            <button className="mobile-menu-btn" onClick={() => app.setSidebarOpen(true)}>
              <Menu size={20} />
            </button>
            <span className="header-context" style={{ fontWeight: 600, fontSize: '1.1rem' }}>
              {app.activeTab === 'settings' ? 'Settings' : 'Current session'}
            </span>
          </div>
          <div className="header-status" style={{ flexDirection: 'row', alignItems: 'center', gap: '12px' }}>
            <div className={`status-indicator ${app.isConnected ? 'connected' : ''}`} />
            <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'flex-end', gap: '4px' }}>
              <span>
                {app.statusLine}
                {app.llmReady === false && (
                  <span style={{ color: '#ff3b30', marginLeft: 8 }}>(LLM Offline)</span>
                )}
              </span>
              <span style={{ fontSize: '0.75rem', opacity: 0.7 }}>{app.bridgeStatus}</span>
            </div>
          </div>
          {app.activeTab === 'chat' && (
            <button
              onClick={app.handleClearChat}
              title="Clear Chat"
              style={{
                background: 'transparent',
                border: 'none',
                color: 'var(--text-muted)',
                cursor: 'pointer',
                marginLeft: 16,
              }}
            >
              <Trash2 size={18} />
            </button>
          )}
        </header>

        {app.activeTab === 'settings' ? (
          <Settings />
        ) : (
          <ChatView
            messages={app.messages}
            input={app.input}
            onInputChange={app.setInput}
            onSend={app.handleSend}
            isBusy={app.isBusy}
            isConnected={app.isConnected}
            chatEndRef={app.chatEndRef}
          />
        )}
      </div>
    </div>
  );
}

export default App;
