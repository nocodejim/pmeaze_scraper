from pydantic import BaseModel
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
    messages: List[MessageBase]
