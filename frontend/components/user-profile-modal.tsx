'use client';

import { Card } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Progress } from '@/components/ui/progress';
import { UserProfile, mockRoutes, Route } from '@/lib/mock-data';
import { X, Trophy, Target, Mountain, MapPin, TrendingUp, Sparkles, Award, Calendar, RotateCcw, Loader2, Sliders } from 'lucide-react';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { useState, useEffect } from 'react';
import { apiClient } from '@/lib/api-client';
import { transformApiRoute } from '@/lib/api-transforms';
import type { ApiProfileStatistics } from '@/lib/api-types';

interface UserProfileModalProps {
  userProfile: UserProfile;
  onClose: () => void;
}

interface CompletedRouteWithSouvenir {
  route: Route;
  souvenirId: number;
}

export function UserProfileModal({ userProfile, onClose }: UserProfileModalProps) {
  const [showResetConfirm, setShowResetConfirm] = useState(false);
  const [completedRoutes, setCompletedRoutes] = useState<CompletedRouteWithSouvenir[]>([]);
  const [isLoadingHistory, setIsLoadingHistory] = useState(false);
  const [historyError, setHistoryError] = useState<string | null>(null);
  const [achievements, setAchievements] = useState<Array<{
    id: string;
    name: string;
    description: string;
    icon: string;
    unlocked: boolean;
  }>>([]);
  const [isLoadingAchievements, setIsLoadingAchievements] = useState(false);
  const [stats, setStats] = useState<ApiProfileStatistics | null>(null);
  const [isLoadingStats, setIsLoadingStats] = useState(false);
  const [statsError, setStatsError] = useState<string | null>(null);
  const [userPreferences, setUserPreferences] = useState<{
    difficulty_range?: [number, number];
    max_distance_km?: number;
    min_distance_km?: number;
    preferred_tags?: string[];
    fitness_level?: string;
    narrative_prompt_style?: string;
  } | null>(null);
  const [isLoadingPreferences, setIsLoadingPreferences] = useState(false);

  const xpProgress = (userProfile.xp % 300) / 300 * 100;
  const fallbackTotalDistance = completedRoutes.reduce((sum, r) => sum + r.route.distance, 0);
  const fallbackTotalElevation = completedRoutes.reduce((sum, r) => sum + r.route.elevation, 0);
  const totalDistance = stats ? stats.total_distance_km : fallbackTotalDistance;
  const totalElevation = stats ? stats.total_elevation_m : fallbackTotalElevation;

  // Load completed routes from souvenirs API
  useEffect(() => {
    const loadCompletedRoutes = async () => {
      // Check if user has a backend profile ID
        const profileId = userProfile.id;
        if (!profileId) {
          // Fallback to mock data for local-only profiles
          const mockCompletedRoutes: CompletedRouteWithSouvenir[] = mockRoutes
            .filter(r => userProfile.completedRoutes.includes(r.id))
            .map((r, index) => ({ route: r, souvenirId: index }));
          setCompletedRoutes(mockCompletedRoutes);
          return;
        }

        const profileIdNum = parseInt(profileId, 10);
        if (isNaN(profileIdNum)) {
          // Fallback to mock data for non-numeric IDs
          const mockCompletedRoutes: CompletedRouteWithSouvenir[] = mockRoutes
            .filter(r => userProfile.completedRoutes.includes(r.id))
            .map((r, index) => ({ route: r, souvenirId: index }));
          setCompletedRoutes(mockCompletedRoutes);
          return;
        }

      setIsLoadingHistory(true);
      setHistoryError(null);

      try {
        // Fetch souvenirs from backend
        const response = await apiClient.getSouvenirs(profileIdNum, {
          limit: 100, // Get all souvenirs
          sort: 'newest'
        });

        // Transform souvenirs to routes with souvenir IDs
        const routes: CompletedRouteWithSouvenir[] = [];
        for (const souvenir of response.souvenirs) {
          if (souvenir.route) {
            const route = transformApiRoute(souvenir.route);
            routes.push({ route, souvenirId: souvenir.id });
          }
        }

        setCompletedRoutes(routes);
      } catch (error: any) {
        console.error('Failed to load completed routes:', error);
        setHistoryError('Failed to load route history. Using local data.');
        // Fallback to mock data on error
        const mockCompletedRoutes: CompletedRouteWithSouvenir[] = mockRoutes
          .filter(r => userProfile.completedRoutes.includes(r.id))
          .map((r, index) => ({ route: r, souvenirId: index }));
        setCompletedRoutes(mockCompletedRoutes);
      } finally {
        setIsLoadingHistory(false);
      }
    };

    loadCompletedRoutes();
  }, [userProfile.id, userProfile.completedRoutes]);

  const handleResetProfile = async () => {
    try {
      console.log('[Reset] Starting reset - will delete ALL user profiles from database');
      
      // Delete ALL profiles from backend (not just current user)
      try {
        const response = await apiClient.delete<{ deleted_count: number; message: string }>(`api/profiles`);
        console.log('[Reset] Successfully deleted all profiles:', response);
      } catch (error) {
        // If deletion fails, log error but continue with local reset
        console.error('[Reset] Failed to delete profiles from backend:', error);
      }
    } catch (error) {
      console.error('[Reset] Error during reset operation:', error);
    } finally {
      // Always clear localStorage and redirect to start fresh
      console.log('[Reset] Clearing localStorage and redirecting to home');
      localStorage.clear();
      window.location.href = '/';
    }
  };

  // Load user preferences from backend
  useEffect(() => {
    const loadUserPreferences = async () => {
      const profileId = userProfile.id;
      console.log('[UserPreferences] Starting to load preferences for profile:', profileId);
      
      if (!profileId) {
        console.log('[UserPreferences] No profile ID, setting preferences to null');
        setUserPreferences(null);
        return;
      }

      const profileIdNum = parseInt(profileId, 10);
      if (isNaN(profileIdNum)) {
        console.log('[UserPreferences] Invalid profile ID (not a number):', profileId);
        setUserPreferences(null);
        return;
      }

      setIsLoadingPreferences(true);
      try {
        console.log('[UserPreferences] Fetching profile from API:', profileIdNum);
        const profileResponse = await apiClient.getProfile(profileIdNum);
        console.log('[UserPreferences] Profile response received:', {
          hasUserVectorJson: !!profileResponse.user_vector_json,
          userVectorJsonLength: profileResponse.user_vector_json?.length || 0,
          userVectorJsonPreview: profileResponse.user_vector_json?.substring(0, 100)
        });
        
        if (profileResponse.user_vector_json) {
          const userVector = JSON.parse(profileResponse.user_vector_json);
          console.log('[UserPreferences] Parsed user vector:', userVector);
          setUserPreferences(userVector);
        } else {
          console.log('[UserPreferences] No user_vector_json in response, setting to null');
          setUserPreferences(null);
        }
      } catch (error) {
        console.error('[UserPreferences] Failed to load user preferences:', error);
        setUserPreferences(null);
      } finally {
        setIsLoadingPreferences(false);
      }
    };

    loadUserPreferences();
  }, [userProfile.id]);

  // Load statistics from backend
  useEffect(() => {
    const loadStatistics = async () => {
      const profileId = userProfile.id;
      if (!profileId) {
        setStats(null);
        return;
      }

      const profileIdNum = parseInt(profileId, 10);
      if (isNaN(profileIdNum)) {
        setStats(null);
        return;
      }

      setIsLoadingStats(true);
      setStatsError(null);
      try {
        const statsResponse = await apiClient.getProfileStatistics(profileIdNum);
        setStats(statsResponse);
      } catch (error) {
        console.error('Failed to load profile statistics:', error);
        setStatsError('Failed to load statistics. Using local data.');
        setStats(null);
      } finally {
        setIsLoadingStats(false);
      }
    };

    loadStatistics();
  }, [userProfile.id, completedRoutes.length]);

  // Load achievements from backend
  useEffect(() => {
    const loadAchievements = async () => {
      const profileId = userProfile.id;
      if (!profileId) {
        // Fallback to empty achievements for local-only profiles
        setAchievements([]);
        return;
      }

      const profileIdNum = parseInt(profileId, 10);
      if (isNaN(profileIdNum)) {
        setAchievements([]);
        return;
      }

      setIsLoadingAchievements(true);
      try {
        const { apiClient } = await import('@/lib/api-client');
        // First check and unlock any new achievements
        try {
          await apiClient.checkAchievements(profileIdNum);
        } catch (checkError) {
          console.warn('Achievement check failed (non-critical):', checkError);
          // Continue even if check fails
        }
        
        // Then get all achievements with unlock status
        const profileAchievements = await apiClient.getProfileAchievements(profileIdNum);
        
        console.log('Loaded achievements:', profileAchievements.length, profileAchievements);
        
        if (profileAchievements && profileAchievements.length > 0) {
          setAchievements(
            profileAchievements.map(a => ({
              id: a.achievement_key,
              name: a.name,
              description: a.description,
              icon: a.icon,
              unlocked: a.unlocked,
            }))
          );
        } else {
          console.warn('No achievements returned from API, using fallback');
          // Fallback: Use default achievements list (all locked)
          setAchievements([
            { id: 'first-steps', name: 'First Steps', description: 'Complete your first route', icon: '🥾', unlocked: false },
            { id: 'explorer', name: 'Explorer', description: 'Complete 3 different routes', icon: '🗺️', unlocked: false },
            { id: 'hiker', name: 'Trail Hiker', description: 'Complete a hiking route', icon: '⛰️', unlocked: false },
            { id: 'runner', name: 'Trail Runner', description: 'Complete a running route', icon: '🏃', unlocked: false },
            { id: 'cyclist', name: 'Cyclist', description: 'Complete a cycling route', icon: '🚴', unlocked: false },
            { id: 'level-5', name: 'Rising Star', description: 'Reach Level 5', icon: '⭐', unlocked: false },
            { id: 'xp-1000', name: 'XP Collector', description: 'Earn 1000 total XP', icon: '💎', unlocked: false },
            { id: 'distance-50', name: 'Long Distance', description: 'Travel 50km total', icon: '🎯', unlocked: false },
          ]);
        }
      } catch (error: any) {
        console.error('Failed to load achievements:', error);
        // Fallback: Use default achievements list (all locked)
        setAchievements([
          { id: 'first-steps', name: 'First Steps', description: 'Complete your first route', icon: '🥾', unlocked: false },
          { id: 'explorer', name: 'Explorer', description: 'Complete 3 different routes', icon: '🗺️', unlocked: false },
          { id: 'hiker', name: 'Trail Hiker', description: 'Complete a hiking route', icon: '⛰️', unlocked: false },
          { id: 'runner', name: 'Trail Runner', description: 'Complete a running route', icon: '🏃', unlocked: false },
          { id: 'cyclist', name: 'Cyclist', description: 'Complete a cycling route', icon: '🚴', unlocked: false },
          { id: 'level-5', name: 'Rising Star', description: 'Reach Level 5', icon: '⭐', unlocked: false },
          { id: 'xp-1000', name: 'XP Collector', description: 'Earn 1000 total XP', icon: '💎', unlocked: false },
          { id: 'distance-50', name: 'Long Distance', description: 'Travel 50km total', icon: '🎯', unlocked: false },
        ]);
      } finally {
        setIsLoadingAchievements(false);
      }
    };

    loadAchievements();
  }, [userProfile.id, completedRoutes.length]); // Reload when routes change

  const unlockedAchievements = achievements.filter(a => a.unlocked);
  const lockedAchievements = achievements.filter(a => !a.unlocked);

  return (
    <div className="fixed inset-0 bg-black/50 backdrop-blur-sm z-50 flex items-start justify-center p-4 pt-8 overflow-y-auto">
      <Card className="max-w-4xl w-full my-auto border-4 border-border shadow-2xl">
        {/* Header */}
        <div className="relative p-8 bg-linear-to-r from-primary/20 via-secondary/20 to-accent/20 border-b-4 border-border">
          <Button
            variant="secondary"
            size="icon"
            className="absolute top-4 right-4"
            onClick={onClose}
          >
            <X className="w-5 h-5" />
          </Button>
          
          <div className="flex items-start gap-6">
            <div className="w-24 h-24 rounded-full bg-primary/30 flex items-center justify-center border-4 border-border">
              <span className="text-4xl">🎒</span>
            </div>
            
            <div className="flex-1">
              <h2 className="text-3xl font-bold text-foreground mb-1">{userProfile.name}</h2>
              <p className="text-lg text-muted-foreground mb-3">{userProfile.explorerType}</p>
              
              <div className="flex items-center gap-4">
                <Badge className="text-base px-4 py-1">
                  Level {userProfile.level}
                </Badge>
                <Badge variant="secondary" className="text-base px-4 py-1">
                  {userProfile.xp} XP
                </Badge>
              </div>
            </div>
          </div>

          {/* XP Progress */}
          <div className="mt-6">
            <div className="flex justify-between text-sm mb-2">
              <span className="text-muted-foreground">Progress to Level {userProfile.level + 1}</span>
              <span className="text-foreground font-semibold">
                {userProfile.xp % 300} / 300 XP
              </span>
            </div>
            <Progress value={xpProgress} className="h-3" />
          </div>
        </div>

        {/* Content */}
        <div className="p-6">
          <Tabs defaultValue="stats" className="w-full">
            <TabsList className="grid w-full grid-cols-3 mb-6">
              <TabsTrigger value="stats">Statistics</TabsTrigger>
              <TabsTrigger value="achievements">Achievements</TabsTrigger>
              <TabsTrigger value="history">History</TabsTrigger>
            </TabsList>

            {/* Statistics Tab */}
            <TabsContent value="stats" className="space-y-6">
              {/* Profile Info */}
              <Card className="p-6 border-2 border-border">
                <h3 className="text-lg font-bold text-foreground mb-4">Explorer Profile</h3>
                <div className="grid md:grid-cols-2 gap-4">
                  <div>
                    <p className="text-sm text-muted-foreground">Fitness Level</p>
                    <p className="text-base font-semibold text-foreground capitalize">
                      {userProfile.fitnessLevel}
                    </p>
                  </div>
                  <div>
                    <p className="text-sm text-muted-foreground">Narrative Style</p>
                    <p className="text-base font-semibold text-foreground capitalize">
                      {userProfile.narrativeStyle}
                    </p>
                  </div>
                  <div>
                    <p className="text-sm text-muted-foreground">Preferred Activities</p>
                    <p className="text-base font-semibold text-foreground">
                      {userProfile.preferredTypes.length > 0 
                        ? userProfile.preferredTypes.map(t => t.replace('-', ' ')).join(', ')
                        : 'All Types'}
                    </p>
                  </div>
                  <div>
                    <p className="text-sm text-muted-foreground">Routes Completed</p>
                    <p className="text-base font-semibold text-foreground">
                      {completedRoutes.length}
                    </p>
                  </div>
                </div>
              </Card>

              {/* Journey Stats */}
              <Card className="p-6 border-2 border-border">
                <h3 className="text-lg font-bold text-foreground mb-4">Journey Statistics</h3>
                {statsError && (
                  <p className="text-xs text-destructive mb-2">{statsError}</p>
                )}
                <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                  <div className="text-center p-4 bg-muted/50 rounded-lg">
                    <Target className="w-8 h-8 mx-auto mb-2 text-primary" />
                    <p className="text-xs text-muted-foreground">Total Distance</p>
                    <p className="text-xl font-bold text-foreground">
                      {totalDistance.toFixed(1)} km
                    </p>
                  </div>
                  <div className="text-center p-4 bg-muted/50 rounded-lg">
                    <TrendingUp className="w-8 h-8 mx-auto mb-2 text-primary" />
                    <p className="text-xs text-muted-foreground">Total Elevation</p>
                    <p className="text-xl font-bold text-foreground">
                      {totalElevation} m
                    </p>
                  </div>
                  <div className="text-center p-4 bg-muted/50 rounded-lg">
                    <Mountain className="w-8 h-8 mx-auto mb-2 text-secondary" />
                    <p className="text-xs text-muted-foreground">Routes Done</p>
                    <p className="text-xl font-bold text-foreground">
                      {stats ? stats.routes_completed : completedRoutes.length}
                    </p>
                  </div>
                  <div className="text-center p-4 bg-muted/50 rounded-lg">
                    <Award className="w-8 h-8 mx-auto mb-2 text-accent" />
                    <p className="text-xs text-muted-foreground">Achievements</p>
                    <p className="text-xl font-bold text-foreground">
                      {stats ? stats.achievements_unlocked : unlockedAchievements.length}
                    </p>
                  </div>
                </div>
              </Card>

              {/* User Preferences */}
              <Card className="p-6 border-2 border-border">
                <h3 className="text-lg font-bold text-foreground mb-4 flex items-center gap-2">
                  <Sliders className="w-5 h-5 text-primary" />
                  Your Preferences
                </h3>
                {isLoadingPreferences ? (
                  <div className="flex items-center justify-center py-4">
                    <Loader2 className="w-5 h-5 animate-spin text-muted-foreground" />
                    <span className="ml-2 text-sm text-muted-foreground">Loading preferences...</span>
                  </div>
                ) : userPreferences ? (
                  <div className="grid md:grid-cols-2 gap-4">
                    {/* Difficulty Range */}
                    {userPreferences.difficulty_range && (
                      <div className="p-4 bg-muted/50 rounded-lg">
                        <p className="text-xs text-muted-foreground mb-1">Difficulty Range</p>
                        <p className="text-lg font-bold text-foreground">
                          {userPreferences.difficulty_range[0]} - {userPreferences.difficulty_range[1]}
                        </p>
                        <p className="text-xs text-muted-foreground mt-1">
                          {userPreferences.difficulty_range[0] === 0 && userPreferences.difficulty_range[1] === 1 && 'Beginner friendly'}
                          {userPreferences.difficulty_range[0] === 1 && userPreferences.difficulty_range[1] === 2 && 'Intermediate level'}
                          {userPreferences.difficulty_range[0] === 2 && userPreferences.difficulty_range[1] === 3 && 'Advanced challenges'}
                        </p>
                      </div>
                    )}

                    {/* Distance Range */}
                    {(userPreferences.min_distance_km !== undefined || userPreferences.max_distance_km !== undefined) && (
                      <div className="p-4 bg-muted/50 rounded-lg">
                        <p className="text-xs text-muted-foreground mb-1">Distance Range</p>
                        <p className="text-lg font-bold text-foreground">
                          {userPreferences.min_distance_km?.toFixed(1) || 0} - {userPreferences.max_distance_km?.toFixed(1) || 100} km
                        </p>
                        <p className="text-xs text-muted-foreground mt-1">Preferred route length</p>
                      </div>
                    )}

                    {/* Fitness Level */}
                    {userPreferences.fitness_level && (
                      <div className="p-4 bg-muted/50 rounded-lg">
                        <p className="text-xs text-muted-foreground mb-1">Fitness Level</p>
                        <p className="text-lg font-bold text-foreground capitalize">
                          {userPreferences.fitness_level}
                        </p>
                        <p className="text-xs text-muted-foreground mt-1">Your training level</p>
                      </div>
                    )}

                    {/* Preferred Tags */}
                    {userPreferences.preferred_tags && userPreferences.preferred_tags.length > 0 && (
                      <div className="p-4 bg-muted/50 rounded-lg">
                        <p className="text-xs text-muted-foreground mb-2">Preferred Interests</p>
                        <div className="flex flex-wrap gap-2">
                          {userPreferences.preferred_tags.map((tag, index) => (
                            <Badge key={index} variant="secondary" className="text-xs">
                              {tag}
                            </Badge>
                          ))}
                        </div>
                      </div>
                    )}
                  </div>
                ) : (
                  <p className="text-sm text-muted-foreground text-center py-4">
                    No preference data available
                  </p>
                )}
              </Card>

              {/* Activity Breakdown */}
              <Card className="p-6 border-2 border-border">
                <h3 className="text-lg font-bold text-foreground mb-4">Activity Breakdown</h3>
                <div className="space-y-3">
                  {['running', 'hiking', 'cycling'].map(type => {
                    const backendCount = stats?.activity_breakdown?.[type] ?? 0;
                    const fallbackCount = completedRoutes.filter(r => r.route.type === type).length;
                    const count = backendCount || fallbackCount;
                    const totalRoutes = stats?.routes_completed || completedRoutes.length;
                    const percentage = totalRoutes > 0 
                      ? (count / totalRoutes) * 100 
                      : 0;
                    
                    return (
                      <div key={type}>
                        <div className="flex justify-between mb-2">
                          <span className="text-sm font-semibold text-foreground capitalize">
                            {type}
                          </span>
                          <span className="text-sm text-muted-foreground">{count} routes</span>
                        </div>
                        <Progress value={percentage} className="h-2" />
                      </div>
                    );
                  })}
                </div>
              </Card>
            </TabsContent>

            {/* Achievements Tab */}
            <TabsContent value="achievements" className="space-y-6">
              {/* Unlocked Achievements */}
              <div>
                <h3 className="text-lg font-bold text-foreground mb-4 flex items-center gap-2">
                  <Trophy className="w-5 h-5 text-accent" />
                  Unlocked (                  {unlockedAchievements.length}/{achievements.length})
                </h3>
                <div className="grid md:grid-cols-2 gap-4">
                  {unlockedAchievements.map(achievement => (
                    <Card key={achievement.id} className="p-4 border-2 border-primary/50 bg-primary/5">
                      <div className="flex items-start gap-3">
                        <div className="text-3xl">{achievement.icon}</div>
                        <div className="flex-1">
                          <h4 className="font-bold text-foreground">{achievement.name}</h4>
                          <p className="text-sm text-muted-foreground">{achievement.description}</p>
                        </div>
                        <div className="shrink-0">
                          <div className="w-8 h-8 rounded-full bg-primary flex items-center justify-center">
                            <span className="text-primary-foreground text-sm">✓</span>
                          </div>
                        </div>
                      </div>
                    </Card>
                  ))}
                </div>
              </div>

              {/* Locked Achievements */}
              {isLoadingAchievements ? (
                <div className="flex items-center justify-center py-8">
                  <Loader2 className="w-6 h-6 animate-spin text-muted-foreground" />
                  <span className="ml-2 text-muted-foreground">Loading achievements...</span>
                </div>
              ) : lockedAchievements.length > 0 ? (
                <div>
                  <h3 className="text-lg font-bold text-foreground mb-4 flex items-center gap-2">
                    <Sparkles className="w-5 h-5 text-muted-foreground" />
                    Locked
                  </h3>
                  <div className="grid md:grid-cols-2 gap-4">
                    {lockedAchievements.map(achievement => (
                      <Card key={achievement.id} className="p-4 border-2 border-border opacity-60">
                        <div className="flex items-start gap-3">
                          <div className="text-3xl grayscale">{achievement.icon}</div>
                          <div className="flex-1">
                            <h4 className="font-bold text-foreground">{achievement.name}</h4>
                            <p className="text-sm text-muted-foreground">{achievement.description}</p>
                          </div>
                        </div>
                      </Card>
                    ))}
                  </div>
                </div>
              ) : achievements.length === 0 ? (
                <div className="text-center py-8 text-muted-foreground">
                  <p>No achievements available. Please check backend connection.</p>
                </div>
              ) : null}
            </TabsContent>

            {/* History Tab */}
            <TabsContent value="history" className="space-y-4">
              <h3 className="text-lg font-bold text-foreground mb-4 flex items-center gap-2">
                <Calendar className="w-5 h-5 text-primary" />
                Completed Routes ({completedRoutes.length})
              </h3>
              
              {isLoadingHistory ? (
                <Card className="p-8 border-2 border-dashed border-border text-center">
                  <Loader2 className="w-6 h-6 mx-auto mb-2 animate-spin text-primary" />
                  <p className="text-muted-foreground">Loading route history...</p>
                </Card>
              ) : historyError ? (
                <Card className="p-4 border-2 border-border bg-destructive/5">
                  <p className="text-sm text-destructive">{historyError}</p>
                </Card>
              ) : completedRoutes.length === 0 ? (
                <Card className="p-8 border-2 border-dashed border-border text-center">
                  <p className="text-muted-foreground">No completed routes yet. Start your first adventure!</p>
                </Card>
              ) : (
                <div className="space-y-3">
                  {completedRoutes.map(completedRoute => (
                    <Card key={completedRoute.souvenirId} className="p-4 border-2 border-border hover:border-primary/50 transition-all">
                      <div className="flex items-center gap-4">
                        <img
                          src={completedRoute.route.imageUrl || "/placeholder.svg"}
                          alt={completedRoute.route.name}
                          className="w-20 h-20 object-cover rounded-lg"
                        />
                        <div className="flex-1">
                          <h4 className="font-bold text-foreground">{completedRoute.route.name}</h4>
                          <p className="text-sm text-muted-foreground flex items-center gap-1">
                            <MapPin className="w-3 h-3" />
                            {completedRoute.route.location}
                          </p>
                          <div className="flex items-center gap-3 mt-2 text-xs">
                            <Badge variant="secondary">{completedRoute.route.difficulty}</Badge>
                            <span className="text-muted-foreground">{completedRoute.route.distance} km</span>
                            <span className="text-accent font-semibold">+{completedRoute.route.xpReward} XP</span>
                          </div>
                        </div>
                      </div>
                    </Card>
                  ))}
                </div>
              )}
            </TabsContent>
          </Tabs>

          {/* Reset Database Section */}
          <div className="mt-8 pt-6 border-t-2 border-border">
            {!showResetConfirm ? (
              <Button
                variant="outline"
                className="w-full border-2 border-destructive/50 hover:bg-destructive/10 hover:border-destructive text-destructive"
                onClick={() => setShowResetConfirm(true)}
              >
                <RotateCcw className="w-4 h-4 mr-2" />
                Reset Database (Delete ALL Users)
              </Button>
            ) : (
              <Card className="p-4 border-2 border-destructive/50 bg-destructive/5">
                <p className="text-sm text-foreground mb-2 font-semibold text-destructive">
                  ⚠️ WARNING: Complete Database Reset
                </p>
                <p className="text-sm text-foreground mb-4">
                  This will delete <strong>ALL user profiles</strong> from the database, including all souvenirs, achievements, and progress. This action cannot be undone.
                </p>
                <div className="flex gap-3">
                  <Button
                    variant="destructive"
                    className="flex-1"
                    onClick={handleResetProfile}
                  >
                    Yes, Delete Everything
                  </Button>
                  <Button
                    variant="outline"
                    className="flex-1"
                    onClick={() => setShowResetConfirm(false)}
                  >
                    Cancel
                  </Button>
                </div>
              </Card>
            )}
          </div>
        </div>
      </Card>
    </div>
  );
}
