from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    # API Keys
    OPENAI_API_KEY: str
    GROQ_API_KEY: str
    SERPAPI_KEY: str
    
    # Database
    DATABASE_URL: str = "sqlite:///./bureaucracy_navigator.db"
    
    # Redis
    REDIS_URL: str = "redis://localhost:6379"
    
    # Chroma
    CHROMA_PERSIST_DIRECTORY: str = "./chroma_db"
    
    # File Upload
    UPLOAD_DIR: str = "./uploads"
    MAX_FILE_SIZE: int = 10 * 1024 * 1024  # 10MB
    
    # Logging
    LOG_LEVEL: str = "INFO"
    
    class Config:
        env_file = ".env"

settings = Settings()
