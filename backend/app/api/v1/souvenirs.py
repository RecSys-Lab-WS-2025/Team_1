"""
Souvenir API endpoints for route completion and souvenir management.

This module provides endpoints for:
- POST /api/profiles/{profile_id}/souvenirs - Complete route and create souvenir
- GET /api/profiles/{profile_id}/souvenirs - Get all souvenirs for a profile
- GET /api/profiles/{profile_id}/souvenirs/{souvenir_id} - Get single souvenir
"""
import json
import logging
from typing import Annotated, Optional

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc, asc
from sqlalchemy.orm import selectinload

from app.database import get_db
from app.models.entities import DemoProfile, Route, Souvenir, MiniQuest, Breakpoint
from app.api.schemas import (
    RouteCompleteRequest,
    RouteCompleteResponse,
    SouvenirResponse,
    SouvenirListResponse,
    RouteResponse,
)
from app.services.xp_calculator import calculate_route_completion_xp
from app.services.genai_service import generate_post_run_summary, generate_pixel_art_svg
from app.services.achievement_service import check_and_unlock_achievements

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/profiles", tags=["souvenirs"])

# Level calculation: 300 XP per level
XP_PER_LEVEL = 300


def calculate_level_from_xp(total_xp: int) -> int:
    """Calculate user level from total XP. Level = floor(total_xp / 300) + 1"""
    return (total_xp // XP_PER_LEVEL) + 1


@router.post("/{profile_id}/souvenirs", response_model=RouteCompleteResponse)
async def create_souvenir(
    profile_id: int,
    request: RouteCompleteRequest,
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """
    Complete a route and create a souvenir record.
    
    This endpoint:
    1. Validates route and profile exist
    2. Calculates XP breakdown (base + quests + difficulty multiplier)
    3. Generates AI summary (or uses fallback)
    4. Creates Souvenir record
    5. Updates user profile (total_xp and level)
    6. Returns complete souvenir information
    
    Args:
        profile_id: User profile ID
        request: Route completion request with route_id and completed_quest_ids
        db: Database session
    
    Returns:
        RouteCompleteResponse with souvenir, XP breakdown, and new level
    
    Raises:
        HTTPException: 404 if profile or route not found
    """
    try:
        logger.info(f"🎁 Creating souvenir: profile_id={profile_id}, route_id={request.route_id}, quests={len(request.completed_quest_ids)}")
        logger.info(f"📋 Request data: route_id={request.route_id}, completed_quest_ids={request.completed_quest_ids}")
        
        # 1. Validate profile
        profile = await db.get(DemoProfile, profile_id)
        if not profile:
            logger.warning(f"⚠️ Profile {profile_id} not found")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Profile with id {profile_id} not found"
            )
        
        # 2. Validate and load route (without breakpoints for performance)
        route_result = await db.execute(
            select(Route)
            .where(Route.id == request.route_id)
        )
        route = route_result.scalar_one_or_none()
        if not route:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Route with id {request.route_id} not found"
            )
        
        # 3. Calculate XP breakdown
        xp_breakdown = await calculate_route_completion_xp(
            route, request.completed_quest_ids, db
        )
        
        # 4. Count total quests for AI summary (estimate if breakpoints not loaded)
        # Since we're not loading breakpoints, use a reasonable estimate
        # or load breakpoints separately if needed
        total_quests = len(request.completed_quest_ids)  # Use completed count as estimate
        
        # 5. Generate AI summary
        try:
            route_length_km = (route.length_meters / 1000) if route.length_meters else 0
            genai_summary = await generate_post_run_summary(
                route_title=route.title,
                route_length_km=route_length_km,
                quests_completed=len(request.completed_quest_ids),
                total_quests=total_quests,
                user_level=profile.level
            )
        except Exception as e:
            logger.warning(f"AI summary generation failed: {e}", exc_info=True)
            # Fallback summary
            genai_summary = (
                f"Congratulations on completing {route.title}! "
                f"You earned {xp_breakdown['total']} XP. "
                f"Keep exploring to discover more adventures!"
            )
        
        # 5.5. Generate pixel art SVG image
        pixel_image_svg = None
        try:
            from datetime import datetime, timezone
            route_length_km = (route.length_meters / 1000) if route.length_meters else 0
            pixel_image_svg = await generate_pixel_art_svg(
                route_title=route.title,
                route_location=route.location,
                completed_at=datetime.now(timezone.utc),
                xp_gained=xp_breakdown['total'],
                distance_km=route_length_km,
                difficulty=route.difficulty
            )
            logger.info(f"✅ Pixel art SVG generated: {len(pixel_image_svg) if pixel_image_svg else 0} characters")
        except Exception as e:
            logger.error(f"❌ Pixel art generation failed: {e}", exc_info=True)
            # SVG generation should not fail with template system, but if it does, we'll retry
            # For now, continue without pixel image - user can run batch script later
            pixel_image_svg = None
            logger.warning(f"⚠️ Souvenir will be created without SVG. Run generate_missing_svgs.py to fix.")
        
        # 6. Create Souvenir
        new_souvenir = Souvenir(
            demo_profile_id=profile_id,
            route_id=request.route_id,
            total_xp_gained=xp_breakdown['total'],
            genai_summary=genai_summary,
            xp_breakdown_json=json.dumps(xp_breakdown, ensure_ascii=False),
            pixel_image_svg=pixel_image_svg
        )
        db.add(new_souvenir)
        
        # 7. Update profile
        old_level = profile.level
        profile.total_xp += xp_breakdown['total']
        profile.level = calculate_level_from_xp(profile.total_xp)
        new_level = profile.level
        
        await db.commit()
        await db.refresh(new_souvenir)
        
        # 7.5. Check and unlock achievements
        try:
            newly_unlocked = await check_and_unlock_achievements(profile_id, db)
            if newly_unlocked:
                logger.info(
                    f"Unlocked {len(newly_unlocked)} achievements for profile {profile_id}: "
                    f"{[a.achievement_key for a in newly_unlocked]}"
                )
        except Exception as e:
            logger.warning(f"Achievement check failed: {e}", exc_info=True)
            # Don't fail the route completion if achievement check fails
        
        # 8. Load route relationship for response
        # We already have the route object from earlier; just ensure the simple
        # foreign-key relationship on Souvenir is refreshed (no lazy breakpoint loading).
        await db.refresh(new_souvenir, ['route'])
        
        # 9. Build response without triggering lazy loading of Route.breakpoints.
        #    We construct a plain dict instead of letting Pydantic introspect the
        #    SQLAlchemy model (which caused MissingGreenlet when accessing breakpoints).
        route_dict = {
            "id": route.id,
            "title": route.title,
            "category_name": route.category_name,
            "length_meters": route.length_meters,
            "duration_min": route.duration_min,
            "difficulty": route.difficulty,
            "short_description": route.short_description,
            "location": route.location,
            "elevation": route.elevation,
            "tags_json": route.tags_json,
            "xp_required": route.xp_required,
            "base_xp_reward": route.base_xp_reward,
            "story_prologue_title": route.story_prologue_title,
            "story_prologue_body": route.story_prologue_body,
            "story_epilogue_body": route.story_epilogue_body,
            "gpx_data_raw": route.gpx_data_raw,
            "breakpoints": [],  # Intentionally empty to keep payload small
            "is_locked": False,
        }

        souvenir_dict = {
            "id": new_souvenir.id,
            "demo_profile_id": new_souvenir.demo_profile_id,
            "route_id": new_souvenir.route_id,
            "completed_at": new_souvenir.completed_at,
            "total_xp_gained": new_souvenir.total_xp_gained,
            "genai_summary": new_souvenir.genai_summary,
            "xp_breakdown_json": new_souvenir.xp_breakdown_json,
            "pixel_image_svg": new_souvenir.pixel_image_svg,
            "route": route_dict,
        }
        
        logger.info(f"✅ Souvenir created successfully: id={new_souvenir.id}, xp={xp_breakdown['total']}, new_level={new_level}")
        
        return RouteCompleteResponse(
            souvenir=SouvenirResponse(**souvenir_dict),
            xp_breakdown=xp_breakdown,
            total_xp_gained=xp_breakdown['total'],
            new_total_xp=profile.total_xp,  # Return the new total XP after update
            new_level=new_level
        )
    except HTTPException as e:
        # Re-raise HTTP exceptions (like 404) with logging
        logger.warning(f"⚠️ HTTP Exception in create_souvenir: {e.status_code} - {e.detail}")
        raise
    except Exception as e:
        logger.error(f"❌ Error creating souvenir: {type(e).__name__}: {str(e)}", exc_info=True)
        logger.error(f"❌ Full traceback:", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create souvenir: {str(e)}"
        )


