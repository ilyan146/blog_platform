"""Application configuration.

Every environment-dependent value lives here. Required fields have no default,
so the app fails fast at startup if they are missing rather than misbehaving
later. Import once: `from app.config import settings`.
"""

from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    # --- Core ---
    database_url: str
    jwt_secret: str
    jwt_algorithm: str = "HS256"
    access_token_ttl_minutes: int = 60 * 24

    # --- CORS ---
    cors_origins: list[str] = ["http://localhost:5173"]

    # --- Azure AI Foundry ---
    azure_openai_endpoint: str
    azure_openai_api_key: str
    azure_openai_deployment: str
    azure_openai_api_version: str = "2024-10-21"


@lru_cache
def get_settings() -> Settings:
    return Settings()  # type: ignore[call-arg]


settings = get_settings()
