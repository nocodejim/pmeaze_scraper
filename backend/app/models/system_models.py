from pydantic import BaseModel
from typing import List, Dict, Any

class HealthResponse(BaseModel):
    status: str
    database: str
    rag_system: Dict[str, Any]

class ExampleQuestion(BaseModel):
    question: str
    category: str

class ExamplesResponse(BaseModel):
    examples: List[ExampleQuestion]
