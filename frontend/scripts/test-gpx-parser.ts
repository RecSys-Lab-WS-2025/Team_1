/**
 * Test script for GPX parser functionality
 * Run with: npx tsx scripts/test-gpx-parser.ts
 */

import {
  parseGPX,
  findClosestPointOnTrack,
  projectToSVG,
  generatePathFromPoints,
  calculateDistance,
  type GPXPoint,
} from '../lib/gpx-parser';

// Sample GPX data (simplified)
const sampleGPX = `<?xml version="1.0" encoding="UTF-8"?>
<gpx version="1.1" creator="Test">
  <trk>
    <name>Test Route</name>
    <trkseg>
      <trkpt lat="48.1351" lon="11.5820">
        <ele>520</ele>
      </trkpt>
      <trkpt lat="48.1360" lon="11.5830">
        <ele>525</ele>
      </trkpt>
      <trkpt lat="48.1370" lon="11.5840">
        <ele>530</ele>
      </trkpt>
      <trkpt lat="48.1380" lon="11.5850">
        <ele>535</ele>
      </trkpt>
      <trkpt lat="48.1390" lon="11.5860">
        <ele>540</ele>
      </trkpt>
    </trkseg>
  </trk>
</gpx>`;

console.log('🧪 Testing GPX Parser\n');

// Test 1: Parse GPX
console.log('1. Testing GPX parsing...');
const track = parseGPX(sampleGPX);
if (track && track.points.length > 0) {
  console.log(`   ✅ Successfully parsed ${track.points.length} points`);
  console.log(`   First point: lat=${track.points[0].lat}, lon=${track.points[0].lon}`);
  console.log(`   Last point: lat=${track.points[track.points.length - 1].lat}, lon=${track.points[track.points.length - 1].lon}`);
} else {
  console.log('   ❌ Failed to parse GPX');
  process.exit(1);
}

// Test 2: Calculate distance
console.log('\n2. Testing distance calculation...');
const point1: GPXPoint = { lat: 48.1351, lon: 11.5820 };
const point2: GPXPoint = { lat: 48.1360, lon: 11.5830 };
const distance = calculateDistance(point1, point2);
console.log(`   ✅ Distance between two points: ${distance.toFixed(4)} km`);
if (distance > 0 && distance < 1) {
  console.log('   ✅ Distance is reasonable (should be < 1km for close points)');
} else {
  console.log('   ⚠️  Distance seems unusual');
}

// Test 3: Find closest point
console.log('\n3. Testing closest point finding...');
const targetLat = 48.1375;
const targetLon = 11.5845;
const closest = findClosestPointOnTrack(track!, targetLat, targetLon);
console.log(`   ✅ Found closest point at index ${closest.index}`);
console.log(`   Closest point: lat=${closest.point.lat}, lon=${closest.point.lon}`);
console.log(`   Distance: ${closest.distance.toFixed(4)} km`);
if (closest.index >= 0 && closest.index < track!.points.length) {
  console.log('   ✅ Index is valid');
} else {
  console.log('   ❌ Invalid index');
}

// Test 4: Project to SVG
console.log('\n4. Testing SVG projection...');
const width = 800;
const height = 350;
const padding = 60;
const projected = projectToSVG(track!.points, width, height, padding);
console.log(`   ✅ Projected ${projected.length} points to SVG coordinates`);
console.log(`   First projected: x=${projected[0].x.toFixed(2)}, y=${projected[0].y.toFixed(2)}`);
console.log(`   Last projected: x=${projected[projected.length - 1].x.toFixed(2)}, y=${projected[projected.length - 1].y.toFixed(2)}`);

// Check if all points are within bounds
const allInBounds = projected.every(p => 
  p.x >= 0 && p.x <= width && p.y >= 0 && p.y <= height
);
if (allInBounds) {
  console.log('   ✅ All points are within SVG bounds');
} else {
  console.log('   ⚠️  Some points are outside bounds');
}

// Test 5: Generate path
console.log('\n5. Testing path generation...');
const pathD = generatePathFromPoints(projected);
console.log(`   ✅ Generated path with ${pathD.length} characters`);
console.log(`   Path preview: ${pathD.substring(0, 100)}...`);
if (pathD.startsWith('M ')) {
  console.log('   ✅ Path starts with move command');
} else {
  console.log('   ❌ Path format incorrect');
}

// Test 6: Empty/null GPX handling
console.log('\n6. Testing edge cases...');
const emptyTrack = parseGPX('');
if (emptyTrack === null) {
  console.log('   ✅ Empty GPX returns null');
} else {
  console.log('   ⚠️  Empty GPX should return null');
}

const nullTrack = parseGPX(null as any);
if (nullTrack === null) {
  console.log('   ✅ Null GPX returns null');
} else {
  console.log('   ⚠️  Null GPX should return null');
}

console.log('\n✅ All tests completed!');

