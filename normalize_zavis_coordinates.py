#!/usr/bin/env python3
"""Correct deterministic latitude/longitude reversals in the Zavis index."""

import csv
from pathlib import Path

PATH = Path("sources/csv/zavis-providers-enriched.csv")


def is_uae(lat: float, lon: float) -> bool:
    """Return whether coordinates are within the project UAE bounds."""
    return 22 <= lat <= 26.6 and 51 <= lon <= 56.6


def main() -> None:
    """Swap only coordinates that become valid UAE points when reversed."""
    with PATH.open(encoding="utf-8-sig", newline="") as stream:
        rows = list(csv.DictReader(stream))
    fixed = 0
    for row in rows:
        try:
            lat, lon = float(row["lat"]), float(row["lon"])
        except (TypeError, ValueError):
            continue
        if not is_uae(lat, lon) and is_uae(lon, lat):
            row["lat"], row["lon"] = row["lon"], row["lat"]
            row["maps_url"] = f'https://www.google.com/maps?q={row["lat"]},{row["lon"]}'
            fixed += 1
    with PATH.open("w", encoding="utf-8", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=rows[0])
        writer.writeheader()
        writer.writerows(rows)
    print(f"Corrected {fixed} reversed coordinate pairs")


if __name__ == "__main__":
    main()
