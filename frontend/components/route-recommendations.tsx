"use client";

import { useState, useEffect } from "react";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { mockRoutes, UserProfile, Route } from "@/lib/mock-data";
import { apiClient } from "@/lib/api-client";
import { ApiRecommendationResponse } from "@/lib/api-types";
import { transformApiRoutes, transformApiSouvenir } from "@/lib/api-transforms";
import { logger } from "@/lib/logger";
import {
  Mountain,
  MapPin,
  Clock,
  TrendingUp,
  Heart,
  ThumbsDown,
  SkipForward,
  CheckCircle2,
  Lock,
  Sparkles,
  User,
  Bike,
} from "lucide-react";
import { RouteDetailModal } from "@/components/route-detail-modal";
import { HikingSimulator } from "@/components/hiking-simulator";
import { FeedbackDialog } from "@/components/feedback-dialog";
import { UserProfileModal } from "@/components/user-profile-modal";
import { SouvenirGallery } from "@/components/souvenir-gallery";
import { RecommendationScoreModal } from "@/components/recommendation-score-modal";

interface RouteRecommendationsProps {
  userProfile: UserProfile;
  isLoggedIn: boolean;
  onUpdateProfile: (profile: UserProfile) => void;
  onGoToQuestionnaire?: () => void;
  // </CHANGE>
}

// Helper function to display difficulty labels
const getDifficultyLabel = (difficulty: Route["difficulty"]): string => {
  const labels: Record<Route["difficulty"], string> = {
    easy: "easy",
    medium: "moderate",
    hard: "difficult",
    expert: "expert",
  };
  return labels[difficulty];
};

