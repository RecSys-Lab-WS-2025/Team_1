'use client';

import { useState, useEffect } from 'react';
import { Card } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { DigitalSouvenir } from '@/lib/mock-data';
import { apiClient } from '@/lib/api-client';
import { transformApiSouvenirs } from '@/lib/api-transforms';
import { Trophy, MapPin, Calendar, Sparkles, X, Mountain, Footprints, TrendingUp, ChevronDown, ChevronUp } from 'lucide-react';

interface SouvenirGalleryProps {
  souvenirs: DigitalSouvenir[];
  onClose: () => void;
  profileId?: string | null;
  isLoggedIn?: boolean;
  refreshTrigger?: number; // Force refresh when this changes
}

export function SouvenirGallery({ 
  souvenirs: initialSouvenirs, 
  onClose, 
  profileId,
  isLoggedIn = false,
  refreshTrigger = 0
}: SouvenirGalleryProps) {
  const [souvenirs, setSouvenirs] = useState<DigitalSouvenir[]>(initialSouvenirs);
  const [isLoading, setIsLoading] = useState(false);
  const [sortBy, setSortBy] = useState<'newest' | 'oldest' | 'xp_high' | 'xp_low'>('newest');
  const [expandedSummaries, setExpandedSummaries] = useState<Set<string>>(new Set());
  const [expandedBreakdowns, setExpandedBreakdowns] = useState<Set<string>>(new Set());

  // Update souvenirs when initialSouvenirs prop changes
  useEffect(() => {
    if (!isLoggedIn || !profileId) {
      // For non-logged-in users, use prop directly
      setSouvenirs(initialSouvenirs);
    }
  }, [initialSouvenirs, isLoggedIn, profileId]);

  // Load souvenirs from backend if user is logged in
  useEffect(() => {
    if (isLoggedIn && profileId) {
      loadSouvenirsFromBackend();
    }
  }, [isLoggedIn, profileId]);

  // Reload when sort changes (only if loading from backend)
  useEffect(() => {
    if (isLoggedIn && profileId) {
      loadSouvenirsFromBackend();
    }
  }, [sortBy]);

  // Reload when refreshTrigger changes (e.g., when gallery is opened after completing a route)
  useEffect(() => {
    if (isLoggedIn && profileId && refreshTrigger > 0) {
      // Add a longer delay when refreshTrigger changes to ensure backend has processed
      const timer = setTimeout(() => {
        loadSouvenirsFromBackend();
      }, 800);
      return () => clearTimeout(timer);
    }
  }, [refreshTrigger]);

  const loadSouvenirsFromBackend = async (retryCount = 0) => {
    if (!profileId) {
      setIsLoading(false);
      return;
    }
    
    setIsLoading(true);
    try {
      const profileIdNum = parseInt(profileId, 10);
      if (!isNaN(profileIdNum)) {
        // Add a delay to ensure backend has saved the new souvenir (longer on retry)
        const delay = retryCount > 0 ? 1000 : 500;
        await new Promise(resolve => setTimeout(resolve, delay));
        
        const response = await apiClient.getSouvenirs(profileIdNum, {
          limit: 100,
          sort: sortBy,
        });
        const transformed = transformApiSouvenirs(response.souvenirs);
        setSouvenirs(transformed);
        setIsLoading(false); // Set loading to false immediately after setting souvenirs
        console.log(`[SouvenirGallery] Loaded ${transformed.length} souvenirs from backend`);
        return; // Early return to avoid fallback
      }
    } catch (error) {
      console.error('Failed to load souvenirs from backend:', error);
      
      // Retry once if this is the first attempt and we have a refresh trigger
      // Limit retries to prevent infinite loops
      if (retryCount === 0 && refreshTrigger > 0 && retryCount < 2) {
        console.log('[SouvenirGallery] Retrying load after 1 second...');
        setTimeout(() => {
          loadSouvenirsFromBackend(retryCount + 1);
        }, 1000);
        return; // Don't set loading to false yet, will retry
      }
      
      // Fallback to initialSouvenirs or localStorage
      try {
        if (typeof window !== 'undefined') {
          const profileStr = localStorage.getItem('trailsaga-profile');
          if (profileStr) {
            const profile = JSON.parse(profileStr);
            if (profile.souvenirs && Array.isArray(profile.souvenirs)) {
              // Convert localStorage souvenirs to DigitalSouvenir format
              const localSouvenirs = profile.souvenirs.map((s: any) => ({
                ...s,
                completedAt: s.completedAt ? new Date(s.completedAt) : new Date(),
              }));
              setSouvenirs(localSouvenirs);
              setIsLoading(false);
              console.log(`[SouvenirGallery] Loaded ${localSouvenirs.length} souvenirs from localStorage`);
              return;
            }
          }
        }
      } catch (e) {
        console.error('Failed to load from localStorage:', e);
      }
      // Final fallback to initialSouvenirs
      setSouvenirs(initialSouvenirs);
      setIsLoading(false);
      console.log(`[SouvenirGallery] Using initialSouvenirs: ${initialSouvenirs.length} souvenirs`);
    }
    // Note: setIsLoading(false) is now handled in each branch above
  };

  const toggleSummary = (souvenirId: string) => {
    const newSet = new Set(expandedSummaries);
    if (newSet.has(souvenirId)) {
      newSet.delete(souvenirId);
    } else {
      newSet.add(souvenirId);
    }
    setExpandedSummaries(newSet);
  };

  const toggleBreakdown = (souvenirId: string) => {
    const newSet = new Set(expandedBreakdowns);
    if (newSet.has(souvenirId)) {
      newSet.delete(souvenirId);
    } else {
      newSet.add(souvenirId);
    }
    setExpandedBreakdowns(newSet);
  };

  // Get AI summary and XP breakdown from souvenir data
  const getSouvenirMetadata = (souvenir: DigitalSouvenir) => {
    return {
      genaiSummary: souvenir.genaiSummary || null,
      xpBreakdown: souvenir.xpBreakdown || null,
    };
  };

  const sortedSouvenirs = [...souvenirs].sort((a, b) => {
    switch (sortBy) {
      case 'newest':
        return new Date(b.completedAt).getTime() - new Date(a.completedAt).getTime();
      case 'oldest':
        return new Date(a.completedAt).getTime() - new Date(b.completedAt).getTime();
      case 'xp_high':
        return b.xpGained - a.xpGained;
      case 'xp_low':
        return a.xpGained - b.xpGained;
      default:
        return 0;
    }
  });

  const stats = {
    total: souvenirs.length,
    totalXP: souvenirs.reduce((sum, s) => sum + s.xpGained, 0),
    totalDistance: souvenirs.reduce((sum, s) => sum + s.distance, 0)
  };

  return (
    <div className="fixed inset-0 bg-background z-50 overflow-y-auto">
      {/* Header */}
      <header className="border-b-4 border-border bg-card/80 backdrop-blur-sm sticky top-0 z-10">
        <div className="container mx-auto px-4 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <Trophy className="w-8 h-8 text-accent" strokeWidth={2.5} />
              <h1 className="text-2xl font-bold text-foreground">
                My Souvenir Gallery
              </h1>
            </div>
            <Button variant="outline" size="icon" onClick={onClose} className="border-2">
              <X className="w-5 h-5" />
            </Button>
          </div>
        </div>
      </header>

      <main className="container mx-auto px-4 py-8">
        <div className="mb-6 text-center">
          <p className="text-lg text-foreground">
            You've collected <span className="font-bold text-accent">{stats.total}</span> adventure {stats.total === 1 ? 'souvenir' : 'souvenirs'}. 
            <br />
            <span className="text-muted-foreground">Keep exploring to expand your collection.</span>
          </p>
        </div>

        {/* Sort Controls */}
        {souvenirs.length > 0 && (
          <div className="mb-6 flex justify-end">
            <Select value={sortBy} onValueChange={(value: any) => setSortBy(value)}>
              <SelectTrigger className="w-[180px]">
                <SelectValue placeholder="Sort by" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="newest">Newest First</SelectItem>
                <SelectItem value="oldest">Oldest First</SelectItem>
                <SelectItem value="xp_high">Most XP</SelectItem>
                <SelectItem value="xp_low">Least XP</SelectItem>
              </SelectContent>
            </Select>
          </div>
        )}

        {/* Stats Overview */}
        <div className="grid md:grid-cols-3 gap-4 mb-8">
          <Card className="p-6 border-2 border-border bg-gradient-to-br from-primary/10 to-primary/5">
            <div className="flex items-center gap-3">
              <div className="w-12 h-12 rounded-full bg-primary/20 flex items-center justify-center">
                <Trophy className="w-6 h-6 text-primary" />
              </div>
              <div>
                <p className="text-sm text-muted-foreground">Total Adventures</p>
                <p className="text-2xl font-bold text-foreground">{stats.total}</p>
              </div>
            </div>
          </Card>

          <Card className="p-6 border-2 border-border bg-gradient-to-br from-accent/10 to-accent/5">
            <div className="flex items-center gap-3">
              <div className="w-12 h-12 rounded-full bg-accent/20 flex items-center justify-center">
                <Sparkles className="w-6 h-6 text-accent" />
              </div>
              <div>
                <p className="text-sm text-muted-foreground">Total XP Earned</p>
                <p className="text-2xl font-bold text-foreground">{stats.totalXP}</p>
              </div>
            </div>
          </Card>

          <Card className="p-6 border-2 border-border bg-gradient-to-br from-secondary/10 to-secondary/5">
            <div className="flex items-center gap-3">
              <div className="w-12 h-12 rounded-full bg-secondary/20 flex items-center justify-center">
                <Footprints className="w-6 h-6 text-secondary" />
              </div>
              <div>
                <p className="text-sm text-muted-foreground">Total Distance</p>
                <p className="text-2xl font-bold text-foreground">{stats.totalDistance.toFixed(1)} km</p>
              </div>
            </div>
          </Card>
        </div>

        {/* Loading State */}
        {isLoading && (
          <Card className="p-12 text-center border-2 border-border">
            <p className="text-muted-foreground">Loading souvenirs...</p>
          </Card>
        )}

        {/* Souvenir Grid */}
        {!isLoading && sortedSouvenirs.length === 0 ? (
          <Card className="p-12 text-center border-2 border-border">
            <Trophy className="w-16 h-16 mx-auto mb-4 text-muted-foreground" />
            <h2 className="text-xl font-bold text-foreground mb-2">No Souvenirs Yet</h2>
            <p className="text-muted-foreground">
              Complete your first route to earn your first digital souvenir!
            </p>
          </Card>
        ) : (
          <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
            {sortedSouvenirs.map((souvenir) => {
              const metadata = getSouvenirMetadata(souvenir);
              const isSummaryExpanded = expandedSummaries.has(souvenir.id);
              const isBreakdownExpanded = expandedBreakdowns.has(souvenir.id);
              const hasPixelArt = !!souvenir.pixelImageSvg;
              
              // Parse XP breakdown if available
              let xpBreakdown: any = null;
              if (metadata.xpBreakdown) {
                try {
                  xpBreakdown = typeof metadata.xpBreakdown === 'string' 
                    ? JSON.parse(metadata.xpBreakdown) 
                    : metadata.xpBreakdown;
                } catch (e) {
                  // Ignore parse errors
                }
              }
              
              return (
              <Card 
                key={souvenir.id}
                className="overflow-hidden border-0 bg-transparent shadow-none"
              >
                {/* Pixel Art SVG - Always use template-generated SVG */}
                {souvenir.pixelImageSvg ? (
                  <div 
                    className="w-full flex items-center justify-center"
                    style={{ 
                      imageRendering: 'pixelated',
                      aspectRatio: '4/3', // SVG viewBox is 400x300
                    }}
                  >
                    <div
                      dangerouslySetInnerHTML={{ __html: souvenir.pixelImageSvg }}
                      style={{
                        width: '100%',
                        height: 'auto',
                        display: 'block',
                        maxWidth: '100%',
                      }}
                      className="w-full"
                    />
                  </div>
                ) : (
                  // Placeholder if SVG is missing (should not happen - SVG is generated when souvenir is created)
                  <div className="w-full aspect-[4/3] bg-muted/50 flex items-center justify-center border-2 border-dashed border-border">
                    <div className="text-center p-4">
                      <Trophy className="w-12 h-12 mx-auto mb-2 text-muted-foreground" />
                      <p className="text-sm text-muted-foreground">SVG Missing</p>
                      <p className="text-xs text-muted-foreground mt-1">Run batch script to generate</p>
                    </div>
                  </div>
                )}

                {/* Content - Only show expandable sections (AI Summary, XP Breakdown) */}
                <div className="pt-4 space-y-3">

                  {/* AI Summary */}
                  {metadata.genaiSummary && (
                    <div className="pt-3 border-t-2 border-border">
                      <Button
                        variant="ghost"
                        size="sm"
                        className="w-full justify-between p-0 h-auto"
                        onClick={() => toggleSummary(souvenir.id)}
                      >
                        <span className="text-sm font-semibold text-foreground flex items-center gap-2">
                          <Sparkles className="w-4 h-4 text-accent" />
                          AI Summary
                        </span>
                        {isSummaryExpanded ? (
                          <ChevronUp className="w-4 h-4" />
                        ) : (
                          <ChevronDown className="w-4 h-4" />
                        )}
                      </Button>
                      {isSummaryExpanded && (
                        <p className="mt-2 text-sm text-muted-foreground italic">
                          {metadata.genaiSummary}
                        </p>
                      )}
                    </div>
                  )}

                  {/* XP Breakdown */}
                  {xpBreakdown && (
                    <div className="pt-3 border-t-2 border-border">
                      <Button
                        variant="ghost"
                        size="sm"
                        className="w-full justify-between p-0 h-auto"
                        onClick={() => toggleBreakdown(souvenir.id)}
                      >
                        <span className="text-sm font-semibold text-foreground flex items-center gap-2">
                          <TrendingUp className="w-4 h-4 text-accent" />
                          XP Breakdown
                        </span>
                        {isBreakdownExpanded ? (
                          <ChevronUp className="w-4 h-4" />
                        ) : (
                          <ChevronDown className="w-4 h-4" />
                        )}
                      </Button>
                      {isBreakdownExpanded && (
                        <div className="mt-2 space-y-1 text-sm">
                          <div className="flex justify-between">
                            <span className="text-muted-foreground">Base XP:</span>
                            <span className="font-semibold">{xpBreakdown.base || 0}</span>
                          </div>
                          <div className="flex justify-between">
                            <span className="text-muted-foreground">Quest XP:</span>
                            <span className="font-semibold">{xpBreakdown.quests || 0}</span>
                          </div>
                          <div className="flex justify-between">
                            <span className="text-muted-foreground">Multiplier:</span>
                            <span className="font-semibold">×{xpBreakdown.difficulty_multiplier || 1.0}</span>
                          </div>
                          <div className="flex justify-between pt-1 border-t border-border">
                            <span className="font-semibold text-foreground">Total:</span>
                            <span className="font-bold text-accent">{xpBreakdown.total || souvenir.xpGained} XP</span>
                          </div>
                        </div>
                      )}
                    </div>
                  )}

                  {/* Badges */}
                  {souvenir.badgesEarned.length > 0 && (
                    <div className="flex flex-wrap gap-1">
                      {souvenir.badgesEarned.map((badge, index) => (
                        <Badge key={index} variant="outline" className="text-xs">
                          {badge}
                        </Badge>
                      ))}
                    </div>
                  )}
                </div>
              </Card>
              );
            })}
          </div>
        )}
      </main>
    </div>
  );
}
