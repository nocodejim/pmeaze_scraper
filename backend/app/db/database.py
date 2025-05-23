from sqlmodel import create_engine, Session, SQLModel
from app.core.config import settings

DATABASE_URL = "sqlite:///./quickbuild_rag.db"  # Will create DB file in project root

engine = create_engine(DATABASE_URL, echo=True, connect_args={"check_same_thread": False})

def create_db_and_tables():
    SQLModel.metadata.create_all(engine)

def get_session():
    with Session(engine) as session:
        yield session
