from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    app_name: str = "Meridian"
    app_version: str = "0.1.0"
    debug: bool = True

    # Database
    database_url: str = "postgresql+asyncpg://meridian:meridian@localhost:5432/meridian"
    database_url_sync: str = "postgresql://meridian:meridian@localhost:5432/meridian"

    # File storage
    upload_dir: str = "uploads"
    max_upload_size_mb: int = 50

    # AI / LLM
    openai_api_key: str = ""
    openai_model: str = "gpt-4o"
    embedding_model: str = "text-embedding-3-small"

    # ChromaDB
    chroma_persist_dir: str = "./chroma_data"

    # Auth (placeholder)
    secret_key: str = "dev-secret-change-in-production"
    access_token_expire_minutes: int = 60

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8"}


@lru_cache
def get_settings() -> Settings:
    return Settings()
