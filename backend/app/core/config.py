from functools import lru_cache
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "MediClaim AI API"
    app_version: str = "1.0.0"
    environment: str = "development"

    # Database — PostgreSQL via asyncpg
    database_url: str = "postgresql+asyncpg://mediclaim:mediclaim@localhost:5432/mediclaim"

    # Storage — local disk
    upload_dir: str = "uploads"

    # API Keys
    gemini_api_key: str | None = None

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    @property
    def upload_path(self) -> Path:
        p = Path(self.upload_dir)
        p.mkdir(parents=True, exist_ok=True)
        return p


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
