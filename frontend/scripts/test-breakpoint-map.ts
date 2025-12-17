/**
 * Test script to verify breakpoint map improvements
 * Run with: npx tsx scripts/test-breakpoint-map.ts
 */

import { mockRoutes } from '../lib/mock-data';
import { transformApiRoute } from '../lib/api-transforms';
import type { ApiRoute, ApiBreakpoint } from '../lib/api-types';

// Test 1: Check if mock data has coordinates
console.log('🧪 Test 1: Checking mock data coordinates...');
const mockRoute = mockRoutes[0];
const hasMockCoords = mockRoute.breakpoints.every(
  (bp) => bp.latitude !== undefined && bp.longitude !== undefined
);
console.log(`✅ Mock route "${mockRoute.name}" has coordinates: ${hasMockCoords}`);
mockRoute.breakpoints.forEach((bp, idx) => {
  console.log(`   Breakpoint ${idx + 1}: ${bp.name} - lat: ${bp.latitude}, lng: ${bp.longitude}, order: ${bp.orderIndex}`);
});

// Test 2: Test API transform with coordinates
console.log('\n🧪 Test 2: Testing API transform with coordinates...');
const apiRouteWithCoords: ApiRoute = {
  id: 1,
  title: "Test Route",
  category_name: "Hiking trail",
  length_meters: 5000,
  duration_min: 120,
  difficulty: 1,
  short_description: "Test route",
  location: "Munich, Germany",
  elevation: 100,
  tags_json: '["forest", "scenic"]',
  xp_required: 0,
  base_xp_reward: 100,
  story_prologue_title: null,
  story_prologue_body: null,
  story_epilogue_body: null,
  breakpoints: [
    {
      id: 1,
      route_id: 1,
      order_index: 0,
      poi_name: "Start",
      poi_type: "trailhead",
      latitude: 48.1374,
      longitude: 11.5755,
      main_quest_snippet: "Start here",
      mini_quests: [],
    },
    {
      id: 2,
      route_id: 1,
      order_index: 1,
      poi_name: "Middle",
      poi_type: "viewpoint",
      latitude: null, // Missing coordinate
      longitude: null,
      main_quest_snippet: "Middle point",
      mini_quests: [],
    },
    {
      id: 3,
      route_id: 1,
      order_index: 2,
      poi_name: "End",
      poi_type: "finish",
      latitude: 48.15,
      longitude: 11.6,
      main_quest_snippet: "End here",
      mini_quests: [],
    },
  ],
  is_locked: false,
};

const transformedRoute = transformApiRoute(apiRouteWithCoords);
console.log(`✅ Transformed route: ${transformedRoute.name}`);
transformedRoute.breakpoints.forEach((bp, idx) => {
  console.log(`   Breakpoint ${idx + 1}: ${bp.name} - lat: ${bp.latitude}, lng: ${bp.longitude}, order: ${bp.orderIndex}`);
  if (bp.latitude === undefined || bp.longitude === undefined) {
    console.log(`   ⚠️  WARNING: Breakpoint missing coordinates!`);
  }
});

// Test 3: Test API transform without coordinates (should generate mock)
console.log('\n🧪 Test 3: Testing API transform without coordinates (fallback)...');
const apiRouteNoCoords: ApiRoute = {
  id: 2,
  title: "Route Without Coords",
  category_name: "Hiking trail",
  length_meters: 3000,
  duration_min: 90,
  difficulty: 0,
  short_description: "Test route",
  location: "Berlin, Germany",
  elevation: 50,
  tags_json: '[]',
  xp_required: 0,
  base_xp_reward: 50,
  story_prologue_title: null,
  story_prologue_body: null,
  story_epilogue_body: null,
  breakpoints: [
    {
      id: 10,
      route_id: 2,
      order_index: 0,
      poi_name: "Start",
      poi_type: "trailhead",
      latitude: null,
      longitude: null,
      main_quest_snippet: "Start",
      mini_quests: [],
    },
    {
      id: 11,
      route_id: 2,
      order_index: 1,
      poi_name: "End",
      poi_type: "finish",
      latitude: null,
      longitude: null,
      main_quest_snippet: "End",
      mini_quests: [],
    },
  ],
  is_locked: false,
};

const transformedRouteNoCoords = transformApiRoute(apiRouteNoCoords);
console.log(`✅ Transformed route: ${transformedRouteNoCoords.name}`);
transformedRouteNoCoords.breakpoints.forEach((bp, idx) => {
  console.log(`   Breakpoint ${idx + 1}: ${bp.name} - lat: ${bp.latitude}, lng: ${bp.longitude}, order: ${bp.orderIndex}`);
  if (bp.latitude !== undefined && bp.longitude !== undefined) {
    console.log(`   ✅ Generated mock coordinates for Berlin area`);
  } else {
    console.log(`   ❌ ERROR: Failed to generate mock coordinates!`);
  }
});

// Test 4: Verify sorting
console.log('\n🧪 Test 4: Verifying breakpoint sorting...');
const unsortedBreakpoints: ApiBreakpoint[] = [
  {
    id: 1,
    route_id: 1,
    order_index: 2,
    poi_name: "Third",
    poi_type: null,
    latitude: null,
    longitude: null,
    main_quest_snippet: null,
    mini_quests: [],
  },
  {
    id: 2,
    route_id: 1,
    order_index: 0,
    poi_name: "First",
    poi_type: null,
    latitude: null,
    longitude: null,
    main_quest_snippet: null,
    mini_quests: [],
  },
  {
    id: 3,
    route_id: 1,
    order_index: 1,
    poi_name: "Second",
    poi_type: null,
    latitude: null,
    longitude: null,
    main_quest_snippet: null,
    mini_quests: [],
  },
];

const testRoute: ApiRoute = {
  id: 3,
  title: "Sorting Test",
  category_name: "Hiking trail",
  length_meters: 1000,
  duration_min: 30,
  difficulty: 0,
  short_description: "Test",
  location: "Test Location",
  elevation: 0,
  tags_json: null,
  xp_required: 0,
  base_xp_reward: 10,
  story_prologue_title: null,
  story_prologue_body: null,
  story_epilogue_body: null,
  breakpoints: unsortedBreakpoints,
  is_locked: false,
};

const sortedRoute = transformApiRoute(testRoute);
const orderIsCorrect = sortedRoute.breakpoints.every(
  (bp, idx) => bp.orderIndex === idx
);
console.log(`✅ Breakpoints sorted correctly: ${orderIsCorrect}`);
sortedRoute.breakpoints.forEach((bp, idx) => {
  console.log(`   ${idx + 1}. ${bp.name} (orderIndex: ${bp.orderIndex})`);
});

console.log('\n✅ All tests completed!');

