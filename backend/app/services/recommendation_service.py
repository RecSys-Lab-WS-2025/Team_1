"""
Recommendation service implementing Content-Based Filtering (CBF).

This service provides route recommendations by matching user preferences
with route attributes using similarity scoring.
"""
import json
import random
from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.entities import Route, DemoProfile, Breakpoint


# Category mapping: custom category → route.category_name values
CATEGORY_MAPPING = {
    "running": ["Jogging", "Trail running"],
    "hiking": ["Theme trail", "Hiking trail"],
    "cycling": ["Cycling", "Mountainbiking", "Long distance cycling"],
}

# Weights for CBF scoring components
SCORE_WEIGHTS = {
    "difficulty": 0.4,
    "distance": 0.3,
    "tags": 0.3,
}


def extract_route_vector(route: Route) -> dict:
    """
    Extract route features into a comparable vector.
    
    Parameters
    ----------
    route : Route
        Route entity from database
    
    Returns
    -------
    dict
        Route vector with difficulty, length_km, and tags
    """
    # Parse tags from JSON
    tags = []
    if route.tags_json:
        try:
            tags = json.loads(route.tags_json)
            if isinstance(tags, list):
                # Flatten if nested or extract tag names
                flat_tags = []
                for tag in tags:
                    if isinstance(tag, str):
                        flat_tags.append(tag.lower())
                    elif isinstance(tag, dict) and "name" in tag:
                        flat_tags.append(tag["name"].lower())
                tags = flat_tags
        except (json.JSONDecodeError, TypeError):
            tags = []
    
    return {
        "difficulty": route.difficulty if route.difficulty is not None else 0,
        "length_km": (route.length_meters / 1000.0) if route.length_meters else 0.0,
        "tags": tags,
    }


def calculate_difficulty_score(user_difficulty_range: list[int], route_difficulty: int) -> float:
    """
    Calculate difficulty match score.
    
    Returns 1.0 if route difficulty is within user's acceptable range, else 0.0.
    
    Parameters
    ----------
    user_difficulty_range : list[int]
        [min_difficulty, max_difficulty] from user profile
    route_difficulty : int
        Route difficulty level (0-6)
    
    Returns
    -------
    float
        Score between 0.0 and 1.0
    """
    if not user_difficulty_range or len(user_difficulty_range) < 2:
        return 0.5  # Neutral score if no preference
    
    min_diff, max_diff = user_difficulty_range[0], user_difficulty_range[1]
    
    if min_diff <= route_difficulty <= max_diff:
        return 1.0
    
    # Calculate distance from range with decay
    if route_difficulty < min_diff:
        distance = min_diff - route_difficulty
    else:
        distance = route_difficulty - max_diff
    
    # Exponential decay: 0.5^distance
    return max(0.0, 0.5 ** distance)


def calculate_distance_score(
    user_min_km: float,
    user_max_km: float,
    route_length_km: float
) -> float:
    """
    Calculate distance match score.
    
    Returns 1.0 if route length is within user's preferred range,
    with exponential decay for distances outside the range.
    
    Parameters
    ----------
    user_min_km : float
        Minimum preferred distance
    user_max_km : float
        Maximum preferred distance
    route_length_km : float
        Route length in kilometers
    
    Returns
    -------
    float
        Score between 0.0 and 1.0
    """
    if route_length_km == 0.0:
        return 0.3  # Low score for missing data
    
    if user_min_km <= route_length_km <= user_max_km:
        return 1.0
    
    # Calculate distance from acceptable range
    if route_length_km < user_min_km:
        distance_ratio = (user_min_km - route_length_km) / user_max_km
    else:
        distance_ratio = (route_length_km - user_max_km) / user_max_km
    
    # Exponential decay based on how far outside the range
    return max(0.0, 0.7 ** distance_ratio)


