from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    app_name: str = "CarbonPilot AI"
    environment: str = "local"
    database_url: str = "postgresql+psycopg://carbonpilot:carbonpilot@localhost:5432/carbonpilot"
    langsmith_tracing: bool = False
    langsmith_api_key: str | None = None
    langsmith_project: str = "carbonpilot-ai"
    gemini_api_key: str | None = None
    jwt_secret: str = "change-me-local-only"
    jwt_algorithm: str = "HS256"
    jwt_expire_minutes: int = 60


@lru_cache
def get_settings() -> Settings:
    return Settings()