/**
 * Utility functions to transform backend API responses to frontend data structures
 */

import {
  ApiRoute,
  ApiBreakpoint,
  mapApiDifficulty,
  mapApiCategory,
} from "./api-types";
import { Route, Breakpoint, MiniQuest } from "./mock-data";

/**
 * Pool of available route images for random assignment
 */
const ROUTE_IMAGES = [
  "/black-forest-hiking-trail-misty-morning.jpg",
  "/bavarian-alps-mountain-summit-sunrise.jpg",
  "/berlin-wall-memorial-east-side-gallery.jpg",
  "/munich-city-center-marienplatz.jpg",
  "/rhine-river-valley-vineyards-castle.jpg",
  "/saxon-switzerland-bastei-bridge-rock-formation.jpg",
];

/**
 * Transform API breakpoint to frontend breakpoint
 */
function transformBreakpoint(apiBreakpoint: ApiBreakpoint): Breakpoint {
  // Determine breakpoint type based on content
  let type: "story" | "quest" | "checkpoint" = "checkpoint";

  if (apiBreakpoint.main_quest_snippet || apiBreakpoint.side_plot_snippet) {
    type = "story";
  }
  if (apiBreakpoint.mini_quests && apiBreakpoint.mini_quests.length > 0) {
    type = "quest";
  }

  // Transform first mini quest if available
  let quest: MiniQuest | undefined;
  if (apiBreakpoint.mini_quests && apiBreakpoint.mini_quests.length > 0) {
    const apiQuest = apiBreakpoint.mini_quests[0];
    quest = {
      id: String(apiQuest.id),
      title: `Quest at ${apiBreakpoint.poi_name || "Checkpoint"}`,
      description: apiQuest.task_description,
      type: "observation", // Default type, could be enhanced with backend data
      xpReward: apiQuest.xp_reward,
    };
  }

  return {
    id: String(apiBreakpoint.id),
    name:
      apiBreakpoint.poi_name || `Checkpoint ${apiBreakpoint.order_index + 1}`,
    distance: apiBreakpoint.order_index, // Could be enhanced with actual distance from route start
    type,
    content:
      apiBreakpoint.main_quest_snippet ||
      apiBreakpoint.side_plot_snippet ||
      undefined,
    quest,
  };
}

/**
 * Transform API route to frontend route
 *
 * This function converts backend ApiRoute data to the frontend Route interface,
 * mapping the base_xp_reward to xpReward and handling all other field transformations.
 */
export function transformApiRoute(apiRoute: ApiRoute): Route {
  return {
    id: String(apiRoute.id),
    name: apiRoute.title,
    type: mapApiCategory(apiRoute.category_name),
    difficulty: mapApiDifficulty(apiRoute.difficulty),
    distance: apiRoute.length_meters
      ? Number((apiRoute.length_meters / 1000).toFixed(1))
      : 0,
    elevation: apiRoute.elevation || 0,
    duration: apiRoute.duration_min || 0,
    location: apiRoute.location || "Unknown location",
    description: apiRoute.short_description || "No description available",
    imageUrl: ROUTE_IMAGES[apiRoute.id % ROUTE_IMAGES.length],
    xpReward: apiRoute.base_xp_reward, // ⭐ Base XP reward from backend
    rating: 4.5, // Could be enhanced with actual rating data from backend
    completions: 100, // Could be enhanced with actual completion count from backend
    tags: [], // Could be enhanced by parsing tags_json from backend
    isLocked: apiRoute.is_locked,
    xpRequired: apiRoute.xp_required,
    breakpoints: apiRoute.breakpoints.map(transformBreakpoint),
    prologue: apiRoute.story_prologue_body || undefined,
    epilogue: apiRoute.story_epilogue_body || undefined,
  };
}

/**
 * Transform multiple API routes to frontend routes
 */
export function transformApiRoutes(apiRoutes: ApiRoute[]): Route[] {
  return apiRoutes.map(transformApiRoute);
}

/**
 * Example usage with apiClient:
 *
 * ```typescript
 * import { apiClient, ApiRecommendationResponse } from '@/lib/api-client';
 * import { transformApiRoutes } from '@/lib/api-transforms';
 *
 * async function fetchRoutes(profileId?: number) {
 *   const response = await apiClient.get<ApiRecommendationResponse>(
 *     `/api/v1/routes/recommendations?profile_id=${profileId}&limit=20`
 *   );
 *   const frontendRoutes = transformApiRoutes(response.routes);
 *   return frontendRoutes;
 * }
 * ```
 */
