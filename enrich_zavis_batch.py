#!/usr/bin/env python3
"""Fetch missing Zavis coordinates in resumable batches."""

import argparse
import csv
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

from extract_zavis import parse_provider_detail, safe_fetch

ROOT = Path(__file__).resolve().parent
SOURCE = ROOT / "sources/csv/zavis-providers-enriched.csv"


def enrich(row: dict[str, str]) -> dict[str, str]:
    """Fetch one detail page without retrying unavailable pages."""
    try:
        detail = parse_provider_detail(safe_fetch(row["url"], timeout=20))
    except Exception:
        detail = {"lat": "", "lon": "", "email": ""}
    row.update({"lat": detail["lat"], "lon": detail["lon"], "email": detail["email"]})
    row["maps_url"] = (f'https://www.google.com/maps?q={detail["lat"]},{detail["lon"]}'
                       if detail["lat"] and detail["lon"] else row.get("maps_url", ""))
    return row


def main() -> None:
    """Update one missing-coordinate batch in place."""
    parser = argparse.ArgumentParser()
    parser.add_argument("--offset", type=int, default=0)
    parser.add_argument("--limit", type=int, default=100)
    args = parser.parse_args()
    with SOURCE.open(encoding="utf-8-sig", newline="") as stream:
        rows = list(csv.DictReader(stream))
    missing = [row for row in rows if not row.get("lat") or not row.get("lon")]
    batch = missing[args.offset:args.offset + args.limit]
    with ThreadPoolExecutor(max_workers=2) as pool:
        completed = list(pool.map(enrich, batch))
    by_id = {row["id"]: row for row in completed}
    for index, row in enumerate(rows):
        if row["id"] in by_id:
            rows[index] = by_id[row["id"]]
    with SOURCE.open("w", encoding="utf-8", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=rows[0])
        writer.writeheader()
        writer.writerows(rows)
    located = sum(bool(row.get("lat") and row.get("lon")) for row in completed)
    print(f"Processed {len(completed)} rows; added {located} coordinates; remaining {len(missing) - located}")


if __name__ == "__main__":
    main()
