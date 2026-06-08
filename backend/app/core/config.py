from functools import lru_cache
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "MediClaim AI API"
    app_version: str = "1.0.0"
    environment: str = "development"

    # Database — SQLite by default (no extra drivers needed on Python 3.14)
    # Switch to postgresql+asyncpg://mediclaim:mediclaim@localhost:5432/mediclaim
    # once asyncpg supports Python 3.14, or run via Docker.
    database_url: str = "sqlite+aiosqlite:///./mediclaim.db"

    # Storage — local disk by default
    upload_dir: str = "uploads"
    use_s3: bool = False
    aws_access_key_id: str = ""
    aws_secret_access_key: str = ""
    aws_s3_bucket: str = ""
    aws_region: str = "ap-south-1"

    # OpenAI (optional — simulation mode if empty)
    openai_api_key: str = ""

    # Clerk (optional — dev bypass if empty)
    clerk_secret_key: str = ""
    clerk_publishable_key: str = ""

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
