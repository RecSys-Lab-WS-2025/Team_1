"""
Achievements API endpoints for retrieving and checking user achievements.
"""
from typing import Annotated, List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.entities import Achievement, ProfileAchievement, DemoProfile
from app.services.achievement_service import (
    get_all_achievements,
    get_user_achievements,
    check_and_unlock_achievements,
)

router = APIRouter(prefix="/achievements", tags=["achievements"])


@router.get("", response_model=List[dict])
async def list_achievements(
    db: Annotated[AsyncSession, Depends(get_db)] = ...,
):
    """
    Get all achievement definitions.
    
    Returns:
        List of all achievements with their definitions
    """
    achievements = await get_all_achievements(db)
    return [
        {
            "id": a.id,
            "achievement_key": a.achievement_key,
            "name": a.name,
            "description": a.description,
            "icon": a.icon,
            "condition_type": a.condition_type,
            "condition_value": a.condition_value,
        }
        for a in achievements
    ]


@router.get("/profiles/{profile_id}", response_model=List[dict])
async def get_profile_achievements(
    profile_id: int,
    db: Annotated[AsyncSession, Depends(get_db)] = ...,
):
    """
    Get all achievements for a specific user profile.
    
    Returns:
        List of achievements with unlock status
    """
    # Verify profile exists
    profile = await db.get(DemoProfile, profile_id)
    if not profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Profile with id {profile_id} not found",
        )

    # Ensure achievements are seeded (in case they weren't seeded on startup)
    from app.services.achievement_service import seed_achievements
    try:
        await seed_achievements(db)
    except Exception:
        # Ignore if already seeded
        pass
    
    # Get all achievements
    all_achievements = await get_all_achievements(db)
    
    # Get user's unlocked achievements
    user_achievements = await get_user_achievements(profile_id, db)
    unlocked_achievement_ids = {ua.achievement_id for ua in user_achievements}
    
    # Build response with unlock status
    result = []
    for achievement in all_achievements:
        is_unlocked = achievement.id in unlocked_achievement_ids
        unlocked_at = None
        if is_unlocked:
            # Find the unlock record
            for ua in user_achievements:
                if ua.achievement_id == achievement.id:
                    unlocked_at = ua.unlocked_at.isoformat()
                    break
        
        result.append({
            "id": achievement.id,
            "achievement_key": achievement.achievement_key,
            "name": achievement.name,
            "description": achievement.description,
            "icon": achievement.icon,
            "unlocked": is_unlocked,
            "unlocked_at": unlocked_at,
        })
    
    return result


@router.post("/profiles/{profile_id}/check", response_model=List[dict])
async def check_achievements(
    profile_id: int,
    db: Annotated[AsyncSession, Depends(get_db)] = ...,
):
    """
    Check and unlock achievements for a user profile.
    
    This endpoint:
    1. Checks all achievement conditions
    2. Unlocks any newly qualified achievements
    3. Returns list of newly unlocked achievements
    
    Returns:
        List of newly unlocked achievements
    """
    # Verify profile exists
    profile = await db.get(DemoProfile, profile_id)
    if not profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Profile with id {profile_id} not found",
        )

    # Check and unlock achievements
    newly_unlocked = await check_and_unlock_achievements(profile_id, db)
    
    return [
        {
            "id": a.id,
            "achievement_key": a.achievement_key,
            "name": a.name,
            "description": a.description,
            "icon": a.icon,
        }
        for a in newly_unlocked
    ]

