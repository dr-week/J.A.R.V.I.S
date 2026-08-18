import React, { useState } from 'react';
import { FolderTree, Code2, GitCommit, FileText, X, Check } from 'lucide-react';

export interface WorkspaceDrawerProps {
  isOpen: boolean;
  onClose: () => void;
  treeData?: string;
  astOutline?: { classes: string[]; functions: string[] } | null;
  pendingDiff?: {
    filePath: string;
    search: string;
    replace: string;
  } | null;
  onApproveDiff?: () => void;
  onRejectDiff?: () => void;
  onSelectNode?: (name: string) => void;
}

export const WorkspaceDrawer: React.FC<WorkspaceDrawerProps> = ({
  isOpen,
  onClose,
  treeData = '',
  astOutline,
  pendingDiff,
  onApproveDiff,
  onRejectDiff,
  onSelectNode,
}) => {
  const [activeTab, setActiveTab] = useState<'tree' | 'outline' | 'diff'>(pendingDiff ? 'diff' : 'tree');

  if (!isOpen) return null;

  return (
    <div className="fixed inset-y-0 right-0 z-50 flex w-80 sm:w-96 flex-col border-l border-white/10 bg-[#0a0a0c]/95 p-4 font-sans backdrop-blur-2xl shadow-2xl transition-all duration-300 animate-slide-left">
      
      {/* Drawer Header */}
      <div className="flex items-center justify-between border-b border-white/10 pb-3">
        <div className="flex items-center gap-2">
          <Code2 className="h-5 w-5 text-cyan-400" />
          <span className="font-mono text-xs sm:text-sm font-bold tracking-wider text-white">WORKSPACE BENCH</span>
        </div>
        <button 
          onClick={onClose}
          className="rounded-lg p-1 text-white/50 hover:bg-white/10 hover:text-white transition"
          aria-label="Close workspace bench"
        >
          <X className="h-5 w-5" />
        </button>
      </div>

      {/* Navigation Tabs */}
      <div className="my-3 flex rounded-xl border border-white/5 bg-black/40 p-1">
        <button
          onClick={() => setActiveTab('tree')}
          className={`flex flex-1 items-center justify-center gap-1.5 rounded-lg py-1.5 font-mono text-xs transition-all ${
            activeTab === 'tree' ? 'bg-cyan-500/20 text-cyan-400 border border-cyan-500/30' : 'text-white/50 hover:text-white'
          }`}
        >
          <FolderTree className="h-3.5 w-3.5" />
          Tree
        </button>
        <button
          onClick={() => setActiveTab('outline')}
          className={`flex flex-1 items-center justify-center gap-1.5 rounded-lg py-1.5 font-mono text-xs transition-all ${
            activeTab === 'outline' ? 'bg-cyan-500/20 text-cyan-400 border border-cyan-500/30' : 'text-white/50 hover:text-white'
          }`}
        >
          <FileText className="h-3.5 w-3.5" />
          AST
        </button>
        <button
          onClick={() => setActiveTab('diff')}
          className={`flex flex-1 items-center justify-center gap-1.5 rounded-lg py-1.5 font-mono text-xs transition-all ${
            activeTab === 'diff' ? 'bg-amber-500/20 text-amber-400 border border-amber-500/30' : 'text-white/50 hover:text-white'
          }`}
        >
          <GitCommit className="h-3.5 w-3.5" />
          Diff
        </button>
      </div>

      {/* Tab Content Area */}
      <div className="flex-1 overflow-y-auto rounded-xl border border-white/5 bg-black/20 p-3 font-mono text-xs">
        
        {/* Tab 1: Tree View */}
        {activeTab === 'tree' && (
          <pre className="whitespace-pre text-white/70 leading-relaxed font-mono text-[11px] select-text">
            {treeData || "// No workspace tree loaded\n// Run workspace_map_tree or trigger Cmd+B"}
          </pre>
        )}

        {/* Tab 2: AST Outline View */}
        {activeTab === 'outline' && (
          <div className="space-y-4">
            <div>
              <h4 className="text-[10px] uppercase tracking-wider text-cyan-400 font-bold mb-2">Classes</h4>
              {astOutline?.classes?.length ? (
                astOutline.classes.map((cls, i) => (
                  <button 
                    key={i} 
                    onClick={() => onSelectNode && onSelectNode(cls)}
                    className="w-full text-left text-white/80 py-1 px-1.5 rounded hover:bg-white/5 hover:text-cyan-300 transition block truncate"
                  >
                    • {cls}
                  </button>
                ))
              ) : (
                <span className="text-white/40 italic">No classes found in active file</span>
              )}
            </div>
            <div>
              <h4 className="text-[10px] uppercase tracking-wider text-cyan-400 font-bold mb-2">Functions</h4>
              {astOutline?.functions?.length ? (
                astOutline.functions.map((fn, i) => (
                  <button 
                    key={i} 
                    onClick={() => onSelectNode && onSelectNode(fn)}
                    className="w-full text-left text-white/80 py-1 px-1.5 rounded hover:bg-white/5 hover:text-cyan-300 transition block truncate"
                  >
                    • {fn}
                  </button>
                ))
              ) : (
                <span className="text-white/40 italic">No functions found in active file</span>
              )}
            </div>
          </div>
        )}

        {/* Tab 3: Diff Inspector (Red/Green Preview) */}
        {activeTab === 'diff' && (
          <div className="space-y-3">
            {pendingDiff ? (
              <>
                <div className="text-[10px] text-white/50 truncate font-mono">File: {pendingDiff.filePath}</div>
                
                {/* Search Block (Red Deletion) */}
                <div className="rounded-lg border border-red-500/30 bg-red-500/10 p-2.5">
                  <span className="text-[9px] uppercase tracking-wider text-red-400 font-bold mb-1 block">- Search Target (Old)</span>
                  <pre className="whitespace-pre-wrap text-red-300 text-[11px]">{pendingDiff.search}</pre>
                </div>

                {/* Replace Block (Green Addition) */}
                <div className="rounded-lg border border-emerald-500/30 bg-emerald-500/10 p-2.5">
                  <span className="text-[9px] uppercase tracking-wider text-emerald-400 font-bold mb-1 block">+ Proposed Replace (New)</span>
                  <pre className="whitespace-pre-wrap text-emerald-300 text-[11px]">{pendingDiff.replace}</pre>
                </div>

                {/* Approval Action Buttons */}
                <div className="flex gap-2 pt-2">
                  <button 
                    onClick={onApproveDiff}
                    className="flex flex-1 items-center justify-center gap-1 rounded-lg bg-emerald-500/20 border border-emerald-500/40 py-2 text-emerald-400 font-bold hover:bg-emerald-500/30 transition-all"
                  >
                    <Check className="h-4 w-4" /> Approve
                  </button>
                  <button 
                    onClick={onRejectDiff}
                    className="flex flex-1 items-center justify-center gap-1 rounded-lg bg-red-500/20 border border-red-500/40 py-2 text-red-400 font-bold hover:bg-red-500/30 transition-all"
                  >
                    <X className="h-4 w-4" /> Reject
                  </button>
                </div>
              </>
            ) : (
              <div className="flex h-48 flex-col items-center justify-center text-center text-white/40">
                <GitCommit className="h-8 w-8 mb-2 opacity-30" />
                <span>No active file mutation pending approval</span>
              </div>
            )}
          </div>
        )}

      </div>
    </div>
  );
};
export default WorkspaceDrawer;
