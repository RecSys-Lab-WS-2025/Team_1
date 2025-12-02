"""
Profile API endpoints for user questionnaire submission and profile management.

This module implements:
- POST /api/profiles - Submit questionnaire and create profile (US-03 & US-04)
- GET /api/profiles/{id} - Retrieve profile details
- PATCH /api/profiles/{id} - Update profile
"""
import json
import logging
from typing import Annotated, Optional

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from sqlalchemy.orm import selectinload

from app.api.schemas import (
    FeedbackCreate,
    FeedbackResponse,
    ProfileCreate,
    ProfileCreateResponse,
    ProfileResponse,
    ProfileUpdate,
    ProfileStatisticsResponse,
)
from app.database import get_db
from app.models.entities import DemoProfile, ProfileFeedback, Route, Souvenir, ProfileAchievement
from app.services.genai_service import generate_welcome_summary
from app.services.user_profile_service import (
    generate_fallback_welcome,
    translate_questionnaire_to_vector,
)
from app.logger import get_logger, log_request, log_business_logic, log_database_operation

logger = get_logger(__name__)


def map_category_to_activity_type(category_name: Optional[str]) -> str:
    """
    Map backend category_name to frontend activity type.
    
    Maps backend category_name values to frontend categories:
    - Running: "Jogging", "Trail running"
    - Cycling: "Cycling", "Mountainbiking", "Long distance cycling"
    - Hiking: "Theme trail", "Hiking trail", and everything else
    """
    if not category_name:
        return "hiking"
    
    lower = category_name.lower()
    
    # Running: "Jogging", "Trail running"
    if "run" in lower or "jogging" in lower:
        return "running"
    
    # Cycling: "Cycling", "Mountainbiking", "Long distance cycling"
    if "cycling" in lower or "mountain" in lower or "bike" in lower:
        return "cycling"
    
    # Hiking: "Theme trail", "Hiking trail", and everything else
    return "hiking"


router = APIRouter(prefix="/profiles", tags=["profiles"])


@router.post("", response_model=ProfileCreateResponse, status_code=status.HTTP_201_CREATED)
async def submit_questionnaire(
    questionnaire: ProfileCreate,
    db: Annotated[AsyncSession, Depends(get_db)],
) -> ProfileCreateResponse:
    """
    Submit cold-start questionnaire and create user profile (US-03 & US-04).
    
    This endpoint:
    1. Translates questionnaire answers to a structured user_vector
    2. Generates a personalized welcome summary using GenAI
    3. Stores the profile in the database
    4. Returns the profile ID and welcome summary
    
    Parameters
    ----------
    questionnaire : ProfileCreate
        User's answers to the onboarding questionnaire
    db : AsyncSession
        Database session
    
    Returns
    -------
    ProfileCreateResponse
        Created profile with welcome summary and user_vector
    """
    import time
    start_time = time.time()
    
    logger.info("=" * 80)
    logger.info("📝 Received questionnaire submission")
    logger.debug(f"Questionnaire data: fitness={questionnaire.fitness}, type={questionnaire.type}, narrative={questionnaire.narrative}")
    
    # 1. Translate questionnaire to user_vector
    logger.debug("🔄 Translating questionnaire into user vector...")
    user_vector = translate_questionnaire_to_vector(questionnaire)
    logger.debug(f"✅ User vector generated: {user_vector}")
    
    # 2. Generate welcome summary with GenAI (with fallback)
    logger.debug("🤖 Generating welcome summary...")
    try:
        welcome_summary = await generate_welcome_summary(questionnaire)
        logger.info("✅ GenAI welcome summary generated successfully")
    except HTTPException as e:
        # Log HTTP errors from Ollama (e.g., 503 Service Unavailable)
        logger.warning(
            f"⚠️ GenAI service unavailable (status {e.status_code}), using fallback: {e.detail}",
            exc_info=True
        )
        welcome_summary = generate_fallback_welcome(questionnaire)
        logger.info("✅ Fallback welcome summary used")
    except Exception as e:
        # Log other unexpected errors
        logger.warning(
            f"⚠️ GenAI generation failed, using fallback: {type(e).__name__}: {str(e)}",
            exc_info=True
        )
        welcome_summary = generate_fallback_welcome(questionnaire)
        logger.info("✅ Fallback welcome summary used")
    
    # 3. Create database record
    logger.debug("💾 Creating user profile record...")
    new_profile = DemoProfile(
        user_vector_json=json.dumps(user_vector, ensure_ascii=False),
        genai_welcome_summary=welcome_summary,
        total_xp=0,
        level=1,
    )
    db.add(new_profile)
    await db.commit()
    await db.refresh(new_profile)
    
    log_database_operation(
        logger,
        "INSERT",
        "DemoProfile",
        record_id=new_profile.id,
        duration_ms=(time.time() - start_time) * 1000
    )
    
    log_business_logic(
        logger,
        "create",
        "user profile",
        entity_id=new_profile.id,
        fitness=questionnaire.fitness,
        narrative=questionnaire.narrative
    )
    
    duration_ms = (time.time() - start_time) * 1000
    log_request(
        logger,
        "POST",
        "/api/profiles",
        status_code=201,
        duration_ms=duration_ms,
        user_id=new_profile.id
    )
    
    logger.info(f"✅ User profile created successfully: profile_id={new_profile.id}, duration={duration_ms:.2f}ms")
    logger.info("=" * 80)
    
    # 4. Return response
    return ProfileCreateResponse(
        id=new_profile.id,
        welcome_summary=welcome_summary,
        user_vector=user_vector,
    )


