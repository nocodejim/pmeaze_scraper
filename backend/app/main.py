from fastapi import FastAPI, HTTPException
from starlette.responses import JSONResponse
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

app = FastAPI(title=settings.PROJECT_NAME, lifespan=lifespan)

app.include_router(rag_router, prefix=settings.API_V1_STR, tags=["RAG"])
app.include_router(session_router, prefix=settings.API_V1_STR, tags=["Sessions"])
app.include_router(system_router, prefix=settings.API_V1_STR, tags=["System"])

@app.get("/")
async def root():
    return {"message": "QuickBuild RAG API", "docs": "/docs"}
