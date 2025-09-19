from pydantic import Field
from pydantic_settings import BaseSettings
from typing import List, Optional
from functools import lru_cache


class Settings(BaseSettings):
    # Project info
    PROJECT_NAME: str = "numeo-ai"
    VERSION: str = "0.1.0"
    DESCRIPTION: str = "Backend API for Numeo AI Task"

    # API configuration
    API_V1_STR: str = "/api/v1"

    # CORS settings
    CORS_ORIGINS: List[str] = [
        "http://localhost:3000",
    ]

    # Logging settings
    LOG_LEVEL: str = Field("INFO", env="LOG_LEVEL")

    # Database settings
    DB_USER: str = Field(..., env="DB_USER")
    DB_PASSWORD: str = Field(..., env="DB_PASSWORD")
    DB_NAME: str = Field(..., env="DB_NAME")
    DB_HOST: str = Field(..., env="DB_HOST")
    DB_PORT: str = Field(..., env="DB_PORT")

    # Security
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    # OpenAI
    OPENAI_API_KEY: str = Field(..., env="OPENAI_API_KEY")

    # Google authentication credentials
    GOOGLE_CLIENT_ID: str = Field(..., env="GOOGLE_CLIENT_ID")
    GOOGLE_CLIENT_SECRET: str = Field(..., env="GOOGLE_CLIENT_SECRET")
    GOOGLE_REDIRECT_URI: str = Field(
        default="https://cyano-pitifully-ronan.ngrok-free.app/auth/google/callback"
    )
    GOOGLE_OAUTH_SCOPES: List[str] = [
        "https://www.googleapis.com/auth/gmail.readonly",
        "https://www.googleapis.com/auth/gmail.send",
    ]

    # Gmail Push / PubSub
    GCP_PROJECT_ID: Optional[str] = Field(None, env="GCP_PROJECT_ID")
    GMAIL_PUBSUB_TOPIC: Optional[str] = Field(None, env="GMAIL_PUBSUB_TOPIC")
    GMAIL_WATCH_LABEL_IDS: List[str] = ["INBOX"]

    class Config:
        env_file = ".env"
        case_sensitive = True


@lru_cache
def get_settings() -> "Settings":
    return Settings()


settings = get_settings()