@router.get("/{profile_id}/souvenirs", response_model=SouvenirListResponse)
async def get_souvenirs(
    profile_id: int,
    db: Annotated[AsyncSession, Depends(get_db)],
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    sort: str = Query("newest", regex="^(newest|oldest|xp_high|xp_low)$"),
):
    """
    Get all souvenirs for a profile with optional sorting and pagination.
    
    Args:
        profile_id: User profile ID
        db: Database session
        limit: Maximum number of souvenirs to return (default: 20, max: 100)
        offset: Pagination offset (default: 0)
        sort: Sort order - newest, oldest, xp_high, xp_low (default: newest)
    
    Returns:
        SouvenirListResponse with souvenirs list and total count
    
    Raises:
        HTTPException: 404 if profile not found
    """
    # Validate profile
    profile = await db.get(DemoProfile, profile_id)
    if not profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Profile with id {profile_id} not found"
        )
    
    # Build query with route relationship
    # Only load route basic info, not all breakpoints/mini_quests to avoid performance issues
    query = (
        select(Souvenir)
        .where(Souvenir.demo_profile_id == profile_id)
        .options(selectinload(Souvenir.route))  # Only load route, not nested breakpoints
    )
    
    # Apply sorting
    if sort == "newest":
        query = query.order_by(desc(Souvenir.completed_at))
    elif sort == "oldest":
        query = query.order_by(asc(Souvenir.completed_at))
    elif sort == "xp_high":
        query = query.order_by(desc(Souvenir.total_xp_gained))
    elif sort == "xp_low":
        query = query.order_by(asc(Souvenir.total_xp_gained))
    
    # Get total count
    count_result = await db.execute(
        select(Souvenir).where(Souvenir.demo_profile_id == profile_id)
    )
    total = len(count_result.scalars().all())
    
    # Apply pagination
    query = query.limit(limit).offset(offset)
    
    # Execute query
    result = await db.execute(query)
    souvenirs = result.scalars().all()
    
    # Convert to response models without triggering lazy loading of breakpoints
    souvenir_responses = []
    for souvenir in souvenirs:
        route_dict = None
        if souvenir.route:
            route = souvenir.route
            route_dict = {
                "id": route.id,
                "title": route.title,
                "category_name": route.category_name,
                "length_meters": route.length_meters,
                "duration_min": route.duration_min,
                "difficulty": route.difficulty,
                "short_description": route.short_description,
                "location": route.location,
                "elevation": route.elevation,
                "tags_json": route.tags_json,
                "xp_required": route.xp_required,
                "base_xp_reward": route.base_xp_reward,
                "story_prologue_title": route.story_prologue_title,
                "story_prologue_body": route.story_prologue_body,
                "story_epilogue_body": route.story_epilogue_body,
                "gpx_data_raw": route.gpx_data_raw,
                "breakpoints": [],  # Intentionally empty
                "is_locked": False,
            }

        souvenir_response = SouvenirResponse(
            id=souvenir.id,
            demo_profile_id=souvenir.demo_profile_id,
            route_id=souvenir.route_id,
            completed_at=souvenir.completed_at,
            total_xp_gained=souvenir.total_xp_gained,
            genai_summary=souvenir.genai_summary,
            xp_breakdown_json=souvenir.xp_breakdown_json,
            pixel_image_svg=souvenir.pixel_image_svg,
            route=RouteResponse(**route_dict) if route_dict else None,
        )
        souvenir_responses.append(souvenir_response)
    
    return SouvenirListResponse(
        souvenirs=souvenir_responses,
        total=total
    )


