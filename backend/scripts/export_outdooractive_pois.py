"""
Export Outdooractive POI references for all routes currently stored in the database.

Workflow:
1. Read every route ID from the `routes` table.
2. Use the Outdooractive `/oois/{ids}` bulk endpoint to fetch detailed tour metadata.
3. Extract up to N POI IDs from each tour (default: 5).
4. Batch-fetch the POI objects themselves (JSON or XML response) and consolidate their
   basic fields.
5. Write a JSON payload that links each route to its POIs plus a deduplicated list of
   POI summaries.

Example:
    python backend/scripts/export_outdooractive_pois.py \
        --output /tmp/route_pois.json \
        --route-limit 25

You must provide a valid Outdooractive API key via `OUTDOORACTIVE_API_KEY` or --api-key.
"""

from __future__ import annotations

import argparse
import asyncio
import json
import os
import sys
import time
from collections import defaultdict
from datetime import datetime, timezone
from typing import Any, Iterable, Sequence
from xml.etree import ElementTree as ET

import httpx
from sqlalchemy import select

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, ROOT_DIR)

from app.database import get_db, init_db  # noqa: E402
from app.models.entities import Route  # noqa: E402
from app.settings import get_settings  # noqa: E402

RETRYABLE_STATUSES = {408, 425, 429, 500, 502, 503, 504}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--output",
        type=str,
        default=os.path.join(ROOT_DIR, "data/outdooractive/route_pois_consolidated.json"),
        help="Destination JSON file for the consolidated route/POI payload.",
    )
    parser.add_argument(
        "--api-key",
        type=str,
        default=os.environ.get("OUTDOORACTIVE_API_KEY"),
        help="Outdooractive API key (defaults to OUTDOORACTIVE_API_KEY env var).",
    )
    parser.add_argument(
        "--project",
        type=str,
        default="api-dev-oa",
        help="Outdooractive project identifier (default: api-dev-oa).",
    )
    parser.add_argument(
        "--route-limit",
        type=int,
        default=None,
        help="Optional maximum number of routes to process (useful for smoke tests).",
    )
    parser.add_argument(
        "--route-chunk-size",
        type=int,
        default=20,
        help="Number of route IDs to request per bulk /oois call.",
    )
    parser.add_argument(
        "--poi-chunk-size",
        type=int,
        default=80,
        help="Number of POI IDs to request per bulk /oois call.",
    )
    parser.add_argument(
        "--max-pois-per-route",
        type=int,
        default=5,
        help="Maximum POI IDs to keep per route (smaller counts are preserved as-is).",
    )
    parser.add_argument(
        "--timeout",
        type=float,
        default=20.0,
        help="HTTP timeout (seconds) for Outdooractive requests.",
    )
    parser.add_argument(
        "--max-retries",
        type=int,
        default=5,
        help="Maximum retry attempts for retryable HTTP statuses.",
    )
    parser.add_argument(
        "--initial-backoff",
        type=float,
        default=1.0,
        help="Initial delay (seconds) applied after a retryable failure.",
    )
    parser.add_argument(
        "--backoff-multiplier",
        type=float,
        default=2.0,
        help="Multiplier applied to the delay after each retry.",
    )
    parser.add_argument(
        "--request-interval",
        type=float,
        default=0.4,
        help="Sleep duration (seconds) between successful API calls to avoid rate limits.",
    )
    return parser.parse_args()


async def load_routes_from_db(limit: int | None) -> list[dict[str, Any]]:
    """Fetch (id, title, category_name) for every route currently persisted."""
    settings = get_settings()
    init_db(settings)

    async with get_db() as session:
        stmt = select(Route.id, Route.title, Route.category_name).order_by(Route.id)
        if limit is not None:
            stmt = stmt.limit(limit)
        result = await session.execute(stmt)
        rows = result.all()

    routes: list[dict[str, Any]] = []
    for route_id, title, category in rows:
        routes.append(
            {
                "id": int(route_id),
                "title": title,
                "category_name": category,
            }
        )
    return routes


def chunked(seq: Sequence[Any], size: int) -> Iterable[Sequence[Any]]:
    for idx in range(0, len(seq), size):
        yield seq[idx : idx + size]


def strip_namespace(tag: str) -> str:
    return tag.split("}", 1)[-1] if "}" in tag else tag


