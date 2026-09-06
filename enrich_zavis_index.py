#!/usr/bin/env python3
"""Add coordinates from Zavis detail pages to the complete provider index."""

import csv
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

from extract_zavis import parse_provider_detail, safe_fetch

ROOT = Path(__file__).resolve().parent
SOURCE = ROOT / "sources/csv/zavis-providers.csv"
OUTPUT = ROOT / "sources/csv/zavis-providers-enriched.csv"


def enrich(row: dict[str, str]) -> dict[str, str]:
    """Fetch one Zavis detail page and append location/contact fields."""
    detail = parse_provider_detail(safe_fetch(row.get("url", ""), timeout=20))
    row.update({"lat": detail["lat"], "lon": detail["lon"], "email": detail["email"]})
    row["maps_url"] = (f'https://www.google.com/maps?q={detail["lat"]},{detail["lon"]}'
                       if detail["lat"] and detail["lon"] else "")
    return row


def main() -> int:
    """Enrich all indexed providers into a checkpointed separate CSV."""
    input_path = OUTPUT if OUTPUT.exists() else SOURCE
    with input_path.open(encoding="utf-8-sig", newline="") as stream:
        rows = list(csv.DictReader(stream))
    fields = list(rows[0])
    for field in ("lat", "lon", "email", "maps_url"):
        if field not in fields:
            fields.append(field)
    pending = [row for row in rows if not row.get("lat") or not row.get("lon")]
    processed = 0
    while pending:
        batch = pending[:100]
        with ThreadPoolExecutor(max_workers=2) as pool:
            enriched = list(pool.map(enrich, batch))
        by_id = {row["id"]: row for row in enriched}
        rows = [by_id.get(row["id"], row) for row in rows]
        with OUTPUT.open("w", encoding="utf-8", newline="") as stream:
            writer = csv.DictWriter(stream, fieldnames=fields)
            writer.writeheader()
            writer.writerows(rows)
        located = sum(bool(row["lat"] and row["lon"]) for row in enriched)
        processed += len(batch)
        print(f"Checkpoint {processed}; added {located}", flush=True)
        if not located:
            print("Stopping after a no-progress batch", flush=True)
            break
        pending = [row for row in rows if not row.get("lat") or not row.get("lon")]
    located = sum(bool(row["lat"] and row["lon"]) for row in rows)
    print(f"Enriched {located} of {len(rows)} Zavis providers with coordinates")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
