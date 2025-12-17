'use client';

import { useState, useEffect } from 'react';
import { WelcomeScreen } from '@/components/welcome-screen';
import { OnboardingQuestionnaire } from '@/components/onboarding-questionnaire';
import { RouteRecommendations } from '@/components/route-recommendations';
import { UserProfile, defaultUserProfile } from '@/lib/mock-data';

export default function Home() {
  const [currentView, setCurrentView] = useState<'welcome' | 'onboarding' | 'home'>('welcome');
  const [userProfile, setUserProfile] = useState<UserProfile | null>(null);
  const [isLoggedIn, setIsLoggedIn] = useState(false);

  useEffect(() => {
    // Check if user has completed onboarding
    const savedProfile = localStorage.getItem('trailsaga-profile');
    if (savedProfile) {
      const profile = JSON.parse(savedProfile);
      
      // Verify user exists in backend database
      verifyUserProfile(profile).then((isValid) => {
        if (isValid) {
          setUserProfile(profile);
          setIsLoggedIn(true);
          setCurrentView('home');
        } else {
          // User doesn't exist in backend, clear localStorage and show welcome
          console.warn('User profile not found in backend, clearing local data');
          localStorage.removeItem('trailsaga-profile');
          setUserProfile(null);
          setIsLoggedIn(false);
          setCurrentView('welcome');
        }
      }).catch((error) => {
        // If backend is unavailable, still use local profile
        console.warn('Could not verify user profile:', error);
        setUserProfile(profile);
        setIsLoggedIn(true);
        setCurrentView('home');
      });
    }
  }, []);

  const verifyUserProfile = async (profile: UserProfile): Promise<boolean> => {
    // Only verify if we have a numeric backend profile ID
    if (!profile.id) return false;
    
    const profileIdNum = parseInt(profile.id, 10);
    if (isNaN(profileIdNum)) return false; // Local-only profile, skip verification
    
    try {
      const { apiClient } = await import('@/lib/api-client');
      await apiClient.get(`api/profiles/${profileIdNum}`);
      return true; // User exists in backend
    } catch (error: any) {
      // 404 means user doesn't exist
      if (error?.status === 404) {
        return false;
      }
      // Other errors (network, etc.) - assume user exists to avoid disrupting UX
      throw error;
    }
  };

  const handleStartAdventure = () => {
    setCurrentView('onboarding');
  };

  const handleOnboardingComplete = (profile: UserProfile) => {
    setUserProfile(profile);
    setIsLoggedIn(true);
    localStorage.setItem('trailsaga-profile', JSON.stringify(profile));
    setCurrentView('home');
  };

  const handleGuestExplore = () => {
    setIsLoggedIn(false);
    setCurrentView('home');
  };

  if (currentView === 'welcome') {
    return (
      <WelcomeScreen 
        onStartAdventure={handleStartAdventure}
        onGuestExplore={handleGuestExplore}
      />
    );
  }

  if (currentView === 'onboarding') {
    return (
      <OnboardingQuestionnaire 
        onComplete={handleOnboardingComplete}
      />
    );
  }

  return (
    <RouteRecommendations 
      userProfile={userProfile || defaultUserProfile}
      isLoggedIn={isLoggedIn}
      onUpdateProfile={setUserProfile}
      onGoToQuestionnaire={() => setCurrentView('onboarding')}
      // </CHANGE>
    />
  );
}
