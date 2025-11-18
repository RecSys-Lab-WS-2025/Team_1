"""
GenAI service for generating personalized narratives and summaries using TinyLlama.

This service encapsulates all LLM interactions including:
- Welcome summaries (US-04)
- Route stories (US-06)
- Mini-quest generation (US-10)
- Post-run summaries (US-13)
"""
import httpx
from typing import Optional

from app.api.schemas import ProfileCreate
from app.settings import get_settings


async def generate_welcome_summary(questionnaire: ProfileCreate) -> str:
    """
    Generate a personalized welcome summary using TinyLlama.
    
    This function creates a 2-3 sentence explorer identity summary based on
    the user's questionnaire answers (US-04).
    
    Parameters
    ----------
    questionnaire : ProfileCreate
        User's questionnaire answers
    
    Returns
    -------
    str
        A personalized welcome message with an explorer title
    
    Raises
    ------
    httpx.HTTPError
        If TinyLlama API call fails
    httpx.TimeoutException
        If TinyLlama API times out
    """
    settings = get_settings()
    
    # Build adventure types list for the prompt
    adventure_types_str = ", ".join(questionnaire.type) if questionnaire.type else "exploration"
    
    # Construct the prompt
    prompt = f"""Generate a 2-3 sentence explorer identity summary based on the user's questionnaire answers:

Fitness Level: {questionnaire.fitness}
Preferred Adventure Types: {adventure_types_str}
Narrative Style: {questionnaire.narrative}

Requirements:
1. Give the user a cool "explorer title" (e.g., "City Explorer", "Mountain Challenger")
2. Briefly describe their characteristics and suitable adventure types
3. Use an inspiring and immersive tone
4. Output in English, 2-3 sentences total

Explorer Summary:"""

    # Call Ollama API with TinyLlama
    try:
        async with httpx.AsyncClient(timeout=settings.tinyllama_timeout) as client:
            response = await client.post(
                settings.tinyllama_api_url,
                json={
                    "model": settings.tinyllama_model,
                    "prompt": prompt,
                    "stream": False,
                    "options": {
                        "temperature": 0.8,
                        "top_p": 0.9,
                        "num_predict": 150,  # max tokens
                    },
                },
            )
            response.raise_for_status()
            
            # Parse Ollama response
            result = response.json()
            
            # Extract generated text from Ollama format
            if "response" in result and result.get("done", False):
                generated_text = result["response"].strip()
                if generated_text:
                    return generated_text
            
            # Fallback if response is empty
            raise ValueError("Empty response from Ollama")
    
    except (httpx.HTTPError, httpx.TimeoutException, ValueError) as e:
        # Re-raise to allow caller to handle with fallback
        raise e


async def generate_route_story(
    route_title: str,
    route_location: str,
    route_length_km: float,
    route_difficulty: int,
    narrative_style: str,
) -> tuple[str, str]:
    """
    Generate a prologue story for a route using TinyLlama (US-06).
    
    Parameters
    ----------
    route_title : str
        Route name
    route_location : str
        Route location
    route_length_km : float
        Route length in kilometers
    route_difficulty : int
        Difficulty level (0-6)
    narrative_style : str
        User's preferred narrative style
    
    Returns
    -------
    tuple[str, str]
        (prologue_title, prologue_body)
    
    Raises
    ------
    httpx.HTTPError
        If TinyLlama API call fails
    """
    settings = get_settings()
    
    # Map narrative style to English descriptions
    style_mapping = {
        "adventure": "epic adventure style emphasizing heroic journeys and challenges",
        "mystery": "mysterious suspense style emphasizing unsolved mysteries and hidden clues",
        "playful": "lighthearted and humorous style suitable for family and leisure",
    }
    style_desc = style_mapping.get(narrative_style, style_mapping["adventure"])
    
    prompt = f"""Create a short prologue story for the following outdoor route:

Route Name: {route_title}
Location: {route_location}
Distance: {route_length_km} km
Difficulty: {route_difficulty}/6
Style: {style_desc}

Requirements:
1. First provide an engaging story title (within 10 words)
2. Then write a 2-3 paragraph opening story (100-150 words total)
3. Create atmosphere and make users feel like they're "embarking on a quest"
4. Output in English

Format:
Title: [your title]
Body: [your story]"""

    try:
        async with httpx.AsyncClient(timeout=settings.tinyllama_timeout) as client:
            response = await client.post(
                settings.tinyllama_api_url,
                json={
                    "model": settings.tinyllama_model,
                    "prompt": prompt,
                    "stream": False,
                    "options": {
                        "temperature": 0.85,
                        "top_p": 0.9,
                        "num_predict": 300,
                    },
                },
            )
            response.raise_for_status()
            
            result = response.json()
            
            if "response" in result and result.get("done", False):
                generated_text = result["response"].strip()
                
                # Parse title and body
                if "Title:" in generated_text and "Body:" in generated_text:
                    parts = generated_text.split("Body:", 1)
                    title = parts[0].replace("Title:", "").strip()
                    body = parts[1].strip()
                    return title, body
                
                # Fallback: use generated text as body
                return "Begin Your Adventure", generated_text
            
            raise ValueError("Empty response from Ollama")
    
    except (httpx.HTTPError, httpx.TimeoutException, ValueError) as e:
        raise e


async def generate_post_run_summary(
    route_title: str,
    route_length_km: float,
    quests_completed: int,
    total_quests: int,
    user_level: int,
) -> str:
    """
    Generate a post-run summary and next challenge suggestion (US-13).
    
    Parameters
    ----------
    route_title : str
        Completed route name
    route_length_km : float
        Route length
    quests_completed : int
        Number of quests completed
    total_quests : int
        Total number of quests
    user_level : int
        User's current level
    
    Returns
    -------
    str
        Personalized summary and suggestions
    
    Raises
    ------
    httpx.HTTPError
        If TinyLlama API call fails
    """
    settings = get_settings()
    
    quest_completion_rate = (quests_completed / total_quests * 100) if total_quests > 0 else 0
    
    prompt = f"""Generate a personalized summary and next challenge suggestion for a completed outdoor route:

Completed Route: {route_title}
Distance: {route_length_km} km
Quests Completed: {quests_completed}/{total_quests} ({quest_completion_rate:.0f}%)
Current Level: {user_level}

Requirements:
1. Summarize the adventure highlights in 3-5 sentences
2. Provide next challenge suggestions (e.g., "Try a slightly longer route next time")
3. Use an encouraging and motivating tone
4. Output in English

Summary:"""

    try:
        async with httpx.AsyncClient(timeout=settings.tinyllama_timeout) as client:
            response = await client.post(
                settings.tinyllama_api_url,
                json={
                    "model": settings.tinyllama_model,
                    "prompt": prompt,
                    "stream": False,
                    "options": {
                        "temperature": 0.8,
                        "top_p": 0.9,
                        "num_predict": 200,
                    },
                },
            )
            response.raise_for_status()
            
            result = response.json()
            
            if "response" in result and result.get("done", False):
                generated_text = result["response"].strip()
                if generated_text:
                    return generated_text
            
            raise ValueError("Empty response from Ollama")
    
    except (httpx.HTTPError, httpx.TimeoutException, ValueError) as e:
        raise e

