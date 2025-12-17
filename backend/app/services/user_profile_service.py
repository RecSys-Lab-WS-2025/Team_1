"""
User profile service for questionnaire translation and user vector management.

This service translates user questionnaire answers into structured user_vector
that can be used by the recommendation algorithm (CBF + Adaptive Re-ranking).
"""
from typing import Any

from app.api.schemas import ProfileCreate


# Fitness level → Difficulty range and distance constraints
FITNESS_MAPPING = {
    "beginner": {
        "difficulty_range": [0, 1],
        "max_distance_km": 8.0,
        "min_distance_km": 0.0,
    },
    "intermediate": {
        "difficulty_range": [1, 2],
        "max_distance_km": 20.0,
        "min_distance_km": 5.0,
    },
    "advanced": {
        "difficulty_range": [2, 3],
        "max_distance_km": 50.0,
        "min_distance_km": 10.0,
    },
}

# Adventure type → Tags (based on actual Outdooractive tags)
ADVENTURE_TYPE_TO_TAGS = {
    "history-culture": ["culture", "heritage", "architecture", "museum"],
    "natural-scenery": ["flora", "fauna", "panorama", "scenic", "geology"],
    "family-fun": ["suitableforfamilies", "playground", "dining", "loopTour"],
}

# Import narrative style prompts from genai_service for consistency
from app.services.genai_service import NARRATIVE_STYLE_PROMPTS


def translate_questionnaire_to_vector(questionnaire: ProfileCreate) -> dict[str, Any]:
    """
    Translate questionnaire answers to a structured user_vector for recommendations.
    
    Parameters
    ----------
    questionnaire : ProfileCreate
        User's questionnaire answers with fields: fitness, type (list), narrative
    
    Returns
    -------
    dict[str, Any]
        User vector containing:
        - difficulty_range: List of acceptable difficulty levels (0-6)
        - max_distance_km: Maximum acceptable distance
        - min_distance_km: Minimum acceptable distance
        - preferred_tags: List of preferred route tags
        - narrative_prompt_style: Style descriptor for LLM story generation
        - fitness_level: Original fitness level string
    """
    # 1. Map fitness level to difficulty and distance constraints
    fitness_config = FITNESS_MAPPING.get(
        questionnaire.fitness,
        FITNESS_MAPPING["beginner"]  # Default to beginner if unknown
    )
    
    # 2. Map adventure types to preferred tags
    preferred_tags: list[str] = []
    for adventure_type in questionnaire.type:
        tags = ADVENTURE_TYPE_TO_TAGS.get(adventure_type, [])
        preferred_tags.extend(tags)
    
    # Remove duplicates while preserving order
    preferred_tags = list(dict.fromkeys(preferred_tags))
    
    # 3. Map narrative style to LLM prompt descriptor
    narrative_prompt_style = NARRATIVE_STYLE_PROMPTS.get(
        questionnaire.narrative,
        NARRATIVE_STYLE_PROMPTS["adventure"]  # Default to adventure
    )
    
    # 4. Construct the user_vector
    user_vector = {
        "difficulty_range": fitness_config["difficulty_range"],
        "max_distance_km": fitness_config["max_distance_km"],
        "min_distance_km": fitness_config["min_distance_km"],
        "preferred_tags": preferred_tags,
        "narrative_prompt_style": narrative_prompt_style,
        "fitness_level": questionnaire.fitness,
    }
    
    return user_vector


def generate_fallback_welcome(questionnaire: ProfileCreate) -> str:
    """
    Generate a rule-based welcome message when GenAI is unavailable.
    
    This serves as a fallback when Ollama or other LLM services are unavailable.
    
    Parameters
    ----------
    questionnaire : ProfileCreate
        User's questionnaire answers
    
    Returns
    -------
    str
        A personalized welcome message
    """
    # Determine explorer title based on fitness and narrative
    explorer_titles = {
        "beginner": {
            "adventure": "Novice Explorer",
            "mystery": "Urban Detective",
            "playful": "Joyful Wanderer",
        },
        "intermediate": {
            "adventure": "Skilled Wanderer",
            "mystery": "Secret Seeker",
            "playful": "Energetic Explorer",
        },
        "advanced": {
            "adventure": "Elite Pathfinder",
            "mystery": "Legendary Adventurer",
            "playful": "Peak Conqueror",
        },
    }
    
    # Get the title
    fitness_titles = explorer_titles.get(questionnaire.fitness, explorer_titles["beginner"])
    title = fitness_titles.get(questionnaire.narrative, fitness_titles["adventure"])
    
    # Map adventure types to English descriptions
    adventure_type_names = {
        "history-culture": "history and culture",
        "natural-scenery": "natural scenery",
        "family-fun": "family-friendly adventures",
    }
    
    # Build adventure types description
    adventure_names = [
        adventure_type_names.get(t, t) for t in questionnaire.type
    ]
    adventure_description = " and ".join(adventure_names) if adventure_names else "exploration"
    
    # Map narrative to style description
    narrative_styles = {
        "adventure": "epic adventures",
        "mystery": "mysterious discoveries",
        "playful": "playful journeys",
    }
    narrative_style = narrative_styles.get(questionnaire.narrative, "adventures")
    
    # Construct the welcome message
    welcome_message = (
        f"Welcome, {title}!\n\n"
        f"You're passionate about {adventure_description}. "
        f"We've prepared a collection of {narrative_style} tailored just for you!\n\n"
        f"Ready to begin your legendary saga? 🤍"
    )
    
    return welcome_message

