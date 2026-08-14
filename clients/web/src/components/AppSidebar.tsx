import { Bot, Clock, MessageSquare, Settings as SettingsIcon, X } from 'lucide-react';
import type { SessionInfo } from '../api/brainApi';
import { Tooltip, TooltipTrigger, TooltipContent } from './ui/tooltip';
import { cn } from '../lib/utils';

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
    <>
      {/* Mobile backdrop overlay with Radix-like animation */}
      {open && (
        <div
          className="sidebar-overlay fixed inset-0 z-40 bg-black/60 backdrop-blur-sm transition-opacity duration-200 md:hidden"
          onClick={onClose}
          aria-hidden="true"
        />
      )}

      <aside
        className={cn(
          'sidebar z-50 flex w-64 flex-col border-r border-white/10 bg-[#0c0c12]/80 p-5 backdrop-blur-xl transition-all duration-300',
          open ? 'open translate-x-0' : '-translate-x-full md:translate-x-0'
        )}
        role="navigation"
        aria-label="Main Navigation"
      >
        <div className="sidebar-header mb-6 flex items-center gap-2.5 px-2 text-lg font-semibold tracking-tight text-foreground">
          <Bot size={22} className="animate-pulse text-primary" />
          <span className="font-bold">Jarvis</span>
          {open && (
            <Tooltip>
              <TooltipTrigger asChild>
                <button
                  type="button"
                  className="mobile-menu-btn ml-auto rounded-md p-1.5 text-muted-foreground transition hover:bg-white/10 hover:text-foreground md:hidden"
                  onClick={onClose}
                  aria-label="Close navigation"
                >
                  <X size={18} />
                </button>
              </TooltipTrigger>
              <TooltipContent side="right">
                <span>Close menu</span>
              </TooltipContent>
            </Tooltip>
          )}
        </div>

        <div className="sidebar-content flex flex-1 flex-col gap-1 overflow-y-auto">
          <button
            type="button"
            className={cn(
              'sidebar-item group relative flex w-full items-center gap-2.5 rounded-xl px-3.5 py-2.5 text-left text-sm font-medium transition duration-150',
              activeTab === 'chat'
                ? 'active bg-primary/15 text-foreground border border-primary/20 shadow-sm'
                : 'text-muted-foreground hover:bg-white/[0.04] hover:text-foreground'
            )}
            onClick={() => onSelectTab('chat')}
            aria-current={activeTab === 'chat' ? 'page' : undefined}
          >
            <MessageSquare size={16} className={activeTab === 'chat' ? 'text-primary' : 'text-muted-foreground'} />
            <span>Current Session</span>
          </button>

          <button
            type="button"
            className={cn(
              'sidebar-item group relative flex w-full items-center gap-2.5 rounded-xl px-3.5 py-2.5 text-left text-sm font-medium transition duration-150',
              activeTab === 'settings'
                ? 'active bg-primary/15 text-foreground border border-primary/20 shadow-sm'
                : 'text-muted-foreground hover:bg-white/[0.04] hover:text-foreground'
            )}
            onClick={() => onSelectTab('settings')}
            aria-current={activeTab === 'settings' ? 'page' : undefined}
          >
            <SettingsIcon size={16} className={activeTab === 'settings' ? 'text-primary' : 'text-muted-foreground'} />
            <span>Settings</span>
          </button>

          <div className="session-section-header mt-6 mb-2 px-3 text-[0.72rem] font-semibold uppercase tracking-wider text-muted-foreground/80">
            Recent Sessions
          </div>

          <div className="session-list flex flex-col gap-1" role="list" aria-label="Recent chat sessions">
            {sessions.map((s) => {
              const isCurrent = sessionId === s.id;
              return (
                <button
                  type="button"
                  key={s.id}
                  className={cn(
                    'session-item flex w-full flex-col items-start gap-1 rounded-xl px-3.5 py-2 text-left text-sm transition duration-150',
                    isCurrent
                      ? 'active bg-primary/15 text-foreground border border-primary/20'
                      : 'text-muted-foreground hover:bg-white/[0.04] hover:text-foreground'
                  )}
                  onClick={() => onLoadSession(s.id)}
                  aria-selected={isCurrent}
                  role="listitem"
                >
                  <div className="session-item-title w-full truncate font-medium text-[0.86rem]">
                    {s.title || 'Untitled Session'}
                  </div>
                  <div className="session-item-meta flex items-center gap-1.5 text-[0.72rem] text-muted-foreground/70">
                    <Clock size={11} />
                    <span>
                      {new Date(s.updated_at).toLocaleDateString()}{' '}
                      {new Date(s.updated_at).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                    </span>
                  </div>
                </button>
              );
            })}

            {sessions.length === 0 && (
              <div className="px-3 py-2 text-xs text-muted-foreground/60 italic">
                No recent sessions
              </div>
            )}
          </div>
        </div>
      </aside>
    </>
  );
}