def calculate_tag_score(user_tags: list[str], route_tags: list[str]) -> float:
    """
    Calculate tag overlap score using Jaccard similarity.
    
    Jaccard similarity = |intersection| / |union|
    
    Parameters
    ----------
    user_tags : list[str]
        User's preferred tags
    route_tags : list[str]
        Route's tags
    
    Returns
    -------
    float
        Score between 0.0 and 1.0
    """
    if not user_tags and not route_tags:
        return 0.5  # Neutral if both empty
    
    if not user_tags or not route_tags:
        return 0.2  # Low score if one is empty
    
    # Convert to sets for set operations
    user_set = set(tag.lower() for tag in user_tags)
    route_set = set(tag.lower() for tag in route_tags)
    
    intersection = user_set & route_set
    union = user_set | route_set
    
    if len(union) == 0:
        return 0.0
    
    return len(intersection) / len(union)


def calculate_cbf_score(user_vector: dict, route_vector: dict) -> float:
    """
    Calculate overall CBF similarity score between user and route.
    
    Parameters
    ----------
    user_vector : dict
        User preference vector with difficulty_range, min/max_distance_km, preferred_tags
    route_vector : dict
        Route feature vector with difficulty, length_km, tags
    
    Returns
    -------
    float
        Overall similarity score between 0.0 and 1.0
    """
    # Calculate component scores
    difficulty_score = calculate_difficulty_score(
        user_vector.get("difficulty_range", [0, 3]),
        route_vector["difficulty"]
    )
    
    distance_score = calculate_distance_score(
        user_vector.get("min_distance_km", 0.0),
        user_vector.get("max_distance_km", 100.0),
        route_vector["length_km"]
    )
    
    tag_score = calculate_tag_score(
        user_vector.get("preferred_tags", []),
        route_vector["tags"]
    )
    
    # Weighted average
    final_score = (
        SCORE_WEIGHTS["difficulty"] * difficulty_score +
        SCORE_WEIGHTS["distance"] * distance_score +
        SCORE_WEIGHTS["tags"] * tag_score
    )
    
    return final_score


async def get_recommended_routes(
    db: AsyncSession,
    profile_id: Optional[int] = None,
    category: Optional[str] = None,
    limit: int = 20
) -> list[Route]:
    """
    Get recommended routes using CBF or random selection.
    
    Parameters
    ----------
    db : AsyncSession
        Database session
    profile_id : Optional[int]
        User profile ID for personalized recommendations. If None, returns random routes.
    category : Optional[str]
        Activity type filter: "running", "hiking", "cycling", or None for all
    limit : int
        Maximum number of routes to return
    
    Returns
    -------
    list[Route]
        List of recommended routes, sorted by relevance (if personalized) or random
    """
    # Build base query with eager loading of relationships
    query = select(Route).options(
        selectinload(Route.breakpoints).selectinload(Breakpoint.mini_quests)
    )
    
    # Apply category filter if specified
    if category and category in CATEGORY_MAPPING:
        category_names = CATEGORY_MAPPING[category]
        query = query.where(Route.category_name.in_(category_names))
    
    # Execute query
    result = await db.execute(query)
    routes = list(result.scalars().all())
    
    # If no profile_id, return random routes
    if profile_id is None:
        random.shuffle(routes)
        return routes[:limit]
    
    # Get user profile and vector
    profile = await db.get(DemoProfile, profile_id)
    if not profile or not profile.user_vector_json:
        # Fallback to random if profile not found or no vector
        random.shuffle(routes)
        return routes[:limit]
    
    try:
        user_vector = json.loads(profile.user_vector_json)
    except (json.JSONDecodeError, TypeError):
        # Fallback to random if user_vector is invalid
        random.shuffle(routes)
        return routes[:limit]
    
    # Calculate CBF scores for all routes
    route_scores = []
    for route in routes:
        route_vector = extract_route_vector(route)
        score = calculate_cbf_score(user_vector, route_vector)
        route_scores.append((route, score))
    
    # Sort by score (descending) and return top N
    route_scores.sort(key=lambda x: x[1], reverse=True)
    recommended_routes = [route for route, score in route_scores[:limit]]
    
    return recommended_routes

