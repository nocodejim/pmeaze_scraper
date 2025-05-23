export type MessageSender = 'user' | 'ai';

export interface Source {
  title: string;
  section: string;
  url: string;
  relevance: number;
}

export interface ChatMessage {
  id: string;
  content: string;
  sender: MessageSender;
  timestamp: Date;
  confidence?: number;
  sources?: Source[];
}

export interface Session {
  id: string;
  name?: string;
  created_at: Date;
  updated_at: Date;
}