def find_direct_child(node: ET.Element, tag_name: str) -> ET.Element | None:
    for child in list(node):
        if strip_namespace(child.tag) == tag_name:
            return child
    return None


def find_direct_child_text(node: ET.Element, tag_name: str) -> str | None:
    child = find_direct_child(node, tag_name)
    if child is None:
        return None
    text = (child.text or "").strip()
    return text or None


def find_first_descendant(node: ET.Element, tag_name: str) -> ET.Element | None:
    for descendant in node.iter():
        if descendant is node:
            continue
        if strip_namespace(descendant.tag) == tag_name:
            return descendant
    return None


def parse_route_batch_for_pois(xml_text: str, max_pois_per_route: int) -> dict[int, list[int]]:
    """Parse a bulk /oois XML response and return {route_id: [poi_id, ...]}."""
    try:
        root = ET.fromstring(xml_text)
    except ET.ParseError as exc:  # pragma: no cover - depends on remote API
        raise ValueError(f"Failed to parse tour metadata XML: {exc}") from exc

    route_to_pois: dict[int, list[int]] = {}
    for node in root.iter():
        tag = strip_namespace(node.tag).lower()
        if tag not in {"ooi", "item"}:
            continue

        route_id_text = find_direct_child_text(node, "id") or node.attrib.get("id")
        if not route_id_text:
            continue

        try:
            route_id = int(route_id_text)
        except ValueError:
            continue

        node_type = (find_direct_child_text(node, "type") or node.attrib.get("type") or "").lower()
        if node_type and node_type not in {"tour", "route"}:
            # Skip POI responses that might sneak into the same payload.
            continue

        pois_section = find_first_descendant(node, "pois")
        poi_ids: list[int] = []
        if pois_section is not None:
            for poi_node in list(pois_section):
                if strip_namespace(poi_node.tag) != "poi":
                    continue
                poi_id_text = poi_node.attrib.get("id") or (poi_node.text or "").strip()
                if not poi_id_text:
                    continue
                try:
                    poi_id = int(poi_id_text)
                except ValueError:
                    continue
                poi_ids.append(poi_id)
                if 0 < max_pois_per_route <= len(poi_ids):
                    break

        route_to_pois[route_id] = poi_ids
    return route_to_pois


def build_oois_url(project: str, ids: Sequence[int], api_key: str) -> str:
    joined = ",".join(str(value) for value in ids)
    return f"https://www.outdooractive.com/api/project/{project}/oois/{joined}?key={api_key}"


def fetch_with_retries(
    client: httpx.Client,
    url: str,
    *,
    accept: str,
    timeout: float,
    max_retries: int,
    initial_backoff: float,
    backoff_multiplier: float,
) -> httpx.Response:
    attempt = 0
    delay = initial_backoff

    while True:
        attempt += 1
        try:
            response = client.get(url, headers={"Accept": accept}, timeout=timeout)
            response.raise_for_status()
            return response
        except httpx.HTTPStatusError as exc:  # pragma: no cover - network side effect
            status = exc.response.status_code
            should_retry = status in RETRYABLE_STATUSES and attempt <= max_retries
            if not should_retry:
                raise

            sleep_for = delay
            retry_after = exc.response.headers.get("Retry-After")
            if retry_after:
                try:
                    sleep_for = max(sleep_for, float(retry_after))
                except ValueError:
                    pass
            print(
                f"↻ HTTP {status} for {url} (attempt {attempt}/{max_retries}); "
                f"sleeping {sleep_for:.1f}s before retry."
            )
            time.sleep(sleep_for)
            delay *= backoff_multiplier


def unwrap_nested_items(payload: Any) -> list[Any]:
    """
    Try to extract the list of POI objects from various possible JSON wrappers.

    Outdooractive's responses vary between bare arrays and nested dicts such as:
      {"result": {"items": [{"ooi": {...}}]}}
    """
    if payload is None:
        return []
    if isinstance(payload, list):
        return payload
    if isinstance(payload, dict):
        for key in ("items", "results", "result", "data", "pois", "oois"):
            if key not in payload:
                continue
            nested = payload[key]
            items = unwrap_nested_items(nested)
            if items:
                return items
    return []


def unwrap_ooi_container(item: Any) -> dict[str, Any] | None:
    if isinstance(item, dict):
        for key in ("ooi", "poi", "item", "result"):
            value = item.get(key)
            if isinstance(value, dict):
                return value
    return item if isinstance(item, dict) else None