@router.get("/{profile_id}", response_model=ProfileResponse)
async def get_profile(
    profile_id: int,
    db: Annotated[AsyncSession, Depends(get_db)],
) -> ProfileResponse:
    """
    Retrieve profile details by ID.
    
    Parameters
    ----------
    profile_id : int
        Profile ID
    db : AsyncSession
        Database session
    
    Returns
    -------
    ProfileResponse
        Profile details
    
    Raises
    ------
    HTTPException
        404 if profile not found
    """
    import time
    start_time = time.time()
    
    logger.debug(f"🔍 Fetching user profile: profile_id={profile_id}")
    profile = await db.get(DemoProfile, profile_id)
    
    if profile is None:
        logger.warning(f"❌ User profile not found: profile_id={profile_id}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Profile with id {profile_id} not found",
        )
    
    duration_ms = (time.time() - start_time) * 1000
    log_request(
        logger,
        "GET",
        f"/api/profiles/{profile_id}",
        status_code=200,
        duration_ms=duration_ms,
        user_id=profile_id
    )
    logger.debug(f"✅ User profile fetched successfully: profile_id={profile_id}, duration={duration_ms:.2f}ms")
    
    return ProfileResponse.model_validate(profile)


@router.patch("/{profile_id}", response_model=ProfileResponse)
async def update_profile(
    profile_id: int,
    profile_update: ProfileUpdate,
    db: Annotated[AsyncSession, Depends(get_db)],
) -> ProfileResponse:
    """
    Update profile details (partial update).
    
    Parameters
    ----------
    profile_id : int
        Profile ID
    profile_update : ProfileUpdate
        Fields to update
    db : AsyncSession
        Database session
    
    Returns
    -------
    ProfileResponse
        Updated profile
    
    Raises
    ------
    HTTPException
        404 if profile not found
    """
    profile = await db.get(DemoProfile, profile_id)
    
    if profile is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Profile with id {profile_id} not found",
        )
    
    # Update only provided fields
    update_data = profile_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(profile, field, value)
    
    await db.commit()
    await db.refresh(profile)
    
    return ProfileResponse.model_validate(profile)


@router.delete("/{profile_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_profile(
    profile_id: int,
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """
    Delete a user profile from the database.
    
    Parameters
    ----------
    profile_id : int
        Profile ID to delete
    db : AsyncSession
        Database session
    
    Raises
    ------
    HTTPException
        404 if profile not found
    """
    profile = await db.get(DemoProfile, profile_id)
    
    if profile is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Profile with id {profile_id} not found",
        )
    
    await db.delete(profile)
    await db.flush()  # Flush to ensure deletion is processed
    
    return None


