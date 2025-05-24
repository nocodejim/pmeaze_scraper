import React from 'react';
import { ChatMessage } from '../types/chat';
import { formatTimestamp } from '../utils/dateUtils'; // Import the utility

interface MessageBubbleProps {
  message: ChatMessage;
}

const MessageBubble: React.FC<MessageBubbleProps> = ({ message }) => {
  const isUser = message.sender === 'user';

  if (message.isLoading) {
    return (
      <div className="flex justify-start mb-4">
        <div className="max-w-[70%] p-4 rounded-lg bg-gray-100 text-gray-800 rounded-bl-none">
          <div className="text-sm italic">Assistant is thinking...</div>
        </div>
      </div>
    );
  }

  return (
    <div className={`flex flex-col ${isUser ? 'items-end' : 'items-start'} mb-2`}>
      <div
        className={`max-w-[70%] p-3 rounded-lg shadow-sm ${
          isUser
            ? 'bg-blue-500 text-white rounded-br-none'
            : 'bg-gray-100 text-gray-800 rounded-bl-none'
        }`}
      >
        <div className="text-sm whitespace-pre-wrap">{message.content}</div>
        
        {/* Show sources for AI messages */}
        {!isUser && message.sources && message.sources.length > 0 && (
          <div className="mt-3 pt-3 border-t border-gray-200">
            <div className="text-xs text-gray-600 mb-2">Sources:</div>
            {message.sources.map((source, index) => (
              <div key={index} className="text-xs mb-1">
                <a
                  href={source.url}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="text-blue-600 hover:text-blue-800 underline"
                >
                  {source.title} - {source.section}
                </a>
                <span className="text-gray-500 ml-2">({source.relevance.toFixed(3)})</span>
              </div>
            ))}
          </div>
        )}
        
        {/* Show confidence for AI messages */}
        {!isUser && message.confidence !== undefined && (
          <div className="text-xs text-gray-500 mt-2">
            Confidence: {(message.confidence * 100).toFixed(1)}%
          </div>
        )}
      </div>
      <div className={`text-xs text-gray-500 mt-1 px-1 ${isUser ? 'text-right' : 'text-left'}`}>
        {formatTimestamp(message.timestamp)}
      </div>
    </div>
  );
};

export default MessageBubble;
