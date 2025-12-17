"""
Generate mock breakpoints for all routes that don't have any breakpoints yet.

This script analyzes route metadata (title, category, location, length, difficulty)
and generates appropriate breakpoints with POI names, types, and story snippets.
"""
from __future__ import annotations

import asyncio
import json
import random
from pathlib import Path
from typing import Optional

from sqlalchemy import select, func, not_
from sqlalchemy.orm import selectinload

# Allow running the script directly
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.database import get_db_session, init_db
from app.models.entities import Breakpoint, Route
from app.settings import get_settings


# POI types based on route categories
POI_TYPES_BY_CATEGORY = {
    "Jogging": ["trailhead", "city_square", "park", "riverside", "viewpoint", "finish_line"],
    "Trail running": ["trailhead", "forest", "viewpoint", "ridge", "summit", "saddle"],
    "Hiking trail": ["trailhead", "viewpoint", "forest", "mountain_pass", "summit", "shelter"],
    "Theme trail": ["trailhead", "landmark", "viewpoint", "information_point", "monument"],
    "Cycling": ["trailhead", "city_square", "riverside", "bridge", "village", "viewpoint"],
    "Mountainbiking": ["trailhead", "forest", "viewpoint", "ridge", "technical_section"],
    "Long distance cycling": ["trailhead", "village", "bridge", "landmark", "rest_area"],
    "cityTour": ["historic_square", "monument", "landmark", "market", "museum", "cathedral"],
}


def determine_num_breakpoints(route: Route) -> int:
    """Determine number of breakpoints based on route length."""
    if not route.length_meters:
        return 4  # Default
    
    length_km = route.length_meters / 1000
    
    if length_km < 2:
        return 3
    elif length_km < 5:
        return 4
    elif length_km < 10:
        return 5
    elif length_km < 20:
        return 6
    else:
        return 7


def get_poi_types_for_category(category: Optional[str]) -> list[str]:
    """Get appropriate POI types based on route category."""
    if not category:
        return ["trailhead", "viewpoint", "landmark", "rest_area", "finish_line"]
    
    for cat, types in POI_TYPES_BY_CATEGORY.items():
        if cat in category:
            return types
    
    return ["trailhead", "viewpoint", "landmark", "rest_area", "finish_line"]


def generate_poi_name(poi_type: str, index: int, total: int, route: Route) -> str:
    """Generate a reasonable POI name based on type and context."""
    location_hint = route.location or "Area"
    
    poi_names = {
        "trailhead": f"Trail Start",
        "city_square": f"City Square",
        "park": f"Park Entrance",
        "riverside": f"Riverside Path",
        "viewpoint": f"Scenic Viewpoint",
        "forest": f"Forest Clearing",
        "ridge": f"Ridge Crossing",
        "summit": f"Summit Viewpoint",
        "saddle": f"Mountain Saddle",
        "landmark": f"Landmark Point",
        "bridge": f"River Bridge",
        "village": f"Village Center",
        "historic_square": f"Historic Square",
        "monument": f"Monument Plaza",
        "market": f"Market Square",
        "museum": f"Museum Entrance",
        "cathedral": f"Cathedral Square",
        "information_point": f"Information Point",
        "mountain_pass": f"Mountain Pass",
        "shelter": f"Mountain Shelter",
        "rest_area": f"Rest Area",
        "technical_section": f"Technical Section",
        "finish_line": f"Trail Finish",
    }
    
    base_name = poi_names.get(poi_type, "Checkpoint")
    
    if index == 0:
        return f"{base_name} - Start"
    elif index == total - 1:
        return f"{base_name} - Finish"
    else:
        return f"{base_name} {index + 1}"


