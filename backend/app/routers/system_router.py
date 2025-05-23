from fastapi import APIRouter, Depends
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
    
    return ExamplesResponse(examples=examples)
