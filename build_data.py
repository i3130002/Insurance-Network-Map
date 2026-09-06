#!/usr/bin/env python3
"""
Build script for Insurance-Network-Map data.

1. Dedupes + validates the merged MOH provider registry (2,583 entries).
2. Emits data/moh-complete.json (full registry) with valid coords only,
   invalid-coord entries preserved in data/needs-geocoding.json.
3. Emits per-insurance-plan JSON files by filtering against the plan's
   emirate coverage. Official network assignments are applied afterward.
4. Emits data/plans.json with plan metadata for the UI.
"""
import csv
import json
import os
import re
from collections import Counter

ROOT = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(ROOT, 'data')
os.makedirs(DATA, exist_ok=True)

# UAE bounding box (generous)
LAT_MIN, LAT_MAX = 22.0, 26.6
LON_MIN, LON_MAX = 51.0, 56.6

EMIRATE_NAMES = {
    'AJM': 'Ajman', 'AUH': 'Abu Dhabi', 'DXB': 'Dubai', 'FUJ': 'Fujairah',
    'RAK': 'Ras Al Khaimah', 'SHJ': 'Sharjah', 'UMQ': 'Umm Al Quwain',
    'ALAIN': 'Al Ain',
}


def norm_name(s: str) -> str:
    """Normalize a provider name for dedup comparison."""
    s = (s or '').upper()
    s = re.sub(r'[^A-Z0-9 ]', ' ', s)
    s = re.sub(r'\s+', ' ', s).strip()
    # Drop legal suffixes and branch noise
    for token in ('LLC', 'L L C', 'SOLE PROPRIETORSHIP', 'BRANCH 01', 'BRANCH 1',
                  'BRANCH 2', 'BRANCH 3', 'BRANCH', 'BR', 'LTD', 'CENTER',
                  'CENTRE'):
        s = re.sub(rf'\b{re.escape(token)}\b', ' ', s)
    return re.sub(r'\s+', ' ', s).strip()


def coord_ok(lat, lon) -> bool:
    try:
        la, lo = float(lat), float(lon)
    except (TypeError, ValueError):
        return False
    return LAT_MIN <= la <= LAT_MAX and LON_MIN <= lo <= LON_MAX


def load_merged() -> list:
    """Load the merged provider registry from this repository."""
    merged_path = os.path.join(ROOT, 'sources', 'merged-registry.json')
    with open(merged_path, encoding='utf-8') as f:
        entries = json.load(f)
    return entries


def load_takafol_plans() -> list[tuple[str, str, str, str, list[str], str]]:
    """Load one selectable plan definition for each imported Takafol network."""
    catalog_path = os.path.join(ROOT, 'sources', 'csv', 'takafol-network-catalog.csv')
    if not os.path.exists(catalog_path):
        return []
    plans = []
    with open(catalog_path, encoding='utf-8-sig', newline='') as f:
        for row in csv.DictReader(f):
            network_id = (row.get('NETWORK_ID') or '').strip()
            network_name = (row.get('NETWORK_NAME') or '').strip()
            if not network_id or not network_name:
                continue
            plan_id = f'takafol-{network_id}'
            plans.append((
                plan_id, f'Takafol Emarat — {network_name}', 'Takafol Emarat',
                'Both', ['AJM', 'AUH', 'DXB', 'FUJ', 'RAK', 'SHJ', 'UMQ'],
                network_id,
            ))
    return plans


def load_zavis_matches() -> dict[int, dict[str, str]]:
    """Load one-time registry-to-Zavis matches for provider enrichment."""
    path = os.path.join(ROOT, 'sources', 'csv', 'zavis-provider-matches.csv')
    if not os.path.exists(path):
        return {}
    with open(path, encoding='utf-8-sig', newline='') as f:
        return {int(row['Index']): row for row in csv.DictReader(f) if row.get('zavis_url')}


def build_registry(entries: list):
    seen = {}
    valid, invalid = [], []
    stats = Counter()

    for e in entries:
        name = (e.get('PROVIDER NAME') or '').strip()
        if not name:
            stats['no_name'] += 1
            continue

        key = (norm_name(name), (e.get('P') or '').strip())
        lat, lon = e.get('lat'), e.get('lon')

        rec = {
            'P': (e.get('P') or '').strip(),
            'PROVIDER TYPE': (e.get('PROVIDER TYPE') or '').strip(),
            'PROVIDER NAME': name,
            'AREA': (e.get('AREA') or '').strip(),
            'ADDRESS': (e.get('ADDRESS') or '').strip(),
            'TELEPHONE': str(e.get('TELEPHONE') or '').strip(),
            'lat': lat,
            'lon': lon,
            'confidence': e.get('confidence') or '',
            'formatted': (e.get('formatted') or '').strip(),
        }

        if key in seen:
            stats['dupes'] += 1
            # Keep the record with better data (coords + longer address)
            prev = seen[key]
            prev_has = coord_ok(prev['lat'], prev['lon'])
            cur_has = coord_ok(lat, lon)
            if cur_has and not prev_has:
                seen[key] = rec
            elif cur_has == prev_has and len(rec['ADDRESS']) > len(prev['ADDRESS']):
                seen[key] = rec
            continue

        seen[key] = rec
        if coord_ok(lat, lon):
            valid.append(rec)
            stats['valid'] += 1
        else:
            invalid.append(rec)
            stats['invalid'] += 1

    # Re-index
    out = []
    for i, rec in enumerate(seen.values(), 1):
        rec = dict(rec)
        rec['Index'] = i
        out.append(rec)
    valid = [rec for rec in out if coord_ok(rec['lat'], rec['lon'])]
    invalid = [rec for rec in out if not coord_ok(rec['lat'], rec['lon'])]
    stats['valid'] = len(valid)
    stats['invalid'] = len(invalid)
    return out, stats


