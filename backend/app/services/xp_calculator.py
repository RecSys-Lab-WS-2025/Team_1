"""
XP calculation service for route completion.

This service calculates XP breakdown for completing routes, including:
- Base XP (from route.base_xp_reward)
- Quest XP (from completed mini quests)
- Difficulty multiplier
"""
from typing import List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.models.entities import Route, MiniQuest, Breakpoint


# Difficulty multipliers for total XP calculation
DIFFICULTY_MULTIPLIER = {
    0: 1.0,  # easy
    1: 1.2,  # medium
    2: 1.5,  # hard
    3: 2.0,  # expert
}


async def calculate_route_completion_xp(
    route: Route,
    completed_quest_ids: List[int],
    db: AsyncSession
) -> dict:
    """
    Calculate XP breakdown for completing a route.
    
    Args:
        route: The completed route
        completed_quest_ids: List of completed mini quest IDs
        db: Database session
    
    Returns:
        dict with structure:
        {
            "base": int,  # Base XP from route
            "quests": int,  # Total XP from completed quests
            "difficulty_multiplier": float,  # Multiplier based on route difficulty
            "total": int  # Total XP gained (base + quests) * multiplier
        }
    """
    # 1. Get base XP from route
    base_xp = route.base_xp_reward or 0
    
    # 2. Calculate quest XP
    quest_xp = 0
    if completed_quest_ids:
        # Query all mini quests for this route
        result = await db.execute(
            select(MiniQuest)
            .join(Breakpoint)
            .where(Breakpoint.route_id == route.id)
            .where(MiniQuest.id.in_(completed_quest_ids))
        )
        completed_quests = result.scalars().all()
        quest_xp = sum(quest.xp_reward for quest in completed_quests)
    
    # 3. Get difficulty multiplier
    difficulty = route.difficulty if route.difficulty is not None else 0
    multiplier = DIFFICULTY_MULTIPLIER.get(difficulty, 1.0)
    
    # 4. Calculate total XP
    # Total = (base_xp + quest_xp) * difficulty_multiplier
    total_xp = int((base_xp + quest_xp) * multiplier)
    
    return {
        "base": base_xp,
        "quests": quest_xp,
        "difficulty_multiplier": multiplier,
        "total": total_xp
    }