@router.get("/{profile_id}/souvenirs/{souvenir_id}", response_model=SouvenirResponse)
async def get_souvenir(
    profile_id: int,
    souvenir_id: int,
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """
    Get a single souvenir by ID.
    
    Args:
        profile_id: User profile ID
        souvenir_id: Souvenir ID
        db: Database session
    
    Returns:
        SouvenirResponse with full souvenir details including route
    
    Raises:
        HTTPException: 404 if profile or souvenir not found
    """
    # Validate profile
    profile = await db.get(DemoProfile, profile_id)
    if not profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Profile with id {profile_id} not found"
        )
    
    # Get souvenir with route (without nested breakpoints for performance)
    result = await db.execute(
        select(Souvenir)
        .where(Souvenir.id == souvenir_id)
        .where(Souvenir.demo_profile_id == profile_id)
        .options(selectinload(Souvenir.route))  # Only load route, not nested breakpoints
    )
    souvenir = result.scalar_one_or_none()
    
    if not souvenir:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Souvenir with id {souvenir_id} not found for profile {profile_id}"
        )
    
    # Convert to response (without breakpoints to reduce payload and without lazy loads)
    route_dict = None
    if souvenir.route:
        route = souvenir.route
        route_dict = {
            "id": route.id,
            "title": route.title,
            "category_name": route.category_name,
            "length_meters": route.length_meters,
            "duration_min": route.duration_min,
            "difficulty": route.difficulty,
            "short_description": route.short_description,
            "location": route.location,
            "elevation": route.elevation,
            "tags_json": route.tags_json,
            "xp_required": route.xp_required,
            "base_xp_reward": route.base_xp_reward,
            "story_prologue_title": route.story_prologue_title,
            "story_prologue_body": route.story_prologue_body,
            "story_epilogue_body": route.story_epilogue_body,
            "gpx_data_raw": route.gpx_data_raw,
            "breakpoints": [],  # Intentionally empty
            "is_locked": False,
        }

    return SouvenirResponse(
        id=souvenir.id,
        demo_profile_id=souvenir.demo_profile_id,
        route_id=souvenir.route_id,
        completed_at=souvenir.completed_at,
        total_xp_gained=souvenir.total_xp_gained,
        genai_summary=souvenir.genai_summary,
        xp_breakdown_json=souvenir.xp_breakdown_json,
        pixel_image_svg=souvenir.pixel_image_svg,
        route=RouteResponse(**route_dict) if route_dict else None,
    )

