#!/usr/bin/env node

/**
 * XP Save Test Script
 * 
 * This script helps test and debug the XP saving functionality
 * when clicking the "check it out in your Souvenir Gallery" link.
 * 
 * Usage:
 *   1. Open your app in the browser
 *   2. Open browser DevTools Console (F12)
 *   3. Copy and paste the code from this script into the console
 *   4. Complete a route and test the Gallery link
 */

const XP_TEST_SCRIPT = `
(function() {
  console.log('%c🧪 XP Save Test Script Loaded', 'color: #007bff; font-size: 16px; font-weight: bold;');
  
  let testState = {
    initialXP: null,
    initialLevel: null,
    initialRoutes: null,
    initialSouvenirs: null,
    galleryClicked: false,
    continueClicked: false,
    xpSaved: false
  };

  function getProfile() {
    try {
      const profileStr = localStorage.getItem('trailsaga-profile');
      if (profileStr) {
        return JSON.parse(profileStr);
      }
    } catch (e) {
      console.error('❌ Error reading profile:', e);
    }
    return null;
  }

  function logState(label, profile) {
    if (!profile) return;
    console.log(\`\\n📊 \${label}:\`, {
      XP: profile.xp || 0,
      Level: profile.level || 1,
      CompletedRoutes: (profile.completedRoutes || []).length,
      Souvenirs: (profile.souvenirs || []).length,
      ProfileID: profile.id || 'N/A'
    });
  }

  function startTest() {
    const profile = getProfile();
    if (!profile) {
      console.warn('⚠️ No profile found. Please complete onboarding first.');
      return;
    }

    testState.initialXP = profile.xp || 0;
    testState.initialLevel = profile.level || 1;
    testState.initialRoutes = (profile.completedRoutes || []).length;
    testState.initialSouvenirs = (profile.souvenirs || []).length;

    console.log('%c🚀 Starting XP Save Test', 'color: #28a745; font-size: 14px; font-weight: bold;');
    logState('Initial State', profile);
    console.log('\\n📝 Instructions:');
    console.log('1. Complete a route in your app');
    console.log('2. On the completion screen, click "check it out in your Souvenir Gallery"');
    console.log('3. Watch this console for results');
    console.log('\\n⏳ Monitoring localStorage changes...');
  }

  function checkXPChange() {
    const profile = getProfile();
    if (!profile) return;

    const currentXP = profile.xp || 0;
    const currentLevel = profile.level || 1;
    const currentRoutes = (profile.completedRoutes || []).length;
    const currentSouvenirs = (profile.souvenirs || []).length;

    if (testState.initialXP === null) {
      startTest();
      return;
    }

    const xpDiff = currentXP - testState.initialXP;
    const levelDiff = currentLevel - testState.initialLevel;
    const routesDiff = currentRoutes - testState.initialRoutes;
    const souvenirsDiff = currentSouvenirs - testState.initialSouvenirs;

    if (xpDiff !== 0 || levelDiff !== 0 || routesDiff !== 0 || souvenirsDiff !== 0) {
      console.log('%c\\n✨ CHANGE DETECTED!', 'color: #ffc107; font-size: 14px; font-weight: bold;');
      logState('Current State', profile);

      if (xpDiff > 0) {
        console.log(\`%c✅ XP INCREASED: +\${xpDiff} XP\`, 'color: #28a745; font-weight: bold;');
        testState.xpSaved = true;
      } else if (xpDiff < 0) {
        console.log(\`%c❌ XP DECREASED: \${xpDiff} XP\`, 'color: #dc3545; font-weight: bold;');
      }

      if (levelDiff > 0) {
        console.log(\`%c🎉 LEVEL UP: Level \${testState.initialLevel} → \${currentLevel}\`, 'color: #28a745; font-weight: bold;');
      }

      if (routesDiff > 0) {
        console.log(\`%c✅ Route completed: +\${routesDiff} route(s)\`, 'color: #28a745; font-weight: bold;');
      }

      if (souvenirsDiff > 0) {
        console.log(\`%c✅ Souvenir added: +\${souvenirsDiff} souvenir(s)\`, 'color: #28a745; font-weight: bold;');
      }

      // Test completion
      if (testState.galleryClicked && testState.xpSaved) {
        console.log('%c\\n🎉 TEST PASSED: XP was saved when clicking Gallery link!', 'color: #28a745; font-size: 16px; font-weight: bold;');
      } else if (testState.galleryClicked && !testState.xpSaved) {
        console.log('%c\\n❌ TEST FAILED: XP was NOT saved when clicking Gallery link!', 'color: #dc3545; font-size: 16px; font-weight: bold;');
        console.log('\\n💡 Possible issues:');
        console.log('  - handleSaveCompletion() may not be called');
        console.log('  - onComplete() callback may not be working');
        console.log('  - handleCompleteRoute() may have errors');
      }

      // Update initial state for next check
      testState.initialXP = currentXP;
      testState.initialLevel = currentLevel;
      testState.initialRoutes = currentRoutes;
      testState.initialSouvenirs = currentSouvenirs;
    }
  }

  // Intercept console logs to detect Gallery click
  const originalLog = console.log;
  console.log = function(...args) {
    const message = args.join(' ');
    if (message.includes('Souvenir link clicked') || message.includes('handleViewSouvenirs called')) {
      testState.galleryClicked = true;
      console.log('%c🔗 Gallery link clicked detected!', 'color: #007bff; font-weight: bold;');
    }
    if (message.includes('Continue Exploring') || message.includes('handleCompletionClose')) {
      testState.continueClicked = true;
      console.log('%c🔘 Continue button clicked detected!', 'color: #007bff; font-weight: bold;');
    }
    originalLog.apply(console, args);
  };

  // Monitor localStorage changes
  const originalSetItem = Storage.prototype.setItem;
  Storage.prototype.setItem = function(key, value) {
    if (key === 'trailsaga-profile') {
      console.log('%c💾 localStorage updated: trailsaga-profile', 'color: #17a2b8;');
      setTimeout(checkXPChange, 100);
    }
    originalSetItem.apply(this, arguments);
  };

  // Also poll for changes (since storage event only fires in other tabs)
  let lastProfileStr = localStorage.getItem('trailsaga-profile');
  setInterval(() => {
    const currentProfileStr = localStorage.getItem('trailsaga-profile');
    if (currentProfileStr !== lastProfileStr) {
      lastProfileStr = currentProfileStr;
      setTimeout(checkXPChange, 100);
    }
  }, 500);

  // Start monitoring
  startTest();

  // Export test functions
  window.XPTest = {
    check: checkXPChange,
    getState: () => testState,
    reset: () => {
      testState.initialXP = null;
      testState.galleryClicked = false;
      testState.continueClicked = false;
      testState.xpSaved = false;
      startTest();
    },
    getProfile: getProfile
  };

  console.log('\\n💡 Test functions available via window.XPTest');
  console.log('   - XPTest.check() - Manually check for changes');
  console.log('   - XPTest.getState() - Get current test state');
  console.log('   - XPTest.reset() - Reset and start new test');
  console.log('   - XPTest.getProfile() - Get current profile');
})();
`;

// Write script to file for easy copy-paste
console.log(XP_TEST_SCRIPT);

// Also create a version that can be saved to file
if (typeof module !== 'undefined' && module.exports) {
  module.exports = XP_TEST_SCRIPT;
}

