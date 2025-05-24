import { 
  RAGQueryRequest, 
  RAGResponse, 
  SessionCreateRequest, 
  SessionResponse, 
  SessionHistoryResponse,
  APIError, // Added
  BackendErrorResponse // Added
} from '../types/api';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api/v1';

async function apiRequest<T>(endpoint: string, options?: RequestInit): Promise<T> {
  const response = await fetch(`${API_BASE_URL}${endpoint}`, {
    headers: {
      'Content-Type': 'application/json',
      ...options?.headers,
    },
    ...options,
  });

  if (!response.ok) {
    let errorMessage = `Request failed with status ${response.status}: ${response.statusText}`;
    let errorType: string | undefined;
    let errorDetails: string | undefined;

    try {
      // Try to parse the error response as JSON
      const errorData: BackendErrorResponse = await response.json();
      if (errorData.error && errorData.error.message) {
        errorMessage = errorData.error.message;
        errorType = errorData.error.type;
        errorDetails = errorData.error.details;
      }
    } catch (e) {
      // Failed to parse backend error JSON, or it's not in the expected format
      // The initial errorMessage is already set with status and statusText
      console.error("Failed to parse backend error JSON or unexpected format:", e);
    }
    throw new APIError(errorMessage, response.status, errorType, errorDetails);
  }

  // Handle cases where response.ok is true, but content might be empty (e.g., 204 No Content for DELETE)
  if (response.status === 204) {
    return Promise.resolve(undefined as T); // Or handle as appropriate for your application
  }
  
  return response.json();
}

export async function askQuestion(request: RAGQueryRequest): Promise<RAGResponse> {
  return apiRequest<RAGResponse>('/ask', {
    method: 'POST',
    body: JSON.stringify(request),
  });
}

export async function createSession(request: SessionCreateRequest = {}): Promise<SessionResponse> {
  return apiRequest<SessionResponse>('/sessions', {
    method: 'POST',
    body: JSON.stringify(request),
  });
}

export async function getSessionHistory(sessionId: string): Promise<SessionHistoryResponse> {
  return apiRequest<SessionHistoryResponse>(`/sessions/${sessionId}/history`);
}

export async function deleteSession(sessionId: string): Promise<void> {
  return apiRequest<void>(`/sessions/${sessionId}`, {
    method: 'DELETE',
  });
}
