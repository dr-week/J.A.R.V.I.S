export type ChatRole = 'system' | 'user' | 'assistant';

export interface ChatMessage {
  id: string;
  role: ChatRole;
  text: string;
}

export type NodeStatus = 'idle' | 'active' | 'completed' | 'pending_approval' | 'halted';

export interface DAGNode {
  id: string;
  label: string;
  status: NodeStatus;
  latency?: string;
  error?: string;
}

export interface VelocityUpdate {
  app_id?: string;
  status?: string;
  message?: string;
  step?: string;
  progress?: number;
  nodes?: DAGNode[];
  ttft?: string;
  tps?: string;
  vramUsage?: string;
}

export interface ConfirmRequest {
  request_id: string;
  tool: string;
  params: any;
  risk_level?: 'confirm_once' | 'confirm_always';
  challenge_token?: string;
}
