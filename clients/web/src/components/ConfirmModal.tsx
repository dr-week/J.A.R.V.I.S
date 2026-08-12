import { ShieldAlert, Check, X } from 'lucide-react';
import type { ConfirmRequest } from '../types/chat';
import './ConfirmModal.css';

interface ConfirmModalProps {
  request: ConfirmRequest;
  onResolve: (approved: boolean) => void;
}

export function ConfirmModal({ request, onResolve }: ConfirmModalProps) {
  return (
    <div className="confirm-modal-overlay">
      <div className="confirm-modal-content glass-panel animate-slide-up">
        <div className="confirm-header">
          <div className="confirm-icon-wrapper">
            <ShieldAlert size={24} className="confirm-icon" />
          </div>
          <h2 className="confirm-title">Approve Action</h2>
        </div>
        
        <div className="confirm-body">
          <p className="confirm-message">
            Jarvis wants to execute <span className="confirm-tool-name">{request.tool}</span>.
          </p>
          <div className="confirm-params">
            <pre>{JSON.stringify(request.params, null, 2)}</pre>
          </div>
        </div>

        <div className="confirm-actions">
          <button 
            className="confirm-btn deny" 
            onClick={() => onResolve(false)}
          >
            <X size={18} /> Deny
          </button>
          <button 
            className="confirm-btn approve" 
            onClick={() => onResolve(true)}
          >
            <Check size={18} /> Approve
          </button>
        </div>
      </div>
    </div>
  );
}
