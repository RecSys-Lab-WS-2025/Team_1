"use client";

import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Route, UserProfile } from "@/lib/mock-data";
import {
  X,
  MapPin,
  Clock,
  TrendingUp,
  Mountain,
  Sparkles,
  Lock,
} from "lucide-react";

interface RouteDetailModalProps {
  route: Route;
  userProfile: UserProfile;
  isLoggedIn: boolean;
  onClose: () => void;
  onStartRoute: (route: Route) => void;
  onGoToQuestionnaire: () => void;
}

export function RouteDetailModal({
  route,
  userProfile,
  isLoggedIn,
  onClose,
  onStartRoute,
  onGoToQuestionnaire,
}: RouteDetailModalProps) {
  const isLocked = route.isLocked && userProfile.xp < (route.xpRequired || 0);
  const isCompleted = userProfile.completedRoutes.includes(route.id);

  const hasCompletedQuestionnaire = isLoggedIn && userProfile.explorerType;

  return (
    <div className="fixed inset-0 bg-black/50 backdrop-blur-sm z-50 flex items-center justify-center p-4 overflow-y-auto">
      <Card className="max-w-3xl w-full my-8 border-4 border-border shadow-2xl">
        {/* Header Image */}
        <div className="relative h-64 bg-muted">
          <img
            src={route.imageUrl || "/placeholder.svg"}
            alt={route.name}
            className="w-full h-full object-cover"
          />
          <Button
            variant="secondary"
            size="icon"
            className="absolute top-4 right-4"
            onClick={onClose}
          >
            <X className="w-5 h-5" />
          </Button>

          {/* XP Reward Badge */}
          <div className="absolute bottom-4 left-4 bg-accent/90 backdrop-blur-sm text-accent-foreground px-4 py-2 rounded-full flex items-center gap-2 font-semibold shadow-lg">
            <Sparkles className="w-5 h-5" />
            <span>{route.xpReward} XP</span>
          </div>

          {isLocked && (
            <div className="absolute inset-0 bg-black/50 flex items-center justify-center">
              <div className="text-center text-white">
                <Lock className="w-16 h-16 mx-auto mb-3" />
                <p className="text-xl font-semibold">Locked Route</p>
                <p className="text-sm mt-1">
                  Requires {route.xpRequired} XP to unlock
                </p>
              </div>
            </div>
          )}
        </div>

        {/* Content */}
        <div className="p-6 space-y-6">
          {/* Title & Location */}
          <div>
            <div className="flex items-start justify-between gap-4 mb-2">
              <h2 className="text-3xl font-bold text-foreground">
                {route.name}
              </h2>
              <Badge
                variant={
                  route.difficulty === "easy"
                    ? "secondary"
                    : route.difficulty === "expert"
                    ? "destructive"
                    : "default"
                }
                className="text-sm"
              >
                {route.difficulty}
              </Badge>
            </div>
            <p className="text-muted-foreground flex items-center gap-2">
              <MapPin className="w-4 h-4" />
              {route.location}
            </p>
          </div>

          {/* Description */}
          <div
            className="text-foreground leading-relaxed line-clamp-9"
            dangerouslySetInnerHTML={{ __html: route.description }}
          />

          {/* Stats Grid */}
          <div className="grid grid-cols-2 md:grid-cols-3 gap-4 p-4 bg-muted/50 rounded-lg border-2 border-border">
            <div className="text-center">
              <Mountain className="w-6 h-6 mx-auto mb-1 text-primary" />
              <p className="text-sm text-muted-foreground">Distance</p>
              <p className="text-lg font-bold text-foreground">
                {route.distance} km
              </p>
            </div>
            <div className="text-center">
              <TrendingUp className="w-6 h-6 mx-auto mb-1 text-primary" />
              <p className="text-sm text-muted-foreground">Elevation</p>
              <p className="text-lg font-bold text-foreground">
                {route.elevation} m
              </p>
            </div>
            <div className="text-center">
              <Clock className="w-6 h-6 mx-auto mb-1 text-primary" />
              <p className="text-sm text-muted-foreground">Duration</p>
              <p className="text-lg font-bold text-foreground">
                {Math.round(route.duration / 60)}h {route.duration % 60}m
              </p>
            </div>
          </div>

          {/* Breakpoints Preview */}
          <div>
            <h3 className="text-lg font-bold text-foreground mb-3">
              Journey Breakpoints
            </h3>
            <div className="space-y-2">
              {route.breakpoints.map((bp, index) => (
                <div
                  key={bp.id}
                  className="flex items-center gap-3 p-3 bg-muted/30 rounded-lg border border-border"
                >
                  <div className="shrink-0 w-8 h-8 rounded-full bg-primary text-primary-foreground flex items-center justify-center font-bold">
                    {index + 1}
                  </div>
                  <div className="flex-1">
                    <p className="font-semibold text-foreground">{bp.name}</p>
                    <p className="text-sm text-muted-foreground">
                      {bp.distance} km
                    </p>
                  </div>
                  {bp.type === "quest" && (
                    <Badge variant="secondary" className="text-xs">
                      Mini Quest
                    </Badge>
                  )}
                </div>
              ))}
            </div>
          </div>

          {/* Tags */}
          <div className="flex flex-wrap gap-2">
            {route.tags.map((tag) => (
              <Badge key={tag} variant="outline" className="text-xs">
                #{tag}
              </Badge>
            ))}
          </div>

          <div className="pt-4 border-t-2 border-border">
            {!hasCompletedQuestionnaire ? (
              <div className="text-center">
                <p className="text-muted-foreground mb-4">
                  Complete your quick setup to start this adventure and track
                  your progress.
                </p>
                <Button
                  className="w-full bg-primary hover:bg-primary/90 text-primary-foreground font-semibold"
                  onClick={onGoToQuestionnaire}
                >
                  Take 2-minute setup →
                </Button>
              </div>
            ) : isLocked ? (
              <div className="text-center">
                <p className="text-muted-foreground mb-2">
                  You need {(route.xpRequired || 0) - userProfile.xp} more XP to
                  unlock this route
                </p>
                <Button className="w-full" disabled>
                  <Lock className="mr-2 w-4 h-4" />
                  Locked
                </Button>
              </div>
            ) : (
              <Button
                className="w-full bg-primary hover:bg-primary/90 text-primary-foreground font-semibold text-lg py-6"
                onClick={() => onStartRoute(route)}
              >
                <Sparkles className="mr-2 w-5 h-5" />
                {isCompleted ? "Replay Adventure" : "Start Adventure →"}
              </Button>
            )}
          </div>
        </div>
      </Card>
    </div>
  );
}
