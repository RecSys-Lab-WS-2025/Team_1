#!/usr/bin/env python3
"""
Script to calculate and update base_xp_reward for all routes and xp_reward for mini quests.

This script implements the XP calculation formula:
- Base XP = Difficulty Score + Distance Score + Duration Score + Elevation Score
- Mini Quest XP = 25 × Difficulty Multiplier

Usage:
    python scripts/calculate_route_xp.py [--dry-run]
"""
import argparse
import asyncio
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.database import get_db_session, init_db
from app.models.entities import Route, MiniQuest, Breakpoint
from app.settings import get_settings


# XP Calculation Constants
DIFFICULTY_XP = {
    0: 20,
    1: 40,
    2: 70,
    3: 120,
}

DIFFICULTY_MULTIPLIER = {
    0: 1.0,
    1: 1.2,
    2: 1.5,
    3: 2.0,
}

BASE_QUEST_XP = 25


def calculate_difficulty_score(difficulty: int | None) -> int:
    """Calculate difficulty score."""
    if difficulty is None:
        return DIFFICULTY_XP[0]
    return DIFFICULTY_XP.get(difficulty, DIFFICULTY_XP[0])


def calculate_distance_score(length_meters: float | None) -> int:
    """Calculate distance score: min(150, length_km * 2)"""
    if length_meters is None or length_meters == 0:
        return 0
    length_km = length_meters / 1000.0
    return min(150, int(length_km * 2))


def calculate_duration_score(duration_min: int | None) -> int:
    """Calculate duration score: min(100, duration_min / 3)"""
    if duration_min is None or duration_min == 0:
        return 0
    return min(100, int(duration_min / 3))


def calculate_elevation_score(elevation: int | None) -> int:
    """Calculate elevation score: min(130, elevation / 10)"""
    if elevation is None:
        return 20  # Default for missing elevation
    return min(130, int(elevation / 10))


def calculate_base_xp_reward(route: Route) -> int:
    """
    Calculate total base XP reward for a route.
    
    Base XP = Difficulty Score + Distance Score + Duration Score + Elevation Score
    """
    difficulty_score = calculate_difficulty_score(route.difficulty)
    distance_score = calculate_distance_score(route.length_meters)
    duration_score = calculate_duration_score(route.duration_min)
    elevation_score = calculate_elevation_score(route.elevation)
    
    total = difficulty_score + distance_score + duration_score + elevation_score
    return total


def calculate_mini_quest_xp(difficulty: int | None) -> int:
    """
    Calculate XP reward for a mini quest based on route difficulty.
    
    Mini Quest XP = Base Quest XP (25) × Difficulty Multiplier
    """
    if difficulty is None:
        difficulty = 0
    multiplier = DIFFICULTY_MULTIPLIER.get(difficulty, 1.0)
    return int(BASE_QUEST_XP * multiplier)


async def update_route_xp(dry_run: bool = False) -> None:
    """
    Update base_xp_reward for all routes in the database.
    """
    settings = get_settings()
    init_db(settings)
    
    session = await get_db_session()
    try:
        # Fetch all routes with their mini quests
        result = await session.execute(
            select(Route).options(
                selectinload(Route.breakpoints).selectinload(Breakpoint.mini_quests)
            )
        )
        routes = result.scalars().all()
        
        print(f"\n{'=' * 80}")
        print(f"Found {len(routes)} routes to process")
        print(f"{'=' * 80}\n")
        
        updated_routes = 0
        updated_quests = 0
        
        for route in routes:
            # Calculate base XP reward
            old_xp = route.base_xp_reward
            new_xp = calculate_base_xp_reward(route)
            
            difficulty_score = calculate_difficulty_score(route.difficulty)
            distance_score = calculate_distance_score(route.length_meters)
            duration_score = calculate_duration_score(route.duration_min)
            elevation_score = calculate_elevation_score(route.elevation)
            
            print(f"Route {route.id}: {route.title}")
            print(f"  Difficulty: {route.difficulty} → {difficulty_score} XP")
            print(f"  Distance: {route.length_meters/1000 if route.length_meters else 0:.1f} km → {distance_score} XP")
            print(f"  Duration: {route.duration_min if route.duration_min else 0} min → {duration_score} XP")
            print(f"  Elevation: {route.elevation if route.elevation else 'N/A'} m → {elevation_score} XP")
            print(f"  Base XP: {old_xp} → {new_xp}")
            
            if not dry_run:
                route.base_xp_reward = new_xp
                updated_routes += 1
            
            # Update mini quests for this route
            quest_xp = calculate_mini_quest_xp(route.difficulty)
            for breakpoint in route.breakpoints:
                for quest in breakpoint.mini_quests:
                    old_quest_xp = quest.xp_reward
                    if not dry_run:
                        quest.xp_reward = quest_xp
                        updated_quests += 1
                    print(f"    Quest {quest.id}: {old_quest_xp} → {quest_xp} XP")
            
            print()
        
        if not dry_run:
            await session.commit()
            print(f"\n{'=' * 80}")
            print(f"✅ Updated {updated_routes} routes and {updated_quests} mini quests")
            print(f"{'=' * 80}\n")
        else:
            print(f"\n{'=' * 80}")
            print(f"🔍 DRY RUN: Would update {len(routes)} routes")
            print(f"{'=' * 80}\n")
    finally:
        await session.close()


def parse_args() -> argparse.Namespace:
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description="Calculate and update base_xp_reward for all routes"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would be updated without making changes",
    )
    return parser.parse_args()


async def async_main() -> None:
    """Main async entry point."""
    args = parse_args()
    await update_route_xp(dry_run=args.dry_run)


def main() -> None:
    """Main entry point."""
    asyncio.run(async_main())


if __name__ == "__main__":
    main()

