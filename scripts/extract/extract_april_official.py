"""Extract UAE MedNet tiers from APRIL's official workbook."""
import csv
from pathlib import Path
from zipfile import ZipFile
from xml.etree import ElementTree as ET

M = 'http://schemas.openxmlformats.org/spreadsheetml/2006/main'
R = 'http://schemas.openxmlformats.org/officeDocument/2006/relationships'
P = 'http://schemas.openxmlformats.org/package/2006/relationships'
BOOK = Path('sources/raw/APRIL International Middle East Network August 2026.xlsx')

def main() -> None:
    """Extract the three UAE tier sheets with their official fields."""
    with ZipFile(BOOK) as book:
        strings = ET.fromstring(book.read('xl/sharedStrings.xml'))
        shared = [''.join(t.text or '' for t in item.iter(f'{{{M}}}t'))
                  for item in strings.findall(f'{{{M}}}si')]
        rels = ET.fromstring(book.read('xl/_rels/workbook.xml.rels'))
        targets = {x.attrib['Id']: x.attrib['Target'] for x in rels.findall(f'{{{P}}}Relationship')}
        workbook = ET.fromstring(book.read('xl/workbook.xml'))
        for sheet in workbook.findall(f'{{{M}}}sheets/{{{M}}}sheet'):
            tier = sheet.attrib['name']
            if tier not in {'Premium', 'Classic', 'Green', 'Alternative', 'Dental'}: continue
            path = targets[sheet.attrib[f'{{{R}}}id']]
            path = path if path.startswith('xl/') else f"xl/{path.lstrip('/')}"
            rows = []
            for row in ET.fromstring(book.read(path)).findall(f'.//{{{M}}}row'):
                values = []
                for cell in row.findall(f'{{{M}}}c'):
                    value = cell.find(f'{{{M}}}v')
                    if value is None: values.append(''); continue
                    text = shared[int(value.text)] if cell.attrib.get('t') == 's' else value.text or ''
                    values.append(' '.join(text.split()))
                rows.append(values)
            header = next(i for i, row in enumerate(rows) if row[:2] == ['PROVIDER CODE', 'PROVIDER NAME'])
            fields = ['PROVIDER CODE', 'PROVIDER NAME', 'PROVIDER TYPE', 'EMIRATE', 'REGION', 'ADDRESS', 'LICENSE NUMBER', 'SPECIALITY', 'TELEPHONE']
            output = Path(f'sources/networks/APRIL MedNet {tier} August 2026.csv')
            with output.open('w', newline='', encoding='utf-8') as handle:
                writer = csv.DictWriter(handle, fieldnames=fields + ['NETWORK_TIER', 'SOURCE'])
                writer.writeheader()
                for row in rows[header + 1:]:
                    if len(row) < 2 or not row[1].strip(): continue
                    values = {field: row[i] if i < len(row) else '' for i, field in enumerate(fields)}
                    values.update(NETWORK_TIER=tier, SOURCE='APRIL official workbook August 2026')
                    writer.writerow(values)
            print(tier, sum(1 for _ in output.open(encoding='utf-8')) - 1)

if __name__ == '__main__':
    main()
