from functools import lru_cache
from typing import Literal

from pydantic import BaseSettings, Field, HttpUrl, SecretStr, validator


class Settings(BaseSettings):
    """
    Runtime configuration for the FastAPI service.
    """

    app_name: str = Field(default="Rec Lab API")
    version: str = Field(default="0.1.0")

    # Supabase configuration.
    supabase_url: HttpUrl = Field(..., env="SUPABASE_URL")
    supabase_anon_key: SecretStr = Field(..., env="SUPABASE_ANON_KEY")
    supabase_service_role_key: SecretStr | None = Field(
        default=None, env="SUPABASE_SERVICE_ROLE_KEY"
    )

    # LLM provider selection.
    llm_provider: Literal["openai", "huggingface"] = Field(
        default="openai", env="LLM_PROVIDER"
    )
    openai_api_key: SecretStr | None = Field(default=None, env="OPENAI_API_KEY")
    huggingface_api_key: SecretStr | None = Field(
        default=None, env="HUGGINGFACE_API_KEY"
    )

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

    @validator("openai_api_key", always=True)
    def validate_openai_key(cls, value, values) -> SecretStr | None:
        if values.get("llm_provider") == "openai" and value is None:
            raise ValueError("OPENAI_API_KEY is required when LLM_PROVIDER=openai")
        return value

    @validator("huggingface_api_key", always=True)
    def validate_huggingface_key(cls, value, values) -> SecretStr | None:
        if values.get("llm_provider") == "huggingface" and value is None:
            raise ValueError(
                "HUGGINGFACE_API_KEY is required when LLM_PROVIDER=huggingface"
            )
        return value


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    """
    Cached accessor for application settings.
    """
    return Settings()

