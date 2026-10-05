#!/usr/bin/env python3
"""
Geocode remaining Health First Plan G providers with approximate coordinates.
Uses Nominatim (OSM) with 1 req/sec rate limit.
Run with: python3 geocode_healthfirst.py
"""

import json
import os
import re
import time
import urllib.parse
import urllib.request

ROOT = '/home/tony/.t3/worktrees/Insurance Network Map/t3code-ba0d50c8'
HF_PATH = os.path.join(ROOT, 'data', 'healthfirst-plan-g-pcp-c.json')

UA = 'InsuranceNetworkMap/1.0 (UAE provider directory)'
LAT_MIN, LAT_MAX = 22.0, 26.6
LON_MIN, LON_MAX = 51.0, 56.6

EMIRATE_TOKENS = {
    'AJM': ['ajman', 'عجمان'],
    'AUH': ['abu dhabi', 'abu zaby', 'أبوظبي', 'أبو ظبي'],
    'DXB': ['dubai', 'dubayy', 'دبي'],
    'FUJ': ['fujairah', 'al fujairah', 'الفجيرة'],
    'RAK': ['ras al khaimah', 'رأس الخيمة'],
    'SHJ': ['sharjah', 'ash shariqah', 'الشارقة'],
    'UMQ': ['umm al quwain', 'أم القيوين', 'ام القيوين'],
    'ALAIN': ['al ain', 'abu dhabi', 'العين', 'أبوظبي', 'أبو ظبي'],
}

EMIRATE_NAMES = {
    'AJM': 'Ajman', 'AUH': 'Abu Dhabi', 'DXB': 'Dubai', 'FUJ': 'Fujairah',
    'RAK': 'Ras Al Khaimah', 'SHJ': 'Sharjah', 'UMQ': 'Umm Al Quwain',
    'ALAIN': 'Al Ain',
}


def norm_name(s):
    s = (s or '').upper()
    s = re.sub(r'[^A-Z0-9 ]', ' ', s)
    for t in ('LLC', 'L L C', 'SOLE PROPRIETORSHIP', 'BRANCH', 'BR', 'LTD',
              'CENTER', 'CENTRE', 'MEDICAL', 'CLINIC', 'HOSPITAL', 'PHARMACY'):
        s = re.sub(rf'\b{re.escape(t)}\b', ' ', s)
    return re.sub(r'\s+', ' ', s).strip()


def nominatim(query, limit=1):
    url = ('https://nominatim.openstreetmap.org/search?'
           + urllib.parse.urlencode({
               'q': query, 'countrycodes': 'ae', 'format': 'json',
               'limit': limit, 'addressdetails': 0}))
    req = urllib.request.Request(url, headers={'User-Agent': UA})
    with urllib.request.urlopen(req, timeout=10) as r:
        return json.load(r)


def geocode_one(entry):
    em = entry.get('P', '')
    name = entry.get('PROVIDER NAME', '')
    area = entry.get('AREA', '')
    addr = entry.get('ADDRESS', '')
    em_name = EMIRATE_NAMES.get(em, '')

    queries = [
        f'{name}, {area}, {em_name}, UAE',
        f'{name}, {em_name}, UAE',
        f'{addr}, {em_name}, UAE',
        f'{area}, {em_name}, UAE',
    ]
    for q in queries:
        try:
            results = nominatim(q)
        except Exception as e:
            print(f'    Error: {e}')
            time.sleep(2)
            continue
        for res in results:
            try:
                la, lo = float(res['lat']), float(res['lon'])
            except (KeyError, ValueError):
                continue
            if not (LAT_MIN <= la <= LAT_MAX and LON_MIN <= lo <= LON_MAX):
                continue
            display = (res.get('display_name') or '').lower()
            tokens = EMIRATE_TOKENS.get(em, [])
            if tokens and not any(t in display for t in tokens):
                continue
            if q.startswith(name):
                name_tokens = [w for w in norm_name(name).split() if len(w) > 2]
                hit = sum(1 for w in name_tokens if w in display)
                if name_tokens and hit / len(name_tokens) < 0.4:
                    continue
                return la, lo, res.get('display_name', ''), 'name_match'
            return la, lo, res.get('display_name', ''), 'area_match'
        time.sleep(1.1)
    return None


def main():
    with open(HF_PATH) as f:
        hf = json.load(f)

    # Providers with low-confidence (0.001 = emirate center approximation)
    approx = [p for p in hf if p.get('confidence') == '0.001']
    print(f'Providers to geocode: {len(approx)}')

    if not approx:
        print('No providers need geocoding')
        return

    matched = 0
    for i, p in enumerate(approx):
        print(f'[{i+1}/{len(approx)}] {p["PROVIDER NAME"][:60]}...')
        result = geocode_one(p)
        if result:
            la, lo, display, conf = result
            p['lat'] = str(la)
            p['lon'] = str(lo)
            p['confidence'] = conf
            p['formatted'] = display
            matched += 1
            print(f'  -> {la:.6f}, {lo:.6f} ({conf})')
        else:
            print(f'  -> FAILED')

        # Save checkpoint every 10
        if (i + 1) % 10 == 0:
            with open(HF_PATH, 'w') as f:
                json.dump(hf, f, ensure_ascii=False, indent=1)
            print(f'  Checkpoint saved ({i+1} processed)')

    # Final save
    with open(HF_PATH, 'w') as f:
        json.dump(hf, f, ensure_ascii=False, indent=1)

    print(f'\nDone: {matched}/{len(approx)} geocoded successfully')


if __name__ == '__main__':
    main()