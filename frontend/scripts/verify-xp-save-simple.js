#!/usr/bin/env node

/**
 * Simple XP Save Fix Verification
 * Directly reads and analyzes the code
 */

const fs = require('fs');
const path = require('path');

const completionSummaryPath = path.join(__dirname, '..', 'components', 'completion-summary.tsx');
const hikingSimulatorPath = path.join(__dirname, '..', 'components', 'hiking-simulator.tsx');

console.log('🧪 XP Save Fix Verification\n');
console.log('='.repeat(60));

// Check completion-summary.tsx
console.log('\n📄 Checking completion-summary.tsx:');
if (fs.existsSync(completionSummaryPath)) {
  const content = fs.readFileSync(completionSummaryPath, 'utf-8');
  
  // Find the Gallery button section
  const galleryMatch = content.match(/check it out in your Souvenir Gallery[\s\S]{0,200}/);
  
  if (galleryMatch) {
    console.log('✅ Gallery link text found');
    const section = galleryMatch[0];
    
    // Check for onClose call
    if (section.includes('onClose()')) {
      console.log('✅ onClose() is called');
    } else {
      console.log('❌ onClose() is NOT called');
    }
    
    // Check for onViewSouvenirs call
    if (section.includes('onViewSouvenirs()')) {
      console.log('✅ onViewSouvenirs() is called');
    } else {
      console.log('❌ onViewSouvenirs() is NOT called');
    }
    
    // Check for setTimeout
    if (section.includes('setTimeout')) {
      console.log('✅ setTimeout is used');
    } else {
      console.log('❌ setTimeout is NOT used');
    }
    
    // Show the actual code snippet
    console.log('\n📝 Code snippet:');
    const onClickMatch = content.match(/onClick=\{\(\) => \{[\s\S]{0,300}onViewSouvenirs\(\)[\s\S]{0,50}\}/);
    if (onClickMatch) {
      console.log(onClickMatch[0].split('\n').slice(0, 10).join('\n') + '...');
    }
  } else {
    console.log('❌ Gallery link not found');
  }
} else {
  console.log('❌ File not found');
}

// Check hiking-simulator.tsx
console.log('\n📄 Checking hiking-simulator.tsx:');
if (fs.existsSync(hikingSimulatorPath)) {
  const content = fs.readFileSync(hikingSimulatorPath, 'utf-8');
  
  // Check for isRouteCompleted
  if (content.includes('isRouteCompleted')) {
    console.log('✅ isRouteCompleted state exists');
  } else {
    console.log('❌ isRouteCompleted state NOT found');
  }
  
  // Check for handleSaveCompletion
  if (content.includes('handleSaveCompletion')) {
    console.log('✅ handleSaveCompletion function exists');
    
    // Check if it's called in handleViewSouvenirs
    const viewSouvenirsMatch = content.match(/const handleViewSouvenirs = [\s\S]{0,200}/);
    if (viewSouvenirsMatch && viewSouvenirsMatch[0].includes('handleSaveCompletion()')) {
      console.log('✅ handleSaveCompletion is called in handleViewSouvenirs');
    } else {
      console.log('❌ handleSaveCompletion is NOT called in handleViewSouvenirs');
    }
  } else {
    console.log('❌ handleSaveCompletion function NOT found');
  }
  
  // Check if handleViewSouvenirs is passed to CompletionSummary
  if (content.includes('onViewSouvenirs={handleViewSouvenirs}')) {
    console.log('✅ handleViewSouvenirs is passed to CompletionSummary');
  } else {
    console.log('❌ handleViewSouvenirs is NOT passed to CompletionSummary');
  }
} else {
  console.log('❌ File not found');
}

console.log('\n' + '='.repeat(60));
console.log('\n✅ Verification complete!');
console.log('\n💡 To test in browser:');
console.log('   1. Open test-xp-save.html in browser');
console.log('   2. Complete a route in your app');
console.log('   3. Click "check it out in your Souvenir Gallery"');
console.log('   4. Check if XP is saved in the test page');

