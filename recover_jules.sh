#!/bin/bash

# Jules Recovery Script
# Extracts and recreates project structure from Jules chat output
# Author: Recovery Assistant
# Date: $(date)

set -euo pipefail  # Exit on error, undefined vars, pipe failures

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
LOG_FILE="${SCRIPT_DIR}/recovery.log"
BACKUP_DIR="${SCRIPT_DIR}/backups/$(date +%Y%m%d_%H%M%S)"
DRY_RUN=${DRY_RUN:-false}
DEBUG=${DEBUG:-false}
FORCE=${FORCE:-false}

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Logging functions
log() {
    echo -e "[$(date '+%Y-%m-%d %H:%M:%S')] $1" | tee -a "$LOG_FILE"
}

log_info() {
    log "${BLUE}[INFO]${NC} $1"
}

log_warn() {
    log "${YELLOW}[WARN]${NC} $1"
}

log_error() {
    log "${RED}[ERROR]${NC} $1"
}

log_success() {
    log "${GREEN}[SUCCESS]${NC} $1"
}

debug() {
    if [[ "$DEBUG" == "true" ]]; then
        log "${YELLOW}[DEBUG]${NC} $1"
    fi
}

# Setup logging
setup_logging() {
    mkdir -p "$(dirname "$LOG_FILE")"
    log_info "=== Jules Recovery Script Started ==="
    log_info "Log file: $LOG_FILE"
    log_info "Backup directory: $BACKUP_DIR"
    log_info "Dry run: $DRY_RUN"
    log_info "Debug mode: $DEBUG"
}

# Create backup of existing file
backup_file() {
    local file_path="$1"
    if [[ -f "$file_path" ]]; then
        mkdir -p "$BACKUP_DIR/$(dirname "$file_path")"
        cp "$file_path" "$BACKUP_DIR/$file_path"
        debug "Backed up: $file_path"
    fi
}

# Create directory if it doesn't exist
ensure_directory() {
    local dir_path="$1"
    if [[ ! -d "$dir_path" ]]; then
        if [[ "$DRY_RUN" == "false" ]]; then
            mkdir -p "$dir_path"
            log_info "Created directory: $dir_path"
        else
            log_info "[DRY RUN] Would create directory: $dir_path"
        fi
    else
        debug "Directory exists: $dir_path"
    fi
}

# Write file with content
write_file() {
    local file_path="$1"
    local content="$2"
    local overwrite="${3:-false}"
    
    # Create parent directory
    ensure_directory "$(dirname "$file_path")"
    
    # Check if file exists and handle accordingly
    if [[ -f "$file_path" ]] && [[ "$overwrite" == "false" ]] && [[ "$FORCE" == "false" ]]; then
        log_warn "File exists, skipping: $file_path (use FORCE=true to overwrite)"
        return 0
    fi
    
    # Backup existing file
    if [[ -f "$file_path" ]]; then
        backup_file "$file_path"
    fi
    
    # Write file
    if [[ "$DRY_RUN" == "false" ]]; then
        echo -e "$content" > "$file_path"
        log_success "Created/Updated: $file_path ($(echo -e "$content" | wc -l) lines)"
    else
        log_info "[DRY RUN] Would create: $file_path ($(echo -e "$content" | wc -l) lines)"
    fi
}

# Define all helper functions first, then main functions

create_backend_models() {
    log_info "Creating backend model files..."
    
    # backend/app/models/db_models.py
    write_file "backend/app/models/db_models.py" 'from sqlmodel import SQLModel, Field
from typing import Optional
from datetime import datetime
from enum import Enum
import uuid

class MessageTypeEnum(str, Enum):
    question = "question"
    answer = "answer"

class SessionTable(SQLModel, table=True):
    __tablename__ = "sessions"
    
    id: Optional[str] = Field(default_factory=lambda: str(uuid.uuid4()), primary_key=True)
    name: Optional[str] = None
    user_id: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)

class MessageTable(SQLModel, table=True):
    __tablename__ = "messages"
    
    id: Optional[str] = Field(default_factory=lambda: str(uuid.uuid4()), primary_key=True)
    session_id: str = Field(foreign_key="sessions.id")
    type: MessageTypeEnum
    content: str
    metadata: Optional[str] = None  # JSON string
    created_at: datetime = Field(default_factory=datetime.now)'
    
    # backend/app/models/rag_models.py
    write_file "backend/app/models/rag_models.py" 'from pydantic import BaseModel
