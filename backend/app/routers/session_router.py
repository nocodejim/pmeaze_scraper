from fastapi import APIRouter, HTTPException, Depends, status
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
    return {"message": "Session deleted successfully"}
