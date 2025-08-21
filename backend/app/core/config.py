"""
Application configuration management.
"""
from typing import Any, Dict, List, Optional, Union
from pydantic import AnyHttpUrl, validator
from pydantic_settings import BaseSettings
import os
from pathlib import Path

class Settings(BaseSettings):
    """Application settings with environment variable support."""
    
    # API Configuration
    API_V1_STR: str = "/api/v1"
    PROJECT_NAME: str = "AI Scrum Master"
    VERSION: str = "1.0.0"
    
    # Security
    SECRET_KEY: str = "your-secret-key-change-in-production"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 8  # 8 days
    
    # CORS
    BACKEND_CORS_ORIGINS: List[str] = [
        "http://localhost:3000",  # React dev server
        "http://localhost:8080",  # Alternative frontend
        "http://localhost:5173",  # Vite dev server
    ]

    @validator("BACKEND_CORS_ORIGINS", pre=True)
    def assemble_cors_origins(cls, v: Union[str, List[str]]) -> List[str]:
        if isinstance(v, str):
            return [i.strip() for i in v.split(",")]
        elif isinstance(v, list):
            return v
        return ["http://localhost:3000"]

    # Database (using SQLite for development)
    DATABASE_URL: str = "sqlite:///./scrum_db.sqlite"
    
    # Redis for caching and task queue
    REDIS_URL: str = "redis://localhost:6379"
    
    # OpenAI Configuration
    OPENAI_API_KEY: str = ""
    OPENAI_MODEL: str = "gpt-4"
    OPENAI_MAX_TOKENS: int = 2000
    OPENAI_TEMPERATURE: float = 0.7
    
    # Slack Integration
    SLACK_BOT_TOKEN: str = ""
    SLACK_SIGNING_SECRET: str = ""
    SLACK_APP_TOKEN: str = ""
    SLACK_WEBHOOK_URL: str = ""
    
    # Jira Integration
    JIRA_URL: str = ""
    JIRA_USERNAME: str = ""
    JIRA_API_TOKEN: str = ""
    JIRA_PROJECT_KEY: str = ""
    
    # GitHub Integration
    GITHUB_TOKEN: str = ""
    GITHUB_OWNER: str = ""
    GITHUB_REPO: str = ""
    
    # Vector Database (ChromaDB)
    VECTOR_DB_PATH: str = "./data/chromadb"
    VECTOR_COLLECTION_NAME: str = "scrum_knowledge"
    
    # AI Configuration
    AI_CONTEXT_WINDOW: int = 4000
    AI_MAX_RETRIES: int = 3
    AI_TEMPERATURE: float = 0.3  # Lower for more consistent outputs
    
    # Workflow Configuration
    STANDUP_TIME: str = "09:00"  # Daily standup time (24h format)
    STANDUP_TIMEZONE: str = "UTC"
    STANDUP_CHANNEL: str = "#standup"
    
    # Feature Flags
    ENABLE_SLACK_BOT: bool = True
    ENABLE_JIRA_INTEGRATION: bool = True
    ENABLE_GITHUB_INTEGRATION: bool = False
    ENABLE_AUTO_STANDUP: bool = True
    ENABLE_BACKLOG_GROOMING: bool = True
    
    # Logging
    LOG_LEVEL: str = "INFO"
    LOG_FORMAT: str = "json"
    
    # Security
    SECRET_KEY: str = "your-secret-key-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    class Config:
        env_file = ".env"
        case_sensitive = True

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # Create data directory if it doesn't exist
        Path(self.VECTOR_DB_PATH).parent.mkdir(parents=True, exist_ok=True)

# Global settings instance
settings = Settings()

# Validate critical settings
def validate_settings():
    """Validate critical configuration settings."""
    errors = []
    
    if not settings.OPENAI_API_KEY:
        errors.append("OPENAI_API_KEY is required")
    
    if settings.ENABLE_SLACK_BOT and not settings.SLACK_BOT_TOKEN:
        errors.append("SLACK_BOT_TOKEN is required when Slack integration is enabled")
    
    if settings.ENABLE_JIRA_INTEGRATION and not all([
        settings.JIRA_URL, settings.JIRA_USERNAME, settings.JIRA_API_TOKEN
    ]):
        errors.append("JIRA credentials are required when Jira integration is enabled")
    
    if errors:
        raise ValueError("Configuration errors: " + "; ".join(errors))

# Environment-specific configurations
class DevelopmentSettings(Settings):
    """Development environment settings."""
    LOG_LEVEL: str = "DEBUG"
    AI_TEMPERATURE: float = 0.5

class ProductionSettings(Settings):
    """Production environment settings."""
    LOG_LEVEL: str = "WARNING"
    AI_TEMPERATURE: float = 0.2
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24  # 1 day in production

def get_settings() -> Settings:
    """Get settings based on environment."""
    env = os.getenv("ENVIRONMENT", "development").lower()
    
    if env == "production":
        return ProductionSettings()
    elif env == "development":
        return DevelopmentSettings()
    else:
        return Settings()