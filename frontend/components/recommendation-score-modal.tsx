"use client";

import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
import { Progress } from "@/components/ui/progress";
import { Badge } from "@/components/ui/badge";
import { RecommendationScoreBreakdown } from "@/lib/mock-data";
import { TrendingUp, Target, Tags, Info } from "lucide-react";

interface RecommendationScoreModalProps {
  score: number;
  breakdown: RecommendationScoreBreakdown;
  routeName: string;
  open: boolean;
  onClose: () => void;
}

export function RecommendationScoreModal({
  score,
  breakdown,
  routeName,
  open,
  onClose,
}: RecommendationScoreModalProps) {
  const percentage = Math.round(score * 100);

  return (
    <Dialog open={open} onOpenChange={onClose}>
      <DialogContent className="max-w-2xl max-h-[90vh] overflow-y-auto">
        <DialogHeader>
          <DialogTitle className="flex items-center gap-2">
            <TrendingUp className="w-5 h-5 text-primary" />
            Recommendation Score Explanation
          </DialogTitle>
          <DialogDescription>
            How we calculated the match score for{" "}
            <span className="font-semibold text-foreground">{routeName}</span>
          </DialogDescription>
        </DialogHeader>

        <div className="space-y-6 mt-4">
          {/* Overall Score */}
          <div className="p-4 bg-primary/10 rounded-lg border-2 border-primary/20">
            <div className="flex items-center justify-between mb-2">
              <span className="text-sm font-semibold text-muted-foreground">
                Overall Match Score
              </span>
              <Badge variant="default" className="text-lg px-3 py-1">
                {percentage}%
              </Badge>
            </div>
            <Progress value={percentage} className="h-3" />
            <p className="text-xs text-muted-foreground mt-2">
              This score indicates how well this route matches your preferences.
              Higher scores mean better matches!
            </p>
          </div>

          {/* Score Breakdown */}
          <div className="space-y-4">
            <h3 className="text-lg font-semibold flex items-center gap-2">
              <Info className="w-4 h-4" />
              Score Breakdown
            </h3>

            {/* Difficulty Score */}
            <div className="p-4 border-2 rounded-lg">
              <div className="flex items-center justify-between mb-3">
                <div className="flex items-center gap-2">
                  <Target className="w-4 h-4 text-primary" />
                  <span className="font-semibold">Difficulty Match</span>
                  <Badge variant="outline" className="ml-2">
                    Weight: {(breakdown.difficulty.weight * 100).toFixed(0)}%
                  </Badge>
                </div>
                <Badge variant="secondary">
                  {Math.round(breakdown.difficulty.score * 100)}%
                </Badge>
              </div>
              <Progress
                value={breakdown.difficulty.score * 100}
                className="h-2 mb-3"
              />
              <div className="text-sm space-y-1">
                <p className="text-muted-foreground">
                  <span className="font-medium">Your preference:</span>{" "}
                  Difficulty {breakdown.difficulty.user_range[0]} -{" "}
                  {breakdown.difficulty.user_range[1]}
                </p>
                <p className="text-muted-foreground">
                  <span className="font-medium">Route difficulty:</span>{" "}
                  {breakdown.difficulty.route_value}
                </p>
                <p className="text-xs text-muted-foreground mt-2">
                  Weighted contribution:{" "}
                  {Math.round(breakdown.difficulty.weighted_score * 100)}%
                </p>
              </div>
            </div>

            {/* Distance Score */}
            <div className="p-4 border-2 rounded-lg">
              <div className="flex items-center justify-between mb-3">
                <div className="flex items-center gap-2">
                  <TrendingUp className="w-4 h-4 text-primary" />
                  <span className="font-semibold">Distance Match</span>
                  <Badge variant="outline" className="ml-2">
                    Weight: {(breakdown.distance.weight * 100).toFixed(0)}%
                  </Badge>
                </div>
                <Badge variant="secondary">
                  {Math.round(breakdown.distance.score * 100)}%
                </Badge>
              </div>
              <Progress
                value={breakdown.distance.score * 100}
                className="h-2 mb-3"
              />
              <div className="text-sm space-y-1">
                <p className="text-muted-foreground">
                  <span className="font-medium">Your preference:</span>{" "}
                  {breakdown.distance.user_range[0].toFixed(1)} -{" "}
                  {breakdown.distance.user_range[1].toFixed(1)} km
                </p>
                <p className="text-muted-foreground">
                  <span className="font-medium">Route distance:</span>{" "}
                  {breakdown.distance.route_value.toFixed(1)} km
                </p>
                <p className="text-xs text-muted-foreground mt-2">
                  Weighted contribution:{" "}
                  {Math.round(breakdown.distance.weighted_score * 100)}%
                </p>
              </div>
            </div>

            {/* Tags Score */}
            <div className="p-4 border-2 rounded-lg">
              <div className="flex items-center justify-between mb-3">
                <div className="flex items-center gap-2">
                  <Tags className="w-4 h-4 text-primary" />
                  <span className="font-semibold">Tag Match</span>
                  <Badge variant="outline" className="ml-2">
                    Weight: {(breakdown.tags.weight * 100).toFixed(0)}%
                  </Badge>
                </div>
                <Badge variant="secondary">
                  {Math.round(breakdown.tags.score * 100)}%
                </Badge>
              </div>
              <Progress
                value={breakdown.tags.score * 100}
                className="h-2 mb-3"
              />
              <div className="text-sm space-y-2">
                <div>
                  <p className="font-medium text-muted-foreground mb-1">
                    Your interests:
                  </p>
                  <div className="flex flex-wrap gap-1">
                    {breakdown.tags.user_tags.length > 0 ? (
                      breakdown.tags.user_tags.map((tag, i) => (
                        <Badge key={i} variant="outline" className="text-xs">
                          {tag}
                        </Badge>
                      ))
                    ) : (
                      <span className="text-xs text-muted-foreground">
                        None specified
                      </span>
                    )}
                  </div>
                </div>
                <div>
                  <p className="font-medium text-muted-foreground mb-1">
                    Route tags:
                  </p>
                  <div className="flex flex-wrap gap-1">
                    {breakdown.tags.route_tags.length > 0 ? (
                      breakdown.tags.route_tags.map((tag, i) => (
                        <Badge
                          key={i}
                          variant={
                            breakdown.tags.user_tags.includes(tag.toLowerCase())
                              ? "default"
                              : "outline"
                          }
                          className="text-xs"
                        >
                          {tag}
                        </Badge>
                      ))
                    ) : (
                      <span className="text-xs text-muted-foreground">
                        No tags
                      </span>
                    )}
                  </div>
                </div>
                <p className="text-xs text-muted-foreground mt-2">
                  Weighted contribution:{" "}
                  {Math.round(breakdown.tags.weighted_score * 100)}%
                </p>
              </div>
            </div>
          </div>

          {/* Algorithm Info */}
          <div className="p-4 bg-muted/50 rounded-lg border border-border space-y-3">
            <p className="text-xs text-muted-foreground">
              <strong>How it works:</strong> We use Content-Based Filtering
              (CBF) to match routes to your preferences. Each factor (difficulty,
              distance, tags) is scored individually and then combined using
              weighted averages. The final score ranges from 0% (poor match) to
              100% (perfect match).
            </p>
            
            {/* Feedback Penalty Info */}
            {breakdown.feedback_adjusted && breakdown.feedback_penalty !== undefined && (
              <div className="p-3 bg-orange-50 dark:bg-orange-950/20 rounded border border-orange-200 dark:border-orange-800">
                <p className="text-xs font-semibold text-orange-900 dark:text-orange-200 mb-1">
                  ⚠️ Feedback Penalty Applied
                </p>
                <p className="text-xs text-orange-800 dark:text-orange-300">
                  This route has received negative feedback from you. The score has been reduced:
                </p>
                <ul className="text-xs text-orange-700 dark:text-orange-400 mt-2 ml-4 list-disc space-y-1">
                  <li>1 feedback: Score reduced to 50%</li>
                  <li>2 feedbacks: Score reduced to 10%</li>
                  <li>3+ feedbacks: Score reduced to 1%</li>
                </ul>
                <p className="text-xs text-orange-800 dark:text-orange-300 mt-2">
                  Base score: {Math.round((breakdown.base_score || score) * 100)}% → 
                  Final score: {Math.round(score * 100)}% 
                  (Penalty: {Math.round((breakdown.feedback_penalty || 1) * 100)}%)
                </p>
              </div>
            )}
          </div>
        </div>
      </DialogContent>
    </Dialog>
  );
}



