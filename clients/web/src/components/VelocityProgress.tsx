import { Terminal } from 'lucide-react';
import type { VelocityUpdate } from '../types/chat';
import './VelocityProgress.css';

interface VelocityProgressProps {
  update: VelocityUpdate;
}

export function VelocityProgress({ update }: VelocityProgressProps) {
  const isError = update.status === 'error';
  const isComplete = update.status === 'complete';
  const progressPercent = typeof update.progress === 'number' ? Math.max(5, update.progress * 100) : 100;

  return (
    <div className={`velocity-panel glass-panel animate-slide-up ${isError ? 'velocity-error' : ''}`}>
      <div className="velocity-header">
        <Terminal size={16} className={!isComplete && !isError ? 'animate-pulse' : ''} />
        <span className="velocity-app-id">{update.app_id || 'Jarvis Tool'}</span>
        <span className="velocity-status-badge">{update.status}</span>
      </div>
      <div className="velocity-body">
        <div className="velocity-message">{update.message || update.step || 'Running background task...'}</div>
        {!isComplete && !isError && (
          <div className="velocity-progress-bar">
            <div 
              className="velocity-progress-fill" 
              style={{ width: `${progressPercent}%` }}
            />
          </div>
        )}
      </div>
    </div>
  );
}
