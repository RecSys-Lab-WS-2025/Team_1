"use client";

import { useState, useEffect } from "react";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { mockRoutes, UserProfile, Route } from "@/lib/mock-data";
import { apiClient } from "@/lib/api-client";
import { ApiRecommendationResponse } from "@/lib/api-types";
import { transformApiRoutes } from "@/lib/api-transforms";
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
} from "lucide-react";
import { RouteDetailModal } from "@/components/route-detail-modal";
import { HikingSimulator } from "@/components/hiking-simulator";
import { FeedbackDialog } from "@/components/feedback-dialog";
import { UserProfileModal } from "@/components/user-profile-modal";
import { SouvenirGallery } from "@/components/souvenir-gallery";

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
    "all" | "hiking" | "city-walk" | "trail-running"
  >("all");
  const [feedbackRoute, setFeedbackRoute] = useState<Route | null>(null);
  const [showProfile, setShowProfile] = useState(false);
  const [showGallery, setShowGallery] = useState(false);
  const [backendRoutes, setBackendRoutes] = useState<Route[]>([]);
  const [isLoadingRoutes, setIsLoadingRoutes] = useState(false);
  const [backendError, setBackendError] = useState<string | null>(null);

  // Fetch routes from backend for guest users
  useEffect(() => {
    // Only fetch for guest users (not logged in)
    if (!isLoggedIn) {
      fetchBackendRoutes();
    }
  }, [isLoggedIn]);

  const fetchBackendRoutes = async () => {
    setIsLoadingRoutes(true);
    setBackendError(null);

    try {
      const response = await apiClient.get<ApiRecommendationResponse>(
        "api/routes/recommendations?limit=20"
      );
      const routes = transformApiRoutes(response.routes);
      setBackendRoutes(routes);
    } catch (error) {
      console.error("Failed to fetch routes:", error);
      setBackendError(
        "Could not load routes from server. Showing sample routes instead."
      );
      setBackendRoutes([]); // Fallback to mock
    } finally {
      setIsLoadingRoutes(false);
    }
  };

  // Simple recommendation logic based on user profile
  const getRecommendedRoutes = () => {
    // Use backend routes for guests if available, otherwise fallback to mock
    const sourceRoutes =
      !isLoggedIn && backendRoutes.length > 0 ? backendRoutes : mockRoutes;

    let routes = [...sourceRoutes];

    // Filter by type if selected
    if (selectedType !== "all") {
      routes = routes.filter((r) => r.type === selectedType);
    }

    // If logged in, personalize recommendations
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

        scoreA += difficultyScore[userProfile.fitnessLevel][a.difficulty] || 0;
        scoreB += difficultyScore[userProfile.fitnessLevel][b.difficulty] || 0;

        // Completed routes go to bottom
        if (userProfile.completedRoutes.includes(a.id)) scoreA -= 20;
        if (userProfile.completedRoutes.includes(b.id)) scoreB -= 20;

        // Apply user biases
        scoreA +=
          userProfile.difficultyBias *
          (a.difficulty === "hard" || a.difficulty === "expert" ? 1 : -1);
        scoreB +=
          userProfile.difficultyBias *
          (b.difficulty === "hard" || b.difficulty === "expert" ? 1 : -1);

        return scoreB - scoreA;
      });
    }

    return routes;
  };

  const handleStartRoute = (route: Route) => {
    if (route.isLocked && userProfile.xp < (route.xpRequired || 0)) {
      return;
    }
    setActiveRoute(route);
  };

  const handleCompleteRoute = (route: Route, xpGained: number) => {
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
  };

  const handleFeedback = (route: Route, type: "dislike" | "skip") => {
    if (type === "dislike") {
      setFeedbackRoute(route);
    }
  };

  const handleFeedbackSubmit = (reason: string) => {
    // Update user profile based on feedback
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
  };

  const handleViewSouvenirsFromSimulator = () => {
    console.log("[v0] handleViewSouvenirsFromSimulator called");
    setActiveRoute(null);
    setShowGallery(true);
  };

  if (activeRoute) {
    return (
      <HikingSimulator
        route={activeRoute}
        userProfile={userProfile}
        onComplete={handleCompleteRoute}
        onExit={() => setActiveRoute(null)}
        onViewSouvenirs={handleViewSouvenirsFromSimulator}
      />
    );
  }

  if (showGallery) {
    return (
      <SouvenirGallery
        souvenirs={userProfile.souvenirs}
        onClose={() => setShowGallery(false)}
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
              <h1 className="text-2xl font-bold text-foreground">
                Trail<span className="text-primary">Saga</span>
              </h1>
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
                    onClick={() => setShowGallery(true)}
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

        {/* Loading/Error Banner for Guest Users */}
        {!isLoggedIn && (
          <div className="mb-4">
            {isLoadingRoutes && (
              <Card className="p-4 bg-muted/50 border-2">
                <p className="text-sm text-muted-foreground flex items-center gap-2">
                  <span className="animate-spin">⏳</span>
                  Loading routes from database...
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
              <Card className="p-4 bg-green-50 dark:bg-green-900/20 border-2 border-green-500">
                <p className="text-sm text-green-800 dark:text-green-200">
                  ✓ Showing {backendRoutes.length} routes from the TrailSaga
                  database
                </p>
              </Card>
            )}
          </div>
        )}

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
            <TabsTrigger value="hiking" className="py-3">
              <Mountain className="w-4 h-4 mr-2" />
              Hiking
            </TabsTrigger>
            <TabsTrigger value="city-walk" className="py-3">
              <MapPin className="w-4 h-4 mr-2" />
              City Walk
            </TabsTrigger>
            <TabsTrigger value="trail-running" className="py-3">
              <TrendingUp className="w-4 h-4 mr-2" />
              Trail Run
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
                    <div className="absolute top-2 right-2 bg-primary text-primary-foreground px-3 py-1 rounded-full text-sm font-semibold flex items-center gap-1">
                      <CheckCircle2 className="w-4 h-4" />
                      Completed
                    </div>
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
          onClose={() => setSelectedRoute(null)}
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
          onSubmit={handleFeedbackSubmit}
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
    </div>
  );
}
