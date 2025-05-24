from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import List

class Settings(BaseSettings):
    PROJECT_NAME: str = "QuickBuild RAG API"
    API_V1_STR: str = "/api/v1"
    DATABASE_URL: str = "sqlite:///./quickbuild_rag.db"
    # Path relative to the backend app directory if used directly by Python code.
    # For Docker, this path needs to be valid *inside* the container.
    RAG_JSON_PATH: str = "../scraper/output/all_content.json" 
    CORS_ORIGINS: List[str] = ["http://localhost:3000", "http://localhost:5173"]

    # For loading from .env file
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding='utf-8', extra='ignore')

settings = Settings()
