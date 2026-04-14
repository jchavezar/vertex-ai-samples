"""Configuration management for Vertex Cowork."""

from functools import lru_cache
from typing import Literal

from pydantic import Field
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # GCP Configuration
    gcp_project_id: str = Field(..., description="Google Cloud Project ID")
    gcp_location: str = Field(default="us-central1", description="GCP region")

    # API Configuration
    api_host: str = Field(default="0.0.0.0")
    api_port: int = Field(default=8080)

    # Database
    database_url: str = Field(
        default="postgresql+asyncpg://localhost:5432/vertex_cowork"
    )
    redis_url: str = Field(default="redis://localhost:6379")

    # Default Framework
    default_framework: Literal["adk", "langgraph"] = Field(default="adk")

    # Model Defaults
    default_model: str = Field(default="gemini-2.0-flash")
    default_model_provider: Literal["vertex", "model_garden"] = Field(
        default="vertex"
    )

    # Security
    enable_auth: bool = Field(default=True)

    model_config = {"env_prefix": "VERTEX_COWORK_", "env_file": ".env"}


@lru_cache
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()
