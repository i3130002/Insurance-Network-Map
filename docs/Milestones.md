# Milestones

## M1 — Registry and map foundation — Complete

- Registry data is normalized into the application data model.
- The UAE map supports provider markers, search, filters, and plan selection.

## M2 — Official network ingestion — In progress

- 41 Takafol network workbooks are imported.
- 492 of 705 plans use official-source matching after the 2026-09-06 assignment run.
- 213 plans retain approximations. 15 plans have no mapped providers after source emirate normalization recovered 56 empty plans.
- Exit criteria: all configured plans use a verified official source, with source lineage documented.

## M3 — Zavis provider source and enrichment — Complete with follow-up work

- 11,499 provider records are extracted from the public Zavis directory.
- 2,390 registry providers are matched to Zavis.
- 1,137 providers receive Zavis coordinates.
- Exit criteria: failed pages are retried and all safe matches have reviewed identity and coordinates.

## M4 — Data quality and coverage — In progress

- Current follow-up: seven failed Zavis pages, 1,253 unmatched registry providers, and 106 providers without coordinates.
- Approximate legacy network plans still require official sources.
- Exit criteria: unresolved records are either corrected, explicitly classified, or documented as intentionally excluded.

## M5 — Release readiness — Pending

- Desktop and mobile browser checks passed for selection, search, filters, empty results, and reset. Representative Zavis and Google Maps links returned HTTP 200.
- Fixed the mobile panel covering the map. The largest plan loaded 2,216 markers in 77–83 ms locally without throttling.
- The existing published site passed an ADNIC Classic selection check. Local fixes are not deployed.
- Data validation now requires assignment metadata. All 705 plans pass validation after network assignment.
- Objective documentation and refresh instructions require a final update.
- Exit criteria: validation and tests pass, deployment smoke test succeeds, and the backlog has an owner or disposition.