def generate_story_snippets(
    poi_type: str,
    poi_name: str,
    index: int,
    total: int,
    route: Route,
    category: Optional[str]
) -> tuple[str, str]:
    """Generate main quest and side plot snippets for a breakpoint."""
    
    # Main quest snippets based on POI type
    main_quests = {
        "trailhead": "Begin your adventure at the trail start and set your pace for the journey ahead.",
        "city_square": "Pass through the bustling city square, feeling the rhythm of urban life.",
        "park": "Enter the peaceful park, leaving the city noise behind.",
        "riverside": "Follow the river's edge, keeping pace with the flowing water.",
        "viewpoint": "Reach the viewpoint and take in the stunning panoramic views.",
        "forest": "Venture into the forest, surrounded by ancient trees.",
        "ridge": "Cross the exposed ridge with dramatic views on both sides.",
        "summit": "Conquer the summit and celebrate the achievement.",
        "saddle": "Pass through the mountain saddle, a natural resting point.",
        "landmark": "Discover the historic landmark, a testament to the area's heritage.",
        "bridge": "Cross the bridge and watch the water flow beneath.",
        "village": "Pass through the charming village, experiencing local culture.",
        "historic_square": "Explore the historic square, stepping back in time.",
        "monument": "Visit the monument, a symbol of historical significance.",
        "market": "Walk through the vibrant market, full of local flavors.",
        "museum": "Pass by the museum, a treasure trove of knowledge.",
        "cathedral": "Admire the cathedral, an architectural masterpiece.",
        "information_point": "Check the information point for trail insights.",
        "mountain_pass": "Cross the mountain pass, a gateway to new vistas.",
        "shelter": "Reach the mountain shelter, a welcome resting spot.",
        "rest_area": "Take a break at the rest area, recharging for the next section.",
        "technical_section": "Navigate the technical section, focusing on technique.",
        "finish_line": "Push through the final stretch and cross the finish line with pride.",
    }
    
    # Side plot snippets - more atmospheric and descriptive
    side_plots = {
        "trailhead": "Morning birdsong fills the air as you prepare for the journey.",
        "city_square": "Street musicians add a soundtrack to your passage.",
        "park": "Dappled sunlight filters through the canopy above.",
        "riverside": "Ducks glide peacefully on the water's surface.",
        "viewpoint": "A gentle breeze carries the scent of distant meadows.",
        "forest": "The forest floor is carpeted with moss and fallen leaves.",
        "ridge": "Hawks circle overhead, riding the thermal currents.",
        "summit": "The world spreads out below like a living map.",
        "saddle": "Wildflowers dot the landscape in vibrant colors.",
        "landmark": "Stone weathered by time tells stories of ages past.",
        "bridge": "The bridge's arch reflects perfectly in the water below.",
        "village": "The scent of fresh bread drifts from a nearby bakery.",
        "historic_square": "Cobblestones worn smooth by centuries of footsteps.",
        "monument": "The monument stands tall against the changing sky.",
        "market": "Colorful stalls overflow with local produce and crafts.",
        "museum": "Curious passersby stop to read the museum's facade.",
        "cathedral": "The cathedral's spires reach toward the heavens.",
        "information_point": "Informative panels share the area's natural and cultural history.",
        "mountain_pass": "Clouds drift through the pass, creating ever-changing vistas.",
        "shelter": "The shelter offers protection from the elements and a moment of peace.",
        "rest_area": "A bench invites you to pause and appreciate the moment.",
        "technical_section": "Concentration sharpens as you navigate each obstacle.",
        "finish_line": "A sense of accomplishment washes over you as you complete the route.",
    }
    
    main_quest = main_quests.get(poi_type, "Continue along the trail, taking in the surroundings.")
    side_plot = side_plots.get(poi_type, "The path unfolds before you with new discoveries at every turn.")
    
    # Customize based on route characteristics
    if route.title:
        # Add route-specific context for start and finish
        if index == 0:
            main_quest = f"Begin your {route.title.lower()} adventure. " + main_quest
        elif index == total - 1:
            main_quest = f"Complete your {route.title.lower()} journey. " + main_quest
    
    return main_quest, side_plot


