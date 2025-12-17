"""
GenAI service for generating personalized narratives and summaries using Llama3.1:8b.

This service encapsulates all LLM interactions including:
- Welcome summaries (US-04)
- Route stories (US-06)
- Mini-quest generation (US-10)
- Post-run summaries (US-13)
- Pixel art SVG generation for souvenirs

All prompts use Llama3.1 chat template format with proper prompt engineering:
- Few-shot examples for consistency
- Clear system instructions
- Explicit length constraints
- Structured output where needed
"""
import httpx
import time
from typing import Optional
from datetime import datetime
from fastapi import HTTPException

from app.api.schemas import ProfileCreate
from app.settings import get_settings
from app.logger import get_logger, log_api_call

logger = get_logger(__name__)


# Narrative style → LLM prompt style descriptors
# These detailed instructions ensure the LLM produces consistent, style-appropriate output
# Used across all GenAI services (welcome summaries, story generation, etc.)
NARRATIVE_STYLE_PROMPTS = {
    "adventure": (
        "Write in an epic, cinematic tone. Emphasize a sense of grand journey, "
        "meaningful challenges, and heroic progression. Use language that makes the "
        "user feel like the protagonist of a larger saga, with each route as a new "
        "chapter in their legend. Keep the tone inspiring, confident, and slightly "
        "dramatic, but still clear and easy to read."
    ),
    "mystery": (
        "Write in a mysterious, slightly suspenseful tone. Emphasize hidden corners, "
        "quiet details, and secrets waiting to be uncovered. Use language that suggests "
        "clues, layers, and discoveries rather than stating everything directly. "
        "The tone should be intriguing and immersive, inviting the user to look closer "
        "and follow the trail of hints."
    ),
    "playful": (
        "Write in a light-hearted, playful tone. Emphasize fun, curiosity, and small "
        "joyful moments rather than serious challenges. Use friendly, energetic language "
        "and a touch of humor, as if you are a cheerful guide talking to a friend. "
        "The tone should feel casual, encouraging, and welcoming, suitable for users "
        "who want relaxed adventures."
    ),
}


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
    start_time = time.time()
    
    logger.debug(f"🤖 Calling Ollama API: model={settings.ollama_model}, max_tokens={max_tokens}, temperature={temperature}")
    logger.debug(f"📝 Prompt length: {len(prompt)} characters")
    
    try:
        async with httpx.AsyncClient(timeout=settings.ollama_timeout) as client:
            response = await client.post(
                settings.ollama_api_url,
                json={
                    "model": settings.ollama_model,
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
            
            duration_ms = (time.time() - start_time) * 1000
            
            if "response" in result and result.get("done", False):
                response_text = result["response"].strip()
                logger.debug(f"✅ Ollama API call succeeded: response_length={len(response_text)} chars, duration={duration_ms:.2f}ms")
            duration_ms = (time.time() - start_time) * 1000
            
            if "response" in result and result.get("done", False):
                response_text = result["response"].strip()
                logger.debug(f"✅ Ollama API call succeeded: response_length={len(response_text)} chars, duration={duration_ms:.2f}ms")
                log_api_call(
                    logger,
                    "Ollama",
                    settings.ollama_api_url,
                    method="POST",
                    duration_ms=duration_ms,
                    success=True,
                    model=settings.ollama_model,
                    response_length=len(response_text)
                )
                return response_text
            
            logger.error("❌ Ollama API returned empty response")
            raise ValueError("Empty response from Ollama")
    
    except httpx.HTTPStatusError as e:
        duration_ms = (time.time() - start_time) * 1000
        logger.error(f"❌ Ollama API HTTP error: status={e.response.status_code}, detail={e.response.text}")
        log_api_call(
            logger,
            "Ollama",
            settings.ollama_api_url,
            method="POST",
            duration_ms=duration_ms,
            success=False,
            status_code=e.response.status_code
        )
        raise HTTPException(
            status_code=e.response.status_code,
            detail=f"Ollama API error: {str(e)}"
        )
    except httpx.TimeoutException as e:
        duration_ms = (time.time() - start_time) * 1000
        logger.error(f"❌ Ollama API timeout: timeout={settings.ollama_timeout}s, duration={duration_ms:.2f}ms")
        log_api_call(
            logger,
            "Ollama",
            settings.ollama_api_url,
            method="POST",
            duration_ms=duration_ms,
            success=False,
            error="timeout"
        )
        raise HTTPException(
            status_code=504,
            detail=f"Ollama API timeout after {settings.ollama_timeout}s"
        )
    except Exception as e:
        duration_ms = (time.time() - start_time) * 1000
        logger.error(f"❌ Ollama API call failed: {type(e).__name__}: {str(e)}", exc_info=True)
        log_api_call(
            logger,
            "Ollama",
            settings.ollama_api_url,
            method="POST",
            duration_ms=duration_ms,
            success=False,
            error=type(e).__name__
        )
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
    
    # Get detailed narrative style instructions
    narrative_hint = NARRATIVE_STYLE_PROMPTS.get(
        questionnaire.narrative,
        "Use a neutral, friendly narrative tone."
    )
    
    # Construct prompt using Llama3.1 chat template with few-shot examples
    prompt = f"""<|begin_of_text|><|start_header_id|>system<|end_header_id|>
    
You are the TrailSaga – Hogwarts Expedition Series AI Guide. Generate a personalized, engaging welcome message for a new user.

Guidelines:
- Length: 80-100 words
- Tone: Warm, encouraging, and adventurous
- Focus on: fitness level, adventure preferences, narrative style
- Do NOT: invent character names, describe physical appearance, use generic phrases
- Start with a creative explorer title that matches their profile

The narrative style should follow this description: "{narrative_hint}"

Output only the welcome message, no additional text.<|eot_id|><|start_header_id|>user<|end_header_id|>

Profile:
- Fitness: Beginner
- Type: family-fun
- Narrative: playful<|eot_id|><|start_header_id|>assistant<|end_header_id|>
        
Welcome, Joyful Explorer! It is wonderful to have you here. Since you are just starting your journey and enjoy family-friendly fun, TrailSaga – Hogwarts Expedition Series has prepared a delightful collection of easygoing and playful adventures just for you. Expect to find charming theme trails where learning and games go hand in hand. We will keep the pace relaxed so you can fully enjoy the smiles of your loved ones. Let's turn every small step into a happy memory!<|eot_id|><|start_header_id|>user<|end_header_id|>

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
            max_tokens=170,
            temperature=0.6  # Balanced creativity and consistency
        )
        
        # Clean up response
        generated_text = response.strip()
        
        # Remove any markdown or extra formatting
        if generated_text.startswith("**") or generated_text.startswith("#"):
            lines = generated_text.split('\n')
            generated_text = ' '.join(line.strip('*#').strip() for line in lines if line.strip())
        
        if generated_text:
            # Print LLM generated content to console
            print("\n" + "="*80)
            print("✨ LLM GENERATED: Welcome Summary")
            print("="*80)
            print(f"📋 Profile: Fitness={questionnaire.fitness}, Type={questionnaire.type}, Narrative={questionnaire.narrative}")
            print(f"🤖 Model: {get_settings().ollama_model}")
            print("-"*80)
            print(generated_text)
            print("="*80 + "\n")
            
            # Log to UI
            from app.llm_logger import log_llm_output
            log_llm_output(
                message_type="welcome",
                title="✨ Welcome Summary Generated",
                content=generated_text,
                metadata={
                    "fitness": questionnaire.fitness,
                    "type": questionnaire.type,
                    "narrative": questionnaire.narrative,
                    "model": get_settings().ollama_model
                }
            )
            
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
    
You are the TrailSaga – Hogwarts Expedition Series Achievement Generator. Create a motivating summary for a completed adventure.

Guidelines:
- Language: English only (do not use any other language)
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
            # Print LLM generated content to console
            print("\n" + "="*80)
            print("✨ LLM GENERATED: Post-Run Summary")
            print("="*80)
            print(f"🗺️ Route: {route_title}")
            print(f"📏 Distance: {route_length_km} km")
            print(f"🏆 Quests: {quests_completed}/{total_quests} ({quest_completion_rate:.0f}%)")
            print(f"📈 Level: {user_level}")
            print("-"*80)
            print(generated_text)
            print("="*80 + "\n")
            
            # Log to UI
            from app.llm_logger import log_llm_output
            log_llm_output(
                message_type="post_run",
                title=f"🏁 Post-Run Summary: {route_title}",
                content=generated_text,
                metadata={
                    "route_title": route_title,
                    "distance_km": route_length_km,
                    "quests_completed": quests_completed,
                    "total_quests": total_quests,
                    "user_level": user_level
                }
            )
            
            return generated_text
        
        raise ValueError("Empty response from Ollama")
    
    except Exception as e:
        raise e


async def generate_pixel_art_svg(
    route_title: str,
    route_location: Optional[str],
    completed_at: datetime,
    xp_gained: int,
    distance_km: float,
    difficulty: Optional[int] = None,
) -> str:
    """
    Generate a pixel art style SVG image using pre-designed templates.
    
    Uses a template-based system with 10 different Harry Potter themed designs.
    Randomly selects a template and fills it with route completion data.
    
    Parameters
    ----------
    route_title : str
        Name of the completed route
    route_location : Optional[str]
        Location of the route
    completed_at : datetime
        Completion timestamp
    xp_gained : int
        Total XP earned
    distance_km : float
        Route distance in kilometers
    difficulty : Optional[int]
        Route difficulty (0-3 scale)
    
    Returns
    -------
    str
        SVG code as a string (pixel art style)
    """
    # Use template-based system instead of LLM generation
    from app.services.svg_templates import generate_souvenir_svg
    
    # Map difficulty
    difficulty_map = {0: "Easy", 1: "Moderate", 2: "Difficult", 3: "Expert"}
    difficulty_str = difficulty_map.get(difficulty, "Unknown") if difficulty is not None else "Unknown"
    
    # Generate SVG using template system
    generated_svg = generate_souvenir_svg(
        route_title=route_title,
        route_location=route_location,
        completed_at=completed_at,
        xp_gained=xp_gained,
        distance_km=distance_km,
        difficulty=difficulty_str
    )
    
    # Format for logging
    date_str = completed_at.strftime("%Y-%m-%d")
    time_str = completed_at.strftime("%H:%M")
    location_str = route_location if route_location else "Unknown Location"
    
    # Print generated content to console
    print("\n" + "="*80)
    print("🎨 TEMPLATE GENERATED: Pixel Art SVG")
    print("="*80)
    print(f"🗺️ Route: {route_title}")
    print(f"📍 Location: {location_str}")
    print(f"📅 Completed: {date_str} at {time_str}")
    print(f"⭐ XP: {xp_gained}")
    print(f"📏 Distance: {distance_km:.1f} km")
    print(f"🎯 Difficulty: {difficulty_str}")
    print("-"*80)
    print(f"SVG Length: {len(generated_svg)} characters")
    print("="*80 + "\n")
    
    # Log to UI
    from app.llm_logger import log_llm_output
    log_llm_output(
        message_type="pixel_art",
        title=f"🎨 Pixel Art Generated: {route_title}",
        content=f"Generated {len(generated_svg)} character SVG (Template-based)",
        metadata={
            "route_title": route_title,
            "location": location_str,
            "completed_at": date_str,
            "xp_gained": xp_gained,
            "distance_km": distance_km,
            "difficulty": difficulty_str,
            "method": "template"
        }
    )
    
    return generated_svg


def _create_fallback_pixel_svg(
    route_title: str,
    location: str,
    date_str: str,
    time_str: str,
    xp_gained: int,
    distance_km: float,
    difficulty_str: str,
) -> str:
    """
    Create a cute fallback pixel art SVG if LLM generation fails.
    """
    # Truncate title if too long
    title_display = route_title[:18] + "..." if len(route_title) > 18 else route_title
    
    return f'''<svg viewBox="0 0 400 300" xmlns="http://www.w3.org/2000/svg" style="font-family: 'Comic Sans MS', monospace; font-size: 12px;">
  <!-- Cute Gradient Background -->
  <defs>
    <linearGradient id="bgGradient" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" style="stop-color:#FFE4E1;stop-opacity:1" />
      <stop offset="100%" style="stop-color:#E6E6FA;stop-opacity:1" />
    </linearGradient>
  </defs>
  <rect width="400" height="300" fill="url(#bgGradient)"/>
  
  <!-- Cute Rounded Border -->
  <rect x="15" y="15" width="370" height="270" rx="15" fill="none" stroke="#FFB6C1" stroke-width="5"/>
  <rect x="20" y="20" width="360" height="260" rx="12" fill="none" stroke="#98FB98" stroke-width="3"/>
  
  <!-- Cute Mountain with Happy Face (Kawaii Style) -->
  <polygon points="200,70 150,130 250,130" fill="#87CEEB" stroke="#FFB6C1" stroke-width="3"/>
  <polygon points="200,90 170,130 230,130" fill="#98FB98"/>
  <!-- Happy face on mountain -->
  <circle cx="185" cy="100" r="4" fill="#000"/>
  <circle cx="215" cy="100" r="4" fill="#000"/>
  <path d="M 185 110 Q 200 118 215 110" stroke="#000" stroke-width="2" fill="none"/>
  
  <!-- Cute Sun -->
  <circle cx="320" cy="50" r="20" fill="#FFE4B5" stroke="#FFB6C1" stroke-width="2"/>
  <circle cx="320" cy="50" r="15" fill="#FFD700"/>
  <!-- Sun rays -->
  <line x1="320" y1="25" x2="320" y2="20" stroke="#FFD700" stroke-width="3" stroke-linecap="round"/>
  <line x1="345" y1="50" x2="350" y2="50" stroke="#FFD700" stroke-width="3" stroke-linecap="round"/>
  <line x1="320" y1="75" x2="320" y2="80" stroke="#FFD700" stroke-width="3" stroke-linecap="round"/>
  <line x1="295" y1="50" x2="290" y2="50" stroke="#FFD700" stroke-width="3" stroke-linecap="round"/>
  
  <!-- Sparkles around title -->
  <text x="200" y="165" text-anchor="middle" fill="#FF69B4" font-size="18" font-weight="bold">✨ {title_display} ✨</text>
  
  <!-- Location with cute icon -->
  <circle cx="170" cy="185" r="3" fill="#FFB6C1"/>
  <text x="180" y="190" fill="#6A5ACD" font-size="11" font-weight="bold">📍 {location[:22]}</text>
  
  <!-- Cute Stats Grid with rounded corners -->
  <!-- XP Badge -->
  <rect x="40" y="210" width="90" height="60" rx="8" fill="#FFE4E1" stroke="#FFB6C1" stroke-width="3"/>
  <text x="85" y="235" text-anchor="middle" fill="#FF69B4" font-size="16" font-weight="bold">⭐ {xp_gained}</text>
  <text x="85" y="250" text-anchor="middle" fill="#6A5ACD" font-size="10" font-weight="bold">XP</text>
  <!-- Sparkle decoration -->
  <text x="60" y="230" fill="#FFD700" font-size="10">✨</text>
  <text x="110" y="235" fill="#FFD700" font-size="8">⭐</text>
  
  <!-- Distance Badge -->
  <rect x="150" y="210" width="90" height="60" rx="8" fill="#E6F3FF" stroke="#87CEEB" stroke-width="3"/>
  <text x="195" y="235" text-anchor="middle" fill="#4169E1" font-size="16" font-weight="bold">👣 {distance_km:.1f}</text>
  <text x="195" y="250" text-anchor="middle" fill="#6A5ACD" font-size="10" font-weight="bold">KM</text>
  
  <!-- Difficulty Badge -->
  <rect x="260" y="210" width="90" height="60" rx="8" fill="#F0FFF0" stroke="#98FB98" stroke-width="3"/>
  <text x="305" y="235" text-anchor="middle" fill="#228B22" font-size="13" font-weight="bold">🎯 {difficulty_str}</text>
  <text x="305" y="250" text-anchor="middle" fill="#6A5ACD" font-size="10" font-weight="bold">LEVEL</text>
  
  <!-- Date/Time with cute frame -->
  <rect x="100" y="275" width="200" height="20" rx="10" fill="#FFF8DC" stroke="#FFB6C1" stroke-width="2"/>
  <text x="200" y="288" text-anchor="middle" fill="#6A5ACD" font-size="10" font-weight="bold">📅 {date_str} ⏰ {time_str}</text>
  
  <!-- Cute Corner Decorations (Hearts and Stars) -->
  <text x="30" y="35" fill="#FF69B4" font-size="16">💖</text>
  <text x="360" y="35" fill="#98FB98" font-size="16">⭐</text>
  <text x="30" y="280" fill="#FFD700" font-size="16">✨</text>
  <text x="360" y="280" fill="#FFB6C1" font-size="16">💕</text>
  
  <!-- Small decorative elements -->
  <circle cx="50" cy="100" r="3" fill="#FFB6C1" opacity="0.6"/>
  <circle cx="350" cy="120" r="3" fill="#98FB98" opacity="0.6"/>
  <circle cx="50" cy="200" r="3" fill="#FFD700" opacity="0.6"/>
  <circle cx="350" cy="180" r="3" fill="#87CEEB" opacity="0.6"/>
</svg>'''

