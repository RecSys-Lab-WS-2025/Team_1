'use client';

import { Card } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Progress } from '@/components/ui/progress';
import { UserProfile, mockRoutes } from '@/lib/mock-data';
import { X, Trophy, Target, Mountain, MapPin, TrendingUp, Sparkles, Award, Calendar, RotateCcw } from 'lucide-react';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { useState } from 'react';

interface UserProfileModalProps {
  userProfile: UserProfile;
  onClose: () => void;
}

export function UserProfileModal({ userProfile, onClose }: UserProfileModalProps) {
  const [showResetConfirm, setShowResetConfirm] = useState(false);

  const xpProgress = (userProfile.xp % 300) / 300 * 100;
  const completedRoutes = mockRoutes.filter(r => userProfile.completedRoutes.includes(r.id));
  const totalDistance = completedRoutes.reduce((sum, r) => sum + r.distance, 0);
  const totalElevation = completedRoutes.reduce((sum, r) => sum + r.elevation, 0);

  const handleResetProfile = () => {
    localStorage.clear();
    window.location.href = '/';
  };

  const achievements = [
    {
      id: 'first-steps',
      name: 'First Steps',
      description: 'Complete your first route',
      icon: '🥾',
      unlocked: completedRoutes.length >= 1
    },
    {
      id: 'explorer',
      name: 'Explorer',
      description: 'Complete 3 different routes',
      icon: '🗺️',
      unlocked: completedRoutes.length >= 3
    },
    {
      id: 'hiker',
      name: 'Trail Hiker',
      description: 'Complete a hiking route',
      icon: '⛰️',
      unlocked: completedRoutes.some(r => r.type === 'hiking')
    },
    {
      id: 'runner',
      name: 'Trail Runner',
      description: 'Complete a running route',
      icon: '🏃',
      unlocked: completedRoutes.some(r => r.type === 'running')
    },
    {
      id: 'cyclist',
      name: 'Cyclist',
      description: 'Complete a cycling route',
      icon: '🚴',
      unlocked: completedRoutes.some(r => r.type === 'cycling')
    },
    {
      id: 'level-5',
      name: 'Rising Star',
      description: 'Reach Level 5',
      icon: '⭐',
      unlocked: userProfile.level >= 5
    },
    {
      id: 'xp-1000',
      name: 'XP Collector',
      description: 'Earn 1000 total XP',
      icon: '💎',
      unlocked: userProfile.xp >= 1000
    },
    {
      id: 'distance-50',
      name: 'Long Distance',
      description: 'Travel 50km total',
      icon: '🎯',
      unlocked: totalDistance >= 50
    },
  ];

  const unlockedAchievements = achievements.filter(a => a.unlocked);
  const lockedAchievements = achievements.filter(a => !a.unlocked);

  return (
    <div className="fixed inset-0 bg-black/50 backdrop-blur-sm z-50 flex items-center justify-center p-4 overflow-y-auto">
      <Card className="max-w-4xl w-full my-8 border-4 border-border shadow-2xl">
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
                <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                  <div className="text-center p-4 bg-muted/50 rounded-lg">
                    <Target className="w-8 h-8 mx-auto mb-2 text-primary" />
                    <p className="text-xs text-muted-foreground">Total Distance</p>
                    <p className="text-xl font-bold text-foreground">{totalDistance.toFixed(1)} km</p>
                  </div>
                  <div className="text-center p-4 bg-muted/50 rounded-lg">
                    <TrendingUp className="w-8 h-8 mx-auto mb-2 text-primary" />
                    <p className="text-xs text-muted-foreground">Total Elevation</p>
                    <p className="text-xl font-bold text-foreground">{totalElevation} m</p>
                  </div>
                  <div className="text-center p-4 bg-muted/50 rounded-lg">
                    <Mountain className="w-8 h-8 mx-auto mb-2 text-secondary" />
                    <p className="text-xs text-muted-foreground">Routes Done</p>
                    <p className="text-xl font-bold text-foreground">{completedRoutes.length}</p>
                  </div>
                  <div className="text-center p-4 bg-muted/50 rounded-lg">
                    <Award className="w-8 h-8 mx-auto mb-2 text-accent" />
                    <p className="text-xs text-muted-foreground">Achievements</p>
                    <p className="text-xl font-bold text-foreground">{unlockedAchievements.length}</p>
                  </div>
                </div>
              </Card>

              {/* Activity Breakdown */}
              <Card className="p-6 border-2 border-border">
                <h3 className="text-lg font-bold text-foreground mb-4">Activity Breakdown</h3>
                <div className="space-y-3">
                  {['running', 'hiking', 'cycling'].map(type => {
                    const count = completedRoutes.filter(r => r.type === type).length;
                    const percentage = completedRoutes.length > 0 
                      ? (count / completedRoutes.length) * 100 
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
                  Unlocked ({unlockedAchievements.length}/{achievements.length})
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
              {lockedAchievements.length > 0 && (
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
              )}
            </TabsContent>

            {/* History Tab */}
            <TabsContent value="history" className="space-y-4">
              <h3 className="text-lg font-bold text-foreground mb-4 flex items-center gap-2">
                <Calendar className="w-5 h-5 text-primary" />
                Completed Routes ({completedRoutes.length})
              </h3>
              
              {completedRoutes.length === 0 ? (
                <Card className="p-8 border-2 border-dashed border-border text-center">
                  <p className="text-muted-foreground">No completed routes yet. Start your first adventure!</p>
                </Card>
              ) : (
                <div className="space-y-3">
                  {completedRoutes.map(route => (
                    <Card key={route.id} className="p-4 border-2 border-border hover:border-primary/50 transition-all">
                      <div className="flex items-center gap-4">
                        <img
                          src={route.imageUrl || "/placeholder.svg"}
                          alt={route.name}
                          className="w-20 h-20 object-cover rounded-lg"
                        />
                        <div className="flex-1">
                          <h4 className="font-bold text-foreground">{route.name}</h4>
                          <p className="text-sm text-muted-foreground flex items-center gap-1">
                            <MapPin className="w-3 h-3" />
                            {route.location}
                          </p>
                          <div className="flex items-center gap-3 mt-2 text-xs">
                            <Badge variant="secondary">{route.difficulty}</Badge>
                            <span className="text-muted-foreground">{route.distance} km</span>
                            <span className="text-accent font-semibold">+{route.xpReward} XP</span>
                          </div>
                        </div>
                      </div>
                    </Card>
                  ))}
                </div>
              )}
            </TabsContent>
          </Tabs>

          {/* Reset Profile Section */}
          <div className="mt-8 pt-6 border-t-2 border-border">
            {!showResetConfirm ? (
              <Button
                variant="outline"
                className="w-full border-2 border-destructive/50 hover:bg-destructive/10 hover:border-destructive text-destructive"
                onClick={() => setShowResetConfirm(true)}
              >
                <RotateCcw className="w-4 h-4 mr-2" />
                Reset Profile
              </Button>
            ) : (
              <Card className="p-4 border-2 border-destructive/50 bg-destructive/5">
                <p className="text-sm text-foreground mb-4 font-semibold">
                  Are you sure? This will delete all your progress and return you to the welcome screen.
                </p>
                <div className="flex gap-3">
                  <Button
                    variant="destructive"
                    className="flex-1"
                    onClick={handleResetProfile}
                  >
                    Yes, Reset Everything
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
