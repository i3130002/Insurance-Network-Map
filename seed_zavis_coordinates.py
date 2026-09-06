#!/usr/bin/env python3
"""Seed the full Zavis index with coordinates already captured in the crosswalk."""

import csv
from pathlib import Path

ROOT = Path(__file__).resolve().parent
INDEX = ROOT / "sources/csv/zavis-providers.csv"
CROSSWALK = ROOT / "sources/csv/zavis-provider-matches.csv"
OUTPUT = ROOT / "sources/csv/zavis-providers-enriched.csv"


def main() -> None:
    """Write all Zavis rows with known crosswalk coordinates preserved."""
    with INDEX.open(encoding="utf-8-sig", newline="") as stream:
        rows = list(csv.DictReader(stream))
    with CROSSWALK.open(encoding="utf-8-sig", newline="") as stream:
        known = {row["zavis_id"]: row for row in csv.DictReader(stream) if row["zavis_id"]}
    fields = list(rows[0]) + ["lat", "lon", "email", "maps_url"]
    located = 0
    for row in rows:
        match = known.get(row["id"], {})
        row["lat"], row["lon"] = match.get("zavis_lat", ""), match.get("zavis_lon", "")
        row["email"] = match.get("zavis_email", "")
        row["maps_url"] = match.get("zavis_maps_url", "")
        located += bool(row["lat"] and row["lon"])
    with OUTPUT.open("w", encoding="utf-8", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)
    print(f"Seeded {located} of {len(rows)} Zavis providers with known coordinates")


if __name__ == "__main__":
    main()
