import os
from typing import List, Union
from pydantic import AnyHttpUrl, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    PROJECT_NAME: str = "AgriAssist AI"
    API_V1_STR: str = "/api/v1"
    
    # Security
    JWT_SECRET_KEY: str = "supersecretkeychangeinproduction1234567890"  # Keep a default for development
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # Database Configuration
    # Fallback to local mysql container root:password@localhost/agriassist
    DATABASE_URL: str = "mysql+pymysql://root:Pranav%4099@localhost:3306/agriassist"
    
    # Gemini API Config
    GEMINI_API_KEY: str = ""
    
    # CORS Origins
    BACKEND_CORS_ORIGINS: List[str] = [
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:3000",
        "http://127.0.0.1:3000"
    ]

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore"
    )


settings = Settings()
