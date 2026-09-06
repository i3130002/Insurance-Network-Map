#!/usr/bin/env python3
"""Replace Al Buhaira tier files with rows from the current official locator."""

import csv
from pathlib import Path


ROOT = Path(__file__).resolve().parent
SOURCE = ROOT / "sources/networks/Al Buhaira Medical Network Current.csv"
TIERS = {
    "COMPREHENSIVE": "Al Buhaira Comprehensive.csv",
    "COMPREHENSIVE PLUS": "Al Buhaira Comprehensive Plus.csv",
    "LIMITED": "Al Buhaira Limited.csv",
    "RESTRICTED": "Al Buhaira Restricted.csv",
    "STANDARD": "Al Buhaira Standard.csv",
}
FIELDS = ["PROVIDER NAME", "EMIRATE", "PROVIDER TYPE", "AREA", "ADDRESS", "TELEPHONE"]


def split_current_source() -> None:
    """Write one build-compatible CSV for each current Al Buhaira tier."""
    grouped = {tier: [] for tier in TIERS}
    with SOURCE.open(encoding="utf-8-sig", newline="") as handle:
        for row in csv.DictReader(handle):
            tier = row["NETWORK"].strip().upper()
            if tier in grouped:
                grouped[tier].append({
                    "PROVIDER NAME": row["PROVIDER"].strip(),
                    "EMIRATE": row["EMIRATE"].strip(),
                    "PROVIDER TYPE": row["SPECIALITY"].strip(),
                    "AREA": "",
                    "ADDRESS": row["LOCATION"].strip(),
                    "TELEPHONE": row["TELEPHONE"].strip(),
                })

    for tier, filename in TIERS.items():
        output = ROOT / "sources/networks" / filename
        with output.open("w", encoding="utf-8", newline="") as handle:
            writer = csv.DictWriter(handle, fieldnames=FIELDS)
            writer.writeheader()
            writer.writerows(grouped[tier])
        print(f"{tier}: {len(grouped[tier])}")


if __name__ == "__main__":
    split_current_source()
