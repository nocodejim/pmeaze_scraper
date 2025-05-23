import time
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
        )
