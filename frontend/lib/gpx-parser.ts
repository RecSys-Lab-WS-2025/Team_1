/**
 * GPX parsing utilities for route map visualization
 */

export interface GPXPoint {
  lat: number;
  lon: number;
  elevation?: number;
}

export interface GPXTrack {
  points: GPXPoint[];
}

/**
 * Parse GPX XML string and extract track points
 */
export function parseGPX(gpxData: string | null): GPXTrack | null {
  if (!gpxData) {
    return null;
  }

  try {
    const parser = new DOMParser();
    const xmlDoc = parser.parseFromString(gpxData, 'text/xml');
    
    // Check for parsing errors
    const parserError = xmlDoc.querySelector('parsererror');
    if (parserError) {
      console.warn('GPX parsing error:', parserError.textContent);
      return null;
    }

    const points: GPXPoint[] = [];
    
    // Find all trkpt (track point) elements
    const trackPoints = xmlDoc.querySelectorAll('trkpt');
    
    trackPoints.forEach((trkpt) => {
      const lat = parseFloat(trkpt.getAttribute('lat') || '0');
      const lon = parseFloat(trkpt.getAttribute('lon') || '0');
      
      if (!isNaN(lat) && !isNaN(lon)) {
        const ele = trkpt.querySelector('ele');
        const elevation = ele ? parseFloat(ele.textContent || '0') : undefined;
        
        points.push({
          lat,
          lon,
          elevation: elevation && !isNaN(elevation) ? elevation : undefined,
        });
      }
    });

    // If no track points found, try to find waypoints or route points
    if (points.length === 0) {
      const waypoints = xmlDoc.querySelectorAll('wpt');
      waypoints.forEach((wpt) => {
        const lat = parseFloat(wpt.getAttribute('lat') || '0');
        const lon = parseFloat(wpt.getAttribute('lon') || '0');
        
        if (!isNaN(lat) && !isNaN(lon)) {
          points.push({ lat, lon });
        }
      });
    }

    if (points.length === 0) {
      return null;
    }

    return { points };
  } catch (error) {
    console.error('Failed to parse GPX data:', error);
    return null;
  }
}

/**
 * Calculate distance between two GPS points (Haversine formula)
 * Returns distance in kilometers
 */
export function calculateDistance(
  point1: GPXPoint,
  point2: GPXPoint
): number {
  const R = 6371; // Earth's radius in kilometers
  const dLat = ((point2.lat - point1.lat) * Math.PI) / 180;
  const dLon = ((point2.lon - point1.lon) * Math.PI) / 180;
  
  const a =
    Math.sin(dLat / 2) * Math.sin(dLat / 2) +
    Math.cos((point1.lat * Math.PI) / 180) *
      Math.cos((point2.lat * Math.PI) / 180) *
      Math.sin(dLon / 2) *
      Math.sin(dLon / 2);
  
  const c = 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1 - a));
  return R * c;
}

/**
 * Find the closest point on GPX track to a given breakpoint coordinate
 */
export function findClosestPointOnTrack(
  track: GPXTrack,
  targetLat: number,
  targetLon: number
): { point: GPXPoint; index: number; distance: number } {
  let closestPoint = track.points[0];
  let closestIndex = 0;
  let minDistance = calculateDistance(
    { lat: targetLat, lon: targetLon },
    track.points[0]
  );

  track.points.forEach((point, index) => {
    const distance = calculateDistance(
      { lat: targetLat, lon: targetLon },
      point
    );
    
    if (distance < minDistance) {
      minDistance = distance;
      closestPoint = point;
      closestIndex = index;
    }
  });

  return {
    point: closestPoint,
    index: closestIndex,
    distance: minDistance,
  };
}

/**
 * Project GPS coordinates to SVG coordinates
 */
export function projectToSVG(
  points: GPXPoint[],
  width: number,
  height: number,
  padding: number = 40
): Array<{ x: number; y: number }> {
  if (points.length === 0) {
    return [];
  }

  // Calculate bounding box
  const lats = points.map(p => p.lat);
  const lons = points.map(p => p.lon);
  const minLat = Math.min(...lats);
  const maxLat = Math.max(...lats);
  const minLon = Math.min(...lons);
  const maxLon = Math.max(...lons);

  const latRange = maxLat - minLat || 0.01;
  const lonRange = maxLon - minLon || 0.01;

  // Add padding
  const latPadding = latRange * 0.1;
  const lonPadding = lonRange * 0.1;

  const usableWidth = width - 2 * padding;
  const usableHeight = height - 2 * padding;

  // Project points to SVG coordinates
  return points.map((point) => {
    const normalizedLat = (point.lat - minLat + latPadding) / (latRange + 2 * latPadding);
    const normalizedLon = (point.lon - minLon + lonPadding) / (lonRange + 2 * lonPadding);

    // Flip latitude (SVG y increases downward, but lat increases upward)
    const x = padding + normalizedLon * usableWidth;
    const y = padding + (1 - normalizedLat) * usableHeight;

    return { x, y };
  });
}

/**
 * Generate SVG path from projected points
 */
export function generatePathFromPoints(
  projectedPoints: Array<{ x: number; y: number }>
): string {
  if (projectedPoints.length === 0) {
    return '';
  }

  if (projectedPoints.length === 1) {
    return `M ${projectedPoints[0].x} ${projectedPoints[0].y}`;
  }

  // Use quadratic curves for smooth path
  let pathD = `M ${projectedPoints[0].x} ${projectedPoints[0].y}`;
  
  for (let i = 1; i < projectedPoints.length; i++) {
    const prev = projectedPoints[i - 1];
    const curr = projectedPoints[i];
    
    if (i === 1) {
      // First segment: use line
      pathD += ` L ${curr.x} ${curr.y}`;
    } else {
      // Subsequent segments: use quadratic curve
      const midX = (prev.x + curr.x) / 2;
      pathD += ` Q ${midX} ${prev.y}, ${curr.x} ${curr.y}`;
    }
  }

  return pathD;
}

