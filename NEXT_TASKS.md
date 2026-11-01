# Next Tasks — Insurance Network Map

## Immediate (push will fail if ignored)
- [ ] **Large file monitor**: `data/network-unmatched.json` = 84.7 MB (GitHub warns at 50 MB, rejects at 100 MB)
  - If it hits 100 MB: `git lfs track "data/network-unmatched.json"` + re-commit + force push

## Data Quality (6 empty plans — registry gaps)
| Plan ID | Insurer | Needed |
|---------|---------|--------|
| `daman-narrow-nw` | Daman | providers in MOH registry |
| `daman-al-kamal-auh` | Daman | provider in registry |
| `dni-nextcare-seha-2024` | DNI | SEHA hospitals |
| `orient-nextcare-seha` | Orient | SEHA providers |
| `dni-mednet-optical-2024` | DNI | optical providers |
| `hayah-mednet-optical` | HAYAH | optical providers |

## Pipeline Commands (run in order)
```bash
python3 scripts/extract_zavis.py --output sources/csv/zavis-providers.csv --workers 2
python3 scripts/match_zavis.py
python3 scripts/enrich_zavis.py
python3 scripts/build_data.py
python3 scripts/assign_networks.py
python3 scripts/validate_data.py  # MUST PASS before push
```

## Test Commands
```bash
python3 -m unittest discover -s scripts -p "test_*.py" -v
node --test tests/test_ui_behavior.js
```

## Key Files
- `data/plans.json` — plan metadata (source of truth)
- `data/network-assignments.json` — provider membership layers
- `sources/networks/*.csv` — official insurer lists (authoritative)
- `scripts/validate_data.py` — run before every push
