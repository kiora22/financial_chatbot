import os
from pydantic_settings import BaseSettings
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


class Settings(BaseSettings):
    """Application settings."""
    
    # API Keys
    openai_api_key: str = os.getenv("OPENAI_API_KEY", "")
    
    # Application settings
    log_level: str = os.getenv("LOG_LEVEL", "INFO")
    debug: bool = os.getenv("DEBUG", "False").lower() == "true"
    
    # Frontend
    streamlit_server_port: int = int(os.getenv("STREAMLIT_SERVER_PORT", "8501"))
    streamlit_server_headless: bool = os.getenv("STREAMLIT_SERVER_HEADLESS", "true").lower() == "true"
    
    # Backend
    backend_port: int = int(os.getenv("BACKEND_PORT", "8000"))
    backend_host: str = os.getenv("BACKEND_HOST", "0.0.0.0")
    backend_url: str = os.getenv("BACKEND_URL", "http://localhost:8000")
    
    # Database
    sqlite_db_path: str = os.getenv("SQLITE_DB_PATH", "data/financial_db.sqlite")
    database_url: str = f"sqlite:///{sqlite_db_path}"
    
    # Document processing
    max_document_size_mb: int = int(os.getenv("MAX_DOCUMENT_SIZE_MB", "10"))
    document_watch_folder: str = os.getenv("DOCUMENT_WATCH_FOLDER", "data/document_drop")
    
    # Vector store
    chromadb_host: str = os.getenv("CHROMADB_HOST", "localhost")
    chromadb_port: int = int(os.getenv("CHROMADB_PORT", "8080"))
    chromadb_url: str = f"http://{chromadb_host}:{chromadb_port}"
    
    class Config:
        env_file = ".env"


settings = Settings()