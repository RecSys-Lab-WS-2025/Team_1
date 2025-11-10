from fastapi import APIRouter, Depends

from ...services.llm import LLMRequest, LLMResponse, get_llm_client

router = APIRouter(prefix="/sample", tags=["sample"])


@router.post("/llm", response_model=LLMResponse)
async def sample_llm_endpoint(
    request: LLMRequest,
    llm_client=Depends(get_llm_client),
) -> LLMResponse:
    """
    Demonstrates how to proxy requests to the configured LLM provider.
    """
    return await llm_client.generate(request)

