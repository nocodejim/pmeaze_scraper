from sqlmodel import SQLModel, Field
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
    created_at: datetime = Field(default_factory=datetime.now)
