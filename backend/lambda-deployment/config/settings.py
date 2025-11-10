"""
Configuration settings for the AI Chat Agent backend.
Manages AWS Bedrock credentials and application settings.
"""

import os
from typing import Optional
from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # AWS Configuration
    aws_access_key_id: Optional[str] = None
    aws_secret_access_key: Optional[str] = None
    aws_region: str = "us-east-1"

    # AWS Bedrock Configuration
    bedrock_model_id: str = "us.anthropic.claude-3-5-sonnet-20241022-v2:0"
    bedrock_runtime_endpoint: Optional[str] = None

    # Knowledge Base Configuration
    knowledge_base_id: Optional[str] = None
    knowledge_base_enabled: bool = False
    kb_max_results: int = 5

    # Application Configuration
    app_name: str = "Summoners Reunion AI Agent"
    debug: bool = False
    cors_origins: str = "http://localhost:3000,http://localhost:8000,http://127.0.0.1:8000,http://localhost:8080,http://127.0.0.1:8080"

    @property
    def cors_origins_list(self) -> list[str]:
        """Parse CORS origins from comma-separated string."""
        return [origin.strip() for origin in self.cors_origins.split(",")]

    # Chat Configuration
    max_conversation_history: int = 50
    streaming_enabled: bool = True

    # Model Parameters
    max_tokens: int = 4096
    temperature: float = 1.0
    top_p: float = 0.999

    class Config:
        env_file = "../.env"
        env_file_encoding = "utf-8"
        case_sensitive = False
        extra = "ignore"


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()
