/**
 * Utility functions to transform backend API responses to frontend data structures
 */

import {
  ApiRoute,
  ApiBreakpoint,
  ApiSouvenir,
  mapApiDifficulty,
  mapApiCategory,
  RecommendationScoreBreakdown,
} from "./api-types";
import { Route, Breakpoint, MiniQuest, DigitalSouvenir } from "./mock-data";

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
 * Generate mock coordinates for a breakpoint based on route location and order
 * This is a fallback when backend doesn't provide coordinates
 */
function generateMockCoordinates(
  routeLocation: string | null,
  orderIndex: number,
  totalBreakpoints: number
): { latitude: number; longitude: number } {
  // Try to extract approximate location from route location string
  // Default to Germany center if no location info
  let baseLat = 51.0;
  let baseLng = 10.0;

  if (routeLocation) {
    const lower = routeLocation.toLowerCase();
    // Munich area
    if (lower.includes("munich") || lower.includes("münchen")) {
      baseLat = 48.1351;
      baseLng = 11.582;
    }
    // Berlin area
    else if (lower.includes("berlin")) {
      baseLat = 52.52;
      baseLng = 13.405;
    }
    // Black Forest area
    else if (lower.includes("black forest") || lower.includes("schwarzwald")) {
      baseLat = 48.0;
      baseLng = 8.0;
    }
    // Bavarian Alps
    else if (lower.includes("alps") || lower.includes("bavarian")) {
      baseLat = 47.5;
      baseLng = 11.0;
    }
    // Rhine area
    else if (lower.includes("rhine") || lower.includes("rhein")) {
      baseLat = 50.0;
      baseLng = 7.5;
    }
    // Saxon Switzerland
    else if (lower.includes("saxon") || lower.includes("sächsische")) {
      baseLat = 50.96;
      baseLng = 14.07;
    }
  }

  // Generate coordinates along a path
  // Add variations based on order index to create a route-like path
  // Use larger variations to ensure breakpoints don't overlap
  const progress = totalBreakpoints > 1 ? orderIndex / (totalBreakpoints - 1) : 0;
  // Increase variation: 0.2 degree ≈ 22km, enough to prevent overlap
  const latitude = baseLat + (progress * 0.2) + (Math.sin(progress * Math.PI * 2) * 0.1);
  const longitude = baseLng + (progress * 0.2) + (Math.cos(progress * Math.PI * 2) * 0.1);

  return { latitude, longitude };
}

/**
 * Transform API breakpoint to frontend breakpoint
 */
function transformBreakpoint(
  apiBreakpoint: ApiBreakpoint,
  routeLocation: string | null = null,
  totalBreakpoints: number = 1
): Breakpoint {
  // Determine breakpoint type based on content
  let type: "story" | "quest" | "checkpoint" = "checkpoint";

  if (apiBreakpoint.main_quest_snippet) {
    type = "story";
  }
  if (apiBreakpoint.mini_quests && apiBreakpoint.mini_quests.length > 0) {
    type = "quest";
  }

  // Transform first mini quest if available
  let quest: MiniQuest | undefined;
  if (apiBreakpoint.mini_quests && apiBreakpoint.mini_quests.length > 0) {
    const apiQuest = apiBreakpoint.mini_quests[0];
    
    // Try to parse task_description as JSON (for quiz quests)
    let questType: "photo" | "quiz" | "observation" = "observation";
    let description = apiQuest.task_description;
    let choices: string[] | undefined;
    let correctAnswer: number | undefined;
    
    try {
      const parsed = JSON.parse(apiQuest.task_description);
      if (parsed.type === "quiz") {
        questType = "quiz";
        description = parsed.description || parsed.question;
        choices = parsed.choices;
        correctAnswer = parsed.correct_answer;
      } else if (parsed.type === "photo") {
        questType = "photo";
        description = parsed.description || apiQuest.task_description;
      }
    } catch (e) {
      // Not JSON, use as-is
      // Determine type from description
      if (apiQuest.task_description.toLowerCase().includes("camera") || 
          apiQuest.task_description.toLowerCase().includes("photograph")) {
        questType = "photo";
      } else if (apiQuest.task_description.toLowerCase().includes("puzzle") ||
                 apiQuest.task_description.toLowerCase().includes("riddle") ||
                 apiQuest.task_description.toLowerCase().includes("solve")) {
        questType = "quiz";
        // Generate default quiz if not provided
        choices = [
          "Option A",
          "Option B", 
          "Option C",
          "Option D"
        ];
        correctAnswer = 0;
      }
    }
    
    quest = {
      id: String(apiQuest.id),
      title: `Quest at ${apiBreakpoint.poi_name || "Checkpoint"}`,
      description: description,
      type: questType,
      xpReward: apiQuest.xp_reward,
      choices: choices,
      correctAnswer: correctAnswer,
    };
  }

  // Use backend coordinates if available, otherwise generate mock coordinates
  let latitude: number | undefined;
  let longitude: number | undefined;
  if (apiBreakpoint.latitude !== null && apiBreakpoint.longitude !== null) {
    latitude = apiBreakpoint.latitude;
    longitude = apiBreakpoint.longitude;
  } else {
    // Generate mock coordinates as fallback
    const mockCoords = generateMockCoordinates(
      routeLocation,
      apiBreakpoint.order_index,
      totalBreakpoints
    );
    latitude = mockCoords.latitude;
    longitude = mockCoords.longitude;
  }

  return {
    id: String(apiBreakpoint.id),
    name:
      apiBreakpoint.poi_name || `Checkpoint ${apiBreakpoint.order_index + 1}`,
    distance: apiBreakpoint.order_index, // Could be enhanced with actual distance from route start
    type,
    content: apiBreakpoint.main_quest_snippet || undefined,
    quest,
    latitude,
    longitude,
    orderIndex: apiBreakpoint.order_index,
  };
}

