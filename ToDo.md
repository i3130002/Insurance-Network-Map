# To-do

Prioritized work for completing the Insurance Network Map.

## P0 — Data completeness

- [x] Retry the seven Zavis pages that returned HTTP 503.
- [x] Re-run the Zavis crawl and verify deduplication and record counts.
- [x] Fetch usable coordinates for matched providers still missing them; no
      matched provider remains in the current 106-record coordinate backlog.
- [ ] Match the remaining 1,253 registry providers to Zavis using phone, name, emirate, and address review.
- [ ] Resolve the remaining 106 providers without coordinates.

## P1 — Network accuracy

- [ ] Replace approximate plans with official network sources for AXA, Emirates NBD, and Gulf Insurance.
- [x] Replace legacy DARIC Standard/Premium approximations with current Neuron General/Comprehensive mappings; capture provider evidence linking Dar Al Takaful to Noor Takaful.
- [x] Capture and normalize HAYAH Health Protect’s official September 2025 MedNet network workbook and map its published Tier 1 and Tier 2 plans.
- [x] Map HAYAH Health Protect Worldwide Tiers 3–5 from the official plan documents to MedNet Silver Premium and Gold.
- [x] Capture MEDGULF UAE assigned-provider network; official page exposes only an ASP.NET postback, so the current interactive UAE locator snapshot is retained.
- [ ] Obtain an Allianz UAE provider roster; current official plan documents describe tier names but state that provider lists are issued in the membership pack.
- [ ] Obtain a current SAICO UAE provider roster; current member materials direct members to the SAICOHEALTH app rather than publish a public file.
- [x] Capture and normalize Adamjee's official July 2023 MedNet network workbook.
- [x] Extract FMC Network UAE FirstCare Farid GN-2 provider roster from the official network workbook.
- [x] Capture FMC's official current 18-tier network catalog from its public provider API.
- [x] Capture an official FMC Abu Hail provider sample across all advertised network tiers.
- [x] Capture an official FMC Abu Dhabi provider sample across all advertised network tiers.
- [x] Download and normalize DNI's official February 2024 NextCare tier workbooks.
- [x] Normalize DNI's official February 2024 NextCare PCP Abu Dhabi sheet; TPA-PHM contains India-only records and was excluded from the UAE catalog.
- [x] Capture and normalize MedNet's official UAE locator catalog as a generic reference snapshot.
- [x] Normalize DNI's official April 2024 MedNet tier workbook.
- [x] Normalize DNI's official 2024 Lifeline Empire, Pearl, and Sapphire workbooks.
- [x] Normalize DNI's official April 2024 Aafiya and NAS tier workbooks; the Workers tier had no marked rows.
- [x] Normalize DNI's official March 2024 Neuron Global Choice and Global Choice Renewal workbooks.
- [x] Map Emirates Insurance Company AVIVA Comprehensive and General to the current Neuron networks, confirmed by Neuron and provider coverage pages.
- [x] Map Noor Takaful Family and Individual to current Neuron Comprehensive and General networks, confirmed by provider coverage pages.
- [x] Add the official Dubai Insurance DubaiCare provider network API capture.
- [x] Map Dubai Insurance Basic, Flexi, and Northern Emirates plans to DubaiCare.
- [x] Download the official Al Sagr NAS and NextCare network workbooks.
- [x] Normalize the official Al Sagr NextCare August 2023 workbook and add its plan mapping.
- [x] Normalize the official Al Sagr NAS Value/Value Lite workbook and add plan mappings.
- [x] Normalize the official Al Sagr NAS Comprehensive/GN/RN/SRN/WR workbook and add its plan mapping.
- [x] Normalize the official Al Sagr Value workbook and add its plan mapping.
- [x] Normalize the official Al Sagr Value Lite July 2023 workbook and add its plan mapping.
- [x] Capture and normalize the official QIC Value Lite Dubai inpatient network workbook.
- [x] Capture the official QIC Medical Individual page and map its Al Madallah RN4 network.
- [x] Download Alliance’s official RN3, RN2, RN, and GN network workbooks.
- [x] Normalize Alliance RN3 and add its plan mapping.
- [x] Normalize Alliance RN2 and add its plan mapping.
- [x] Normalize Alliance RN and GN and add plan mappings.
- [x] Download and normalize Alliance GN Plus and add its plan mapping.
- [x] Download and normalize the official Al Ain Insurance NAS provider network workbook.
- [x] Capture and normalize Al Buhaira’s official Comprehensive network pages.
- [x] Capture and normalize Al Buhaira’s official Comprehensive Plus network pages.
- [x] Capture and normalize Al Buhaira’s official Limited network pages.
- [x] Capture and normalize Al Buhaira’s official Restricted network pages.
- [x] Capture and normalize Al Buhaira’s official Standard network pages.
- [x] Capture and normalize Al Dhafra’s official Classic Network SEHA Plus list.
- [x] Capture and normalize Al Dhafra’s official Classic Network WRN list.
- [x] Capture and normalize Al Dhafra’s official Comprehensive, Executive, Restricted, and Premier PDFs, including their SEHA Plus variants.
- [x] Capture and normalize the AXA Gulf UAE Star Network PDF.
- [x] Capture and normalize the AXA Gulf UAE Star Plus Network PDF.
- [x] Capture and normalize the AXA Gulf UAE Diamond Network PDF.
- [x] Capture and normalize NextCare’s official UAE Consolidated Network August 2026 workbook.
- [x] Capture and normalize NextCare’s official UAE Teleconsultation Network August 2026 workbook.
- [x] Map Salama MediShield to the official NextCare Consolidated UAE August 2026 network.
- [x] Add Salama Gold, Silver Premium, Silver Classic, Green, and Silk Road tiers from the official brochure.
- [x] Map Methaq’s official healthcare guide to the current NextCare consolidated network.
- [x] Download and normalize Fidelity United’s official NextCare GN+, GN, RN, RN2, RN3, RN Enhanced, PCP, PCP AUH, and PHM workbooks.
- [x] Normalize the official RAK Insurance live MedNet Gold, Silver Premium, Silver Classic, Green, Silk Road, Emerald, and Pearl catalogs.
- [x] Capture and normalize MetLife UAE’s official EBP provider network PDF.
- [x] Capture and normalize NGI’s official April 2026 HealthNet Exclusive, Premier, Advantage, Standard Plus, Standard, Basic Plus, and Basic workbooks.
- [x] Add NGI’s official April 2026 Dental and Optical network sheets.
- [x] Capture and normalize Sukoon’s official August 2026 Secure Network for Shield Saver and Shield Saver Plus.
- [x] Refresh Sukoon Edge Network from the official August 2026 workbook.
- [x] Capture and normalize Sukoon’s official August 2026 Premium, Advance, Vital, and Healthcare Providers networks.
- [x] Capture and normalize ADNIC’s official August 2026 Platinum, Gold, Gold Plus, Silver, Bronze, Blue, and Hala networks.
- [x] Document AXA Gulf’s GIG successor and add explicit GIG A.1 Dubai/Abu Dhabi successor network plans.
- [x] Add the GIG A.2 Abu Dhabi network as an AXA successor plan.
- [x] Add the GIG A.2, A.3, and A.4 Dubai networks as AXA successor plans.
- [x] Add the GIG A.3 and A.4 Abu Dhabi networks as AXA successor plans.
- [x] Add explicit GIG successor-network plans for the unresolved Gulf Insurance label.
- [x] Add GIG A.2-A.4 Dubai and Abu Dhabi successor tiers for Gulf Insurance.
- [x] Add the GIG A.1 Northern Emirates catalog to AXA and Gulf successor plans.
- [x] Add the GIG A.1 All UAE catalog to GIG, AXA, and Gulf successor plans.
- [x] Add the GIG A.2 All UAE catalog to GIG, AXA, and Gulf successor plans.
- [x] Add the GIG A.3 All UAE catalog to GIG, AXA, and Gulf successor plans.
- [x] Add the GIG A.4 All UAE catalog to GIG, AXA, and Gulf successor plans.
- [x] Add the Emirates NBD employee medical plan backed by its official Orient partnership disclosure.
- [x] Map the current Noor successor domain to Watania Essential Benefits Plan 1 and its stated NAS-VN network.
- [x] Add Watania Essential Benefits Plan 2, which states the same NAS-VN network.
- [x] Refresh Sukoon plan networks from the official August 2026 workbook and add Advance Plus and Vital Eco.
- [x] Add current ADNIC live API catalogs for Platinum, G Plus, Gold, Silver, Bronze, Asasi, Blue, and Hala.
- [x] Add official Aman eCare Blue, Green, Classic, Silver, and Gold catalogs and plan mappings.
- [x] Add the official Daman Royal WW all-emirates locator extract.
- [x] Add the official Daman Grand all-emirates locator extract.
- [x] Add the official Daman Grand AW Asia 2 all-emirates locator extract.
- [x] Add the official Daman Grand WW all-emirates locator extract.
- [x] Add the official Daman Royal WW exc. US/Canada all-emirates locator extract.
- [x] Add the official Cigna EBP Value Lite network PDF.
- [x] Add the official Daman Grand WW exc. US all-emirates locator extract.
- [x] Add the official Daman Key all-emirates locator extract.
- [x] Add the official Daman Comprehensive 5 all-emirates locator extract.
- [x] Add the official Daman Supreme WW all-emirates locator extract.
- [x] Add the official Daman Supreme WW exc. US all-emirates locator extract.
- [x] Add the official Daman Supreme WW exc. US/Canada/Europe all-emirates locator extract.
- [x] Add the official Daman Visitors Plan all-emirates locator extract.
- [x] Add the populated Daman Flexi Abu Dhabi locator extract.
- [x] Add the official Daman Primary SEA/ISC/AC all-emirates locator extract.
- [x] Add the official Daman Advanced SEA/ISC/AC all-emirates locator extract.
- [x] Add the official Daman Key SEA/ISC/AC all-emirates locator extract.
- [x] Add the official Daman Grand SEA/ISC/AC all-emirates locator extract.
- [x] Add the official Daman Abu Dhabi Plan locator extract.
- [x] Add the official Daman Al Kamal Abu Dhabi locator extract.
- [x] Add the official Sukoon Premium Network locator extract.
- [x] Add the official Sukoon Edge Network locator extract.
- [x] Add the official Sukoon Signature Network locator extract.
- [x] Add the official Sukoon Advance Network locator extract.
- [x] Add the official Sukoon Vital Network locator extract.
- [x] Add the official Sukoon All Pharmacies locator extract.
- [x] Add the official Union NAS Value Lite network workbook.
- [x] Add the official Union eCare Classic network workbook.
- [x] Add the official Union eCare Green network workbook.
- [x] Add the official Union eCare Blue network workbook.
- [x] Add the official Union NAS network workbook.
- [x] Capture Union's current official 2025 network-download set with Brave/Playwright.
- [x] Add the official Union NAS Value network workbook.
- [x] Add the official Union Aafiya Elite network workbook.
- [x] Add the official Union Aafiya Diamond network workbook.
- [x] Add the official Union Aafiya Gold network workbook.
- [x] Add the official Union Aafiya Plus network workbook.
- [x] Add the official Union Aafiya IP network workbook.
- [x] Add the official Union Aafiya OP network workbook.
- [x] Add the official Union Aafiya Essential IP network workbook.
- [x] Add the official Union Aafiya Essential OP network workbook.
- [x] Add the official Union Aafiya APN IP and OP network workbooks.
- [x] Add the official DNI Lifeline Empire network workbook.
- [x] Add the official DNI Lifeline Pearl network workbook.
- [x] Add the official DNI Lifeline Sapphire network workbook.
- [x] Add the official DNI Nextcare consolidated network workbook.
- [x] Add the official DNI Nextcare GN, RNE, RN, RN2, RN3, PCP, PCP C, and PCP Abu Dhabi tiers.
- [x] Add the official DNI Nextcare SEHA Providers network.
- [x] Add the official DNI Nextcare Regional and TPA-PHM networks.
- [x] Add the official DNI MedNet network workbook.
- [x] Add the official DNI NAS network workbook.
- [x] Add the official DNI Global Choice, Global Choice Renewal, and Aafiya network workbooks.
- [x] Add the official Union Nextcare General network workbook.
- [x] Add the official Union Nextcare General Plus network workbook.
- [x] Add the official Union Nextcare PCP network workbook.
- [x] Add the official Union Nextcare Restricted network workbook.
- [x] Add the official Union Nextcare Restricted 2 network workbook.
- [x] Add the official Union Nextcare Restricted 3 network workbook.
- [x] Add the official Union Nextcare PCP-C network workbook.
- [x] Add the official Union Nextcare PCP Abu Dhabi network workbook.
- [x] Add the official Union Nextcare RN Enhanced network workbook.
- [x] Add the official Union NAS Workers Lite network workbook.
- [x] Add the official Orient August 2026 Value Network workbook.
- [x] Add the official Orient August 2026 Consolidated Nextcare workbook.
- [x] Add the official Orient August 2026 NAS Standard workbook.
- [x] Add the official Orient Nextcare PCP Northern Emirates workbook.
- [x] Add populated sheets from the official Orient Nextcare and Value workbooks.
- [x] Add the actual NETWORK LIST sheets from DNI Global Choice and Orient NAS workbooks.
- [x] Add the actual NETWORK LIST sheet from the Union NAS workbook.
- [x] Add populated sheets from the official Union NAS Value and Value Lite workbooks.
- [x] Add the official Orient MedNet Annual Health Checkup provider subset.
- [x] Add the separate June 2026 Orient Nextcare RN3 sheet.
- [x] Add the official Orient June 2026 Nextcare OP-PCP and IP-RN3 workbook.
- [x] Add the official Orient August 2026 MedNet Gold workbook.
- [x] Add the official Orient August 2026 MedNet Silver Premium network.
- [x] Add the official Orient August 2026 MedNet Silver Classic network.
- [x] Add the official Orient August 2026 MedNet Green network.
- [x] Add the official Orient August 2026 MedNet Silk Road OP network.
- [x] Add the official Orient August 2026 MedNet Silk Road IP network.
- [x] Add the official Orient August 2026 MedNet Emerald network.
- [x] Add the official Orient August 2026 MedNet Pearl network.
- [x] Add the official Orient August 2026 MedNet EBP OP network.
- [x] Add the official Orient August 2026 MedNet EBP IP network.
- [x] Add the official Orient August 2026 MedNet Basic OP network.
- [x] Add the official Orient August 2026 MedNet Basic IP network.
- [x] Add official GIG Gulf A.2, A.3, and A.4 Dubai outpatient locator extracts.
- [x] Add official GIG Gulf A.1 Abu Dhabi outpatient locator extract.
- [x] Add official GIG Gulf A.1 Northern Emirates outpatient locator extract.
- [ ] Review unmatched official-network rows, including the excluded MEDNET reimbursement list.
- [ ] Preserve source lineage and confidence for every plan and provider match.
- [ ] Review duplicate and ambiguous provider merges for false positives.
- [x] Add the official archived Cigna Healthguard UAE network tiers.
- [x] Add the official MaxHealth-hosted Neuron and NAS network workbooks.
- [x] Replace Noor Takaful placeholder mappings with its documented Neuron Comprehensive and General tiers.
- [x] Remove the generic Takafol Emarat placeholder; current catalog plans are loaded from explicit network files.
- [x] Add LIVA Easy Health Gold and Bronze plans from official Inayah network files.
- [x] Refresh LIVA Gold/Bronze and add Chrome/Opal BH from the current official Inayah workbooks.
- [x] Add ADNTC’s official August 2026 NAS General, Restricted, Super-Restricted, and Workers networks.
- [x] Add Arabia Insurance Company’s NextCare consolidated network association, confirmed by the current Cleveland Clinic Abu Dhabi payer directory.
- [x] Download and normalize the NextCare PCP RN3 network; map it to Al Fujairah National Insurance’s documented medical plan.
- [x] Download and normalize Takaful Emarat’s current NAS Comprehensive workbook from its official SharePoint catalog.
- [x] Download and normalize Takaful Emarat’s current NextCare GN+, GN, GN-excluding-groups, RN, RN2, RN3, PCP, and RNE workbooks.
- [x] Download and normalize Takaful Emarat’s current MedNet Gold, Silver Premium, Silver Classic, Green, Emerald, Pearl, and Silk Road workbooks.
- [x] Download and normalize Takaful Emarat’s current eCare Classic, Green, Blue, and Blue North Care NE workbooks.
- [x] Download and normalize Takaful Emarat’s current Aafiya Elite, Diamond, Gold, APN Plus, APN Edge, Essential, and APN workbooks.
- [x] Download and normalize Takaful Emarat’s current Al Madallah Elite, Premier, Choice, Select RN3, Access RN4, and Neo workbooks.
- [x] Download and normalize Takaful Emarat’s current NAS excluded-provider PDF (93 records); keep it as an exclusion source, not a positive network plan.
- [x] Capture April International Classic, Premium, and Green public network pages (11 March 2026) as discovery snapshots; reconcile row-count differences before plan mapping.
- [x] Download and normalize APRIL International’s official August 2026 Middle East workbook for MedNet Premium, Classic, and Green.
- [x] Extract APRIL International’s official August 2026 MedNet Alternative and Dental UAE sheets.

