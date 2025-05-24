from sqlmodel import Session, select
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
    message_metadata: Optional[dict] = None
) -> MessageTable:
    """Create a new message in a session."""
    message = MessageTable(
        session_id=session_id,
        type=message_type,
        content=content,
        message_metadata=json.dumps(message_metadata) if message_metadata else None
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
        metadata = json.loads(msg.message_metadata) if msg.message_metadata else None
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
    )
