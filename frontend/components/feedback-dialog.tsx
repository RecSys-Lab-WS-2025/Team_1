'use client';

import { useState } from 'react';
import { Button } from '@/components/ui/button';
import { Card } from '@/components/ui/card';
import { Route } from '@/lib/mock-data';
import { X } from 'lucide-react';

interface FeedbackDialogProps {
  route: Route;
  onSubmit: (reason: string) => void;
  onClose: () => void;
}

export function FeedbackDialog({ route, onSubmit, onClose }: FeedbackDialogProps) {
  const [selectedReason, setSelectedReason] = useState<string | null>(null);
  const [isSubmitting, setIsSubmitting] = useState(false);

  const reasons = [
    { value: 'too-hard', label: 'Too Difficult', icon: '💪' },
    { value: 'too-easy', label: 'Too Easy', icon: '😴' },
    { value: 'too-far', label: 'Too Far', icon: '🚗' },
    { value: 'not-interested', label: 'Not Interested', icon: '🤷' },
  ];

  const handleSubmit = async () => {
    if (selectedReason && !isSubmitting) {
      setIsSubmitting(true);
      try {
        await onSubmit(selectedReason);
      } catch (error) {
        console.error('Error submitting feedback:', error);
        // Reset submitting state on error so user can try again
        setIsSubmitting(false);
      }
    }
  };

  return (
    <div className="fixed inset-0 bg-black/50 backdrop-blur-sm z-50 flex items-center justify-center p-4">
      <Card className="max-w-md w-full p-6 border-4 border-border shadow-2xl">
        <div className="flex justify-between items-start mb-4">
          <h3 className="text-xl font-bold text-foreground">Help us improve</h3>
          <Button variant="ghost" size="icon" onClick={onClose}>
            <X className="w-5 h-5" />
          </Button>
        </div>

        <p className="text-muted-foreground mb-6">
          What didn't you like about "{route.name}"? Your feedback helps us provide better recommendations.
        </p>

        <div className="space-y-3 mb-6">
          {reasons.map((reason) => (
            <button
              key={reason.value}
              onClick={() => setSelectedReason(reason.value)}
              className={`
                w-full p-4 rounded-lg border-2 text-left transition-all
                ${selectedReason === reason.value
                  ? 'border-primary bg-primary/10 shadow-lg'
                  : 'border-border bg-card hover:border-primary/50 hover:shadow-md'
                }
              `}
            >
              <div className="flex items-center gap-3">
                <span className="text-2xl">{reason.icon}</span>
                <span className="font-semibold text-foreground">{reason.label}</span>
              </div>
            </button>
          ))}
        </div>

        <div className="flex gap-3">
          <Button variant="outline" onClick={onClose} className="flex-1 border-2">
            Cancel
          </Button>
          <Button
            onClick={handleSubmit}
            disabled={!selectedReason || isSubmitting}
            className="flex-1 bg-primary hover:bg-primary/90 text-primary-foreground font-semibold"
          >
            {isSubmitting ? 'Submitting...' : 'Submit Feedback'}
          </Button>
        </div>
      </Card>
    </div>
  );
}
