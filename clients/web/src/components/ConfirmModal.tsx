import { ShieldAlert, Check, X } from 'lucide-react';
import type { ConfirmRequest } from '../types/chat';
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from './ui/dialog';
import { Button } from './ui/button';

interface ConfirmModalProps {
  request: ConfirmRequest;
  onResolve: (approved: boolean) => void;
}

export function ConfirmModal({ request, onResolve }: ConfirmModalProps) {
  return (
    <Dialog open={true} onOpenChange={(open) => !open && onResolve(false)}>
      <DialogContent 
        className="max-w-md border border-white/10 bg-[#0e0e16]/95 backdrop-blur-2xl p-6 shadow-2xl rounded-2xl animate-slide-up"
        hideClose={false}
      >
        <DialogHeader className="flex flex-row items-center gap-3 space-y-0 text-left">
          <div className="flex h-10 w-10 shrink-0 items-center justify-center rounded-xl border border-destructive/30 bg-destructive/15 text-destructive">
            <ShieldAlert size={22} />
          </div>
          <div>
            <DialogTitle className="text-lg font-semibold tracking-tight text-foreground">
              Approve Action
            </DialogTitle>
            <div className="text-xs text-muted-foreground">Action Confirmation Required</div>
          </div>
        </DialogHeader>

        <div className="my-2 space-y-3">
          <DialogDescription className="text-sm leading-relaxed text-muted-foreground">
            Jarvis wants to execute{' '}
            <span className="inline-block rounded-md border border-primary/20 bg-primary/10 px-2 py-0.5 font-mono text-xs font-semibold text-primary">
              {request.tool}
            </span>
            .
          </DialogDescription>

          <div className="max-h-44 overflow-y-auto rounded-lg border border-white/10 bg-black/40 p-3 shadow-inner">
            <pre className="m-0 font-mono text-xs text-slate-300 whitespace-pre-wrap break-words">
              {JSON.stringify(request.params, null, 2)}
            </pre>
          </div>
        </div>

        <DialogFooter className="mt-4 flex flex-row justify-end gap-2.5 sm:space-x-0">
          <Button
            type="button"
            variant="glass"
            className="border-red-500/20 text-muted-foreground hover:border-red-500/40 hover:bg-destructive/15 hover:text-destructive transition-all"
            onClick={() => onResolve(false)}
          >
            <X size={16} /> Deny
          </Button>
          <Button
            type="button"
            variant="accent"
            className="transition-all"
            onClick={() => onResolve(true)}
          >
            <Check size={16} /> Approve
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
}