PLANS = [
    # (plan_id, display name, insurer, coverage, emirate codes)
    ('adnic-platinum',     'ADNIC Platinum',             'ADNIC',              'Both',       ['AUH'], 'ADNIC Platinum Network August 2026'),
    ('adnic-gold',         'ADNIC Gold',                 'ADNIC',              'Both',       ['AUH'], 'ADNIC Gold Network August 2026'),
    ('adnic-gold-plus',    'ADNIC Gold Plus',            'ADNIC',              'Both',       ['AUH'], 'ADNIC Gold Plus Network August 2026'),
    ('adnic-silver',       'ADNIC Silver',               'ADNIC',              'Both',       ['AUH'], 'ADNIC Silver Network August 2026'),
    ('adnic-bronze',       'ADNIC Bronze',              'ADNIC',              'Both',       ['AUH'], 'ADNIC Bronze Network August 2026'),
    ('adnic-blue',         'ADNIC Blue',                'ADNIC',              'Both',       ['AUH'], 'ADNIC Blue Network August 2026'),
    ('adnic-hala',         'ADNIC Hala',                'ADNIC',              'Both',       ['AUH'], 'ADNIC Hala Network August 2026'),
    ('adnic-platinum-live', 'ADNIC Platinum Live',      'ADNIC Platinum Live', 'Both', ['AJM', 'AUH', 'DXB', 'FUJ', 'RAK', 'SHJ', 'UMQ']),
    ('adnic-g-plus-live',   'ADNIC G Plus Live',         'ADNIC G Plus Live', 'Both', ['AJM', 'AUH', 'DXB', 'FUJ', 'RAK', 'SHJ', 'UMQ']),
    ('adnic-gold-live',     'ADNIC Gold Live',           'ADNIC Gold Live', 'Both', ['AJM', 'AUH', 'DXB', 'FUJ', 'RAK', 'SHJ', 'UMQ']),
    ('adnic-silver-live',   'ADNIC Silver Live',         'ADNIC Silver Live', 'Both', ['AJM', 'AUH', 'DXB', 'FUJ', 'RAK', 'SHJ', 'UMQ']),
    ('adnic-bronze-live',   'ADNIC Bronze Live',         'ADNIC Bronze Live', 'Both', ['AJM', 'AUH', 'DXB', 'FUJ', 'RAK', 'SHJ', 'UMQ']),
    ('adnic-asasi-live',    'ADNIC Asasi Live',          'ADNIC Asasi Live', 'Both', ['AJM', 'AUH', 'DXB', 'FUJ', 'RAK', 'SHJ', 'UMQ']),
    ('adnic-blue-live',     'ADNIC Blue Live',           'ADNIC Blue Live', 'Both', ['AJM', 'AUH', 'DXB', 'FUJ', 'RAK', 'SHJ', 'UMQ']),
    ('adnic-hala-live',     'ADNIC Hala Live',           'ADNIC Hala Live', 'Both', ['AJM', 'AUH', 'DXB', 'FUJ', 'RAK', 'SHJ', 'UMQ']),
    ('adnic-enhanced-live', 'ADNIC Enhanced Network Live', 'ADNIC Enhanced Live', 'Both', ['AJM', 'AUH', 'DXB', 'FUJ', 'RAK', 'SHJ', 'UMQ']),
    ('daman-advanced',     'Daman Advanced',             'Daman Insurance',     'Both',       ['AJM', 'AUH', 'DXB', 'FUJ', 'RAK', 'SHJ', 'UMQ'], 'Daman Insurance Advanced'),
    ('daman-royal-ww',      'Daman Royal WW',              'Daman Insurance Royal WW', 'Both', ['AJM', 'AUH', 'DXB', 'FUJ', 'RAK', 'SHJ', 'UMQ'], 'Daman Insurance Royal WW'),
    ('daman-royal-ww-exc-us-can', 'Daman Royal WW exc. US CAN', 'Daman Insurance Royal WW exc US CAN', 'Both', ['AJM', 'AUH', 'DXB', 'FUJ', 'RAK', 'SHJ', 'UMQ'], 'Daman Insurance Royal WW exc US CAN'),
    ('daman-grand',         'Daman Grand',                 'Daman Insurance Grand', 'Both', ['AJM', 'AUH', 'DXB', 'FUJ', 'RAK', 'SHJ', 'UMQ'], 'Daman Insurance Grand'),
    ('daman-grand-aw-asia-2', 'Daman Grand AW Asia 2',       'Daman Insurance Grand AW Asia 2', 'Both', ['AJM', 'AUH', 'DXB', 'FUJ', 'RAK', 'SHJ', 'UMQ'], 'Daman Insurance Grand AW Asia 2'),
    ('daman-grand-ww',      'Daman Grand WW',              'Daman Insurance Grand WW', 'Both', ['AJM', 'AUH', 'DXB', 'FUJ', 'RAK', 'SHJ', 'UMQ'], 'Daman Insurance Grand WW'),
    ('daman-grand-ww-exc-us', 'Daman Grand WW exc. US',     'Daman Insurance Grand WW exc. US', 'Both', ['AJM', 'AUH', 'DXB', 'FUJ', 'RAK', 'SHJ', 'UMQ'], 'Daman Insurance Grand WW exc US'),
    ('daman-key',           'Daman Key',                   'Daman Insurance Key', 'Both', ['AJM', 'AUH', 'DXB', 'FUJ', 'RAK', 'SHJ', 'UMQ'], 'Daman Insurance Key'),
    ('daman-narrow-nw',     'Daman Narrow NW',              'Daman Insurance Narrow NW', 'Both', ['AJM', 'AUH', 'DXB', 'SHJ'], 'Daman Insurance Narrow NW'),
    ('daman-comprehensive-5', 'Daman Comprehensive 5',     'Daman Insurance Comprehensive 5', 'Both', ['AJM', 'AUH', 'DXB', 'FUJ', 'RAK', 'SHJ', 'UMQ'], 'Daman Insurance Comprehensive 5'),
    ('daman-supreme-ww',   'Daman Supreme WW',              'Daman Insurance Supreme WW', 'Both', ['AJM', 'AUH', 'DXB', 'FUJ', 'RAK', 'SHJ', 'UMQ'], 'Daman Insurance Supreme WW'),
    ('daman-supreme-ww-exc-us', 'Daman Supreme WW exc. US', 'Daman Insurance Supreme WW exc US', 'Both', ['AJM', 'AUH', 'DXB', 'FUJ', 'RAK', 'SHJ', 'UMQ'], 'Daman Insurance Supreme WW exc US'),
    ('daman-supreme-ww-exc-us-can-eur', 'Daman Supreme WW exc. US CAN EUR', 'Daman Insurance Supreme WW exc US CAN EUR', 'Both', ['AJM', 'AUH', 'DXB', 'FUJ', 'RAK', 'SHJ', 'UMQ'], 'Daman Insurance Supreme WW exc US CAN EUR'),
    ('daman-visitors',      'Daman Visitors Plan',           'Daman Insurance Visitors Plan', 'Both', ['AJM', 'AUH', 'DXB', 'FUJ', 'RAK', 'SHJ', 'UMQ'], 'Daman Insurance Visitors Plan'),
    ('daman-flexi-auh',     'Daman Flexi Abu Dhabi',           'Daman Insurance Flexi', 'Both', ['AUH'], 'Daman Insurance Flexi'),
    ('daman-primary-sea',   'Daman Primary SEA ISC AC',        'Daman Insurance Primary SEA ISC AC', 'Both', ['AJM', 'AUH', 'DXB', 'FUJ', 'RAK', 'SHJ', 'UMQ'], 'Daman Insurance Primary SEA ISC AC'),
    ('daman-advanced-sea',   'Daman Advanced SEA ISC AC',       'Daman Insurance Advanced SEA ISC AC', 'Both', ['AJM', 'AUH', 'DXB', 'FUJ', 'RAK', 'SHJ', 'UMQ'], 'Daman Insurance Advanced SEA ISC AC'),
    ('daman-key-sea',        'Daman Key SEA ISC AC',            'Daman Insurance Key SEA ISC AC', 'Both', ['AJM', 'AUH', 'DXB', 'FUJ', 'RAK', 'SHJ', 'UMQ'], 'Daman Insurance Key SEA ISC AC'),
    ('daman-grand-sea',      'Daman Grand SEA ISC AC',          'Daman Insurance Grand SEA ISC AC', 'Both', ['AJM', 'AUH', 'DXB', 'FUJ', 'RAK', 'SHJ', 'UMQ'], 'Daman Insurance Grand SEA ISC AC'),
    ('daman-abu-dhabi-plan', 'Daman Abu Dhabi Plan',            'Daman Insurance Abu Dhabi Plan', 'Both', ['AUH'], 'Daman Insurance Abu Dhabi Plan'),
    ('daman-al-kamal-auh',  'Daman Al Kamal Abu Dhabi',         'Daman Insurance Al Kamal', 'Both', ['AUH'], 'Daman Insurance Al Kamal'),
    ('dubai-insurance-dubaicare', 'Dubai Insurance DubaiCare', 'Dubai Insurance', 'Both', ['AJM', 'AUH', 'DXB', 'FUJ', 'RAK', 'SHJ', 'UMQ'], 'Dubai Insurance DubaiCare'),
    ('dubai-insurance-basic', 'Dubai Insurance Basic Individual', 'Dubai Insurance', 'Both', ['DXB'], 'Dubai Insurance DubaiCare'),
    ('dubai-insurance-flexi', 'Dubai Insurance Flexi Individual', 'Dubai Insurance', 'Both', ['AUH'], 'Dubai Insurance DubaiCare'),
    ('dubai-insurance-ne', 'Dubai Insurance NE Individual', 'Dubai Insurance', 'Both', ['AJM', 'FUJ', 'RAK', 'SHJ', 'UMQ'], 'Dubai Insurance DubaiCare'),
    ('dubai-care-n2-exclusive', 'Dubai Care N2 Exclusive', 'Dubai Care', 'Both', ['AJM', 'AUH', 'DXB', 'FUJ', 'RAK', 'SHJ', 'UMQ'], 'Dubai Care N2 Exclusive'),
    ('dubai-care-n2', 'Dubai Care N2', 'Dubai Care', 'Both', ['AJM', 'AUH', 'DXB', 'FUJ', 'RAK', 'SHJ', 'UMQ'], 'Dubai Care N2'),
    ('dubai-care-n3', 'Dubai Care N3', 'Dubai Care', 'Both', ['AJM', 'AUH', 'DXB', 'FUJ', 'RAK', 'SHJ', 'UMQ'], 'Dubai Care N3'),
    ('dubai-care-n4', 'Dubai Care N4', 'Dubai Care', 'Both', ['AJM', 'AUH', 'DXB', 'FUJ', 'RAK', 'SHJ', 'UMQ'], 'Dubai Care N4'),
    ('dubai-care-n5-enhanced', 'Dubai Care N5 Enhanced', 'Dubai Care', 'Both', ['AJM', 'AUH', 'DXB', 'FUJ', 'RAK', 'SHJ', 'UMQ'], 'Dubai Care N5 Enhanced'),
    ('dubai-care-enhanced-n5-op', 'Dubai Care Enhanced N5 OP', 'Dubai Care', 'Outpatient', ['AJM', 'AUH', 'DXB', 'FUJ', 'RAK', 'SHJ', 'UMQ'], 'Dubai Care Enhanced N5 OP'),
    ('dubai-care-n5-op', 'Dubai Care N5 OP', 'Dubai Care', 'Outpatient', ['AJM', 'AUH', 'DXB', 'FUJ', 'RAK', 'SHJ', 'UMQ'], 'Dubai Care N5 OP'),
    ('dubai-care-n5-ip', 'Dubai Care N5 IP', 'Dubai Care', 'Inpatient', ['AJM', 'AUH', 'DXB', 'FUJ', 'RAK', 'SHJ', 'UMQ'], 'Dubai Care N5 IP'),
    ('al-sagr-nextcare', 'Al Sagr NextCare Network', 'Al Sagr Insurance', 'Both', ['AJM', 'AUH', 'DXB', 'FUJ', 'RAK', 'SHJ', 'UMQ'], 'Al Sagr NextCare August 2023'),
    ('al-sagr-nas-value', 'Al Sagr NAS Value', 'Al Sagr Insurance', 'Both', ['AJM', 'AUH', 'DXB', 'FUJ', 'RAK', 'SHJ', 'UMQ'], 'Al Sagr NAS Value Value Lite'),
    ('al-sagr-nas-value-lite', 'Al Sagr NAS Value Lite', 'Al Sagr Insurance', 'Both', ['AJM', 'AUH', 'DXB', 'FUJ', 'RAK', 'SHJ', 'UMQ'], 'Al Sagr NAS Value Value Lite'),
    ('al-sagr-nas-comprehensive', 'Al Sagr NAS Comprehensive', 'Al Sagr Insurance', 'Both', ['AJM', 'AUH', 'DXB', 'FUJ', 'RAK', 'SHJ', 'UMQ'], 'Al Sagr NAS Comprehensive GN RN SRN WR'),
    ('al-sagr-value', 'Al Sagr Value Network', 'Al Sagr Insurance', 'Both', ['AJM', 'AUH', 'DXB', 'FUJ', 'RAK', 'SHJ', 'UMQ'], 'Al Sagr Value July 2023'),
    ('al-sagr-value-lite', 'Al Sagr Value Lite Network', 'Al Sagr Insurance', 'Both', ['AJM', 'AUH', 'DXB', 'FUJ', 'RAK', 'SHJ', 'UMQ'], 'Al Sagr Value Lite July 2023'),
    ('qic-value-lite-dubai-ip', 'QIC Value Lite Dubai Inpatient', 'QIC UAE', 'Inpatient', ['DXB'], 'QIC Value Lite Network August 2022'),
    ('qic-medical-individual', 'QIC Medical Individual Al Madallah RN4', 'QIC UAE', 'Both', ['AJM', 'AUH', 'DXB', 'FUJ', 'RAK', 'SHJ', 'UMQ'], 'Takaful Emarat Al Madallah Access RN4 Current'),
    ('alliance-rn3', 'Alliance RN3 Network', 'Alliance Insurance', 'Inpatient', ['AJM', 'AUH', 'DXB', 'FUJ', 'RAK', 'SHJ', 'UMQ'], 'Alliance RN3 Networks'),
    ('alliance-rn2', 'Alliance RN2 Network', 'Alliance Insurance', 'Inpatient', ['AJM', 'AUH', 'DXB', 'FUJ', 'RAK', 'SHJ', 'UMQ'], 'Alliance RN2'),
    ('alliance-rn', 'Alliance RN Network', 'Alliance Insurance', 'Inpatient', ['AJM', 'AUH', 'DXB', 'FUJ', 'RAK', 'SHJ', 'UMQ'], 'Alliance RN'),
    ('alliance-gn', 'Alliance GN Network', 'Alliance Insurance', 'Both', ['AJM', 'AUH', 'DXB', 'FUJ', 'RAK', 'SHJ', 'UMQ'], 'Alliance GN'),
    ('alliance-gn-plus', 'Alliance GN Plus Network', 'Alliance Insurance', 'Both', ['AJM', 'AUH', 'DXB', 'FUJ', 'RAK', 'SHJ', 'UMQ'], 'Alliance GN Plus'),
    ('alain-nas-provider-network', 'Al Ain Insurance NAS Provider Network', 'Al Ain Insurance', 'Both', ['AJM', 'AUH', 'DXB', 'FUJ', 'RAK', 'SHJ', 'UMQ'], 'Al Ain Insurance NAS Provider Network'),
    ('al-buhaira-comprehensive', 'Al Buhaira Comprehensive', 'Al Buhaira National Insurance', 'Both', ['AJM', 'AUH', 'DXB', 'FUJ', 'RAK', 'SHJ', 'UMQ'], 'Al Buhaira Comprehensive'),
    ('al-buhaira-comprehensive-plus', 'Al Buhaira Comprehensive Plus', 'Al Buhaira National Insurance', 'Both', ['AJM', 'AUH', 'DXB', 'FUJ', 'RAK', 'SHJ', 'UMQ'], 'Al Buhaira Comprehensive Plus'),
    ('al-buhaira-limited', 'Al Buhaira Limited', 'Al Buhaira National Insurance', 'Both', ['AJM', 'AUH', 'DXB', 'FUJ', 'RAK', 'SHJ', 'UMQ'], 'Al Buhaira Limited'),
    ('al-buhaira-restricted', 'Al Buhaira Restricted', 'Al Buhaira National Insurance', 'Both', ['AJM', 'AUH', 'DXB', 'FUJ', 'RAK', 'SHJ', 'UMQ'], 'Al Buhaira Restricted'),
    ('al-buhaira-standard', 'Al Buhaira Standard', 'Al Buhaira National Insurance', 'Both', ['AJM', 'AUH', 'DXB', 'FUJ', 'RAK', 'SHJ', 'UMQ'], 'Al Buhaira Standard'),
    ('al-dhafra-classic-seha-plus', 'Al Dhafra Classic Network SEHA Plus', 'Al Dhafra Insurance', 'Both', ['AJM', 'AUH', 'DXB', 'FUJ', 'RAK', 'SHJ', 'UMQ'], 'Al Dhafra Classic Network SEHA Plus'),
    ('al-dhafra-classic-wrn', 'Al Dhafra Classic Network WRN', 'Al Dhafra Insurance', 'Both', ['AJM', 'AUH', 'DXB', 'FUJ', 'RAK', 'SHJ', 'UMQ'], 'Al Dhafra Classic Network WRN'),
    ('al-dhafra-comprehensive', 'Al Dhafra Comprehensive Network', 'Al Dhafra Insurance', 'Both', ['AJM', 'AUH', 'DXB', 'FUJ', 'RAK', 'SHJ', 'UMQ'], 'Al Dhafra Comprehensive'),
    ('al-dhafra-comprehensive-seha-plus', 'Al Dhafra Comprehensive Network SEHA Plus', 'Al Dhafra Insurance', 'Both', ['AJM', 'AUH', 'DXB', 'FUJ', 'RAK', 'SHJ', 'UMQ'], 'Al Dhafra Comprehensive SEHA Plus'),
    ('al-dhafra-executive', 'Al Dhafra Executive Network', 'Al Dhafra Insurance', 'Both', ['AJM', 'AUH', 'DXB', 'FUJ', 'RAK', 'SHJ', 'UMQ'], 'Al Dhafra Executive'),
    ('al-dhafra-executive-seha-plus', 'Al Dhafra Executive Network SEHA Plus', 'Al Dhafra Insurance', 'Both', ['AJM', 'AUH', 'DXB', 'FUJ', 'RAK', 'SHJ', 'UMQ'], 'Al Dhafra Executive SEHA Plus'),
    ('al-dhafra-restricted', 'Al Dhafra Restricted Network', 'Al Dhafra Insurance', 'Both', ['AJM', 'AUH', 'DXB', 'FUJ', 'RAK', 'SHJ', 'UMQ'], 'Al Dhafra Restricted'),
    ('al-dhafra-restricted-seha-plus', 'Al Dhafra Restricted Network SEHA Plus', 'Al Dhafra Insurance', 'Both', ['AJM', 'AUH', 'DXB', 'FUJ', 'RAK', 'SHJ', 'UMQ'], 'Al Dhafra Restricted SEHA Plus'),
    ('al-dhafra-premier', 'Al Dhafra Premier Network', 'Al Dhafra Insurance', 'Both', ['AJM', 'AUH', 'DXB', 'FUJ', 'RAK', 'SHJ', 'UMQ'], 'Al Dhafra Premier'),
    ('al-dhafra-premier-seha-plus', 'Al Dhafra Premier Network SEHA Plus', 'Al Dhafra Insurance', 'Both', ['AJM', 'AUH', 'DXB', 'FUJ', 'RAK', 'SHJ', 'UMQ'], 'Al Dhafra Premier SEHA Plus'),
    ('axa-star-network', 'AXA Gulf UAE Star Network', 'AXA Gulf', 'Both', ['AJM', 'AUH', 'DXB', 'FUJ', 'RAK', 'SHJ', 'UMQ'], 'AXA Gulf UAE Star Network'),
    ('axa-star-plus-network', 'AXA Gulf UAE Star Plus Network', 'AXA Gulf', 'Both', ['AJM', 'AUH', 'DXB', 'FUJ', 'RAK', 'SHJ', 'UMQ'], 'AXA Gulf UAE Star Plus Network'),
    ('axa-diamond-network', 'AXA Gulf UAE Diamond Network', 'AXA Gulf', 'Both', ['AJM', 'AUH', 'DXB', 'FUJ', 'RAK', 'SHJ', 'UMQ'], 'AXA Gulf UAE Diamond Network'),
    ('nextcare-consolidated-aug-2026', 'NextCare UAE Consolidated August 2026', 'NextCare', 'Both', ['AJM', 'AUH', 'DXB', 'FUJ', 'RAK', 'SHJ', 'UMQ'], 'NextCare Consolidated UAE August 2026'),
    ('nextcare-teleconsultation-aug-2026', 'NextCare Teleconsultation Providers August 2026', 'NextCare', 'Outpatient', ['AJM', 'AUH', 'DXB', 'FUJ', 'RAK', 'SHJ', 'UMQ'], 'NextCare Teleconsultation Providers August 2026'),
    ('salama-medishield-nextcare', 'Salama MediShield NextCare', 'Salama Insurance', 'Both', ['AJM', 'AUH', 'DXB', 'FUJ', 'RAK', 'SHJ', 'UMQ'], 'NextCare Consolidated UAE August 2026'),
    ('salama-gold', 'Salama Gold', 'Salama Insurance', 'Both', ['AJM', 'AUH', 'DXB', 'FUJ', 'RAK', 'SHJ', 'UMQ'], 'Orient Insurance MedNet Gold'),
    ('salama-silver-premium', 'Salama Silver Premium', 'Salama Insurance', 'Both', ['AJM', 'AUH', 'DXB', 'FUJ', 'RAK', 'SHJ', 'UMQ'], 'Orient Insurance MedNet Silver Premium'),
    ('salama-silver-classic', 'Salama Silver Classic', 'Salama Insurance', 'Both', ['AJM', 'AUH', 'DXB', 'FUJ', 'RAK', 'SHJ', 'UMQ'], 'Orient Insurance MedNet Silver Classic'),
    ('salama-green', 'Salama Green', 'Salama Insurance', 'Both', ['AJM', 'AUH', 'DXB', 'FUJ', 'RAK', 'SHJ', 'UMQ'], 'Orient Insurance MedNet Green'),
    ('salama-silk-road', 'Salama Silk Road', 'Salama Insurance', 'Both', ['AJM', 'AUH', 'DXB', 'FUJ', 'RAK', 'SHJ', 'UMQ'], 'Orient Insurance MedNet Silk Road OP'),
    ('methaq-nextcare', 'Methaq NextCare Network', 'Methaq Takaful', 'Both', ['AJM', 'AUH', 'DXB', 'FUJ', 'RAK', 'SHJ', 'UMQ'], 'NextCare Consolidated UAE August 2026'),
    ('fidelity-nextcare-gn-plus', 'Fidelity United NextCare GN+', 'Fidelity United', 'Both', ['AJM', 'AUH', 'DXB', 'FUJ', 'RAK', 'SHJ', 'UMQ'], 'Fidelity United NextCare GN Plus'),
    ('fidelity-nextcare-gn', 'Fidelity United NextCare GN', 'Fidelity United', 'Both', ['AJM', 'AUH', 'DXB', 'FUJ', 'RAK', 'SHJ', 'UMQ'], 'Fidelity United NextCare GN'),
    ('fidelity-nextcare-rn', 'Fidelity United NextCare RN', 'Fidelity United', 'Both', ['AJM', 'AUH', 'DXB', 'FUJ', 'RAK', 'SHJ', 'UMQ'], 'Fidelity United NextCare RN'),
    ('fidelity-nextcare-rn2', 'Fidelity United NextCare RN2', 'Fidelity United', 'Both', ['AJM', 'AUH', 'DXB', 'FUJ', 'RAK', 'SHJ', 'UMQ'], 'Fidelity United NextCare RN2'),
    ('fidelity-nextcare-rn3', 'Fidelity United NextCare RN3', 'Fidelity United', 'Both', ['AJM', 'AUH', 'DXB', 'FUJ', 'RAK', 'SHJ', 'UMQ'], 'Fidelity United NextCare RN3'),
    ('fidelity-nextcare-rn-enhanced', 'Fidelity United NextCare RN Enhanced', 'Fidelity United', 'Both', ['AJM', 'AUH', 'DXB', 'FUJ', 'RAK', 'SHJ', 'UMQ'], 'Fidelity United NextCare RN Enhanced'),
    ('fidelity-nextcare-pcp', 'Fidelity United NextCare PCP', 'Fidelity United', 'Outpatient', ['AJM', 'AUH', 'DXB', 'FUJ', 'RAK', 'SHJ', 'UMQ'], 'Fidelity United NextCare PCP'),
    ('fidelity-nextcare-pcp-auh', 'Fidelity United NextCare PCP AUH', 'Fidelity United', 'Outpatient', ['AUH'], 'Fidelity United NextCare PCP AUH'),
    ('fidelity-nextcare-phm', 'Fidelity United NextCare PHM', 'Fidelity United', 'Both', ['AJM', 'AUH', 'DXB', 'FUJ', 'RAK', 'SHJ', 'UMQ'], 'Fidelity United NextCare PHM'),
    ('rak-mednet-gold', 'RAK Insurance MedNet Gold', 'RAK Insurance', 'Both', ['AJM', 'AUH', 'DXB', 'FUJ', 'RAK', 'SHJ', 'UMQ'], 'RAK Insurance MedNet Gold'),
    ('rak-mednet-silver-premium', 'RAK Insurance MedNet Silver Premium', 'RAK Insurance', 'Both', ['AJM', 'AUH', 'DXB', 'FUJ', 'RAK', 'SHJ', 'UMQ'], 'RAK Insurance MedNet Silver Premium'),
    ('rak-mednet-silver-classic', 'RAK Insurance MedNet Silver Classic', 'RAK Insurance', 'Both', ['AJM', 'AUH', 'DXB', 'FUJ', 'RAK', 'SHJ', 'UMQ'], 'RAK Insurance MedNet Silver Classic'),
    ('rak-mednet-green', 'RAK Insurance MedNet Green', 'RAK Insurance', 'Both', ['AJM', 'AUH', 'DXB', 'FUJ', 'RAK', 'SHJ', 'UMQ'], 'RAK Insurance MedNet Green'),
    ('rak-mednet-silk-road-ip', 'RAK Insurance MedNet Silk Road IP', 'RAK Insurance', 'Inpatient', ['AJM', 'AUH', 'DXB', 'FUJ', 'RAK', 'SHJ', 'UMQ'], 'RAK Insurance MedNet Silk Road Ip'),
    ('rak-mednet-silk-road-op', 'RAK Insurance MedNet Silk Road OP', 'RAK Insurance', 'Outpatient', ['AJM', 'AUH', 'DXB', 'FUJ', 'RAK', 'SHJ', 'UMQ'], 'RAK Insurance MedNet Silk Road Op'),
    ('rak-mednet-emerald', 'RAK Insurance MedNet Emerald', 'RAK Insurance', 'Both', ['AJM', 'AUH', 'DXB', 'FUJ', 'RAK', 'SHJ', 'UMQ'], 'RAK Insurance MedNet Emerald'),
    ('rak-mednet-pearl', 'RAK Insurance MedNet Pearl', 'RAK Insurance', 'Both', ['AJM', 'AUH', 'DXB', 'FUJ', 'RAK', 'SHJ', 'UMQ'], 'RAK Insurance MedNet Pearl'),
    ('rak-mednet-gold-current', 'RAK Insurance MedNet Gold Current', 'RAK Insurance', 'Both', ['AJM', 'AUH', 'DXB', 'FUJ', 'RAK', 'SHJ', 'UMQ'], 'RAK Insurance MedNet Gold Current'),
    ('rak-mednet-silver-premium-current', 'RAK Insurance MedNet Silver Premium Current', 'RAK Insurance', 'Both', ['AJM', 'AUH', 'DXB', 'FUJ', 'RAK', 'SHJ', 'UMQ'], 'RAK Insurance MedNet Silver Premium Current'),
    ('rak-mednet-silver-classic-current', 'RAK Insurance MedNet Silver Classic Current', 'RAK Insurance', 'Both', ['AJM', 'AUH', 'DXB', 'FUJ', 'RAK', 'SHJ', 'UMQ'], 'RAK Insurance MedNet Silver Classic Current'),
    ('rak-mednet-green-current', 'RAK Insurance MedNet Green Current', 'RAK Insurance', 'Both', ['AJM', 'AUH', 'DXB', 'FUJ', 'RAK', 'SHJ', 'UMQ'], 'RAK Insurance MedNet Green Current'),
    ('rak-mednet-silk-road-ip-current', 'RAK Insurance MedNet Silk Road IP Current', 'RAK Insurance', 'Inpatient', ['AJM', 'AUH', 'DXB', 'FUJ', 'RAK', 'SHJ', 'UMQ'], 'RAK Insurance MedNet Silk Road Ip Current'),
    ('rak-mednet-silk-road-op-current', 'RAK Insurance MedNet Silk Road OP Current', 'RAK Insurance', 'Outpatient', ['AJM', 'AUH', 'DXB', 'FUJ', 'RAK', 'SHJ', 'UMQ'], 'RAK Insurance MedNet Silk Road Op Current'),
    ('rak-mednet-emerald-current', 'RAK Insurance MedNet Emerald Current', 'RAK Insurance', 'Both', ['AJM', 'AUH', 'DXB', 'FUJ', 'RAK', 'SHJ', 'UMQ'], 'RAK Insurance MedNet Emerald Current'),
    ('rak-mednet-pearl-current', 'RAK Insurance MedNet Pearl Current', 'RAK Insurance', 'Both', ['AJM', 'AUH', 'DXB', 'FUJ', 'RAK', 'SHJ', 'UMQ'], 'RAK Insurance MedNet Pearl Current'),
    ('metlife-ebp', 'MetLife EBP Network', 'MetLife UAE', 'Both', ['AJM', 'AUH', 'DXB', 'FUJ', 'RAK', 'SHJ', 'UMQ'], 'MetLife EBP Network'),
    ('msh-uae-platinum-reference', 'MSH UAE Platinum Reference Network', 'MSH International', 'Both', ['AJM', 'AUH', 'DXB', 'FUJ', 'RAK', 'SHJ', 'UMQ'], 'MSH UAE Platinum Reference'),
    ('mednet-uae-reference', 'MedNet UAE Locator Reference 2026', 'MedNet UAE', 'Both', ['AJM', 'AUH', 'DXB', 'FUJ', 'RAK', 'SHJ', 'UMQ'], 'MedNet UAE Locator July 2026'),
    ('medgulf-assigned-providers-current', 'MEDGULF UAE Assigned Providers Reference 2026', 'MEDGULF UAE', 'Both', ['AJM', 'AUH', 'DXB', 'FUJ', 'RAK', 'SHJ', 'UMQ'], 'MEDGULF Assigned Providers UAE Current'),
    ('adnic-platinum-live-current', 'ADNIC Platinum Live 2026', 'ADNIC', 'Both', ['AJM', 'AUH', 'DXB', 'FUJ', 'RAK', 'SHJ', 'UMQ'], 'ADNIC Platinum Live'),
    ('adnic-g-plus-live-current', 'ADNIC G Plus Live 2026', 'ADNIC', 'Both', ['AJM', 'AUH', 'DXB', 'FUJ', 'RAK', 'SHJ', 'UMQ'], 'ADNIC G Plus Live'),
    ('adnic-gold-live-current', 'ADNIC Gold Live 2026', 'ADNIC', 'Both', ['AJM', 'AUH', 'DXB', 'FUJ', 'RAK', 'SHJ', 'UMQ'], 'ADNIC Gold Live'),
    ('adnic-silver-live-current', 'ADNIC Silver Live 2026', 'ADNIC', 'Both', ['AJM', 'AUH', 'DXB', 'FUJ', 'RAK', 'SHJ', 'UMQ'], 'ADNIC Silver Live'),
    ('adnic-bronze-live-current', 'ADNIC Bronze Live 2026', 'ADNIC', 'Both', ['AJM', 'AUH', 'DXB', 'FUJ', 'RAK', 'SHJ', 'UMQ'], 'ADNIC Bronze Live'),
    ('adnic-asasi-live-current', 'ADNIC Asasi Live 2026', 'ADNIC', 'Both', ['AJM', 'AUH', 'DXB', 'FUJ', 'RAK', 'SHJ', 'UMQ'], 'ADNIC Asasi Live'),
    ('adnic-blue-live-current', 'ADNIC Blue Live 2026', 'ADNIC', 'Both', ['AJM', 'AUH', 'DXB', 'FUJ', 'RAK', 'SHJ', 'UMQ'], 'ADNIC Blue Live'),
    ('adnic-hala-live-current', 'ADNIC Hala Live 2026', 'ADNIC', 'Both', ['AJM', 'AUH', 'DXB', 'FUJ', 'RAK', 'SHJ', 'UMQ'], 'ADNIC Hala Live'),
    ('adnic-enhanced-live-current', 'ADNIC Enhanced Live 2026', 'ADNIC', 'Both', ['AJM', 'AUH', 'DXB', 'FUJ', 'RAK', 'SHJ', 'UMQ'], 'ADNIC Enhanced Live'),
    ('april-mednet-premium-current', 'APRIL International MedNet Premium 2026', 'APRIL International', 'Both', ['AJM', 'AUH', 'DXB', 'FUJ', 'RAK', 'SHJ', 'UMQ'], 'APRIL MedNet Premium August 2026'),
    ('april-mednet-classic-current', 'APRIL International MedNet Classic 2026', 'APRIL International', 'Both', ['AJM', 'AUH', 'DXB', 'FUJ', 'RAK', 'SHJ', 'UMQ'], 'APRIL MedNet Classic August 2026'),
    ('april-mednet-green-current', 'APRIL International MedNet Green 2026', 'APRIL International', 'Both', ['AJM', 'AUH', 'DXB', 'FUJ', 'RAK', 'SHJ', 'UMQ'], 'APRIL MedNet Green August 2026'),
    ('april-mednet-alternative-current', 'APRIL International MedNet Alternative 2026', 'APRIL International', 'Both', ['AJM', 'AUH', 'DXB', 'FUJ', 'RAK', 'SHJ', 'UMQ'], 'APRIL MedNet Alternative August 2026'),
    ('april-mednet-dental-current', 'APRIL International MedNet Dental 2026', 'APRIL International', 'Outpatient', ['AJM', 'AUH', 'DXB', 'FUJ', 'RAK', 'SHJ', 'UMQ'], 'APRIL MedNet Dental August 2026'),
    ('ecare-classic-current', 'E-Care Classic Network 2026', 'E-Care International', 'Both', ['AJM', 'AUH', 'DXB', 'FUJ', 'RAK', 'SHJ', 'UMQ'], 'E-Care Classic Current'),
    ('ecare-blue-current', 'E-Care Blue Network 2026', 'E-Care International', 'Both', ['AJM', 'AUH', 'DXB', 'FUJ', 'RAK', 'SHJ', 'UMQ'], 'E-Care Blue Current'),
    ('ecare-green-current', 'E-Care Green Network 2026', 'E-Care International', 'Both', ['AJM', 'AUH', 'DXB', 'FUJ', 'RAK', 'SHJ', 'UMQ'], 'E-Care Green Current'),
    ('allianz-uae-intermediary-reference', 'Allianz UAE Intermediary Reference Network', 'Allianz UAE', 'Both', ['AJM', 'AUH', 'DXB', 'FUJ', 'RAK', 'SHJ', 'UMQ'], 'Allianz UAE Intermediary Reference'),
    ('ngi-hn-exclusive', 'NGI HealthNet Exclusive', 'National General Insurance', 'Both', ['AJM', 'AUH', 'DXB', 'FUJ', 'RAK', 'SHJ', 'UMQ'], 'NGI Hn Exclusive Network April 2026'),
    ('ngi-hn-premier', 'NGI HealthNet Premier', 'National General Insurance', 'Both', ['AJM', 'AUH', 'DXB', 'FUJ', 'RAK', 'SHJ', 'UMQ'], 'NGI Hn Premier Network April 2026'),
    ('ngi-hn-advantage', 'NGI HealthNet Advantage', 'National General Insurance', 'Both', ['AJM', 'AUH', 'DXB', 'FUJ', 'RAK', 'SHJ', 'UMQ'], 'NGI Hn Advantage Network April 2026'),
    ('ngi-hn-standard-plus', 'NGI HealthNet Standard Plus', 'National General Insurance', 'Both', ['AJM', 'AUH', 'DXB', 'FUJ', 'RAK', 'SHJ', 'UMQ'], 'NGI Hn Standard Plus Network April 2026'),
    ('ngi-hn-standard', 'NGI HealthNet Standard', 'National General Insurance', 'Both', ['AJM', 'AUH', 'DXB', 'FUJ', 'RAK', 'SHJ', 'UMQ'], 'NGI Hn Standard Network April 2026'),
    ('ngi-hn-basic-plus', 'NGI HealthNet Basic Plus', 'National General Insurance', 'Both', ['AJM', 'AUH', 'DXB', 'FUJ', 'RAK', 'SHJ', 'UMQ'], 'NGI Hn Basic Plus Network April 2026'),
    ('ngi-hn-basic', 'NGI HealthNet Basic', 'National General Insurance', 'Both', ['AJM', 'AUH', 'DXB', 'FUJ', 'RAK', 'SHJ', 'UMQ'], 'NGI Hn Basic Network April 2026'),
    ('ngi-hn-dental', 'NGI HealthNet Dental Network', 'National General Insurance', 'Outpatient', ['AJM', 'AUH', 'DXB', 'FUJ', 'RAK', 'SHJ', 'UMQ'], 'NGI HealthNet Dental Network April 2026'),
    ('ngi-hn-optical', 'NGI HealthNet Optical Network', 'National General Insurance', 'Outpatient', ['AJM', 'AUH', 'DXB', 'FUJ', 'RAK', 'SHJ', 'UMQ'], 'NGI HealthNet Optical Network April 2026'),
    ('sukoon-shield-saver', 'Sukoon Shield Saver Secure Network', 'Sukoon Insurance', 'Both', ['DXB', 'FUJ', 'RAK', 'SHJ', 'UMQ'], 'Sukoon Insurance Secure August 2026'),
    ('sukoon-shield-saver-plus', 'Sukoon Shield Saver Plus Secure Network', 'Sukoon Insurance', 'Both', ['DXB', 'FUJ', 'RAK', 'SHJ', 'UMQ'], 'Sukoon Insurance Secure August 2026'),
    ('union-nas-value-lite', 'Union NAS Value Lite',             'Union Insurance NAS Value Lite', 'Both', ['AJM', 'AUH', 'DXB', 'FUJ', 'RAK', 'SHJ', 'UMQ']),
    ('union-nas-value-lite-ip', 'Union NAS Value Lite IP',       'Union NAS Value Lite IP', 'Inpatient', ['AJM', 'DXB', 'FUJ', 'RAK', 'SHJ', 'UMQ']),
    ('union-nas-value-lite-auh', 'Union NAS Value Lite Abu Dhabi', 'Union NAS Value Lite Abu Dhabi', 'Both', ['AUH']),
    ('union-nas-value-lite-dental', 'Union NAS Value Lite Dental', 'Union NAS Value Lite Dental', 'Outpatient', ['AJM', 'AUH', 'DXB', 'FUJ', 'RAK', 'SHJ', 'UMQ']),
    ('union-nas-value-pharmacies', 'Union NAS Value Pharmacies', 'Union NAS Value Pharmacies', 'Outpatient', ['AJM', 'AUH', 'DXB', 'FUJ', 'RAK', 'SHJ', 'UMQ']),
    ('union-nas-value-ip', 'Union NAS Value IP',              'Union NAS Value IP', 'Inpatient', ['AJM', 'AUH', 'DXB', 'FUJ', 'RAK', 'SHJ', 'UMQ']),
    ('union-nas-value-dental', 'Union NAS Value Dental',      'Union NAS Value Dental', 'Outpatient', ['AJM', 'AUH', 'DXB', 'FUJ', 'RAK', 'SHJ', 'UMQ']),
    ('union-ecare-classic', 'Union eCare Classic',               'Union Insurance eCare Classic', 'Both', ['AJM', 'AUH', 'DXB', 'FUJ', 'RAK', 'SHJ', 'UMQ']),
    ('union-ecare-green',   'Union eCare Green',                 'Union Insurance eCare Green', 'Both', ['AJM', 'AUH', 'DXB', 'FUJ', 'RAK', 'SHJ', 'UMQ']),
    ('union-ecare-blue',    'Union eCare Blue',                  'Union Insurance eCare Blue', 'Both', ['AJM', 'AUH', 'DXB', 'FUJ', 'RAK', 'SHJ', 'UMQ']),
    ('union-nas',            'Union NAS Network',                 'Union Insurance NAS', 'Both', ['AJM', 'AUH', 'DXB', 'FUJ', 'RAK', 'SHJ', 'UMQ']),
    ('union-nas-network-list', 'Union NAS Network List',           'Union NAS Network List', 'Both', ['AJM', 'AUH', 'DXB', 'FUJ', 'RAK', 'SHJ', 'UMQ']),
    ('union-nas-value',      'Union NAS Value Network',            'Union Insurance NAS Value', 'Both', ['AJM', 'AUH', 'DXB', 'FUJ', 'RAK', 'SHJ', 'UMQ']),
    ('union-aafiya-elite',   'Union Aafiya Elite',                  'Union Insurance Aafiya Elite', 'Both', ['AJM', 'AUH', 'DXB', 'FUJ', 'RAK', 'SHJ', 'UMQ']),
    ('union-aafiya-diamond', 'Union Aafiya Diamond',                'Union Insurance Aafiya Diamond', 'Both', ['AJM', 'AUH', 'DXB', 'FUJ', 'RAK', 'SHJ', 'UMQ']),
    ('union-aafiya-gold',    'Union Aafiya Gold',                   'Union Insurance Aafiya Gold', 'Both', ['AJM', 'AUH', 'DXB', 'FUJ', 'RAK', 'SHJ', 'UMQ']),
    ('union-aafiya-plus',    'Union Aafiya Plus',                   'Union Insurance Aafiya Plus', 'Both', ['AJM', 'AUH', 'DXB', 'FUJ', 'RAK', 'SHJ', 'UMQ']),
    ('union-aafiya-ip',      'Union Aafiya IP',                     'Union Insurance Aafiya IP', 'Inpatient', ['AJM', 'AUH', 'DXB', 'FUJ', 'RAK', 'SHJ', 'UMQ']),
    ('union-aafiya-op',      'Union Aafiya OP',                     'Union Insurance Aafiya OP', 'Outpatient', ['AJM', 'AUH', 'DXB', 'FUJ', 'RAK', 'SHJ', 'UMQ']),
    ('union-aafiya-essential-ip', 'Union Aafiya Essential IP',       'Union Insurance Aafiya Essential IP', 'Inpatient', ['AJM', 'AUH', 'DXB', 'FUJ', 'RAK', 'SHJ', 'UMQ']),
    ('union-aafiya-essential-op', 'Union Aafiya Essential OP',       'Union Insurance Aafiya Essential OP', 'Outpatient', ['AJM', 'AUH', 'DXB', 'FUJ', 'RAK', 'SHJ', 'UMQ']),
    ('union-aafiya-apn-ip', 'Union Aafiya APN IP',                  'Union Insurance Aafiya APN IP', 'Inpatient', ['AJM', 'AUH', 'DXB', 'FUJ', 'RAK', 'SHJ', 'UMQ']),
    ('union-aafiya-apn-op', 'Union Aafiya APN OP',                  'Union Insurance Aafiya APN OP', 'Outpatient', ['AJM', 'AUH', 'DXB', 'FUJ', 'RAK', 'SHJ', 'UMQ']),
    ('union-nas-comprehensive-current', 'Union Insurance NAS Comprehensive 2026', 'Union Insurance', 'Both', ['AJM', 'AUH', 'DXB', 'FUJ', 'RAK', 'SHJ', 'UMQ'], 'Union NAS Comprehensive Network Current 2026'),
    ('union-nas-general-current', 'Union Insurance NAS General 2026', 'Union Insurance', 'Both', ['AJM', 'AUH', 'DXB', 'FUJ', 'RAK', 'SHJ', 'UMQ'], 'Union NAS General Network Current 2026'),
    ('union-nas-restricted-current', 'Union Insurance NAS Restricted 2026', 'Union Insurance', 'Both', ['AJM', 'AUH', 'DXB', 'FUJ', 'RAK', 'SHJ', 'UMQ'], 'Union NAS Restricted Network Current 2026'),
    ('union-nextcare-gn-current', 'Union Insurance NextCare GN 2026', 'Union Insurance', 'Both', ['AJM', 'AUH', 'DXB', 'FUJ', 'RAK', 'SHJ', 'UMQ'], 'Union NextCare GN Current 2026'),
    ('union-nextcare-gn-plus-current', 'Union Insurance NextCare GN Plus 2026', 'Union Insurance', 'Both', ['AJM', 'AUH', 'DXB', 'FUJ', 'RAK', 'SHJ', 'UMQ'], 'Union NextCare GN Plus Current 2026'),
    ('union-nextcare-rn-enhanced-current', 'Union Insurance NextCare RN Enhanced 2026', 'Union Insurance', 'Both', ['AJM', 'AUH', 'DXB', 'FUJ', 'RAK', 'SHJ', 'UMQ'], 'Union NextCare RN Enhanced Current 2026'),
    ('union-nextcare-restricted-current', 'Union Insurance NextCare Restricted 2026', 'Union Insurance', 'Both', ['AJM', 'AUH', 'DXB', 'FUJ', 'RAK', 'SHJ', 'UMQ'], 'Union NextCare Restricted Current 2026'),
    ('union-nextcare-restricted-2-current', 'Union Insurance NextCare Restricted 2 2026', 'Union Insurance', 'Both', ['AJM', 'AUH', 'DXB', 'FUJ', 'RAK', 'SHJ', 'UMQ'], 'Union NextCare Restricted 2 Current 2026'),
    ('union-nextcare-restricted-3-current', 'Union Insurance NextCare Restricted 3 2026', 'Union Insurance', 'Both', ['AJM', 'AUH', 'DXB', 'FUJ', 'RAK', 'SHJ', 'UMQ'], 'Union NextCare Restricted 3 Current 2026'),
    ('union-nextcare-pcp-current', 'Union Insurance NextCare PCP 2026', 'Union Insurance', 'Outpatient', ['AJM', 'AUH', 'DXB', 'FUJ', 'RAK', 'SHJ', 'UMQ'], 'Union NextCare PCP Current 2026'),
    ('union-nextcare-pcp-c-current', 'Union Insurance NextCare PCP C 2026', 'Union Insurance', 'Outpatient', ['AJM', 'AUH', 'DXB', 'FUJ', 'RAK', 'SHJ', 'UMQ'], 'Union NextCare PCP C Current 2026'),
    ('union-nextcare-pcp-auh-current', 'Union Insurance NextCare PCP Abu Dhabi 2026', 'Union Insurance', 'Outpatient', ['AUH'], 'Union NextCare PCP AUH Current 2026'),
    ('union-nas-value-current', 'Union Insurance NAS Value 2026', 'Union Insurance', 'Both', ['AJM', 'AUH', 'DXB', 'FUJ', 'RAK', 'SHJ', 'UMQ'], 'Union NAS Value Network Current 2026'),
    ('union-nas-value-op-current', 'Union Insurance NAS Value OP 2026', 'Union Insurance', 'Outpatient', ['AJM', 'AUH', 'DXB', 'FUJ', 'RAK', 'SHJ', 'UMQ'], 'Union NAS Value OP Current 2026'),
    ('union-ecare-blue-current', 'Union Insurance eCare Blue 2026', 'Union Insurance', 'Both', ['AJM', 'AUH', 'DXB', 'FUJ', 'RAK', 'SHJ', 'UMQ'], 'Union eCare Blue Current 2026'),
    ('union-ecare-green-current', 'Union Insurance eCare Green 2026', 'Union Insurance', 'Both', ['AJM', 'AUH', 'DXB', 'FUJ', 'RAK', 'SHJ', 'UMQ'], 'Union eCare Green Current 2026'),
    ('union-ecare-classic-current', 'Union Insurance eCare Classic 2026', 'Union Insurance', 'Both', ['AJM', 'AUH', 'DXB', 'FUJ', 'RAK', 'SHJ', 'UMQ'], 'Union eCare Classic Current 2026'),
    ('union-nas-value-lite-auh-current', 'Union Insurance NAS Value Lite Abu Dhabi 2026', 'Union Insurance', 'Both', ['AUH'], 'Union NAS Value Lite AUH OP IP Current 2026'),
    ('union-nas-value-lite-ip-ne-current', 'Union Insurance NAS Value Lite Northern Emirates IP 2026', 'Union Insurance', 'Inpatient', ['AJM', 'FUJ', 'RAK', 'SHJ', 'UMQ'], 'Union NAS Value Lite IP DXB NE Current 2026'),
    ('union-nas-value-lite-op-ne-current', 'Union Insurance NAS Value Lite Northern Emirates OP 2026', 'Union Insurance', 'Outpatient', ['AJM', 'FUJ', 'RAK', 'SHJ', 'UMQ'], 'Union NAS Value Lite OP DXB NE Current 2026'),
    ('union-nas-value-lite-dental-current', 'Union Insurance NAS Value Lite Dental 2026', 'Union Insurance', 'Outpatient', ['AJM', 'AUH', 'DXB', 'FUJ', 'RAK', 'SHJ', 'UMQ'], 'Union NAS Value Lite Dental Current 2026'),
    ('union-nas-value-ip-current', 'Union Insurance NAS Value IP 2026', 'Union Insurance', 'Inpatient', ['AJM', 'AUH', 'DXB', 'FUJ', 'RAK', 'SHJ', 'UMQ'], 'Union NAS Value IP Current 2026'),
    ('union-nas-value-pharmacies-current', 'Union Insurance NAS Value Pharmacies 2026', 'Union Insurance', 'Outpatient', ['AJM', 'AUH', 'DXB', 'FUJ', 'RAK', 'SHJ', 'UMQ'], 'Union NAS Value Pharmacies Current 2026'),
    ('union-nas-workers-current', 'Union Insurance NAS Workers 2026', 'Union Insurance', 'Both', ['AJM', 'AUH', 'DXB', 'FUJ', 'RAK', 'SHJ', 'UMQ'], 'Union NAS Workers Network Current 2026'),
    ('union-nas-rn-plus-current', 'Union Insurance NAS RN Plus 2026', 'Union Insurance', 'Both', ['AJM', 'AUH', 'DXB', 'FUJ', 'RAK', 'SHJ', 'UMQ'], 'Union NAS RN Plus Current 2026'),
    ('union-nas-super-restricted-current', 'Union Insurance NAS Super-Restricted 2026', 'Union Insurance', 'Both', ['AJM', 'AUH', 'DXB', 'FUJ', 'RAK', 'SHJ', 'UMQ'], 'Union NAS Super-Restricted Network Current 2026'),
    ('union-nas-executive-current', 'Union Insurance NAS Executive 2026', 'Union Insurance', 'Both', ['AJM', 'AUH', 'DXB', 'FUJ', 'RAK', 'SHJ', 'UMQ'], 'Union NAS Executive Network Current 2026'),
    ('union-aafiya-apn-current', 'Union Insurance Aafiya APN 2026', 'Union Insurance', 'Both', ['AJM', 'AUH', 'DXB', 'FUJ', 'RAK', 'SHJ', 'UMQ'], 'Union Aafiya APN Current 2026'),
    ('union-aafiya-diamond-current', 'Union Insurance Aafiya Diamond 2026', 'Union Insurance', 'Both', ['AJM', 'AUH', 'DXB', 'FUJ', 'RAK', 'SHJ', 'UMQ'], 'Union Aafiya Diamond Current 2026'),
    ('union-aafiya-edge-current', 'Union Insurance Aafiya Edge 2026', 'Union Insurance', 'Both', ['AJM', 'AUH', 'DXB', 'FUJ', 'RAK', 'SHJ', 'UMQ'], 'Union Aafiya Edge Current 2026'),
    ('union-aafiya-elite-current', 'Union Insurance Aafiya Elite 2026', 'Union Insurance', 'Both', ['AJM', 'AUH', 'DXB', 'FUJ', 'RAK', 'SHJ', 'UMQ'], 'Union Aafiya Elite Current 2026'),
    ('union-aafiya-essential-current', 'Union Insurance Aafiya Essential 2026', 'Union Insurance', 'Both', ['AJM', 'AUH', 'DXB', 'FUJ', 'RAK', 'SHJ', 'UMQ'], 'Union Aafiya Essential Current 2026'),
    ('union-aafiya-gold-current', 'Union Insurance Aafiya Gold 2026', 'Union Insurance', 'Both', ['AJM', 'AUH', 'DXB', 'FUJ', 'RAK', 'SHJ', 'UMQ'], 'Union Aafiya Gold Current 2026'),
    ('union-aafiya-plus-current', 'Union Insurance Aafiya Plus 2026', 'Union Insurance', 'Both', ['AJM', 'AUH', 'DXB', 'FUJ', 'RAK', 'SHJ', 'UMQ'], 'Union Aafiya Plus Current 2026'),
    ('union-nas-value-dental-current', 'Union Insurance NAS Value Dental 2026', 'Union Insurance', 'Outpatient', ['AJM', 'AUH', 'DXB', 'FUJ', 'RAK', 'SHJ', 'UMQ'], 'Union NAS Value Dental Current 2026'),
    ('union-nextcare-regional-current', 'Union Insurance NextCare Regional 2026', 'Union Insurance', 'Both', ['AJM', 'AUH', 'DXB', 'FUJ', 'RAK', 'SHJ', 'UMQ'], 'Union NextCare Regional Current 2026'),
    ('dni-lifeline-empire', 'DNI Lifeline Empire',                  'DNI Lifeline Empire', 'Both', ['AJM', 'AUH', 'DXB', 'FUJ', 'RAK', 'SHJ', 'UMQ'], 'DNI Lifeline Empire Current'),
    ('dni-lifeline-pearl', 'DNI Lifeline Pearl',                   'DNI Lifeline Pearl', 'Both', ['AJM', 'AUH', 'DXB', 'FUJ', 'RAK', 'SHJ', 'UMQ'], 'DNI Lifeline Pearl Current'),
    ('dni-lifeline-sapphire', 'DNI Lifeline Sapphire',              'DNI Lifeline Sapphire', 'Both', ['AJM', 'AUH', 'DXB', 'FUJ', 'RAK', 'SHJ', 'UMQ'], 'DNI Lifeline Sapphire Current'),
    ('dni-nextcare-consolidated', 'DNI Nextcare Consolidated',       'DNI Nextcare Consolidated', 'Both', ['AJM', 'AUH', 'DXB', 'FUJ', 'RAK', 'SHJ', 'UMQ'], 'DNI Nextcare Consolidated'),
    ('dni-nextcare-gn', 'DNI Nextcare GN',                          'DNI Nextcare GN', 'Both', ['AJM', 'AUH', 'DXB', 'FUJ', 'RAK', 'SHJ', 'UMQ']),
    ('dni-nextcare-rne', 'DNI Nextcare RNE',                        'DNI Nextcare RNE', 'Both', ['AJM', 'AUH', 'DXB', 'FUJ', 'RAK', 'SHJ', 'UMQ']),
    ('dni-nextcare-rn', 'DNI Nextcare RN',                          'DNI Nextcare RN', 'Inpatient', ['AJM', 'AUH', 'DXB', 'FUJ', 'RAK', 'SHJ', 'UMQ']),
    ('dni-nextcare-rn2', 'DNI Nextcare RN2',                        'DNI Nextcare RN2', 'Inpatient', ['AJM', 'AUH', 'DXB', 'FUJ', 'RAK', 'SHJ', 'UMQ']),
    ('dni-nextcare-rn3', 'DNI Nextcare RN3',                        'DNI Nextcare RN3', 'Inpatient', ['AJM', 'AUH', 'DXB', 'FUJ', 'RAK', 'SHJ', 'UMQ']),
    ('dni-nextcare-pcp', 'DNI Nextcare PCP',                        'DNI Nextcare PCP', 'Outpatient', ['AJM', 'AUH', 'DXB', 'FUJ', 'RAK', 'SHJ', 'UMQ']),
    ('dni-nextcare-pcp-c', 'DNI Nextcare PCP C',                    'DNI Nextcare PCP C', 'Outpatient', ['AJM', 'AUH', 'DXB', 'FUJ', 'RAK', 'SHJ', 'UMQ']),
    ('dni-nextcare-pcp-auh', 'DNI Nextcare PCP Abu Dhabi',           'DNI Nextcare PCP Abu Dhabi', 'Outpatient', ['AUH']),
    ('dni-nextcare-seha', 'DNI Nextcare SEHA Providers',             'DNI Nextcare SEHA Providers', 'Both', ['AUH']),
    ('dni-nextcare-regional', 'DNI Nextcare Regional',               'DNI Nextcare Regional', 'Both', ['AJM', 'AUH', 'DXB', 'FUJ', 'RAK', 'SHJ', 'UMQ']),
    ('dni-nextcare-tpa-phm', 'DNI Nextcare TPA-PHM',                 'DNI Nextcare TPA-PHM', 'Both', ['AJM', 'AUH', 'DXB', 'FUJ', 'RAK', 'SHJ', 'UMQ'], 'DNI Nextcare TPA PHM'),
    ('dni-mednet', 'DNI MedNet',                                  'DNI MedNet', 'Both', ['AJM', 'AUH', 'DXB', 'FUJ', 'RAK', 'SHJ', 'UMQ']),
    ('dni-nas', 'DNI NAS',                                          'DNI NAS', 'Both', ['AJM', 'AUH', 'DXB', 'FUJ', 'RAK', 'SHJ', 'UMQ']),
    ('dni-global-choice', 'DNI Global Choice',                        'DNI Global Choice', 'Both', ['AJM', 'AUH', 'DXB', 'FUJ', 'RAK', 'SHJ', 'UMQ']),
    ('dni-global-choice-renewal', 'DNI Global Choice Renewal',        'DNI Global Choice Renewal', 'Both', ['AJM', 'AUH', 'DXB', 'FUJ', 'RAK', 'SHJ', 'UMQ']),
    ('dni-global-choice-network', 'DNI Global Choice Network',       'DNI Global Choice Network', 'Both', ['AJM', 'AUH', 'DXB', 'FUJ', 'RAK', 'SHJ', 'UMQ'], 'DNI Global Choice Network'),
    ('dni-global-choice-renewal-network', 'DNI Global Choice Renewal Network', 'DNI Global Choice Renewal Network', 'Both', ['AJM', 'AUH', 'DXB', 'FUJ', 'RAK', 'SHJ', 'UMQ'], 'DNI Global Choice Renewal Network'),
    ('dni-neuron-global-choice-2024', 'DNI Neuron Global Choice 2024', 'DNI Neuron Global Choice', 'Both', ['AJM', 'AUH', 'DXB', 'FUJ', 'RAK', 'SHJ', 'UMQ'], 'DNI Neuron Global Choice March 2024'),
    ('dni-neuron-global-choice-renewal-2024', 'DNI Neuron Global Choice Renewal 2024', 'DNI Neuron Global Choice Renewal', 'Both', ['AJM', 'AUH', 'DXB', 'FUJ', 'RAK', 'SHJ', 'UMQ'], 'DNI Neuron Global Choice Renewal March 2024'),
    ('dni-aafiya-elite-2024', 'DNI Aafiya Elite 2024', 'DNI Aafiya', 'Both', ['AJM', 'AUH', 'DXB', 'FUJ', 'RAK', 'SHJ', 'UMQ'], 'DNI Aafiya Elite April 2024'),
    ('dni-aafiya-diamond-2024', 'DNI Aafiya Diamond 2024', 'DNI Aafiya', 'Both', ['AJM', 'AUH', 'DXB', 'FUJ', 'RAK', 'SHJ', 'UMQ'], 'DNI Aafiya Diamond April 2024'),
    ('dni-aafiya-gold-2024', 'DNI Aafiya Gold 2024', 'DNI Aafiya', 'Both', ['AJM', 'AUH', 'DXB', 'FUJ', 'RAK', 'SHJ', 'UMQ'], 'DNI Aafiya Gold April 2024'),
    ('dni-aafiya-plus-2024', 'DNI Aafiya Plus 2024', 'DNI Aafiya', 'Both', ['AJM', 'AUH', 'DXB', 'FUJ', 'RAK', 'SHJ', 'UMQ'], 'DNI Aafiya Plus April 2024'),
    ('dni-aafiya', 'DNI Aafiya',                                      'DNI Aafiya', 'Both', ['AJM', 'AUH', 'DXB', 'FUJ', 'RAK', 'SHJ', 'UMQ']),
    ('dni-mednet-gold-2024', 'DNI MedNet Gold 2024', 'DNI MedNet', 'Both', ['AJM', 'AUH', 'DXB', 'FUJ', 'RAK', 'SHJ', 'UMQ'], 'DNI MedNet Gold April 2024'),
    ('dni-mednet-silver-premium-2024', 'DNI MedNet Silver Premium 2024', 'DNI MedNet', 'Both', ['AJM', 'AUH', 'DXB', 'FUJ', 'RAK', 'SHJ', 'UMQ'], 'DNI MedNet Silver Premium April 2024'),
    ('dni-mednet-silver-classic-2024', 'DNI MedNet Silver Classic 2024', 'DNI MedNet', 'Both', ['AJM', 'AUH', 'DXB', 'FUJ', 'RAK', 'SHJ', 'UMQ'], 'DNI MedNet Silver Classic April 2024'),
    ('dni-mednet-green-2024', 'DNI MedNet Green 2024', 'DNI MedNet', 'Both', ['AJM', 'AUH', 'DXB', 'FUJ', 'RAK', 'SHJ', 'UMQ'], 'DNI MedNet Green April 2024'),
    ('dni-mednet-emerald-2024', 'DNI MedNet Emerald 2024', 'DNI MedNet', 'Both', ['AJM', 'AUH', 'DXB', 'FUJ', 'RAK', 'SHJ', 'UMQ'], 'DNI MedNet Emerald April 2024'),
    ('dni-mednet-pearl-2024', 'DNI MedNet Pearl 2024', 'DNI MedNet', 'Both', ['AJM', 'AUH', 'DXB', 'FUJ', 'RAK', 'SHJ', 'UMQ'], 'DNI MedNet Pearl April 2024'),
    ('dni-mednet-silk-road-op-2024', 'DNI MedNet Silk Road OP 2024', 'DNI MedNet', 'Outpatient', ['AJM', 'AUH', 'DXB', 'FUJ', 'RAK', 'SHJ', 'UMQ'], 'DNI MedNet Silk Road Op April 2024'),
    ('dni-mednet-silk-road-ip-2024', 'DNI MedNet Silk Road IP 2024', 'DNI MedNet', 'Inpatient', ['AJM', 'AUH', 'DXB', 'FUJ', 'RAK', 'SHJ', 'UMQ'], 'DNI MedNet Silk Road Ip April 2024'),
    ('dni-mednet-ebp-op-2024', 'DNI MedNet EBP OP 2024', 'DNI MedNet', 'Outpatient', ['AJM', 'AUH', 'DXB', 'FUJ', 'RAK', 'SHJ', 'UMQ'], 'DNI MedNet Ebp Op April 2024'),
    ('dni-mednet-ebp-ip-2024', 'DNI MedNet EBP IP 2024', 'DNI MedNet', 'Inpatient', ['AJM', 'AUH', 'DXB', 'FUJ', 'RAK', 'SHJ', 'UMQ'], 'DNI MedNet Ebp Ip April 2024'),
    ('dni-mednet-basic-op-2024', 'DNI MedNet Basic OP 2024', 'DNI MedNet', 'Outpatient', ['AJM', 'AUH', 'DXB', 'FUJ', 'RAK', 'SHJ', 'UMQ'], 'DNI MedNet Basic Op April 2024'),
    ('dni-mednet-basic-ip-2024', 'DNI MedNet Basic IP 2024', 'DNI MedNet', 'Inpatient', ['AJM', 'AUH', 'DXB', 'FUJ', 'RAK', 'SHJ', 'UMQ'], 'DNI MedNet Basic Ip April 2024'),
    ('dni-mednet-dental-2024', 'DNI MedNet Dental 2024', 'DNI MedNet', 'Outpatient', ['AJM', 'AUH', 'DXB', 'FUJ', 'RAK', 'SHJ', 'UMQ'], 'DNI MedNet Dental April 2024'),
    ('dni-mednet-optical-2024', 'DNI MedNet Optical 2024', 'DNI MedNet', 'Outpatient', ['AJM', 'AUH', 'DXB', 'FUJ', 'RAK', 'SHJ', 'UMQ'], 'DNI MedNet Optical April 2024'),
    ('dni-mednet-alternative-2024', 'DNI MedNet Alternative 2024', 'DNI MedNet', 'Both', ['AJM', 'AUH', 'DXB', 'FUJ', 'RAK', 'SHJ', 'UMQ'], 'DNI MedNet Alternative April 2024'),
    ('dni-nas-comprehensive-2024', 'DNI NAS Comprehensive 2024', 'DNI NAS', 'Both', ['AJM', 'AUH', 'DXB', 'FUJ', 'RAK', 'SHJ', 'UMQ'], 'DNI NAS Comprehensive Network March 2024'),
    ('dni-nas-executive-2024', 'DNI NAS Executive 2024', 'DNI NAS', 'Both', ['AJM', 'AUH', 'DXB', 'FUJ', 'RAK', 'SHJ', 'UMQ'], 'DNI NAS Executive Network March 2024'),
    ('dni-nas-general-2024', 'DNI NAS General 2024', 'DNI NAS', 'Both', ['AJM', 'AUH', 'DXB', 'FUJ', 'RAK', 'SHJ', 'UMQ'], 'DNI NAS General Network March 2024'),
    ('dni-nas-restricted-2024', 'DNI NAS Restricted 2024', 'DNI NAS', 'Both', ['AJM', 'AUH', 'DXB', 'FUJ', 'RAK', 'SHJ', 'UMQ'], 'DNI NAS Restricted Network March 2024'),
    ('dni-nas-super-restricted-2024', 'DNI NAS Super-Restricted 2024', 'DNI NAS', 'Both', ['AJM', 'AUH', 'DXB', 'FUJ', 'RAK', 'SHJ', 'UMQ'], 'DNI NAS Super-Restricted Network March 2024'),
    ('dni-nextcare-gn-2024', 'DNI NextCare GN 2024', 'DNI NextCare GN', 'Both', ['AJM', 'AUH', 'DXB', 'FUJ', 'RAK', 'SHJ', 'UMQ'], 'DNI NextCare GN February 2024'),
    ('dni-nextcare-gn-plus-2024', 'DNI NextCare GN Plus 2024', 'DNI NextCare GN', 'Both', ['AJM', 'AUH', 'DXB', 'FUJ', 'RAK', 'SHJ', 'UMQ'], 'DNI NextCare GN+ February 2024'),
    ('dni-nextcare-rn-2024', 'DNI NextCare RN 2024', 'DNI NextCare RN', 'Inpatient', ['AJM', 'AUH', 'DXB', 'FUJ', 'RAK', 'SHJ', 'UMQ'], 'DNI NextCare RN February 2024'),
    ('dni-nextcare-rn2-2024', 'DNI NextCare RN2 2024', 'DNI NextCare RN2', 'Inpatient', ['AJM', 'AUH', 'DXB', 'FUJ', 'RAK', 'SHJ', 'UMQ'], 'DNI NextCare RN2 February 2024'),
    ('dni-nextcare-rn3-2024', 'DNI NextCare RN3 2024', 'DNI NextCare RN3', 'Inpatient', ['AJM', 'AUH', 'DXB', 'FUJ', 'RAK', 'SHJ', 'UMQ'], 'DNI NextCare RN3 February 2024'),
    ('dni-nextcare-rne-2024', 'DNI NextCare RNE 2024', 'DNI NextCare RNE', 'Both', ['AJM', 'AUH', 'DXB', 'FUJ', 'RAK', 'SHJ', 'UMQ'], 'DNI NextCare RNE February 2024'),
    ('dni-nextcare-pcp-2024', 'DNI NextCare PCP 2024', 'DNI NextCare PCP', 'Outpatient', ['AJM', 'AUH', 'DXB', 'FUJ', 'RAK', 'SHJ', 'UMQ'], 'DNI NextCare PCP February 2024'),
    ('dni-nextcare-pcp-c-2024', 'DNI NextCare PCP C 2024', 'DNI NextCare PCP', 'Outpatient', ['AJM', 'AUH', 'DXB', 'FUJ', 'RAK', 'SHJ', 'UMQ'], 'DNI NextCare PCP C February 2024'),
    ('dni-nextcare-pcp-auh-2024', 'DNI NextCare PCP Abu Dhabi 2024', 'DNI NextCare PCP', 'Outpatient', ['AUH'], 'DNI NextCare PCP AUH February 2024'),
    ('dni-nextcare-regional-2024', 'DNI NextCare Regional 2024', 'DNI NextCare Regional', 'Both', ['AJM', 'AUH', 'DXB', 'FUJ', 'RAK', 'SHJ', 'UMQ'], 'DNI NextCare REGIONAL February 2024'),
    ('dni-nextcare-seha-2024', 'DNI NextCare SEHA Providers 2024', 'DNI NextCare SEHA Providers', 'Both', ['AUH'], 'DNI NextCare SEHA Providers February 2024'),
    ('union-nextcare-general', 'Union Nextcare General',           'Union Insurance Nextcare General', 'Both', ['AJM', 'AUH', 'DXB', 'FUJ', 'RAK', 'SHJ', 'UMQ']),
    ('union-nextcare-general-plus', 'Union Nextcare General Plus',  'Union Insurance Nextcare General Plus', 'Both', ['AJM', 'AUH', 'DXB', 'FUJ', 'RAK', 'SHJ', 'UMQ']),
    ('union-nextcare-pcp', 'Union Nextcare PCP',                'Union Insurance Nextcare PCP', 'Outpatient', ['AJM', 'AUH', 'DXB', 'FUJ', 'RAK', 'SHJ', 'UMQ']),
    ('union-nextcare-restricted', 'Union Nextcare Restricted',     'Union Insurance Nextcare Restricted', 'Both', ['AJM', 'AUH', 'DXB', 'FUJ', 'RAK', 'SHJ', 'UMQ']),
    ('union-nextcare-restricted-2', 'Union Nextcare Restricted 2',  'Union Insurance Nextcare Restricted 2', 'Both', ['AJM', 'AUH', 'DXB', 'FUJ', 'RAK', 'SHJ', 'UMQ']),
    ('union-nextcare-restricted-3', 'Union Nextcare Restricted 3',  'Union Insurance Nextcare Restricted 3', 'Both', ['AJM', 'AUH', 'DXB', 'FUJ', 'RAK', 'SHJ', 'UMQ']),
    ('union-nextcare-pcp-c', 'Union Nextcare PCP-C',               'Union Insurance Nextcare PCP C', 'Outpatient', ['AJM', 'AUH', 'DXB', 'FUJ', 'RAK', 'SHJ', 'UMQ']),
    ('union-nextcare-pcp-auh', 'Union Nextcare PCP Abu Dhabi',     'Union Insurance Nextcare PCP Abu Dhabi', 'Outpatient', ['AUH']),
    ('union-nextcare-rn-enhanced', 'Union Nextcare RN Enhanced',     'Union Insurance Nextcare RN Enhanced', 'Inpatient', ['AJM', 'AUH', 'DXB', 'FUJ', 'RAK', 'SHJ', 'UMQ']),
    ('union-nas-workers-lite', 'Union NAS Workers Lite',             'Union Insurance NAS Workers Lite', 'Both', ['AJM', 'AUH', 'DXB', 'FUJ', 'RAK', 'SHJ', 'UMQ']),
    ('orient-value',         'Orient Value Network',               'Orient Insurance Value', 'Both', ['AJM', 'AUH', 'DXB', 'FUJ', 'RAK', 'SHJ', 'UMQ']),
    ('orient-nextcare-consolidated', 'Orient Nextcare Consolidated',  'Orient Insurance Nextcare Consolidated', 'Both', ['AJM', 'AUH', 'DXB', 'FUJ', 'RAK', 'SHJ', 'UMQ']),
    ('orient-nextcare-gn', 'Orient Nextcare GN',                     'Orient Nextcare GN', 'Both', ['AJM', 'AUH', 'DXB', 'FUJ', 'RAK', 'SHJ', 'UMQ']),
    ('orient-nextcare-rne', 'Orient Nextcare RNE',                   'Orient Nextcare RNE', 'Both', ['AJM', 'AUH', 'DXB', 'FUJ', 'RAK', 'SHJ', 'UMQ']),
    ('orient-nextcare-rn', 'Orient Nextcare RN',                     'Orient Nextcare RN', 'Inpatient', ['AJM', 'AUH', 'DXB', 'FUJ', 'RAK', 'SHJ', 'UMQ']),
    ('orient-nextcare-rn2', 'Orient Nextcare RN2',                   'Orient Nextcare RN2', 'Inpatient', ['AJM', 'AUH', 'DXB', 'FUJ', 'RAK', 'SHJ', 'UMQ']),
    ('orient-nextcare-rn3', 'Orient Nextcare RN3',                   'Orient Nextcare RN3', 'Inpatient', ['AJM', 'AUH', 'DXB', 'FUJ', 'RAK', 'SHJ', 'UMQ']),
    ('orient-nextcare-pcp', 'Orient Nextcare PCP',                   'Orient Nextcare PCP', 'Outpatient', ['AJM', 'AUH', 'DXB', 'FUJ', 'RAK', 'SHJ', 'UMQ']),
    ('orient-nextcare-pcp-auh', 'Orient Nextcare PCP Abu Dhabi',     'Orient Nextcare PCP Abu Dhabi', 'Outpatient', ['AUH']),
    ('orient-nextcare-pcp-c', 'Orient Nextcare PCP C',               'Orient Nextcare PCP C', 'Outpatient', ['AJM', 'AUH', 'DXB', 'FUJ', 'RAK', 'SHJ', 'UMQ']),
    ('orient-nextcare-pcp-dental', 'Orient Nextcare PCP Dental',     'Orient Nextcare PCP Dental', 'Outpatient', ['AJM', 'AUH', 'DXB', 'FUJ', 'RAK', 'SHJ', 'UMQ']),
    ('orient-nextcare-seha', 'Orient Nextcare SEHA Providers',       'Orient Nextcare SEHA Providers', 'Both', ['AUH']),
    ('orient-nextcare-june-rn3', 'Orient Nextcare June RN3',          'Orient Nextcare June RN3', 'Inpatient', ['AJM', 'AUH', 'DXB', 'FUJ', 'RAK', 'SHJ', 'UMQ']),
    ('orient-value-pharmacy', 'Orient Value Pharmacy',               'Orient Value Pharmacy', 'Outpatient', ['AJM', 'AUH', 'DXB', 'FUJ', 'RAK', 'SHJ', 'UMQ']),
    ('orient-value-ip', 'Orient Value Inpatient',                    'Orient Value Inpatient', 'Inpatient', ['AJM', 'AUH', 'DXB', 'FUJ', 'RAK', 'SHJ', 'UMQ']),
    ('orient-value-vnl-dental', 'Orient Value VNL Dental',            'Orient Value VNL Dental', 'Outpatient', ['AJM', 'AUH', 'DXB', 'FUJ', 'RAK', 'SHJ', 'UMQ']),
    ('orient-mednet-annual-checkup', 'Orient MedNet Annual Health Checkup', 'Orient MedNet Annual Health Checkup', 'Outpatient', ['AJM', 'AUH', 'DXB', 'FUJ', 'RAK', 'SHJ', 'UMQ']),
    ('orient-nas-standard',  'Orient NAS Standard',                'Orient Insurance NAS Standard', 'Both', ['AJM', 'AUH', 'DXB', 'FUJ', 'RAK', 'SHJ', 'UMQ']),
    ('orient-nas-standard-network', 'Orient NAS Standard Network',  'Orient NAS Standard Network', 'Both', ['AJM', 'AUH', 'DXB', 'FUJ', 'RAK', 'SHJ', 'UMQ']),
    ('orient-nextcare-pcp-ne', 'Orient Nextcare PCP Northern Emirates', 'Orient Insurance Nextcare PCP Northern Emirates', 'Outpatient', ['AJM', 'FUJ', 'RAK', 'SHJ', 'UMQ']),
    ('orient-nextcare-op-pcp-ip-rn3', 'Orient Nextcare OP-PCP / IP-RN3', 'Orient Insurance Nextcare OP PCP IP RN3', 'Both', ['AJM', 'AUH', 'DXB', 'FUJ', 'RAK', 'SHJ', 'UMQ']),
    ('orient-mednet-gold',   'Orient MedNet Gold',                  'Orient Insurance MedNet Gold', 'Both', ['AJM', 'AUH', 'DXB', 'FUJ', 'RAK', 'SHJ', 'UMQ']),
    ('orient-mednet-silver-premium', 'Orient MedNet Silver Premium', 'Orient Insurance MedNet Silver Premium', 'Both', ['AJM', 'AUH', 'DXB', 'FUJ', 'RAK', 'SHJ', 'UMQ']),
    ('orient-mednet-silver-classic', 'Orient MedNet Silver Classic', 'Orient Insurance MedNet Silver Classic', 'Both', ['AJM', 'AUH', 'DXB', 'FUJ', 'RAK', 'SHJ', 'UMQ']),
    ('orient-mednet-green', 'Orient MedNet Green',                   'Orient Insurance MedNet Green', 'Both', ['AJM', 'AUH', 'DXB', 'FUJ', 'RAK', 'SHJ', 'UMQ']),
    ('orient-mednet-silk-road-op', 'Orient MedNet Silk Road OP',      'Orient Insurance MedNet Silk Road OP', 'Outpatient', ['AJM', 'AUH', 'DXB', 'FUJ', 'RAK', 'SHJ', 'UMQ']),
    ('orient-mednet-silk-road-ip', 'Orient MedNet Silk Road IP',      'Orient Insurance MedNet Silk Road IP', 'Inpatient', ['AJM', 'AUH', 'DXB', 'FUJ', 'RAK', 'SHJ', 'UMQ']),
    ('orient-mednet-emerald', 'Orient MedNet Emerald',               'Orient Insurance MedNet Emerald', 'Both', ['AJM', 'AUH', 'DXB', 'FUJ', 'RAK', 'SHJ', 'UMQ']),
    ('orient-mednet-pearl', 'Orient MedNet Pearl',                  'Orient Insurance MedNet Pearl', 'Both', ['AJM', 'AUH', 'DXB', 'FUJ', 'RAK', 'SHJ', 'UMQ']),
    ('orient-mednet-ebp-op', 'Orient MedNet EBP OP',                 'Orient Insurance MedNet EBP OP', 'Outpatient', ['AJM', 'AUH', 'DXB', 'FUJ', 'RAK', 'SHJ', 'UMQ']),
    ('orient-mednet-ebp-ip', 'Orient MedNet EBP IP',                 'Orient Insurance MedNet EBP IP', 'Inpatient', ['AJM', 'AUH', 'DXB', 'FUJ', 'RAK', 'SHJ', 'UMQ']),
    ('orient-mednet-basic-op', 'Orient MedNet Basic OP',              'Orient Insurance MedNet Basic OP', 'Outpatient', ['AJM', 'AUH', 'DXB', 'FUJ', 'RAK', 'SHJ', 'UMQ']),
    ('orient-mednet-basic-ip', 'Orient MedNet Basic IP',              'Orient Insurance MedNet Basic IP', 'Inpatient', ['AJM', 'AUH', 'DXB', 'FUJ', 'RAK', 'SHJ', 'UMQ']),
    ('sukoon-premium',     'Sukoon Premium Network',           'Sukoon Insurance Premium', 'Both', ['AJM', 'AUH', 'DXB', 'FUJ', 'RAK', 'SHJ', 'UMQ'], 'Sukoon Premium Network August 2026'),
    ('sukoon-edge',        'Sukoon Edge Network',              'Sukoon Insurance Edge', 'Both', ['AJM', 'AUH', 'DXB', 'FUJ', 'RAK', 'SHJ', 'UMQ'], 'Sukoon Edge Network August 2026'),
    ('sukoon-signature',   'Sukoon Signature Network',         'Sukoon Insurance Signature', 'Both', ['AJM', 'AUH', 'DXB', 'FUJ', 'RAK', 'SHJ', 'UMQ'], 'Sukoon Signature Network August 2026'),
    ('sukoon-advance-plus', 'Sukoon Advance Plus Network',      'Sukoon Insurance Advance Plus', 'Both', ['AJM', 'AUH', 'DXB', 'FUJ', 'RAK', 'SHJ', 'UMQ'], 'Sukoon Advance Plus Network August 2026'),
    ('sukoon-advance',     'Sukoon Advance Network',           'Sukoon Insurance Advance', 'Both', ['AJM', 'AUH', 'DXB', 'FUJ', 'RAK', 'SHJ', 'UMQ'], 'Sukoon Advance Network August 2026'),
    ('sukoon-vital',       'Sukoon Vital Network',             'Sukoon Insurance Vital', 'Both', ['AJM', 'AUH', 'DXB', 'FUJ', 'RAK', 'SHJ', 'UMQ'], 'Sukoon Vital Network August 2026'),
    ('sukoon-vital-eco',   'Sukoon Vital Eco Network',         'Sukoon Insurance Vital Eco', 'Both', ['AJM', 'AUH', 'DXB', 'FUJ', 'RAK', 'SHJ', 'UMQ'], 'Sukoon Vital Eco Network August 2026'),
    ('sukoon-signature-medcare', 'Sukoon Signature + Medcare Network', 'Sukoon Insurance Signature Medcare', 'Both', ['AJM', 'AUH', 'DXB', 'FUJ', 'RAK', 'SHJ', 'UMQ'], 'Sukoon Signature Medcare Network August 2026'),
    ('sukoon-all-pharmacies', 'Sukoon All Pharmacies',          'Sukoon Insurance All Pharmacies', 'Both', ['AJM', 'AUH', 'DXB', 'FUJ', 'RAK', 'SHJ', 'UMQ']),
    ('sukoon-healthcare-providers-current', 'Sukoon Healthcare Providers Network August 2026', 'Sukoon Insurance', 'Both', ['AJM', 'AUH', 'DXB', 'FUJ', 'RAK', 'SHJ', 'UMQ'], 'Sukoon Healthcare Providers Network August 2026'),
    ('gig-a1-dubai',       'GIG Gulf A.1 Dubai Outpatient', 'GIG Gulf A1 Dubai', 'Outpatient', ['DXB']),
    ('gig-a1-current',     'GIG Gulf A.1 Current Outpatient', 'GIG Gulf', 'Outpatient', ['AJM', 'AUH', 'DXB', 'FUJ', 'RAK', 'SHJ', 'UMQ'], 'GIG Gulf A.1 Current'),
    ('gig-a1-abu-dhabi',   'GIG Gulf A.1 Abu Dhabi Outpatient', 'GIG Gulf A1 Abu Dhabi', 'Outpatient', ['AUH']),
    ('gig-a1-northern',    'GIG Gulf A.1 Northern Emirates Outpatient', 'GIG Gulf A1 UAE Northern', 'Outpatient', ['AJM', 'FUJ', 'RAK', 'SHJ', 'UMQ']),
    ('gig-a1-uae-all',     'GIG Gulf A.1 UAE Outpatient', 'GIG Gulf A1 UAE All', 'Outpatient', ['AJM', 'AUH', 'DXB', 'FUJ', 'RAK', 'SHJ', 'UMQ']),
    ('gig-a2-uae-all',     'GIG Gulf A.2 UAE Outpatient', 'GIG Gulf A2 UAE All', 'Outpatient', ['AJM', 'AUH', 'DXB', 'FUJ', 'RAK', 'SHJ', 'UMQ']),
    ('gig-a2-ip',          'GIG Gulf A.2 UAE Inpatient', 'GIG Gulf A2 IP', 'Inpatient', ['AJM', 'AUH', 'DXB', 'FUJ', 'RAK', 'SHJ', 'UMQ']),
    ('gig-a2-plus',       'GIG Gulf A.2 Plus Outpatient', 'GIG Gulf A2 Plus', 'Outpatient', ['AJM', 'AUH', 'DXB', 'FUJ', 'RAK', 'SHJ', 'UMQ']),
    ('gig-a2-plus-ip',    'GIG Gulf A.2 Plus Inpatient', 'GIG Gulf A2 Plus IP', 'Inpatient', ['AJM', 'AUH', 'DXB', 'FUJ', 'RAK', 'SHJ', 'UMQ']),
    ('gig-a3-uae-all',     'GIG Gulf A.3 UAE Outpatient', 'GIG Gulf A3 UAE All', 'Outpatient', ['AJM', 'AUH', 'DXB', 'FUJ', 'RAK', 'SHJ', 'UMQ']),
    ('gig-a3-base',        'GIG Gulf A.3 Base Outpatient', 'GIG Gulf A3', 'Outpatient', ['AJM', 'AUH', 'DXB', 'FUJ', 'RAK', 'SHJ', 'UMQ']),
    ('gig-a3-ip',          'GIG Gulf A.3 UAE Inpatient', 'GIG Gulf A3 IP', 'Inpatient', ['AJM', 'AUH', 'DXB', 'FUJ', 'RAK', 'SHJ', 'UMQ']),
    ('gig-a3-seha',        'GIG Gulf A.3 plus SEHA Outpatient', 'GIG Gulf A3 plus SEHA', 'Outpatient', ['AUH', 'ALAIN']),
    ('gig-a3-seha-ip',     'GIG Gulf A.3 plus SEHA Inpatient', 'GIG Gulf A3 plus SEHA IP', 'Inpatient', ['AUH', 'ALAIN']),
    ('gig-a3-mediclinic',  'GIG Gulf A.3 plus Mediclinic Outpatient', 'GIG Gulf A3 plus Mediclinic', 'Outpatient', ['AJM', 'AUH', 'DXB', 'FUJ', 'RAK', 'SHJ', 'UMQ']),
    ('gig-a3-mediclinic-ip', 'GIG Gulf A.3 plus Mediclinic Inpatient', 'GIG Gulf A3 plus Mediclinic IP', 'Inpatient', ['AJM', 'AUH', 'DXB', 'FUJ', 'RAK', 'SHJ', 'UMQ']),
    ('gig-a3-a',          'GIG Gulf A.3 A Outpatient', 'GIG Gulf A3 A', 'Outpatient', ['AJM', 'AUH', 'DXB', 'FUJ', 'RAK', 'SHJ', 'UMQ']),
    ('gig-a3-awali',      'GIG Gulf A.3 + AWALI HOSP Outpatient', 'GIG Gulf A3 AWALI HOSP', 'Outpatient', ['AJM', 'AUH', 'DXB', 'FUJ', 'RAK', 'SHJ', 'UMQ']),
    ('gig-a3-awali-ip',   'GIG Gulf A.3 + AWALI HOSP Inpatient', 'GIG Gulf A3 AWALI HOSP IP', 'Inpatient', ['AJM', 'AUH', 'DXB', 'FUJ', 'RAK', 'SHJ', 'UMQ']),
    ('gig-a3-a-ip',       'GIG Gulf A.3 A Inpatient', 'GIG Gulf A3 A IP', 'Inpatient', ['AJM', 'AUH', 'DXB', 'FUJ', 'RAK', 'SHJ', 'UMQ']),
    ('gig-a4-uae-all',     'GIG Gulf A.4 UAE Outpatient', 'GIG Gulf A4 UAE All', 'Outpatient', ['AJM', 'AUH', 'DXB', 'FUJ', 'RAK', 'SHJ', 'UMQ']),
    ('gig-a4-ip',          'GIG Gulf A.4 UAE Inpatient', 'GIG Gulf A4 IP', 'Inpatient', ['AJM', 'AUH', 'DXB', 'FUJ', 'RAK', 'SHJ', 'UMQ']),
    ('gig-a4-burjeel',     'GIG Gulf A.4 Burjeel Outpatient', 'GIG Gulf A4 Burjeel', 'Outpatient', ['AJM', 'AUH', 'DXB', 'FUJ', 'RAK', 'SHJ', 'UMQ']),
    ('gig-a4-burjeel-ip',  'GIG Gulf A.4 Burjeel Inpatient', 'GIG Gulf A4 Burjeel IP', 'Inpatient', ['AJM', 'AUH', 'DXB', 'FUJ', 'RAK', 'SHJ', 'UMQ']),
    ('gig-a4-nmc-royal-shj-ip', 'GIG Gulf A.4 NMC Royal Sharjah Inpatient', 'GIG Gulf A4 NMC Royal Shj IP', 'Inpatient', ['SHJ']),
    ('gig-a4-nmc-royal-shj', 'GIG Gulf A.4 NMC Royal Sharjah Outpatient', 'GIG Gulf A4 NMC Royal Shj', 'Outpatient', ['SHJ']),
    ('gig-a2-dubai',       'GIG Gulf A.2 Dubai Outpatient', 'GIG Gulf A2 Dubai', 'Outpatient', ['DXB']),
    ('gig-a3-dubai',       'GIG Gulf A.3 Dubai Outpatient', 'GIG Gulf A3 Dubai', 'Outpatient', ['DXB']),
    ('gig-a4-dubai',       'GIG Gulf A.4 Dubai Outpatient', 'GIG Gulf A4 Dubai', 'Outpatient', ['DXB']),
    ('gig-a5-uae-all',     'GIG Gulf A.5 UAE Outpatient', 'GIG Gulf A5 All', 'Outpatient', ['AJM', 'AUH', 'DXB', 'FUJ', 'RAK', 'SHJ', 'UMQ']),
    ('gig-a5-prime',       'GIG Gulf A.5 + PRIME Outpatient', 'GIG Gulf A5 PRIME', 'Outpatient', ['AJM', 'AUH', 'DXB', 'FUJ', 'RAK', 'SHJ', 'UMQ']),
    ('gig-a5-ip',          'GIG Gulf A.5 UAE Inpatient', 'GIG Gulf A5 IP', 'Inpatient', ['AJM', 'AUH', 'DXB', 'FUJ', 'RAK', 'SHJ', 'UMQ']),
    ('gig-a5-prime-ip',    'GIG Gulf A.5 + PRIME Inpatient', 'GIG Gulf A5 PRIME IP', 'Inpatient', ['AJM', 'AUH', 'DXB', 'FUJ', 'RAK', 'SHJ', 'UMQ']),
    ('gig-a5-emirates',    'GIG Gulf A.5 + EMIRATES Outpatient', 'GIG Gulf A5 EMIRATES', 'Outpatient', ['AJM', 'AUH', 'DXB', 'FUJ', 'RAK', 'SHJ', 'UMQ']),
    ('gig-a5-emirates-ip', 'GIG Gulf A.5 + EMIRATES Inpatient', 'GIG Gulf A5 EMIRATES IP', 'Inpatient', ['AJM', 'AUH', 'DXB', 'FUJ', 'RAK', 'SHJ', 'UMQ']),
    ('gig-a1-plus-ex-ccad-current', 'GIG Gulf A.1 Plus excl. CCAD 2026', 'GIG Gulf', 'Both', ['AJM', 'AUH', 'DXB', 'FUJ', 'RAK', 'SHJ', 'UMQ'], 'GIG Gulf A.1 PLUS EX CCAD'),
    ('gig-a3-current', 'GIG Gulf A.3 Network 2026', 'GIG Gulf', 'Both', ['AJM', 'AUH', 'DXB', 'FUJ', 'RAK', 'SHJ', 'UMQ'], 'GIG Gulf A.3'),
    ('gig-a4-nmc-royal-shj-current', 'GIG Gulf A.4 NMC Royal Sharjah 2026', 'GIG Gulf', 'Both', ['SHJ'], 'GIG Gulf A.4 NMC Royal Shj'),
    ('gig-a5-emirates-current', 'GIG Gulf A.5 + Emirates 2026', 'GIG Gulf', 'Both', ['AJM', 'AUH', 'DXB', 'FUJ', 'RAK', 'SHJ', 'UMQ'], 'GIG Gulf A.5 + EMIRATES'),
    ('gig-a5-prime-current', 'GIG Gulf A.5 + Prime 2026', 'GIG Gulf', 'Both', ['AJM', 'AUH', 'DXB', 'FUJ', 'RAK', 'SHJ', 'UMQ'], 'GIG Gulf A.5 + PRIME'),
    ('gig-a1-tc1',         'GIG Gulf A.1 TC1 Outpatient', 'GIG Gulf A.1 TC1', 'Outpatient', ['AJM', 'AUH', 'DXB', 'FUJ', 'RAK', 'SHJ', 'UMQ']),
    ('gig-a1-tc1-ip',      'GIG Gulf A.1 TC1 Inpatient', 'GIG Gulf A1 TC1 IP', 'Inpatient', ['AJM', 'AUH', 'DXB', 'FUJ', 'RAK', 'SHJ', 'UMQ']),
    ('gig-a1-ip',          'GIG Gulf A.1 UAE Inpatient', 'GIG Gulf A1 IP', 'Inpatient', ['AJM', 'AUH', 'DXB', 'FUJ', 'RAK', 'SHJ', 'UMQ']),
    ('gig-a1-plus',        'GIG Gulf A.1 Plus Outpatient', 'GIG Gulf A1 Plus', 'Outpatient', ['AJM', 'AUH', 'DXB', 'FUJ', 'RAK', 'SHJ', 'UMQ']),
    ('gig-a1-plus-ip',     'GIG Gulf A.1 Plus Inpatient', 'GIG Gulf A1 Plus IP', 'Inpatient', ['AJM', 'AUH', 'DXB', 'FUJ', 'RAK', 'SHJ', 'UMQ']),
    ('gig-a1-select',      'GIG Gulf A.1 Select Outpatient', 'GIG Gulf A1 Select', 'Outpatient', ['AJM', 'AUH', 'DXB', 'FUJ', 'RAK', 'SHJ', 'UMQ']),
    ('gig-a1-select-ip',   'GIG Gulf A.1 Select Inpatient', 'GIG Gulf A1 Select IP', 'Inpatient', ['AJM', 'AUH', 'DXB', 'FUJ', 'RAK', 'SHJ', 'UMQ']),
    ('gig-a1-plus-ex-ccad', 'GIG Gulf A.1 Plus Ex CCAD Outpatient', 'GIG Gulf A1 PLUS EX CCAD', 'Outpatient', ['AJM', 'AUH', 'DXB', 'FUJ', 'RAK', 'SHJ', 'UMQ']),
    ('gig-a1-plus-ex-ccad-ip', 'GIG Gulf A.1 Plus Ex CCAD Inpatient', 'GIG Gulf A1 PLUS EX CCAD IP', 'Inpatient', ['AJM', 'AUH', 'DXB', 'FUJ', 'RAK', 'SHJ', 'UMQ']),
    ('gig-a1-ex-mcme',     'GIG Gulf A.1 Ex MCME Outpatient', 'GIG Gulf A1 EX MCME', 'Outpatient', ['AJM', 'AUH', 'DXB', 'FUJ', 'RAK', 'SHJ', 'UMQ']),
    ('gig-a1-ex-mcme-ip',  'GIG Gulf A.1 Ex MCME Inpatient', 'GIG Gulf A1 EX MCME IP', 'Inpatient', ['AJM', 'AUH', 'DXB', 'FUJ', 'RAK', 'SHJ', 'UMQ']),
    ('gig-a1-ex-mch-ahd',  'GIG Gulf A.1 Ex MCH + AHD Outpatient', 'GIG Gulf A1 EX MCH AHD', 'Outpatient', ['AJM', 'AUH', 'DXB', 'FUJ', 'RAK', 'SHJ', 'UMQ']),
    ('gig-a1-ex-mch-ahd-ip', 'GIG Gulf A.1 Ex MCH + AHD Inpatient', 'GIG Gulf A1 EX MCH AHD IP', 'Inpatient', ['AJM', 'AUH', 'DXB', 'FUJ', 'RAK', 'SHJ', 'UMQ']),
    ('gig-a1-ex-al-zahra',  'GIG Gulf A.1 Exc Al Zahra Outpatient', 'GIG Gulf A1 Exc Al Zahra', 'Outpatient', ['AJM', 'AUH', 'DXB', 'FUJ', 'RAK', 'SHJ', 'UMQ']),
    ('gig-a1-ex-al-zahra-ip', 'GIG Gulf A.1 Exc Al Zahra Inpatient', 'GIG Gulf A1 Exc Al Zahra IP', 'Inpatient', ['AJM', 'AUH', 'DXB', 'FUJ', 'RAK', 'SHJ', 'UMQ']),
    ('gig-a1-excl-ccad',    'GIG Gulf A.1 excl CCAD Outpatient', 'GIG Gulf A1 excl CCAD', 'Outpatient', ['AJM', 'AUH', 'DXB', 'FUJ', 'RAK', 'SHJ', 'UMQ']),
    ('gig-a1-excl-ccad-ahd', 'GIG Gulf A.1 excl CCAD/AHD Outpatient', 'GIG Gulf A1 excl CCAD AHD', 'Outpatient', ['AJM', 'AUH', 'DXB', 'FUJ', 'RAK', 'SHJ', 'UMQ']),
    ('gig-a1-excl-ccad-ahd-ip', 'GIG Gulf A.1 excl CCAD/AHD Inpatient', 'GIG Gulf A1 excl CCAD AHD IP', 'Inpatient', ['AJM', 'AUH', 'DXB', 'FUJ', 'RAK', 'SHJ', 'UMQ']),
    ('gig-a1-excl-ccad-ip', 'GIG Gulf A.1 excl CCAD Inpatient', 'GIG Gulf A1 excl CCAD IP', 'Inpatient', ['AJM', 'AUH', 'DXB', 'FUJ', 'RAK', 'SHJ', 'UMQ']),
    ('gig-a1-excl-al-ahli', 'GIG Gulf A.1 Excl Al Ahli Outpatient', 'GIG Gulf A.1 EXCL AL AHLI', 'Outpatient', ['AJM', 'AUH', 'DXB', 'FUJ', 'RAK', 'SHJ', 'UMQ']),
    ('gig-a1-excl-al-ahli-ip', 'GIG Gulf A.1 Excl Al Ahli Inpatient', 'GIG Gulf A1 EXCL AL AHLI IP', 'Inpatient', ['AJM', 'AUH', 'DXB', 'FUJ', 'RAK', 'SHJ', 'UMQ']),
    ('gig-a6-uae-all',     'GIG Gulf A.6 UAE Outpatient', 'GIG Gulf A6 All', 'Outpatient', ['AJM', 'AUH', 'DXB', 'FUJ', 'RAK', 'SHJ', 'UMQ']),
    ('gig-a6-ip',          'GIG Gulf A.6 UAE Inpatient', 'GIG Gulf A6 IP', 'Inpatient', ['AJM', 'AUH', 'DXB', 'FUJ', 'RAK', 'SHJ', 'UMQ']),
    ('gig-eco-dxb-op',     'GIG Gulf Eco Dubai Outpatient', 'GIG Gulf Eco DXB OP', 'Outpatient', ['DXB']),
    ('gig-eco-dxb-ip',     'GIG Gulf Eco Dubai Inpatient', 'GIG Gulf Eco DXB IP', 'Inpatient', ['DXB']),
    ('gig-aeco1-uae-all',   'GIG Gulf A.Eco 1 UAE Outpatient', 'GIG Gulf AEco1 All', 'Outpatient', ['AJM', 'AUH', 'DXB', 'FUJ', 'RAK', 'SHJ', 'UMQ']),
    ('gig-aeco1-ip',        'GIG Gulf A.Eco 1 UAE Inpatient', 'GIG Gulf AEco1 IP', 'Inpatient', ['AJM', 'AUH', 'DXB', 'FUJ', 'RAK', 'SHJ', 'UMQ']),
    ('gig-aeco1-clinics',   'GIG Gulf A.Eco 1 Clinics', 'GIG Gulf AEco1 Clinics', 'Outpatient', ['AJM', 'AUH', 'DXB', 'FUJ', 'RAK', 'SHJ', 'UMQ']),
    ('gig-aeco1-clinics-ip', 'GIG Gulf A.Eco 1 Clinics Inpatient', 'GIG Gulf AEco1 Clinics IP', 'Inpatient', ['AJM', 'AUH', 'DXB', 'FUJ', 'RAK', 'SHJ', 'UMQ']),
    ('gig-aeco1-exc-sharq', 'GIG Gulf A.Eco 1 Exc Al Sharq', 'GIG Gulf AEco1 Exc Al Sharq', 'Outpatient', ['AJM', 'AUH', 'DXB', 'FUJ', 'RAK', 'SHJ', 'UMQ']),
    ('gig-aeco1-exc-sharq-ip', 'GIG Gulf A.Eco 1 Exc Al Sharq Inpatient', 'GIG Gulf AEco1 Exc Al Sharq IP', 'Inpatient', ['AJM', 'AUH', 'DXB', 'FUJ', 'RAK', 'SHJ', 'UMQ']),
    ('adico-classic',      'ADNIC Classic',              'ADNIC',              'Inpatient',  ['AUH']),
    ('adico-premium',      'ADNIC Premium',              'ADNIC',              'Both',       ['AUH']),
    ('adamjee-mednet-gold-2023', 'Adamjee MedNet Gold (July 2023)', 'Adamjee Insurance', 'Both', ['AJM', 'DXB', 'FUJ', 'RAK', 'SHJ', 'UMQ'], 'Adamjee MedNet Gold July 2023'),
    ('adamjee-mednet-silver-premium-2023', 'Adamjee MedNet Silver Premium (July 2023)', 'Adamjee Insurance', 'Both', ['AJM', 'DXB', 'FUJ', 'RAK', 'SHJ', 'UMQ'], 'Adamjee MedNet Silver Premium July 2023'),
    ('adamjee-mednet-silver-classic-2023', 'Adamjee MedNet Silver Classic (July 2023)', 'Adamjee Insurance', 'Both', ['AJM', 'DXB', 'FUJ', 'RAK', 'SHJ', 'UMQ'], 'Adamjee MedNet Silver Classic July 2023'),
    ('adamjee-mednet-green-2023', 'Adamjee MedNet Green (July 2023)', 'Adamjee Insurance', 'Both', ['AJM', 'DXB', 'FUJ', 'RAK', 'SHJ', 'UMQ'], 'Adamjee MedNet Green July 2023'),
    ('adamjee-mednet-emerald-2023', 'Adamjee MedNet Emerald (July 2023)', 'Adamjee Insurance', 'Both', ['AJM', 'DXB', 'FUJ', 'RAK', 'SHJ', 'UMQ'], 'Adamjee MedNet Emerald July 2023'),
    ('adamjee-mednet-pearl-2023', 'Adamjee MedNet Pearl (July 2023)', 'Adamjee Insurance', 'Both', ['AJM', 'DXB', 'FUJ', 'RAK', 'SHJ', 'UMQ'], 'Adamjee MedNet Pearl July 2023'),
    ('adamjee-mednet-silk-road-op-2023', 'Adamjee MedNet Silk Road OP (July 2023)', 'Adamjee Insurance', 'Outpatient', ['AJM', 'DXB', 'FUJ', 'RAK', 'SHJ', 'UMQ'], 'Adamjee MedNet Silk Road OP July 2023'),
    ('adamjee-mednet-silk-road-ip-2023', 'Adamjee MedNet Silk Road IP (July 2023)', 'Adamjee Insurance', 'Inpatient', ['AJM', 'DXB', 'FUJ', 'RAK', 'SHJ', 'UMQ'], 'Adamjee MedNet Silk Road IP July 2023'),
    ('adamjee-mednet-ebp-op-2023', 'Adamjee MedNet EBP OP (July 2023)', 'Adamjee Insurance', 'Outpatient', ['DXB'], 'Adamjee MedNet EBP OP July 2023'),
    ('adamjee-mednet-ebp-ip-2023', 'Adamjee MedNet EBP IP (July 2023)', 'Adamjee Insurance', 'Inpatient', ['DXB'], 'Adamjee MedNet EBP IP July 2023'),
    ('adamjee-mednet-dental-2023', 'Adamjee MedNet Dental (July 2023)', 'Adamjee Insurance', 'Both', ['AJM', 'DXB', 'FUJ', 'RAK', 'SHJ', 'UMQ'], 'Adamjee MedNet Dental July 2023'),
    ('axa-basic',          'AXA Gulf Basic',             'AXA Gulf',           'Inpatient',  ['DXB', 'AUH', 'SHJ']),
    ('axa-premier',        'AXA Gulf Premier',           'AXA Gulf',           'Both',       ['DXB', 'AUH', 'SHJ']),
    ('axa-gig-a1-dubai',   'AXA Gulf via GIG A.1 Dubai Outpatient', 'AXA Gulf', 'Outpatient', ['DXB'], 'GIG Gulf A1 Dubai'),
    ('axa-gig-a1-auh',     'AXA Gulf via GIG A.1 Abu Dhabi Outpatient', 'AXA Gulf', 'Outpatient', ['AUH'], 'GIG Gulf A1 Abu Dhabi'),
    ('axa-gig-a2-auh',     'AXA Gulf via GIG A.2 Abu Dhabi Outpatient', 'AXA Gulf', 'Outpatient', ['AUH'], 'GIG Gulf A2 Abu Dhabi'),
    ('axa-gig-a3-auh',     'AXA Gulf via GIG A.3 Abu Dhabi Outpatient', 'AXA Gulf', 'Outpatient', ['AUH'], 'GIG Gulf A3 Abu Dhabi'),
    ('axa-gig-a4-auh',     'AXA Gulf via GIG A.4 Abu Dhabi Outpatient', 'AXA Gulf', 'Outpatient', ['AUH'], 'GIG Gulf A4 Abu Dhabi'),
    ('axa-gig-a2-dubai',   'AXA Gulf via GIG A.2 Dubai Outpatient', 'AXA Gulf', 'Outpatient', ['DXB'], 'GIG Gulf A2 Dubai'),
    ('axa-gig-a3-dubai',   'AXA Gulf via GIG A.3 Dubai Outpatient', 'AXA Gulf', 'Outpatient', ['DXB'], 'GIG Gulf A3 Dubai'),
    ('axa-gig-a4-dubai',   'AXA Gulf via GIG A.4 Dubai Outpatient', 'AXA Gulf', 'Outpatient', ['DXB'], 'GIG Gulf A4 Dubai'),
    ('axa-gig-a1-northern', 'AXA Gulf via GIG A.1 Northern Emirates Outpatient', 'AXA Gulf', 'Outpatient', ['AJM', 'FUJ', 'RAK', 'SHJ', 'UMQ'], 'GIG Gulf A1 UAE Northern'),
    ('axa-gig-a1-uae-all',  'AXA Gulf via GIG A.1 UAE Outpatient', 'AXA Gulf', 'Outpatient', ['AJM', 'AUH', 'DXB', 'FUJ', 'RAK', 'SHJ', 'UMQ'], 'GIG Gulf A1 UAE All'),
    ('axa-gig-a2-uae-all',  'AXA Gulf via GIG A.2 UAE Outpatient', 'AXA Gulf', 'Outpatient', ['AJM', 'AUH', 'DXB', 'FUJ', 'RAK', 'SHJ', 'UMQ'], 'GIG Gulf A2 UAE All'),
    ('axa-gig-a2-ip',       'AXA Gulf via GIG A.2 UAE Inpatient', 'AXA Gulf', 'Inpatient', ['AJM', 'AUH', 'DXB', 'FUJ', 'RAK', 'SHJ', 'UMQ'], 'GIG Gulf A2 IP'),
    ('axa-gig-a2-plus',    'AXA Gulf via GIG A.2 Plus Outpatient', 'AXA Gulf', 'Outpatient', ['AJM', 'AUH', 'DXB', 'FUJ', 'RAK', 'SHJ', 'UMQ'], 'GIG Gulf A2 Plus'),
    ('axa-gig-a2-plus-ip', 'AXA Gulf via GIG A.2 Plus Inpatient', 'AXA Gulf', 'Inpatient', ['AJM', 'AUH', 'DXB', 'FUJ', 'RAK', 'SHJ', 'UMQ'], 'GIG Gulf A2 Plus IP'),
    ('axa-gig-a3-uae-all',  'AXA Gulf via GIG A.3 UAE Outpatient', 'AXA Gulf', 'Outpatient', ['AJM', 'AUH', 'DXB', 'FUJ', 'RAK', 'SHJ', 'UMQ'], 'GIG Gulf A3 UAE All'),
    ('axa-gig-a3-base',     'AXA Gulf via GIG A.3 Base Outpatient', 'AXA Gulf', 'Outpatient', ['AJM', 'AUH', 'DXB', 'FUJ', 'RAK', 'SHJ', 'UMQ'], 'GIG Gulf A3'),
    ('axa-gig-a3-ip',       'AXA Gulf via GIG A.3 UAE Inpatient', 'AXA Gulf', 'Inpatient', ['AJM', 'AUH', 'DXB', 'FUJ', 'RAK', 'SHJ', 'UMQ'], 'GIG Gulf A3 IP'),
    ('axa-gig-a3-seha',     'AXA Gulf via GIG A.3 plus SEHA Outpatient', 'AXA Gulf', 'Outpatient', ['AUH', 'ALAIN'], 'GIG Gulf A3 plus SEHA'),
    ('axa-gig-a3-seha-ip',  'AXA Gulf via GIG A.3 plus SEHA Inpatient', 'AXA Gulf', 'Inpatient', ['AUH', 'ALAIN'], 'GIG Gulf A3 plus SEHA IP'),
    ('axa-gig-a3-mediclinic', 'AXA Gulf via GIG A.3 plus Mediclinic Outpatient', 'AXA Gulf', 'Outpatient', ['AJM', 'AUH', 'DXB', 'FUJ', 'RAK', 'SHJ', 'UMQ'], 'GIG Gulf A3 plus Mediclinic'),
    ('axa-gig-a3-mediclinic-ip', 'AXA Gulf via GIG A.3 plus Mediclinic Inpatient', 'AXA Gulf', 'Inpatient', ['AJM', 'AUH', 'DXB', 'FUJ', 'RAK', 'SHJ', 'UMQ'], 'GIG Gulf A3 plus Mediclinic IP'),
    ('axa-gig-a3-a',       'AXA Gulf via GIG A.3 A Outpatient', 'AXA Gulf', 'Outpatient', ['AJM', 'AUH', 'DXB', 'FUJ', 'RAK', 'SHJ', 'UMQ'], 'GIG Gulf A3 A'),
    ('axa-gig-a3-awali',   'AXA Gulf via GIG A.3 + AWALI HOSP Outpatient', 'AXA Gulf', 'Outpatient', ['AJM', 'AUH', 'DXB', 'FUJ', 'RAK', 'SHJ', 'UMQ'], 'GIG Gulf A3 AWALI HOSP'),
    ('axa-gig-a3-awali-ip', 'AXA Gulf via GIG A.3 + AWALI HOSP Inpatient', 'AXA Gulf', 'Inpatient', ['AJM', 'AUH', 'DXB', 'FUJ', 'RAK', 'SHJ', 'UMQ'], 'GIG Gulf A3 AWALI HOSP IP'),
    ('axa-gig-a3-a-ip',    'AXA Gulf via GIG A.3 A Inpatient', 'AXA Gulf', 'Inpatient', ['AJM', 'AUH', 'DXB', 'FUJ', 'RAK', 'SHJ', 'UMQ'], 'GIG Gulf A3 A IP'),
    ('axa-gig-a4-uae-all',  'AXA Gulf via GIG A.4 UAE Outpatient', 'AXA Gulf', 'Outpatient', ['AJM', 'AUH', 'DXB', 'FUJ', 'RAK', 'SHJ', 'UMQ'], 'GIG Gulf A4 UAE All'),
    ('axa-gig-a4-ip',       'AXA Gulf via GIG A.4 UAE Inpatient', 'AXA Gulf', 'Inpatient', ['AJM', 'AUH', 'DXB', 'FUJ', 'RAK', 'SHJ', 'UMQ'], 'GIG Gulf A4 IP'),
    ('axa-gig-a4-burjeel',  'AXA Gulf via GIG A.4 Burjeel Outpatient', 'AXA Gulf', 'Outpatient', ['AJM', 'AUH', 'DXB', 'FUJ', 'RAK', 'SHJ', 'UMQ'], 'GIG Gulf A4 Burjeel'),
    ('axa-gig-a4-burjeel-ip', 'AXA Gulf via GIG A.4 Burjeel Inpatient', 'AXA Gulf', 'Inpatient', ['AJM', 'AUH', 'DXB', 'FUJ', 'RAK', 'SHJ', 'UMQ'], 'GIG Gulf A4 Burjeel IP'),
    ('axa-gig-a4-nmc-royal-shj-ip', 'AXA Gulf via GIG A.4 NMC Royal Sharjah Inpatient', 'AXA Gulf', 'Inpatient', ['SHJ'], 'GIG Gulf A4 NMC Royal Shj IP'),
    ('axa-gig-a4-nmc-royal-shj', 'AXA Gulf via GIG A.4 NMC Royal Sharjah Outpatient', 'AXA Gulf', 'Outpatient', ['SHJ'], 'GIG Gulf A4 NMC Royal Shj'),
    ('axa-gig-a5-uae-all',  'AXA Gulf via GIG A.5 UAE Outpatient', 'AXA Gulf', 'Outpatient', ['AJM', 'AUH', 'DXB', 'FUJ', 'RAK', 'SHJ', 'UMQ'], 'GIG Gulf A5 All'),
    ('axa-gig-a5-prime',    'AXA Gulf via GIG A.5 + PRIME Outpatient', 'AXA Gulf', 'Outpatient', ['AJM', 'AUH', 'DXB', 'FUJ', 'RAK', 'SHJ', 'UMQ'], 'GIG Gulf A5 PRIME'),
    ('axa-gig-a5-ip',       'AXA Gulf via GIG A.5 UAE Inpatient', 'AXA Gulf', 'Inpatient', ['AJM', 'AUH', 'DXB', 'FUJ', 'RAK', 'SHJ', 'UMQ'], 'GIG Gulf A5 IP'),
    ('axa-gig-a5-prime-ip', 'AXA Gulf via GIG A.5 + PRIME Inpatient', 'AXA Gulf', 'Inpatient', ['AJM', 'AUH', 'DXB', 'FUJ', 'RAK', 'SHJ', 'UMQ'], 'GIG Gulf A5 PRIME IP'),
    ('axa-gig-a5-emirates', 'AXA Gulf via GIG A.5 + EMIRATES Outpatient', 'AXA Gulf', 'Outpatient', ['AJM', 'AUH', 'DXB', 'FUJ', 'RAK', 'SHJ', 'UMQ'], 'GIG Gulf A5 EMIRATES'),
    ('axa-gig-a5-emirates-ip', 'AXA Gulf via GIG A.5 + EMIRATES Inpatient', 'AXA Gulf', 'Inpatient', ['AJM', 'AUH', 'DXB', 'FUJ', 'RAK', 'SHJ', 'UMQ'], 'GIG Gulf A5 EMIRATES IP'),
    ('axa-gig-a1-tc1',      'AXA Gulf via GIG A.1 TC1 Outpatient', 'AXA Gulf', 'Outpatient', ['AJM', 'AUH', 'DXB', 'FUJ', 'RAK', 'SHJ', 'UMQ'], 'GIG Gulf A.1 TC1'),
    ('axa-gig-a1-tc1-ip',   'AXA Gulf via GIG A.1 TC1 Inpatient', 'AXA Gulf', 'Inpatient', ['AJM', 'AUH', 'DXB', 'FUJ', 'RAK', 'SHJ', 'UMQ'], 'GIG Gulf A1 TC1 IP'),
    ('axa-gig-a1-ip',       'AXA Gulf via GIG A.1 UAE Inpatient', 'AXA Gulf', 'Inpatient', ['AJM', 'AUH', 'DXB', 'FUJ', 'RAK', 'SHJ', 'UMQ'], 'GIG Gulf A1 IP'),
    ('axa-gig-a1-plus',     'AXA Gulf via GIG A.1 Plus Outpatient', 'AXA Gulf', 'Outpatient', ['AJM', 'AUH', 'DXB', 'FUJ', 'RAK', 'SHJ', 'UMQ'], 'GIG Gulf A1 Plus'),
    ('axa-gig-a1-plus-ip',  'AXA Gulf via GIG A.1 Plus Inpatient', 'AXA Gulf', 'Inpatient', ['AJM', 'AUH', 'DXB', 'FUJ', 'RAK', 'SHJ', 'UMQ'], 'GIG Gulf A1 Plus IP'),
    ('axa-gig-a1-select',   'AXA Gulf via GIG A.1 Select Outpatient', 'AXA Gulf', 'Outpatient', ['AJM', 'AUH', 'DXB', 'FUJ', 'RAK', 'SHJ', 'UMQ'], 'GIG Gulf A1 Select'),
    ('axa-gig-a1-select-ip', 'AXA Gulf via GIG A.1 Select Inpatient', 'AXA Gulf', 'Inpatient', ['AJM', 'AUH', 'DXB', 'FUJ', 'RAK', 'SHJ', 'UMQ'], 'GIG Gulf A1 Select IP'),
    ('axa-gig-a1-plus-ex-ccad', 'AXA Gulf via GIG A.1 Plus Ex CCAD Outpatient', 'AXA Gulf', 'Outpatient', ['AJM', 'AUH', 'DXB', 'FUJ', 'RAK', 'SHJ', 'UMQ'], 'GIG Gulf A1 PLUS EX CCAD'),
    ('axa-gig-a1-plus-ex-ccad-ip', 'AXA Gulf via GIG A.1 Plus Ex CCAD Inpatient', 'AXA Gulf', 'Inpatient', ['AJM', 'AUH', 'DXB', 'FUJ', 'RAK', 'SHJ', 'UMQ'], 'GIG Gulf A1 PLUS EX CCAD IP'),
    ('axa-gig-a1-ex-mcme',  'AXA Gulf via GIG A.1 Ex MCME Outpatient', 'AXA Gulf', 'Outpatient', ['AJM', 'AUH', 'DXB', 'FUJ', 'RAK', 'SHJ', 'UMQ'], 'GIG Gulf A1 EX MCME'),
    ('axa-gig-a1-ex-mcme-ip', 'AXA Gulf via GIG A.1 Ex MCME Inpatient', 'AXA Gulf', 'Inpatient', ['AJM', 'AUH', 'DXB', 'FUJ', 'RAK', 'SHJ', 'UMQ'], 'GIG Gulf A1 EX MCME IP'),
    ('axa-gig-a1-ex-mch-ahd', 'AXA Gulf via GIG A.1 Ex MCH + AHD Outpatient', 'AXA Gulf', 'Outpatient', ['AJM', 'AUH', 'DXB', 'FUJ', 'RAK', 'SHJ', 'UMQ'], 'GIG Gulf A1 EX MCH AHD'),
    ('axa-gig-a1-ex-mch-ahd-ip', 'AXA Gulf via GIG A.1 Ex MCH + AHD Inpatient', 'AXA Gulf', 'Inpatient', ['AJM', 'AUH', 'DXB', 'FUJ', 'RAK', 'SHJ', 'UMQ'], 'GIG Gulf A1 EX MCH AHD IP'),
    ('axa-gig-a1-ex-al-zahra', 'AXA Gulf via GIG A.1 Exc Al Zahra Outpatient', 'AXA Gulf', 'Outpatient', ['AJM', 'AUH', 'DXB', 'FUJ', 'RAK', 'SHJ', 'UMQ'], 'GIG Gulf A1 Exc Al Zahra'),
    ('axa-gig-a1-ex-al-zahra-ip', 'AXA Gulf via GIG A.1 Exc Al Zahra Inpatient', 'AXA Gulf', 'Inpatient', ['AJM', 'AUH', 'DXB', 'FUJ', 'RAK', 'SHJ', 'UMQ'], 'GIG Gulf A1 Exc Al Zahra IP'),
    ('axa-gig-a1-excl-ccad',  'AXA Gulf via GIG A.1 excl CCAD Outpatient', 'AXA Gulf', 'Outpatient', ['AJM', 'AUH', 'DXB', 'FUJ', 'RAK', 'SHJ', 'UMQ'], 'GIG Gulf A1 excl CCAD'),
    ('axa-gig-a1-excl-ccad-ahd', 'AXA Gulf via GIG A.1 excl CCAD/AHD Outpatient', 'AXA Gulf', 'Outpatient', ['AJM', 'AUH', 'DXB', 'FUJ', 'RAK', 'SHJ', 'UMQ'], 'GIG Gulf A1 excl CCAD AHD'),
    ('axa-gig-a1-excl-ccad-ahd-ip', 'AXA Gulf via GIG A.1 excl CCAD/AHD Inpatient', 'AXA Gulf', 'Inpatient', ['AJM', 'AUH', 'DXB', 'FUJ', 'RAK', 'SHJ', 'UMQ'], 'GIG Gulf A1 excl CCAD AHD IP'),
    ('axa-gig-a1-excl-ccad-ip', 'AXA Gulf via GIG A.1 excl CCAD Inpatient', 'AXA Gulf', 'Inpatient', ['AJM', 'AUH', 'DXB', 'FUJ', 'RAK', 'SHJ', 'UMQ'], 'GIG Gulf A1 excl CCAD IP'),
    ('axa-gig-a1-excl-al-ahli', 'AXA Gulf via GIG A.1 Excl Al Ahli Outpatient', 'AXA Gulf', 'Outpatient', ['AJM', 'AUH', 'DXB', 'FUJ', 'RAK', 'SHJ', 'UMQ'], 'GIG Gulf A.1 EXCL AL AHLI'),
    ('axa-gig-a1-excl-al-ahli-ip', 'AXA Gulf via GIG A.1 Excl Al Ahli Inpatient', 'AXA Gulf', 'Inpatient', ['AJM', 'AUH', 'DXB', 'FUJ', 'RAK', 'SHJ', 'UMQ'], 'GIG Gulf A1 EXCL AL AHLI IP'),
    ('axa-gig-a6-uae-all',  'AXA Gulf via GIG A.6 UAE Outpatient', 'AXA Gulf', 'Outpatient', ['AJM', 'AUH', 'DXB', 'FUJ', 'RAK', 'SHJ', 'UMQ'], 'GIG Gulf A6 All'),
    ('axa-gig-a6-ip',       'AXA Gulf via GIG A.6 UAE Inpatient', 'AXA Gulf', 'Inpatient', ['AJM', 'AUH', 'DXB', 'FUJ', 'RAK', 'SHJ', 'UMQ'], 'GIG Gulf A6 IP'),
    ('axa-gig-eco-dxb-op',  'AXA Gulf via GIG Eco Dubai Outpatient', 'AXA Gulf', 'Outpatient', ['DXB'], 'GIG Gulf Eco DXB OP'),
    ('axa-gig-eco-dxb-ip',  'AXA Gulf via GIG Eco Dubai Inpatient', 'AXA Gulf', 'Inpatient', ['DXB'], 'GIG Gulf Eco DXB IP'),
    ('axa-gig-aeco1-uae-all', 'AXA Gulf via GIG A.Eco 1 UAE Outpatient', 'AXA Gulf', 'Outpatient', ['AJM', 'AUH', 'DXB', 'FUJ', 'RAK', 'SHJ', 'UMQ'], 'GIG Gulf AEco1 All'),
    ('axa-gig-aeco1-ip',      'AXA Gulf via GIG A.Eco 1 UAE Inpatient', 'AXA Gulf', 'Inpatient', ['AJM', 'AUH', 'DXB', 'FUJ', 'RAK', 'SHJ', 'UMQ'], 'GIG Gulf AEco1 IP'),
    ('axa-gig-aeco1-clinics', 'AXA Gulf via GIG A.Eco 1 Clinics', 'AXA Gulf', 'Outpatient', ['AJM', 'AUH', 'DXB', 'FUJ', 'RAK', 'SHJ', 'UMQ'], 'GIG Gulf AEco1 Clinics'),
    ('axa-gig-aeco1-clinics-ip', 'AXA Gulf via GIG A.Eco 1 Clinics Inpatient', 'AXA Gulf', 'Inpatient', ['AJM', 'AUH', 'DXB', 'FUJ', 'RAK', 'SHJ', 'UMQ'], 'GIG Gulf AEco1 Clinics IP'),
    ('axa-gig-aeco1-exc-sharq', 'AXA Gulf via GIG A.Eco 1 Exc Al Sharq', 'AXA Gulf', 'Outpatient', ['AJM', 'AUH', 'DXB', 'FUJ', 'RAK', 'SHJ', 'UMQ'], 'GIG Gulf AEco1 Exc Al Sharq'),
    ('axa-gig-aeco1-exc-sharq-ip', 'AXA Gulf via GIG A.Eco 1 Exc Al Sharq Inpatient', 'AXA Gulf', 'Inpatient', ['AJM', 'AUH', 'DXB', 'FUJ', 'RAK', 'SHJ', 'UMQ'], 'GIG Gulf AEco1 Exc Al Sharq IP'),
    ('aman-essential',     'Aman Essential',             'Aman Insurance',     'Outpatient', ['AJM', 'SHJ', 'FUJ', 'UMQ']),
    ('aman-comprehensive', 'Aman Comprehensive',         'Aman Insurance',     'Both',       ['AJM', 'SHJ', 'FUJ', 'UMQ']),
    ('aman-ecare-blue',    'Aman eCare Blue',             'Aman Insurance',     'Outpatient', ['AJM', 'AUH', 'DXB', 'FUJ', 'RAK', 'SHJ', 'UMQ'], 'Aman Insurance Blue'),
    ('aman-ecare-green',   'Aman eCare Green',            'Aman Insurance',     'Outpatient', ['AJM', 'AUH', 'DXB', 'FUJ', 'RAK', 'SHJ', 'UMQ'], 'Aman Insurance Green'),
    ('aman-ecare-classic', 'Aman eCare Classic',          'Aman Insurance',     'Both',       ['AJM', 'AUH', 'DXB', 'FUJ', 'RAK', 'SHJ', 'UMQ'], 'Aman Insurance Classic'),
    ('aman-ecare-silver',  'Aman eCare Silver',           'Aman Insurance',     'Both',       ['AJM', 'AUH', 'DXB', 'FUJ', 'RAK', 'SHJ', 'UMQ'], 'Aman Insurance Silver'),
    ('aman-ecare-gold',    'Aman eCare Gold',             'Aman Insurance',     'Both',       ['AJM', 'AUH', 'DXB', 'FUJ', 'RAK', 'SHJ', 'UMQ'], 'Aman Insurance Gold'),
    ('daric-standard',     'DARIC Standard',             'DARIC',              'Inpatient',  ['DXB', 'SHJ', 'AJM'], 'Neuron MaxHealth General Network August 2026'),
    ('daric-premium',      'DARIC Premium',              'DARIC',              'Both',       ['DXB', 'SHJ', 'AJM'], 'Neuron MaxHealth Comprehensive Network August 2026'),
    ('hayah-health-protect-tier-1', 'HAYAH Health Protect Regional Tier 1', 'HAYAH', 'Both', ['AJM', 'DXB', 'FUJ', 'RAK', 'SHJ', 'UMQ'], 'HAYAH MedNet Green'),
    ('hayah-health-protect-tier-2', 'HAYAH Health Protect Regional Tier 2', 'HAYAH', 'Both', ['AJM', 'DXB', 'FUJ', 'RAK', 'SHJ', 'UMQ'], 'HAYAH MedNet Silver Classic'),
    ('hayah-health-protect-tier-3', 'HAYAH Health Protect Worldwide Tier 3', 'HAYAH', 'Both', ['AJM', 'DXB', 'FUJ', 'RAK', 'SHJ', 'UMQ'], 'HAYAH MedNet Silver Premium'),
    ('hayah-health-protect-tier-4', 'HAYAH Health Protect Worldwide Tier 4', 'HAYAH', 'Both', ['AJM', 'DXB', 'FUJ', 'RAK', 'SHJ', 'UMQ'], 'HAYAH MedNet Silver Premium'),
    ('hayah-health-protect-tier-5', 'HAYAH Health Protect Worldwide Tier 5', 'HAYAH', 'Both', ['AJM', 'DXB', 'FUJ', 'RAK', 'SHJ', 'UMQ'], 'HAYAH MedNet Gold'),
    ('hayah-mednet-gold', 'HAYAH MedNet Gold Network', 'HAYAH', 'Both', ['AJM', 'AUH', 'DXB', 'FUJ', 'RAK', 'SHJ', 'UMQ'], 'HAYAH MedNet Gold'),
    ('hayah-mednet-silver-premium', 'HAYAH MedNet Silver Premium Network', 'HAYAH', 'Both', ['AJM', 'AUH', 'DXB', 'FUJ', 'RAK', 'SHJ', 'UMQ'], 'HAYAH MedNet Silver Premium'),
    ('hayah-mednet-silver-classic', 'HAYAH MedNet Silver Classic Network', 'HAYAH', 'Both', ['AJM', 'AUH', 'DXB', 'FUJ', 'RAK', 'SHJ', 'UMQ'], 'HAYAH MedNet Silver Classic'),
    ('hayah-mednet-green', 'HAYAH MedNet Green Network', 'HAYAH', 'Both', ['AJM', 'AUH', 'DXB', 'FUJ', 'RAK', 'SHJ', 'UMQ'], 'HAYAH MedNet Green'),
    ('hayah-mednet-emerald', 'HAYAH MedNet Emerald Network', 'HAYAH', 'Both', ['AJM', 'AUH', 'DXB', 'FUJ', 'RAK', 'SHJ', 'UMQ'], 'HAYAH MedNet Emerald'),
    ('hayah-mednet-pearl', 'HAYAH MedNet Pearl Network', 'HAYAH', 'Both', ['AJM', 'AUH', 'DXB', 'FUJ', 'RAK', 'SHJ', 'UMQ'], 'HAYAH MedNet Pearl'),
    ('hayah-mednet-silk-road-op', 'HAYAH MedNet Silk Road OP Network', 'HAYAH', 'Outpatient', ['AJM', 'AUH', 'DXB', 'FUJ', 'RAK', 'SHJ', 'UMQ'], 'HAYAH MedNet Silk Road OP'),
    ('hayah-mednet-ebp-op', 'HAYAH MedNet EBP OP Network', 'HAYAH', 'Outpatient', ['AJM', 'AUH', 'DXB', 'FUJ', 'RAK', 'SHJ', 'UMQ'], 'HAYAH MedNet EBP OP'),
    ('hayah-mednet-basic-op', 'HAYAH MedNet Basic OP Network', 'HAYAH', 'Outpatient', ['AJM', 'AUH', 'DXB', 'FUJ', 'RAK', 'SHJ', 'UMQ'], 'HAYAH MedNet Basic OP'),
    ('hayah-mednet-basic-ip', 'HAYAH MedNet Basic IP Network', 'HAYAH', 'Inpatient', ['AJM', 'AUH', 'DXB', 'FUJ', 'RAK', 'SHJ', 'UMQ'], 'HAYAH MedNet Basic IP'),
    ('hayah-mednet-ebp-ip', 'HAYAH MedNet EBP IP Network', 'HAYAH', 'Inpatient', ['AJM', 'AUH', 'DXB', 'FUJ', 'RAK', 'SHJ', 'UMQ'], 'HAYAH MedNet EBP IP'),
    ('hayah-mednet-silk-road-ip', 'HAYAH MedNet Silk Road IP Network', 'HAYAH', 'Inpatient', ['AJM', 'AUH', 'DXB', 'FUJ', 'RAK', 'SHJ', 'UMQ'], 'HAYAH MedNet Silk Road IP'),
    ('hayah-mednet-dental', 'HAYAH MedNet Dental Network', 'HAYAH', 'Outpatient', ['AJM', 'AUH', 'DXB', 'FUJ', 'RAK', 'SHJ', 'UMQ'], 'HAYAH MedNet Dental'),
    ('hayah-mednet-optical', 'HAYAH MedNet Optical Network', 'HAYAH', 'Outpatient', ['AJM', 'AUH', 'DXB', 'FUJ', 'RAK', 'SHJ', 'UMQ'], 'HAYAH MedNet Optical'),
    ('hayah-mednet-alternative', 'HAYAH MedNet Alternative Network', 'HAYAH', 'Both', ['AJM', 'AUH', 'DXB', 'FUJ', 'RAK', 'SHJ', 'UMQ'], 'HAYAH MedNet Alternative'),
    ('enbd-gold',          'Emirates NBD Gold',          'Emirates NBD Ins.',  'Both',       ['DXB', 'AUH']),
    ('enbd-silver',        'Emirates NBD Silver',        'Emirates NBD Ins.',  'Inpatient',  ['DXB', 'AUH']),
    ('enbd-orient-medical', 'Emirates NBD Employee Medical via Orient', 'Emirates NBD Ins.', 'Both', ['AJM', 'AUH', 'DXB', 'FUJ', 'RAK', 'SHJ', 'UMQ'], 'Orient Insurance'),
    ('cigna-ebp-value-lite', 'Cigna EBP Value Lite',        'Cigna Insurance', 'Both', ['AJM', 'AUH', 'DXB', 'FUJ', 'RAK', 'SHJ', 'UMQ'], 'Cigna EBP Value Lite Current'),
    ('cigna-healthguard-comprehensive', 'Cigna Healthguard Comprehensive', 'Cigna Insurance', 'Both', ['AJM', 'AUH', 'DXB', 'FUJ', 'RAK', 'SHJ', 'UMQ'], 'Cigna Healthguard Comprehensive Network'),
    ('cigna-healthguard-comprehensive-excl-ahd', 'Cigna Healthguard Comprehensive excl. AHD', 'Cigna Insurance', 'Both', ['AJM', 'AUH', 'DXB', 'FUJ', 'RAK', 'SHJ', 'UMQ'], 'Cigna Healthguard Comprehensive excl AHD Network'),
    ('cigna-healthguard-general', 'Cigna Healthguard General', 'Cigna Insurance', 'Both', ['AJM', 'AUH', 'DXB', 'FUJ', 'RAK', 'SHJ', 'UMQ'], 'Cigna Healthguard General Network'),
    ('liva-easy-health-gold-plus', 'Liva Easy Health Gold Plus', 'Liva Insurance', 'Both', ['AJM', 'AUH', 'DXB', 'FUJ', 'RAK', 'SHJ', 'UMQ'], 'Liva Inayah Gold August 2026'),
    ('liva-easy-health-gold', 'Liva Easy Health Gold', 'Liva Insurance', 'Both', ['AJM', 'AUH', 'DXB', 'FUJ', 'RAK', 'SHJ', 'UMQ'], 'Liva Inayah Gold August 2026'),
    ('liva-easy-health-bronze-plus', 'Liva Easy Health Bronze Plus', 'Liva Insurance', 'Both', ['AJM', 'AUH', 'DXB', 'FUJ', 'RAK', 'SHJ', 'UMQ'], 'Liva Inayah Bronze August 2026'),
    ('liva-easy-health-bronze', 'Liva Easy Health Bronze', 'Liva Insurance', 'Both', ['AJM', 'AUH', 'DXB', 'FUJ', 'RAK', 'SHJ', 'UMQ'], 'Liva Inayah Bronze August 2026'),
    ('liva-easy-health-chrome-plus', 'Liva Easy Health Chrome Plus', 'Liva Insurance', 'Both', ['AJM', 'AUH', 'DXB', 'FUJ', 'RAK', 'SHJ', 'UMQ'], 'Liva Inayah Chrome August 2026'),
    ('liva-easy-health-chrome', 'Liva Easy Health Chrome', 'Liva Insurance', 'Both', ['AJM', 'AUH', 'DXB', 'FUJ', 'RAK', 'SHJ', 'UMQ'], 'Liva Inayah Chrome August 2026'),
    ('liva-easy-health-opal-bh', 'Liva Easy Health Opal BH', 'Liva Insurance', 'Both', ['AJM', 'AUH', 'DXB', 'FUJ', 'RAK', 'SHJ', 'UMQ'], 'Liva Inayah ChromeLite August 2026'),
    ('liva-inayah-platinum', 'Liva Inayah Platinum', 'Liva Insurance', 'Both', ['AJM', 'AUH', 'DXB', 'FUJ', 'RAK', 'SHJ', 'UMQ'], 'Liva Inayah Platinum August 2026'),
    ('liva-inayah-diamond', 'Liva Inayah Diamond', 'Liva Insurance', 'Both', ['AJM', 'AUH', 'DXB', 'FUJ', 'RAK', 'SHJ', 'UMQ'], 'Liva Inayah Diamond August 2026'),
    ('liva-inayah-silver', 'Liva Inayah Silver', 'Liva Insurance', 'Both', ['AJM', 'AUH', 'DXB', 'FUJ', 'RAK', 'SHJ', 'UMQ'], 'Liva Inayah Silver August 2026'),
    ('liva-inayah-chromelite', 'Liva Inayah ChromeLite', 'Liva Insurance', 'Both', ['AJM', 'AUH', 'DXB', 'FUJ', 'RAK', 'SHJ', 'UMQ'], 'Liva Inayah ChromeLite August 2026'),
    ('liva-inayah-sapphire', 'Liva Inayah Sapphire', 'Liva Insurance', 'Both', ['AJM', 'AUH', 'DXB', 'FUJ', 'RAK', 'SHJ', 'UMQ'], 'Liva Inayah Sapphire August 2026'),
    ('liva-inayah-ebp', 'Liva Inayah EBP', 'Liva Insurance', 'Both', ['AJM', 'AUH', 'DXB', 'FUJ', 'RAK', 'SHJ', 'UMQ'], 'Liva Inayah EBP August 2026'),
    ('liva-nas-current', 'Liva NAS Network August 2026', 'Liva Insurance', 'Both', ['AJM', 'AUH', 'DXB', 'FUJ', 'RAK', 'SHJ', 'UMQ'], 'Liva NAS - Network List - Aug - 2026'),
    ('liva-neuron-current', 'Liva Neuron Network August 2026', 'Liva Insurance', 'Both', ['AJM', 'AUH', 'DXB', 'FUJ', 'RAK', 'SHJ', 'UMQ'], 'Liva Neuron - Network List - Aug - 2026'),
    ('liva-mednet-current', 'Liva Mednet Network August 2026', 'Liva Insurance', 'Both', ['AJM', 'AUH', 'DXB', 'FUJ', 'RAK', 'SHJ', 'UMQ'], 'Liva Mednet - Network List - Aug - 2026'),
    ('liva-nextcare-current', 'Liva NextCare Network August 2026', 'Liva Insurance', 'Both', ['AJM', 'AUH', 'DXB', 'FUJ', 'RAK', 'SHJ', 'UMQ'], 'Liva NextCare - Network List - Aug - 2026'),
    ('liva-nas-value', 'Liva NAS Value Network August 2026', 'Liva Insurance', 'Both', ['AJM', 'AUH', 'DXB', 'FUJ', 'RAK', 'SHJ', 'UMQ'], 'Liva NAS - Network List - Aug - 2026 - Value Network'),
    ('liva-nas-valuelite', 'Liva NAS ValueLite Network August 2026', 'Liva Insurance', 'Both', ['AJM', 'AUH', 'DXB', 'FUJ', 'RAK', 'SHJ', 'UMQ'], 'Liva NAS - Network List - Aug - 2026 - ValueLite Network'),
    ('liva-nas-workers-lite', 'Liva NAS Workers Lite Network August 2026', 'Liva Insurance', 'Both', ['AJM', 'AUH', 'DXB', 'FUJ', 'RAK', 'SHJ', 'UMQ'], 'Liva NAS - Network List - Aug - 2026 - Workers Lite Network'),
    ('liva-almadallah-elite', 'Liva Al Madallah Elite GN+', 'Liva Insurance', 'Both', ['AJM', 'AUH', 'DXB', 'FUJ', 'RAK', 'SHJ', 'UMQ'], 'Liva Al Madallah AM-Elite (GN+) August 2026'),
    ('liva-almadallah-premier', 'Liva Al Madallah Premier GN', 'Liva Insurance', 'Both', ['AJM', 'AUH', 'DXB', 'FUJ', 'RAK', 'SHJ', 'UMQ'], 'Liva Al Madallah AM-Premier (GN) August 2026'),
    ('liva-almadallah-advantage', 'Liva Al Madallah Advantage RN', 'Liva Insurance', 'Both', ['AJM', 'AUH', 'DXB', 'FUJ', 'RAK', 'SHJ', 'UMQ'], 'Liva Al Madallah AM-Advantage (RN) August 2026'),
    ('liva-almadallah-choice', 'Liva Al Madallah Choice RN2', 'Liva Insurance', 'Both', ['AJM', 'AUH', 'DXB', 'FUJ', 'RAK', 'SHJ', 'UMQ'], 'Liva Al Madallah AM-Choice (RN2) August 2026'),
    ('liva-almadallah-select', 'Liva Al Madallah Select RN3', 'Liva Insurance', 'Both', ['AJM', 'AUH', 'DXB', 'FUJ', 'RAK', 'SHJ', 'UMQ'], 'Liva Al Madallah AM-Select (RN3) August 2026'),
    ('liva-almadallah-access', 'Liva Al Madallah Access RN4', 'Liva Insurance', 'Both', ['AJM', 'AUH', 'DXB', 'FUJ', 'RAK', 'SHJ', 'UMQ'], 'Liva Al Madallah AM-Access (RN4) August 2026'),
    ('liva-almadallah-neo', 'Liva Al Madallah Neo RN5', 'Liva Insurance', 'Both', ['AJM', 'AUH', 'DXB', 'FUJ', 'RAK', 'SHJ', 'UMQ'], 'Liva Al Madallah AM-Neo (RN5) August 2026'),
    ('adntc-general', 'ADNTC General Network', 'Abu Dhabi National Takaful', 'Both', ['AJM', 'AUH', 'DXB', 'FUJ', 'RAK', 'SHJ', 'UMQ'], 'ADNTC NAS General Network August 2026'),
    ('adntc-restricted', 'ADNTC Restricted Network', 'Abu Dhabi National Takaful', 'Both', ['AJM', 'AUH', 'DXB', 'FUJ', 'RAK', 'SHJ', 'UMQ'], 'ADNTC NAS Restricted Network August 2026'),
    ('adntc-super-restricted', 'ADNTC Super-Restricted Network', 'Abu Dhabi National Takaful', 'Both', ['AJM', 'AUH', 'DXB', 'FUJ', 'RAK', 'SHJ', 'UMQ'], 'ADNTC NAS Super-Restricted Network August 2026'),
    ('adntc-workers', 'ADNTC Workers Network', 'Abu Dhabi National Takaful', 'Both', ['AJM', 'AUH', 'DXB', 'FUJ', 'RAK', 'SHJ', 'UMQ'], 'ADNTC NAS Workers Network August 2026'),
    ('fmc-rn-firstcare-farid-gn2', 'FMC RN FirstCare Farid GN-2', 'FMC Network UAE', 'Both', ['AJM', 'AUH', 'DXB', 'FUJ', 'RAK', 'SHJ', 'UMQ'], 'FMC RN FirstCare Farid GN-2'),
    ('fmc-standard-network', 'FMC Standard Network', 'FMC Network UAE', 'Both', ['AJM', 'AUH', 'DXB', 'FUJ', 'RAK', 'SHJ', 'UMQ'], 'FMC Standard Network'),
    ('fmc-standard-network-2', 'FMC Standard Network 2', 'FMC Network UAE', 'Both', ['AJM', 'AUH', 'DXB', 'FUJ', 'RAK', 'SHJ', 'UMQ'], 'FMC Standard Network 2'),
    ('fmc-standard-network-3', 'FMC Standard Network 3', 'FMC Network UAE', 'Both', ['AJM', 'AUH', 'DXB', 'FUJ', 'RAK', 'SHJ', 'UMQ'], 'FMC Standard Network 3'),
    ('dubai-care-n1', 'Dubai Care N1', 'Dubai Care', 'Both', ['AJM', 'AUH', 'DXB', 'FUJ', 'RAK', 'SHJ', 'UMQ'], 'Dubai Care N1'),
    ('neuron-comprehensive', 'Neuron Comprehensive Network', 'Neuron TPA', 'Both', ['AJM', 'AUH', 'DXB', 'FUJ', 'RAK', 'SHJ', 'UMQ'], 'Neuron MaxHealth Comprehensive Network August 2026'),
    ('neuron-general-plus', 'Neuron General Network Plus', 'Neuron TPA', 'Both', ['AJM', 'AUH', 'DXB', 'FUJ', 'RAK', 'SHJ', 'UMQ'], 'Neuron MaxHealth General Plus Network August 2026'),
    ('neuron-general', 'Neuron General Network', 'Neuron TPA', 'Both', ['AJM', 'AUH', 'DXB', 'FUJ', 'RAK', 'SHJ', 'UMQ'], 'Neuron MaxHealth General Network August 2026'),
    ('neuron-restricted', 'Neuron Restricted Network', 'Neuron TPA', 'Both', ['AJM', 'AUH', 'DXB', 'FUJ', 'RAK', 'SHJ', 'UMQ'], 'Neuron MaxHealth Restricted Network August 2026'),
    ('neuron-restricted-1', 'Neuron Restricted Network 1', 'Neuron TPA', 'Both', ['AJM', 'AUH', 'DXB', 'FUJ', 'RAK', 'SHJ', 'UMQ'], 'Neuron MaxHealth Restricted 1 Network August 2026'),
    ('nas-maxhealth-comprehensive', 'NAS Comprehensive Network', 'NAS TPA', 'Both', ['AJM', 'AUH', 'DXB', 'FUJ', 'RAK', 'SHJ', 'UMQ'], 'NAS MaxHealth Comprehensive Network November 2025'),
    ('nas-maxhealth-general-plus', 'NAS General Network Plus', 'NAS TPA', 'Both', ['AJM', 'AUH', 'DXB', 'FUJ', 'RAK', 'SHJ', 'UMQ'], 'NAS MaxHealth General Plus Network November 2025'),
    ('nas-maxhealth-general', 'NAS General Network', 'NAS TPA', 'Both', ['AJM', 'AUH', 'DXB', 'FUJ', 'RAK', 'SHJ', 'UMQ'], 'NAS MaxHealth General Network November 2025'),
    ('gulf-essential',     'Gulf Insurance Essential',   'Gulf Insurance',     'Inpatient',  ['DXB', 'SHJ', 'AJM']),
    ('gulf-comprehensive', 'Gulf Insurance Comprehensive','Gulf Insurance',     'Both',       ['DXB', 'SHJ', 'AJM']),
    ('gulf-gig-a1-dubai',  'Gulf Insurance via GIG A.1 Dubai Outpatient', 'Gulf Insurance', 'Outpatient', ['DXB'], 'GIG Gulf A1 Dubai'),
    ('gulf-gig-a1-auh',    'Gulf Insurance via GIG A.1 Abu Dhabi Outpatient', 'Gulf Insurance', 'Outpatient', ['AUH'], 'GIG Gulf A1 Abu Dhabi'),
    ('gulf-gig-a2-dubai',  'Gulf Insurance via GIG A.2 Dubai Outpatient', 'Gulf Insurance', 'Outpatient', ['DXB'], 'GIG Gulf A2 Dubai'),
    ('gulf-gig-a3-dubai',  'Gulf Insurance via GIG A.3 Dubai Outpatient', 'Gulf Insurance', 'Outpatient', ['DXB'], 'GIG Gulf A3 Dubai'),
    ('gulf-gig-a4-dubai',  'Gulf Insurance via GIG A.4 Dubai Outpatient', 'Gulf Insurance', 'Outpatient', ['DXB'], 'GIG Gulf A4 Dubai'),
    ('gulf-gig-a2-auh',    'Gulf Insurance via GIG A.2 Abu Dhabi Outpatient', 'Gulf Insurance', 'Outpatient', ['AUH'], 'GIG Gulf A2 Abu Dhabi'),
    ('gulf-gig-a3-auh',    'Gulf Insurance via GIG A.3 Abu Dhabi Outpatient', 'Gulf Insurance', 'Outpatient', ['AUH'], 'GIG Gulf A3 Abu Dhabi'),
    ('gulf-gig-a4-auh',    'Gulf Insurance via GIG A.4 Abu Dhabi Outpatient', 'Gulf Insurance', 'Outpatient', ['AUH'], 'GIG Gulf A4 Abu Dhabi'),
    ('gulf-gig-a1-northern', 'Gulf Insurance via GIG A.1 Northern Emirates Outpatient', 'Gulf Insurance', 'Outpatient', ['AJM', 'FUJ', 'RAK', 'SHJ', 'UMQ'], 'GIG Gulf A1 UAE Northern'),
    ('gulf-gig-a1-uae-all',  'Gulf Insurance via GIG A.1 UAE Outpatient', 'Gulf Insurance', 'Outpatient', ['AJM', 'AUH', 'DXB', 'FUJ', 'RAK', 'SHJ', 'UMQ'], 'GIG Gulf A1 UAE All'),
    ('gulf-gig-a2-uae-all',  'Gulf Insurance via GIG A.2 UAE Outpatient', 'Gulf Insurance', 'Outpatient', ['AJM', 'AUH', 'DXB', 'FUJ', 'RAK', 'SHJ', 'UMQ'], 'GIG Gulf A2 UAE All'),
    ('gulf-gig-a2-ip',       'Gulf Insurance via GIG A.2 UAE Inpatient', 'Gulf Insurance', 'Inpatient', ['AJM', 'AUH', 'DXB', 'FUJ', 'RAK', 'SHJ', 'UMQ'], 'GIG Gulf A2 IP'),
    ('gulf-gig-a2-plus',    'Gulf Insurance via GIG A.2 Plus Outpatient', 'Gulf Insurance', 'Outpatient', ['AJM', 'AUH', 'DXB', 'FUJ', 'RAK', 'SHJ', 'UMQ'], 'GIG Gulf A2 Plus'),
    ('gulf-gig-a2-plus-ip', 'Gulf Insurance via GIG A.2 Plus Inpatient', 'Gulf Insurance', 'Inpatient', ['AJM', 'AUH', 'DXB', 'FUJ', 'RAK', 'SHJ', 'UMQ'], 'GIG Gulf A2 Plus IP'),
    ('gulf-gig-a3-uae-all',  'Gulf Insurance via GIG A.3 UAE Outpatient', 'Gulf Insurance', 'Outpatient', ['AJM', 'AUH', 'DXB', 'FUJ', 'RAK', 'SHJ', 'UMQ'], 'GIG Gulf A3 UAE All'),
    ('gulf-gig-a3-base',     'Gulf Insurance via GIG A.3 Base Outpatient', 'Gulf Insurance', 'Outpatient', ['AJM', 'AUH', 'DXB', 'FUJ', 'RAK', 'SHJ', 'UMQ'], 'GIG Gulf A3'),
    ('gulf-gig-a3-ip',       'Gulf Insurance via GIG A.3 UAE Inpatient', 'Gulf Insurance', 'Inpatient', ['AJM', 'AUH', 'DXB', 'FUJ', 'RAK', 'SHJ', 'UMQ'], 'GIG Gulf A3 IP'),
    ('gulf-gig-a3-seha',     'Gulf Insurance via GIG A.3 plus SEHA Outpatient', 'Gulf Insurance', 'Outpatient', ['AUH', 'ALAIN'], 'GIG Gulf A3 plus SEHA'),
    ('gulf-gig-a3-seha-ip',  'Gulf Insurance via GIG A.3 plus SEHA Inpatient', 'Gulf Insurance', 'Inpatient', ['AUH', 'ALAIN'], 'GIG Gulf A3 plus SEHA IP'),
    ('gulf-gig-a3-mediclinic', 'Gulf Insurance via GIG A.3 plus Mediclinic Outpatient', 'Gulf Insurance', 'Outpatient', ['AJM', 'AUH', 'DXB', 'FUJ', 'RAK', 'SHJ', 'UMQ'], 'GIG Gulf A3 plus Mediclinic'),
    ('gulf-gig-a3-mediclinic-ip', 'Gulf Insurance via GIG A.3 plus Mediclinic Inpatient', 'Gulf Insurance', 'Inpatient', ['AJM', 'AUH', 'DXB', 'FUJ', 'RAK', 'SHJ', 'UMQ'], 'GIG Gulf A3 plus Mediclinic IP'),
    ('gulf-gig-a3-a',       'Gulf Insurance via GIG A.3 A Outpatient', 'Gulf Insurance', 'Outpatient', ['AJM', 'AUH', 'DXB', 'FUJ', 'RAK', 'SHJ', 'UMQ'], 'GIG Gulf A3 A'),
    ('gulf-gig-a3-awali',   'Gulf Insurance via GIG A.3 + AWALI HOSP Outpatient', 'Gulf Insurance', 'Outpatient', ['AJM', 'AUH', 'DXB', 'FUJ', 'RAK', 'SHJ', 'UMQ'], 'GIG Gulf A3 AWALI HOSP'),
    ('gulf-gig-a3-awali-ip', 'Gulf Insurance via GIG A.3 + AWALI HOSP Inpatient', 'Gulf Insurance', 'Inpatient', ['AJM', 'AUH', 'DXB', 'FUJ', 'RAK', 'SHJ', 'UMQ'], 'GIG Gulf A3 AWALI HOSP IP'),
    ('gulf-gig-a3-a-ip',    'Gulf Insurance via GIG A.3 A Inpatient', 'Gulf Insurance', 'Inpatient', ['AJM', 'AUH', 'DXB', 'FUJ', 'RAK', 'SHJ', 'UMQ'], 'GIG Gulf A3 A IP'),
    ('gulf-gig-a4-uae-all',  'Gulf Insurance via GIG A.4 UAE Outpatient', 'Gulf Insurance', 'Outpatient', ['AJM', 'AUH', 'DXB', 'FUJ', 'RAK', 'SHJ', 'UMQ'], 'GIG Gulf A4 UAE All'),
    ('gulf-gig-a4-ip',       'Gulf Insurance via GIG A.4 UAE Inpatient', 'Gulf Insurance', 'Inpatient', ['AJM', 'AUH', 'DXB', 'FUJ', 'RAK', 'SHJ', 'UMQ'], 'GIG Gulf A4 IP'),
    ('gulf-gig-a4-burjeel',  'Gulf Insurance via GIG A.4 Burjeel Outpatient', 'Gulf Insurance', 'Outpatient', ['AJM', 'AUH', 'DXB', 'FUJ', 'RAK', 'SHJ', 'UMQ'], 'GIG Gulf A4 Burjeel'),
    ('gulf-gig-a4-burjeel-ip', 'Gulf Insurance via GIG A.4 Burjeel Inpatient', 'Gulf Insurance', 'Inpatient', ['AJM', 'AUH', 'DXB', 'FUJ', 'RAK', 'SHJ', 'UMQ'], 'GIG Gulf A4 Burjeel IP'),
    ('gulf-gig-a4-nmc-royal-shj-ip', 'Gulf Insurance via GIG A.4 NMC Royal Sharjah Inpatient', 'Gulf Insurance', 'Inpatient', ['SHJ'], 'GIG Gulf A4 NMC Royal Shj IP'),
    ('gulf-gig-a4-nmc-royal-shj', 'Gulf Insurance via GIG A.4 NMC Royal Sharjah Outpatient', 'Gulf Insurance', 'Outpatient', ['SHJ'], 'GIG Gulf A4 NMC Royal Shj'),
    ('gulf-gig-a5-uae-all',  'Gulf Insurance via GIG A.5 UAE Outpatient', 'Gulf Insurance', 'Outpatient', ['AJM', 'AUH', 'DXB', 'FUJ', 'RAK', 'SHJ', 'UMQ'], 'GIG Gulf A5 All'),
    ('gulf-gig-a5-prime',    'Gulf Insurance via GIG A.5 + PRIME Outpatient', 'Gulf Insurance', 'Outpatient', ['AJM', 'AUH', 'DXB', 'FUJ', 'RAK', 'SHJ', 'UMQ'], 'GIG Gulf A5 PRIME'),
    ('gulf-gig-a5-ip',       'Gulf Insurance via GIG A.5 UAE Inpatient', 'Gulf Insurance', 'Inpatient', ['AJM', 'AUH', 'DXB', 'FUJ', 'RAK', 'SHJ', 'UMQ'], 'GIG Gulf A5 IP'),
    ('gulf-gig-a5-prime-ip', 'Gulf Insurance via GIG A.5 + PRIME Inpatient', 'Gulf Insurance', 'Inpatient', ['AJM', 'AUH', 'DXB', 'FUJ', 'RAK', 'SHJ', 'UMQ'], 'GIG Gulf A5 PRIME IP'),
    ('gulf-gig-a5-emirates', 'Gulf Insurance via GIG A.5 + EMIRATES Outpatient', 'Gulf Insurance', 'Outpatient', ['AJM', 'AUH', 'DXB', 'FUJ', 'RAK', 'SHJ', 'UMQ'], 'GIG Gulf A5 EMIRATES'),
    ('gulf-gig-a5-emirates-ip', 'Gulf Insurance via GIG A.5 + EMIRATES Inpatient', 'Gulf Insurance', 'Inpatient', ['AJM', 'AUH', 'DXB', 'FUJ', 'RAK', 'SHJ', 'UMQ'], 'GIG Gulf A5 EMIRATES IP'),
    ('gulf-gig-a1-tc1',      'Gulf Insurance via GIG A.1 TC1 Outpatient', 'Gulf Insurance', 'Outpatient', ['AJM', 'AUH', 'DXB', 'FUJ', 'RAK', 'SHJ', 'UMQ'], 'GIG Gulf A.1 TC1'),
    ('gulf-gig-a1-tc1-ip',   'Gulf Insurance via GIG A.1 TC1 Inpatient', 'Gulf Insurance', 'Inpatient', ['AJM', 'AUH', 'DXB', 'FUJ', 'RAK', 'SHJ', 'UMQ'], 'GIG Gulf A1 TC1 IP'),
    ('gulf-gig-a1-ip',       'Gulf Insurance via GIG A.1 UAE Inpatient', 'Gulf Insurance', 'Inpatient', ['AJM', 'AUH', 'DXB', 'FUJ', 'RAK', 'SHJ', 'UMQ'], 'GIG Gulf A1 IP'),
    ('gulf-gig-a1-plus',     'Gulf Insurance via GIG A.1 Plus Outpatient', 'Gulf Insurance', 'Outpatient', ['AJM', 'AUH', 'DXB', 'FUJ', 'RAK', 'SHJ', 'UMQ'], 'GIG Gulf A1 Plus'),
    ('gulf-gig-a1-plus-ip',  'Gulf Insurance via GIG A.1 Plus Inpatient', 'Gulf Insurance', 'Inpatient', ['AJM', 'AUH', 'DXB', 'FUJ', 'RAK', 'SHJ', 'UMQ'], 'GIG Gulf A1 Plus IP'),
    ('gulf-gig-a1-select',   'Gulf Insurance via GIG A.1 Select Outpatient', 'Gulf Insurance', 'Outpatient', ['AJM', 'AUH', 'DXB', 'FUJ', 'RAK', 'SHJ', 'UMQ'], 'GIG Gulf A1 Select'),
    ('gulf-gig-a1-select-ip', 'Gulf Insurance via GIG A.1 Select Inpatient', 'Gulf Insurance', 'Inpatient', ['AJM', 'AUH', 'DXB', 'FUJ', 'RAK', 'SHJ', 'UMQ'], 'GIG Gulf A1 Select IP'),
    ('gulf-gig-a1-plus-ex-ccad', 'Gulf Insurance via GIG A.1 Plus Ex CCAD Outpatient', 'Gulf Insurance', 'Outpatient', ['AJM', 'AUH', 'DXB', 'FUJ', 'RAK', 'SHJ', 'UMQ'], 'GIG Gulf A1 PLUS EX CCAD'),
    ('gulf-gig-a1-plus-ex-ccad-ip', 'Gulf Insurance via GIG A.1 Plus Ex CCAD Inpatient', 'Gulf Insurance', 'Inpatient', ['AJM', 'AUH', 'DXB', 'FUJ', 'RAK', 'SHJ', 'UMQ'], 'GIG Gulf A1 PLUS EX CCAD IP'),
    ('gulf-gig-a1-ex-mcme',  'Gulf Insurance via GIG A.1 Ex MCME Outpatient', 'Gulf Insurance', 'Outpatient', ['AJM', 'AUH', 'DXB', 'FUJ', 'RAK', 'SHJ', 'UMQ'], 'GIG Gulf A1 EX MCME'),
    ('gulf-gig-a1-ex-mcme-ip', 'Gulf Insurance via GIG A.1 Ex MCME Inpatient', 'Gulf Insurance', 'Inpatient', ['AJM', 'AUH', 'DXB', 'FUJ', 'RAK', 'SHJ', 'UMQ'], 'GIG Gulf A1 EX MCME IP'),
    ('gulf-gig-a1-ex-mch-ahd', 'Gulf Insurance via GIG A.1 Ex MCH + AHD Outpatient', 'Gulf Insurance', 'Outpatient', ['AJM', 'AUH', 'DXB', 'FUJ', 'RAK', 'SHJ', 'UMQ'], 'GIG Gulf A1 EX MCH AHD'),
    ('gulf-gig-a1-ex-mch-ahd-ip', 'Gulf Insurance via GIG A.1 Ex MCH + AHD Inpatient', 'Gulf Insurance', 'Inpatient', ['AJM', 'AUH', 'DXB', 'FUJ', 'RAK', 'SHJ', 'UMQ'], 'GIG Gulf A1 EX MCH AHD IP'),
    ('gulf-gig-a1-ex-al-zahra', 'Gulf Insurance via GIG A.1 Exc Al Zahra Outpatient', 'Gulf Insurance', 'Outpatient', ['AJM', 'AUH', 'DXB', 'FUJ', 'RAK', 'SHJ', 'UMQ'], 'GIG Gulf A1 Exc Al Zahra'),
    ('gulf-gig-a1-ex-al-zahra-ip', 'Gulf Insurance via GIG A.1 Exc Al Zahra Inpatient', 'Gulf Insurance', 'Inpatient', ['AJM', 'AUH', 'DXB', 'FUJ', 'RAK', 'SHJ', 'UMQ'], 'GIG Gulf A1 Exc Al Zahra IP'),
    ('gulf-gig-a1-excl-ccad',  'Gulf Insurance via GIG A.1 excl CCAD Outpatient', 'Gulf Insurance', 'Outpatient', ['AJM', 'AUH', 'DXB', 'FUJ', 'RAK', 'SHJ', 'UMQ'], 'GIG Gulf A1 excl CCAD'),
    ('gulf-gig-a1-excl-ccad-ahd', 'Gulf Insurance via GIG A.1 excl CCAD/AHD Outpatient', 'Gulf Insurance', 'Outpatient', ['AJM', 'AUH', 'DXB', 'FUJ', 'RAK', 'SHJ', 'UMQ'], 'GIG Gulf A1 excl CCAD AHD'),
    ('gulf-gig-a1-excl-ccad-ahd-ip', 'Gulf Insurance via GIG A.1 excl CCAD/AHD Inpatient', 'Gulf Insurance', 'Inpatient', ['AJM', 'AUH', 'DXB', 'FUJ', 'RAK', 'SHJ', 'UMQ'], 'GIG Gulf A1 excl CCAD AHD IP'),
    ('gulf-gig-a1-excl-ccad-ip', 'Gulf Insurance via GIG A.1 excl CCAD Inpatient', 'Gulf Insurance', 'Inpatient', ['AJM', 'AUH', 'DXB', 'FUJ', 'RAK', 'SHJ', 'UMQ'], 'GIG Gulf A1 excl CCAD IP'),
    ('gulf-gig-a1-excl-al-ahli', 'Gulf Insurance via GIG A.1 Excl Al Ahli Outpatient', 'Gulf Insurance', 'Outpatient', ['AJM', 'AUH', 'DXB', 'FUJ', 'RAK', 'SHJ', 'UMQ'], 'GIG Gulf A.1 EXCL AL AHLI'),
    ('gulf-gig-a1-excl-al-ahli-ip', 'Gulf Insurance via GIG A.1 Excl Al Ahli Inpatient', 'Gulf Insurance', 'Inpatient', ['AJM', 'AUH', 'DXB', 'FUJ', 'RAK', 'SHJ', 'UMQ'], 'GIG Gulf A1 EXCL AL AHLI IP'),
    ('gulf-gig-a6-uae-all',  'Gulf Insurance via GIG A.6 UAE Outpatient', 'Gulf Insurance', 'Outpatient', ['AJM', 'AUH', 'DXB', 'FUJ', 'RAK', 'SHJ', 'UMQ'], 'GIG Gulf A6 All'),
    ('gulf-gig-a6-ip',       'Gulf Insurance via GIG A.6 UAE Inpatient', 'Gulf Insurance', 'Inpatient', ['AJM', 'AUH', 'DXB', 'FUJ', 'RAK', 'SHJ', 'UMQ'], 'GIG Gulf A6 IP'),
    ('gulf-gig-eco-dxb-op',  'Gulf Insurance via GIG Eco Dubai Outpatient', 'Gulf Insurance', 'Outpatient', ['DXB'], 'GIG Gulf Eco DXB OP'),
    ('gulf-gig-eco-dxb-ip',  'Gulf Insurance via GIG Eco Dubai Inpatient', 'Gulf Insurance', 'Inpatient', ['DXB'], 'GIG Gulf Eco DXB IP'),
    ('gulf-gig-aeco1-uae-all', 'Gulf Insurance via GIG A.Eco 1 UAE Outpatient', 'Gulf Insurance', 'Outpatient', ['AJM', 'AUH', 'DXB', 'FUJ', 'RAK', 'SHJ', 'UMQ'], 'GIG Gulf AEco1 All'),
    ('gulf-gig-aeco1-ip',      'Gulf Insurance via GIG A.Eco 1 UAE Inpatient', 'Gulf Insurance', 'Inpatient', ['AJM', 'AUH', 'DXB', 'FUJ', 'RAK', 'SHJ', 'UMQ'], 'GIG Gulf AEco1 IP'),
    ('gulf-gig-aeco1-clinics', 'Gulf Insurance via GIG A.Eco 1 Clinics', 'Gulf Insurance', 'Outpatient', ['AJM', 'AUH', 'DXB', 'FUJ', 'RAK', 'SHJ', 'UMQ'], 'GIG Gulf AEco1 Clinics'),
    ('gulf-gig-aeco1-clinics-ip', 'Gulf Insurance via GIG A.Eco 1 Clinics Inpatient', 'Gulf Insurance', 'Inpatient', ['AJM', 'AUH', 'DXB', 'FUJ', 'RAK', 'SHJ', 'UMQ'], 'GIG Gulf AEco1 Clinics IP'),
    ('gulf-gig-aeco1-exc-sharq', 'Gulf Insurance via GIG A.Eco 1 Exc Al Sharq', 'Gulf Insurance', 'Outpatient', ['AJM', 'AUH', 'DXB', 'FUJ', 'RAK', 'SHJ', 'UMQ'], 'GIG Gulf AEco1 Exc Al Sharq'),
    ('gulf-gig-aeco1-exc-sharq-ip', 'Gulf Insurance via GIG A.Eco 1 Exc Al Sharq Inpatient', 'Gulf Insurance', 'Inpatient', ['AJM', 'AUH', 'DXB', 'FUJ', 'RAK', 'SHJ', 'UMQ'], 'GIG Gulf AEco1 Exc Al Sharq IP'),
    ('noor-family',        'Noor Takaful Family',        'Noor Takaful',       'Both',       ['AJM', 'AUH', 'DXB', 'FUJ', 'RAK', 'SHJ', 'UMQ'], 'Neuron MaxHealth Comprehensive Network August 2026'),
    ('noor-individual',    'Noor Takaful Individual',    'Noor Takaful',       'Both',       ['AJM', 'AUH', 'DXB', 'FUJ', 'RAK', 'SHJ', 'UMQ'], 'Neuron MaxHealth General Network August 2026'),
    ('emirates-insurance-aviva-comprehensive', 'Emirates Insurance Company AVIVA Comprehensive', 'Emirates Insurance Company', 'Both', ['AJM', 'AUH', 'DXB', 'FUJ', 'RAK', 'SHJ', 'UMQ'], 'Neuron MaxHealth Comprehensive Network August 2026'),
    ('emirates-insurance-aviva-general', 'Emirates Insurance Company AVIVA General', 'Emirates Insurance Company', 'Both', ['AJM', 'AUH', 'DXB', 'FUJ', 'RAK', 'SHJ', 'UMQ'], 'Neuron MaxHealth General Network August 2026'),
    ('arabia-insurance-nextcare', 'Arabia Insurance Company NextCare Consolidated', 'Arabia Insurance Company', 'Both', ['AJM', 'AUH', 'DXB', 'FUJ', 'RAK', 'SHJ', 'UMQ'], 'NextCare Consolidated UAE August 2026'),
    ('al-fujairah-nextcare-pcp-rn3', 'Al Fujairah National Insurance NextCare PCP RN3', 'Al Fujairah National Insurance', 'Both', ['AJM', 'AUH', 'DXB', 'FUJ', 'RAK', 'SHJ', 'UMQ'], 'NextCare PCP RN3 Network December 2024'),
    ('takafol-emarat-nas-comprehensive-current', 'Takaful Emarat NAS Comprehensive Network 2026', 'Takaful Emarat', 'Both', ['AJM', 'AUH', 'DXB', 'FUJ', 'RAK', 'SHJ', 'UMQ'], 'Takaful Emarat NAS Comprehensive Current'),
    ('takafol-emarat-nextcare-gn-plus-current', 'Takaful Emarat NextCare GN Plus 2026', 'Takaful Emarat', 'Both', ['AJM', 'AUH', 'DXB', 'FUJ', 'RAK', 'SHJ', 'UMQ'], 'Takaful Emarat NextCare GN Plus Current'),
    ('takafol-emarat-nextcare-gn-current', 'Takaful Emarat NextCare GN 2026', 'Takaful Emarat', 'Both', ['AJM', 'AUH', 'DXB', 'FUJ', 'RAK', 'SHJ', 'UMQ'], 'Takaful Emarat NextCare GN Current'),
    ('takafol-emarat-nextcare-gn-excluding-groups-current', 'Takaful Emarat NextCare GN Excluding Groups 2026', 'Takaful Emarat', 'Both', ['AJM', 'AUH', 'DXB', 'FUJ', 'RAK', 'SHJ', 'UMQ'], 'Takaful Emarat NextCare GN Excluding Groups Current'),
    ('takafol-emarat-nextcare-rn-current', 'Takaful Emarat NextCare RN 2026', 'Takaful Emarat', 'Both', ['AJM', 'AUH', 'DXB', 'FUJ', 'RAK', 'SHJ', 'UMQ'], 'Takaful Emarat NextCare RN Current'),
    ('takafol-emarat-nextcare-rn2-current', 'Takaful Emarat NextCare RN2 2026', 'Takaful Emarat', 'Both', ['AJM', 'AUH', 'DXB', 'FUJ', 'RAK', 'SHJ', 'UMQ'], 'Takaful Emarat NextCare RN2 Current'),
    ('takafol-emarat-nextcare-rn3-current', 'Takaful Emarat NextCare RN3 2026', 'Takaful Emarat', 'Both', ['AJM', 'AUH', 'DXB', 'FUJ', 'RAK', 'SHJ', 'UMQ'], 'Takaful Emarat NextCare RN3 Current'),
    ('takafol-emarat-nextcare-pcp-current', 'Takaful Emarat NextCare PCP 2026', 'Takaful Emarat', 'Outpatient', ['AJM', 'AUH', 'DXB', 'FUJ', 'RAK', 'SHJ', 'UMQ'], 'Takaful Emarat NextCare PCP Current'),
    ('takafol-emarat-nextcare-rne-current', 'Takaful Emarat NextCare RNE 2026', 'Takaful Emarat', 'Both', ['AJM', 'AUH', 'DXB', 'FUJ', 'RAK', 'SHJ', 'UMQ'], 'Takaful Emarat NextCare RNE Current'),
    ('takafol-emarat-mednet-gold-current', 'Takaful Emarat MedNet Gold 2026', 'Takaful Emarat', 'Both', ['AJM', 'AUH', 'DXB', 'FUJ', 'RAK', 'SHJ', 'UMQ'], 'Takaful Emarat MedNet Gold Current'),
    ('takafol-emarat-mednet-silver-premium-current', 'Takaful Emarat MedNet Silver Premium 2026', 'Takaful Emarat', 'Both', ['AJM', 'AUH', 'DXB', 'FUJ', 'RAK', 'SHJ', 'UMQ'], 'Takaful Emarat MedNet Silver Premium Current'),
    ('takafol-emarat-mednet-silver-classic-current', 'Takaful Emarat MedNet Silver Classic 2026', 'Takaful Emarat', 'Both', ['AJM', 'AUH', 'DXB', 'FUJ', 'RAK', 'SHJ', 'UMQ'], 'Takaful Emarat MedNet Silver Classic Current'),
    ('takafol-emarat-mednet-green-current', 'Takaful Emarat MedNet Green 2026', 'Takaful Emarat', 'Both', ['AJM', 'AUH', 'DXB', 'FUJ', 'RAK', 'SHJ', 'UMQ'], 'Takaful Emarat MedNet Green Current'),
    ('takafol-emarat-mednet-emerald-current', 'Takaful Emarat MedNet Emerald 2026', 'Takaful Emarat', 'Both', ['AJM', 'AUH', 'DXB', 'FUJ', 'RAK', 'SHJ', 'UMQ'], 'Takaful Emarat MedNet Emerald Current'),
    ('takafol-emarat-mednet-pearl-current', 'Takaful Emarat MedNet Pearl 2026', 'Takaful Emarat', 'Both', ['AJM', 'AUH', 'DXB', 'FUJ', 'RAK', 'SHJ', 'UMQ'], 'Takaful Emarat MedNet Pearl Current'),
    ('takafol-emarat-mednet-silk-road-current', 'Takaful Emarat MedNet Silk Road 2026', 'Takaful Emarat', 'Both', ['AJM', 'AUH', 'DXB', 'FUJ', 'RAK', 'SHJ', 'UMQ'], 'Takaful Emarat MedNet Silk Road Current'),
    ('takafol-emarat-ecare-classic-current', 'Takaful Emarat eCare Classic 2026', 'Takaful Emarat', 'Both', ['AJM', 'AUH', 'DXB', 'FUJ', 'RAK', 'SHJ', 'UMQ'], 'Takaful Emarat eCare Classic Current'),
    ('takafol-emarat-ecare-green-current', 'Takaful Emarat eCare Green 2026', 'Takaful Emarat', 'Both', ['AJM', 'AUH', 'DXB', 'FUJ', 'RAK', 'SHJ', 'UMQ'], 'Takaful Emarat eCare Green Current'),
    ('takafol-emarat-ecare-blue-current', 'Takaful Emarat eCare Blue 2026', 'Takaful Emarat', 'Both', ['AJM', 'AUH', 'DXB', 'FUJ', 'RAK', 'SHJ', 'UMQ'], 'Takaful Emarat eCare Blue Current'),
    ('takafol-emarat-ecare-blue-north-care-ne-current', 'Takaful Emarat eCare Blue North Care NE 2026', 'Takaful Emarat', 'Both', ['AJM', 'FUJ', 'RAK', 'SHJ', 'UMQ'], 'Takaful Emarat eCare Blue North Care NE Current'),
    ('takafol-emarat-aafiya-elite-current', 'Takaful Emarat Aafiya Elite 2026', 'Takaful Emarat', 'Both', ['AJM', 'AUH', 'DXB', 'FUJ', 'RAK', 'SHJ', 'UMQ'], 'Takaful Emarat Aafiya Elite Current'),
    ('takafol-emarat-aafiya-diamond-current', 'Takaful Emarat Aafiya Diamond 2026', 'Takaful Emarat', 'Both', ['AJM', 'AUH', 'DXB', 'FUJ', 'RAK', 'SHJ', 'UMQ'], 'Takaful Emarat Aafiya Diamond Current'),
    ('takafol-emarat-aafiya-gold-current', 'Takaful Emarat Aafiya Gold 2026', 'Takaful Emarat', 'Both', ['AJM', 'AUH', 'DXB', 'FUJ', 'RAK', 'SHJ', 'UMQ'], 'Takaful Emarat Aafiya Gold Current'),
    ('takafol-emarat-aafiya-apn-plus-current', 'Takaful Emarat Aafiya APN Plus 2026', 'Takaful Emarat', 'Both', ['AJM', 'AUH', 'DXB', 'FUJ', 'RAK', 'SHJ', 'UMQ'], 'Takaful Emarat Aafiya APN Plus Current'),
    ('takafol-emarat-aafiya-apn-edge-current', 'Takaful Emarat Aafiya APN Edge 2026', 'Takaful Emarat', 'Both', ['AJM', 'AUH', 'DXB', 'FUJ', 'RAK', 'SHJ', 'UMQ'], 'Takaful Emarat Aafiya APN Edge Current'),
    ('takafol-emarat-aafiya-essential-current', 'Takaful Emarat Aafiya Essential 2026', 'Takaful Emarat', 'Both', ['AJM', 'AUH', 'DXB', 'FUJ', 'RAK', 'SHJ', 'UMQ'], 'Takaful Emarat Aafiya Essential Current'),
    ('takafol-emarat-aafiya-apn-current', 'Takaful Emarat Aafiya APN 2026', 'Takaful Emarat', 'Both', ['AJM', 'AUH', 'DXB', 'FUJ', 'RAK', 'SHJ', 'UMQ'], 'Takaful Emarat Aafiya APN Current'),
    ('takafol-emarat-al-madallah-elite-current', 'Takaful Emarat Al Madallah Elite 2026', 'Takaful Emarat', 'Both', ['AJM', 'AUH', 'DXB', 'FUJ', 'RAK', 'SHJ', 'UMQ'], 'Takaful Emarat Al Madallah Elite Current'),
    ('takafol-emarat-al-madallah-premier-current', 'Takaful Emarat Al Madallah Premier 2026', 'Takaful Emarat', 'Both', ['AJM', 'AUH', 'DXB', 'FUJ', 'RAK', 'SHJ', 'UMQ'], 'Takaful Emarat Al Madallah Premier Current'),
    ('takafol-emarat-al-madallah-choice-current', 'Takaful Emarat Al Madallah Choice 2026', 'Takaful Emarat', 'Both', ['AJM', 'AUH', 'DXB', 'FUJ', 'RAK', 'SHJ', 'UMQ'], 'Takaful Emarat Al Madallah Choice Current'),
    ('takafol-emarat-al-madallah-select-rn3-current', 'Takaful Emarat Al Madallah Select RN3 2026', 'Takaful Emarat', 'Both', ['AJM', 'AUH', 'DXB', 'FUJ', 'RAK', 'SHJ', 'UMQ'], 'Takaful Emarat Al Madallah Select RN3 Current'),
    ('takafol-emarat-al-madallah-access-rn4-current', 'Takaful Emarat Al Madallah Access RN4 2026', 'Takaful Emarat', 'Both', ['AJM', 'AUH', 'DXB', 'FUJ', 'RAK', 'SHJ', 'UMQ'], 'Takaful Emarat Al Madallah Access RN4 Current'),
    ('takafol-emarat-al-madallah-neo-current', 'Takaful Emarat Al Madallah Neo 2026', 'Takaful Emarat', 'Both', ['AJM', 'AUH', 'DXB', 'FUJ', 'RAK', 'SHJ', 'UMQ'], 'Takaful Emarat Al Madallah Neo Current'),
    ('watania-ebp1',       'Watania Essential Benefits Plan 1', 'Watania Takaful', 'Both', ['AJM', 'DXB', 'FUJ', 'RAK', 'SHJ', 'UMQ'], 'nas-value-network'),
    ('watania-ebp2',       'Watania Essential Benefits Plan 2', 'Watania Takaful', 'Both', ['AJM', 'DXB', 'FUJ', 'RAK', 'SHJ', 'UMQ'], 'nas-value-network'),
]


