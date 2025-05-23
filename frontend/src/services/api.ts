import { RAGQueryRequest, RAGResponse, SessionCreateRequest, SessionResponse, SessionHistoryResponse } from '../types/api';

const API_BASE_URL = 'http://localhost:8000/api/v1';

async function apiRequest<T>(endpoint: string, options?: RequestInit): Promise<T> {
  const response = await fetch(`${API_BASE_URL}${endpoint}`, {
    headers: {
      'Content-Type': 'application/json',
      ...options?.headers,
    },
    ...options,
  });

  if (!response.ok) {
    throw new Error(`API request failed: ${response.statusText}`);
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
