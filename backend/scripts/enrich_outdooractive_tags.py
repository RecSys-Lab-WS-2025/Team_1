"""
Fetch tag metadata for Outdooractive tours and enrich the cached JSON payload.

Usage:
    python backend/scripts/enrich_outdooractive_tags.py \
        --tours-json backend/data/outdooractive/tours_20251118T094405Z.json \
        --api-key 0123456789abcdef0123456789abcdef
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import time
from pathlib import Path
from typing import Any
from xml.etree import ElementTree as ET

import httpx

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--tours-json",
        type=str,
        default=os.path.join(ROOT_DIR, "data/outdooractive/tours_20251118T094405Z.json"),
        help="Path to the cached Outdooractive tours JSON file.",
    )
    parser.add_argument(
        "--api-key",
        type=str,
        required=True,
        help="Outdooractive API key (32 hex chars).",
    )
    parser.add_argument(
        "--project",
        type=str,
        default="api-dev-oa",
        help="Outdooractive project identifier. Defaults to api-dev-oa.",
    )
    parser.add_argument(
        "--chunk-size",
        type=int,
        default=20,
        help="Number of tour IDs to request per API call.",
    )
    parser.add_argument(
        "--sleep",
        type=float,
        default=0.2,
        help="Delay between batch requests to avoid rate limits (seconds).",
    )
    return parser.parse_args()


def load_tours(json_path: str) -> dict[str, Any]:
    with open(json_path, "r", encoding="utf-8") as fp:
        return json.load(fp)


def flatten_tour_ids(payload: dict[str, Any]) -> list[int]:
    ids: list[int] = []
    for category in payload.get("categories", []):
        for tour in category.get("tours", []):
            tour_id = tour.get("id")
            if isinstance(tour_id, int):
                ids.append(tour_id)
    return ids


def chunked(seq: list[int], size: int) -> list[list[int]]:
    return [seq[i : i + size] for i in range(0, len(seq), size)]


OA_NAMESPACE = {"oa": "http://www.outdooractive.com/api/"}


def fetch_properties_for_ids(
    client: httpx.Client,
    *,
    ids: list[int],
    api_key: str,
    project: str,
) -> dict[int, list[dict[str, str]]]:
    if not ids:
        return {}

    joined_ids = ",".join(str(i) for i in ids)
    url = f"https://www.outdooractive.com/api/project/{project}/oois/{joined_ids}"
    params = {"key": api_key}
    response = client.get(url, params=params)
    response.raise_for_status()

    root = ET.fromstring(response.text)
    results: dict[int, list[dict[str, str]]] = {}

    for tour_node in root.findall(".//oa:tour", namespaces=OA_NAMESPACE):
        ooi_id_raw = tour_node.get("id")
        if not ooi_id_raw:
            continue
        try:
            ooi_id = int(ooi_id_raw)
        except ValueError:
            continue

        tags: list[dict[str, str]] = []
        for prop in tour_node.findall(".//oa:properties/oa:property", namespaces=OA_NAMESPACE):
            tag_data = {
                "tag": prop.get("tag"),
                "text": prop.get("text"),
                "hasIcon": prop.get("hasIcon"),
                "iconURL": prop.get("iconURL"),
            }
            tags.append(tag_data)
        results[ooi_id] = tags

    return results


def enrich_payload_with_tags(
    payload: dict[str, Any],
    *,
    tag_lookup: dict[int, list[dict[str, str]]],
) -> None:
    for category in payload.get("categories", []):
        for tour in category.get("tours", []):
            tour_id = tour.get("id")
            if not isinstance(tour_id, int):
                continue
            tags = tag_lookup.get(tour_id, [])
            tour["tags"] = tags


def main() -> None:
    args = parse_args()
    payload = load_tours(args.tours_json)
    all_ids = flatten_tour_ids(payload)
    unique_ids = sorted(set(all_ids))

    print(f"Unique tours to enrich: {len(unique_ids)}")
    client = httpx.Client(timeout=30.0)
    tag_lookup: dict[int, list[dict[str, str]]] = {}

    try:
        for batch in chunked(unique_ids, args.chunk_size):
            props = fetch_properties_for_ids(
                client,
                ids=batch,
                api_key=args.api_key,
                project=args.project,
            )
            tag_lookup.update(props)
            print(f"Fetched tags for batch of {len(batch)} tours.")
            if args.sleep:
                time.sleep(args.sleep)
    finally:
        client.close()

    enrich_payload_with_tags(payload, tag_lookup=tag_lookup)

    output_path = Path(args.tours_json)
    with output_path.open("w", encoding="utf-8") as fp:
        json.dump(payload, fp, ensure_ascii=False, indent=2)

    print(f"Updated tags for {len(tag_lookup)} tours and wrote back to {output_path}.")


if __name__ == "__main__":
    main()

