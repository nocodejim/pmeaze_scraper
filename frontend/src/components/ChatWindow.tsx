import React, { useState, useEffect } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { ChatMessage, MessageSender, Source } from '../types/chat';
import * as api from '../services/api';
import { APIError } from '../types/api'; // Added APIError
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
  const [chatError, setChatError] = useState<string | null>(null); // Added chatError state
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
      const apiErr = error as APIError;
      setChatError(apiErr.message || 'An unexpected error occurred while fetching the answer.');
      // Optionally, still add a generic error message to the chat list, or rely on ChatInput display
      console.error('Error asking question:', apiErr);
      // If you want to keep the error message in the chat list as well:
      // const errorMessageInChat: ChatMessage = {
      //   id: `error_${Date.now()}`,
      //   content: apiErr.message || 'Sorry, I encountered an error. Please try again.',
      //   sender: 'ai',
      //   timestamp: new Date(),
      // };
      // setMessages(prev => [...prev, errorMessageInChat]);
    },
    onMutate: () => {
      setChatError(null); // Clear previous errors when a new mutation starts
    }
  });

  const handleSendMessage = (content: string) => {
    setChatError(null); // Clear previous errors on new send attempt

    const userMessage: ChatMessage = {
      id: `user_${Date.now()}`,
      content,
      sender: 'user',
      timestamp: new Date(),
    };
    
    setMessages(prev => [...prev, userMessage]);
    
    const loadingMessageId = `ai_loading_${Date.now()}`;
    const aiLoadingMessage: ChatMessage = {
      id: loadingMessageId,
      content: "Assistant is thinking...",
      sender: 'ai',
      timestamp: new Date(),
      isLoading: true,
    };
    setMessages(prev => [...prev, aiLoadingMessage]);

    const mutationPayload = {
      question: content,
      session_id: sessionId, // Will be null if no session, backend handles new session if ID is null/missing
      top_k: 3
    };

    const mutationOptions = {
      onSuccess: (response: api.RAGResponse) => {
        setMessages(prev => prev.filter(msg => msg.id !== loadingMessageId));
        const aiResponseMessage: ChatMessage = {
          id: `ai_${Date.now()}`,
          content: response.answer,
          sender: 'ai',
          timestamp: new Date(),
          confidence: response.confidence,
          sources: response.sources
        };
        setMessages(prev => [...prev, aiResponseMessage]);
        if (response.session_id && !sessionId) {
          setSessionId(response.session_id);
          localStorage.setItem('chat_session_id', response.session_id);
        }
        if (response.session_id || sessionId) {
          queryClient.invalidateQueries({ queryKey: ['session-history', response.session_id || sessionId] });
        }
      },
      onError: (error: Error) => {
        setMessages(prev => prev.filter(msg => msg.id !== loadingMessageId));
        const apiErr = error as APIError;
        setChatError(apiErr.message || 'An unexpected error occurred while fetching the answer.');
        // The existing onError in askQuestionMutation already handles console.error
      }
    };

    if (!sessionId) {
      createSessionMutation.mutate({}, {
        onSuccess: (sessionResponse) => {
          setSessionId(sessionResponse.id);
          localStorage.setItem('chat_session_id', sessionResponse.id);
          askQuestionMutation.mutate({ ...mutationPayload, session_id: sessionResponse.id }, mutationOptions);
        },
        onError: (error) => {
          setMessages(prev => prev.filter(msg => msg.id !== loadingMessageId));
          const apiErr = error as APIError;
          setChatError(apiErr.message || 'Failed to create a session.');
        }
      });
    } else {
      askQuestionMutation.mutate({ ...mutationPayload, session_id: sessionId }, mutationOptions);
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
        error={chatError} // Pass down the error message
      />
    </div>
  );
};

export default ChatWindow;
