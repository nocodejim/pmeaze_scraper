from pydantic import BaseModel
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
    session_id: Optional[str] = None