@router.post("/{profile_id}/feedback", response_model=FeedbackResponse, status_code=status.HTTP_201_CREATED)
async def submit_feedback(
    profile_id: int,
    feedback: FeedbackCreate,
    db: Annotated[AsyncSession, Depends(get_db)],
) -> FeedbackResponse:
    """
    Submit negative feedback for a route recommendation (US-08).
    
    This endpoint allows users to provide feedback on routes they don't like,
    which helps improve future recommendations through adaptive re-ranking.
    
    Parameters
    ----------
    profile_id : int
        Profile ID of the user submitting feedback
    feedback : FeedbackCreate
        Feedback data containing route_id and reason
    db : AsyncSession
        Database session
    
    Returns
    -------
    FeedbackResponse
        Created feedback entry
    
    Raises
    ------
    HTTPException
        404 if profile or route not found
    """
    # Verify profile exists
    profile = await db.get(DemoProfile, profile_id)
    if profile is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Profile with id {profile_id} not found",
        )
    
    # Verify route exists
    route = await db.get(Route, feedback.route_id)
    if route is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Route with id {feedback.route_id} not found",
        )
    
    # Create feedback entry
    new_feedback = ProfileFeedback(
        demo_profile_id=profile_id,
        route_id=feedback.route_id,
        reason=feedback.reason,
    )
    db.add(new_feedback)
    await db.commit()
    await db.refresh(new_feedback)
    
    return FeedbackResponse.model_validate(new_feedback)


@router.get("/{profile_id}/statistics", response_model=ProfileStatisticsResponse)
async def get_profile_statistics(
    profile_id: int,
    db: Annotated[AsyncSession, Depends(get_db)],
) -> ProfileStatisticsResponse:
    """
    Get aggregated statistics for a user profile.
    
    This endpoint provides efficient server-side aggregation of:
    - Total distance traveled (sum of all completed route distances)
    - Total elevation gained (sum of all completed route elevations)
    - Routes completed count
    - Achievements unlocked count
    - Activity breakdown (running/hiking/cycling counts)
    
    Parameters
    ----------
    profile_id : int
        Profile ID
    db : AsyncSession
        Database session
    
    Returns
    -------
    ProfileStatisticsResponse
        Aggregated statistics for the profile
    
    Raises
    ------
    HTTPException
        404 if profile not found
    """
    # Validate profile exists
    profile = await db.get(DemoProfile, profile_id)
    if profile is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Profile with id {profile_id} not found",
        )
    
    # Get all souvenirs with routes (no limit for accurate statistics)
    souvenirs_result = await db.execute(
        select(Souvenir)
        .where(Souvenir.demo_profile_id == profile_id)
        .options(selectinload(Souvenir.route))
    )
    souvenirs = souvenirs_result.scalars().all()
    
    # Aggregate statistics from souvenirs
    total_distance_km = 0.0
    total_elevation_m = 0
    activity_breakdown = {"running": 0, "hiking": 0, "cycling": 0}
    
    for souvenir in souvenirs:
        if souvenir.route:
            # Sum distance (convert meters to km)
            if souvenir.route.length_meters:
                total_distance_km += souvenir.route.length_meters / 1000.0
            
            # Sum elevation
            if souvenir.route.elevation:
                total_elevation_m += souvenir.route.elevation
            
            # Count by activity type
            if souvenir.route.category_name:
                activity_type = map_category_to_activity_type(souvenir.route.category_name)
                activity_breakdown[activity_type] = activity_breakdown.get(activity_type, 0) + 1
    
    # Count unlocked achievements
    achievements_result = await db.execute(
        select(func.count(ProfileAchievement.id))
        .where(ProfileAchievement.demo_profile_id == profile_id)
    )
    achievements_unlocked = achievements_result.scalar() or 0
    
    return ProfileStatisticsResponse(
        total_distance_km=round(total_distance_km, 1),
        total_elevation_m=total_elevation_m,
        routes_completed=len(souvenirs),
        achievements_unlocked=achievements_unlocked,
        activity_breakdown=activity_breakdown,
    )

