from functools import lru_cache
from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


PROJECT_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_DB_PATH = PROJECT_ROOT / "data" / "app.db"
DEFAULT_DB_PATH.parent.mkdir(parents=True, exist_ok=True)
DEFAULT_DB_URL = f"sqlite+aiosqlite:///{DEFAULT_DB_PATH.as_posix()}"


class Settings(BaseSettings):
    """
    Runtime configuration for the FastAPI service.
    """

    app_name: str = Field(default="Rec Lab API")
    version: str = Field(default="0.1.0")

    # Database configuration (SQLite by default)
    database_url: str = Field(
        default=DEFAULT_DB_URL,
        env="DATABASE_URL",
        description="Database connection string. Defaults to sqlite+aiosqlite:///.../data/app.db",
    )

    # TinyLlama configuration (for GenAI story generation via Ollama)
    tinyllama_api_url: str = Field(
        default="http://localhost:11434/api/generate",
        env="TINYLLAMA_API_URL",
        description="Ollama API endpoint URL for TinyLlama",
    )
    tinyllama_model: str = Field(
        default="tinyllama",
        env="TINYLLAMA_MODEL",
        description="Ollama model name to use",
    )
    tinyllama_timeout: int = Field(
        default=30,
        env="TINYLLAMA_TIMEOUT",
        description="Timeout in seconds for TinyLlama API calls",
    )

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    """
    Cached accessor for application settings.
    """
    return Settings()

