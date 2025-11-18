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
    
    # Construct the prompt using ChatML format with few-shot examples
    prompt = f"""<|system|>
You are the TrailSaga AI Guide. Your task is to generate a personalized welcome message for a new user based on their profile.
The message must be around 80-100 words.
Do not invent characters (like "FiNT"). Do not describe physical appearance.
Focus on their fitness level, preferred adventure types, and narrative style.
</s>
<|user|>
Fitness: Beginner
Type: family-fun
Narrative: playful
</s>
<|assistant|>
Welcome, Joyful Explorer! It is wonderful to have you here. Since you are just starting your journey and enjoy family-friendly fun, TrailSaga has prepared a delightful collection of easygoing and playful adventures just for you. Expect to find charming theme trails where learning and games go hand in hand. We will keep the pace relaxed so you can fully enjoy the smiles of your loved ones. Let's turn every small step into a happy memory!
</s>
<|user|>
Fitness: Advanced
Type: hiking, natural-scenery
Narrative: mystery
</s>
<|assistant|>
Greetings, Seeker of the Unknown! Your impressive fitness level tells us you are ready to conquer steep paths and deep forests. Because you are drawn to natural scenery and mystery, we have curated routes that lead not just to breathtaking views, but to ancient secrets hidden in the landscape. Prepare for challenging hikes where every turn might reveal a forgotten legend or a hidden ruin. The wild is calling, and it has a puzzle waiting for you to solve.
</s>
<|user|>
Fitness: {questionnaire.fitness}
Type: {adventure_types_str}
Narrative: {questionnaire.narrative}
</s>
<|assistant|>"""


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
                        "temperature": 0.6,
                        "top_p": 1.1,
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
        "adventure": "epic and heroic",
        "mystery": "mysterious and suspenseful",
        "playful": "lighthearted and fun",
    }
    style_desc = style_mapping.get(narrative_style, style_mapping["adventure"])
    
    # Construct prompt for route story generation
    prompt = f"""<|system|>
You are the TrailSaga Story Generator. Create an engaging prologue for an outdoor route.
Format: First line = Title (max 10 words), then 2-3 short paragraphs (100-150 words total).
Create atmosphere. Be {style_desc}.
</s>
<|user|>
Route: Black Forest Trail
Location: Germany
Distance: 8.5 km
Difficulty: 2/6
</s>
<|assistant|>
Title: Secrets of the Ancient Pines

The morning mist clings to the towering trees of the Black Forest. Local legends speak of travelers who walked these paths centuries ago, searching for something hidden in the shadows. Today, you stand at the threshold of your own mystery.

As you step onto the trail, the forest seems to watch and wait. Every twisted root and moss-covered stone holds a story. What secrets will you uncover in the emerald depths?
</s>
<|user|>
Route: {route_title}
Location: {route_location}
Distance: {route_length_km} km
Difficulty: {route_difficulty}/6
</s>
<|assistant|>"""

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
    
    # Construct prompt for post-run summary
    prompt = f"""<|system|>
You are the TrailSaga Achievement Generator. Create a motivating summary for a completed route.
Format: 3-5 sentences. Be encouraging and suggest next steps.
</s>
<|user|>
Route: Mountain Vista Trail
Distance: 12.5 km
Quests: 3/4 (75%)
Level: 5
</s>
<|assistant|>
Congratulations on conquering the Mountain Vista Trail! You pushed through 12.5 kilometers of challenging terrain and completed most of your quests. Your determination is truly impressive. You're ready for even greater challenges now. Why not try a route with more elevation gain next time?
</s>
<|user|>
Route: {route_title}
Distance: {route_length_km} km
Quests: {quests_completed}/{total_quests} ({quest_completion_rate:.0f}%)
Level: {user_level}
</s>
<|assistant|>"""

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

