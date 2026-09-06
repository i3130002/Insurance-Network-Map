"""Extract the fixed-column provider table from the Allianz reference PDF."""

import csv
import re
import subprocess
from pathlib import Path

from bs4 import BeautifulSoup


SOURCE = Path("sources/raw/Allianz Network List UAE Intermediary Reference.pdf")
OUTPUT = Path("sources/networks/Allianz UAE Intermediary Reference.csv")


def extract_rows() -> list[dict[str, str]]:
    """Return provider rows grouped from the PDF's fixed x-coordinate columns."""
    html = subprocess.check_output(["pdftotext", "-bbox-layout", str(SOURCE), "-"])
    soup = BeautifulSoup(html, "html.parser")
    rows: list[dict[str, str]] = []
    current: dict[str, list[str]] | None = None
    for line in soup.select("line"):
        if not line.get("ymin"):
            continue
        words = [(float(w["xmin"]), w.get_text(" ", strip=True)) for w in line.select("word")]
        if not words:
            continue
        starts_name = any(x < 120 for x, _ in words)
        if starts_name:
            if current and current["name"]:
                rows.append({key: " ".join(value).strip() for key, value in current.items()})
            current = {"name": [], "city": [], "address": [], "email": [], "direct_billing": []}
        if current is None:
            continue
        for x, word in words:
            if x < 270:
                current["name"].append(word)
            elif x < 325:
                current["city"].append(word)
            elif x < 455:
                current["address"].append(word)
            elif x < 620:
                current["email"].append(word)
            else:
                current["direct_billing"].append(word)
    if current and current["name"]:
        rows.append({key: " ".join(value).strip() for key, value in current.items()})
    return [
        row for row in rows
        if row["name"] not in {"Network", "Network in the UAE", "Full Name"}
    ]


def main() -> None:
    """Write the intermediary reference rows and report the count."""
    rows = extract_rows()
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    with OUTPUT.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=rows[0])
        writer.writeheader()
        writer.writerows(rows)
    print(f"saved {OUTPUT} ({len(rows)} rows)")


if __name__ == "__main__":
    main()