def find_first_by_keys(structure: Any, key_candidates: tuple[str, ...]) -> Any | None:
    """
    Depth-first search for the first value whose key matches one of key_candidates.
    """
    lowered = {key.lower() for key in key_candidates}
    stack = [structure]

    while stack:
        current = stack.pop()
        if isinstance(current, dict):
            for key, value in current.items():
                key_lower = key.lower()
                if key_lower in lowered:
                    if isinstance(value, (str, int, float)):
                        return value
                    if isinstance(value, dict):
                        for nested_key in ("value", "name", "text"):
                            nested_value = value.get(nested_key)
                            if isinstance(nested_value, (str, int, float)):
                                return nested_value
                    if isinstance(value, list):
                        for element in value:
                            if isinstance(element, (str, int, float)):
                                return element
                if isinstance(value, (dict, list)):
                    stack.append(value)
        elif isinstance(current, list):
            stack.extend(current)
    return None


def to_int(value: Any) -> int | None:
    if value is None:
        return None
    try:
        return int(str(value).strip())
    except (ValueError, TypeError):
        return None


def to_float(value: Any) -> float | None:
    if value is None:
        return None
    try:
        return float(str(value).strip())
    except (ValueError, TypeError):
        return None


def summarize_poi_record(record: dict[str, Any]) -> dict[str, Any]:
    poi_id = (
        record.get("id")
        or record.get("@id")
        or find_first_by_keys(record, ("poiId", "ooiId", "identifier"))
    )
    normalized_id = to_int(poi_id)
    if normalized_id is None:
        raise ValueError("Unable to extract POI id from record.")

    name = find_first_by_keys(record, ("title", "name", "label"))
    poi_type = find_first_by_keys(record, ("type", "category", "subcategory"))
    category = None
    if isinstance(record.get("category"), dict):
        category = record["category"].get("name") or record["category"].get("value")
    if not category:
        category = find_first_by_keys(record, ("categoryName", "category"))

    lat = find_first_by_keys(record, ("lat", "latitude", "y"))
    lon = find_first_by_keys(record, ("lon", "lng", "longitude", "x"))

    summary = {
        "id": normalized_id,
        "name": name,
        "type": poi_type,
        "category": category,
        "latitude": to_float(lat),
        "longitude": to_float(lon),
        "raw": record,
    }
    return summary


def element_to_nested_dict(element: ET.Element) -> dict[str, Any]:
    data: dict[str, Any] = {}
    if element.attrib:
        for key, value in element.attrib.items():
            data[f"@{key}"] = value

    children = list(element)
    if not children:
        text = (element.text or "").strip()
        if text:
            data["value"] = text
        return data

    grouped: dict[str, list[Any]] = defaultdict(list)
    for child in children:
        grouped[strip_namespace(child.tag)].append(element_to_nested_dict(child))

    for key, values in grouped.items():
        if len(values) == 1:
            data[key] = values[0]
        else:
            data[key] = values
    return data


def parse_poi_batch(content: str) -> list[dict[str, Any]]:
    try:
        payload = json.loads(content)
    except json.JSONDecodeError:
        # Attempt XML parsing fallback.
        try:
            root = ET.fromstring(content)
        except ET.ParseError as exc:  # pragma: no cover - remote API dependent
            raise ValueError("POI payload is neither valid JSON nor XML.") from exc

        summaries: list[dict[str, Any]] = []
        for node in root.iter():
            tag = strip_namespace(node.tag).lower()
            if tag not in {"ooi", "item"}:
                continue
            record = element_to_nested_dict(node)
            summaries.append(summarize_poi_record(record))
        return summaries

    items = unwrap_nested_items(payload)
    if not items and isinstance(payload, dict):
        # Some responses encode a single POI as a dict without a list wrapper.
        items = [payload]

    summaries: list[dict[str, Any]] = []
    for item in items:
        record = unwrap_ooi_container(item)
        if not isinstance(record, dict):
            continue
        summaries.append(summarize_poi_record(record))
    return summaries


