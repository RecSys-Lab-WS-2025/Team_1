'use client';

import { Card } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Route, UserProfile } from '@/lib/mock-data';
import { Trophy, Sparkles, ArrowRight } from 'lucide-react';
import { useState, useEffect } from 'react';

interface CompletionSummaryProps {
  route: Route;
  userProfile: UserProfile;
  xpGained: number;
  questsCompleted: number;
  /**
   * Optional AI-generated trip summary (from backend post-run summary).
   * If provided, this will be shown instead of the deterministic summary.
   */
  aiSummary?: string | null;
  onClose: () => void;
  onViewSouvenirs?: () => void;
}

export function CompletionSummary({
  route,
  userProfile,
  xpGained,
  questsCompleted,
  aiSummary,
  onClose,
  onViewSouvenirs,
}: CompletionSummaryProps) {
  const XP_PER_LEVEL = 300;
  const oldTotalXP = userProfile.xp;
  const newTotalXP = userProfile.xp + xpGained;
  const oldLevel = Math.floor(oldTotalXP / XP_PER_LEVEL) + 1;
  const newLevel = Math.floor(newTotalXP / XP_PER_LEVEL) + 1;
  const leveledUp = newLevel > oldLevel;
  
  const oldXPInCurrentLevel = oldTotalXP % XP_PER_LEVEL;
  const newXPInCurrentLevel = newTotalXP % XP_PER_LEVEL;
  const xpToNextLevel = XP_PER_LEVEL - newXPInCurrentLevel;
  
  const [animatedXP, setAnimatedXP] = useState(oldXPInCurrentLevel);
  const [showLevelUpCelebration, setShowLevelUpCelebration] = useState(false);

  useEffect(() => {
    const timer = setTimeout(() => {
      if (leveledUp) {
        setAnimatedXP(XP_PER_LEVEL);
        setTimeout(() => {
          setShowLevelUpCelebration(true);
          setTimeout(() => {
            setAnimatedXP(newXPInCurrentLevel);
            setTimeout(() => {
              setShowLevelUpCelebration(false);
            }, 2000);
          }, 500);
        }, 1000);
      } else {
        setAnimatedXP(newXPInCurrentLevel);
      }
    }, 500);
    return () => clearTimeout(timer);
  }, []);

  /**
   * Deterministic trip summary (no AI / randomness).
   */
  const getDeterministicSummary = () => {
    const difficultyLabel = route.difficulty;
    return `You completed ${route.name}, a ${difficultyLabel} route, earning ${xpGained} XP as a ${userProfile.explorerType}. Keep exploring to unlock more adventures and routes. 🤍`;
  };

  // Prefer AI-generated summary when available, fall back to deterministic one
  const tripSummaryText = aiSummary && aiSummary.trim().length > 0
    ? aiSummary
    : getDeterministicSummary();
  const isAiSummary = !!(aiSummary && aiSummary.trim().length > 0);

  return (
    <div className="min-h-screen bg-gradient-to-b from-primary/20 via-background to-accent/20 flex items-center justify-center p-4">
      <Card className="max-w-2xl w-full p-8 md:p-12 bg-card/95 backdrop-blur-sm border-4 border-primary shadow-2xl">
        <div className="text-center space-y-8">
          <div className="flex justify-center">
            <div className="relative">
              <div className="w-24 h-24 rounded-full bg-primary/20 flex items-center justify-center animate-pulse">
                <Trophy className="w-16 h-16 text-primary" />
              </div>
              {leveledUp && (
                <div className="absolute -top-2 -right-2">
                  <Sparkles className="w-12 h-12 text-accent animate-spin" style={{ animationDuration: '3s' }} />
                </div>
              )}
            </div>
          </div>

          <div className="space-y-2">
            <h1 className="text-3xl md:text-4xl font-bold text-foreground">
              Journey Complete!
            </h1>
            <p className="text-xl text-muted-foreground">{route.name}</p>
          </div>

          {leveledUp && (
            <Badge className="text-lg px-6 py-2 bg-accent text-accent-foreground">
              Level Up! Now Level {newLevel}
            </Badge>
          )}

          <Card className="p-6 bg-muted/50 border-2 border-border">
            <h3 className="font-semibold text-foreground mb-4 text-lg">XP Breakdown</h3>
            <div className="space-y-3">
              <div className="flex justify-between items-center">
                <span className="text-muted-foreground">Base Route XP</span>
                <span className="font-bold text-foreground">{route.xpReward} XP</span>
              </div>
              <div className="flex justify-between items-center">
                <span className="text-muted-foreground">Mini Quests Completed</span>
                <span className="font-bold text-foreground">{questsCompleted}</span>
              </div>
              <div className="flex justify-between items-center">
                <span className="text-muted-foreground">Difficulty Multiplier</span>
                <span className="font-bold text-foreground capitalize">{route.difficulty}</span>
              </div>
              <div className="border-t-2 border-border pt-3 flex justify-between items-center">
                <span className="font-semibold text-foreground text-lg">Total XP Earned</span>
                <span className="font-bold text-accent text-2xl">+{xpGained} XP</span>
              </div>
            </div>
          </Card>

          <div className="relative">
            <Card className="p-4 bg-muted/30 border-2 border-border">
              <div className="space-y-3">
                <div className="flex justify-between items-center">
                  <span className="text-sm font-semibold text-foreground">
                    Level {newLevel} {userProfile.explorerType}
                  </span>
                  <span className="text-xs text-muted-foreground">
                    {newXPInCurrentLevel} / {XP_PER_LEVEL} XP to next level
                  </span>
                </div>
                
                <div className="h-3 bg-muted rounded-full overflow-hidden border-2 border-primary/30">
                  <div
                    className="h-full bg-gradient-to-r from-primary to-accent transition-all duration-1000 ease-out"
                    style={{ width: `${(animatedXP / XP_PER_LEVEL) * 100}%` }}
                  />
                </div>
                
                {showLevelUpCelebration && (
                  <div className="flex items-center justify-center gap-2 animate-pulse">
                    <Sparkles className="w-5 h-5 text-accent" />
                    <span className="text-sm font-bold text-accent">
                      Congrats! You reached Level {newLevel} on this route!
                    </span>
                    <Sparkles className="w-5 h-5 text-accent" />
                  </div>
                )}
              </div>
            </Card>
          </div>

          <Card className="p-6 bg-secondary/10 border-2 border-secondary">
            <div className="space-y-3">
              <div className="flex items-center justify-center gap-2">
                <Sparkles className="w-5 h-5 text-secondary" />
                <h3 className="font-semibold text-foreground">
                  {isAiSummary ? 'AI Trip Summary' : 'Trip Summary'}
                </h3>
              </div>
              
              {!isAiSummary && (
                <div className="flex items-center justify-center gap-2 text-xs text-muted-foreground">
                  <Sparkles className="w-4 h-4 animate-spin text-secondary" />
                  <span>Generating AI Trip Summary...</span>
                </div>
              )}

              <p className="text-foreground leading-relaxed italic">
                {tripSummaryText}
              </p>
            </div>
          </Card>

          <div className="text-center text-sm text-muted-foreground">
            You've earned a new digital souvenir —{' '}
            <button
              onClick={() => {
                console.log('[v0] Souvenir link clicked, onViewSouvenirs:', onViewSouvenirs);
                // Save XP first by calling onClose, then open gallery
                if (onClose) {
                  console.log('[v0] Calling onClose to save XP before opening gallery');
                  onClose();
                }
                // Then open gallery after a short delay to ensure save completes
                if (onViewSouvenirs) {
                  setTimeout(() => {
                    console.log('[v0] Opening gallery after XP save');
                    onViewSouvenirs();
                  }, 100);
                }
              }}
              className="text-primary hover:text-primary/80 underline font-semibold"
            >
              check it out in your Souvenir Gallery
            </button>
          </div>

          <Button
            size="lg"
            className="w-full py-6 text-lg bg-primary hover:bg-primary/90 text-primary-foreground font-semibold shadow-lg"
            onClick={onClose}
          >
            Continue Exploring
            <ArrowRight className="ml-2 w-5 h-5" />
          </Button>
        </div>
      </Card>
    </div>
  );
}