from typing import List, Optional

class SourceDocument(BaseModel):
    title: str
    section: str
    url: str
    relevance: float

class RAGQueryRequest(BaseModel):
    question: str
    session_id: Optional[str] = None
    top_k: Optional[int] = 3

class RAGResponse(BaseModel):
    answer: str
    confidence: float
    sources: List[SourceDocument]
    response_time: float
    session_id: Optional[str] = None'
    
    # backend/app/models/session_models.py
    write_file "backend/app/models/session_models.py" 'from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

class SessionCreateRequest(BaseModel):
    name: Optional[str] = None

class SessionResponse(BaseModel):
    id: str
    name: Optional[str]
    created_at: datetime
    updated_at: datetime

class MessageBase(BaseModel):
    id: str
    type: str
    content: str
    created_at: datetime
    metadata: Optional[dict] = None

class SessionHistoryResponse(BaseModel):
    session_id: str
    messages: List[MessageBase]'
    
    # backend/app/models/system_models.py
    write_file "backend/app/models/system_models.py" 'from pydantic import BaseModel
from typing import List, Dict, Any

class HealthResponse(BaseModel):
    status: str
    database: str
    rag_system: Dict[str, Any]

class ExampleQuestion(BaseModel):
    question: str
    category: str

class ExamplesResponse(BaseModel):
    examples: List[ExampleQuestion]'
}

create_backend_routers() {
    log_info "Creating backend router files..."
    
    # backend/app/routers/rag_router.py
    write_file "backend/app/routers/rag_router.py" 'import time
from uuid import UUID
from fastapi import APIRouter, HTTPException, Depends, status
from typing import List
from sqlmodel import Session

from app.models.rag_models import RAGQueryRequest, RAGResponse, SourceDocument
from app.models.db_models import MessageTypeEnum
from app.services.rag_service import RAGService
from app.core.config import settings
from app.db.database import get_session
from app.crud.crud_session import create_message, get_or_create_session

router = APIRouter()

@router.post("/ask", response_model=RAGResponse)
async def ask_question(
    request: RAGQueryRequest,
    db: Session = Depends(get_session)
):
    """Ask a question to the RAG system."""
    start_time = time.time()
    
    try:
        # Initialize RAG service
        rag_service = RAGService()
        
        # Get or create session
        session_id = None
        if request.session_id:
            session = get_or_create_session(db, request.session_id)
            session_id = session.id
        
        # Log user question
        if session_id:
            create_message(
                db=db,
                session_id=session_id,
                message_type=MessageTypeEnum.question,
                content=request.question
            )
        
        # Get answer from RAG system
        rag_result = rag_service.ask_question(request.question, request.top_k or 3)
        
        # Convert sources to response format
        sources = [
            SourceDocument(
                title=source.get("title", "Unknown"),
                section=source.get("section", "Unknown"),
                url=source.get("url", ""),
                relevance=source.get("relevance", 0.0)
            )
            for source in rag_result.get("sources", [])
        ]
        
        response_time = time.time() - start_time
        
        response = RAGResponse(
            answer=rag_result.get("answer", "No answer available"),
            confidence=rag_result.get("confidence", 0.0),
            sources=sources,
            response_time=response_time,
            session_id=session_id
        )
        
        # Log AI response
        if session_id:
            create_message(
                db=db,
                session_id=session_id,
                message_type=MessageTypeEnum.answer,
                content=response.answer,
                metadata={"confidence": response.confidence, "sources": len(sources)}
            )
        
        return response
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error processing question: {str(e)}"
        )'
    
    # backend/app/routers/session_router.py
    write_file "backend/app/routers/session_router.py" 'from fastapi import APIRouter, HTTPException, Depends, status
from sqlmodel import Session
from typing import List

from app.models.session_models import SessionCreateRequest, SessionResponse, SessionHistoryResponse
from app.db.database import get_session
from app.crud.crud_session import create_session, get_session_by_id, delete_session, get_session_history

router = APIRouter()

@router.post("/sessions", response_model=SessionResponse)
async def create_new_session(
    request: SessionCreateRequest,
    db: Session = Depends(get_session)
):
    """Create a new chat session."""
    session = create_session(db, request.name)
    return SessionResponse(
        id=session.id,
        name=session.name,
        created_at=session.created_at,
        updated_at=session.updated_at
    )

