from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional
from datetime import datetime

# New Health Status Models
class SubsystemStatus(BaseModel):
    status: str = "ok"
    details: Optional[str] = None

class DetailedHealthStatus(BaseModel):
    api_status: str = "ok"
    database_status: SubsystemStatus
    rag_system_status: SubsystemStatus
    # timestamp: datetime = Field(default_factory=datetime.utcnow) # Optional: consider adding for freshness

class ExampleQuestion(BaseModel):
    question: str
    category: str

class ExamplesResponse(BaseModel):
    examples: List[ExampleQuestion]

class ErrorDetail(BaseModel):
    type: str
    message: str
    details: Optional[str] = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)

class ErrorResponse(BaseModel):
    error: ErrorDetail