def main():
    entries = load_merged()
    print(f'Loaded {len(entries)} raw entries')

    registry, stats = build_registry(entries)
    zavis_matches = load_zavis_matches()
    for provider in registry:
        match = zavis_matches.get(provider['Index'])
        if match:
            provider['ZAVIS ID'] = match['zavis_id']
            provider['ZAVIS URL'] = match['zavis_url']
            provider['ZAVIS NAME'] = match['zavis_name']
            provider['ZAVIS ADDRESS'] = match['zavis_address']
            provider['ZAVIS PHONE'] = match['zavis_phone']
            provider['ZAVIS MAPS URL'] = match.get('zavis_maps_url', '')
            if coord_ok(match.get('zavis_lat'), match.get('zavis_lon')):
                provider['lat'] = match['zavis_lat']
                provider['lon'] = match['zavis_lon']
                provider['coordinate_source'] = 'Zavis'
    print(f'Zavis enrichment: {len(zavis_matches)} matched providers')
    print(f'Registry: {stats["valid"]} valid coords, '
          f'{stats["invalid"]} invalid/missing, {stats["dupes"]} dupes removed')

    with open(os.path.join(DATA, 'moh-complete.json'), 'w', encoding='utf-8') as f:
        json.dump(registry, f, ensure_ascii=False, indent=1)

    with open(os.path.join(DATA, 'needs-geocoding.json'), 'w', encoding='utf-8') as f:
        json.dump(
            [{'PROVIDER NAME': r['PROVIDER NAME'], 'P': r['P'],
              'AREA': r['AREA'], 'ADDRESS': r['ADDRESS'],
              'TELEPHONE': r['TELEPHONE']} for r in registry if not coord_ok(r['lat'], r['lon'])],
            f, ensure_ascii=False, indent=1)

    # Per-plan datasets: all providers within the plan's emirate footprint.
    # (True network membership needs official provider lists from each insurer.)
    plans_meta = []
    plans = [plan if len(plan) == 6 else (*plan, '') for plan in PLANS] + load_takafol_plans()
    for plan_id, display, insurer, coverage, ems, network_id in plans:
        subset = [r for r in registry if r['P'] in ems and coord_ok(r['lat'], r['lon'])]
        path = f'data/{plan_id}.json'
        with open(os.path.join(ROOT, path), 'w', encoding='utf-8') as f:
            json.dump(subset, f, ensure_ascii=False, indent=1)
        plans_meta.append({
            'id': plan_id, 'name': display, 'insurer': insurer,
            'coverage': coverage, 'emirates': ems,
            'file': path, 'providers': len(subset),
        })
        if network_id:
            plans_meta[-1]['network_id'] = network_id
        print(f'  {display:35s} {len(subset):5d} providers')

    with open(os.path.join(DATA, 'plans.json'), 'w', encoding='utf-8') as f:
        json.dump(plans_meta, f, ensure_ascii=False, indent=2)

    print(f'\nDone. Registry: {len(registry)} providers, {len(plans_meta)} plans.')


if __name__ == '__main__':
    main()
