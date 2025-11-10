from __future__ import annotations

from typing import Any, Protocol

from openai import AsyncOpenAI
from pydantic import BaseModel

from ..settings import Settings, get_settings


class LLMRequest(BaseModel):
    prompt: str
    max_tokens: int = 512
    temperature: float = 0.2


class LLMResponse(BaseModel):
    output: str
    raw: dict[str, Any] | None = None


class LLMClient(Protocol):
    async def generate(self, request: LLMRequest) -> LLMResponse:
        ...


class OpenAIClient:
    def __init__(self, settings: Settings):
        self._client = AsyncOpenAI(api_key=settings.openai_api_key.get_secret_value())  # type: ignore[arg-type]

    async def generate(self, request: LLMRequest) -> LLMResponse:
        completion = await self._client.responses.create(
            model="gpt-4o-mini",
            input=request.prompt,
            max_output_tokens=request.max_tokens,
            temperature=request.temperature,
        )
        output = completion.output[0].content[0].text if completion.output else ""
        return LLMResponse(output=output, raw=completion.model_dump())


class HuggingFaceClient:
    def __init__(self, settings: Settings):
        self.api_key = settings.huggingface_api_key.get_secret_value()  # type: ignore[union-attr]
        # Placeholder: add HTTP client setup here (e.g., using httpx)

    async def generate(self, request: LLMRequest) -> LLMResponse:
        raise NotImplementedError(
            "Hugging Face client not yet implemented. Add API call here."
        )


def get_llm_client(settings: Settings | None = None) -> LLMClient:
    settings = settings or get_settings()
    if settings.llm_provider == "openai":
        return OpenAIClient(settings=settings)
    if settings.llm_provider == "huggingface":
        return HuggingFaceClient(settings=settings)
    raise ValueError(f"Unsupported LLM provider '{settings.llm_provider}'")