@router.get("/sessions/{session_id}/history", response_model=SessionHistoryResponse)
async def get_session_history_endpoint(
    session_id: str,
    db: Session = Depends(get_session)
):
    """Get chat history for a session."""
    history = get_session_history(db, session_id)
    if not history:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Session not found"
        )
    return history

@router.delete("/sessions/{session_id}")
async def delete_session_endpoint(
    session_id: str,
    db: Session = Depends(get_session)
):
    """Delete a chat session and its history."""
    success = delete_session(db, session_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Session not found"
        )
    return {"message": "Session deleted successfully"}'
    
    # backend/app/routers/system_router.py
    write_file "backend/app/routers/system_router.py" 'from fastapi import APIRouter, Depends
from sqlmodel import Session

from app.models.system_models import HealthResponse, ExamplesResponse, ExampleQuestion
from app.services.rag_service import RAGService
from app.db.database import get_session

router = APIRouter()

@router.get("/health", response_model=HealthResponse)
async def health_check(db: Session = Depends(get_session)):
    """Check system health."""
    # Check database
    try:
        # Simple DB query to verify connection
        db.exec("SELECT 1")
        db_status = "healthy"
    except Exception as e:
        db_status = f"unhealthy: {str(e)}"
    
    # Check RAG system
    try:
        rag_service = RAGService()
        rag_health = rag_service.health_check()
    except Exception as e:
        rag_health = {"status": "unhealthy", "error": str(e)}
    
    return HealthResponse(
        status="healthy" if db_status == "healthy" and rag_health["status"] == "healthy" else "unhealthy",
        database=db_status,
        rag_system=rag_health
    )

@router.get("/examples", response_model=ExamplesResponse)
async def get_example_questions():
    """Get example questions for the UI."""
    examples = [
        ExampleQuestion(question="How do I add a step to an existing configuration?", category="Configuration"),
        ExampleQuestion(question="What are the different types of build triggers?", category="Triggers"),
        ExampleQuestion(question="How do I set up email notifications?", category="Notifications"),
        ExampleQuestion(question="What is the difference between build configurations and build steps?", category="Concepts"),
        ExampleQuestion(question="How do I configure a build badge?", category="Configuration"),
        ExampleQuestion(question="What are the key features of the QuickBuild dashboard?", category="UI"),
    ]
    
    return ExamplesResponse(examples=examples)'
}

create_backend_crud() {
    log_info "Creating backend CRUD files..."
    
    # backend/app/crud/crud_session.py
    write_file "backend/app/crud/crud_session.py" 'from sqlmodel import Session, select
from typing import Optional
import json
from datetime import datetime

from app.models.db_models import SessionTable, MessageTable, MessageTypeEnum
from app.models.session_models import SessionHistoryResponse, MessageBase

def create_session(db: Session, name: Optional[str] = None) -> SessionTable:
    """Create a new session."""
    session = SessionTable(name=name)
    db.add(session)
    db.commit()
    db.refresh(session)
    return session

def get_session_by_id(db: Session, session_id: str) -> Optional[SessionTable]:
    """Get session by ID."""
    statement = select(SessionTable).where(SessionTable.id == session_id)
    return db.exec(statement).first()

def get_or_create_session(db: Session, session_id: str) -> SessionTable:
    """Get existing session or create new one if not found."""
    session = get_session_by_id(db, session_id)
    if not session:
        session = create_session(db)
    return session

def delete_session(db: Session, session_id: str) -> bool:
    """Delete session and all its messages."""
    session = get_session_by_id(db, session_id)
    if not session:
        return False
    
    # Delete messages first
    statement = select(MessageTable).where(MessageTable.session_id == session_id)
    messages = db.exec(statement).all()
    for message in messages:
        db.delete(message)
    
    # Delete session
    db.delete(session)
    db.commit()
    return True

def create_message(
    db: Session, 
    session_id: str, 
    message_type: MessageTypeEnum, 
    content: str,
    metadata: Optional[dict] = None
) -> MessageTable:
    """Create a new message in a session."""
    message = MessageTable(
        session_id=session_id,
        type=message_type,
        content=content,
        metadata=json.dumps(metadata) if metadata else None
    )
    db.add(message)
    db.commit()
    db.refresh(message)
    return message

def get_session_history(db: Session, session_id: str) -> Optional[SessionHistoryResponse]:
    """Get all messages for a session."""
    session = get_session_by_id(db, session_id)
    if not session:
        return None
    
    statement = select(MessageTable).where(MessageTable.session_id == session_id).order_by(MessageTable.created_at)
    messages = db.exec(statement).all()
    
    message_list = []
    for msg in messages:
        metadata = json.loads(msg.metadata) if msg.metadata else None
        message_list.append(MessageBase(
            id=msg.id,
            type=msg.type.value,
            content=msg.content,
            created_at=msg.created_at,
            metadata=metadata
        ))
    
    return SessionHistoryResponse(
        session_id=session_id,
        messages=message_list
    )'
}

