#!/usr/bin/env python3
"""Extract the tabular provider rows from the official Cigna EBP PDF."""

import csv
import subprocess
import tempfile
import xml.etree.ElementTree as ET
from pathlib import Path


ROOT = Path(__file__).resolve().parent
PDF = ROOT / "sources/raw/Cigna EBP Network Current.pdf"
OUTPUT = ROOT / "sources/networks/Cigna EBP Value Lite Current.csv"
FIELDS = ["PROVIDER NAME", "EMIRATE", "PROVIDER TYPE", "AREA", "ADDRESS", "TELEPHONE"]


def make_xml() -> ET.Element:
    """Render the PDF as XML so wrapped table cells retain their positions."""
    with tempfile.TemporaryDirectory(prefix="cigna-pdf-") as directory:
        output = Path(directory) / "network.xml"
        subprocess.run(["pdftohtml", "-xml", "-i", "-hidden", str(PDF), str(output)], check=True,
                       stdout=subprocess.DEVNULL, stderr=subprocess.PIPE)
        return ET.parse(output).getroot()


def text_at(node: ET.Element, left: int) -> str:
    """Join text fragments belonging to one table column."""
    values = [item.text.strip() for item in node.findall("text") if abs(int(item.get("left", 0)) - left) <= 8 and item.text]
    return " ".join(values)


def extract() -> list[dict[str, str]]:
    """Extract provider rows, using the network label as the row boundary."""
    rows = []
    for page in make_xml().findall("page"):
        items = list(page.findall("text"))
        anchors = [index for index, item in enumerate(items)
                   if (item.text or "").strip().startswith("Value Lite -")]
        for position, start in enumerate(anchors):
            end = anchors[position + 1] if position + 1 < len(anchors) else len(items)
            section = ET.Element("section")
            for item in items[start:end]:
                section.append(item)
            provider = text_at(section, 154)
            provider_type = text_at(section, 334)
            address = text_at(section, 445)
            emirate = text_at(section, 684)
            phone = text_at(section, 762)
            for label in ("Out-patient clinics", "Dental Clinics", "Pharmacy", "Hospital"):
                if provider_type.startswith(label):
                    remainder = provider_type[len(label):].strip()
                    provider_type = label
                    if remainder and not address:
                        address = remainder
                    break
            if provider and provider_type and emirate:
                rows.append({"PROVIDER NAME": provider, "EMIRATE": emirate, "PROVIDER TYPE": provider_type,
                             "AREA": "", "ADDRESS": address, "TELEPHONE": phone})
    return rows


if __name__ == "__main__":
    records = extract()
    with OUTPUT.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=FIELDS)
        writer.writeheader()
        writer.writerows(records)
    print(f"wrote {len(records)} records to {OUTPUT}")
