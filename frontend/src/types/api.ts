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

// --- Standardized Error Types ---

export interface BackendErrorDetail {
  type: string;
  message: string;
  details?: string;
  timestamp: string; 
}

export interface BackendErrorResponse {
  error: BackendErrorDetail;
}

// Custom Error class for frontend
export class APIError extends Error {
  status: number;
  type?: string;
  details?: string;

  constructor(message: string, status: number, type?: string, details?: string) {
    super(message);
    this.name = 'APIError';
    this.status = status;
    this.type = type;
    this.details = details;
    // Set the prototype explicitly for correct instanceof checks
    Object.setPrototypeOf(this, APIError.prototype);
  }
}
