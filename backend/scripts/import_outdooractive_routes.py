"""
Import Outdooractive tour metadata into the `routes` table.

Usage:
    python backend/scripts/import_outdooractive_routes.py \
        --tours-json backend/data/outdooractive/tours_20251118T094405Z.json
"""

from __future__ import annotations

import argparse
import asyncio
import json
import os
import re
from typing import Any

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))

import sys

sys.path.insert(0, ROOT_DIR)

from app.database import get_db, init_db
from app.models.entities import Route
from app.settings import get_settings


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--tours-json",
        type=str,
        default=os.path.join(ROOT_DIR, "data/outdooractive/tours_20251118T094405Z.json"),
        help="Path to the cached Outdooractive tours JSON file.",
    )
    parser.add_argument(
        "--limit",
        type=int,
        default=None,
        help="Optional maximum number of tours to import (after deduplication).",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Parse and show stats without touching the database.",
    )
    return parser.parse_args()


PARAGRAPH_TAG_PATTERN = re.compile(r"</p\s*>", flags=re.IGNORECASE)
BR_TAG_PATTERN = re.compile(r"<br\s*/?>", flags=re.IGNORECASE)
HTML_TAG_PATTERN = re.compile(r"<[^>]+>")


def html_to_text(raw: str | None) -> str | None:
    if not raw:
        return None
    text = BR_TAG_PATTERN.sub("\n", raw)
    text = PARAGRAPH_TAG_PATTERN.sub("\n\n", text)
    text = HTML_TAG_PATTERN.sub(" ", text)
    text = re.sub(r"\s+", " ", text)
    text = re.sub(r"(\s*\n\s*)+", "\n", text)
    normalized = text.strip()
    return normalized or None


def load_tours(json_path: str) -> list[dict[str, Any]]:
    with open(json_path, "r", encoding="utf-8") as fp:
        payload = json.load(fp)

    seen_ids: set[int] = set()
    tours: list[dict[str, Any]] = []
    for category in payload.get("categories", []):
        for tour in category.get("tours", []):
            tour_id = tour.get("id")
            if tour_id is None or tour_id in seen_ids:
                continue
            tours.append(tour)
            seen_ids.add(tour_id)
    return tours


def compose_short_description(short_text: str | None, long_text: str | None) -> str | None:
    short_norm = short_text.strip() if short_text else None
    long_norm = html_to_text(long_text)

    if short_norm and long_norm:
        return f"{short_norm}\n\n{long_norm}"
    if short_norm:
        return short_norm
    return long_norm


def extract_tag_texts(tour: dict[str, Any]) -> str | None:
    tags = tour.get("tags") or []
    texts = [tag.get("text") for tag in tags if isinstance(tag, dict) and tag.get("text")]
    if not texts:
        return None
    return json.dumps(texts, ensure_ascii=False)


def transform_tour_to_route_fields(tour: dict[str, Any]) -> dict[str, Any]:
    category = tour.get("category") or {}
    difficulty_raw = tour.get("difficulty")
    try:
        difficulty = int(difficulty_raw) if difficulty_raw not in (None, "") else None
    except ValueError:
        difficulty = None

    return {
        "id": tour["id"],
        "title": tour.get("title") or "Untitled Route",
        "category_name": category.get("name"),
        "length_meters": tour.get("length_m"),
        "duration_min": tour.get("duration_min"),
        "difficulty": difficulty,
        "short_description": compose_short_description(
            tour.get("short_text"),
            tour.get("long_text"),
        ),
        "tags_json": extract_tag_texts(tour),
        "gpx_data_raw": None,
        "xp_required": 0,
        "story_prologue_title": None,
        "story_prologue_body": None,
        "story_epilogue_body": None,
    }


async def upsert_routes(
    tours: list[dict[str, Any]],
    *,
    limit: int | None,
    dry_run: bool,
) -> None:
    if limit is not None:
        tours = tours[:limit]

    print(f"Prepared {len(tours)} unique tours.")
    if dry_run:
        previews = [tour.get("title", "Untitled") for tour in tours[:5]]
        print("Dry run enabled. Sample titles:", previews)
        return

    settings = get_settings()
    init_db(settings)

    async with get_db() as session:
        upserted = 0
        for tour in tours:
            route_fields = transform_tour_to_route_fields(tour)
            route = await session.get(Route, route_fields["id"])
            if route is None:
                route = Route(**route_fields)
                session.add(route)
            else:
                for key, value in route_fields.items():
                    setattr(route, key, value)
            upserted += 1
        await session.commit()
        print(f"Upserted {upserted} routes.")


async def async_main() -> None:
    args = parse_args()
    tours = load_tours(args.tours_json)
    await upsert_routes(tours, limit=args.limit, dry_run=args.dry_run)


def main() -> None:
    asyncio.run(async_main())


if __name__ == "__main__":
    main()

