#!/usr/bin/env node

/**
 * XP Save Fix Verification Script
 * 
 * This script verifies that the XP save fix is correctly implemented
 * by checking the code logic and file contents.
 */

const fs = require('fs');
const path = require('path');

const colors = {
  reset: '\x1b[0m',
  green: '\x1b[32m',
  red: '\x1b[31m',
  yellow: '\x1b[33m',
  blue: '\x1b[34m',
  cyan: '\x1b[36m',
};

function log(message, color = 'reset') {
  console.log(`${colors[color]}${message}${colors.reset}`);
}

function checkFile(filePath, checks) {
  const fullPath = path.join(__dirname, '..', filePath);
  
  if (!fs.existsSync(fullPath)) {
    log(`❌ File not found: ${filePath}`, 'red');
    return false;
  }

  const content = fs.readFileSync(fullPath, 'utf-8');
  let passed = true;

  log(`\n📄 Checking: ${filePath}`, 'cyan');
  
  for (const check of checks) {
    const { name, test, required = true } = check;
    const result = test(content);
    
    if (result) {
      log(`  ✅ ${name}`, 'green');
    } else {
      if (required) {
        log(`  ❌ ${name} (REQUIRED)`, 'red');
        passed = false;
      } else {
        log(`  ⚠️  ${name} (OPTIONAL)`, 'yellow');
      }
    }
  }

  return passed;
}

function main() {
  log('🧪 XP Save Fix Verification Script\n', 'blue');
  log('='.repeat(60), 'blue');

  let allPassed = true;

  // Check completion-summary.tsx
  const summaryChecks = [
    {
      name: 'Gallery link onClick handler exists',
      test: (content) => /check it out in your Souvenir Gallery/.test(content),
    },
    {
      name: 'onClose is called in onClick handler',
      test: (content) => {
        const gallerySection = content.match(/check it out in your Souvenir Gallery[\s\S]{0,500}/);
        if (!gallerySection) return false;
        return /onClose\(\)/.test(gallerySection[0]);
      },
    },
    {
      name: 'onClose is called before onViewSouvenirs',
      test: (content) => {
        const gallerySection = content.match(/check it out in your Souvenir Gallery[\s\S]{0,500}/);
        if (!gallerySection) return false;
        const section = gallerySection[0];
        const onCloseIndex = section.indexOf('onClose()');
        const onViewSouvenirsIndex = section.indexOf('onViewSouvenirs()');
        return onCloseIndex !== -1 && onViewSouvenirsIndex !== -1 && onCloseIndex < onViewSouvenirsIndex;
      },
    },
    {
      name: 'setTimeout is used for onViewSouvenirs call',
      test: (content) => {
        const gallerySection = content.match(/check it out in your Souvenir Gallery[\s\S]{0,500}/);
        if (!gallerySection) return false;
        return /setTimeout.*onViewSouvenirs/.test(gallerySection[0]);
      },
    },
    {
      name: 'Console log for debugging exists',
      test: (content) => /console\.log.*Souvenir link clicked/.test(content),
    },
  ];

  if (!checkFile('components/completion-summary.tsx', summaryChecks)) {
    allPassed = false;
  }

  // Check hiking-simulator.tsx
  const simulatorChecks = [
    {
      name: 'isRouteCompleted state exists',
      test: (content) => /const \[isRouteCompleted/.test(content),
    },
    {
      name: 'handleSaveCompletion function exists',
      test: (content) => /const handleSaveCompletion/.test(content),
    },
    {
      name: 'handleSaveCompletion checks isRouteCompleted',
      test: (content) => /if \(!isRouteCompleted\)/.test(content),
    },
    {
      name: 'handleViewSouvenirs calls handleSaveCompletion',
      test: (content) => {
        const viewSouvenirsMatch = content.match(/const handleViewSouvenirs[^}]+}/s);
        if (!viewSouvenirsMatch) return false;
        return /handleSaveCompletion\(\)/.test(viewSouvenirsMatch[0]);
      },
    },
    {
      name: 'handleViewSouvenirs is passed to CompletionSummary',
      test: (content) => /onViewSouvenirs=\{handleViewSouvenirs\}/.test(content),
    },
  ];

  if (!checkFile('components/hiking-simulator.tsx', simulatorChecks)) {
    allPassed = false;
  }

  // Summary
  log('\n' + '='.repeat(60), 'blue');
  if (allPassed) {
    log('\n✅ All checks passed! The fix appears to be correctly implemented.', 'green');
    log('\n📝 Next steps:', 'cyan');
    log('  1. Test in browser by completing a route', 'cyan');
    log('  2. Click "check it out in your Souvenir Gallery" link', 'cyan');
    log('  3. Verify XP is saved by checking localStorage', 'cyan');
    log('  4. Use test-xp-save.html for visual monitoring', 'cyan');
  } else {
    log('\n❌ Some checks failed. Please review the code.', 'red');
    log('\n💡 The fix may not be complete. Check the failed items above.', 'yellow');
  }

  // Show code flow
  log('\n📋 Expected Code Flow:', 'blue');
  log('='.repeat(60), 'blue');
  log(`
1. User clicks "check it out in your Souvenir Gallery" link
   ↓
2. completion-summary.tsx onClick handler:
   - Calls onClose() → saves XP
   - Calls onViewSouvenirs() after 100ms delay → opens gallery
   ↓
3. hiking-simulator.tsx handleCompletionClose (onClose):
   - Calls handleSaveCompletion()
   ↓
4. hiking-simulator.tsx handleSaveCompletion:
   - Checks if !isRouteCompleted
   - Sets isRouteCompleted = true
   - Calls onComplete(route, totalXpGained, completedQuests)
   ↓
5. route-recommendations.tsx handleCompleteRoute (onComplete):
   - Creates souvenir
   - Updates XP in profile
   - Saves to localStorage/backend
  `, 'cyan');

  return allPassed ? 0 : 1;
}

if (require.main === module) {
  process.exit(main());
}

module.exports = { main };

