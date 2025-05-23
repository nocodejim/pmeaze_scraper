import React, { useState, useEffect } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { ChatMessage, MessageSender, Source } from '../types/chat';
import * as api from '../services/api';
import ChatInput from './ChatInput';
import MessageList from './MessageList';
import { RAGQueryRequest } from '../types/api';

const welcomeMessage: ChatMessage = {
  id: 'welcome_msg',
  content: 'Hello! I am your QuickBuild documentation assistant. Ask me anything about QuickBuild configuration, features, or usage.',
  sender: 'ai' as MessageSender,
  timestamp: new Date(),
};

const ChatWindow: React.FC = () => {
  const [messages, setMessages] = useState<ChatMessage[]>([welcomeMessage]);
  const [sessionId, setSessionId] = useState<string | null>(null);
  const queryClient = useQueryClient();

  // Load session from localStorage on mount
  useEffect(() => {
    const savedSessionId = localStorage.getItem('chat_session_id');
    if (savedSessionId) {
      setSessionId(savedSessionId);
    }
  }, []);

  // Load chat history when session ID is available
  const { data: historyData } = useQuery({
    queryKey: ['session-history', sessionId],
    queryFn: () => api.getSessionHistory(sessionId!),
    enabled: !!sessionId,
  });

  // Update messages when history loads
  useEffect(() => {
    if (historyData?.messages && historyData.messages.length > 0) {
      const chatMessages: ChatMessage[] = historyData.messages.map(msg => ({
        id: msg.id,
        content: msg.content,
        sender: msg.type === 'question' ? 'user' : 'ai',
        timestamp: new Date(msg.created_at),
        ...(msg.metadata && {
          confidence: msg.metadata.confidence,
          sources: msg.metadata.sources
        })
      }));
      setMessages([welcomeMessage, ...chatMessages]);
    }
  }, [historyData]);

  // Create session mutation
  const createSessionMutation = useMutation({
    mutationFn: api.createSession,
    onSuccess: (response) => {
      setSessionId(response.id);
      localStorage.setItem('chat_session_id', response.id);
    }
  });

  // Ask question mutation
  const askQuestionMutation = useMutation({
    mutationFn: (variables: RAGQueryRequest) => api.askQuestion(variables),
    onSuccess: (response, variables) => {
      // Add AI response message
      const aiMessage: ChatMessage = {
        id: `ai_${Date.now()}`,
        content: response.answer,
        sender: 'ai',
        timestamp: new Date(),
        confidence: response.confidence,
        sources: response.sources
      };
      
      setMessages(prev => [...prev, aiMessage]);
      
      // Invalidate session history to refresh
      if (sessionId) {
        queryClient.invalidateQueries({ queryKey: ['session-history', sessionId] });
      }
    },
    onError: (error) => {
      console.error('Error asking question:', error);
      const errorMessage: ChatMessage = {
        id: `error_${Date.now()}`,
        content: 'Sorry, I encountered an error processing your question. Please try again.',
        sender: 'ai',
        timestamp: new Date(),
      };
      setMessages(prev => [...prev, errorMessage]);
    }
  });

  const handleSendMessage = (content: string) => {
    // Add user message immediately (optimistic update)
    const userMessage: ChatMessage = {
      id: `user_${Date.now()}`,
      content,
      sender: 'user',
      timestamp: new Date(),
    };
    
    setMessages(prev => [...prev, userMessage]);

    // Create session if none exists
    if (!sessionId) {
      createSessionMutation.mutate({}, {
        onSuccess: (response) => {
          askQuestionMutation.mutate({
            question: content,
            session_id: response.id,
            top_k: 3
          });
        }
      });
    } else {
      // Ask question with existing session
      askQuestionMutation.mutate({
        question: content,
        session_id: sessionId,
        top_k: 3
      });
    }
  };

  return (
    <div className="flex flex-col h-screen bg-gray-50">
      <div className="bg-white shadow-sm border-b p-4">
        <h1 className="text-xl font-semibold text-gray-800">QuickBuild Assistant</h1>
      </div>
      
      <MessageList messages={messages} />
      
      <ChatInput 
        onSendMessage={handleSendMessage} 
        disabled={askQuestionMutation.isPending || createSessionMutation.isPending}
      />
    </div>
  );
};

export default ChatWindow;
