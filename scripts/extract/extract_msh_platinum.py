"""Extract the UAE MSH Platinum provider table from its public PDF."""

import csv
import re
import subprocess
from pathlib import Path

SOURCE = Path("sources/raw/MSH UAE Platinum Network Reference.pdf")
OUTPUT = Path("sources/networks/MSH UAE Platinum Reference.csv")
TYPES = re.compile(r"^(DENTAL|HOSPITAL|OUTCENTER|PHARMACY|LABORATORY|OPTICAL|CLINIC|MEDICAL CENTER)\s{2,}")
PHONE = re.compile(r"(?:\+?971|0)[\d ()-]{7,}$")


def main() -> None:
    """Extract provider rows, preserving multiline address text."""
    text = subprocess.check_output(["pdftotext", "-layout", str(SOURCE), "-"]).decode()
    rows = []
    current = None
    for raw in text.splitlines():
        line = raw.strip()
        match = TYPES.match(line)
        if match:
            if current:
                rows.append(current)
            parts = re.split(r"\s{2,}", line)
            parts = [part.strip() for part in parts if part.strip()]
            current = {"type": parts[0], "name": parts[1] if len(parts) > 1 else "", "address": "", "city": "", "phone": ""}
            phone = PHONE.search(line)
            if phone:
                current["phone"] = phone.group().strip()
                before = line[:phone.start()].strip()
                fields = re.split(r"\s{2,}", before)
                if len(fields) >= 4:
                    current["city"] = fields[-1]
                    current["address"] = " ".join(fields[2:-1])
                elif len(fields) >= 3:
                    current["address"] = " ".join(fields[2:])
            continue
        if current and line and not line.startswith("This directory") and "MSH PLATINUM" not in line and "TYPE" not in line:
            current["address"] = f"{current['address']} {line}".strip()
    if current:
        rows.append(current)
    rows = [row for row in rows if row["name"] and row["phone"]]
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    with OUTPUT.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=["PROVIDER NAME", "EMIRATE", "PROVIDER TYPE", "AREA", "ADDRESS", "TELEPHONE", "lat", "lon", "SOURCE"])
        writer.writeheader()
        for row in rows:
            writer.writerow({"PROVIDER NAME": row["name"], "EMIRATE": row["city"], "PROVIDER TYPE": row["type"], "AREA": "", "ADDRESS": row["address"], "TELEPHONE": row["phone"], "lat": "", "lon": "", "SOURCE": str(SOURCE)})
    print(f"saved {OUTPUT} ({len(rows)} rows)")


if __name__ == "__main__":
    main()
