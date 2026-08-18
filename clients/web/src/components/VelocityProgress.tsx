import React from 'react';
import { 
  Network, 
  FileCheck, 
  ShieldAlert, 
  Terminal, 
  Database, 
  Activity, 
  Cpu, 
  HardDrive 
} from 'lucide-react';
import type { DAGNode, NodeStatus, VelocityUpdate } from '../types/chat';

export interface VelocityProgressProps {
  update?: VelocityUpdate;
  nodes?: DAGNode[];
  ttft?: string;
  tps?: string;
  vramUsage?: string;
}

const DEFAULT_NODES: DAGNode[] = [
  { id: 'router', label: 'Intent Router', status: 'completed', latency: '0.4ms' },
  { id: 'validator', label: 'Pydantic Gate', status: 'completed', latency: '1.2ms' },
  { id: 'risk_gate', label: 'Risk Barrier', status: 'active', latency: '0.8ms' },
  { id: 'executor', label: 'Subprocess Exec', status: 'idle' },
  { id: 'memory', label: 'SoulMem Sync', status: 'idle' }
];

export const VelocityProgress: React.FC<VelocityProgressProps> = ({ 
  update,
  nodes = update?.nodes || DEFAULT_NODES, 
  ttft = update?.ttft || '42ms', 
  tps = update?.tps || '38.4 tok/s', 
  vramUsage = update?.vramUsage || '2.20 GB' 
}) => {
  const iconMap: Record<string, React.ReactNode> = {
    'router': <Network className="h-4 w-4" />,
    'validator': <FileCheck className="h-4 w-4" />,
    'risk_gate': <ShieldAlert className="h-4 w-4" />,
    'executor': <Terminal className="h-4 w-4" />,
    'memory': <Database className="h-4 w-4" />
  };

  const getStatusStyles = (status: NodeStatus) => {
    switch (status) {
      case 'active':
        return 'border-cyan-500/50 bg-cyan-500/10 text-cyan-400 shadow-[0_0_15px_rgba(6,182,212,0.4)] animate-pulse transform-gpu';
      case 'completed':
        return 'border-emerald-500/30 bg-emerald-500/10 text-emerald-400';
      case 'pending_approval':
        return 'border-amber-500/50 bg-amber-500/10 text-amber-400 shadow-[0_0_15px_rgba(245,158,11,0.4)]';
      case 'halted':
        return 'border-red-500/50 bg-red-500/10 text-red-400 shadow-[0_0_15px_rgba(239,68,68,0.4)]';
      default:
        return 'border-white/10 bg-white/5 text-white/40';
    }
  };

  return (
    <div className="relative w-full overflow-hidden rounded-[24px_12px_24px_12px/12px_24px_12px_24px] border border-white/10 bg-[#0a0a0c]/80 p-5 sm:p-6 font-sans backdrop-blur-2xl shadow-[inset_0_1px_1px_rgba(255,255,255,0.2)] mb-4">
      
      {/* Liquid Glass Analog Grain Overlay */}
      <svg className="pointer-events-none absolute inset-0 z-0 h-full w-full opacity-15 mix-blend-overlay">
        <filter id="dag-grain">
          <feTurbulence type="fractalNoise" baseFrequency="0.75" numOctaves="3" stitchTiles="stitch" />
          <feColorMatrix type="saturate" values="0" />
        </filter>
        <rect width="100%" height="100%" filter="url(#dag-grain)" />
      </svg>

      {/* Header: Hardware & Orchestrator Metrics */}
      <div className="relative z-10 mb-6 flex flex-wrap items-center justify-between gap-3 rounded-xl border border-white/5 bg-black/40 p-3 sm:p-4">
        <div className="flex gap-4 sm:gap-6">
          <div className="flex items-center gap-2">
            <Activity className="h-4 w-4 text-white/50" />
            <div className="flex flex-col">
              <span className="font-mono text-[10px] uppercase tracking-wider text-white/40">TTFT</span>
              <span className="font-mono text-xs font-medium text-white/80">{ttft}</span>
            </div>
          </div>
          <div className="flex items-center gap-2">
            <Cpu className="h-4 w-4 text-cyan-500/70" />
            <div className="flex flex-col">
              <span className="font-mono text-[10px] uppercase tracking-wider text-white/40">Throughput</span>
              <span className="font-mono text-xs font-medium text-white/80">{tps}</span>
            </div>
          </div>
        </div>
        
        <div className="flex items-center gap-2 rounded-lg border border-white/10 bg-white/5 px-3 py-1.5">
          <HardDrive className="h-4 w-4 text-emerald-400" />
          <div className="flex flex-col text-right">
            <span className="font-mono text-[10px] uppercase tracking-wider text-white/40">GTX 1050 Ti VRAM</span>
            <span className="font-mono text-xs font-bold text-emerald-400">{vramUsage} / 4.00 GB</span>
          </div>
        </div>
      </div>

      {/* Execution DAG Timeline */}
      <div className="relative z-10 flex w-full items-start justify-between overflow-x-auto pb-4 pt-1">
        {/* Ambient background connecting line */}
        <div className="absolute left-0 top-5 -z-10 h-px w-full bg-white/5" />

        {nodes.map((node, index) => {
          const isLast = index === nodes.length - 1;
          
          return (
            <div key={node.id} className="relative flex flex-col items-center min-w-[70px] px-1">
              
              {/* Active Connector Highlight */}
              {!isLast && (node.status === 'completed' || node.status === 'active') && (
                <div className="absolute left-1/2 top-5 -z-10 h-px w-[200%] bg-gradient-to-r from-cyan-500/50 to-transparent" />
              )}

              {/* Node Icon Circle */}
              <div 
                className={`flex h-10 w-10 items-center justify-center rounded-full border border-solid backdrop-blur-md transition-all duration-500 ${getStatusStyles(node.status)}`}
              >
                {iconMap[node.id] || <Activity className="h-4 w-4" />}
              </div>

              {/* Node Label & Metadata */}
              <div className="mt-3 flex flex-col items-center text-center">
                <span className={`font-mono text-[11px] font-semibold tracking-tight ${node.status === 'active' ? 'text-white' : 'text-white/60'}`}>
                  {node.label}
                </span>
                
                {node.latency && (
                  <span className="mt-0.5 font-mono text-[9px] text-white/40">
                    {node.latency}
                  </span>
                )}
                
                {/* Circuit Breaker Error Trace */}
                {node.status === 'halted' && node.error && (
                  <div className="absolute top-16 w-40 rounded-lg border border-red-500/20 bg-red-500/10 p-2 backdrop-blur-xl z-20">
                    <p className="font-mono text-[9px] leading-tight text-red-400">{node.error}</p>
                  </div>
                )}
                
                {/* Pending HITL Challenge */}
                {node.status === 'pending_approval' && (
                  <div className="absolute top-16 flex animate-bounce items-center gap-1 rounded-full border border-amber-500/30 bg-amber-500/10 px-2 py-0.5 z-20">
                    <ShieldAlert className="h-3 w-3 text-amber-400" />
                    <span className="font-mono text-[8px] uppercase tracking-wider text-amber-400">Auth Required</span>
                  </div>
                )}
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
};
export default VelocityProgress;
