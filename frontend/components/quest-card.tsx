'use client';

import { useState } from 'react';
import { Card } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { MiniQuest } from '@/lib/mock-data';
import { Camera, HelpCircle, Eye, CheckCircle2, Sparkles, X } from 'lucide-react';

interface QuestCardProps {
  quest: MiniQuest;
  onComplete: () => void;
  onSkip?: () => void;
}

export function QuestCard({ quest, onComplete, onSkip }: QuestCardProps) {
  const [selectedAnswer, setSelectedAnswer] = useState<number | null>(null);
  const [submitted, setSubmitted] = useState(false);
  const [isCorrect, setIsCorrect] = useState(false);

  const handlePhotoQuest = () => {
    // Simulate photo upload
    setTimeout(() => {
      setSubmitted(true);
      setIsCorrect(true);
      setTimeout(() => {
        onComplete();
      }, 1000);
    }, 500);
  };

  const handleQuizSubmit = () => {
    if (selectedAnswer === null) return;
    
    const correct = selectedAnswer === quest.correctAnswer;
    setIsCorrect(correct);
    setSubmitted(true);
    
    if (correct) {
      setTimeout(() => {
        onComplete();
      }, 1500);
    }
  };

  const getQuestIcon = () => {
    switch (quest.type) {
      case 'photo':
        return <Camera className="w-8 h-8 text-accent" />;
      case 'quiz':
        return <HelpCircle className="w-8 h-8 text-accent" />;
      case 'observation':
        return <Eye className="w-8 h-8 text-accent" />;
      default:
        return <Sparkles className="w-8 h-8 text-accent" />;
    }
  };

  return (
    <Card className="p-8 border-4 border-accent/50 bg-card/95 shadow-2xl quest-card-appear">
      <div className="space-y-6">
        {/* Skip Button */}
        {onSkip && !submitted && (
          <div className="flex justify-end -mt-4 -mr-4">
            <Button
              variant="ghost"
              size="sm"
              onClick={onSkip}
              className="text-muted-foreground hover:text-foreground"
            >
              <X className="w-4 h-4 mr-1" />
              Skip Quest
            </Button>
          </div>
        )}

        {/* Header */}
        <div className="text-center space-y-3">
          <div className="flex justify-center">
            <div className="w-16 h-16 rounded-full bg-accent/20 flex items-center justify-center">
              {getQuestIcon()}
            </div>
          </div>
          <div>
            <Badge variant="secondary" className="mb-2">Mini Quest</Badge>
            <h2 className="text-2xl md:text-3xl font-bold text-foreground">{quest.title}</h2>
          </div>
        </div>

        {/* Quest Description */}
        <div className="p-6 bg-accent/10 rounded-lg border-2 border-accent/30">
          <p className="text-foreground leading-relaxed text-center">{quest.description}</p>
        </div>

        {/* Quest Content */}
        <div className="space-y-4">
          {quest.type === 'photo' && !submitted && (
            <Button
              size="lg"
              className="w-full py-6 text-lg bg-accent hover:bg-accent/90 text-accent-foreground font-semibold"
              onClick={handlePhotoQuest}
            >
              <Camera className="mr-2 w-5 h-5" />
              Simulate Photo Upload
            </Button>
          )}

          {quest.type === 'quiz' && !submitted && (
            <>
              <div className="space-y-3">
                {quest.choices?.map((choice, index) => (
                  <button
                    key={index}
                    onClick={() => setSelectedAnswer(index)}
                    className={`w-full p-4 rounded-lg border-2 text-left transition-all ${
                      selectedAnswer === index
                        ? 'border-accent bg-accent/10 shadow-lg'
                        : 'border-border bg-card hover:border-accent/50 hover:shadow-md'
                    }`}
                  >
                    <div className="flex items-center gap-3">
                      <div
                        className={`w-6 h-6 rounded-full border-2 flex items-center justify-center ${
                          selectedAnswer === index
                            ? 'border-accent bg-accent'
                            : 'border-border'
                        }`}
                      >
                        {selectedAnswer === index && (
                          <div className="w-3 h-3 rounded-full bg-accent-foreground" />
                        )}
                      </div>
                      <span className="font-semibold text-foreground">{choice}</span>
                    </div>
                  </button>
                ))}
              </div>
              <Button
                size="lg"
                className="w-full py-6 text-lg bg-accent hover:bg-accent/90 text-accent-foreground font-semibold"
                onClick={handleQuizSubmit}
                disabled={selectedAnswer === null}
              >
                Submit Answer
              </Button>
            </>
          )}

          {/* Observation quest or default quest type */}
          {(quest.type === 'observation' || (!quest.type || (quest.type !== 'photo' && quest.type !== 'quiz'))) && !submitted && (
            <Button
              size="lg"
              className="w-full py-6 text-lg bg-accent hover:bg-accent/90 text-accent-foreground font-semibold"
              onClick={() => {
                setSubmitted(true);
                setIsCorrect(true);
                setTimeout(() => {
                  onComplete();
                }, 1000);
              }}
            >
              <CheckCircle2 className="mr-2 w-5 h-5" />
              Complete Quest
            </Button>
          )}

          {/* Result */}
          {submitted && (
            <div
              className={`p-6 rounded-lg border-2 text-center space-y-3 ${
                isCorrect
                  ? 'bg-primary/10 border-primary'
                  : 'bg-destructive/10 border-destructive'
              }`}
            >
              <div className="flex justify-center">
                <div
                  className={`w-12 h-12 rounded-full flex items-center justify-center ${
                    isCorrect ? 'bg-primary' : 'bg-destructive'
                  }`}
                >
                  {isCorrect ? (
                    <CheckCircle2 className="w-7 h-7 text-primary-foreground" />
                  ) : (
                    <span className="text-2xl text-destructive-foreground">✗</span>
                  )}
                </div>
              </div>
              <div>
                <p className={`text-xl font-bold ${isCorrect ? 'text-primary' : 'text-destructive'}`}>
                  {isCorrect ? 'Quest Completed!' : 'Not Quite Right'}
                </p>
                {isCorrect && (
                  <p className="text-accent font-semibold text-lg mt-2">
                    +{quest.xpReward} XP Earned
                  </p>
                )}
                {!isCorrect && quest.correctAnswer !== undefined && (
                  <p className="text-muted-foreground mt-2">
                    Correct answer: {quest.choices?.[quest.correctAnswer]}
                  </p>
                )}
              </div>
              {!isCorrect && (
                <Button
                  variant="outline"
                  onClick={() => {
                    setSubmitted(false);
                    setSelectedAnswer(null);
                  }}
                  className="mt-4"
                >
                  Try Again
                </Button>
              )}
            </div>
          )}
        </div>

        {/* XP Reward Display */}
        {!submitted && (
          <div className="text-center pt-2">
            <p className="text-sm text-muted-foreground">
              Reward: <span className="font-bold text-accent">{quest.xpReward} XP</span>
            </p>
          </div>
        )}
      </div>
    </Card>
  );
}
