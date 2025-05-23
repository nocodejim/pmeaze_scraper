import sys
import os
from typing import Dict, Any, Optional

# Add the parent directory to Python path to import from rag_system
sys.path.append(os.path.join(os.path.dirname(__file__), "..", "..", ".."))

from app.core.config import settings

class RAGService:
    """Service for interfacing with the QuickBuild RAG agent."""
    
    def __init__(self):
        self._rag_agent = None
        
    def _get_rag_agent(self):
        """Lazy load the RAG agent to avoid startup delays."""
        if self._rag_agent is None:
            try:
                from rag_system.rag_agent import QuickBuildRAG
                self._rag_agent = QuickBuildRAG(settings.RAG_JSON_PATH)
            except Exception as e:
                raise RuntimeError(f"Failed to initialize RAG agent: {e}")
        return self._rag_agent
    
    def ask_question(self, question: str, top_k: int = 3) -> Dict[str, Any]:
        """
        Ask a question to the RAG system.
        
        Args:
            question: The question to ask
            top_k: Number of relevant documents to retrieve
            
        Returns:
            Dictionary with answer, confidence, sources, etc.
        """
        rag_agent = self._get_rag_agent()
        return rag_agent.ask(question, top_k)
    
    def health_check(self) -> Dict[str, Any]:
        """
        Check if the RAG system is healthy.
        
        Returns:
            Dictionary with health status
        """
        try:
            rag_agent = self._get_rag_agent()
            # Try a simple operation
            result = rag_agent.ask("test", top_k=1)
            return {
                "status": "healthy",
                "documents_loaded": len(rag_agent.documents) if hasattr(rag_agent, "documents") else "unknown"
            }
        except Exception as e:
            return {
                "status": "unhealthy", 
                "error": str(e)
            }