create_backend_db() {
    log_info "Creating backend database files..."
    
    # backend/app/db/database.py
    write_file "backend/app/db/database.py" 'from sqlmodel import create_engine, Session, SQLModel
from app.core.config import settings

DATABASE_URL = "sqlite:///./quickbuild_rag.db"  # Will create DB file in project root

engine = create_engine(DATABASE_URL, echo=True, connect_args={"check_same_thread": False})

def create_db_and_tables():
    SQLModel.metadata.create_all(engine)

def get_session():
    with Session(engine) as session:
        yield session'
}

create_frontend_components() {
    log_info "Creating frontend component files..."
    
    ensure_directory "frontend/src/components"
    
    # ChatInput component
    write_file "frontend/src/components/ChatInput.tsx" 'import React, { useState, KeyboardEvent } from '\''react'\'';

interface ChatInputProps {
  onSendMessage: (message: string) => void;
  disabled?: boolean;
}

const ChatInput: React.FC<ChatInputProps> = ({ onSendMessage, disabled = false }) => {
  const [message, setMessage] = useState('\''\'');

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (message.trim() && !disabled) {
      onSendMessage(message.trim());
      setMessage('\''\'');
    }
  };

  const handleKeyDown = (e: KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === '\''Enter'\'' && !e.shiftKey) {
      e.preventDefault();
      handleSubmit(e);
    }
  };

  return (
    <form onSubmit={handleSubmit} className="border-t bg-white p-4">
      <div className="flex space-x-4">
        <textarea
          value={message}
          onChange={(e) => setMessage(e.target.value)}
          onKeyDown={handleKeyDown}
          placeholder="Ask a question about QuickBuild..."
          className="flex-1 resize-none border border-gray-300 rounded-lg p-3 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
          rows={3}
          disabled={disabled}
        />
        <button
          type="submit"
          disabled={!message.trim() || disabled}
          className="px-6 py-2 bg-blue-500 text-white rounded-lg hover:bg-blue-600 disabled:bg-gray-400 disabled:cursor-not-allowed"
        >
          Send
        </button>
      </div>
    </form>
  );
};

export default ChatInput;'
    
    # MessageBubble component
    write_file "frontend/src/components/MessageBubble.tsx" 'import React from '\''react'\'';
import { ChatMessage } from '\''../types/chat'\'';

interface MessageBubbleProps {
  message: ChatMessage;
}