def main() -> None:
    args = parse_args()
    if not args.api_key:
        print("Error: Missing Outdooractive API key. Use --api-key or OUTDOORACTIVE_API_KEY.")
        sys.exit(1)

    routes = asyncio.run(load_routes_from_db(args.route_limit))
    if not routes:
        print("No routes found in the database. Aborting.")
        sys.exit(0)
    print(f"Loaded {len(routes)} routes from the database.")

    client = httpx.Client()
    route_records: list[dict[str, Any]] = []
    route_failures: list[dict[str, Any]] = []
    unique_poi_ids: set[int] = set()

    try:
        for batch_index, batch in enumerate(chunked(routes, args.route_chunk_size), start=1):
            batch_ids = [route["id"] for route in batch]
            url = build_oois_url(args.project, batch_ids, args.api_key)

            try:
                response = fetch_with_retries(
                    client,
                    url,
                    accept="application/xml",
                    timeout=args.timeout,
                    max_retries=args.max_retries,
                    initial_backoff=args.initial_backoff,
                    backoff_multiplier=args.backoff_multiplier,
                )
            except Exception as exc:  # noqa: BLE001 - network error
                route_failures.append({"ids": batch_ids, "reason": str(exc)})
                print(f"✗ Route batch {batch_index} failed: {exc}")
                continue

            route_poi_map = parse_route_batch_for_pois(response.text, args.max_pois_per_route)
            for route in batch:
                poi_ids = route_poi_map.get(route["id"], [])
                unique_poi_ids.update(poi_ids)
                route_records.append(
                    {
                        "id": route["id"],
                        "title": route.get("title"),
                        "category": route.get("category_name"),
                        "poi_ids": poi_ids,
                        "poi_count": len(poi_ids),
                    }
                )
            print(
                f"✓ Route batch {batch_index}: fetched {len(batch)} tours, "
                f"collected {sum(len(ids) for ids in route_poi_map.values())} POI refs."
            )
            if args.request_interval > 0:
                time.sleep(args.request_interval)
    finally:
        client.close()

    route_records.sort(key=lambda entry: entry["id"])
    unique_poi_ids_sorted = sorted(unique_poi_ids)
    print(f"\nCollected {len(unique_poi_ids_sorted)} unique POI IDs across {len(route_records)} routes.")

    poi_records: dict[int, dict[str, Any]] = {}
    poi_failures: list[dict[str, Any]] = []

    if unique_poi_ids_sorted:
        client = httpx.Client()
        try:
            for batch_index, batch in enumerate(chunked(unique_poi_ids_sorted, args.poi_chunk_size), start=1):
                url = build_oois_url(args.project, batch, args.api_key)
                try:
                    response = fetch_with_retries(
                        client,
                        url,
                        accept="application/json, application/xml;q=0.9",
                        timeout=args.timeout,
                        max_retries=args.max_retries,
                        initial_backoff=args.initial_backoff,
                        backoff_multiplier=args.backoff_multiplier,
                    )
                    summaries = parse_poi_batch(response.text)
                except Exception as exc:  # noqa: BLE001
                    poi_failures.append({"ids": batch, "reason": str(exc)})
                    print(f"✗ POI batch {batch_index} failed: {exc}")
                    continue

                returned_ids = set()
                for summary in summaries:
                    poi_id = summary.get("id")
                    if poi_id is None:
                        continue
                    poi_records[int(poi_id)] = summary
                    returned_ids.add(int(poi_id))

                missing = [poi_id for poi_id in batch if poi_id not in returned_ids]
                if missing:
                    poi_failures.append({"ids": missing, "reason": "missing_from_response"})

                print(
                    f"✓ POI batch {batch_index}: requested {len(batch)} ids, received {len(returned_ids)} records."
                )
                if args.request_interval > 0:
                    time.sleep(args.request_interval)
        finally:
            client.close()

    output_payload = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "project": args.project,
        "route_count": len(route_records),
        "poi_count": len(poi_records),
        "parameters": {
            "route_limit": args.route_limit,
            "route_chunk_size": args.route_chunk_size,
            "poi_chunk_size": args.poi_chunk_size,
            "max_pois_per_route": args.max_pois_per_route,
        },
        "routes": route_records,
        "pois": sorted(poi_records.values(), key=lambda entry: entry["id"]),
        "route_failures": route_failures,
        "poi_failures": poi_failures,
    }

    output_path = os.path.abspath(args.output)
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as fp:
        json.dump(output_payload, fp, ensure_ascii=False, indent=2)

    print(
        f"\nSaved consolidated POI payload for {len(route_records)} routes "
        f"and {len(poi_records)} POIs to {output_path}"
    )
    if route_failures or poi_failures:
        print("Some batches reported failures. Consult the JSON output for specifics.")


if __name__ == "__main__":
    main()