def estimate_coordinates(route: Route, index: int, total: int) -> tuple[Optional[float], Optional[float]]:
    """Estimate coordinates for breakpoints based on route location."""
    # Use location string to estimate rough coordinates if available
    # For Germany routes, use approximate central coordinates
    # This is a simplified estimation - in production, you'd parse GPX data
    
    if not route.location:
        return None, None
    
    # Very rough estimates for major German regions
    location_lower = route.location.lower()
    
    # Bavaria/Munich area
    if any(word in location_lower for word in ["bavaria", "munich", "münchen", "alps"]):
        base_lat, base_lon = 48.1351, 11.5820
    # Berlin area
    elif any(word in location_lower for word in ["berlin", "brandenburg"]):
        base_lat, base_lon = 52.5200, 13.4050
    # Black Forest
    elif any(word in location_lower for word in ["black forest", "schwarzwald"]):
        base_lat, base_lon = 48.3000, 8.2000
    # Saxony
    elif any(word in location_lower for word in ["saxony", "sachsen", "dresden"]):
        base_lat, base_lon = 51.0500, 13.7373
    # Rhine area
    elif any(word in location_lower for word in ["rhine", "rhein", "cologne", "köln"]):
        base_lat, base_lon = 50.9375, 6.9603
    # Default (central Germany)
    else:
        base_lat, base_lon = 51.1657, 10.4515
    
    # Add small variations based on breakpoint index
    # This creates a rough linear progression along the route
    progress = index / max(total - 1, 1)
    lat_offset = (random.random() - 0.5) * 0.1  # ±0.05 degrees
    lon_offset = (random.random() - 0.5) * 0.1 + progress * 0.2  # More variation along route
    
    return base_lat + lat_offset, base_lon + lon_offset


def generate_breakpoints_for_route(route: Route) -> list[dict[str, any]]:
    """Generate a list of breakpoints for a given route."""
    num_bps = determine_num_breakpoints(route)
    poi_types = get_poi_types_for_category(route.category_name)
    
    breakpoints = []
    
    for i in range(num_bps):
        # Select appropriate POI type
        if i == 0:
            poi_type = "trailhead"
        elif i == num_bps - 1:
            poi_type = "finish_line"
        else:
            poi_type = random.choice([t for t in poi_types if t not in ["trailhead", "finish_line"]])
        
        poi_name = generate_poi_name(poi_type, i, num_bps, route)
        main_quest, side_plot = generate_story_snippets(poi_type, poi_name, i, num_bps, route, route.category_name)
        lat, lon = estimate_coordinates(route, i, num_bps)
        
        breakpoints.append({
            "order_index": i,
            "poi_name": poi_name,
            "poi_type": poi_type,
            "latitude": lat,
            "longitude": lon,
            "main_quest_snippet": main_quest,
            "side_plot_snippet": side_plot,
        })
    
    return breakpoints


async def main() -> None:
    """Generate breakpoints for all routes that don't have any."""
    settings = get_settings()
    init_db(settings)

    async with await get_db_session() as session:
        # Find routes without breakpoints
        # Use a subquery to check which routes have breakpoints
        routes_with_bps = select(Breakpoint.route_id).distinct()
        
        result = await session.execute(
            select(Route)
            .where(not_(Route.id.in_(routes_with_bps)))
            .order_by(Route.id)
        )
        routes_without_bps = result.scalars().all()
        
        print(f"\n{'=' * 80}")
        print(f"Found {len(routes_without_bps)} routes without breakpoints")
        print(f"{'=' * 80}\n")
        
        if not routes_without_bps:
            print("✅ All routes already have breakpoints!")
            return
        
        total_breakpoints = 0
        
        for route in routes_without_bps:
            print(f"Processing route {route.id}: {route.title[:60]}...")
            
            breakpoints = generate_breakpoints_for_route(route)
            
            for bp_data in breakpoints:
                session.add(Breakpoint(route_id=route.id, **bp_data))
                total_breakpoints += 1
            
            print(f"  ✅ Generated {len(breakpoints)} breakpoints")
        
        await session.commit()
        
        print(f"\n{'=' * 80}")
        print(f"✅ Successfully generated {total_breakpoints} breakpoints for {len(routes_without_bps)} routes")
        print(f"{'=' * 80}\n")


if __name__ == "__main__":
    asyncio.run(main())

