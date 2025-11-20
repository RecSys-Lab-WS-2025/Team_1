/**
 * TypeScript types for TrailSaga Backend API responses
 * These match the Pydantic schemas defined in backend/app/api/schemas.py
 */

export interface ApiBreakpoint {
  id: number;
  route_id: number;
  order_index: number;
  poi_name: string | null;
  poi_type: string | null;
  latitude: number | null;
  longitude: number | null;
  main_quest_snippet: string | null;
  side_plot_snippet: string | null;
  mini_quests: ApiMiniQuest[];
}

export interface ApiMiniQuest {
  id: number;
  breakpoint_id: number;
  task_description: string;
  xp_reward: number;
}

export interface ApiRoute {
  id: number;
  title: string;
  category_name: string | null;
  length_meters: number | null;
  duration_min: number | null;
  difficulty: number | null; // 0-3 scale
  short_description: string | null;
  location: string | null;
  elevation: number | null;
  xp_required: number; // XP needed to unlock this route
  base_xp_reward: number; // XP earned from completing this route (Base XP)
  story_prologue_title: string | null;
  story_prologue_body: string | null;
  story_epilogue_body: string | null;
  breakpoints: ApiBreakpoint[];
  is_locked: boolean; // Computed field based on user XP
}

export interface ApiRecommendationResponse {
  routes: ApiRoute[];
  total: number;
  is_personalized: boolean;
}

export interface ApiProfile {
  id: number;
  total_xp: number;
  level: number;
  user_vector_json: string | null;
  genai_welcome_summary: string | null;
  unlocked_routes_json: string | null;
}

export interface ApiProfileCreate {
  fitness: string; // "beginner" | "intermediate" | "advanced"
  type: string[]; // ["history-culture", "natural-scenery", "family-fun"]
  narrative: string; // "adventure" | "mystery" | "playful"
}

export interface ApiSouvenir {
  id: number;
  demo_profile_id: number;
  route_id: number;
  completed_at: string; // ISO datetime string
  total_xp_gained: number;
  genai_summary: string | null;
  xp_breakdown_json: string | null; // JSON string containing XP breakdown details
  route?: ApiRoute;
}

/**
 * XP Breakdown structure (stored as JSON string in xp_breakdown_json)
 */
export interface XpBreakdown {
  base_xp: {
    difficulty: number;
    distance: number;
    duration: number;
    elevation: number;
    total: number;
  };
  mini_quests: {
    completed_count: number;
    total_xp: number;
    details: Array<{
      quest_id: number;
      description: string;
      xp: number;
    }>;
  };
  total_xp_gained: number;
}

/**
 * Helper function to map API difficulty (0-3) to frontend difficulty labels
 * 0 -> easy, 1 -> moderate, 2 -> difficult, 3 -> expert
 */
export function mapApiDifficulty(
  difficulty: number | null
): "easy" | "medium" | "hard" | "expert" {
  if (difficulty === null || difficulty === 0) return "easy";
  if (difficulty === 1) return "medium"; // "moderate" displayed as "medium" in UI
  if (difficulty === 2) return "hard"; // "difficult" displayed as "hard" in UI
  return "expert";
}

/**
 * Helper function to map API category_name to frontend route type
 * Maps backend category_name values to frontend categories based on CATEGORY_MAPPING
 */
export function mapApiCategory(
  categoryName: string | null
): "hiking" | "running" | "cycling" {
  if (!categoryName) return "hiking";

  const lower = categoryName.toLowerCase();
  
  // Running: "Jogging", "Trail running"
  if (lower.includes("run") || lower.includes("jogging"))
    return "running";
  
  // Cycling: "Cycling", "Mountainbiking", "Long distance cycling"
  if (lower.includes("cycling") || lower.includes("mountain") || lower.includes("bike"))
    return "cycling";
  
  // Hiking: "Theme trail", "Hiking trail", and everything else
  return "hiking";
}
