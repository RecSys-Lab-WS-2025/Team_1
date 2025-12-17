#!/usr/bin/env python3
"""
Generate preview SVG files for all 10 templates.
"""
import sys
from pathlib import Path
from datetime import datetime

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.services.svg_templates import SVG_TEMPLATES, fill_template

# Create output directory
output_dir = Path(__file__).parent.parent.parent / "svg_templates_preview"
output_dir.mkdir(exist_ok=True)

# Sample data for all templates
sample_data = {
    "route_title": "Alpine Adventure Trail",
    "location": "Bavarian Alps, Germany",
    "xp": 250,
    "distance": "8.5",
    "difficulty": "DIFFICULT",
    "date": "2025-12-02",
    "time": "15:30"
}

print("🎨 Generating SVG template previews...\n")
print(f"📁 Output directory: {output_dir}\n")

# Generate SVG for each template
for i, template in enumerate(SVG_TEMPLATES, 1):
    try:
        # Fill template with sample data
        svg_content = fill_template(
            template=template,
            route_title=sample_data["route_title"],
            location=sample_data["location"],
            xp=sample_data["xp"],
            distance=sample_data["distance"],
            difficulty=sample_data["difficulty"],
            date=sample_data["date"],
            time=sample_data["time"]
        )
        
        # Determine template name based on content
        template_names = [
            "01_wand_with_stars",
            "02_stars_cluster",
            "03_crescent_moon",
            "04_owl_silhouette",
            "05_magical_book",
            "06_golden_snitch",
            "07_house_badge",
            "08_spell_circle",
            "09_potion_bottle",
            "10_crystal_ball"
        ]
        
        filename = f"{template_names[i-1]}.svg"
        filepath = output_dir / filename
        
        # Write SVG file
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(svg_content)
        
        print(f"✅ Template {i:2d}: {filename} ({len(svg_content)} chars)")
        
    except Exception as e:
        print(f"❌ Template {i:2d}: Error - {e}")

print(f"\n🎉 All templates generated in: {output_dir}")
print(f"📊 Total: {len(SVG_TEMPLATES)} templates")

