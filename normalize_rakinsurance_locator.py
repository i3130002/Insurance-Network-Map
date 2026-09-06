"""Normalize the current RAKINSURANCE locator response by MedNet tier."""

import csv
import json
from pathlib import Path


RAW = Path("sources/raw/rakinsurance-live-network.json")
OUT = Path("sources/networks")


def normalize() -> None:
    """Write one current CSV per network tier exposed by the locator."""
    rows = json.loads(RAW.read_text())
    tiers = sorted({tier for row in rows for tier in row["field_network_type"]})
    for tier in tiers:
        output = OUT / f"RAK Insurance MedNet {tier.title()} Current.csv"
        with output.open("w", newline="") as handle:
            writer = csv.writer(handle)
            writer.writerow(["PROVIDER NAME", "EMIRATE", "PROVIDER TYPE", "AREA", "ADDRESS", "TELEPHONE"])
            for row in rows:
                if tier not in row["field_network_type"]:
                    continue
                writer.writerow([
                    row.get("field_name", ""),
                    row.get("field_emirate", ""),
                    row.get("field_provider_type", ""),
                    row.get("field_region", ""),
                    row.get("field_provider_address", ""),
                    row.get("field_phone", ""),
                ])


if __name__ == "__main__":
    normalize()