const MessageBubble: React.FC<MessageBubbleProps> = ({ message }) => {
  const isUser = message.sender === '\''user'\'';
  
  return (
    <div className={`flex ${isUser ? '\''justify-end'\'' : '\''justify-start'\''} mb-4`}>
      <div
        className={`max-w-[70%] p-4 rounded-lg ${
          isUser
            ? '\''bg-blue-500 text-white rounded-br-none'\''
            : '\''bg-gray-100 text-gray-800 rounded-bl-none'\''
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
    </div>
  );
};

export default MessageBubble;'
    
    # MessageList component  
    write_file "frontend/src/components/MessageList.tsx" 'import React, { useEffect, useRef } from '\''react'\'';
import { ChatMessage } from '\''../types/chat'\'';
import MessageBubble from '\''./MessageBubble'\'';

interface MessageListProps {
  messages: ChatMessage[];
}

const MessageList: React.FC<MessageListProps> = ({ messages }) => {
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: '\''smooth'\'' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  return (
    <div className="flex-1 overflow-y-auto p-4 space-y-4">
      {messages.map((message) => (
        <MessageBubble key={message.id} message={message} />
      ))}
      <div ref={messagesEndRef} />
    </div>
  );
};

export default MessageList;'
    
    # ChatWindow component
    write_file "frontend/src/components/ChatWindow.tsx" 'import React, { useState, useEffect } from '\''react'\'';
import { useQuery, useMutation, useQueryClient } from '\''@tanstack/react-query'\'';
import { ChatMessage, MessageSender, Source } from '\''../types/chat'\'';
import * as api from '\''../services/api'\'';
import ChatInput from '\''./ChatInput'\'';
import MessageList from '\''./MessageList'\'';
import { RAGQueryRequest } from '\''../types/api'\'';

const welcomeMessage: ChatMessage = {
  id: '\''welcome_msg'\'',
  content: '\''Hello! I am your QuickBuild documentation assistant. Ask me anything about QuickBuild configuration, features, or usage.'\'',
  sender: '\''ai'\'' as MessageSender,
  timestamp: new Date(),
};

const ChatWindow: React.FC = () => {
  const [messages, setMessages] = useState<ChatMessage[]>([welcomeMessage]);
  const [sessionId, setSessionId] = useState<string | null>(null);
  const queryClient = useQueryClient();

  // Load session from localStorage on mount
  useEffect(() => {
    const savedSessionId = localStorage.getItem('\''chat_session_id'\'');
    if (savedSessionId) {
      setSessionId(savedSessionId);
    }
  }, []);

  // Load chat history when session ID is available
  const { data: historyData } = useQuery({
    queryKey: ['\''session-history'\'', sessionId],
    queryFn: () => api.getSessionHistory(sessionId!),
    enabled: !!sessionId,
  });

  // Update messages when history loads
  useEffect(() => {
    if (historyData?.messages && historyData.messages.length > 0) {
      const chatMessages: ChatMessage[] = historyData.messages.map(msg => ({
        id: msg.id,
        content: msg.content,
        sender: msg.type === '\''question'\'' ? '\''user'\'' : '\''ai'\'',
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
      localStorage.setItem('\''chat_session_id'\'', response.id);
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
        sender: '\''ai'\'',
        timestamp: new Date(),
        confidence: response.confidence,
        sources: response.sources
      };
      
      setMessages(prev => [...prev, aiMessage]);
      
      // Invalidate session history to refresh
      if (sessionId) {
        queryClient.invalidateQueries({ queryKey: ['\''session-history'\'', sessionId] });
      }
    },
    onError: (error) => {
      console.error('\''Error asking question:'\'', error);
      const errorMessage: ChatMessage = {
        id: `error_${Date.now()}`,
        content: '\''Sorry, I encountered an error processing your question. Please try again.'\'',
        sender: '\''ai'\'',
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
      sender: '\''user'\'',
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

export default ChatWindow;'
}

create_frontend_config() {
    log_info "Creating frontend config files..."
    
    # vite.config.ts
    write_file "frontend/vite.config.ts" 'import { defineConfig } from '\''vite'\''
import react from '\''@vitejs/plugin-react'\''

// https://vite.dev/config/
export default defineConfig({
  plugins: [react()],
})'
    
    # tailwind.config.js
    write_file "frontend/tailwind.config.js" '/** @type {import('\''tailwindcss'\'').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {},
  },
  plugins: [],
}'
    
    # postcss.config.js
    write_file "frontend/postcss.config.js" 'export default {
  plugins: {
    tailwindcss: {},
    autoprefixer: {},
  },
}'
    
    # package.json
    write_file "frontend/package.json" '{
  "name": "quickbuild-rag-frontend",
  "private": true,
  "version": "0.0.0",
  "type": "module",
  "scripts": {
    "dev": "vite",
    "build": "tsc -b && vite build",
    "lint": "eslint .",
    "preview": "vite preview"
  },
  "dependencies": {
    "@tanstack/react-query": "^5.76.2",
    "@tanstack/react-query-devtools": "^5.76.2",
    "react": "^19.1.0",
    "react-dom": "^19.1.0"
  },
  "devDependencies": {
    "@eslint/js": "^9.25.0",
    "@types/react": "^19.1.2",
    "@types/react-dom": "^19.1.2",
    "@vitejs/plugin-react": "^4.4.1",
    "autoprefixer": "^10.4.20",
    "eslint": "^9.17.0",
    "eslint-plugin-react-hooks": "^5.0.0",
    "eslint-plugin-react-refresh": "^0.4.16",
    "globals": "^15.14.0",
    "postcss": "^8.5.1",
    "tailwindcss": "^3.4.17",
    "typescript": "~5.6.2",
    "typescript-eslint": "^8.18.2",
    "vite": "^6.0.5"
  }
}'

    # index.html
    write_file "frontend/index.html" '<!doctype html>
<html lang="en">
  <head>
    <meta charset="UTF-8" />
    <link rel="icon" type="image/svg+xml" href="/vite.svg" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <title>QuickBuild RAG Assistant</title>
  </head>
  <body>
    <div id="root"></div>
    <script type="module" src="/src/main.tsx"></script>
  </body>
</html>'

    # .gitignore
    write_file "frontend/.gitignore" '# Logs
logs
*.log
npm-debug.log*
yarn-debug.log*
yarn-error.log*
pnpm-debug.log*
lerna-debug.log*

node_modules
dist
dist-ssr
*.local

# Editor directories and files
.vscode/*
!.vscode/extensions.json
.idea
.DS_Store
*.suo
*.ntvs*
*.njsproj
*.sln
*.sw?'
}

create_frontend_types_and_services() {
    log_info "Creating frontend types and services..."
    
    ensure_directory "frontend/src/types"
    ensure_directory "frontend/src/services"
    ensure_directory "frontend/src/utils"
    
    # types/chat.ts
    write_file "frontend/src/types/chat.ts" 'export type MessageSender = '\''user'\'' | '\''ai'\'';

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
}'
    
    # types/api.ts
    write_file "frontend/src/types/api.ts" 'export interface SourceDocument {
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
}'
    
    # services/api.ts
    write_file "frontend/src/services/api.ts" 'import { RAGQueryRequest, RAGResponse, SessionCreateRequest, SessionResponse, SessionHistoryResponse } from '\''../types/api'\'';

const API_BASE_URL = '\''http://localhost:8000/api/v1'\'';

async function apiRequest<T>(endpoint: string, options?: RequestInit): Promise<T> {
  const response = await fetch(`${API_BASE_URL}${endpoint}`, {
    headers: {
      '\''Content-Type'\'': '\''application/json'\'',
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
  return apiRequest<RAGResponse>('\''/ask'\'', {
    method: '\''POST'\'',
    body: JSON.stringify(request),
  });
}

export async function createSession(request: SessionCreateRequest = {}): Promise<SessionResponse> {
  return apiRequest<SessionResponse>('\''/sessions'\'', {
    method: '\''POST'\'',
    body: JSON.stringify(request),
  });
}

export async function getSessionHistory(sessionId: string): Promise<SessionHistoryResponse> {
  return apiRequest<SessionHistoryResponse>(`/sessions/${sessionId}/history`);
}

export async function deleteSession(sessionId: string): Promise<void> {
  return apiRequest<void>(`/sessions/${sessionId}`, {
    method: '\''DELETE'\'',
  });
}'
    
    # Main app files
    write_file "frontend/src/main.tsx" 'import { StrictMode } from '\''react'\'';
import { createRoot } from '\''react-dom/client'\'';
import { QueryClient, QueryClientProvider } from '\''@tanstack/react-query'\'';
import { ReactQueryDevtools } from '\''@tanstack/react-query-devtools'\'';
import '\''./index.css'\'';
import App from '\''./App.tsx'\'';

const queryClient = new QueryClient();

createRoot(document.getElementById('\''root'\'')!).render(
  <StrictMode>
    <QueryClientProvider client={queryClient}>
      <App />
      <ReactQueryDevtools initialIsOpen={false} />
    </QueryClientProvider>
  </StrictMode>,
);'
    
    write_file "frontend/src/App.tsx" 'import React from '\''react'\'';
import ChatWindow from '\''./components/ChatWindow'\'';
import '\''./App.css'\'';

function App() {
  return (
    <div className="App">
      <ChatWindow />
    </div>
  );
}

export default App;'
    
    write_file "frontend/src/App.css" '#root {
  max-width: 1280px;
  margin: 0 auto;
  padding: 2rem;
  text-align: center;
}'
    
    write_file "frontend/src/index.css" '@tailwind base;
@tailwind components;
@tailwind utilities;'
    
    write_file "frontend/src/vite-env.d.ts" '/// <reference types="vite/client" />'
}

# Create all backend files
create_backend_files() {
    log_info "Creating backend files..."
    
    # Create directory structure
    ensure_directory "backend/app/core"
    ensure_directory "backend/app/models"
    ensure_directory "backend/app/routers"
    ensure_directory "backend/app/services"
    ensure_directory "backend/app/crud"
    ensure_directory "backend/app/db"
    ensure_directory "backend/app/dependencies"
    ensure_directory "backend/tests"
    
    # Basic __init__.py files
    write_file "backend/app/__init__.py" ""
    write_file "backend/app/core/__init__.py" ""
    write_file "backend/app/dependencies/__init__.py" ""
    write_file "backend/tests/__init__.py" ""
    
    # Core config
    write_file "backend/app/core/config.py" 'from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    PROJECT_NAME: str = "QuickBuild RAG API"
    API_V1_STR: str = "/api/v1"
    RAG_JSON_PATH: str = "scraper/output/all_content.json"  # Default path

    class Config:
        env_file = ".env"  # Optional: if you use a .env file for local development

settings = Settings()'
    
    # Main FastAPI app
    write_file "backend/app/main.py" 'from fastapi import FastAPI, HTTPException
from starlette.responses import JSONResponse
from contextlib import asynccontextmanager

from app.routers import rag_router, session_router, system_router
from app.core.config import settings
from app.db.database import create_db_and_tables

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    create_db_and_tables()
    yield
    # Shutdown (if needed)

app = FastAPI(title=settings.PROJECT_NAME, lifespan=lifespan)

app.include_router(rag_router, prefix=settings.API_V1_STR, tags=["RAG"])
app.include_router(session_router, prefix=settings.API_V1_STR, tags=["Sessions"])
app.include_router(system_router, prefix=settings.API_V1_STR, tags=["System"])

@app.get("/")
async def root():
    return {"message": "QuickBuild RAG API", "docs": "/docs"}'
    
    # Requirements file
    write_file "backend/requirements.txt" 'fastapi>=0.104.0
uvicorn[standard]>=0.24.0
pydantic>=2.5.0
pydantic-settings>=2.1.0
python-multipart>=0.0.6
python-dotenv>=0.20.0
sqlmodel>=0.0.14'
    
    # RAG Service
    write_file "backend/app/services/rag_service.py" 'import sys
import os
from typing import Dict, Any, Optional

# Add the parent directory to Python path to import from rag_system
sys.path.append(os.path.join(os.path.dirname(__file__), "..", "..", ".."))

from app.core.config import settings

class RAGService:
    """Service for interfacing with the QuickBuild RAG agent."""
    
    def __init__(self):
        self._rag_agent = None
        
    def _get_rag_agent(self):
        """Lazy load the RAG agent to avoid startup delays."""
        if self._rag_agent is None:
            try:
                from rag_system.rag_agent import QuickBuildRAG
                self._rag_agent = QuickBuildRAG(settings.RAG_JSON_PATH)
            except Exception as e:
                raise RuntimeError(f"Failed to initialize RAG agent: {e}")
        return self._rag_agent
    
    def ask_question(self, question: str, top_k: int = 3) -> Dict[str, Any]:
        """
        Ask a question to the RAG system.
        
        Args:
            question: The question to ask
            top_k: Number of relevant documents to retrieve
            
        Returns:
            Dictionary with answer, confidence, sources, etc.
        """
        rag_agent = self._get_rag_agent()
        return rag_agent.ask(question, top_k)
    
    def health_check(self) -> Dict[str, Any]:
        """
        Check if the RAG system is healthy.
        
        Returns:
            Dictionary with health status
        """
        try:
            rag_agent = self._get_rag_agent()
            # Try a simple operation
            result = rag_agent.ask("test", top_k=1)
            return {
                "status": "healthy",
                "documents_loaded": len(rag_agent.documents) if hasattr(rag_agent, "documents") else "unknown"
            }
        except Exception as e:
            return {
                "status": "unhealthy", 
                "error": str(e)
            }'
    
    # Create __init__.py files for modules
    write_file "backend/app/models/__init__.py" 'from .rag_models import RAGQueryRequest, RAGResponse, SourceDocument
from .db_models import SessionTable, MessageTable, MessageTypeEnum
from .session_models import SessionCreateRequest, SessionResponse, SessionHistoryResponse, MessageBase
from .system_models import HealthResponse, ExamplesResponse, ExampleQuestion

__all__ = [
    "RAGQueryRequest", 
    "RAGResponse", 
    "SourceDocument",
    "SessionTable",
    "MessageTable",
    "MessageTypeEnum",
    "SessionCreateRequest",
    "SessionResponse", 
    "SessionHistoryResponse",
    "MessageBase",
    "HealthResponse",
    "ExamplesResponse", 
    "ExampleQuestion"
]'
    
    write_file "backend/app/routers/__init__.py" 'from .rag_router import router as rag_router
from .session_router import router as session_router
from .system_router import router as system_router

__all__ = ["rag_router", "session_router", "system_router"]'
    
    write_file "backend/app/services/__init__.py" 'from .rag_service import RAGService

__all__ = ["RAGService"]'
    
    write_file "backend/app/crud/__init__.py" 'from .crud_session import (
    create_session,
    get_session_by_id,
    delete_session,
    create_message,
    get_session_history,
    get_or_create_session
)

__all__ = [
    "create_session",
    "get_session_by_id", 
    "delete_session",
    "create_message",
    "get_session_history",
    "get_or_create_session"
]'
    
    # Call helper functions to create the detailed files
    create_backend_models
    create_backend_routers
    create_backend_crud
    create_backend_db
}

# Create all frontend files
create_frontend_files() {
    log_info "Creating frontend files..."
    
    ensure_directory "frontend/src"
    
    create_frontend_config
    create_frontend_components
    create_frontend_types_and_services
}

# Validation and testing functions
validate_files() {
    log_info "Validating created files..."
    
    # Check critical backend files
    critical_backend_files=(
        "backend/app/main.py"
        "backend/app/core/config.py"
        "backend/requirements.txt"
        "backend/app/services/rag_service.py"
        "backend/app/routers/rag_router.py"
    )
    
    # Check critical frontend files
    critical_frontend_files=(
        "frontend/package.json"
        "frontend/src/main.tsx"
        "frontend/src/App.tsx"
        "frontend/src/components/ChatWindow.tsx"
    )
    
    for file in "${critical_backend_files[@]}"; do
        if [[ -f "$file" ]]; then
            log_success "✓ $file exists"
        else
            log_error "✗ Missing critical file: $file"
        fi
    done
    
    for file in "${critical_frontend_files[@]}"; do
        if [[ -f "$file" ]]; then
            log_success "✓ $file exists"
        else
            log_error "✗ Missing critical file: $file"
        fi
    done
}

# Cleanup function
cleanup() {
    log_info "Cleanup function called"
}

# Help function
show_help() {
    echo "Jules Recovery Script - Help"
    echo ""
    echo "Usage: $0 [OPTIONS]"
    echo ""
    echo "Options:"
    echo "  --dry-run        Show what would be created without actually creating files"
    echo "  --debug          Enable debug logging"
    echo "  --force          Overwrite existing files"
    echo "  --help           Show this help message"
    echo ""
    echo "Environment Variables:"
    echo "  DRY_RUN=true     Enable dry run mode"
    echo "  DEBUG=true       Enable debug mode"
    echo "  FORCE=true       Force overwrite existing files"
    echo ""
    echo "Examples:"
    echo "  $0                           # Normal run"
    echo "  $0 --dry-run                 # See what would be created"
    echo "  DEBUG=true $0               # Run with debug output"
    echo "  FORCE=true $0               # Overwrite existing files"
    echo ""
}

# Main execution
main() {
    # Parse arguments
    while [[ $# -gt 0 ]]; do
        case $1 in
            --dry-run)
                DRY_RUN=true
                shift
                ;;
            --debug)
                DEBUG=true
                shift
                ;;
            --force)
                FORCE=true
                shift
                ;;
            --help)
                show_help
                exit 0
                ;;
            *)
                log_error "Unknown option: $1"
                show_help
                exit 1
                ;;
        esac
    done
    
    # Setup
    setup_logging
    trap cleanup EXIT
    
    # Create all files
    log_info "Starting file creation process..."
    create_backend_files
    create_frontend_files
    
    # Validate
    validate_files
    
    # Summary
    log_info "=== Recovery Summary ==="
    log_info "Backend files created in: backend/"
    log_info "Frontend files created in: frontend/"
    log_info "Backup directory: $BACKUP_DIR"
    log_info "Log file: $LOG_FILE"
    
    if [[ "$DRY_RUN" == "true" ]]; then
        log_info "DRY RUN completed - no files were actually created"
    else
        log_success "Recovery completed successfully!"
        log_info "Next steps:"
        log_info "1. cd backend && pip install -r requirements.txt"
        log_info "2. cd frontend && npm install"
        log_info "3. Start backend: cd backend && uvicorn app.main:app --reload"
        log_info "4. Start frontend: cd frontend && npm run dev"
    fi
}

# Run main function
main "$@"