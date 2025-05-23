from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    PROJECT_NAME: str = "QuickBuild RAG API"
    API_V1_STR: str = "/api/v1"
    RAG_JSON_PATH: str = "scraper/output/all_content.json"  # Default path

    class Config:
        env_file = ".env"  # Optional: if you use a .env file for local development

settings = Settings()
