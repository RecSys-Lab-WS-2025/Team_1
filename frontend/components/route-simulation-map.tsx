'use client';

import { Route, Breakpoint } from '@/lib/mock-data';
import { MapPin, CheckCircle2, Sparkles, Target } from 'lucide-react';
import { useMemo } from 'react';
import {
  parseGPX,
  findClosestPointOnTrack,
  projectToSVG,
  generatePathFromPoints,
  type GPXTrack,
} from '@/lib/gpx-parser';

interface RouteSimulationMapProps {
  route: Route;
  currentBreakpointIndex: number;
  completedBreakpoints: string[];
}

/**
 * Predefined layouts for different numbers of breakpoints
 * Each layout provides fixed positions, path, and label positions for optimal visualization
 */
const BREAKPOINT_LAYOUTS: Record<number, { 
  positions: Array<{ x: number; y: number }>; 
  pathD: string;
  labelOffsets: Array<{ x: number; y: number }>; // Label position relative to breakpoint
}> = {
  1: {
    positions: [{ x: 400, y: 175 }],
    pathD: 'M 400 175',
    labelOffsets: [{ x: 0, y: 45 }],
  },
  2: {
    positions: [
      { x: 200, y: 175 },
      { x: 600, y: 175 },
    ],
    pathD: 'M 200 175 Q 400 175, 600 175',
    labelOffsets: [
      { x: 0, y: 45 },  // First: below
      { x: 0, y: 45 },  // Second: below
    ],
  },
  3: {
    positions: [
      { x: 150, y: 200 },
      { x: 400, y: 100 },
      { x: 650, y: 200 },
    ],
    pathD: 'M 150 200 Q 275 150, 400 100 Q 525 150, 650 200',
    labelOffsets: [
      { x: 0, y: 45 },  // First: below
      { x: 0, y: 55 },  // Second (top): below with more space
      { x: 0, y: 45 },  // Third: below
    ],
  },
  4: {
    positions: [
      { x: 100, y: 250 },
      { x: 250, y: 100 },
      { x: 550, y: 100 },
      { x: 700, y: 250 },
    ],
    pathD: 'M 100 250 Q 175 175, 250 100 Q 400 100, 550 100 Q 625 175, 700 250',
    labelOffsets: [
      { x: 0, y: 45 },   // First (bottom left): below with more space
      { x: 0, y: 55 },   // Second (top left): below with even more space
      { x: 0, y: -40 },  // Third (top right): above to avoid overlap
      { x: 0, y: 45 },   // Fourth (bottom right): below
    ],
  },
  5: {
    positions: [
      { x: 80, y: 280 },
      { x: 200, y: 150 },
      { x: 400, y: 80 },
      { x: 600, y: 150 },
      { x: 720, y: 280 },
    ],
    pathD: 'M 80 280 Q 140 215, 200 150 Q 300 115, 400 80 Q 500 115, 600 150 Q 660 215, 720 280',
    labelOffsets: [
      { x: 0, y: 45 },   // Bottom left: below
      { x: 0, y: 50 },   // Left middle: below
      { x: 0, y: 60 },   // Top center: below with more space
      { x: 0, y: -40 },  // Right middle: above
      { x: 0, y: 45 },   // Bottom right: below
    ],
  },
  6: {
    positions: [
      { x: 70, y: 280 },
      { x: 180, y: 180 },
      { x: 320, y: 100 },
      { x: 480, y: 100 },
      { x: 620, y: 180 },
      { x: 730, y: 280 },
    ],
    pathD: 'M 70 280 Q 125 230, 180 180 Q 250 140, 320 100 Q 400 100, 480 100 Q 550 140, 620 180 Q 675 230, 730 280',
    labelOffsets: [
      { x: 0, y: 45 },   // Bottom left: below
      { x: 0, y: 50 },   // Left lower: below
      { x: 0, y: 60 },   // Top left: below
      { x: 0, y: -40 },  // Top right: above to avoid overlap
      { x: 0, y: -40 },  // Right middle: above
      { x: 0, y: 45 },   // Bottom right: below
    ],
  },
  7: {
    positions: [
      { x: 60, y: 300 },
      { x: 150, y: 200 },
      { x: 280, y: 120 },
      { x: 400, y: 90 },
      { x: 520, y: 120 },
      { x: 650, y: 200 },
      { x: 740, y: 300 },
    ],
    pathD: 'M 60 300 Q 105 250, 150 200 Q 215 160, 280 120 Q 340 105, 400 90 Q 460 105, 520 120 Q 585 160, 650 200 Q 695 250, 740 300',
    labelOffsets: [
      { x: 0, y: 45 },   // Bottom left: below
      { x: 0, y: 50 },   // Left lower: below
      { x: 0, y: 55 },   // Left upper: below
      { x: 0, y: 60 },   // Top center: below
      { x: 0, y: -40 },  // Right upper: above
      { x: 0, y: -40 },  // Right lower: above
      { x: 0, y: 45 },   // Bottom right: below
    ],
  },
  8: {
    positions: [
      { x: 50, y: 300 },
      { x: 130, y: 220 },
      { x: 230, y: 150 },
      { x: 350, y: 110 },
      { x: 450, y: 110 },
      { x: 570, y: 150 },
      { x: 670, y: 220 },
      { x: 750, y: 300 },
    ],
    pathD: 'M 50 300 Q 90 260, 130 220 Q 180 185, 230 150 Q 290 130, 350 110 Q 400 110, 450 110 Q 510 130, 570 150 Q 620 185, 670 220 Q 710 260, 750 300',
    labelOffsets: [
      { x: 0, y: 45 },   // Bottom left: below
      { x: 0, y: 50 },   // Left lower: below
      { x: 0, y: 55 },   // Left upper: below
      { x: 0, y: 60 },   // Top left: below
      { x: 0, y: -40 },  // Top right: above
      { x: 0, y: -40 },  // Right upper: above
      { x: 0, y: -40 },  // Right lower: above
      { x: 0, y: 45 },   // Bottom right: below
    ],
  },
  9: {
    positions: [
      { x: 50, y: 310 },
      { x: 120, y: 240 },
      { x: 210, y: 180 },
      { x: 320, y: 130 },
      { x: 400, y: 100 },
      { x: 480, y: 130 },
      { x: 590, y: 180 },
      { x: 680, y: 240 },
      { x: 750, y: 310 },
    ],
    pathD: 'M 50 310 Q 85 275, 120 240 Q 165 210, 210 180 Q 265 155, 320 130 Q 360 115, 400 100 Q 440 115, 480 130 Q 535 155, 590 180 Q 635 210, 680 240 Q 715 275, 750 310',
    labelOffsets: [
      { x: 0, y: 45 },   // Bottom left: below
      { x: 0, y: 50 },   // Left lower: below
      { x: 0, y: 55 },   // Left middle: below
      { x: 0, y: 60 },   // Left upper: below
      { x: 0, y: 60 },   // Top center: below
      { x: 0, y: -40 },  // Right upper: above
      { x: 0, y: -40 },  // Right middle: above
      { x: 0, y: -40 },  // Right lower: above
      { x: 0, y: 45 },   // Bottom right: below
    ],
  },
  10: {
    positions: [
      { x: 40, y: 310 },
      { x: 110, y: 250 },
      { x: 200, y: 200 },
      { x: 300, y: 150 },
      { x: 400, y: 120 },
      { x: 500, y: 120 },
      { x: 600, y: 150 },
      { x: 700, y: 200 },
      { x: 790, y: 250 },
      { x: 760, y: 310 },
    ],
    pathD: 'M 40 310 Q 75 280, 110 250 Q 155 225, 200 200 Q 250 175, 300 150 Q 350 135, 400 120 Q 450 120, 500 120 Q 550 135, 600 150 Q 650 175, 700 200 Q 745 225, 790 250 Q 825 280, 760 310',
    labelOffsets: [
      { x: 0, y: 45 },   // Bottom left: below
      { x: 0, y: 50 },   // Left lower: below
      { x: 0, y: 55 },   // Left middle: below
      { x: 0, y: 60 },   // Left upper: below
      { x: 0, y: 60 },   // Top left: below
      { x: 0, y: -40 },  // Top right: above
      { x: 0, y: -40 },  // Right upper: above
      { x: 0, y: -40 },  // Right middle: above
      { x: 0, y: -40 },  // Right lower: above
      { x: 0, y: 45 },   // Bottom right: below
    ],
  },
};

