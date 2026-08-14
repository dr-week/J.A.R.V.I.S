import { Terminal } from 'lucide-react';
import type { VelocityUpdate } from '../types/chat';

interface VelocityProgressProps {
  update: VelocityUpdate;
}

export function VelocityProgress({ update }: VelocityProgressProps) {
  const isError = update.status === 'error';
  const isComplete = update.status === 'complete';
  const progressPercent = typeof update.progress === 'number' ? Math.max(5, update.progress * 100) : 100;

  return (
    <div
      className={`p-4 rounded-xl mb-3.5 flex flex-col gap-3 glass-panel border-l-4 animate-slide-up ${
        isError ? 'border-l-destructive' : 'border-l-primary'
      }`}
    >
      <div className="flex items-center gap-2.5 text-sm text-muted-foreground">
        <Terminal size={16} className={!isComplete && !isError ? 'animate-pulse text-primary' : ''} />
        <span className="font-semibold text-foreground">{update.app_id || 'Jarvis Tool'}</span>
        <span
          className={`px-2 py-0.5 rounded-sm text-[0.72rem] uppercase tracking-wider font-semibold border ${
            isError
              ? 'bg-destructive/15 text-destructive border-destructive/30'
              : 'bg-muted text-muted-foreground border-border'
          }`}
        >
          {update.status}
        </span>
      </div>
      <div className="flex flex-col gap-1.5">
        <div className="text-[0.92rem] leading-relaxed text-foreground">
          {update.message || update.step || 'Running background task...'}
        </div>
        {!isComplete && !isError && (
          <div className="h-1.5 bg-white/10 rounded-full overflow-hidden mt-1.5">
            <div 
              className="h-full bg-gradient-to-r from-primary to-purple-600 transition-all duration-300 rounded-full" 
              style={{ width: `${progressPercent}%` }}
            />
          </div>
        )}
      </div>
    </div>
  );
}
