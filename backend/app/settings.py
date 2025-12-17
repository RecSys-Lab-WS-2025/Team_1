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

    # Ollama LLM configuration (for GenAI story generation)
    # Using Llama3.1:8b for high-quality, structured output
    ollama_api_url: str = Field(
        default="http://127.0.0.1:11434/api/generate",
        env="OLLAMA_API_URL",
        description="Ollama API endpoint URL",
    )
    ollama_model: str = Field(
        default="llama3.1:8b",
        env="OLLAMA_MODEL",
        description="Ollama model name (llama3.1:8b recommended for best results)",
    )
    ollama_timeout: int = Field(
        default=120,
        env="OLLAMA_TIMEOUT",
        description="Timeout in seconds for Ollama API calls (increased for batch story generation)",
    )

    # Logging configuration
    log_level: str = Field(
        default="INFO",
        env="LOG_LEVEL",
        description="Logging level: DEBUG, INFO, WARNING, ERROR, CRITICAL",
    )
    log_enable_file: bool = Field(
        default=True,
        env="LOG_ENABLE_FILE",
        description="Enable file logging",
    )
    log_enable_console: bool = Field(
        default=True,
        env="LOG_ENABLE_CONSOLE",
        description="Enable console logging",
    )
    log_detailed_format: bool = Field(
        default=True,
        env="LOG_DETAILED_FORMAT",
        description="Use detailed log format with function names and line numbers",
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

