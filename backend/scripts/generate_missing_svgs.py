#!/usr/bin/env python3
"""
Batch generate pixel art SVGs for souvenirs that are missing pixel_image_svg.

This script:
1. Finds all souvenirs with NULL pixel_image_svg
2. Loads their route and completion data
3. Generates SVG using template system
4. Updates database with generated SVG
"""

import asyncio
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.database import get_db_session, init_db
from app.models.entities import Souvenir, Route
from app.services.svg_templates import generate_souvenir_svg
from app.settings import get_settings
from app.logger import get_logger

logger = get_logger(__name__)


async def generate_missing_svgs():
    """Generate SVGs for all souvenirs missing pixel_image_svg."""
    print("🚀 Starting batch SVG generation...")
    settings = get_settings()
    init_db(settings)
    
    session = await get_db_session()
    try:
        # Find all souvenirs with NULL or empty pixel_image_svg
        result = await session.execute(
            select(Souvenir)
            .where(
                (Souvenir.pixel_image_svg.is_(None)) | 
                (Souvenir.pixel_image_svg == "")
            )
            .options(selectinload(Souvenir.route))
        )
        souvenirs = result.scalars().all()
        
        if not souvenirs:
            print("✅ No souvenirs missing SVG. All good!")
            logger.info("✅ No souvenirs missing SVG. All good!")
            return
        
        print(f"📦 Found {len(souvenirs)} souvenirs missing SVG. Generating...")
        
        logger.info(f"📦 Found {len(souvenirs)} souvenirs missing SVG. Generating...")
        
        success_count = 0
        error_count = 0
        
        for souvenir in souvenirs:
            try:
                # Load route if not already loaded
                if not souvenir.route:
                    route_result = await session.execute(
                        select(Route).where(Route.id == souvenir.route_id)
                    )
                    souvenir.route = route_result.scalar_one_or_none()
                
                if not souvenir.route:
                    logger.warning(f"⚠️ Souvenir {souvenir.id}: Route {souvenir.route_id} not found, skipping")
                    error_count += 1
                    continue
                
                # Get route data
                route = souvenir.route
                route_title = route.title
                route_location = route.location or "Unknown Location"
                
                # Calculate distance
                distance_km = (route.length_meters / 1000) if route.length_meters else 0
                
                # Map difficulty number to string
                difficulty_map = {
                    1: "Easy",
                    2: "Moderate", 
                    3: "Difficult",
                    4: "Expert"
                }
                difficulty_str = difficulty_map.get(route.difficulty, "Moderate")
                
                # Generate SVG
                svg = generate_souvenir_svg(
                    route_title=route_title,
                    route_location=route_location,
                    completed_at=souvenir.completed_at,
                    xp_gained=souvenir.total_xp_gained,
                    distance_km=distance_km,
                    difficulty=difficulty_str
                )
                
                # Update souvenir
                souvenir.pixel_image_svg = svg
                await session.commit()
                
                logger.info(
                    f"✅ Generated SVG for souvenir {souvenir.id}: "
                    f"route={route_title}, xp={souvenir.total_xp_gained}, "
                    f"svg_length={len(svg)}"
                )
                success_count += 1
                
            except Exception as e:
                logger.error(
                    f"❌ Error generating SVG for souvenir {souvenir.id}: {e}",
                    exc_info=True
                )
                await session.rollback()
                error_count += 1
        
        summary = (
            f"\n{'='*80}\n"
            f"📊 Batch Generation Complete:\n"
            f"  ✅ Success: {success_count}\n"
            f"  ❌ Errors: {error_count}\n"
            f"  📦 Total: {len(souvenirs)}\n"
            f"{'='*80}"
        )
        print(summary)
        logger.info(summary)
        
    finally:
        await session.close()


if __name__ == "__main__":
    asyncio.run(generate_missing_svgs())

