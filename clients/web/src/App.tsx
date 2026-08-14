import { Menu, Trash2 } from 'lucide-react';
import { Settings } from './components/Settings';
import { AppSidebar } from './components/AppSidebar';
import { ChatView } from './components/ChatView';
import { VelocityProgress } from './components/VelocityProgress';
import { ConfirmModal } from './components/ConfirmModal';
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
        <header className="header glass-panel">
          <div className="header-title">
            <button
              className="mobile-menu-btn"
              onClick={() => app.setSidebarOpen(true)}
              aria-label="Open menu"
            >
              <Menu size={20} />
            </button>
            <span className="header-context">
              {app.activeTab === 'settings' ? 'Settings' : 'Current session'}
            </span>
          </div>

          <div className="header-status-wrapper">
            <div className={`status-indicator ${app.isConnected ? 'connected' : ''}`} />
            <div className="header-status-info">
              <div className="header-status-text">
                <span>{app.statusLine}</span>
                {app.llmReady === false && (
                  <span style={{ color: 'var(--danger-color)', marginLeft: 6 }}>(LLM Offline)</span>
                )}
              </div>
              {app.bridgeStatus && (
                <span className="header-status-sub">{app.bridgeStatus}</span>
              )}
            </div>

            {app.activeTab === 'chat' && (
              <button
                className="header-action-btn"
                onClick={app.handleClearChat}
                title="Start new session"
                aria-label="Clear chat"
              >
                <Trash2 size={16} />
              </button>
            )}
          </div>
        </header>

        {app.velocityUpdate && <VelocityProgress update={app.velocityUpdate} />}

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

      {app.confirmRequest && (
        <ConfirmModal 
          request={app.confirmRequest} 
          onResolve={app.handleConfirmResult} 
        />
      )}
    </div>
  );
}

export default App;
