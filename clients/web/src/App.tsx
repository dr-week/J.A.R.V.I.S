import { Menu, Trash2 } from 'lucide-react';
import { Settings } from './components/Settings';
import { AppSidebar } from './components/AppSidebar';
import { ChatView } from './components/ChatView';
import { VelocityProgress } from './components/VelocityProgress';
import { ConfirmModal } from './components/ConfirmModal';
import { useJarvisApp } from './hooks/useJarvisApp';
import { TooltipProvider, Tooltip, TooltipTrigger, TooltipContent } from './components/ui/tooltip';
import './App.css';

function App() {
  const app = useJarvisApp();

  return (
    <TooltipProvider delayDuration={200}>
      <div className="app-layout flex h-[100dvh] w-screen overflow-hidden bg-background text-foreground">
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

        <div className="app-container flex flex-1 flex-col h-full max-w-4xl mx-auto p-3 sm:p-4 box-border w-full">
          <header className="header glass-panel flex items-center justify-between px-4 py-2.5 rounded-2xl mb-3 shrink-0 border border-white/10">
            <div className="header-title flex items-center gap-2">
              <Tooltip>
                <TooltipTrigger asChild>
                  <button
                    type="button"
                    className="mobile-menu-btn md:hidden rounded-lg p-1.5 text-foreground hover:bg-white/10 transition"
                    onClick={() => app.setSidebarOpen(true)}
                    aria-label="Open menu"
                    aria-expanded={app.sidebarOpen}
                  >
                    <Menu size={20} />
                  </button>
                </TooltipTrigger>
                <TooltipContent side="bottom">
                  <span>Open navigation</span>
                </TooltipContent>
              </Tooltip>
              <span className="header-context font-semibold text-sm sm:text-base text-foreground tracking-tight">
                {app.activeTab === 'settings' ? 'Settings' : 'Current session'}
              </span>
            </div>

            <div className="header-status-wrapper flex items-center gap-3" role="status" aria-live="polite">
              <div
                className={`status-indicator w-2 h-2 rounded-full shrink-0 transition-all duration-300 ${
                  app.isConnected ? 'connected bg-emerald-400 shadow-[0_0_8px_rgba(52,199,89,0.6)]' : 'bg-zinc-600'
                }`}
                aria-label={app.isConnected ? 'Connected to brain' : 'Disconnected'}
              />
              <div className="header-status-info flex flex-col items-end gap-0.5">
                <div className="header-status-text text-xs sm:text-sm font-medium text-foreground flex items-center">
                  <span>{app.statusLine}</span>
                  {app.llmReady === false && (
                    <span className="text-destructive font-semibold ml-1.5">(LLM Offline)</span>
                  )}
                </div>
                {app.bridgeStatus && (
                  <span className="header-status-sub text-[0.7rem] text-muted-foreground">{app.bridgeStatus}</span>
                )}
              </div>

              {app.activeTab === 'chat' && (
                <Tooltip>
                  <TooltipTrigger asChild>
                    <button
                      type="button"
                      className="header-action-btn rounded-lg p-1.5 text-muted-foreground hover:text-foreground hover:bg-white/10 transition"
                      onClick={app.handleClearChat}
                      aria-label="Clear chat session"
                    >
                      <Trash2 size={16} />
                    </button>
                  </TooltipTrigger>
                  <TooltipContent side="bottom">
                    <span>New chat session</span>
                  </TooltipContent>
                </Tooltip>
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
    </TooltipProvider>
  );
}

export default App;
