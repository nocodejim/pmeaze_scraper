from fastapi import APIRouter, Depends, HTTPException, status # Added HTTPException, status
from sqlmodel import Session, select # Added select
import os # Added os

from app.models.system_models import DetailedHealthStatus, SubsystemStatus, ExamplesResponse, ExampleQuestion # Updated imports
from app.core.config import settings # Added settings
# from app.services.rag_service import RAGService # RAGService direct check not needed for this version
from app.db.database import get_session

router = APIRouter()

@router.get("/health", response_model=DetailedHealthStatus)
async def health_check(db: Session = Depends(get_session)):
    """Check system health including DB and RAG data file."""
    api_overall_status = "ok"
    
    # 1. Check Database Connectivity
    try:
        db.exec(select(1)).first() # Simple query
        db_subsystem_status = SubsystemStatus(status="ok", details="Database connection successful.")
    except Exception as e:
        db_subsystem_status = SubsystemStatus(status="error", details=f"Database connection failed: {str(e)}")
        api_overall_status = "error" 

    # 2. Check RAG data file existence
    if os.path.exists(settings.RAG_JSON_PATH):
        rag_subsystem_status = SubsystemStatus(status="ok", details="RAG data file found.")
    else:
        rag_subsystem_status = SubsystemStatus(status="error", details=f"RAG data file not found at {settings.RAG_JSON_PATH}")
        if api_overall_status != "error": # Don't override a more critical DB error
             api_overall_status = "degraded"
    
    response_model_content = DetailedHealthStatus(
        api_status=api_overall_status,
        database_status=db_subsystem_status,
        rag_system_status=rag_subsystem_status
    )

    if api_overall_status == "error": # Critical error (DB down)
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=response_model_content.model_dump()
        )
    # For "degraded" or "ok", return 200 OK with the detailed status
    return response_model_content

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
    
    return ExamplesResponse(examples=examples)
