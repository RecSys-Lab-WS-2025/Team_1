"""
Pydantic schemas for API request/response models.
These schemas provide type validation and automatic API documentation.
"""
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict


# ============================================================================
# Route Schemas
# ============================================================================

class BreakpointResponse(BaseModel):
    """Breakpoint response schema."""
    
    id: int
    route_id: int
    order_index: int
    poi_name: Optional[str] = None
    poi_type: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    main_quest_snippet: Optional[str] = None
    side_plot_snippet: Optional[str] = None
    mini_quests: list["MiniQuestResponse"] = []

    model_config = ConfigDict(from_attributes=True)


class RouteResponse(BaseModel):
    """Single route response schema with full details."""
    
    id: int
    title: str
    category_name: Optional[str] = None
    length_meters: Optional[float] = None
    duration_min: Optional[int] = None
    difficulty: Optional[int] = None
    short_description: Optional[str] = None
    xp_required: int
    story_prologue_title: Optional[str] = None
    story_prologue_body: Optional[str] = None
    story_epilogue_body: Optional[str] = None
    breakpoints: list[BreakpointResponse] = []
    is_locked: bool = False  # Computed field based on user XP

    model_config = ConfigDict(from_attributes=True)


class RouteListResponse(BaseModel):
    """Route list response schema."""
    
    routes: list[RouteResponse]
    total: int


class RouteDetailResponse(RouteResponse):
    """Route detail response with all nested data."""
    pass


# ============================================================================
# Profile Schemas
# ============================================================================

class ProfileCreate(BaseModel):
    """Create profile request schema (from questionnaire)."""
    
    fitness_level: str  # beginner/intermediate/advanced/expert
    preferred_types: list[str]  # [hiking, city-walk, trail-running]
    narrative_style: str  # adventure/mystery/nature/history


class ProfileUpdate(BaseModel):
    """Update profile request schema (partial fields)."""
    
    total_xp: Optional[int] = None
    level: Optional[int] = None
    user_vector_json: Optional[str] = None
    genai_welcome_summary: Optional[str] = None
    unlocked_routes_json: Optional[str] = None


class ProfileResponse(BaseModel):
    """Profile response schema."""
    
    id: int
    total_xp: int
    level: int
    user_vector_json: Optional[str] = None
    genai_welcome_summary: Optional[str] = None
    unlocked_routes_json: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)


class WelcomeSummaryRequest(BaseModel):
    """Request to generate welcome summary."""
    
    profile_id: int


class WelcomeSummaryResponse(BaseModel):
    """Welcome summary response."""
    
    summary: str


# ============================================================================
# MiniQuest Schemas
# ============================================================================

class MiniQuestResponse(BaseModel):
    """MiniQuest response schema."""
    
    id: int
    breakpoint_id: int
    task_description: str
    xp_reward: int

    model_config = ConfigDict(from_attributes=True)


class QuestCompleteRequest(BaseModel):
    """Complete quest request schema."""
    
    quest_id: int


class QuestCompleteResponse(BaseModel):
    """Complete quest response schema."""
    
    xp_gained: int
    new_total_xp: int
    new_level: int


# ============================================================================
# Souvenir Schemas
# ============================================================================

class SouvenirResponse(BaseModel):
    """Souvenir response schema."""
    
    id: int
    demo_profile_id: int
    route_id: int
    completed_at: datetime
    total_xp_gained: int
    genai_summary: Optional[str] = None
    xp_breakdown_json: Optional[str] = None
    route: Optional[RouteResponse] = None  # Nested route info

    model_config = ConfigDict(from_attributes=True)


class SouvenirListResponse(BaseModel):
    """Souvenir list response schema."""
    
    souvenirs: list[SouvenirResponse]
    total: int


# ============================================================================
# Feedback Schemas
# ============================================================================

class FeedbackCreate(BaseModel):
    """Create feedback request schema."""
    
    route_id: int
    reason: str  # too_difficult, too_far, not_interested, too_easy, etc.


class FeedbackResponse(BaseModel):
    """Feedback response schema."""
    
    id: int
    demo_profile_id: int
    route_id: int
    reason: str

    model_config = ConfigDict(from_attributes=True)


# ============================================================================
# Recommendation Schemas
# ============================================================================

class RecommendationRequest(BaseModel):
    """Recommendation request schema (query parameters)."""
    
    activity_type: Optional[str] = None  # hiking/city-walk/trail-running


class RecommendationResponse(BaseModel):
    """Recommendation response schema."""
    
    routes: list[RouteResponse]
    total: int


# ============================================================================
# Route Completion Schemas
# ============================================================================

class RouteCompleteRequest(BaseModel):
    """Complete route request schema."""
    
    completed_quest_ids: list[int] = []  # List of completed quest IDs


class RouteCompleteResponse(BaseModel):
    """Complete route response schema."""
    
    souvenir: SouvenirResponse
    xp_breakdown: dict  # {"base": 100, "distance": 30, "quests": 20, "total": 150}
    total_xp_gained: int
    new_level: int


# ============================================================================
# XP Schemas
# ============================================================================

class XPBreakdownResponse(BaseModel):
    """XP breakdown response schema."""
    
    base_xp: int
    distance_xp: int
    difficulty_xp: int
    quest_xp: int
    total: int
    xp_to_next_level: int


# ============================================================================
# Route Simulation Schemas
# ============================================================================

class RouteStartRequest(BaseModel):
    """Start route simulation request."""
    
    route_id: int


class RouteStartResponse(BaseModel):
    """Start route simulation response."""
    
    route: RouteResponse
    current_breakpoint_index: int = 0


class RouteProgressUpdate(BaseModel):
    """Update route progress request."""
    
    current_breakpoint_index: int


class RouteProgressResponse(BaseModel):
    """Route progress response."""
    
    current_breakpoint: BreakpointResponse
    current_breakpoint_index: int
    total_breakpoints: int
    progress_percentage: float


# ============================================================================
# Story Generation Schemas
# ============================================================================

class StoryGenerateRequest(BaseModel):
    """Generate story request schema."""
    
    profile_id: Optional[int] = None  # For personalization


class StoryGenerateResponse(BaseModel):
    """Generate story response schema."""
    
    prologue_title: Optional[str] = None
    prologue_body: Optional[str] = None
    epilogue_body: Optional[str] = None


# Update forward references
BreakpointResponse.model_rebuild()

