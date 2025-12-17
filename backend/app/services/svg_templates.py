"""
Pre-designed SVG templates for souvenir generation.
These templates are Harry Potter / magical themed pixel art designs.
"""

import random
from datetime import datetime
from typing import Dict

# 10 different magical SVG templates with placeholders
SVG_TEMPLATES = [
    # Template 1: Wand with Stars
    """<svg viewBox="0 0 400 300" xmlns="http://www.w3.org/2000/svg" style="font-family: monospace; image-rendering: pixelated;">
  <defs>
    <linearGradient id="bgGrad1" x1="0%" y1="0%" x2="0%" y2="100%">
      <stop offset="0%" style="stop-color:#1a0d2e;stop-opacity:1" />
      <stop offset="100%" style="stop-color:#0f051a;stop-opacity:1" />
    </linearGradient>
    <linearGradient id="cardGrad1" x1="0%" y1="0%" x2="0%" y2="100%">
      <stop offset="0%" style="stop-color:#2d1a44;stop-opacity:1" />
      <stop offset="100%" style="stop-color:#1f0f2e;stop-opacity:1" />
    </linearGradient>
    <filter id="shadow1">
      <feDropShadow dx="2" dy="2" stdDeviation="1" flood-opacity="0.3"/>
    </filter>
  </defs>
  <rect width="400" height="300" fill="url(#bgGrad1)"/>
  <rect x="8" y="8" width="384" height="284" fill="none" stroke="#6A0DAD" stroke-width="6"/>
  <rect x="12" y="12" width="376" height="276" fill="none" stroke="#FFD700" stroke-width="4"/>
  <rect x="20" y="20" width="360" height="260" fill="url(#cardGrad1)" stroke="#6A0DAD" stroke-width="2"/>
  <text x="20" y="35" text-anchor="start" fill="#FFD700" font-size="14">★</text>
  <text x="368" y="35" text-anchor="start" fill="#FFD700" font-size="14">★</text>
  <text x="20" y="283" text-anchor="start" fill="#FFD700" font-size="14">★</text>
  <text x="368" y="283" text-anchor="start" fill="#FFD700" font-size="14">★</text>
  <rect x="195" y="50" width="10" height="50" fill="#FFD700" stroke="#DAA520" stroke-width="1"/>
  <text x="200" y="45" text-anchor="middle" fill="#FFD700" font-size="20">★</text>
  <text x="200" y="155" text-anchor="middle" fill="#FFD700" font-size="20" font-weight="bold">{route_title}</text>
  <text x="200" y="175" text-anchor="middle" fill="#6A0DAD" font-size="11">{location}</text>
  <g filter="url(#shadow1)">
    <rect x="40" y="195" width="90" height="60" fill="#1a0d2e" stroke="#FFD700" stroke-width="3"/>
    <text x="85" y="218" text-anchor="middle" fill="#FFD700" font-size="18" font-weight="bold">{xp}</text>
    <text x="85" y="240" text-anchor="middle" fill="#800020" font-size="10">XP</text>
  </g>
  <g filter="url(#shadow1)">
    <rect x="155" y="195" width="90" height="60" fill="#1a0d2e" stroke="#FFD700" stroke-width="3"/>
    <text x="200" y="218" text-anchor="middle" fill="#FFD700" font-size="18" font-weight="bold">{distance}</text>
    <text x="200" y="240" text-anchor="middle" fill="#800020" font-size="10">KM</text>
  </g>
  <g filter="url(#shadow1)">
    <rect x="270" y="195" width="90" height="60" fill="#2d1a44" stroke="#6A0DAD" stroke-width="3"/>
    <text x="315" y="218" text-anchor="middle" fill="#4B0082" font-size="14" font-weight="bold">{difficulty}</text>
    <text x="315" y="240" text-anchor="middle" fill="#800020" font-size="10">LEVEL</text>
  </g>
  <text x="200" y="275" text-anchor="middle" fill="#6A0DAD" font-size="10">{date} at {time}</text>
</svg>""",

    # Template 2: Stars Cluster
    """<svg viewBox="0 0 400 300" xmlns="http://www.w3.org/2000/svg" style="font-family: monospace; image-rendering: pixelated;">
  <defs>
    <linearGradient id="bgGrad2" x1="0%" y1="0%" x2="0%" y2="100%">
      <stop offset="0%" style="stop-color:#1a1a2e;stop-opacity:1" />
      <stop offset="100%" style="stop-color:#0f0f1a;stop-opacity:1" />
    </linearGradient>
    <linearGradient id="cardGrad2" x1="0%" y1="0%" x2="0%" y2="100%">
      <stop offset="0%" style="stop-color:#2d2d44;stop-opacity:1" />
      <stop offset="100%" style="stop-color:#1f1f2e;stop-opacity:1" />
    </linearGradient>
    <filter id="shadow2">
      <feDropShadow dx="2" dy="2" stdDeviation="1" flood-opacity="0.3"/>
    </filter>
  </defs>
  <rect width="400" height="300" fill="url(#bgGrad2)"/>
  <rect x="8" y="8" width="384" height="284" fill="none" stroke="#FFD700" stroke-width="6"/>
  <rect x="12" y="12" width="376" height="276" fill="none" stroke="#6A0DAD" stroke-width="4"/>
  <rect x="20" y="20" width="360" height="260" fill="url(#cardGrad2)" stroke="#FFD700" stroke-width="2"/>
  <text x="20" y="35" text-anchor="start" fill="#FFD700" font-size="16">★</text>
  <text x="368" y="35" text-anchor="start" fill="#FFD700" font-size="16">★</text>
  <text x="20" y="283" text-anchor="start" fill="#FFD700" font-size="16">★</text>
  <text x="368" y="283" text-anchor="start" fill="#FFD700" font-size="16">★</text>
  <text x="150" y="70" text-anchor="middle" fill="#FFD700" font-size="18">★</text>
  <text x="200" y="60" text-anchor="middle" fill="#FFD700" font-size="20">★</text>
  <text x="250" y="70" text-anchor="middle" fill="#FFD700" font-size="18">★</text>
  <text x="180" y="90" text-anchor="middle" fill="#FFD700" font-size="16">★</text>
  <text x="220" y="90" text-anchor="middle" fill="#FFD700" font-size="16">★</text>
  <text x="200" y="155" text-anchor="middle" fill="#FFD700" font-size="20" font-weight="bold">{route_title}</text>
  <text x="200" y="175" text-anchor="middle" fill="#6A0DAD" font-size="11">{location}</text>
  <g filter="url(#shadow2)">
    <rect x="40" y="195" width="90" height="60" fill="#1a0d2e" stroke="#FFD700" stroke-width="3"/>
    <text x="85" y="218" text-anchor="middle" fill="#FFD700" font-size="18" font-weight="bold">{xp}</text>
    <text x="85" y="240" text-anchor="middle" fill="#800020" font-size="10">XP</text>
  </g>
  <g filter="url(#shadow2)">
    <rect x="155" y="195" width="90" height="60" fill="#1a0d2e" stroke="#FFD700" stroke-width="3"/>
    <text x="200" y="218" text-anchor="middle" fill="#FFD700" font-size="18" font-weight="bold">{distance}</text>
    <text x="200" y="240" text-anchor="middle" fill="#800020" font-size="10">KM</text>
  </g>
  <g filter="url(#shadow2)">
    <rect x="270" y="195" width="90" height="60" fill="#2d1a44" stroke="#6A0DAD" stroke-width="3"/>
    <text x="315" y="218" text-anchor="middle" fill="#4B0082" font-size="14" font-weight="bold">{difficulty}</text>
    <text x="315" y="240" text-anchor="middle" fill="#800020" font-size="10">LEVEL</text>
  </g>
  <text x="200" y="275" text-anchor="middle" fill="#6A0DAD" font-size="10">{date} at {time}</text>
</svg>""",

    # Template 3: Crescent Moon with Stars
    """<svg viewBox="0 0 400 300" xmlns="http://www.w3.org/2000/svg" style="font-family: monospace; image-rendering: pixelated;">
  <defs>
    <linearGradient id="bgGrad3" x1="0%" y1="0%" x2="0%" y2="100%">
      <stop offset="0%" style="stop-color:#1a0d2e;stop-opacity:1" />
      <stop offset="100%" style="stop-color:#0f051a;stop-opacity:1" />
    </linearGradient>
    <linearGradient id="cardGrad3" x1="0%" y1="0%" x2="0%" y2="100%">
      <stop offset="0%" style="stop-color:#2d1a44;stop-opacity:1" />
      <stop offset="100%" style="stop-color:#1f0f2e;stop-opacity:1" />
    </linearGradient>
    <filter id="shadow3">
      <feDropShadow dx="2" dy="2" stdDeviation="1" flood-opacity="0.3"/>
    </filter>
  </defs>
  <rect width="400" height="300" fill="url(#bgGrad3)"/>
  <rect x="8" y="8" width="384" height="284" fill="none" stroke="#4B0082" stroke-width="6"/>
  <rect x="12" y="12" width="376" height="276" fill="none" stroke="#FFD700" stroke-width="4"/>
  <rect x="20" y="20" width="360" height="260" fill="url(#cardGrad3)" stroke="#4B0082" stroke-width="2"/>
  <text x="20" y="35" text-anchor="start" fill="#FFD700" font-size="14">★</text>
  <text x="368" y="35" text-anchor="start" fill="#FFD700" font-size="14">★</text>
  <text x="20" y="283" text-anchor="start" fill="#FFD700" font-size="14">★</text>
  <text x="368" y="283" text-anchor="start" fill="#FFD700" font-size="14">★</text>
  <path d="M 200,50 A 30,30 0 0,1 170,80 A 30,30 0 1,0 200,50 Z" fill="#FFD700" stroke="#DAA520" stroke-width="1"/>
  <text x="150" y="75" text-anchor="middle" fill="#FFD700" font-size="14">★</text>
  <text x="250" y="75" text-anchor="middle" fill="#FFD700" font-size="14">★</text>
  <text x="200" y="155" text-anchor="middle" fill="#FFD700" font-size="20" font-weight="bold">{route_title}</text>
  <text x="200" y="175" text-anchor="middle" fill="#6A0DAD" font-size="11">{location}</text>
  <g filter="url(#shadow3)">
    <rect x="40" y="195" width="90" height="60" fill="#1a0d2e" stroke="#FFD700" stroke-width="3"/>
    <text x="85" y="218" text-anchor="middle" fill="#FFD700" font-size="18" font-weight="bold">{xp}</text>
    <text x="85" y="240" text-anchor="middle" fill="#800020" font-size="10">XP</text>
  </g>
  <g filter="url(#shadow3)">
    <rect x="155" y="195" width="90" height="60" fill="#1a0d2e" stroke="#FFD700" stroke-width="3"/>
    <text x="200" y="218" text-anchor="middle" fill="#FFD700" font-size="18" font-weight="bold">{distance}</text>
    <text x="200" y="240" text-anchor="middle" fill="#800020" font-size="10">KM</text>
  </g>
  <g filter="url(#shadow3)">
    <rect x="270" y="195" width="90" height="60" fill="#2d1a44" stroke="#6A0DAD" stroke-width="3"/>
    <text x="315" y="218" text-anchor="middle" fill="#4B0082" font-size="14" font-weight="bold">{difficulty}</text>
    <text x="315" y="240" text-anchor="middle" fill="#800020" font-size="10">LEVEL</text>
  </g>
  <text x="200" y="275" text-anchor="middle" fill="#6A0DAD" font-size="10">{date} at {time}</text>
</svg>""",

    # Template 4: Owl Silhouette
    """<svg viewBox="0 0 400 300" xmlns="http://www.w3.org/2000/svg" style="font-family: monospace; image-rendering: pixelated;">
  <defs>
    <linearGradient id="bgGrad4" x1="0%" y1="0%" x2="0%" y2="100%">
      <stop offset="0%" style="stop-color:#1a1a2e;stop-opacity:1" />
      <stop offset="100%" style="stop-color:#0f0f1a;stop-opacity:1" />
    </linearGradient>
    <linearGradient id="cardGrad4" x1="0%" y1="0%" x2="0%" y2="100%">
      <stop offset="0%" style="stop-color:#2d2d44;stop-opacity:1" />
      <stop offset="100%" style="stop-color:#1f1f2e;stop-opacity:1" />
    </linearGradient>
    <filter id="shadow4">
      <feDropShadow dx="2" dy="2" stdDeviation="1" flood-opacity="0.3"/>
    </filter>
  </defs>
  <rect width="400" height="300" fill="url(#bgGrad4)"/>
  <rect x="8" y="8" width="384" height="284" fill="none" stroke="#6A0DAD" stroke-width="6"/>
  <rect x="12" y="12" width="376" height="276" fill="none" stroke="#FFD700" stroke-width="4"/>
  <rect x="20" y="20" width="360" height="260" fill="url(#cardGrad4)" stroke="#6A0DAD" stroke-width="2"/>
  <text x="20" y="35" text-anchor="start" fill="#FFD700" font-size="14">★</text>
  <text x="368" y="35" text-anchor="start" fill="#FFD700" font-size="14">★</text>
  <text x="20" y="283" text-anchor="start" fill="#FFD700" font-size="14">★</text>
  <text x="368" y="283" text-anchor="start" fill="#FFD700" font-size="14">★</text>
  <circle cx="200" cy="70" r="25" fill="#4B0082" stroke="#6A0DAD" stroke-width="2"/>
  <circle cx="190" cy="65" r="5" fill="#FFD700"/>
  <circle cx="210" cy="65" r="5" fill="#FFD700"/>
  <polygon points="200,75 195,85 205,85" fill="#FFD700"/>
  <polygon points="200,50 180,60 200,70 220,60" fill="#4B0082"/>
  <text x="200" y="155" text-anchor="middle" fill="#FFD700" font-size="20" font-weight="bold">{route_title}</text>
  <text x="200" y="175" text-anchor="middle" fill="#6A0DAD" font-size="11">{location}</text>
  <g filter="url(#shadow4)">
    <rect x="40" y="195" width="90" height="60" fill="#1a0d2e" stroke="#FFD700" stroke-width="3"/>
    <text x="85" y="218" text-anchor="middle" fill="#FFD700" font-size="18" font-weight="bold">{xp}</text>
    <text x="85" y="240" text-anchor="middle" fill="#800020" font-size="10">XP</text>
  </g>
  <g filter="url(#shadow4)">
    <rect x="155" y="195" width="90" height="60" fill="#1a0d2e" stroke="#FFD700" stroke-width="3"/>
    <text x="200" y="218" text-anchor="middle" fill="#FFD700" font-size="18" font-weight="bold">{distance}</text>
    <text x="200" y="240" text-anchor="middle" fill="#800020" font-size="10">KM</text>
  </g>
  <g filter="url(#shadow4)">
    <rect x="270" y="195" width="90" height="60" fill="#2d1a44" stroke="#6A0DAD" stroke-width="3"/>
    <text x="315" y="218" text-anchor="middle" fill="#4B0082" font-size="14" font-weight="bold">{difficulty}</text>
    <text x="315" y="240" text-anchor="middle" fill="#800020" font-size="10">LEVEL</text>
  </g>
  <text x="200" y="275" text-anchor="middle" fill="#6A0DAD" font-size="10">{date} at {time}</text>
</svg>""",

    # Template 5: Magical Book
    """<svg viewBox="0 0 400 300" xmlns="http://www.w3.org/2000/svg" style="font-family: monospace; image-rendering: pixelated;">
  <defs>
    <linearGradient id="bgGrad5" x1="0%" y1="0%" x2="0%" y2="100%">
      <stop offset="0%" style="stop-color:#1a0d2e;stop-opacity:1" />
      <stop offset="100%" style="stop-color:#0f051a;stop-opacity:1" />
    </linearGradient>
    <linearGradient id="cardGrad5" x1="0%" y1="0%" x2="0%" y2="100%">
      <stop offset="0%" style="stop-color:#2d1a44;stop-opacity:1" />
      <stop offset="100%" style="stop-color:#1f0f2e;stop-opacity:1" />
    </linearGradient>
    <filter id="shadow5">
      <feDropShadow dx="2" dy="2" stdDeviation="1" flood-opacity="0.3"/>
    </filter>
  </defs>
  <rect width="400" height="300" fill="url(#bgGrad5)"/>
  <rect x="8" y="8" width="384" height="284" fill="none" stroke="#FFD700" stroke-width="6"/>
  <rect x="12" y="12" width="376" height="276" fill="none" stroke="#4B0082" stroke-width="4"/>
  <rect x="20" y="20" width="360" height="260" fill="url(#cardGrad5)" stroke="#FFD700" stroke-width="2"/>
  <text x="20" y="35" text-anchor="start" fill="#FFD700" font-size="14">★</text>
  <text x="368" y="35" text-anchor="start" fill="#FFD700" font-size="14">★</text>
  <text x="20" y="283" text-anchor="start" fill="#FFD700" font-size="14">★</text>
  <text x="368" y="283" text-anchor="start" fill="#FFD700" font-size="14">★</text>
  <rect x="170" y="50" width="60" height="70" fill="#800020" stroke="#FFD700" stroke-width="2"/>
  <line x1="200" y1="50" x2="200" y2="120" stroke="#FFD700" stroke-width="2"/>
  <text x="200" y="80" text-anchor="middle" fill="#FFD700" font-size="16">★</text>
  <text x="200" y="155" text-anchor="middle" fill="#FFD700" font-size="20" font-weight="bold">{route_title}</text>
  <text x="200" y="175" text-anchor="middle" fill="#6A0DAD" font-size="11">{location}</text>
  <g filter="url(#shadow5)">
    <rect x="40" y="195" width="90" height="60" fill="#1a0d2e" stroke="#FFD700" stroke-width="3"/>
    <text x="85" y="218" text-anchor="middle" fill="#FFD700" font-size="18" font-weight="bold">{xp}</text>
    <text x="85" y="240" text-anchor="middle" fill="#800020" font-size="10">XP</text>
  </g>
  <g filter="url(#shadow5)">
    <rect x="155" y="195" width="90" height="60" fill="#1a0d2e" stroke="#FFD700" stroke-width="3"/>
    <text x="200" y="218" text-anchor="middle" fill="#FFD700" font-size="18" font-weight="bold">{distance}</text>
    <text x="200" y="240" text-anchor="middle" fill="#800020" font-size="10">KM</text>
  </g>
  <g filter="url(#shadow5)">
    <rect x="270" y="195" width="90" height="60" fill="#2d1a44" stroke="#6A0DAD" stroke-width="3"/>
    <text x="315" y="218" text-anchor="middle" fill="#4B0082" font-size="14" font-weight="bold">{difficulty}</text>
    <text x="315" y="240" text-anchor="middle" fill="#800020" font-size="10">LEVEL</text>
  </g>
  <text x="200" y="275" text-anchor="middle" fill="#6A0DAD" font-size="10">{date} at {time}</text>
</svg>""",

    # Template 6: Golden Snitch Style
    """<svg viewBox="0 0 400 300" xmlns="http://www.w3.org/2000/svg" style="font-family: monospace; image-rendering: pixelated;">
  <defs>
    <linearGradient id="bgGrad6" x1="0%" y1="0%" x2="0%" y2="100%">
      <stop offset="0%" style="stop-color:#1a1a2e;stop-opacity:1" />
      <stop offset="100%" style="stop-color:#0f0f1a;stop-opacity:1" />
    </linearGradient>
    <linearGradient id="cardGrad6" x1="0%" y1="0%" x2="0%" y2="100%">
      <stop offset="0%" style="stop-color:#2d2d44;stop-opacity:1" />
      <stop offset="100%" style="stop-color:#1f1f2e;stop-opacity:1" />
    </linearGradient>
    <filter id="shadow6">
      <feDropShadow dx="2" dy="2" stdDeviation="1" flood-opacity="0.3"/>
    </filter>
  </defs>
  <rect width="400" height="300" fill="url(#bgGrad6)"/>
  <rect x="8" y="8" width="384" height="284" fill="none" stroke="#FFD700" stroke-width="6"/>
  <rect x="12" y="12" width="376" height="276" fill="none" stroke="#6A0DAD" stroke-width="4"/>
  <rect x="20" y="20" width="360" height="260" fill="url(#cardGrad6)" stroke="#FFD700" stroke-width="2"/>
  <text x="20" y="35" text-anchor="start" fill="#FFD700" font-size="14">★</text>
  <text x="368" y="35" text-anchor="start" fill="#FFD700" font-size="14">★</text>
  <text x="20" y="283" text-anchor="start" fill="#FFD700" font-size="14">★</text>
  <text x="368" y="283" text-anchor="start" fill="#FFD700" font-size="14">★</text>
  <circle cx="200" cy="70" r="20" fill="#FFD700" stroke="#DAA520" stroke-width="2"/>
  <rect x="195" y="50" width="10" height="40" fill="#FFD700"/>
  <rect x="190" y="90" width="20" height="5" fill="#FFD700"/>
  <text x="200" y="155" text-anchor="middle" fill="#FFD700" font-size="20" font-weight="bold">{route_title}</text>
  <text x="200" y="175" text-anchor="middle" fill="#6A0DAD" font-size="11">{location}</text>
  <g filter="url(#shadow6)">
    <rect x="40" y="195" width="90" height="60" fill="#1a0d2e" stroke="#FFD700" stroke-width="3"/>
    <text x="85" y="218" text-anchor="middle" fill="#FFD700" font-size="18" font-weight="bold">{xp}</text>
    <text x="85" y="240" text-anchor="middle" fill="#800020" font-size="10">XP</text>
  </g>
  <g filter="url(#shadow6)">
    <rect x="155" y="195" width="90" height="60" fill="#1a0d2e" stroke="#FFD700" stroke-width="3"/>
    <text x="200" y="218" text-anchor="middle" fill="#FFD700" font-size="18" font-weight="bold">{distance}</text>
    <text x="200" y="240" text-anchor="middle" fill="#800020" font-size="10">KM</text>
  </g>
  <g filter="url(#shadow6)">
    <rect x="270" y="195" width="90" height="60" fill="#2d1a44" stroke="#6A0DAD" stroke-width="3"/>
    <text x="315" y="218" text-anchor="middle" fill="#4B0082" font-size="14" font-weight="bold">{difficulty}</text>
    <text x="315" y="240" text-anchor="middle" fill="#800020" font-size="10">LEVEL</text>
  </g>
  <text x="200" y="275" text-anchor="middle" fill="#6A0DAD" font-size="10">{date} at {time}</text>
</svg>""",

    # Template 7: House Badge Style
    """<svg viewBox="0 0 400 300" xmlns="http://www.w3.org/2000/svg" style="font-family: monospace; image-rendering: pixelated;">
  <defs>
    <linearGradient id="bgGrad7" x1="0%" y1="0%" x2="0%" y2="100%">
      <stop offset="0%" style="stop-color:#1a0d2e;stop-opacity:1" />
      <stop offset="100%" style="stop-color:#0f051a;stop-opacity:1" />
    </linearGradient>
    <linearGradient id="cardGrad7" x1="0%" y1="0%" x2="0%" y2="100%">
      <stop offset="0%" style="stop-color:#2d1a44;stop-opacity:1" />
      <stop offset="100%" style="stop-color:#1f0f2e;stop-opacity:1" />
    </linearGradient>
    <filter id="shadow7">
      <feDropShadow dx="2" dy="2" stdDeviation="1" flood-opacity="0.3"/>
    </filter>
  </defs>
  <rect width="400" height="300" fill="url(#bgGrad7)"/>
  <rect x="8" y="8" width="384" height="284" fill="none" stroke="#4B0082" stroke-width="6"/>
  <rect x="12" y="12" width="376" height="276" fill="none" stroke="#FFD700" stroke-width="4"/>
  <rect x="20" y="20" width="360" height="260" fill="url(#cardGrad7)" stroke="#4B0082" stroke-width="2"/>
  <text x="20" y="35" text-anchor="start" fill="#FFD700" font-size="14">★</text>
  <text x="368" y="35" text-anchor="start" fill="#FFD700" font-size="14">★</text>
  <text x="20" y="283" text-anchor="start" fill="#FFD700" font-size="14">★</text>
  <text x="368" y="283" text-anchor="start" fill="#FFD700" font-size="14">★</text>
  <polygon points="200,50 170,100 230,100" fill="#800020" stroke="#FFD700" stroke-width="2"/>
  <polygon points="200,70 180,100 220,100" fill="#006400" stroke="#FFD700" stroke-width="1"/>
  <text x="200" y="90" text-anchor="middle" fill="#FFD700" font-size="16">★</text>
  <text x="200" y="155" text-anchor="middle" fill="#FFD700" font-size="20" font-weight="bold">{route_title}</text>
  <text x="200" y="175" text-anchor="middle" fill="#6A0DAD" font-size="11">{location}</text>
  <g filter="url(#shadow7)">
    <rect x="40" y="195" width="90" height="60" fill="#1a0d2e" stroke="#FFD700" stroke-width="3"/>
    <text x="85" y="218" text-anchor="middle" fill="#FFD700" font-size="18" font-weight="bold">{xp}</text>
    <text x="85" y="240" text-anchor="middle" fill="#800020" font-size="10">XP</text>
  </g>
  <g filter="url(#shadow7)">
    <rect x="155" y="195" width="90" height="60" fill="#1a0d2e" stroke="#FFD700" stroke-width="3"/>
    <text x="200" y="218" text-anchor="middle" fill="#FFD700" font-size="18" font-weight="bold">{distance}</text>
    <text x="200" y="240" text-anchor="middle" fill="#800020" font-size="10">KM</text>
  </g>
  <g filter="url(#shadow7)">
    <rect x="270" y="195" width="90" height="60" fill="#2d1a44" stroke="#6A0DAD" stroke-width="3"/>
    <text x="315" y="218" text-anchor="middle" fill="#4B0082" font-size="14" font-weight="bold">{difficulty}</text>
    <text x="315" y="240" text-anchor="middle" fill="#800020" font-size="10">LEVEL</text>
  </g>
  <text x="200" y="275" text-anchor="middle" fill="#6A0DAD" font-size="10">{date} at {time}</text>
</svg>""",

    # Template 8: Spell Circle
    """<svg viewBox="0 0 400 300" xmlns="http://www.w3.org/2000/svg" style="font-family: monospace; image-rendering: pixelated;">
  <defs>
    <linearGradient id="bgGrad8" x1="0%" y1="0%" x2="0%" y2="100%">
      <stop offset="0%" style="stop-color:#1a1a2e;stop-opacity:1" />
      <stop offset="100%" style="stop-color:#0f0f1a;stop-opacity:1" />
    </linearGradient>
    <linearGradient id="cardGrad8" x1="0%" y1="0%" x2="0%" y2="100%">
      <stop offset="0%" style="stop-color:#2d2d44;stop-opacity:1" />
      <stop offset="100%" style="stop-color:#1f1f2e;stop-opacity:1" />
    </linearGradient>
    <filter id="shadow8">
      <feDropShadow dx="2" dy="2" stdDeviation="1" flood-opacity="0.3"/>
    </filter>
  </defs>
  <rect width="400" height="300" fill="url(#bgGrad8)"/>
  <rect x="8" y="8" width="384" height="284" fill="none" stroke="#6A0DAD" stroke-width="6"/>
  <rect x="12" y="12" width="376" height="276" fill="none" stroke="#FFD700" stroke-width="4"/>
  <rect x="20" y="20" width="360" height="260" fill="url(#cardGrad8)" stroke="#6A0DAD" stroke-width="2"/>
  <text x="20" y="35" text-anchor="start" fill="#FFD700" font-size="14">★</text>
  <text x="368" y="35" text-anchor="start" fill="#FFD700" font-size="14">★</text>
  <text x="20" y="283" text-anchor="start" fill="#FFD700" font-size="14">★</text>
  <text x="368" y="283" text-anchor="start" fill="#FFD700" font-size="14">★</text>
  <circle cx="200" cy="70" r="25" fill="none" stroke="#FFD700" stroke-width="2"/>
  <circle cx="200" cy="70" r="15" fill="none" stroke="#6A0DAD" stroke-width="1"/>
  <text x="200" y="75" text-anchor="middle" fill="#FFD700" font-size="16">★</text>
  <text x="200" y="155" text-anchor="middle" fill="#FFD700" font-size="20" font-weight="bold">{route_title}</text>
  <text x="200" y="175" text-anchor="middle" fill="#6A0DAD" font-size="11">{location}</text>
  <g filter="url(#shadow8)">
    <rect x="40" y="195" width="90" height="60" fill="#1a0d2e" stroke="#FFD700" stroke-width="3"/>
    <text x="85" y="218" text-anchor="middle" fill="#FFD700" font-size="18" font-weight="bold">{xp}</text>
    <text x="85" y="240" text-anchor="middle" fill="#800020" font-size="10">XP</text>
  </g>
  <g filter="url(#shadow8)">
    <rect x="155" y="195" width="90" height="60" fill="#1a0d2e" stroke="#FFD700" stroke-width="3"/>
    <text x="200" y="218" text-anchor="middle" fill="#FFD700" font-size="18" font-weight="bold">{distance}</text>
    <text x="200" y="240" text-anchor="middle" fill="#800020" font-size="10">KM</text>
  </g>
  <g filter="url(#shadow8)">
    <rect x="270" y="195" width="90" height="60" fill="#2d1a44" stroke="#6A0DAD" stroke-width="3"/>
    <text x="315" y="218" text-anchor="middle" fill="#4B0082" font-size="14" font-weight="bold">{difficulty}</text>
    <text x="315" y="240" text-anchor="middle" fill="#800020" font-size="10">LEVEL</text>
  </g>
  <text x="200" y="275" text-anchor="middle" fill="#6A0DAD" font-size="10">{date} at {time}</text>
</svg>""",

    # Template 9: Potion Bottle
    """<svg viewBox="0 0 400 300" xmlns="http://www.w3.org/2000/svg" style="font-family: monospace; image-rendering: pixelated;">
  <defs>
    <linearGradient id="bgGrad9" x1="0%" y1="0%" x2="0%" y2="100%">
      <stop offset="0%" style="stop-color:#1a0d2e;stop-opacity:1" />
      <stop offset="100%" style="stop-color:#0f051a;stop-opacity:1" />
    </linearGradient>
    <linearGradient id="cardGrad9" x1="0%" y1="0%" x2="0%" y2="100%">
      <stop offset="0%" style="stop-color:#2d1a44;stop-opacity:1" />
      <stop offset="100%" style="stop-color:#1f0f2e;stop-opacity:1" />
    </linearGradient>
    <filter id="shadow9">
      <feDropShadow dx="2" dy="2" stdDeviation="1" flood-opacity="0.3"/>
    </filter>
  </defs>
  <rect width="400" height="300" fill="url(#bgGrad9)"/>
  <rect x="8" y="8" width="384" height="284" fill="none" stroke="#FFD700" stroke-width="6"/>
  <rect x="12" y="12" width="376" height="276" fill="none" stroke="#4B0082" stroke-width="4"/>
  <rect x="20" y="20" width="360" height="260" fill="url(#cardGrad9)" stroke="#FFD700" stroke-width="2"/>
  <text x="20" y="35" text-anchor="start" fill="#FFD700" font-size="14">★</text>
  <text x="368" y="35" text-anchor="start" fill="#FFD700" font-size="14">★</text>
  <text x="20" y="283" text-anchor="start" fill="#FFD700" font-size="14">★</text>
  <text x="368" y="283" text-anchor="start" fill="#FFD700" font-size="14">★</text>
  <rect x="185" y="50" width="30" height="50" fill="#4B0082" stroke="#FFD700" stroke-width="2"/>
  <polygon points="185,50 200,40 215,50" fill="#FFD700" stroke="#DAA520" stroke-width="1"/>
  <rect x="190" y="100" width="20" height="10" fill="#6A0DAD"/>
  <text x="200" y="155" text-anchor="middle" fill="#FFD700" font-size="20" font-weight="bold">{route_title}</text>
  <text x="200" y="175" text-anchor="middle" fill="#6A0DAD" font-size="11">{location}</text>
  <g filter="url(#shadow9)">
    <rect x="40" y="195" width="90" height="60" fill="#1a0d2e" stroke="#FFD700" stroke-width="3"/>
    <text x="85" y="218" text-anchor="middle" fill="#FFD700" font-size="18" font-weight="bold">{xp}</text>
    <text x="85" y="240" text-anchor="middle" fill="#800020" font-size="10">XP</text>
  </g>
  <g filter="url(#shadow9)">
    <rect x="155" y="195" width="90" height="60" fill="#1a0d2e" stroke="#FFD700" stroke-width="3"/>
    <text x="200" y="218" text-anchor="middle" fill="#FFD700" font-size="18" font-weight="bold">{distance}</text>
    <text x="200" y="240" text-anchor="middle" fill="#800020" font-size="10">KM</text>
  </g>
  <g filter="url(#shadow9)">
    <rect x="270" y="195" width="90" height="60" fill="#2d1a44" stroke="#6A0DAD" stroke-width="3"/>
    <text x="315" y="218" text-anchor="middle" fill="#4B0082" font-size="14" font-weight="bold">{difficulty}</text>
    <text x="315" y="240" text-anchor="middle" fill="#800020" font-size="10">LEVEL</text>
  </g>
  <text x="200" y="275" text-anchor="middle" fill="#6A0DAD" font-size="10">{date} at {time}</text>
</svg>""",

    # Template 10: Crystal Ball
    """<svg viewBox="0 0 400 300" xmlns="http://www.w3.org/2000/svg" style="font-family: monospace; image-rendering: pixelated;">
  <defs>
    <linearGradient id="bgGrad10" x1="0%" y1="0%" x2="0%" y2="100%">
      <stop offset="0%" style="stop-color:#1a1a2e;stop-opacity:1" />
      <stop offset="100%" style="stop-color:#0f0f1a;stop-opacity:1" />
    </linearGradient>
    <linearGradient id="cardGrad10" x1="0%" y1="0%" x2="0%" y2="100%">
      <stop offset="0%" style="stop-color:#2d2d44;stop-opacity:1" />
      <stop offset="100%" style="stop-color:#1f1f2e;stop-opacity:1" />
    </linearGradient>
    <filter id="shadow10">
      <feDropShadow dx="2" dy="2" stdDeviation="1" flood-opacity="0.3"/>
    </filter>
  </defs>
  <rect width="400" height="300" fill="url(#bgGrad10)"/>
  <rect x="8" y="8" width="384" height="284" fill="none" stroke="#6A0DAD" stroke-width="6"/>
  <rect x="12" y="12" width="376" height="276" fill="none" stroke="#FFD700" stroke-width="4"/>
  <rect x="20" y="20" width="360" height="260" fill="url(#cardGrad10)" stroke="#6A0DAD" stroke-width="2"/>
  <text x="20" y="35" text-anchor="start" fill="#FFD700" font-size="14">★</text>
  <text x="368" y="35" text-anchor="start" fill="#FFD700" font-size="14">★</text>
  <text x="20" y="283" text-anchor="start" fill="#FFD700" font-size="14">★</text>
  <text x="368" y="283" text-anchor="start" fill="#FFD700" font-size="14">★</text>
  <circle cx="200" cy="70" r="22" fill="#6A0DAD" stroke="#FFD700" stroke-width="2"/>
  <circle cx="200" cy="70" r="15" fill="#4B0082" opacity="0.6"/>
  <rect x="185" y="92" width="30" height="8" fill="#FFD700"/>
  <text x="200" y="155" text-anchor="middle" fill="#FFD700" font-size="20" font-weight="bold">{route_title}</text>
  <text x="200" y="175" text-anchor="middle" fill="#6A0DAD" font-size="11">{location}</text>
  <g filter="url(#shadow10)">
    <rect x="40" y="195" width="90" height="60" fill="#1a0d2e" stroke="#FFD700" stroke-width="3"/>
    <text x="85" y="218" text-anchor="middle" fill="#FFD700" font-size="18" font-weight="bold">{xp}</text>
    <text x="85" y="240" text-anchor="middle" fill="#800020" font-size="10">XP</text>
  </g>
  <g filter="url(#shadow10)">
    <rect x="155" y="195" width="90" height="60" fill="#1a0d2e" stroke="#FFD700" stroke-width="3"/>
    <text x="200" y="218" text-anchor="middle" fill="#FFD700" font-size="18" font-weight="bold">{distance}</text>
    <text x="200" y="240" text-anchor="middle" fill="#800020" font-size="10">KM</text>
  </g>
  <g filter="url(#shadow10)">
    <rect x="270" y="195" width="90" height="60" fill="#2d1a44" stroke="#6A0DAD" stroke-width="3"/>
    <text x="315" y="218" text-anchor="middle" fill="#4B0082" font-size="14" font-weight="bold">{difficulty}</text>
    <text x="315" y="240" text-anchor="middle" fill="#800020" font-size="10">LEVEL</text>
  </g>
  <text x="200" y="275" text-anchor="middle" fill="#6A0DAD" font-size="10">{date} at {time}</text>
</svg>"""
]


