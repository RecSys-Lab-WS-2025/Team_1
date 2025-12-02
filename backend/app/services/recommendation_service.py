"""
Recommendation service implementing Content-Based Filtering (CBF).

This service provides route recommendations by matching user preferences
with route attributes using similarity scoring.

Enhanced with feedback-aware recommendations that learn from user feedback.
"""
import json
import math
import random
import time
from datetime import datetime, timezone
from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.entities import Route, DemoProfile, Breakpoint, ProfileFeedback
from app.logger import get_logger, log_business_logic

logger = get_logger(__name__)


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

# Feedback-aware recommendation parameters
# Penalty multipliers based on feedback count:
# - 1 feedback: 50% (0.5)
# - 2 feedbacks: 10% (0.1)
# - 3+ feedbacks: 1% (0.01)
FEEDBACK_PENALTY_MULTIPLIERS = {
    1: 0.5,   # 50%
    2: 0.1,   # 10%
    3: 0.01,  # 1%
}
FEEDBACK_FILTER_THRESHOLD = 4  # Filter routes with 4+ feedback entries (after 3rd feedback shows at 1%)
TIME_DECAY_HALF_LIFE_DAYS = 30.0  # 30 days half-life for feedback weight


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


def calculate_cbf_score(user_vector: dict, route_vector: dict) -> tuple[float, dict]:
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
    tuple[float, dict]
        Overall similarity score between 0.0 and 1.0, and score breakdown
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
    
    # Return score and breakdown
    score_breakdown = {
        "difficulty": {
            "score": difficulty_score,
            "weight": SCORE_WEIGHTS["difficulty"],
            "weighted_score": SCORE_WEIGHTS["difficulty"] * difficulty_score,
            "user_range": user_vector.get("difficulty_range", [0, 3]),
            "route_value": route_vector["difficulty"],
        },
        "distance": {
            "score": distance_score,
            "weight": SCORE_WEIGHTS["distance"],
            "weighted_score": SCORE_WEIGHTS["distance"] * distance_score,
            "user_range": [user_vector.get("min_distance_km", 0.0), user_vector.get("max_distance_km", 100.0)],
            "route_value": route_vector["length_km"],
        },
        "tags": {
            "score": tag_score,
            "weight": SCORE_WEIGHTS["tags"],
            "weighted_score": SCORE_WEIGHTS["tags"] * tag_score,
            "user_tags": user_vector.get("preferred_tags", []),
            "route_tags": route_vector["tags"],
        },
        "total": final_score,
    }
    
    return final_score, score_breakdown


def calculate_time_decay_weight(days_ago: float, half_life_days: float = TIME_DECAY_HALF_LIFE_DAYS) -> float:
    """
    Calculate time decay weight for feedback.
    
    More recent feedback has higher weight. Uses exponential decay.
    
    Parameters
    ----------
    days_ago : float
        Number of days since feedback was given
    half_life_days : float
        Half-life in days (default: 30 days)
    
    Returns
    -------
    float
        Weight between 0.0 and 1.0
    """
    if days_ago <= 0:
        return 1.0
    return math.exp(-days_ago / half_life_days)


def adjust_user_vector_with_feedback(
    user_vector: dict,
    feedback_entries: list[ProfileFeedback],
    route_vectors: dict[int, dict]
) -> dict:
    """
    Adjust user preference vector based on feedback history.
    
    This function learns from user feedback to adapt preferences:
    - too-hard: Lower maximum difficulty preference
    - too-easy: Raise minimum difficulty preference
    - too-far: Reduce maximum distance preference
    - not-interested: Remove route tags from preferred tags
    
    Parameters
    ----------
    user_vector : dict
        Original user preference vector
    feedback_entries : list[ProfileFeedback]
        List of user feedback entries
    route_vectors : dict[int, dict]
        Dictionary mapping route_id to route_vector
    
    Returns
    -------
    dict
        Adjusted user preference vector
    """
    # Create a copy to avoid modifying original
    adjusted_vector = user_vector.copy()
    
    # Initialize adjusted fields
    if "difficulty_range" not in adjusted_vector:
        adjusted_vector["difficulty_range"] = [0, 3]
    else:
        adjusted_vector["difficulty_range"] = list(adjusted_vector["difficulty_range"])
    
    if "max_distance_km" not in adjusted_vector:
        adjusted_vector["max_distance_km"] = 100.0
    else:
        adjusted_vector["max_distance_km"] = float(adjusted_vector["max_distance_km"])
    
    if "preferred_tags" not in adjusted_vector:
        adjusted_vector["preferred_tags"] = []
    else:
        adjusted_vector["preferred_tags"] = list(adjusted_vector["preferred_tags"])
    
    # Process each feedback entry
    now = datetime.now(timezone.utc)
    
    for feedback in feedback_entries:
        route_vector = route_vectors.get(feedback.route_id)
        if not route_vector:
            continue
        
        # Calculate time decay weight (recent feedback matters more)
        # Note: ProfileFeedback doesn't have created_at by default, so we use current time
        # In production, you'd want to add created_at timestamp to ProfileFeedback
        days_ago = 0.0  # Assume recent if no timestamp
        weight = calculate_time_decay_weight(days_ago)
        
        reason = feedback.reason
        
        # Adjust preferences based on feedback reason
        if reason == "too-hard":
            # Lower maximum difficulty preference
            adjusted_vector["difficulty_range"][1] = max(
                0,
                adjusted_vector["difficulty_range"][1] - 0.5 * weight
            )
        elif reason == "too-easy":
            # Raise minimum difficulty preference
            adjusted_vector["difficulty_range"][0] = min(
                3,
                adjusted_vector["difficulty_range"][0] + 0.5 * weight
            )
        elif reason == "too-far":
            # Reduce maximum distance preference
            adjusted_vector["max_distance_km"] *= (1 - 0.1 * weight)
        elif reason == "not-interested":
            # Remove route tags from preferred tags
            route_tags = route_vector.get("tags", [])
            route_tag_set = set(tag.lower() for tag in route_tags)
            adjusted_vector["preferred_tags"] = [
                tag for tag in adjusted_vector["preferred_tags"]
                if tag.lower() not in route_tag_set
            ]
    
    # Ensure difficulty range is valid
    if adjusted_vector["difficulty_range"][0] > adjusted_vector["difficulty_range"][1]:
        # If range is invalid, reset to original or default
        adjusted_vector["difficulty_range"] = user_vector.get("difficulty_range", [0, 3])
    
    # Ensure max_distance is positive
    if adjusted_vector["max_distance_km"] <= 0:
        adjusted_vector["max_distance_km"] = user_vector.get("max_distance_km", 100.0)
    
    return adjusted_vector


