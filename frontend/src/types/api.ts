export interface SourceDocument {
  title: string;
  section: string;
  url: string;
  relevance: number;
}

export interface RAGQueryRequest {
  question: string;
  session_id?: string;
  top_k?: number;
}

export interface RAGResponse {
  answer: string;
  confidence: number;
  sources: SourceDocument[];
  response_time: number;
  session_id?: string;
}

export interface SessionCreateRequest {
  name?: string;
}

export interface SessionResponse {
  id: string;
  name?: string;
  created_at: string;
  updated_at: string;
}

export interface MessageBase {
  id: string;
  type: string;
  content: string;
  created_at: string;
  metadata?: any;
}

export interface SessionHistoryResponse {
  session_id: string;
  messages: MessageBase[];
}
