export type ChatRole = 'system' | 'user' | 'assistant';

export interface ChatMessage {
  id: string;
  role: ChatRole;
  text: string;
}

export interface VelocityUpdate {
  app_id?: string;
  status?: string;
  message?: string;
  step?: string;
  progress?: number;
}

export interface ConfirmRequest {
  request_id: string;
  tool: string;
  params: any;
}
