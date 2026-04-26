"""
Application configuration settings
"""
from pydantic_settings import BaseSettings
from typing import List


class Settings(BaseSettings):
    # App settings
    APP_NAME: str = "Vietnamese Food AI"
    DEBUG: bool = True
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    
    # Database
    DATABASE_URL: str = "postgresql://user:password@localhost:5432/food_ai_db"
    
    # AI Server
    AI_SERVER_URL: str = "http://localhost:8001"
    
    # AI Model settings
    MODEL_PATH: str = "../ai_models/trained_weights"
    
    # CORS
    ALLOWED_ORIGINS: List[str] = ["http://localhost:3000", "http://localhost:8080", "http://localhost:5173"]
    
    # Google Maps
    GOOGLE_MAPS_API_KEY: str = ""
    
    # JWT Settings
    SECRET_KEY: str = "your-secret-key-here"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # Gemini AI Chat
    GEMINI_API_KEY: str = ""
    
    class Config:
        env_file = ".env"
        extra = "ignore"


settings = Settings()
