export interface Message {
  role: 'user' | 'agent';
  content: string;
  timestamp: Date;
}
export interface AgentRequest { session_id: string; message: string; }
export interface AgentResponse { session_id: string; reply: string; }
