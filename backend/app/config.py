import os
from typing import Optional
from dotenv import load_dotenv
from pydantic_settings import BaseSettings, SettingsConfigDict

# Automatically load .env file into os.environ
load_dotenv()


class Settings(BaseSettings):
    PROJECT_NAME: str = "SentinelTrace — Prompt Injection Behavioral Detector"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api/v1"

    # Database & Redis Settings
    DATABASE_URL: str = os.getenv(
        "DATABASE_URL",
        "sqlite+aiosqlite:///./sentinel_trace.db"
    )
    REDIS_URL: str = os.getenv("REDIS_URL", "redis://localhost:6379/0")

    # Security & CORS
    SECRET_KEY: str = os.getenv("SECRET_KEY", "sentinel-trace-super-secret-key-2026-change-in-prod")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7  # 7 days
    CORS_ORIGINS: str = os.getenv("CORS_ORIGINS", "*")

    # LLM Provider Configuration
    LLM_PROVIDER: str = os.getenv("LLM_PROVIDER", "gemini")  # options: gemini, groq, mock
    GEMINI_MODEL: str = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")
    GROQ_MODEL: str = os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile")
    GOOGLE_API_KEY: Optional[str] = os.getenv("GOOGLE_API_KEY", "")
    GROQ_API_KEY: Optional[str] = os.getenv("GROQ_API_KEY", "")

    # ML & Scoring Parameters
    FEATURE_VECTOR_DIM: int = 12
    ISOLATION_FOREST_CONTAMINATION: float = 0.1
    SUSPICION_DECAY_FACTOR: float = 0.85
    ANOMALY_THRESHOLD: float = 0.65

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )


settings = Settings()