def calculate_feedback_penalty(
    route_id: int,
    feedback_entries: list[ProfileFeedback]
) -> float:
    """
    Calculate feedback penalty multiplier for a route.
    
    Penalty schedule:
    - 1 feedback: 50% (0.5)
    - 2 feedbacks: 10% (0.1)
    - 3+ feedbacks: 1% (0.01)
    
    Parameters
    ----------
    route_id : int
        Route ID to check
    feedback_entries : list[ProfileFeedback]
        List of all user feedback entries
    
    Returns
    -------
    float
        Penalty multiplier (0.0 to 1.0)
        - 1.0 if no feedback (no penalty)
        - 0.5 if 1 feedback (50%)
        - 0.1 if 2 feedbacks (10%)
        - 0.01 if 3+ feedbacks (1%)
    """
    route_feedback = [f for f in feedback_entries if f.route_id == route_id]
    
    if not route_feedback:
        return 1.0  # No penalty
    
    feedback_count = len(route_feedback)
    
    # Apply penalty based on feedback count
    if feedback_count >= 3:
        return FEEDBACK_PENALTY_MULTIPLIERS[3]  # 1%
    elif feedback_count == 2:
        return FEEDBACK_PENALTY_MULTIPLIERS[2]  # 10%
    else:  # feedback_count == 1
        return FEEDBACK_PENALTY_MULTIPLIERS[1]  # 50%


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
    start_time = time.time()
    
    logger.debug(f"🔄 Starting route recommendation calculation: profile_id={profile_id}, category={category}, limit={limit}")
    
    # Build base query - limit initial load to avoid loading too much data
    # We'll load relationships only for the final selected routes
    query = select(Route)
    
    # Apply category filter if specified
    if category and category in CATEGORY_MAPPING:
        category_names = CATEGORY_MAPPING[category]
        query = query.where(Route.category_name.in_(category_names))
    
    # For personalized recommendations, we need to score all routes first
    # For random recommendations, we can limit early
    if profile_id is None:
        # For random, limit early and load relationships only for selected routes
        query = query.limit(limit * 3)  # Get 3x limit for better randomization
    
    # Execute query (without relationships for now - faster)
    result = await db.execute(query)
    routes = list(result.scalars().all())
    
    # If no profile_id, return random routes
    if profile_id is None:
        logger.debug(f"🎲 Random recommendation mode: selecting {limit} routes from {len(routes)} candidates")
        random.shuffle(routes)
        selected_routes = routes[:limit]
        # Now load relationships only for selected routes
        route_ids = [r.id for r in selected_routes]
        query_with_relations = select(Route).where(Route.id.in_(route_ids)).options(
            selectinload(Route.breakpoints).selectinload(Breakpoint.mini_quests)
        )
        result_with_relations = await db.execute(query_with_relations)
        routes_with_relations = {r.id: r for r in result_with_relations.scalars().all()}
        final_routes = [routes_with_relations[r.id] for r in selected_routes if r.id in routes_with_relations]
        duration_ms = (time.time() - start_time) * 1000
        logger.info(f"✅ Random recommendation completed: returned {len(final_routes)} routes, duration={duration_ms:.2f}ms")
        return final_routes
    
    # Get user profile and vector
    logger.debug(f"🔍 Fetching user profile and preference vector: profile_id={profile_id}")
    profile = await db.get(DemoProfile, profile_id)
    if not profile or not profile.user_vector_json:
        logger.warning(f"⚠️ User profile or preference vector not found, falling back to random recommendations: profile_id={profile_id}")
        random.shuffle(routes)
        return routes[:limit]
    
    try:
        user_vector = json.loads(profile.user_vector_json)
        logger.debug(f"✅ User preference vector parsed successfully: {user_vector}")
    except (json.JSONDecodeError, TypeError) as e:
        logger.warning(f"⚠️ Failed to parse user preference vector, falling back to random recommendations: {e}")
        random.shuffle(routes)
        return routes[:limit]
    
    # Fetch user feedback entries for feedback-aware recommendations
    logger.debug(f"🔍 Fetching user feedback entries: profile_id={profile_id}")
    feedback_query = select(ProfileFeedback).where(
        ProfileFeedback.demo_profile_id == profile_id
    )
    feedback_result = await db.execute(feedback_query)
    feedback_entries = list(feedback_result.scalars().all())
    logger.debug(f"📊 Number of user feedback entries: {len(feedback_entries)}")
    
    # Build route vectors dictionary for feedback processing
    route_vectors = {}
    for route in routes:
        route_vectors[route.id] = extract_route_vector(route)
    
    # Adjust user vector based on feedback (learn from user preferences)
    if feedback_entries:
        logger.debug("🔄 Adjusting preference vector based on user feedback...")
        adjusted_user_vector = adjust_user_vector_with_feedback(
            user_vector,
            feedback_entries,
            route_vectors
        )
        logger.debug(f"✅ Preference vector adjustment completed: {adjusted_user_vector}")
    else:
        adjusted_user_vector = user_vector
        logger.debug("ℹ️ No user feedback available, using original preference vector")
    
    # Calculate CBF scores for all routes with feedback-aware scoring
    logger.debug(f"📊 Starting CBF score calculation: total_routes={len(routes)}")
    route_scores = []
    for route in routes:
        route_vector = route_vectors[route.id]
        
        # Check if route should be filtered (too many feedback entries)
        route_feedback_count = sum(
            1 for f in feedback_entries if f.route_id == route.id
        )
        if route_feedback_count >= FEEDBACK_FILTER_THRESHOLD:
            # Skip routes with 4+ negative feedback entries (after showing at 1% for 3 feedbacks)
            continue
        
        # Calculate base CBF score using adjusted user vector
        base_score, score_breakdown = calculate_cbf_score(
            adjusted_user_vector,
            route_vector
        )
        
        # Apply feedback penalty
        penalty_multiplier = calculate_feedback_penalty(route.id, feedback_entries)
        final_score = base_score * penalty_multiplier
        
        # Update score breakdown with feedback information
        score_breakdown["feedback_adjusted"] = True
        score_breakdown["base_score"] = base_score
        score_breakdown["final_score"] = final_score
        if penalty_multiplier < 1.0:
            score_breakdown["feedback_penalty"] = penalty_multiplier
            score_breakdown["feedback_count"] = route_feedback_count
        
        route_scores.append((route, final_score, score_breakdown))
    
    # Sort by score (descending) and return top N with scores
    route_scores.sort(key=lambda x: x[1], reverse=True)
    logger.debug(f"📊 CBF score calculation completed: valid_routes={len(route_scores)}")
    
    # Log top scores for debugging
    if route_scores:
        top_3 = route_scores[:3]
        for idx, (route, score, _) in enumerate(top_3, 1):
            logger.debug(f"  {idx}. Route {route.id}: score={score:.4f}")
    
    # Store scores as route attributes for API response
    for route, score, score_breakdown in route_scores[:limit]:
        route.recommendation_score = score
        route.recommendation_score_breakdown = score_breakdown
    
    recommended_routes = [route for route, score, _ in route_scores[:limit]]
    
    # Now load relationships only for the final selected routes (much faster)
    route_ids = [r.id for r in recommended_routes]
    query_with_relations = select(Route).where(Route.id.in_(route_ids)).options(
        selectinload(Route.breakpoints).selectinload(Breakpoint.mini_quests)
    )
    result_with_relations = await db.execute(query_with_relations)
    routes_with_relations = {r.id: r for r in result_with_relations.scalars().all()}
    
    # Preserve scores and return routes with loaded relationships, maintaining order
    final_routes = []
    for route in recommended_routes:
        if route.id in routes_with_relations:
            final_route = routes_with_relations[route.id]
            # Preserve scores
            final_route.recommendation_score = route.recommendation_score
            final_route.recommendation_score_breakdown = route.recommendation_score_breakdown
            final_routes.append(final_route)
    
    duration_ms = (time.time() - start_time) * 1000
    log_business_logic(
        logger,
        "calculate",
        "recommended routes",
        entity_id=profile_id,
        routes_count=len(final_routes),
        total_candidates=len(routes),
        feedback_count=len(feedback_entries)
    )
    
    logger.info(f"✅ Personalized recommendation completed: returned {len(final_routes)} routes, duration={duration_ms:.2f}ms")
    
    return final_routes