export function RouteRecommendations({
  userProfile,
  isLoggedIn,
  onUpdateProfile,
  onGoToQuestionnaire,
}: RouteRecommendationsProps) {
  const [selectedRoute, setSelectedRoute] = useState<Route | null>(null);
  const [activeRoute, setActiveRoute] = useState<Route | null>(null);
  const [selectedType, setSelectedType] = useState<
    "all" | "running" | "hiking" | "cycling"
  >("all");
  const [feedbackRoute, setFeedbackRoute] = useState<Route | null>(null);
  const [showProfile, setShowProfile] = useState(false);
  const [showGallery, setShowGallery] = useState(false);
  const [galleryRefreshTrigger, setGalleryRefreshTrigger] = useState(0);
  const [backendRoutes, setBackendRoutes] = useState<Route[]>([]);
  const [isLoadingRoutes, setIsLoadingRoutes] = useState(false);
  const [backendError, setBackendError] = useState<string | null>(null);
  const [scoreModalRoute, setScoreModalRoute] = useState<Route | null>(null);
  const [routeLimit, setRouteLimit] = useState<number>(20);
  const [isGeneratingStory, setIsGeneratingStory] = useState(false);
  const [storyGenerationRouteId, setStoryGenerationRouteId] = useState<string | null>(null);

  const scrollToMainTop = () => {
    if (typeof window !== "undefined") {
      window.scrollTo({ top: 0, behavior: "smooth" });
    }
  };

  // Fetch routes from backend (for both logged-in and guest users)
  useEffect(() => {
    logger.logComponentLifecycle('RouteRecommendations', 'mount', { isLoggedIn, userProfileId: userProfile.id });
    fetchBackendRoutes();
    
    return () => {
      logger.logComponentLifecycle('RouteRecommendations', 'unmount');
    };
  }, [isLoggedIn, selectedType, userProfile.id, routeLimit]);

  const fetchBackendRoutes = async () => {
    const startTime = performance.now();
    setIsLoadingRoutes(true);
    setBackendError(null);

    logger.info('Start fetching route recommendations', { isLoggedIn, selectedType, routeLimit, userProfileId: userProfile.id }, 'RouteRecommendations', 'FETCH_ROUTES');

    try {
      // Build API URL with optional profile_id and category parameters
      let url = `api/routes/recommendations?limit=${routeLimit}`;

      // Add profile_id for logged-in users (for personalized CBF recommendations)
      // Convert string ID to integer (backend expects int, frontend stores as string)
      if (isLoggedIn && userProfile.id) {
        const profileIdNum = parseInt(userProfile.id, 10);
        if (!isNaN(profileIdNum)) {
          url += `&profile_id=${profileIdNum}`;
        }
      }

      // Add category filter if selected
      if (selectedType !== "all") {
        url += `&category=${selectedType}`;
      }

      logger.debug('Fetching route recommendations', { url }, 'RouteRecommendations', 'FETCH_ROUTES');
      // Use longer timeout for route recommendations (30 seconds should be enough)
      const response = await apiClient.get<ApiRecommendationResponse>(url, undefined, 30000);
      
      const duration = performance.now() - startTime;
      logger.info('Route recommendations fetched successfully', { 
        routesCount: response.routes.length, 
        isPersonalized: response.is_personalized,
        duration: duration.toFixed(2) + 'ms'
      }, 'RouteRecommendations', 'FETCH_ROUTES');
      
      const routes = transformApiRoutes(response.routes);
      setBackendRoutes(routes);

      // Log personalization status
      if (response.is_personalized) {
        logger.logBusinessLogic('Show personalized recommendations', 'Route', undefined, { count: routes.length }, 'RouteRecommendations');
      } else {
        logger.logBusinessLogic('Show random recommendations', 'Route', undefined, { count: routes.length }, 'RouteRecommendations');
      }
      
      logger.logPerformance('Fetch route recommendations', duration, 'RouteRecommendations', { routesCount: routes.length });
    } catch (error: any) {
      const duration = performance.now() - startTime;
      logger.error("Failed to fetch route recommendations", error, 'RouteRecommendations', 'FETCH_ROUTES');
      logger.debug("Error details", {
        message: error?.message,
        status: error?.status,
        name: error?.name,
        duration: duration.toFixed(2) + 'ms'
      }, 'RouteRecommendations', 'FETCH_ROUTES');
      
      // Provide more specific error messages
      let errorMessage = "Could not load routes from server. Showing sample routes instead.";
      
      if (error instanceof Error) {
        if (error.message.includes("Network error") || error.message.includes("Failed to fetch")) {
          errorMessage = "Network error: Could not connect to the server. Please check if the backend is running on http://localhost:8000";
        } else if (error.message.includes("timeout")) {
          errorMessage = "Request timeout: The server took too long to respond. Please try again.";
        } else if (error.status === 404) {
          errorMessage = `API endpoint not found (404). Tried: ${url}. Please check the backend configuration.`;
        } else if (error.status >= 500) {
          errorMessage = "Server error: The backend encountered an issue. Please try again later.";
        } else {
          errorMessage = `Error loading routes: ${error.message}`;
        }
      } else if (error?.status === 404) {
        errorMessage = `API endpoint not found (404). Tried: ${url}. Please check the backend configuration.`;
      }
      
      setBackendError(errorMessage);
      setBackendRoutes([]); // Fallback to mock
    } finally {
      setIsLoadingRoutes(false);
    }
  };

  // Get recommended routes (from backend or fallback to mock)
  const getRecommendedRoutes = () => {
    // Use backend routes if available, otherwise fallback to mock
    // Backend routes are already sorted by CBF for logged-in users
    // or randomized for guest users
    const sourceRoutes = backendRoutes.length > 0 ? backendRoutes : mockRoutes;

    let routes = [...sourceRoutes];

    // Only apply client-side filtering if using mock data
    if (backendRoutes.length === 0) {
      // Filter by type if selected
      if (selectedType !== "all") {
        routes = routes.filter((r) => r.type === selectedType);
      }

      // Apply simple client-side sorting for mock data
      if (isLoggedIn) {
        routes = routes.sort((a, b) => {
          let scoreA = 0;
          let scoreB = 0;

          // Preferred types
          if (userProfile.preferredTypes.includes(a.type)) scoreA += 10;
          if (userProfile.preferredTypes.includes(b.type)) scoreB += 10;

          // Fitness level matching
          const difficultyScore: Record<string, Record<string, number>> = {
            beginner: { easy: 10, medium: 5, hard: 0, expert: -5 },
            intermediate: { easy: 5, medium: 10, hard: 5, expert: 0 },
            advanced: { easy: 0, medium: 5, hard: 10, expert: 5 },
            expert: { easy: -5, medium: 0, hard: 5, expert: 10 },
          };

          scoreA +=
            difficultyScore[userProfile.fitnessLevel][a.difficulty] || 0;
          scoreB +=
            difficultyScore[userProfile.fitnessLevel][b.difficulty] || 0;

          // Completed routes go to bottom
          if (userProfile.completedRoutes.includes(a.id)) scoreA -= 20;
          if (userProfile.completedRoutes.includes(b.id)) scoreB -= 20;

          return scoreB - scoreA;
        });
      }
    }

    return routes;
  };

  const handleStartRoute = async (route: Route) => {
    // Close any open route detail modal when starting a route
    setSelectedRoute(null);
    if (route.isLocked && userProfile.xp < (route.xpRequired || 0)) {
      return;
    }
    
    // Check if route has story content loaded
    // For Wiesn route, we want to always generate/load the full story
    // For other routes, check if we have prologue or any breakpoint with substantial content (>100 chars)
    const isWiesnRoute = route.id === "1362610" || route.name.toLowerCase().includes("wiesn");
    const hasStoryContent = route.prologue || route.breakpoints?.some(bp => bp.content && bp.content.length > 100);
    
    // Always generate/load story for Wiesn route, or if we don't have substantial content
    const shouldLoadStory = isWiesnRoute || !hasStoryContent;
    
    console.log(`🔍 Starting route ${route.id} (${route.name}):`, {
      isWiesnRoute,
      hasStoryContent,
      shouldLoadStory,
      prologue: route.prologue ? `${route.prologue.length} chars` : 'none',
      breakpointsWithContent: route.breakpoints?.filter(bp => bp.content && bp.content.length > 100).length || 0
    });
    
    // If no story content or it's Wiesn route, try to load or generate it
    if (shouldLoadStory) {
      setIsGeneratingStory(true);
      setStoryGenerationRouteId(route.id);
      try {
        const routeIdNum = parseInt(route.id, 10);
        if (!isNaN(routeIdNum)) {
          let storyResponse;
          
          // For Wiesn route, always try to generate (force regenerate to ensure we get the full story)
          // For other routes, first try to get existing story
          if (isWiesnRoute) {
            console.log('📖 Wiesn route detected! Generating/loading full story...');
            // First try to get existing story
            try {
              storyResponse = await apiClient.get<{
                title: string;
                outline: string;
                prologue: string;
                epilogue: string;
                breakpoints: Array<{
                  index: number;
                  main_quest: string;
                  mini_quests: Array<{
                    task_description: string;
                    xp_reward: number;
                  }>;
                }>;
              }>(`api/routes/${routeIdNum}/story`, undefined, 10000);
              console.log('✅ Found existing story for Wiesn route');
            } catch (error: any) {
              // If story doesn't exist or is incomplete, generate it
              if (error?.status === 404 || error?.status === 0) {
                console.log('📖 Story not found or incomplete, generating new story (this may take up to 60 seconds)...');
                storyResponse = await apiClient.post<{
                  title: string;
                  outline: string;
                  prologue: string;
                  epilogue: string;
                  breakpoints: Array<{
                    index: number;
                    main_quest: string;
                    mini_quests: Array<{
                      task_description: string;
                      xp_reward: number;
                    }>;
                  }>;
                }>(`api/routes/${routeIdNum}/generate-story`, {
                  narrative_style: "adventure",
                  force_regenerate: false
                }, undefined, 60000); // 60 seconds for story generation
                console.log('✅ Story generated successfully!');
              } else {
                throw error;
              }
            }
          } else {
            // For non-Wiesn routes, try to get existing story first
            try {
              storyResponse = await apiClient.get<{
                title: string;
                outline: string;
                prologue: string;
                epilogue: string;
                breakpoints: Array<{
                  index: number;
                  main_quest: string;
                  mini_quests: Array<{
                    task_description: string;
                    xp_reward: number;
                  }>;
                }>;
              }>(`api/routes/${routeIdNum}/story`, undefined, 10000); // 10 seconds for existing story
            } catch (error: any) {
              // If story doesn't exist (404), generate it (with longer timeout for generation)
              if (error?.status === 404) {
                console.log('📖 Story not found, generating new story (this may take up to 60 seconds)...');
                storyResponse = await apiClient.post<{
                  title: string;
                  outline: string;
                  prologue: string;
                  epilogue: string;
                  breakpoints: Array<{
                    index: number;
                    main_quest: string;
                    mini_quests: Array<{
                      task_description: string;
                      xp_reward: number;
                    }>;
                  }>;
                }>(`api/routes/${routeIdNum}/generate-story`, {
                  narrative_style: "adventure",
                  force_regenerate: false
                }, undefined, 60000); // 60 seconds for story generation
                console.log('✅ Story generated successfully!');
              } else {
                throw error;
              }
            }
          }
          
          // Update route with story content
          const updatedRoute = {
            ...route,
            prologue: storyResponse.prologue,
            epilogue: storyResponse.epilogue,
            breakpoints: route.breakpoints.map((bp, idx) => {
              // Match by order_index (which should match the index in storyResponse.breakpoints)
              const storyBp = storyResponse.breakpoints.find(sb => sb.index === (bp.orderIndex ?? idx));
              if (storyBp) {
                console.log(`✅ Found story for breakpoint ${idx} (orderIndex: ${bp.orderIndex}): ${storyBp.main_quest.substring(0, 100)}...`);
                // Parse mini quest description for quiz type
                let questType: "photo" | "quiz" | "observation" = "observation";
                let questDescription = storyBp.mini_quests[0]?.task_description || "";
                let choices: string[] | undefined;
                let correctAnswer: number | undefined;
                
                if (storyBp.mini_quests.length > 0) {
                  try {
                    const parsed = JSON.parse(storyBp.mini_quests[0].task_description);
                    if (parsed.type === "quiz") {
                      questType = "quiz";
                      questDescription = parsed.description || parsed.question;
                      choices = parsed.choices;
                      correctAnswer = parsed.correct_answer;
                    } else if (parsed.type === "photo") {
                      questType = "photo";
                      questDescription = parsed.description;
                    } else if (parsed.type === "observation") {
                      questType = "observation";
                      questDescription = parsed.description;
                    } else if (parsed.description) {
                      // Default: use parsed description if available
                      questDescription = parsed.description;
                    }
                  } catch (e) {
                    // Not JSON, use as-is
                    if (questDescription.toLowerCase().includes("camera") || 
                        questDescription.toLowerCase().includes("photograph")) {
                      questType = "photo";
                    } else if (questDescription.toLowerCase().includes("puzzle") ||
                               questDescription.toLowerCase().includes("riddle")) {
                      questType = "quiz";
                    }
                  }
                }
                
                return {
                  ...bp,
                  content: storyBp.main_quest || bp.content, // Use story content, fallback to existing
                  quest: storyBp.mini_quests.length > 0 ? {
                    id: `quest-${bp.id || idx}`,
                    title: `Quest at ${bp.name || 'Checkpoint'}`,
                    description: questDescription,
                    type: questType,
                    xpReward: storyBp.mini_quests[0].xp_reward,
                    choices: choices,
                    correctAnswer: correctAnswer
                  } : bp.quest
                };
              } else {
                console.warn(`⚠️ No story found for breakpoint ${idx} (orderIndex: ${bp.orderIndex ?? idx}), available indices:`, storyResponse.breakpoints.map(sb => sb.index));
                // Keep existing content if no story found
              }
              return bp;
            })
          };
          
          console.log('📖 Updated route with story:', {
            prologueLength: updatedRoute.prologue?.length,
            epilogueLength: updatedRoute.epilogue?.length,
            breakpointsWithContent: updatedRoute.breakpoints.filter(bp => bp.content && bp.content.length > 100).length,
            totalBreakpoints: updatedRoute.breakpoints.length
          });
          
          // Log each breakpoint's content length
          updatedRoute.breakpoints.forEach((bp, idx) => {
            if (bp.content) {
              console.log(`  Breakpoint ${idx} (${bp.name}): ${bp.content.length} chars - ${bp.content.substring(0, 80)}...`);
            } else {
              console.warn(`  Breakpoint ${idx} (${bp.name}): NO CONTENT`);
            }
          });
          
          setIsGeneratingStory(false);
          setStoryGenerationRouteId(null);
          setActiveRoute(updatedRoute);
          return;
        }
      } catch (error) {
        console.error("Failed to load/generate story:", error);
        setIsGeneratingStory(false);
        setStoryGenerationRouteId(null);
        // Continue with original route even if story loading fails
      }
    }
    
    setIsGeneratingStory(false);
    setStoryGenerationRouteId(null);
    setActiveRoute(route);
  };

  const handleCompleteRoute = async (
    route: Route,
    xpGained: number,
    completedQuestIds: string[] = []
  ): Promise<{ aiSummary?: string | null } | void> => {
    // If user is not logged in, use localStorage fallback
    if (!isLoggedIn || !userProfile.id) {
      const newSouvenir = {
        id: `souvenir-${Date.now()}`,
        routeId: route.id,
        routeName: route.name,
        location: route.location,
        completedAt: new Date(),
        xpGained: xpGained,
        badgesEarned: ["Completed"],
        imageUrl: route.imageUrl,
        difficulty: route.difficulty,
        distance: route.distance,
      };

      const updatedProfile = {
        ...userProfile,
        xp: userProfile.xp + xpGained,
        completedRoutes: [...userProfile.completedRoutes, route.id],
        level: Math.floor((userProfile.xp + xpGained) / 300) + 1,
        souvenirs: [newSouvenir, ...userProfile.souvenirs],
      };
      onUpdateProfile(updatedProfile);
      localStorage.setItem("trailsaga-profile", JSON.stringify(updatedProfile));
      setActiveRoute(null);
      return;
    }

    // User is logged in - try to call backend API
    try {
      const profileIdNum = parseInt(userProfile.id, 10);
      // Convert quest IDs to integers and filter out any invalid values
      const questIdsNum = completedQuestIds
        .map((id) => parseInt(id, 10))
        .filter((id) => Number.isFinite(id));
      const routeIdNum = parseInt(route.id, 10);

      // Call backend API to create souvenir
      const response = await apiClient.createSouvenir(
        profileIdNum,
        routeIdNum,
        questIdsNum
      );

      // Transform API response to frontend format
      const newSouvenir = transformApiSouvenir(response.souvenir);

      // Update profile state with backend data
      // Use new_total_xp from backend to ensure accuracy
      const updatedProfile = {
        ...userProfile,
        xp: response.new_total_xp || (userProfile.xp + response.total_xp_gained), // Use backend's total XP
        level: response.new_level,
        completedRoutes: [...userProfile.completedRoutes, route.id],
        souvenirs: [newSouvenir, ...userProfile.souvenirs],
      };

      onUpdateProfile(updatedProfile);
      localStorage.setItem("trailsaga-profile", JSON.stringify(updatedProfile));

      // Return AI-generated summary so HikingSimulator can display it immediately.
      // Do NOT close the simulator here; let the simulator decide when to exit
      // so the user can see the completion screen and AI summary.
      return {
        aiSummary: response.souvenir.genai_summary || null,
      };
    } catch (error) {
      console.error("Failed to create souvenir via API:", error);
      // Fallback to localStorage if API fails
      const newSouvenir = {
        id: `souvenir-${Date.now()}`,
        routeId: route.id,
        routeName: route.name,
        location: route.location,
        completedAt: new Date(),
        xpGained: xpGained,
        badgesEarned: ["Completed"],
        imageUrl: route.imageUrl,
        difficulty: route.difficulty,
        distance: route.distance,
      };

      const updatedProfile = {
        ...userProfile,
        xp: userProfile.xp + xpGained,
        completedRoutes: [...userProfile.completedRoutes, route.id],
        level: Math.floor((userProfile.xp + xpGained) / 300) + 1,
        souvenirs: [newSouvenir, ...userProfile.souvenirs],
      };
      onUpdateProfile(updatedProfile);
      localStorage.setItem("trailsaga-profile", JSON.stringify(updatedProfile));
      setActiveRoute(null);
      throw error; // Re-throw to let caller know it failed
    }
  };

  const handleFeedback = (route: Route, type: "dislike" | "skip") => {
    if (type === "dislike") {
      setFeedbackRoute(route);
    }
  };

  const handleFeedbackSubmit = async (reason: string) => {
    if (!feedbackRoute) return;

    // If user is not logged in, update local profile only
    if (!isLoggedIn || !userProfile.id) {
      const updatedProfile = { ...userProfile };

      if (reason === "too-hard") {
        updatedProfile.difficultyBias = Math.max(
          -5,
          userProfile.difficultyBias - 1
        );
      } else if (reason === "too-easy") {
        updatedProfile.difficultyBias = Math.min(
          5,
          userProfile.difficultyBias + 1
        );
      } else if (reason === "too-far") {
        updatedProfile.distanceBias = Math.max(-5, userProfile.distanceBias - 1);
      }

      onUpdateProfile(updatedProfile);
      localStorage.setItem("trailsaga-profile", JSON.stringify(updatedProfile));
      setFeedbackRoute(null);
      return;
    }

    // User is logged in - call backend API
    try {
      const profileIdNum = parseInt(userProfile.id, 10);
      const routeIdNum = parseInt(feedbackRoute.id, 10);

      await apiClient.submitFeedback(profileIdNum, routeIdNum, reason);

      // Also update local profile for immediate UI feedback
      const updatedProfile = { ...userProfile };

      if (reason === "too-hard") {
        updatedProfile.difficultyBias = Math.max(
          -5,
          userProfile.difficultyBias - 1
        );
      } else if (reason === "too-easy") {
        updatedProfile.difficultyBias = Math.min(
          5,
          userProfile.difficultyBias + 1
        );
      } else if (reason === "too-far") {
        updatedProfile.distanceBias = Math.max(-5, userProfile.distanceBias - 1);
      }

      onUpdateProfile(updatedProfile);
      setFeedbackRoute(null);
      
      // Refresh recommendations to show updated scores based on feedback
      // This will re-fetch routes with updated user preferences and feedback penalties
      if (isLoggedIn && userProfile.id) {
        console.log('🔄 Refreshing recommendations after feedback submission...');
        await fetchBackendRoutes();
      }
    } catch (error) {
      console.error("Failed to submit feedback:", error);
      // Still close the dialog even if API call fails
      setFeedbackRoute(null);
      // Optionally show an error toast/notification here
    }
  };

  const handleViewSouvenirsFromSimulator = async () => {
    console.log("[v0] handleViewSouvenirsFromSimulator called");
    
    // Wait a moment for any pending state updates to complete
    await new Promise(resolve => setTimeout(resolve, 100));
    
    // Close the route simulator first
    setActiveRoute(null);
    
    // Wait a bit more to ensure state has updated
    await new Promise(resolve => setTimeout(resolve, 200));
    
    // Trigger refresh to ensure latest data is loaded
    setGalleryRefreshTrigger(prev => prev + 1);
    
    // Open gallery after a short delay to ensure refresh trigger is set
    setTimeout(() => {
      setShowGallery(true);
    }, 100);
  };

  if (activeRoute) {
    return (
      <>
        {/* Story Generation Loading Overlay */}
        {isGeneratingStory && storyGenerationRouteId && (
          <div className="fixed inset-0 bg-black/50 backdrop-blur-sm z-50 flex items-center justify-center">
            <Card className="p-8 border-4 border-primary max-w-md">
              <div className="text-center space-y-4">
                <div className="animate-spin text-4xl">✨</div>
                <h3 className="text-xl font-bold text-foreground">Generating Story...</h3>
                <p className="text-muted-foreground">
                  Creating your magical adventure! This may take up to 60 seconds.
                </p>
                <p className="text-sm text-muted-foreground">
                  Please wait while we craft your Harry Potter-themed story...
                </p>
              </div>
            </Card>
          </div>
        )}
        <HikingSimulator
          route={activeRoute}
          userProfile={userProfile}
          onComplete={handleCompleteRoute}
          onExit={() => {
            // Fully exit simulation: close simulator, clear any selected route,
            // then scroll back to top of the main recommendations page.
            setActiveRoute(null);
            setSelectedRoute(null);
            scrollToMainTop();
          }}
          onViewSouvenirs={handleViewSouvenirsFromSimulator}
        />
      </>
    );
  }

  if (showGallery) {
    return (
      <SouvenirGallery
        souvenirs={userProfile.souvenirs}
        onClose={() => setShowGallery(false)}
        profileId={isLoggedIn ? userProfile.id : null}
        isLoggedIn={isLoggedIn}
        refreshTrigger={galleryRefreshTrigger}
      />
    );
  }

  const recommendedRoutes = getRecommendedRoutes();

  return (
    <div className="min-h-screen bg-background">
      {/* Header */}
      <header className="border-b-4 border-border bg-card/50 backdrop-blur-sm sticky top-0 z-40">
        <div className="container mx-auto px-4 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <Mountain className="w-8 h-8 text-primary" strokeWidth={2.5} />
              <div className="flex flex-col">
                <h1 className="text-2xl font-bold text-foreground">
                  Trail<span className="text-primary">Saga</span>
                </h1>
                <span className="text-xs font-medium text-muted-foreground">
                  Hogwarts Expedition Series
                </span>
              </div>
            </div>

            {isLoggedIn && (
              <div className="flex items-center gap-3">
                <div className="flex items-center gap-3">
                  <div className="text-right hidden sm:block">
                    <p className="text-sm text-muted-foreground">
                      {userProfile.explorerType}
                    </p>
                    <p className="text-lg font-bold text-foreground">
                      Level {userProfile.level} • {userProfile.xp} XP
                    </p>
                  </div>
                  <Button
                    variant="outline"
                    size="sm"
                    className="border-2 px-3 py-2 h-auto gap-2 hover:bg-accent/10"
                    onClick={() => {
                      setGalleryRefreshTrigger(prev => prev + 1);
                      setShowGallery(true);
                    }}
                  >
                    <span className="text-base">🏅</span>
                    <span className="font-semibold text-accent">
                      {userProfile.souvenirs.length}{" "}
                      {userProfile.souvenirs.length === 1
                        ? "Souvenir"
                        : "Souvenirs"}
                    </span>
                  </Button>
                </div>
                <Button
                  variant="outline"
                  size="icon"
                  className="border-2"
                  onClick={() => setShowProfile(true)}
                >
                  <User className="w-5 h-5" />
                </Button>
              </div>
            )}
          </div>
        </div>
      </header>

      <main className="container mx-auto px-4 py-8">
        {/* Welcome Banner */}
        <div className="mb-8">
          <Card className="p-6 bg-linear-to-r from-primary/20 via-secondary/20 to-accent/20 border-2">
            <h2 className="text-2xl md:text-3xl font-bold text-foreground mb-2">
              {isLoggedIn
                ? `Welcome back, ${userProfile.explorerType}!`
                : "Discover Popular Routes"}
            </h2>
            <p className="text-muted-foreground">
              {isLoggedIn
                ? "Your personalized adventures await. Choose a route to begin your next saga."
                : "Explore our most popular outdoor adventures. Sign up to unlock personalized recommendations!"}
            </p>
          </Card>
        </div>

        {/* Loading/Error Banner */}
        <div className="mb-4">
          {isLoadingRoutes && (
            <Card className="p-4 bg-muted/50 border-2">
              <p className="text-sm text-muted-foreground flex items-center gap-2">
                <span className="animate-spin">⏳</span>
                {isLoggedIn
                  ? "Loading personalized recommendations..."
                  : "Loading routes from database..."}
              </p>
            </Card>
          )}
          {!isLoadingRoutes && backendError && (
            <Card className="p-4 bg-yellow-50 dark:bg-yellow-900/20 border-2 border-yellow-500">
              <p className="text-sm text-yellow-800 dark:text-yellow-200">
                ⚠️ {backendError}
              </p>
            </Card>
          )}
          {!isLoadingRoutes && !backendError && backendRoutes.length > 0 && (
            <div className="flex items-center justify-between gap-4 mb-4">
              <div className="flex items-center gap-2">
                <label htmlFor="route-limit" className="text-sm font-medium text-foreground">
                  Show routes:
                </label>
                <select
                  id="route-limit"
                  value={routeLimit}
                  onChange={(e) => setRouteLimit(Number(e.target.value))}
                  className="px-3 py-1.5 text-sm border-2 border-border rounded-md bg-background text-foreground focus:outline-none focus:ring-2 focus:ring-primary focus:border-primary"
                >
                  <option value={10}>10</option>
                  <option value={20}>20</option>
                  <option value={30}>30</option>
                  <option value={50}>50</option>
                  <option value={100}>100</option>
                  <option value={999}>All</option>
                </select>
              </div>
              <p className="text-sm text-muted-foreground">
                Showing {backendRoutes.length} {backendRoutes.length === 1 ? 'route' : 'routes'}
              </p>
            </div>
          )}
        </div>

        {/* Activity Type Filter */}
        <Tabs
          value={selectedType}
          onValueChange={(v) => setSelectedType(v as any)}
          className="mb-8"
        >
          <TabsList className="grid w-full grid-cols-4 h-auto border-2">
            <TabsTrigger value="all" className="py-3">
              <Sparkles className="w-4 h-4 mr-2" />
              All
            </TabsTrigger>
            <TabsTrigger value="running" className="py-3">
              <TrendingUp className="w-4 h-4 mr-2" />
              Running
            </TabsTrigger>
            <TabsTrigger value="hiking" className="py-3">
              <Mountain className="w-4 h-4 mr-2" />
              Hiking
            </TabsTrigger>
            <TabsTrigger value="cycling" className="py-3">
              <Bike className="w-4 h-4 mr-2" />
              Cycling
            </TabsTrigger>
          </TabsList>
        </Tabs>

        <div className="mb-6">
          <h2 className="text-2xl font-bold text-foreground mb-2">
            {isLoggedIn ? "Recommended for You" : "New Adventures"}
          </h2>
          <p className="text-muted-foreground">
            {isLoggedIn
              ? "Discover routes tailored to your explorer profile"
              : "Start your outdoor journey with these popular routes"}
          </p>
        </div>

        {/* Route Cards */}
        <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
          {recommendedRoutes.map((route) => {
            const isLocked =
              route.isLocked && userProfile.xp < (route.xpRequired || 0);
            const isCompleted = userProfile.completedRoutes.includes(route.id);

            return (
              <Card
                key={route.id}
                className={`overflow-hidden border-2 transition-all hover:shadow-xl ${
                  isLocked ? "opacity-60" : ""
                }`}
              >
                {/* Image */}
                <div className="relative h-48 bg-muted">
                  <img
                    src={route.imageUrl || "/placeholder.svg"}
                    alt={route.name}
                    className="w-full h-full object-cover"
                  />
                  {isLocked && (
                    <div className="absolute inset-0 bg-black/50 flex items-center justify-center">
                      <div className="text-center text-white">
                        <Lock className="w-12 h-12 mx-auto mb-2" />
                        <p className="font-semibold">
                          {route.xpRequired} XP Required
                        </p>
                      </div>
                    </div>
                  )}
                  {isCompleted && (
                    <div className="absolute top-2 right-2 bg-primary text-primary-foreground px-3 py-1 rounded-full text-sm font-semibold flex items-center gap-1 z-20">
                      <CheckCircle2 className="w-4 h-4" />
                      Completed
                    </div>
                  )}
                  {/* Recommendation Score Badge */}
                  {isLoggedIn &&
                    route.recommendationScore !== undefined &&
                    route.recommendationScore !== null &&
                    route.recommendationScoreBreakdown && (
                      <button
                        onClick={(e) => {
                          e.stopPropagation();
                          setScoreModalRoute(route);
                        }}
                        className={`absolute ${
                          isCompleted ? "top-12" : "top-2"
                        } right-2 bg-primary text-primary-foreground px-3 py-1.5 rounded-full text-sm font-semibold flex items-center gap-1.5 hover:bg-primary/90 transition-colors shadow-lg z-10`}
                        title="Click to see how this score was calculated"
                      >
                        <TrendingUp className="w-3.5 h-3.5" />
                        {Math.round(route.recommendationScore * 100)}%
                      </button>
                    )}
                  <Badge
                    className="absolute top-2 left-2"
                    variant={
                      route.difficulty === "easy"
                        ? "secondary"
                        : route.difficulty === "expert"
                        ? "destructive"
                        : "default"
                    }
                  >
                    {getDifficultyLabel(route.difficulty)}
                  </Badge>
                </div>

                {/* Content */}
                <div className="p-4 space-y-3">
                  <div>
                    <h3 className="text-xl font-bold text-foreground mb-1">
                      {route.name}
                    </h3>
                    <p className="text-sm text-muted-foreground flex items-center gap-1">
                      <MapPin className="w-3 h-3" />
                      {route.location}
                    </p>
                  </div>

                  <p className="text-sm text-foreground line-clamp-2">
                    {route.description}
                  </p>

                  {/* Stats */}
                  <div className="grid grid-cols-3 gap-2 text-sm">
                    <div>
                      <p className="text-muted-foreground">Distance</p>
                      <p className="font-semibold text-foreground">
                        {route.distance} km
                      </p>
                    </div>
                    <div>
                      <p className="text-muted-foreground">Duration</p>
                      <p className="font-semibold text-foreground">
                        {Math.round(route.duration / 60)}h
                      </p>
                    </div>
                    <div>
                      <p className="text-muted-foreground">XP Reward</p>
                      <p className="font-semibold text-accent">
                        {route.xpReward} XP
                      </p>
                    </div>
                  </div>

                  {/* Actions */}
                  <div className="flex gap-2 pt-2">
                    <Button
                      className="flex-1 bg-primary hover:bg-primary/90 text-primary-foreground font-semibold"
                      onClick={() => setSelectedRoute(route)}
                      disabled={isLocked}
                    >
                      View Details
                    </Button>
                    {isLoggedIn && !isLocked && (
                      <Button
                        size="icon"
                        variant="outline"
                        className="border-2"
                        onClick={() => handleFeedback(route, "dislike")}
                      >
                        <ThumbsDown className="w-4 h-4" />
                      </Button>
                    )}
                  </div>
                </div>
              </Card>
            );
          })}
        </div>
      </main>

      {/* Route Detail Modal */}
      {selectedRoute && (
        <RouteDetailModal
          route={selectedRoute}
          userProfile={userProfile}
          isLoggedIn={isLoggedIn}
          onClose={() => {
            setSelectedRoute(null);
            scrollToMainTop();
          }}
          onStartRoute={handleStartRoute}
          onGoToQuestionnaire={() => {
            setSelectedRoute(null);
            onGoToQuestionnaire?.();
          }}
          // </CHANGE>
        />
      )}

      {/* Feedback Dialog */}
      {feedbackRoute && (
        <FeedbackDialog
          route={feedbackRoute}
          onSubmit={async (reason) => {
            await handleFeedbackSubmit(reason);
          }}
          onClose={() => setFeedbackRoute(null)}
        />
      )}

      {/* Profile Modal */}
      {showProfile && isLoggedIn && (
        <UserProfileModal
          userProfile={userProfile}
          onClose={() => setShowProfile(false)}
        />
      )}

      {/* Recommendation Score Modal */}
      {scoreModalRoute &&
        scoreModalRoute.recommendationScore !== undefined &&
        scoreModalRoute.recommendationScore !== null &&
        scoreModalRoute.recommendationScoreBreakdown && (
          <RecommendationScoreModal
            score={scoreModalRoute.recommendationScore}
            breakdown={scoreModalRoute.recommendationScoreBreakdown}
            routeName={scoreModalRoute.name}
            open={true}
            onClose={() => setScoreModalRoute(null)}
          />
        )}
    </div>
  );
}
