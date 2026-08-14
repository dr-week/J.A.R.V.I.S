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
    <div className="flex h-screen h-dvh w-screen overflow-hidden bg-background text-foreground">
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

      <div className="flex-1 flex flex-col h-full p-2.5 sm:p-3.5 md:p-4 max-w-[900px] mx-auto w-full box-border">
        {/* Header (Status Zone per DESIGN.md: Honest status, no duplicate brand) */}
        <header className="flex justify-between items-center py-2 px-3.5 sm:px-4.5 rounded-2xl mb-2.5 shrink-0 glass-panel border border-border">
          <div className="flex items-center gap-2">
            <button
              className="md:hidden bg-transparent border-none text-foreground hover:bg-muted p-1.5 rounded-lg cursor-pointer transition-colors"
              onClick={() => app.setSidebarOpen(true)}
              aria-label="Open navigation menu"
            >
              <Menu size={20} />
            </button>
            <span className="font-semibold text-sm sm:text-base text-foreground tracking-tight">
              {app.activeTab === 'settings' ? 'Settings' : 'Current session'}
            </span>
          </div>

          <div className="flex items-center gap-2.5 sm:gap-3">
            <div
              className={`w-2 h-2 rounded-full shrink-0 transition-all duration-300 ${
                app.isConnected
                  ? 'bg-emerald-500 shadow-[0_0_8px_rgba(52,199,89,0.5),0_0_16px_rgba(52,199,89,0.2)]'
                  : 'bg-muted-foreground/40'
              }`}
            />
            <div className="flex flex-col items-end gap-0.5 max-w-[130px] sm:max-w-[200px]">
              <div className="text-xs sm:text-[0.84rem] text-foreground font-medium flex items-center truncate">
                <span className="truncate">{app.statusLine}</span>
                {app.llmReady === false && (
                  <span className="text-destructive ml-1 text-xs font-semibold shrink-0">(LLM Offline)</span>
                )}
              </div>
              {app.bridgeStatus && (
                <span className="text-[0.7rem] sm:text-[0.72rem] text-muted-foreground truncate">
                  {app.bridgeStatus}
                </span>
              )}
            </div>

            {app.activeTab === 'chat' && (
              <button
                className="bg-transparent border-none text-muted-foreground hover:text-foreground hover:bg-muted p-1.5 rounded-lg flex items-center justify-center cursor-pointer transition-colors"
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
