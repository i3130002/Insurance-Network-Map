# Project review, 2026-09-06

## Findings and disposition

1. **Incomplete generated data, corrected.** All 705 plans lacked assignment metadata. The previous assignment file had no entries for 650 plans. Validation passed because official-membership checks required the missing metadata. Completed assignment and made the metadata required by validation.
2. **ADNIC source selection, corrected.** Assignment replaced explicit network IDs with legacy plan IDs. Explicit IDs now take precedence, and metadata records the source choice used during matching.
3. **Stale map selection, corrected.** Clearing a plan retained providers. Delayed responses could restore a previous selection. Selection changes now invalidate pending plan and upload results.
4. **Source coverage, open.** 492 plans use official-source matching. 213 retain chain or geographic approximations. 15 have no mapped providers after normalization recovered 56 empty plans. Empty results mean no matched registry providers, not an empty insurer network.
5. **Source quality, open.** Two ADNIC extracts contain provider-name fields over 130 KB. Inspection confirmed that whole PDF table sections and repeated headers were appended to provider names. The 10 MB CSV limit permits reading but does not correct these records. Re-extract the saved Platinum and Gold Plus PDFs with correct row boundaries and preserve restrictions. Phone matching and normalized names also need branch-identity review before eligibility claims.
6. **Company labels, open.** The catalog has 247 distinct company labels. Some contain network tier names. Consolidation requires an agreed insurer-to-network mapping.
7. **Empty-plan normalization, corrected.** Assignment compared source names such as Dubai with registry codes such as DXB. It now uses the existing emirate normalizer. Official subsets are rebuilt from the registry so a previously empty plan can recover matches. A regression test confirms recovery and repeatability. Dubai Care N2 now has 829 matched providers.

## Structure and boundaries

The site is one static HTML page with generated JSON files. It uses Leaflet and external browser scripts. Python scripts build the registry and assign network membership. JavaScript collectors obtain source files. There is no application server or database.

The UI file is about 490 lines. The data builder is 879 lines and includes a large plan catalog. Assignment is about 280 lines. These are maintenance hotspots. No restructuring was required for this repair.

No project lint or type-check configuration was found. The validator has type hints, but the assignment script does not enforce strict typing. A project-wide typing policy remains unconfigured.

## Verification

- `python3 validate_data.py`: passed for 705 plans and 854,845 provider indexes.
- `python3 -m unittest discover -q`: 12 tests passed.
- `node --test test_ui_behavior.js`: five behavior tests passed using the page's actual JavaScript and registry data.
- The JavaScript tests control fetch timing and replace DOM and map interfaces. They do not verify browser rendering, external links, mobile layout, or performance.
- `node qa_browser.js`: browser checks passed at 1440×900, 390×844, and 360×640 using installed Playwright and Brave. Selection, search, combined filters, reset, empty plans, and selection clearing worked without JavaScript errors.
- Mobile QA found that the panel covered the map. Its maximum height is now half the viewport. The map has 414 pixels below the panel at 390×844 and 312 pixels at 360×640. Saved screenshots confirm the layout.
- The largest plan has 2,216 providers. Local selection-to-marker times were 77–83 ms without CPU or network throttling. These measurements do not represent mobile-device or production network performance.
- Sample direct Zavis and Google Maps destinations returned HTTP 200. This was a representative check, not a full link crawl.
- The published GitHub Pages site returned HTTP 200 and displayed 255 providers after selecting ADNIC Classic, without JavaScript errors. Local changes have not been deployed.
- Browser evidence is saved in `.qa/browser-report.json`, `.qa/link-report.json`, `.qa/published-report.json`, and viewport screenshots. Set `PLAYWRIGHT_MODULE` and `BROWSER_PATH` to override the installed paths used by `qa_browser.js`.
- No deployment or commit was performed. Existing worktree changes were preserved.

## Remaining tasks

The 15 empty plans have these dispositions:

- Source column errors: Union NextCare PCP Abu Dhabi and DNI NAS Comprehensive, Executive, General, Restricted, and Super-Restricted March 2024. Union's emirate column contains provider categories. DNI's provider-name column contains numeric identifiers and its phone column contains addresses. Saved original workbooks are available for repair.
- Regional source review: Union NextCare Regional and DNI NextCare Regional 2024 contain mostly non-UAE cities. Do not assign these rows to UAE emirates without source evidence.
- Identity review: Daman Narrow, Daman Al Kamal, DNI NextCare SEHA, and Orient NextCare SEHA have source rows but no current matches.
- Provider-type coverage review: DNI MedNet Optical and HAYAH MedNet Optical have no matches in the current registry.
- Exclusion disposition: the Takafol MedNet excluded-reimbursement list must not be treated as positive membership.

Continue source matching and coordinate review from `ToDo.md`. Obtain the Allianz and SAICO rosters through an authorized source. Review empty plans, approximate plans, exclusion lists, and ambiguous matches. Deploy the reviewed local changes and repeat the published-site check before release.

Documentation changes are an STE-oriented draft. The official dictionary was not available. Verify project terms such as registry, geocoding, assignment metadata, and network tier before claiming STE compliance.
