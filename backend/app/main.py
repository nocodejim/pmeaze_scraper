import logging
import time
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.base import BaseHTTPMiddleware # RequestResponseCallNext removed
from starlette.types import ASGIApp # Added ASGIApp
from starlette.responses import Response, JSONResponse
from contextlib import asynccontextmanager

from app.routers import rag_router, session_router, system_router
from app.core.config import settings
from app.db.database import create_db_and_tables

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    create_db_and_tables()
    yield
    # Shutdown (if needed)

# Basic logging configuration
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

app = FastAPI(title=settings.PROJECT_NAME, lifespan=lifespan)

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Request Logging Middleware
class RequestLoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next: ASGIApp) -> Response: # Type hint updated
        start_time = time.time()
        
        response = await call_next(request)
        
        process_time = time.time() - start_time
        logger.info(
            f"Processed: {request.method} {request.url.path} - Status: {response.status_code} - Client: {request.client.host} - Time: {process_time:.4f}s"
        )
        
        return response

# Add the middleware to the FastAPI application
app.add_middleware(RequestLoggingMiddleware)

app.include_router(rag_router, prefix=settings.API_V1_STR, tags=["RAG"])
app.include_router(session_router, prefix=settings.API_V1_STR, tags=["Sessions"])
app.include_router(system_router, prefix=settings.API_V1_STR, tags=["System"])

@app.get("/")
async def root():
    return {"message": "QuickBuild RAG API", "docs": "/docs"}