/**
 * Generate a default layout for any number of breakpoints
 * Used when count exceeds predefined layouts
 */
function generateDefaultLayout(count: number, width: number, height: number, padding: number): { 
  positions: Array<{ x: number; y: number }>; 
  pathD: string;
  labelOffsets: Array<{ x: number; y: number }>;
} {
  const positions: Array<{ x: number; y: number }> = [];
  const usableWidth = width - 2 * padding;
  const usableHeight = height - 2 * padding;
  
  for (let i = 0; i < count; i++) {
    const progress = count > 1 ? i / (count - 1) : 0;
    const x = padding + progress * usableWidth;
    // Create a wavy path with more variation for better spacing
    const y = padding + usableHeight / 2 + Math.sin(progress * Math.PI * 2.5) * (usableHeight * 0.3);
    positions.push({ x, y });
  }
  
  // Create smooth curved path
  let pathD = `M ${positions[0].x} ${positions[0].y}`;
  for (let i = 1; i < positions.length; i++) {
    const prev = positions[i - 1];
    const curr = positions[i];
    const midX = (prev.x + curr.x) / 2;
    pathD += ` Q ${midX} ${prev.y}, ${curr.x} ${curr.y}`;
  }
  
  // Generate label offsets - alternate above/below based on position
  const labelOffsets = positions.map((pos, i) => {
    const isTop = pos.y < height / 2;
    return {
      x: 0,
      y: isTop ? 45 : (i % 2 === 0 ? 35 : -30)
    };
  });
  
  return { positions, pathD, labelOffsets };
}