def get_random_template() -> str:
    """Randomly select one of the SVG templates."""
    return random.choice(SVG_TEMPLATES)


def fill_template(
    template: str,
    route_title: str,
    location: str,
    xp: int,
    distance: float,
    difficulty: str,
    date: str,
    time: str
) -> str:
    """
    Fill template placeholders with actual values.
    
    Args:
        template: SVG template string with placeholders
        route_title: Route name
        location: Route location
        xp: XP gained
        distance: Distance in km
        difficulty: Difficulty level string
        date: Completion date
        time: Completion time
    
    Returns:
        Filled SVG string
    """
    return template.format(
        route_title=route_title,
        location=location,
        xp=xp,
        distance=distance,
        difficulty=difficulty,
        date=date,
        time=time
    )


def generate_souvenir_svg(
    route_title: str,
    route_location: str,
    completed_at,
    xp_gained: int,
    distance_km: float,
    difficulty: str
) -> str:
    """
    Generate a souvenir SVG using template system.
    
    Args:
        route_title: Route name
        route_location: Route location
        completed_at: datetime object
        xp_gained: XP earned
        distance_km: Distance in kilometers
        difficulty: Difficulty string (Easy/Moderate/Difficult/Expert)
    
    Returns:
        Complete SVG string
    """
    # Format date and time
    date_str = completed_at.strftime("%Y-%m-%d")
    time_str = completed_at.strftime("%H:%M")
    
    # Select random template
    template = get_random_template()
    
    # Fill template
    svg = fill_template(
        template=template,
        route_title=route_title,
        location=route_location or "Unknown Location",
        xp=xp_gained,
        distance=f"{distance_km:.1f}",
        difficulty=difficulty.upper(),
        date=date_str,
        time=time_str
    )
    
    # Ensure preserveAspectRatio is set for proper scaling
    if 'preserveAspectRatio' not in svg:
        svg = svg.replace(
            '<svg viewBox',
            '<svg preserveAspectRatio="xMidYMid meet" viewBox'
        )
    
    return svg

