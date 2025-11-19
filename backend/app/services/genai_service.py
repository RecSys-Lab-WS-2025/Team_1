"""
GenAI service for generating personalized narratives and summaries using Llama3.1:8b.

This service encapsulates all LLM interactions including:
- Welcome summaries (US-04)
- Route stories (US-06)
- Mini-quest generation (US-10)
- Post-run summaries (US-13)

All prompts use Llama3.1 chat template format with proper prompt engineering:
- Few-shot examples for consistency
- Clear system instructions
- Explicit length constraints
- Structured output where needed
"""
import httpx
from typing import Optional
from fastapi import HTTPException

from app.api.schemas import ProfileCreate
from app.settings import get_settings


async def call_ollama(
    prompt: str,
    max_tokens: int = 300,
    temperature: float = 0.8
) -> str:
    """
    Unified wrapper for Ollama API calls with error handling.
    
    Args:
        prompt: The prompt text to send to the model
        max_tokens: Maximum number of tokens to generate
        temperature: Sampling temperature for generation
    
    Returns:
        str: Generated text response from the model
        
    Raises:
        HTTPException: If the API call fails or returns empty response
    """
    settings = get_settings()
    
    try:
        async with httpx.AsyncClient(timeout=settings.tinyllama_timeout) as client:
            response = await client.post(
                settings.tinyllama_api_url,
                json={
                    "model": settings.tinyllama_model,
                    "prompt": prompt,
                    "stream": False,
                    "options": {
                        "temperature": temperature,
                        "num_predict": max_tokens,
                    },
                },
            )
            response.raise_for_status()
            result = response.json()
            
            if "response" in result and result.get("done", False):
                return result["response"].strip()
            
            raise ValueError("Empty response from Ollama")
    
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Story generation failed: {str(e)}"
        )


async def generate_welcome_summary(questionnaire: ProfileCreate) -> str:
    """
    Generate a personalized welcome summary using Llama3.1:8b.
    
    This function creates an engaging explorer identity summary based on
    the user's questionnaire answers (US-04).
    
    Uses few-shot prompting with Llama3.1 chat template for consistent,
    high-quality output.
    
    Parameters
    ----------
    questionnaire : ProfileCreate
        User's questionnaire answers (fitness, type, narrative)
    
    Returns
    -------
    str
        A personalized welcome message (80-100 words)
    
    Raises
    ------
    httpx.HTTPError
        If Ollama API call fails
    httpx.TimeoutException
        If Ollama API times out
    """
    # Build adventure types list for the prompt
    adventure_types_str = ", ".join(questionnaire.type) if questionnaire.type else "exploration"
    
    # Construct prompt using Llama3.1 chat template with few-shot examples
    prompt = f"""<|begin_of_text|><|start_header_id|>system<|end_header_id|>

You are the TrailSaga AI Guide. Generate a personalized, engaging welcome message for a new user.

Guidelines:
- Length: 80-100 words
- Tone: Warm, encouraging, and adventurous
- Focus on: fitness level, adventure preferences, narrative style
- Do NOT: invent character names, describe physical appearance, use generic phrases
- Start with a creative explorer title that matches their profile

Output only the welcome message, no additional text.<|eot_id|><|start_header_id|>user<|end_header_id|>

Profile:
- Fitness: Beginner
- Type: family-fun
- Narrative: playful<|eot_id|><|start_header_id|>assistant<|end_header_id|>

Welcome, Joyful Explorer! It is wonderful to have you here. Since you are just starting your journey and enjoy family-friendly fun, TrailSaga has prepared a delightful collection of easygoing and playful adventures just for you. Expect to find charming theme trails where learning and games go hand in hand. We will keep the pace relaxed so you can fully enjoy the smiles of your loved ones. Let's turn every small step into a happy memory!<|eot_id|><|start_header_id|>user<|end_header_id|>

Profile:
- Fitness: Advanced
- Type: hiking, natural-scenery
- Narrative: mystery<|eot_id|><|start_header_id|>assistant<|end_header_id|>

Greetings, Seeker of the Unknown! Your impressive fitness level tells us you are ready to conquer steep paths and deep forests. Because you are drawn to natural scenery and mystery, we have curated routes that lead not just to breathtaking views, but to ancient secrets hidden in the landscape. Prepare for challenging hikes where every turn might reveal a forgotten legend or a hidden ruin. The wild is calling, and it has a puzzle waiting for you to solve.<|eot_id|><|start_header_id|>user<|end_header_id|>

Profile:
- Fitness: Intermediate
- Type: history-culture, urban-exploration
- Narrative: adventure<|eot_id|><|start_header_id|>assistant<|end_header_id|>

Welcome, Urban Adventurer! Your solid fitness foundation makes you perfectly suited for exploring the stories hidden within city streets and historical landmarks. We've selected routes that blend physical challenge with cultural discovery, taking you through architectural marvels, forgotten alleyways, and vibrant neighborhoods. Each path is a chapter in a larger adventure, where past and present intertwine. Get ready to uncover tales that most visitors never see, one stride at a time.<|eot_id|><|start_header_id|>user<|end_header_id|>

Profile:
- Fitness: {questionnaire.fitness}
- Type: {adventure_types_str}
- Narrative: {questionnaire.narrative}<|eot_id|><|start_header_id|>assistant<|end_header_id|>

"""

    try:
        response = await call_ollama(
            prompt=prompt,
            max_tokens=150,
            temperature=0.7  # Balanced creativity and consistency
        )
        
        # Clean up response
        generated_text = response.strip()
        
        # Remove any markdown or extra formatting
        if generated_text.startswith("**") or generated_text.startswith("#"):
            lines = generated_text.split('\n')
            generated_text = ' '.join(line.strip('*#').strip() for line in lines if line.strip())
        
        if generated_text:
            return generated_text
        
        raise ValueError("Empty response from Ollama")
    
    except Exception as e:
        # Re-raise to allow caller to handle with fallback
        raise e