/**
 * Transform API route to frontend route
 *
 * This function converts backend ApiRoute data to the frontend Route interface,
 * mapping the base_xp_reward to xpReward and handling all other field transformations.
 */
export function transformApiRoute(apiRoute: ApiRoute): Route {
  // Parse tags_json and take maximum 3 tags
  let tags: string[] = [];
  if (apiRoute.tags_json) {
    try {
      const parsedTags = JSON.parse(apiRoute.tags_json);
      if (Array.isArray(parsedTags)) {
        tags = parsedTags.slice(0, 3); // Take only first 3 tags
      }
    } catch (e) {
      console.warn(`Failed to parse tags_json for route ${apiRoute.id}:`, e);
    }
  }

  // Sort breakpoints by order_index to ensure correct order
  const sortedBreakpoints = [...apiRoute.breakpoints].sort(
    (a, b) => a.order_index - b.order_index
  );

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
    tags: tags, // Parsed from tags_json, max 3 tags
    isLocked: apiRoute.is_locked,
    xpRequired: apiRoute.xp_required,
    breakpoints: sortedBreakpoints.map((bp) =>
      transformBreakpoint(bp, apiRoute.location, sortedBreakpoints.length)
    ),
    prologue: apiRoute.story_prologue_body || undefined,
    epilogue: apiRoute.story_epilogue_body || undefined,
    recommendationScore: apiRoute.recommendation_score ?? undefined,
    recommendationScoreBreakdown: apiRoute.recommendation_score_breakdown ?? undefined,
    gpxData: apiRoute.gpx_data_raw || undefined,
  };
}

/**
 * Transform multiple API routes to frontend routes
 */
export function transformApiRoutes(apiRoutes: ApiRoute[]): Route[] {
  return apiRoutes.map(transformApiRoute);
}

/**
 * Transform API souvenir to frontend DigitalSouvenir
 */
export function transformApiSouvenir(apiSouvenir: ApiSouvenir): DigitalSouvenir {
  // Get route info if available
  const route = apiSouvenir.route;
  const routeName = route?.title || `Route ${apiSouvenir.route_id}`;
  const location = route?.location || "Unknown location";
  const difficulty = route?.difficulty !== null && route?.difficulty !== undefined
    ? mapApiDifficulty(route.difficulty)
    : "easy";
  const distance = route?.length_meters
    ? Number((route.length_meters / 1000).toFixed(1))
    : 0;
  
  // Get image URL from route or use default
  const imageUrl = route
    ? ROUTE_IMAGES[route.id % ROUTE_IMAGES.length]
    : "/placeholder.svg";
  
  // Parse badges from genai_summary or use default
  const badgesEarned: string[] = ["Completed"];
  if (apiSouvenir.genai_summary) {
    // Could extract badges from summary or XP breakdown in the future
  }
  
  return {
    id: String(apiSouvenir.id),
    routeId: String(apiSouvenir.route_id),
    routeName,
    location,
    completedAt: new Date(apiSouvenir.completed_at),
    xpGained: apiSouvenir.total_xp_gained,
    badgesEarned,
    imageUrl,
    difficulty,
    distance,
    genaiSummary: apiSouvenir.genai_summary,
    xpBreakdown: apiSouvenir.xp_breakdown_json,
    pixelImageSvg: apiSouvenir.pixel_image_svg,
  };
}

/**
 * Transform multiple API souvenirs to frontend DigitalSouvenir array
 */
export function transformApiSouvenirs(apiSouvenirs: ApiSouvenir[]): DigitalSouvenir[] {
  return apiSouvenirs.map(transformApiSouvenir);
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