export function RouteSimulationMap({ 
  route, 
  currentBreakpointIndex,
  completedBreakpoints 
}: RouteSimulationMapProps) {
  // Sort breakpoints by orderIndex if available, otherwise keep original order
  const breakpoints = [...route.breakpoints].sort((a, b) => {
    if (a.orderIndex !== undefined && b.orderIndex !== undefined) {
      return a.orderIndex - b.orderIndex;
    }
    return 0;
  });
  
  const width = 800; // Much wider for better spacing and no overlap
  const height = 350; // Slightly taller for better vertical spacing
  const padding = 60; // More padding for labels
  
  // Parse GPX data if available
  const gpxTrack = useMemo(() => {
    if (route.gpxData) {
      return parseGPX(route.gpxData);
    }
    return null;
  }, [route.gpxData]);

  // Calculate layout: use GPX if available, otherwise use fixed layouts
  const { pathD, positions, labelOffsets } = useMemo(() => {
    if (gpxTrack && gpxTrack.points.length > 0) {
      // Use GPX data for realistic route visualization
      const projectedPoints = projectToSVG(gpxTrack.points, width, height, padding);
      const pathD = generatePathFromPoints(projectedPoints);

      // Find closest points on track for each breakpoint
      const positions: Array<{ x: number; y: number }> = [];
      const offsets: Array<{ x: number; y: number }> = [];

      breakpoints.forEach((breakpoint, index) => {
        if (breakpoint.latitude && breakpoint.longitude) {
          // Find closest point on GPX track
          const closest = findClosestPointOnTrack(
            gpxTrack,
            breakpoint.latitude,
            breakpoint.longitude
          );

          // Project the closest point to SVG coordinates
          const projectedClosest = projectToSVG([closest.point], width, height, padding)[0];
          positions.push(projectedClosest);

          // Calculate label offset based on position
          // Try to place labels above or below to avoid overlap
          const isTopHalf = projectedClosest.y < height / 2;
          const offsetY = isTopHalf ? 35 : -25;
          offsets.push({ x: 0, y: offsetY });
        } else {
          // Fallback: use index-based position along path
          const progress = breakpoints.length > 1 
            ? index / (breakpoints.length - 1) 
            : 0.5;
          const pathIndex = Math.floor(progress * (projectedPoints.length - 1));
          positions.push(projectedPoints[pathIndex] || projectedPoints[0]);
          offsets.push({ x: 0, y: 35 });
        }
      });

      return { pathD, positions, labelOffsets: offsets };
    } else {
      // Fallback to fixed layouts
      const count = breakpoints.length;
      if (BREAKPOINT_LAYOUTS[count]) {
        return BREAKPOINT_LAYOUTS[count];
      } else {
        return generateDefaultLayout(count, width, height, padding);
      }
    }
  }, [gpxTrack, breakpoints, width, height, padding]);
  
  return (
    <div className="relative w-full bg-gradient-to-br from-primary/5 to-secondary/5 rounded-lg border-4 border-border p-4">
      <div className="mb-4">
        <h3 className="text-lg font-bold text-foreground flex items-center gap-2">
          <MapPin className="w-5 h-5 text-primary" />
          Route Map
          {gpxTrack && (
            <span className="text-xs text-muted-foreground ml-auto font-normal">
              📍 GPX Track
            </span>
          )}
        </h3>
        <p className="text-xs text-muted-foreground mt-1">
          Follow the path and complete each breakpoint
        </p>
      </div>
      
      <svg
        viewBox={`0 0 ${width} ${height}`}
        className="w-full h-auto"
        style={{ maxHeight: '400px', minHeight: '350px' }}
        preserveAspectRatio="xMidYMid meet"
      >
        {/* Background path */}
        <path
          d={pathD}
          fill="none"
          stroke="currentColor"
          strokeWidth="8"
          strokeLinecap="round"
          className="text-muted/30"
        />
        
        {/* Completed path */}
        {currentBreakpointIndex > 0 && (
          <path
            d={pathD}
            fill="none"
            stroke="currentColor"
            strokeWidth="8"
            strokeLinecap="round"
            strokeDasharray={`${(currentBreakpointIndex / (breakpoints.length - 1)) * 100}% 100%`}
            className="text-primary transition-all duration-500"
          />
        )}
        
        {/* Breakpoint markers */}
        {positions.map((pos, index) => {
          const bp = breakpoints[index];
          const isPast = index < currentBreakpointIndex;
          const isCurrent = index === currentBreakpointIndex;
          const isCompleted = completedBreakpoints.includes(bp.id);
          
          return (
            <g key={bp.id}>
              {/* Marker circle */}
              <circle
                cx={pos.x}
                cy={pos.y}
                r={isCurrent ? 16 : 12}
                fill="currentColor"
                className={
                  isCurrent 
                    ? 'text-accent animate-pulse transition-all duration-300' 
                    : isPast 
                    ? 'text-primary transition-all duration-300' 
                    : 'text-muted transition-all duration-300'
                }
                stroke={isCurrent ? 'currentColor' : 'none'}
                strokeWidth={isCurrent ? 4 : 0}
              />
              
              {/* Icon inside marker */}
              {isPast && (
                <text
                  x={pos.x}
                  y={pos.y}
                  textAnchor="middle"
                  dominantBaseline="central"
                  className="text-xs fill-primary-foreground font-bold"
                >
                  ✓
                </text>
              )}
              
              {isCurrent && (
                <circle
                  cx={pos.x}
                  cy={pos.y}
                  r={8}
                  fill="currentColor"
                  className="text-accent-foreground"
                />
              )}
              
              {/* Quest indicator */}
              {bp.type === 'quest' && !isCompleted && index <= currentBreakpointIndex && (
                <circle
                  cx={pos.x + 12}
                  cy={pos.y - 12}
                  r={6}
                  fill="currentColor"
                  className="text-accent animate-bounce"
                />
              )}
              
              {/* Label - use predefined offset with more spacing to avoid overlap */}
              <text
                x={pos.x + (labelOffsets[index]?.x || 0)}
                y={pos.y + (labelOffsets[index]?.y || 45)}
                textAnchor="middle"
                className={`text-xs font-bold fill-current ${
                  isCurrent ? 'text-primary' : 'text-foreground'
                }`}
                style={{ 
                  pointerEvents: 'none',
                  // Add text shadow for better readability
                  textShadow: '0 1px 2px rgba(0,0,0,0.1)'
                }}
              >
                {bp.name}
              </text>
            </g>
          );
        })}
        
        {/* Character icon at current position - positioned well above breakpoint to avoid label overlap */}
        {currentBreakpointIndex < positions.length && (
          <g className="transition-all duration-500" style={{ pointerEvents: 'none' }}>
            <circle
              cx={positions[currentBreakpointIndex].x}
              cy={positions[currentBreakpointIndex].y - 50}
              r="15"
              fill="currentColor"
              className="text-accent"
            />
            <text
              x={positions[currentBreakpointIndex].x}
              y={positions[currentBreakpointIndex].y - 50}
              textAnchor="middle"
              dominantBaseline="central"
              className="text-lg"
            >
              🎒
            </text>
          </g>
        )}
      </svg>
      
      {/* Legend */}
      <div className="mt-4 flex flex-wrap gap-4 text-xs">
        <div className="flex items-center gap-2">
          <div className="w-3 h-3 rounded-full bg-primary" />
          <span className="text-muted-foreground">Completed</span>
        </div>
        <div className="flex items-center gap-2">
          <div className="w-3 h-3 rounded-full bg-accent animate-pulse" />
          <span className="text-muted-foreground">Current</span>
        </div>
        <div className="flex items-center gap-2">
          <div className="w-3 h-3 rounded-full bg-muted" />
          <span className="text-muted-foreground">Upcoming</span>
        </div>
      </div>
    </div>
  );
}