async def generate_post_run_summary(
    route_title: str,
    route_length_km: float,
    quests_completed: int,
    total_quests: int,
    user_level: int,
) -> str:
    """
    Generate a post-run summary and next challenge suggestion using Llama3.1:8b (US-13).
    
    Creates motivating, personalized feedback based on user's performance
    with actionable suggestions for next adventures.
    
    Parameters
    ----------
    route_title : str
        Completed route name
    route_length_km : float
        Route length in kilometers
    quests_completed : int
        Number of quests completed
    total_quests : int
        Total number of quests
    user_level : int
        User's current level
    
    Returns
    -------
    str
        Personalized summary and suggestions (60-80 words)
    
    Raises
    ------
    httpx.HTTPError
        If Ollama API call fails
    """
    quest_completion_rate = (quests_completed / total_quests * 100) if total_quests > 0 else 0
    
    # Construct prompt using Llama3.1 chat template with few-shot examples
    prompt = f"""<|begin_of_text|><|start_header_id|>system<|end_header_id|>

You are the TrailSaga Achievement Generator. Create a motivating summary for a completed adventure.

Guidelines:
- Length: 60-80 words
- Tone: Encouraging, celebratory, forward-looking
- Include: specific achievements, recognition of effort, next challenge suggestion
- Be specific to their performance and level

Output only the summary, no additional text.<|eot_id|><|start_header_id|>user<|end_header_id|>

Route: Mountain Vista Trail
Distance: 12.5 km
Quests: 3/4 (75%)
Level: 5<|eot_id|><|start_header_id|>assistant<|end_header_id|>

Congratulations on conquering the Mountain Vista Trail! You pushed through 12.5 kilometers of challenging terrain and completed most of your quests. Your determination is truly impressive. You're ready for even greater challenges now. Why not try a route with more elevation gain next time?<|eot_id|><|start_header_id|>user<|end_header_id|>

Route: River Loop Discovery
Distance: 5.2 km
Quests: 5/5 (100%)
Level: 3<|eot_id|><|start_header_id|>assistant<|end_header_id|>

Perfect completion of the River Loop Discovery! You completed all five quests and covered every meter with focus and enthusiasm. This flawless performance shows you're mastering the fundamentals beautifully. Level 3 suits you well, but don't be surprised if you're ready for intermediate trails soon. Consider exploring urban heritage routes next.<|eot_id|><|start_header_id|>user<|end_header_id|>

Route: {route_title}
Distance: {route_length_km} km
Quests: {quests_completed}/{total_quests} ({quest_completion_rate:.0f}%)
Level: {user_level}<|eot_id|><|start_header_id|>assistant<|end_header_id|>

"""

    try:
        response = await call_ollama(
            prompt=prompt,
            max_tokens=150,
            temperature=0.75  # Balanced for consistency and variety
        )
        
        generated_text = response.strip()
        if generated_text:
            return generated_text
        
        raise ValueError("Empty response from Ollama")
    
    except Exception as e:
        raise e

