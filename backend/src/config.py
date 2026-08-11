"""Application configuration.

Loads settings from environment variables / `.env`. Secrets are never hardcoded
or committed; they come from the environment or a git-ignored `.env` file
(constitution Principle 9).
"""

from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    app_name: str = "AI Customer Support Worker"
    environment: str = "development"

    database_url: str = "postgresql+psycopg://support:support@localhost:5432/support"
    session_secret: str = "change-me-in-env"  # MUST be overridden in real deployments

    llm_api_key: str = ""
    llm_model: str = "claude-sonnet-5"
    llm_temperature: float = 0.0  # deterministic where possible (NFR-005)

    knowledge_seed_path: str = "data/knowledge_seed.json"


@lru_cache
def get_settings() -> Settings:
    return Settings()