## P1 — Documentation and data quality

- [x] Update `objectives.html` with the current plan, provider, coordinate, and missing-data counts.
- [x] Validate provider names, phone numbers, addresses, provider types, and coordinate bounds.
- [x] Document the repeatable Zavis matching and enrichment workflow.

## P2 — Product and release

- [x] Add behavior checks for plan clearing, company changes, delayed responses, search, combined filters, empty results, and reset.
- [x] Prevent stale plan responses from restoring providers after the selection changes.
- [x] Require network-assignment metadata during data validation.
- [x] Review the oversized provider-name fields in the ADNIC Platinum and Gold Plus August 2026 extracts. Whole PDF table sections were appended to provider names.
- [ ] Re-extract ADNIC Platinum and Gold Plus August 2026 from the saved PDFs, preserving restrictions and row boundaries.
- [x] Normalize source emirate names during assignment and restore official plan subsets from the registry. Recovered 56 empty plans.
- [ ] Repair shifted columns in the five DNI NAS March 2024 sources and Union NextCare PCP Abu Dhabi source.
- [ ] Resolve the remaining 15 empty plans using the classifications in `Review.md`.
- [x] Test the company → plan → map flow in Brave on desktop and mobile.
- [x] Test provider search, filters, reset behavior, empty results, and mobile layout. Limit the mobile panel to half the viewport so the map remains usable.
- [x] Verify popup link construction and representative direct Zavis and Google Maps destinations. Both sample destinations returned HTTP 200.
- [x] Check the largest plan with 2,216 providers. Local selection-to-marker times were 77–83 ms across three viewport sizes, without CPU or network throttling.
- [x] Run a GitHub Pages smoke test. The existing published page loaded ADNIC Classic with 255 providers and no JavaScript errors. Local changes are not deployed.

## Repeatable data pipeline

```text
python3 extract_zavis.py --output sources/csv/zavis-providers.csv --workers 2
python3 match_zavis.py
python3 enrich_zavis.py
python3 build_data.py
python3 assign_networks.py
python3 validate_data.py
python3 -m unittest discover -p 'test_*.py'
node --test test_ui_behavior.js
node qa_browser.js
```

Raw downloaded XLSX files remain ignored; refreshes must use public source URLs.
