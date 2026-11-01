# Agent Onboarding — Insurance Network Map

## Quick Start

```bash
# Full data pipeline (run in order)
python3 scripts/extract_zavis.py --output sources/csv/zavis-providers.csv --workers 2
python3 scripts/match_zavis.py
python3 scripts/enrich_zavis.py
python3 scripts/build_data.py
python3 scripts/assign_networks.py
python3 scripts/validate_data.py

# Tests
python3 -m unittest discover -s scripts -p "test_*.py" -v
node --test tests/test_ui_behavior.js
```

## Critical Guards

### 1. Large File Monitor (pre-commit hook installed)
- **GitHub warns at 50 MB**, **rejects at 100 MB**
- Currently: `data/network-unmatched.json` = 84.7 MB (warning)
- Check manually: `python3 scripts/check_large_files.py`
- If it hits 100 MB → **push will fail**
- Fix: `git lfs track "data/network-unmatched.json"` then re-add

### 2. Validation Pipeline (must pass before push)
```bash
python3 scripts/validate_data.py
```
- Checks: 701 plans, 856K+ provider indexes, official plan ↔ assignment parity
- Never push if this fails

### 3. Empty Plans Tracker
6 plans have 0 providers (registry gaps):
| Plan ID | Insurer | Issue |
|---------|---------|-------|
| `daman-narrow-nw` | Daman | providers not in MOH registry |
| `daman-al-kamal-auh` | Daman | provider not in registry |
| `dni-nextcare-seha-2024` | DNI | SEHA hospitals missing |
| `orient-nextcare-seha` | Orient | SEHA providers missing |
| `dni-mednet-optical-2024` | DNI | optical providers missing |
| `hayah-mednet-optical` | HAYAH | optical providers missing |

**Do not delete these** — they're documented gaps needing data sourcing.

## Key Files to Know

| File | Purpose |
|------|---------|
| `scripts/build_data.py` | Builds registry + plan JSON from MOH + Zavis |
| `scripts/assign_networks.py` | L1 official / L2 chain / L3 geo assignment |
| `scripts/validate_data.py` | Full validation (run before push) |
| `data/plans.json` | Plan metadata for UI (source of truth) |
| `data/network-assignments.json` | Per-plan provider membership layers |
| `sources/networks/*.csv` | Official insurer network lists (authoritative) |

## Common Tasks

**Add a new official network:**
1. Drop CSV in `sources/networks/` (columns: PROVIDER NAME, EMIRATE, PROVIDER TYPE, AREA, ADDRESS, TELEPHONE, NETWORK_TIER?)
2. Ensure filename matches `network_id` in `data/plans.json`
3. Run: `python3 scripts/assign_networks.py && python3 scripts/validate_data.py`

**Fix a plan with 0 providers:**
1. Check if source CSV exists in `sources/networks/`
2. Verify EMIRATE column uses codes (AUH/DXB/SHJ/AJM/FUJ/RAK/UMQ/ALAIN)
3. Check `data/network-unmatched.json` for unmatched source rows
4. Rebuild: `python3 scripts/build_data.py && python3 scripts/assign_networks.py`

**Update UI:**
- Edit `index.html` (single-page app, vanilla JS + Leaflet)
- Test with: `node --test tests/test_ui_behavior.js`

## Branch / Commit Hygiene
- Work on `main` (this is the only branch)
- Stage explicit paths: `git add <file1> <file2>`
- Message format: `{feat,fix,docs,refactor}: <message>`
- Never `git add -A` / `git commit --no-verify`

## If Push Fails: "File > 100 MB"
```bash
# 1. Install LFS if needed
git lfs install

# 2. Track the large file
git lfs track "data/network-unmatched.json"
git add .gitattributes data/network-unmatched.json

# 3. Re-commit (rewrites history if already pushed)
git commit --amend --no-edit
git push --force-with-lease
```

## Project Structure
```
├── index.html              # Single-page UI
├── scripts/                # All Python/JS build scripts
│   ├── download/           # Insurer site scrapers
│   ├── capture/            # Browser automation
│   ├── extract/            # PDF/XLSX parsers
├── tests/                  # 4 Python + 1 JS test suite
├── data/                   # Generated JSON (tracked)
├── sources/
│   ├── networks/           # Official CSVs (tracked)
│   ├── csv/                # Catalogs, Zavis, Takafol
│   └── raw/                # Raw XLSX downloads (gitignored)
├── docs/                   # Documentation
└── V2/                     # Archived v2 attempt (gitignored)
```

## Contacts / References
- Repo: https://github.com/i3130002/Insurance-Network-Map
- Published: https://i3130002.github.io/Insurance-Network-Map/
- Key sources: Orient, Union, Sukoon, Daman, DNI, Takaful Emarat, ADNIC, NextCare, MedNet, Neuron, NAS
