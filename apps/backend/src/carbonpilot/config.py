from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    app_name: str = "CarbonPilot AI"
    environment: str = "local"
    database_url: str = "postgresql+psycopg://carbonpilot:carbonpilot@localhost:5432/carbonpilot"
    langsmith_tracing: bool = False
    gemini_api_key: str | None = None
    jwt_secret: str = "change-me-local-only"


@lru_cache
def get_settings() -> Settings:
    return Settings()
