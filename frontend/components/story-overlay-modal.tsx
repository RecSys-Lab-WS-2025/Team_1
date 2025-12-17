'use client';

import { Button } from '@/components/ui/button';
import { ArrowRight, X, Scroll } from 'lucide-react';

interface StoryOverlayModalProps {
  type: 'prologue' | 'chapter' | 'epilogue';
  title: string;
  routeName?: string;
  chapterNumber?: number;
  content: string;
  ctaText: string;
  onContinue: () => void;
  questTitle?: string;
  questDescription?: string;
  onAcceptQuest?: () => void;
}

export function StoryOverlayModal({
  type,
  title,
  routeName,
  chapterNumber,
  content,
  ctaText,
  onContinue,
  questTitle,
  questDescription,
  onAcceptQuest
}: StoryOverlayModalProps) {
  const isPrologue = type === 'prologue';
  const isChapter = type === 'chapter';
  const isEpilogue = type === 'epilogue';

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center">
      {/* Dark overlay / scrim */}
      <div className="absolute inset-0 bg-black/70" />
      
      {/* Modal content */}
      <div 
        className={`relative bg-card border-4 border-primary shadow-2xl ${
          isPrologue || isEpilogue 
            ? 'max-w-3xl w-full mx-4' 
            : isChapter
            ? 'max-w-3xl w-full mx-4' // Larger for long chapter content
            : 'max-w-lg w-full mx-4'
        } max-h-[85vh] flex flex-col`}
      >
        {/* Header with scroll-style decoration */}
        <div className="bg-primary/20 border-b-4 border-primary p-6">
          <div className="flex items-center justify-center gap-3 mb-2">
            <Scroll className="w-6 h-6 text-primary" />
            <h2 className="text-2xl font-bold text-foreground text-center">
              {type === 'prologue' && 'Prologue'}
              {type === 'chapter' && `Chapter ${chapterNumber}`}
              {type === 'epilogue' && 'Epilogue'}
            </h2>
            <Scroll className="w-6 h-6 text-primary" />
          </div>
          <p className="text-center text-sm text-muted-foreground font-semibold">
            {routeName || title}
          </p>
        </div>

        {/* Scrollable content area */}
        <div className="flex-1 overflow-y-auto p-6 bg-muted/10">
          <div className="prose prose-base max-w-none">
            <div className="text-foreground leading-relaxed whitespace-pre-line text-base space-y-4">
              {content.split('\n\n').map((paragraph, idx) => (
                <p key={idx} className="mb-4">
                  {paragraph}
            </p>
              ))}
            </div>
          </div>

          {/* Quest teaser section for chapter modals */}
          {isChapter && questTitle && (
            <div className="mt-6 bg-accent/10 border-2 border-accent rounded-lg p-4">
              <div className="flex items-center gap-2 mb-2">
                <span className="text-lg">🎯</span>
                <span className="text-sm font-bold text-accent">QUEST AVAILABLE</span>
              </div>
              <h3 className="font-bold text-foreground mb-1">{questTitle}</h3>
              <p className="text-sm text-muted-foreground">{questDescription}</p>
            </div>
          )}
        </div>

        {/* Footer with CTAs */}
        <div className="border-t-4 border-primary p-6 bg-card">
          {isChapter && questTitle ? (
            <div className="flex flex-col sm:flex-row gap-3">
              <Button
                size="lg"
                className="flex-1 bg-accent hover:bg-accent/90 text-accent-foreground font-bold border-4 border-border"
                onClick={onAcceptQuest}
              >
                Accept Quest
              </Button>
              <Button
                size="lg"
                variant="outline"
                className="flex-1 font-bold border-4 border-border"
                onClick={onContinue}
              >
                Continue
                <ArrowRight className="ml-2 w-5 h-5" />
              </Button>
            </div>
          ) : (
            <Button
              size="lg"
              className="w-full bg-primary hover:bg-primary/90 text-primary-foreground font-bold border-4 border-border"
              onClick={onContinue}
            >
              {ctaText}
              <ArrowRight className="ml-2 w-5 h-5" />
            </Button>
          )}
        </div>
      </div>
    </div>
  );
}
