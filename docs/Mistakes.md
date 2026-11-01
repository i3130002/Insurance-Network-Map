# Mistakes

- 2026-09-06: Two source-discovery reads used absent filenames. No source files changed. Use exact paths from the plan metadata or file discovery before opening source files.

- 2026-09-06: The assignment regression failed as expected: named emirates did not match registry codes, and empty plan files could not recover providers. The test also exposed two unclosed input files; reads now close their files.

- 2026-09-06: The screenshot viewer failed in the bwrap sandbox. Browser screenshots were saved successfully; browser DOM measurements confirmed that the mobile panel covered all but an 8-pixel map strip.

- 2026-09-06: Two further patch attempts failed in the bwrap helper. Invoking the patch utility through an elevated shell variable completed the edits.

- 2026-09-06: Network assignment stopped before writing outputs because two ADNIC extracts have provider-name fields larger than the CSV module's 128 KiB limit. Used the existing project limit of 10 MB. The large extracted names still require source-quality review.

- 2026-09-06: The incomplete-build regression test failed as expected before the fix. The validator accepted plans without assignment metadata and skipped their official-membership checks.

- 2026-09-06: Two shell calls and a patch call failed before execution because bwrap could not configure loopback. Elevated execution allowed the review to continue.
- 2026-09-06: The first UI test run exposed selection races. Two checks also assumed all 2,390 registry records had map coordinates. Corrected the checks to expect 2,284 markers and retain the 106-record coordinate backlog.
- 2026-09-06: Release-workflow discovery reported that the project has no `.github` directory. No workflow files were read or changed.

- 2026-08-30: Playwright could not launch Brave in the restricted shell because snap-confine lacked cap_dac_override; retry with host-level permission.
- 2026-08-30: The MetLife mednet-network.pdf URL now redirects to a self-redirecting page-not-found route; the official search result is stale and no file was saved.
- 2026-08-30: The first Playwright download of MetLife EBP.pdf fetched HTTP 200 but the inline Node script failed because it mixed top-level await with require; retrying with an ES-module import.
- 2026-08-30: The official MetLife May 2020 EBP PDF URL is also retired and redirects in a loop to the page-not-found route; the existing official EBP catalog remains the usable source.
- 2026-08-30: The first LibreOffice conversion of Sukoon’s XLS produced no output because its default user profile was not writable; retry with an isolated temporary profile.
- 2026-08-30: A restricted-shell Brave retry failed again with snap-confine capability errors while inspecting Sukoon’s selector; use escalated Playwright for browser work.
- 2026-08-30: The first Cigna Healthguard PDF parser had a syntax error in its generated CSV field fallback; no output was written, and the parser was corrected before retry.
- 2026-08-30: Direct curl DNS lookup for ngi.ae failed; retrying discovery through the Brave browser network.

- 2026-08-29: The rendered Brave workbook showed `NAS - Comprehensive
  Network.xlsx`, but its SharePoint file API returned HTTP 403. The isolated
  profile has no authenticated download session.

- 2026-08-29: The Brave SharePoint probe reached `NAS - Comprehensive
  Network.xlsx`, but used a Playwright locator method that Puppeteer does not
  provide. The browser cleanup also reported a permission error. Use page
  evaluation with explicit process cleanup on the next probe.

- 2026-08-29: A direct Takaful SharePoint workbook download returned HTTP 403.
  TinyFish can render the network page and expose links, but the binary files
  require a browser download session or another approved transfer path.

- 2026-08-29: `monid runs get` does not support `-o`; use JSON stdout
  redirection to save a completed run result.

- 2026-08-29: The supplied MoniD credential also returned TinyFish HTTP 401.
  The credential was used only in process memory and was not stored.

- 2026-08-29: Pi mapped `MONID_API_KEY` to `TINYFISH_API_KEY`, but TinyFish
  returned HTTP 401. The credential was not printed or saved, and no source
  data was changed.

- 2026-08-29: Targeted Firecrawl search for the GIG UAE locator returned no
  results and produced no output file. Keep the existing source data unchanged.

- 2026-08-29: Firecrawl scrape did not produce an output artifact for Aman’s
  public page. Use targeted Firecrawl search results and verify direct files
  independently before import.

- 2026-08-29: The Firecrawl wrapper command was not found from the repository
  root. Use its absolute skill path when the project has no local wrapper.

- 2026-08-29: Playwright could not start because the configured Chromium
  executable is absent. Use the shared Firecrawl browser path for web work;
  do not install a browser in this environment.

- 2026-08-29: A post-deployment content check failed from Python f-string
  quoting. No project files changed; rerun the check with simple expressions.

- 2026-08-29: The local commit could not create `.git/index.lock` because the
  repository metadata is read-only. The project files remain in the worktree.

- 2026-08-29: The published GitHub Pages URL returned HTTP 404 during the
  release smoke test. The repository is locally valid, but deployment is not
  currently available at the documented URL.

- 2026-08-29: The full Zavis retry exceeded the practical run time while page
  requests were still pending. It was interrupted before the extractor wrote
  its output; keep the existing source until a bounded retry is implemented.
- 2026-08-29: The first bounded Zavis sample still fetched every category because
  `--max-pages` only limited pagination. Add `--max-categories` to bound the
  category-first-page requests as well.
- 2026-08-29: The one-category Zavis sample completed with zero records because
  that category response was unavailable or did not match the parser. Do not
  use the sample as refreshed source data.

- 2026-08-29: A combined UI/documentation patch did not apply because the
  expected duplicate assignment was not present. Re-read the exact lines and
  applied the changes in a narrower patch.

- The completed Zavis crawl had seven pages return temporary HTTP 503 responses; the output contains 11,499 deduplicated records and those URLs should be retried on the next refresh.

- A diagnostic command used a misspelled tool name (`execartement`) and did not run; no project files were changed.

- The full Zavis crawl stopped when a category root returned HTTP 503; category and pagination fetches now use the same non-aborting retry path as detail pages.

- The expanded Zavis parser test initially used one extra escaping layer and failed to find its synthetic provider card; the fixture is being corrected.

- The first Zavis extractor run hit sandbox DNS failure; rerun the public fetch with network escalation.
- Zavis returned HTTP 503 during the first parallel pass; the extractor now retries and records failed URLs instead of aborting the batch.

- Zavis Firecrawl mapping could not start because the wrapper requires Podman, while this environment only exposed Docker Compose. The shared Firecrawl service itself started successfully.

- Validation failed after changing phone matching because generated plan files had not been rebuilt, and `GN+` initially collided with `GN` in the slugifier. Both issues are being corrected before the next validation run.
- Git staging failed with `confused by unstable object source data`; the generated files remain in the worktree and will be staged again after checking repository state.

- 2026-08-28: The first skill-file lookup treated catalog aliases as literal subdirectories. Use the mapped skill roots directly.

- 2026-08-28: Firecrawl could not resolve `api.firecrawl.dev` while fetching the ASD-STE100 site. Switched to the available official web reader.
- 2026-08-28: The skill initializer command used `python`, which is unavailable in this environment. Use `python3`.

- 2026-08-28: The first subagent delegation attempt failed because the inherited model name was unavailable. Retry with an explicitly available lightweight model.
- 2026-08-28: Node could not check JavaScript piped through `/dev/stdin` in this PTY environment. Use a temporary extracted script file for syntax checks.
- 2026-08-28: The first Node inline regex check was over-escaped and failed to parse. Use simple string splitting for the inline check.
- 2026-08-28: Network assignments used raw-registry indexes while plan files used generated-registry indexes. The validator caught 9,333 mismatches; assignments now use the generated registry.
- 2026-08-28: The Nominatim backlog run stalled on network timeouts before its first checkpoint and was interrupted. The geocoder remains resumable; use a reachable geocoding service or smaller batches.
- 2026-08-28: A follow-up commit failed because the main workspace exposes `.git` as read-only. The timeout note remains uncommitted.
- 2026-08-28: Objectives-document delegation hit the subagent thread limit. Apply the small documentation update locally if needed.
- 2026-08-28: ADNIC official assignments initially included providers outside each plan's emirate scope. The validator caught 850 mismatches; the assignment guard now applies the plan scope to official matches.
- 2026-08-28: The escalated geocoding batch was rejected because it would send provider names and addresses to Nominatim. A single read-only connectivity test succeeded.
- 2026-08-28: The approved geocoding run completed, but staging its outputs failed because the main workspace `.git` remains read-only. Attempt a focused commit through the writable agent workspace.
- 2026-08-28: The focused commit attempt failed because Git could not create `.git/index.lock`; retry with escalated permission.
- 2026-08-28: The objectives commit attempt failed because Git could not create `.git/index.lock` in the read-only repository metadata. Retry with escalated permission.
- 2026-08-28: The requested `.gitignore` commit failed because Git could not create `.git/index.lock`; repository metadata is read-only.
- 2026-08-28: Manual removal of generated geocoder fields left trailing commas in two JSON objects. Validate generated JSON after targeted cleanup.
- 2026-08-28: Direct export of a public Takaful Emarat SharePoint workbook returned HTTP 403; retain the official source link and do not infer network membership.
- 2026-08-28: The full Nominatim retry completed with zero additional accepted coordinates; remaining backlog needs better source data.
- 2026-08-28: The first NAS workbook parser used the wrong header row and extracted zero coordinates. Detect the header row after title rows before parsing spreadsheet columns.
- 2026-08-28: The geocoder backlog count was read before the deduplication fix, reporting 174 instead of the final 189. Rebuild generated data before publishing counts.
- 2026-08-28: Takafol's exact SharePoint link and its resolved `NEXTCARE - GN+.xlsx` path both returned HTTP 403 with `download=1`; link-suffix changes cannot bypass the tenant access policy.
- 2026-08-28: Two direct-link patch attempts missed the existing JavaScript context. Inspect exact source lines before applying a narrow patch.
- 2026-08-28: An older geocoder process overlapped a newer source refresh and overwrote registry state. Do not run concurrent writers against `sources/merged-registry.json`.
- 2026-08-28: The ADNIC accuracy check exposed that official plans still contained all emirate providers instead of only official matches. Keep plan-file membership aligned with official assignment layers.
- 2026-08-29: Node `--check` with process substitution tried to open a transient `/proc` pipe. Extract inline JavaScript to a temporary file before syntax checking.
- 2026-08-29: The first interactive SharePoint navigation exceeded the 60-second browser timeout. Bound page navigation separately and inspect partial page state before retrying.
- 2026-08-29: Browser-agent inspection of the completed workbook download hung and had to be interrupted; the browser confirmed the filename but did not expose a transferable local path.
- 2026-08-29: A Playwright download-event capture hung while clicking Excel Online controls. Use the browser agent’s successful download action, but do not assume its remote path is transferable.
- 2026-08-29: The browser session expired before its remote download could be transferred. Reopen the workbook and inspect the download directory in the same session.
- 2026-08-29: The reopened browser reported a Downloads URL but its Playwright filesystem had no `/home/user/Downloads` directory. Treat the Firecrawl download as remote-only unless the tool exposes an artifact transfer.
- 2026-08-29: Capturing the Office iframe download event timed out even after locating the correct frame. The browser agent can click Download a Copy, but Firecrawl does not reliably expose the resulting binary to the workspace.
- 2026-08-29: The captured Playwright download path was not readable from a later browser interaction, so transferring it through separate calls failed. Capture and read the artifact within one browser execution.
- 2026-08-29: The in-session transfer script reused the persistent REPL binding `fs`, causing a redeclaration error. Use unique binding names for browser transfer variables.
- 2026-08-29: The iframe download-event transfer timed out after the menu item was clicked; Excel’s browser download is not consistently observable by Playwright in this session.
- 2026-08-29: The captured Excel download endpoint returned a 1,466-byte HTML internal-error page with HTTP 200, not an XLSX. Verify MIME/signature before accepting browser downloads.
- 2026-08-29: The general web tool followed a Takafol SharePoint workbook link into a Microsoft login redirect and could not fetch the workbook. Use the rendered Excel browser route for public page inspection.
- 2026-08-29: Local Brave headless navigation hung on the SharePoint workbook and produced no download. The user’s interactive Brave session may succeed because it has a full GUI/private profile unavailable to this agent.
- 2026-08-29: The first local Brave automation script used an incorrect Puppeteer ESM path. Resolve the installed package entry point before launching the batch.
- 2026-08-29: Reusing the `frame` binding in the persistent browser REPL caused a redeclaration syntax error. Use unique binding names for each interaction call.
- 2026-08-28: The first Zavis batch exited without producing its result file. Add a hard timeout and verify the output file before treating a public-directory run as complete.
- 2026-08-28: Direct urllib access to Zavis returned HTTP 403; use the approved browser/scraping path for JS-rendered public pages instead of assuming raw HTTP access.
- 2026-08-28: The general web opener rejected the Zavis query URL as unsafe. Use the Firecrawl CLI for this site instead.
- 2026-08-28: A multi-URL Firecrawl CLI call saved both pages to the same generated filename and did not honor the requested output path. Use one URL per call or isolate output directories.
- 2026-08-28: Concurrent Firecrawl subprocesses produced no batch output, and an isolated subprocess returned an error while the direct CLI invocation worked. Keep Firecrawl calls in the controlling shell and verify each saved artifact.
- 2026-08-29: Chromium Flatpak tests with `--download-directory` and an X11 GUI opened the Excel workbook but produced no local XLSX. Treat the native Excel download action as unresolved until a manually confirmed save is available.
- 2026-08-29: Pi's Playwright browser tool could not initialize because `/opt/google/chrome/chrome` is absent. Do not install a browser for this task; use the existing Chromium CDP session instead.
- 2026-08-29: Retesting Pi's Playwright browser produced the same missing-Chrome initialization error before page navigation.
- 2026-08-29: Attempting to stage the Takafol XLSX was rejected by the intentional `*.xlsx` ignore rule. Keep raw workbooks local and export tracked normalized CSV data.
- 2026-08-29: The user’s live Brave session differs from isolated automation profiles: direct download succeeds interactively, while isolated sessions receive zero-byte artifacts. Attach to the live browser or use its chosen download folder for reliable bulk capture.
- 2026-08-29: The UI flow contract test correctly failed before the separate company selector was implemented; keep the test as the regression contract.
- 2026-08-29: The first post-implementation UI contract run used a selector-variable assertion that did not match the DOM lookup style. Assert the actual event-binding expression.
- 2026-08-29: Opening all Takafol direct-download links together triggered blocking. Process one link at a time with a delay and verify each completed file before continuing.
- 2026-08-29: The first direct Playwright-with-Brave test failed from shell quoting before launch. Use a temporary script for browser tests with nested selectors.
- 2026-08-29: The corrected Playwright-with-Brave script used a named ESM import against a CommonJS package and failed before launch. Use the package default export.
- 2026-08-29: Playwright captured the Excel download in Brave, but `download.saveAs()` pointed to a vanished temporary path. Copy the download stream directly while the browser session is open.
- 2026-08-29: Reading the Playwright download stream immediately returned a zero-byte file. Wait for `download.failure()` and `download.path()` before copying the completed artifact.
- 2026-08-29: Direct `download=1` triggered Brave's download event, but Playwright's temporary artifact path was absent when copied. Test the completed download stream as the transfer path.
- 2026-08-29: The direct SharePoint download event returned zero bytes through Playwright's stream. Check Brave's own download directory separately before classifying the response as empty.
## 2026-08-29

- `python3 -m unittest test_takafol_import.py` failed before the importer existed; the new test correctly exposed the missing implementation.
- A combined documentation patch did not apply because one expected paragraph had changed; no files were modified by that failed patch.
- 2026-08-29: The first documentation commit failed because the sandbox could not create `.git/index.lock`; retry Git metadata operations with elevated permission.
- 2026-08-29: The local HTTP smoke test could not bind a socket because the sandbox denies network listeners. Validate static files directly and run the HTTP check in a permitted environment.
## 2026-08-29

- The `pytest` launcher failed because its interpreter does not exist. Use the
  available Python test runner until the environment is repaired.
# 2026-08-29

- Brave navigation to the official Sukoon XLSX returned `ERR_ABORTED` because the browser treated the file response as a download. The collector must use a download event instead of `page.goto` response buffering.
- Brave click on the ADNIC updated-network postback did not emit a download event within 30 seconds. Inspect the postback response directly before retrying.
- A diagnostic script was rejected because it would log response headers containing session cookies. The diagnostic must omit headers and cookie values.
- The Sukoon probe used the deprecated Puppeteer `$x` method, which is unavailable in the installed version. Use element handles selected from `page.$$` instead.
- Sukoon’s live locator reset the selected network tier before the provider search submitted. Tier names were captured, but no provider rows were imported.
- Cleanup found no remaining temporary Sukoon probe file. The delete patch therefore had no target.
- The Daman international-network probe found no exact `Advanced SEA, ISC, AC` option in the redirected live page, so Puppeteer received an undefined select value.
- The first GIG Brave capture was delayed by the external permission review and did not start. Retry is safe because the command only reads the public locator and writes one scoped source artifact.
- The GIG locator presented a certificate-authority error in the Brave session. The retry must enable certificate-error tolerance for this public locator.
- The GIG locator’s submit control was covered by a non-content overlay in headless Brave. Use the page click handler through the DOM for the scoped public query.
- GIG locator captures for A.1–A.4 returned the locator shell rather than provider result tables. The saved shell artifacts were removed and must not be counted as network extracts.
- GIG’s actual SearchResults probe still failed certificate validation despite the Puppeteer option; use Brave’s `--ignore-certificate-errors` flag on the next attempt.
- Direct curl to the GIG locator failed certificate validation in the local CA bundle. Use the already verified Brave certificate-tolerant session for this public page.
- ADNIC returned plan PDFs as inline responses, but Puppeteer could not read the response body after rendering. Use an authenticated in-page form POST and read the PDF blob in the page context.
- An empty cleanup patch for the temporary ADNIC collector was invalid. The collector must be removed with a complete delete patch.
- The default unittest discovery command failed because the project has no importable `tests/` directory. Run the project’s test files directly or add a package only if requested.
- Adding plan-specific network IDs exposed that the builder always appended an empty sixth tuple field. The builder now preserves six-field plans and appends the field only to legacy five-field plans.
- A web-search tool call failed because its JavaScript wrapper parsed the query payload incorrectly. No project data changed; retry with a simpler payload.
- Brave could not connect to DARIC or Gulf Insurance domains, and the Noor Takaful hostname did not resolve. No insurer-specific source was imported from those probes.
- TinyFish returned a fetch failure for the Noor Takaful search query. The Gulf query returned GIG and unrelated directory results, not an official Gulf Insurance network source.
- The first GIG Abu Dhabi normalizer used a regex without a capture group and stopped before writing the CSV. The raw Brave response is intact; rerun with field-specific patterns.
- A tool wrapper call used an unavailable `tools.exec` method and did not run. No project files changed; use `exec_command` for the normalizer.
- TinyFish returned `fetch failed` for the quoted DARIC legal-name query. No project files changed.
- Daman Comprehensive 2 returned no records for all seven emirates; the normalizer then failed because there was no first row from which to derive CSV headers. No empty source CSV was written.
- A nested tool call used unavailable `tools.wait` while the Daman Grand WW capture was running, stopping the capture after four emirates. The retry must use the outer wait tool only.
- Brave Google search was blocked by an unusual-traffic challenge while researching DARIC. No project files changed.
- Brave could not resolve the AXA Gulf locator hostname `locator.axa-gulf.com`; no AXA provider data was collected from that attempt.
- The archived AXA Star and Diamond PDF URLs returned 536-byte HTML challenge pages with HTTP 200, not PDFs. They were not imported as network sources.
- Brave reported `Download is starting` when navigating directly to the Google Sheets eCare exports; capture these URLs with a download event instead of reading the navigation response body.
- The system Python does not have `openpyxl`, so direct XLSX inspection failed. Use the project environment or an installed spreadsheet converter for these captured files.
- A direct Node invocation could not resolve the project-installed `playwright` module. Reuse the configured Node module path for subsequent Brave captures.
- The default `python3` interpreter could not resolve the installed Playwright package; the configured CLI uses Python 3.11 and requires that interpreter explicitly.
- Brave is installed at `/snap/bin/brave`, not `/usr/bin/brave-browser`; the first Python Playwright launch used the wrong executable path.
- Playwright returned the Daman response body as bytes; the first Basic Plus capture did not write a file because the writer expected text.
- Daman Basic Plus returned no records for all seven emirates through the official locator; no source CSV or plan was added.
- Sukoon's custom selector did not expose the expected `All Emirates` option in the first automated click flow; no provider search was submitted and no Sukoon data changed.
- A diagnostic Sukoon Playwright command had invalid Python lambda syntax; no browser search ran and no files changed.
- Sukoon uses custom menu items without ARIA `option` roles; the role-based selection attempt timed out before search submission.
- Sukoon text-based selection likely completed, but a follow-up diagnostic used an invalid button locator and timed out before confirming the selected values.
- The Sukoon Advance capture command was delayed by the external permission review and did not complete; retry with the existing approved Brave/Playwright workflow.
- Daman Essential 5 returned no records for all seven emirates; no plan or empty source was added.
- Daman Exclusive 1 WW, Network 06, and Network 08 each returned no records for all seven emirates; no empty plans were added.
- Daman Standard 2, Standard 3, and Comprehensive 2 WW each returned no records for all seven emirates; no empty plans were added.
- The workbook-link audit used the default Python interpreter instead of the configured Python 3.11 Playwright interpreter; it stopped before auditing links and changed no files.
- DARIC's official domains returned connection refused or timed out in Brave/Playwright; no current official network source was available from those domains.
- The first Union eCare Classic conversion skipped the header row and produced no parsed rows; no source file was written.
- The Union Nextcare Regional workbook contains Bahrain, Egypt, Kuwait, Lebanon, Oman, and Qatar only; it has no UAE rows, so no UAE network source was added.
- The guessed Union Restricted Network 3 URL returned HTTP 404; the official page must be re-read for its current link.
- A helper invocation used the wrong nested tool name while parsing the Aafiya workbook; no output file was written.
- A tool invocation was malformed while starting the Union NAS Workers Lite parser; no parser ran and no output file was written.
- The system Python 3.11 environment has no openpyxl package; workbook inspection must use the available LibreOffice/ZIP tooling.
- A malformed patch was submitted while recording the openpyxl failure; no project file was changed.
- A combined source-registration patch used an incorrect Readme.md context; the source and plan were then applied separately.
- The first Sapphire workbook download attempt raised Playwright's expected “Download is starting” navigation exception before saving the file; no source was written.
- The Sapphire download event produced an empty file; the same official URL must be fetched as a browser-context response before it can be imported.
- A retry used `browser.request` instead of Playwright's request-context API; it failed before fetching and left the empty placeholder unchanged.
- DNI's International MedNet workbook is a country-access table with no UAE provider rows; it was not imported as a network source.
- DNI's published Almadallah link is truncated and returns HTTP 404; no workbook was available to import.
- The current Daman UAE provider page loads an embedded NeoCloud frame, but the frame exposes no controls or provider rows in headless Brave; no additional tier could be queried in this pass.
- A shell heredoc was incorrectly combined with a trailing pipe while listing Daman JSON counts; the listing partially ran but the command ended with a Python NameError.
- Google search returned an unusual-traffic challenge for both broader UAE insurer network queries in Brave; no search results were obtained.
- A Brave probe script for Cigna and MetLife placed an `await` outside its async function and failed before visiting either site.
- A follow-up Cigna/MetLife page probe sliced the unevaluated Playwright coroutine; it stopped after reading Cigna and did not inspect MetLife.
- MetLife's official provider page links to a member-login-gated locator; no public provider rows or downloadable network file was available.
- The DARIC successor-site probe again sliced an unevaluated Playwright coroutine; it confirmed righthealth.ae is reachable but did not extract its links.
- Right Health's official insurance page contains no rendered insurer or network entries in Brave; it cannot substantiate a DARIC network source.
- Brave could not load the possible National General Insurance UAE domains; no official network source was found from that probe.
- A Daman form-inspection script again sliced an unevaluated Playwright coroutine after successfully reading the network option values; form links were not printed.
- An Alliance Insurance search invocation used unavailable nested tool `tools.exec`; no search ran.
- A source-registration patch used an incorrect Orient plan context; no files were changed by that failed patch.
- Daman's legacy provider-search form accepted the Comprehensive 3 option but returned no records and reset the plan selection; no source was added.
- Daman's Standard 2 AW Asia 2 query returned zero records for all seven emirates; its empty CSV was not registered as a plan.
- Daman's HC Comprehensive 3 query returned zero records for Dubai; no source was added.
- Daman's HC Al Aman3 query returned zero records for Dubai; no source was added.
- Daman HC Al Aman 3 Prime, HC Comprehensive 2/3 Peak/3 Pinnacle/3 Prime/5, and HC Exclusive 1 each returned zero Dubai records; no sources were added.
- Daman's Comprehensive 2 WW exc. US/Canada/Europe query returned zero Dubai records; no source was added.
- Daman Flexi returned zero Dubai records; the existing official Flexi source remains Abu Dhabi-only.
- The first web-search orchestration call was malformed by quoting and failed before issuing the insurer-network queries.
- The official MetLife EBP PDF URL now redirects in a loop to the site’s page-not-found route; it was not downloaded.
- Sukoon’s August 2026 Edge download button produced an empty Playwright download artifact; the PDF URL must be recovered from the button’s network request before import.
- A Sukoon request-inspection script sliced a dictionary instead of its key list; it failed after the click and did not print request URLs.
- The first multi-emirate Grand AW Asia 2 capture did not complete or write its CSV; the long sequential browser capture produced no result output.
- A Daman result-control probe sliced an unevaluated Playwright coroutine; the query itself succeeded but link inspection failed before export discovery.
- The first DNI Nextcare CSV export passed full metadata records to a narrow CSV writer; it failed before writing usable rows.
- A LibreOffice CSV conversion probe used a temporary directory that was cleaned before inspection, so it produced no files; no project data was changed.
- A Mistakes.md patch was malformed and rejected before editing; no project data was changed.
- The Sukoon workbook conversion script expected a Provider Type column in the general Healthcare Providers workbook; it failed after writing the four plan workbooks, so the general source was not refreshed.
- A post-validation Sukoon summary treated the integer provider count as a list and raised TypeError; validation and tests had already passed, and no data was changed.
- A second dataset summary assumed provider lists in data/plans.json; the schema stores an integer count, so the summary failed without changing data.
- Brave/Playwright received connection refused from all three attempted DARIC URLs; no official DARIC network file was available from those routes.
- The Sukoon second-page download script used a text-based Next selector that was not present; it failed before downloading any files.
- The Daman Comprehensive 2 probe selected an emirate label that is not present in the locator’s option list; it failed before querying the tier.
- Daman’s Comprehensive 2 all-emirates query returned zero table rows; the follow-up info element was absent and timed out.
- The first Narrow NW patch used a non-matching build_data.py context and was rejected; no project files were changed.
- The first ADNIC API extraction used Browser.request instead of a request context; it failed before downloading and importing the live catalog.
- The first ADNIC live-plan patch used an incorrect whitespace context and was rejected; no project files were changed.
- The first Takaful Emarat SharePoint download loop produced no saved files and ended without output; the SharePoint links need direct response inspection.
- The corrected Takaful Emarat download probe again used a Browser object where a Page was required; it failed before saving files.
- The Takaful Emarat link collector included a text-only span without an href; it failed before saving the workbook batch.
- RAK Insurance’s public API caps each emirate query at 50 records and ignores tested pagination parameters; the collected 334 records are incomplete, so no RAK plans were added.
- A RAK provider-type probe indexed the first empty category without checking for an empty response; it failed after confirming Hospital, Pharmacy, and Clinic filters work.
- RAK Insurance’s area-filter requests returned the same first 50 emirate records for different areas; area partitioning cannot bypass the API cap with the tested parameter.
- The first GIG locator request probe had a Python syntax error before opening the page; no data was changed.
- The corrected GIG locator probe could not find a visible exact-text SEARCH control; it timed out before querying A.5.
- The GIG A.5 probe was blocked by the locator’s confirmation dialog intercepting the Submit button; it timed out before querying.
- A GIG direct SearchResults probe referenced an uninitialized page variable (`sResultPerPage`) and failed before making the request.
- The first GIG A.5 pagination exporter used the Playwright request context, which rejected the locator certificate; it failed before saving records.
- A GIG pagination test received no fetch body for the `Next` request and failed in BeautifulSoup; no source file was written.
- A GIG maximum-page-size probe again received no fetch body from the public endpoint; no source file was written.
- The GIG native List-view probe found the control hidden after the cookie flow and failed before changing views.
- The GIG public JavaScript request failed certificate verification in Playwright’s separate request context; no data was changed.
- The GIG A.4 NMC Royal Sharjah probe hit an intermittent certificate-authority error before loading the locator.
- The first GIG A.4 Burjeel plan patch used a non-matching build_data.py context and was rejected; no project files were changed.
 - GIG Gulf A.2 Plus outpatient locator probe returned zero provider cards; no source file was created.
 - MetLife locator probe script failed after loading because Playwright `page.url` was called as a function; no project data changed.
 - The first A.3 base mapping patch did not match the current `build_data.py` context; no project files changed.
 - The GIG A.5 partner probe script had an indentation syntax error; no project files changed.
 - GIG A.5 + PRIME returned 2,557 cards on one probe but zero on the immediate download retry; the inconsistent result was not imported.
 - RAK Insurance network-type filters were ignored by the public API; all eight generated files were identical 331-record catalogs and were removed without import.
 - Running `assign_networks.py` after the A.1 excl CCAD import rewrote assignment metadata with counts that did not match plan JSON files; rerunning `build_data.py` alone restored consistent validated artifacts.
 - The first A.Eco 1 inpatient mapping patch did not match the current `build_data.py` context; no project files changed.
 - Firecrawl received HTTP 403 from Watania’s official medical page; no network document could be inspected.
 - Firecrawl RAK Insurance official-domain search produced no result output after timing out; no files changed.
- Playwright could not launch `/snap/bin/brave` inside the sandbox because Snap confinement lacked `cap_dac_override`; retry outside the sandbox.
- Validation failed after the SEHA capture because existing generated plan JSON files were partially written/corrupted; rebuild the generated data before validating.
- The Brave/Playwright SERCO capture returned no output files for A.1 SERCO; no catalog was added.
- The diagnostic GIG SERCO retry failed before execution because inline shell quoting malformed the JavaScript string; no site request was made.
- Firecrawl search failed with `getaddrinfo EAI_AGAIN api.firecrawl.dev`; continued with a Brave search-page fallback.
- Google search via Brave was blocked by an automated-traffic challenge; Bing returned unrelated Aman results, so no official Aman network source was identified.
- The multi-query web search for DARIC, Noor, and Emirates NBD failed locally because the tool-call query string was malformed; no request was sent.
- MetLife's current search result linked to a stale PDF URL that redirects repeatedly to `/en/pagenotfound/`; Playwright downloaded no network file.
- Daman's live search-form request did not return within the Playwright response wait window; no provider data was collected from that probe.
- Daman legacy `Comprehensive 5` search exposed the plan selector but did not return a provider response within the Playwright timeout.
- Extended Playwright polling for Daman `Comprehensive 5` again produced no browser output; the legacy search is not reliably consumable in this environment.
- Direct POST to Daman's legacy search with network ID `190` returned the form with “Please select Facility Plan/Network Type”; no provider rows were returned.
- Capturing Daman's UI POST payload hung during the search click and produced no request payload or provider data.
- MetLife network PDF retrieval failed for non-www, query-string, and HTTP URL variants; no PDF response was returned.
- The Noor/Dar Al Takaful multi-query web search failed locally during tool-call string parsing; no web request was sent.
- Daman batch capture failed on `Comprehensive 3`; the AJAX response was only 181 bytes and did not contain provider rows, so no batch catalogs were accepted.
- Daman `Royal WW exc. US CAN` capture produced no response file during the Playwright run; no catalog was accepted.
- Daman `Supreme WW exc. US CAN` capture produced no usable response file during the Playwright run.
- Daman `HC Comprehensive 5` selector returned the valid 181-byte empty AJAX response; no provider rows were available to capture.
- The Dubai Insurance/DARIC search tool call was malformed before execution; no web request was sent.
- The follow-up Dubai Insurance search tool call was malformed before execution; no web request was sent.
- DubaiCare’s cross-origin API fetch failed inside the page; no provider JSON was saved in that capture attempt.
- The DubaiCare batch script used unescaped percent signs in the URL format string and failed before requesting data.
- The DubaiCare API request returned a response with `data: null` to the Playwright request context; the batch script stopped before saving records.
- DubaiCare’s provider API returned HTTP 403 even with the official page referer and origin; no provider records were captured.
- The DubaiCare 42-page browser paging run terminated without output after the first-page capture; the saved file remains at 100 records.
- The smaller DubaiCare batch also terminated before saving additional pages; the saved file remains at 100 records.
- The single-page DubaiCare retry inspected the response before the asynchronous provider request completed; no additional page was saved.
- The DubaiCare list-view probe used a non-exact `List` role locator and hit strict-mode ambiguity; no paging action occurred.
- The exact-selector DubaiCare retry terminated during the long page load before producing output; no additional records were saved.
- The response-driven DubaiCare next-page click did not complete within the tool window; the prior browser response increased the saved collection to 600 records.
- The DubaiCare multi-page 8–10 run terminated before saving further pages; the single-page method remains reliable.
- MetLife’s indexed `mednet-network.pdf` URL redirects to `/en/pagenotfound/`; Playwright downloaded no PDF.
- The MetLife alternate-URL probe used an unsupported Playwright request option and failed before testing either URL.
- MetLife alternate EBP PDF navigation failed in Brave with a browser error page; no PDF was downloaded.
- Al Sagr workbook inspection could not use `openpyxl` because it is not installed; the raw workbooks remain available for later normalization.
- The standard-library Al Sagr workbook converter encountered rows shorter than the header and stopped; no normalized Al Sagr CSV was written.
- Al Sagr NAS Comprehensive workbook parsing initially assumed country code `UAE`; the workbook uses `United Arab Emirates`, so that attempt produced zero rows.
- Al Sagr Value July workbook has a merged title row containing `PROVIDER NETWORK`; the generic header detector selected it and produced zero rows.
- Al Sagr Value Lite July conversion referenced sparse worksheet columns without checking key presence; no normalized file was written.
- QIC UAE’s official medical page did not finish loading within the Brave/Playwright window; no network link was extracted.
- QIC Value Lite workbook normalization assumed fixed XML column positions and produced zero rows; the official raw workbook was downloaded successfully and remains intact.
- Alliance workbook inspection used the display-name `.xlsx` paths, but the downloaded files were saved with `.pdf` suffixes; no workbook was read.
- Refreshing `assign_networks.py` after the QIC import produced the project’s known generated-file/assignment mismatch; validation reported 454 consistency errors. No further assignment refreshes should be run without a controlled rebuild.
- Restoring the assignment baseline with Git failed because the repository index is read-only; the repair command did not change project files.
- QIC individual medical page did not return within the Brave/Playwright window; no RN4 network link was extracted.
- The QIC verification attempted to call a non-existent orchestration tool method; no project command ran.
## 2026-08-30

- Web search query construction failed because a quoted wildcard was not escaped. No project data changed.
- A second web search call failed while parsing a wildcard-domain query. No project data changed.
- A web search call failed while parsing an embedded quoted phrase. No project data changed.
- Direct download of the official Union NAS workbook failed in the sandbox because DNS resolution was unavailable. No project data changed.
- Official Al Dhafra PDF URL returned HTTP 404 during download; no data changed.
- Salama’s official TOB PDF URL returned HTTP 404 during archival download; the official search result still identifies MedNet EBP. No data changed.
- Salama’s current MediShield PDF download failed TLS verification because the host certificate is expired. No data changed.
- A combined NextCare inspection command was rejected because it would print public page content containing API credentials. No data changed.
- The guessed NextCare child-theme JavaScript URL returned HTTP 404. No data changed.
- A direct NextCare provider API request returned HTTP 500; the endpoint likely requires browser session state or request headers. No data changed.
- Retrying the NextCare API with the form’s `uae` country value still returned HTTP 500. No data changed.
- Playwright CLI was available through npx, but Node could not resolve the package for an inline script. No data changed.
- npm package runner also failed to expose Playwright to Node (`MODULE_NOT_FOUND`). No data changed.
- npx’s command-wrapper retry still could not expose Playwright to Node. No data changed.
2026-08-30: Firecrawl search requests failed with DNS error EAI_AGAIN for api.firecrawl.dev; used the web search fallback.
2026-08-30: Two inline Brave/Playwright attempts to capture the Medgulf postback download produced no download file or diagnostic output; the download remains uncollected.
2026-08-30: A diagnostic command that requested all postback response headers was rejected because it could expose session secrets; no headers were printed.
2026-08-30: Direct Medgulf `__doPostBack` invocation failed in the page with a strict-mode JavaScript caller/callee error; no data changed.
2026-08-30: Medgulf form submission through Playwright request context returned no observable response before the browser process ended; no data changed.
2026-08-30: The first web-search tool call had malformed JavaScript string syntax; it returned no search results, and the query was retried successfully.
2026-08-30: Brave `page.goto` reported “Download is starting” for the direct Neuron workbook URL instead of returning a response body; the workbook was not saved by that attempt.
2026-08-30: The system Python environment does not have `openpyxl`; workbook inspection must use the project’s existing spreadsheet tools instead.
2026-08-30: LibreOffice could not convert the downloaded Neuron/NAS workbooks in the restricted environment; no CSV output was produced.
2026-08-30: `uv run --with openpyxl` could not fetch the package because DNS access to PyPI was unavailable; workbook parsing used the XLSX XML format instead.
2026-08-30: A web-search call containing quoted search terms was rejected by the tool’s JavaScript parser; no results were returned.

- 2026-08-30: Web search tool rejected a query containing quoted text with a JavaScript syntax error; retried with a single unquoted query.
- 2026-08-30: The project root does not have a directly resolvable Playwright module; the existing script uses the shared `/tmp/nextcare-playwright` installation instead.
- 2026-08-30: Brave Playwright launch failed inside the sandbox because snap-confine lacked the required capability; retry requires an escalated browser launch.
- 2026-08-30: The ADNIC Playwright download attempt completed without a download artifact or diagnostic output; the page's ASP.NET postback did not expose a usable file event.
- 2026-08-30: The current MetLife MedNet PDF URL redirected to the site’s page-not-found route; Playwright exceeded its redirect limit and no file was saved.
- 2026-08-30: Medgulf’s ASP.NET “Download All Network List” postback did not emit a Playwright download event within 90 seconds.
- 2026-08-30: Sukoon’s August 2026 Edge download emitted a Playwright download event, but `download.saveAs()` failed because the temporary artifact disappeared before copying.
- 2026-08-30: A retry that would print and reuse Sukoon’s signed download URL was rejected by the safety layer; the signed URL was not exposed or reused.
- 2026-08-30: A diagnostic that printed HTML around Sukoon download entries was rejected because rendered markup could contain signed URLs; no URL or markup was exposed.
- 2026-08-30: The Sukoon Healthcare Providers response was an XLSX payload with an `.xls` filename; passing it to the XLSX-only importer raised `BadZipFile`.
- 2026-08-30: The first multiline parser for Takaful Emarat’s excluded-provider PDF assumed all 93 records had a recognized emirate and raised an index error; no output was written.
- 2026-08-30: The first Al Buhaira refresh parsed only page 1 because the pagination parser did not account for HTML-escaped ampersands; the refresh was stopped before processing the remaining tiers.
- 2026-08-30: An initial patch for the Al Buhaira pagination regex did not match the generated script text; the correction is being applied against the exact line.
- 2026-08-30: Web search tool rejected a multi-query request with a JavaScript syntax error; retrying each query separately.
- 2026-08-30: Sukoon Vital Eco workbook used a shifted provider header layout; the generic normalizer raised `IndexError`. Reparse using the workbook's `Provider Name` column at index 2.
- 2026-08-30: Medgulf Brave/Playwright launch failed because the sandbox could not run `/snap/bin/brave` (`snap-confine` missing `cap_dac_override`).
- 2026-08-30: An ADNIC Brave/Playwright inspection command was rejected because it would have printed unredacted frame URLs; retry with URL-safe diagnostics only.
- 2026-08-30: ADNIC’s rendered download card text was not an exact DOM text node; the exact-text Playwright locator found zero elements and timed out.
- 2026-08-30: An ADNIC DOM diagnostic was rejected because it attempted to print raw href attributes; no URL-bearing attributes were exposed.
- 2026-08-30: Union’s NAS download link was present but hidden in the rendered table; the initial Playwright click timed out waiting for visibility.
- 2026-08-30: Union’s rendered NAS download returned a 2014 workbook containing terminated/closed providers, despite the current page label. Rejected as stale and left unmapped.
- 2026-08-30: ADNIC Platinum interaction returned a navigated-away response before Playwright could read its body (`Network.getResponseBody` unavailable). Retry with navigation-response capture.
- 2026-08-30: ADNIC Platinum form submission aborted navigation (`ERR_ABORTED`), so the navigation-response capture did not obtain the file.
- 2026-08-30: ADNIC form replay passed an unresolved Playwright header promise to the request context; it rejected because the header value was an object instead of a string.
- 2026-08-30: The automated ADNIC Platinum mapping edit placed the source filename outside the plan tuple and caused a syntax error. Corrected manually before validation.
- 2026-08-30: A Daman API-route inspection command had shell quoting syntax errors; no request was made.
- 2026-08-30: The corrected Daman inspection still had over-escaped JavaScript regex syntax and failed before execution.
- 2026-08-30: A Daman route check was rejected because it attempted to print raw HTML fragments; no sensitive fragment was exposed.
- 2026-08-30: A Daman JavaScript inspection command was rejected because it would have printed matching bundle lines; retry with redacted route extraction.
- 2026-08-30: The redacted Daman bundle regex was still considered too broad and rejected before execution; no bundle content was exposed.
- 2026-08-30: The NGI action-target extraction command had shell quoting errors and failed before execution.
- 2026-08-30: NGI’s network control did not expose a PDF target in its `onclick` attribute; the downloader stopped before making a request.
- 2026-08-30: DNI link inspection attempted to construct a URL from a non-URL anchor value and failed; no link data was exposed.
- 2026-08-30: Daman domestic-finder diagnostics were rejected because they would print hidden control values; no values were exposed.
- 2026-08-30: Fidelity United HTML inspection was rejected because a broad PDF regex could print arbitrary markup; no page content was exposed.
- 2026-08-30: MediFinder Daman-link inspection was rejected because it would print a raw third-party href; no URL was exposed.
- 2026-08-30: A MediFinder network-response inspection command had a JavaScript parenthesis error; no response content was exposed.
- 2026-08-30: The Daman Visitors filter experiment clicked non-filter heading buttons and produced zero extracted records; the experimental block was removed from the extractor.
- 2026-08-30: Medgulf’s alternate POST replay did not complete within the browser session and produced no workbook; no file was saved.
- 2026-08-30: The DARIC web-search request failed because the search payload contained malformed quoted query syntax; no search ran.
- 2026-08-30: The DARIC search tool continued rejecting the plain query payload with a parser error; no search ran.
- 2026-08-30: The multi-query GIG legacy-AXA search payload failed with a web-tool parser error; no search ran.
- 2026-08-30: The multi-query Gulf Insurance search payload triggered the web-tool parser error; no search ran.
2026-08-30: Brave/Playwright MEDGULF download failed because snap-confine lacks cap_dac_override in the sandbox.
2026-08-30: Elevated MEDGULF Playwright click completed but produced no saved download file; source remains uncollected.
2026-08-30: MEDGULF's visible controls are JavaScript postbacks with no Playwright download event or saved workbook; both controls were tested.
2026-08-30: A MEDGULF inspection command was rejected because it would have printed hidden form values; no secrets were exposed.
2026-08-30: Direct MEDGULF ASP.NET postback closed the Playwright page before a response was available; no network document was saved.
2026-08-30: Isolated-context MEDGULF postback also closed the page before Playwright exposed a download or response.
2026-08-30: MEDGULF selected-provider export submitted a POST request, then closed the page before Playwright exposed the response.
2026-08-30: A broad FMC frontend-bundle inspection was rejected because it could print embedded request data; no sensitive data was exposed.
2026-08-30: FMC multi-city search returned an empty/non-JSON response for one city, so the browser probe could not complete.
2026-08-30: An FMC probe was rejected because it would have printed provider response content; no provider data was exposed.
2026-08-30: Adamjee's July 2023 download click produced no saved Playwright artifact; no network file was collected.
2026-08-30: The bounded Zavis retry failed at sitemap fetch because DNS resolution temporarily failed; the existing CSV was not changed.
2026-08-30: Applying the refreshed Zavis crosswalk caused validation to report a missing Takaful provider index (2383); diagnosis is in progress.
2026-08-30: A malformed inspection tool call failed while checking the Zavis crosswalk entry for provider index 1416.
2026-08-30: An Adamjee link-inspection command was rejected because it would have printed raw onclick metadata; no sensitive data was exposed.
2026-08-30: RAK Insurance exposed a download event, but Playwright could not copy its temporary artifact using a relative destination.
2026-08-30: RAK Insurance's Playwright download event produced a zero-byte artifact; the advertised workbook was not collected.
2026-08-30: A direct Node Playwright module lookup failed because Playwright is installed in the project helper directory, not the default Node module path.
2026-08-30: A malformed empty patch failed while recording the Playwright lookup failure; no project files were changed by that patch.
2026-08-30: FMC Brave/Playwright launch failed in the sandbox because snap-confine lacked cap_dac_override; retry requires elevated browser execution.
2026-08-30: FMC Playwright reached the page, but the probe assumed JSON from a relative settings endpoint and received an HTML response; no provider data was written.
2026-08-30: MEDGULF elevated Brave/Playwright retry triggered the ASP.NET POST, but the target page closed before waitForResponse completed; no network file was saved.
2026-08-30: Allianz Brave/Playwright provider-finder probe ended without output or an HTML artifact; no public roster or endpoint was captured.
2026-08-30: SAICO guide URL returned Brave's PDF viewer HTML shell (536 bytes), not the PDF bytes; the invalid artifact was removed.
2026-08-30: An empty README patch failed while recording the successful SAICO guide capture; no project files were changed by that patch.
2026-08-30: LibreOffice did not emit CSV output when converting the downloaded DNI Aafiya workbook; the workbook remains preserved as the authoritative XLSX artifact.
2026-08-30: A combined ToDo/README patch failed because the README wording differed from the expected context; no changes from that patch were applied.
2026-08-30: A malformed patch failed while creating the DNI MedNet normalizer; no project files were changed by that patch.
2026-08-30: A combined Lifeline ToDo/README patch failed because the README context differed; no changes from that patch were applied.
2026-08-30: A malformed patch failed while creating the DNI Aafiya/NAS normalizer; no project files were changed by that patch.
2026-08-30: A second malformed patch failed while creating the DNI Aafiya/NAS normalizer; no project files were changed by that patch.
2026-08-30: DNI’s official Al Madallah link resolves to a truncated URL and returns HTTP 404; no workbook was available to download.
2026-08-30: DNI Al Madallah URL extension retries (.xlsx, .xls, and spaced .xlsx) all returned HTTP 404; no official workbook was recovered.
2026-08-30: The official MetLife MedNet network URL found in search redirects repeatedly to the page-not-found route; Playwright reached the redirect limit and saved no document.
2026-08-30: NGI’s Brave/Playwright form-control probe ended without output after the page load; no additional network data was captured.
2026-08-30: The existing NGI HealthNet downloader found no current network target in the changed Downloads page; no files were saved.
2026-08-30: An NGI inspection command was rejected because it would print hidden onclick metadata; no sensitive data was exposed.
2026-08-30: A patch to correct NGI’s download-event ordering did not match the one-line probe source; no project files were changed by that patch.
2026-08-30: A combined delete/add patch for the NGI probe was rejected because apply_patch does not accept multiple operations on one path.
2026-08-30: NGI’s three visible HealthNet network-provider download controls were clicked with Brave/Playwright, but none emitted a download event.
2026-08-30: NGI response-capture retry produced no output or saved PDF before the browser process ended; no provider files were captured.
2026-08-30: Aafiya’s public network PDF URL found in search now returns HTTP 404; no independent insurer-hosted file was recovered.
2026-08-30: The Union Aafiya column inspection assumed every cell had a value node and failed on an empty header cell; no workbook data was changed.
2026-08-30: Fidelity United’s Brave/Playwright page probe ended without output or a saved artifact; no new network file was captured.
2026-08-30: The first sparse-cell Union NAS parser used the wrong header row/sheet mapping and stopped before creating dated CSVs; build validation itself still passed.
2026-08-30: The corrected Union NAS parser reached the official header but initially requested non-existent tier names; no CSVs were written by that attempt.
2026-08-30: A second Union NAS normalizer patch failed because one generated function line lacked the patch marker; no project files were changed by that patch.
2026-08-30: The first Union eCare Classic/Green normalizer assumed dense rows and stopped on sparse cells; no eCare Classic/Green CSVs were created.
2026-08-30: The Union current Aafiya workbook inspection assumed every cell had a value node and failed on an empty cell; no workbook data was changed.
2026-08-30: The DNI Neuron normalizer created Global Choice (3,785 UAE providers), then found no marked BSBG rows in the renewal workbook and stopped before creating a renewal CSV.
2026-08-30: The corrected DNI Aafiya/NAS normalizer produced four Aafiya and five NAS tier files, then stopped because the official NAS Workers column contained no marked providers.
2026-08-30: Firecrawl setup was authenticated, but the search request failed with a transient DNS error resolving api.firecrawl.dev; no search result was obtained.
2026-08-30: A second Firecrawl search retry failed with the same DNS resolution error for api.firecrawl.dev; no DARIC source was returned.
2026-08-30: The local FMC workbook inspection could not import openpyxl in the system Python; no workbook data was changed.
2026-08-30: The FMC web-search query batch was malformed in the tool request and returned a client-side syntax error; no search was performed.
2026-08-30: The FMC HospitalsDubai.pdf Playwright capture failed inside the sandbox because snap-confine rejected Brave capabilities; no PDF was saved.
2026-08-30: The elevated FMC HospitalsDubai.pdf request returned HTTP 200 with text/html instead of PDF bytes; no provider artifact was saved.
2026-08-30: The first ADICO/Aman/DARIC web-search batch failed with a client-side tool syntax error; no search results were obtained.
2026-08-30: A broad temporary-directory inspection encountered permission-denied systemd directories; no project data was affected.
2026-08-30: A MEDGULF page-inspection command was rejected because it would print raw HTML/script matches; no page content or secrets were exposed.
2026-08-30: MEDGULF’s official Download All Network List control produced no Playwright download event within 30 seconds; no workbook was saved.
2026-08-30: The Insurance House search batch failed with a client-side tool syntax error; no search results were obtained.
2026-08-30: The HAYAH build/ToDo/README patch failed because its README context did not match; no changes from that patch were applied.
2026-08-30: HAYAH’s Nextcare download control produced no Playwright download event; its MedNet workbook was captured successfully, but no Nextcare file was saved.
2026-08-30: HAYAH’s official Nextcare workbook URL returned HTTP 502 with text/plain; no workbook was saved.
2026-08-30: A Brave retry of HAYAH’s official Nextcare workbook also returned HTTP 502 (text/html); no workbook was saved.
2026-08-30: A later HAYAH Nextcare workbook retry still returned HTTP 502 (text/plain); no workbook was saved.
2026-08-30: The elevated MEDGULF Brave/Playwright downloader closed the ASP.NET page before its POST response became available; no network file was saved.
2026-08-30: MEDGULF context-level POST interception returned text/plain HTTP 200 and no workbook; the second download control timed out and no file was saved.
2026-08-30: Allianz official UAE network-options page returned a Cloudflare challenge to Brave/Playwright; no provider roster was available.
2026-08-30: A MEDGULF request-tracing command was rejected because it would print unredacted request URLs that could contain hidden tokens; no page data was exposed.
2026-08-30: The web-search request for DARIC plan names failed because the tool rejected malformed query encoding; no data changed.
2026-08-30: The first DARIC mapping patch did not apply because the source lines had different spacing; no data changed.
2026-08-30: The SAICO web-search request failed in the web tool parser; no data changed.
2026-08-30: The ADNTC Playwright download attempt used a nonexistent locator.download API; the target workbook was already present and valid, so no data changed.
2026-08-30: The global Python environment lacks openpyxl, so direct inspection of the ADNTC workbook failed; existing normalized CSVs remain available.
2026-08-30: LibreOffice could not export the multi-sheet ADNTC workbook to CSV in the sandbox; workbook XML inspection succeeded and confirmed the NETWORK LIST sheet.
2026-08-30: FMC public-locator submission hung after the filter-completion click and the browser process ended without returning result text; no file was saved.
2026-08-30: FMC’s discovered browser API returned an empty/non-JSON response for the provider search request; no API export was saved.
2026-08-30: The FMC no-filter browser API probe exited without a response; no data changed.
2026-08-30: FMC’s exact-city API probe returned an empty non-JSON response, so automated tier collection could not proceed; no data changed.
2026-08-30: The first FMC request-context test had a JavaScript try/finally syntax error; no request was sent and no data changed.
2026-08-30: FMC’s provider search without providerType returned an empty non-JSON response; no data changed.
2026-08-30: FMC Farid GN-2 Dubai hospital collection stalled on slow API requests and ended without saving the partial export.
2026-08-30: The FMC catalog documentation patch did not apply because the README wording differed; no source data changed.
2026-08-30: FMC representative-area collection saved an Ajman partial file, then stopped when a later emirate city response had no usable data; no complete UAE sample was produced.
2026-08-30: The Watania web-search request failed in the web tool parser; no data changed.
2026-08-30: An internal tool orchestration snippet was malformed while starting the Watania source audit; no command ran and no data changed.
2026-08-30: The first Mistakes.md append patch was malformed; no project data changed.
2026-08-30: MEDGULF Brave/Playwright retry closed the page during the ASP.NET postback before a response completed; no workbook was saved.
2026-08-30: MEDGULF form-state replay did not return a saved response; the browser closed during the checkbox postback and no workbook was created.
2026-08-30: The first SAICO portal probe was rejected because it attempted to print portal content and full URLs; no portal request ran.
2026-08-30: The build-data search command used an invalid ripgrep expression; no project data changed.
2026-08-30: The follow-up build-data search repeated the invalid ripgrep expression; no project data changed.
2026-08-30: The corrected MEDGULF download-form replay still terminated without a response or workbook; no file was saved.
2026-08-30: The MEDGULF broader-directory probe could not find the All TPA option by label and timed out; no data changed.
2026-08-30: Firecrawl search for an indexed MEDGULF network document failed with DNS error EAI_AGAIN; no search results were returned.
2026-08-30: The broker-archived MEDGULF provider PDF returned HTTP 500 through Playwright; no reference file was saved.
2026-08-30: Allianz’s official April 2025 factsheet URL returned HTTP 403 through Playwright; no file was saved.
2026-08-30: The MEDGULF downloader was corrected to share Brave cookies and headers, but the process still terminated before returning a response or saving the workbook.
2026-08-30: The Zavis refresh crawl failed on sandbox DNS resolution before any output was written.
2026-08-30: The external-network Zavis refresh also terminated without producing an output file; the current Zavis CSV was preserved.
2026-08-30: The full Zavis coordinate enrichment terminated in the sandbox before producing output; the source index was preserved.
2026-08-30: The external-network full Zavis enrichment terminated before writing output after detail-page failures; the source index was preserved.
2026-08-30: The first resumable Zavis crawler repeated zero-progress batches indefinitely because it did not stop when a batch added no coordinates; it was stopped and patched.
2026-08-30: The local HTTP server smoke-test could not bind port 8765 in the sandbox; no application data changed.
2026-08-30: The escalated local HTTP server smoke-test was rejected because it would serve the whole project directory; no application data changed.
2026-08-30: The first Allianz PDF bbox parser expected lowercase coordinate attributes; the parser failed before producing output.
# 2026-08-31 — MEDGULF reference download used a removed hard-coded Playwright path

`medgulf_reference_download.js` failed because `/tmp/nextcare-playwright/node_modules/playwright` does not exist. Locate the current Playwright installation before retrying.

# 2026-08-31 — MEDGULF broker archive returned HTTP 500

The archived provider-list URL returned an HTML 500 response, so no roster was saved.

# 2026-08-31 — Allianz current benefit guide denied automated download

The official January 2026 PDF URL returned HTTP 403 through Playwright request context; no replacement file was saved.

# 2026-08-31 — MEDGULF postback did not return a workbook

The official page rendered and exposed the expected ASP.NET controls, but the scripted postback produced no workbook response or saved file. The form target was corrected to the primary form for the next retry.

# 2026-08-31 — MEDGULF indexed archive returned HTTP 404

The publicly indexed broker PDF URL returned 404 when downloaded directly, despite search-index content exposing sample UAE rows; no archive copy was saved.

# 2026-08-31 — Allianz Provider Finder guidance denied automated download

The official Provider Finder flyer URL returned HTTP 403 through Playwright; its indexed content was reviewed but no local copy was saved.

# 2026-08-31 — MEDGULF bulk extractor selected during asynchronous postback

The first all-TPA extractor captured zero Nextcare rows and timed out selecting UAE because the country options were still being replaced; it also targeted the wrong table. The extractor is being corrected to wait for options and use the provider table.

# 2026-08-31 — MEDGULF CSV merge found an unnamed pagination column

The first merge failed because the browser capture included an extra unnamed CSV field. The merge will ignore that structural column.

# 2026-08-31 — MEDGULF dedicated NAS capture timed out

The NAS postback did not expose UAE options within the timeout; the previously captured NAS rows remain available for the combined merge.

# 2026-08-31 — MEDGULF final merge encountered another unnamed field

A dedicated capture included an extra pagination field; the final merge needs `extrasaction=ignore` for that structural column.

# 2026-08-31 — Liva workbook batch conversion produced no CSVs

The first LibreOffice headless batch emitted no converted files. Retry with one workbook and an isolated writable profile.

# 2026-08-31 — uv XLSB parser used a read-only cache

The first `uv run --with pyxlsb` parse failed because uv could not initialize `/home/tony/.cache/uv`; retry with a temporary cache directory.

# 2026-08-31 — uv could not fetch pyxlsb with temporary cache

The retry failed on a temporary DNS lookup error for pypi.org; the Inayah XLSB remains unparsed.

# 2026-08-31 — Inayah XLSB writer shadowed its field list

The XLSB extraction succeeded, but CSV writing failed because a file handle reused the field-list variable name. The writer was corrected before retry.

# 2026-08-31 — Coordinate backlog parser rejected a large CSV field

`geocode_backlog.py` failed on an oversized provider address field. Added a larger CSV field limit before retrying.
## 2026-08-31

- `saico_probe.js` used a stale Playwright module path under `/tmp`; the probe failed before opening the provider portal.
- The web-search tool call was malformed due to a JavaScript string syntax error; no request was sent.
- A second web-search tool call was rejected by the wrapper parser before dispatch; no request was sent.
- The inline Zurich download command had an async-IIFE invocation typo and failed before downloading.
- The April International MediFinder capture did not produce an HTML artifact; the browser process ended without a usable result.
- The hydrated April capture found two “Load more” buttons and failed strict locator matching; the locator now selects the last control.
- The April field-extraction check assumed title-cased raw filenames, but the parameterized collector writes lowercase tier names; the check failed before reading data.
- The April field extractor repeated the same filename-case assumption for Classic; it failed before changing any CSV.
- The parallel April enrichment repeated the lowercase filename assumption for Classic; Premium completed, Classic did not run.
- The April discrepancy check passed a generator instead of file text to the regex; it failed before reading the snapshots.
- The APRIL registry-match check used the invalid encoding label `utf8-sig`; it failed before reading the registry.
- The first APRIL fuzzy-match review exceeded the 30-second command window because it recomputed comparisons for every row; no review file was written.
- The corrected discrepancy check still assumed lowercase Classic filename; no snapshot was read.
- The official APRIL workbook inspection attempted to import unavailable `openpyxl`; the archive download succeeded, but that parser was not installed.
- `saico_probe.js` could not launch Brave because snap confinement refused the `/snap/bin/brave` executable; no provider portal was opened.
- The insurer discovery search wrapper rejected an unescaped quote in the query string; no search request was sent.
- The first MetLife Brave download snippet called `browser.request`; Playwright requires a browser context request, so it failed before downloading.
- The MetLife network PDF URL now redirects to a looping page-not-found response; no replacement file was downloaded.
- Firecrawl was authenticated, but its API request failed with temporary DNS error `EAI_AGAIN api.firecrawl.dev`; no discovery result was written.
- The monitoring poll used an expired background session ID after the Al Buhaira capture had already finished; validation through the output file confirmed completion.
- Firecrawl search failed again with temporary DNS error `EAI_AGAIN api.firecrawl.dev`; no discovery result was written.
- The current MetLife MedNet PDF URL now redirects to a looping page-not-found response; no current PDF was downloaded.
- The first Cigna PDF XML extraction tried to parse `pdftohtml` stdout, but that command requires a file output path; no CSV was written.
- The DHA participating-insurers page returned HTTP 502 during a follow-up open; no additional insurer list was retrieved.
- The FMC bundle probe used an invalid CSS selector with an unquoted attribute value; no request was made to the page bundle.
- A follow-up FMC header probe was refused by Brave snap confinement before page launch; the RPC request shape was already captured successfully.
- The first direct FMC RPC replay passed HTTP/2 pseudo-headers to Playwright’s request API; the API rejected `:authority` before sending.
- The Dubai Care batch collector expected a “Load more” button on the small N5 IP tier; that page has no button, so the batch stopped before collecting N5 IP.
- The MediFinder Lifeline catalog click returned a cache-miss error; no page content was retrieved.
- A direct open of the MediFinder Lifeline URL also returned a cache-miss error; no page content was retrieved.
- The Lifeline mapped/unmatched total probe had a JavaScript parenthesis error; request payload tracing still confirmed separate `p_has_coords=true` and `false` calls.
- Firecrawl CLI scrape of health.damana.com failed with DNS EAI_AGAIN for api.firecrawl.dev; continued with direct browser probing.
- SAICO portal probe could not load Playwright from the historical /tmp/nextcare-playwright path; locating the current installed module.
- Direct curl to health.damana.com also failed because the host could not be resolved; SAICO portal capture is deferred until DNS/service access returns.
- Web search call for MSH, Now Health, and eCare failed because the tool input contained an unescaped quote; no external state changed.
- E-Care MediFinder capture could not launch Brave inside the sandbox because snap-confine refused execution; retry requires escalated browser access.
- E-Care collector captured Blue, Green, and Classic but the Silver route had no embedded network ID; Silver is not indexed pending a verified API route.
- MSH extraction succeeded with 1,085 rows, but the follow-up head/wc check used the wrong filename; no data was changed by the failed check.
- Web search call for Emirates NBD, Gulf Insurance, and AXA failed with a tool-side syntax error; no external state changed.
- GIG/AXA audit command was not executed because of a malformed tool call; no external state changed.
- MSH additional-tier web search failed with a tool-side syntax error; no external state changed.
- MEDGULF audit command was not executed due to a malformed tool call; no external state changed.
- GIG current downloader failed because its historical `/tmp/nextcare-playwright` Playwright module path no longer exists; locate the active installation before retrying.
- Direct curl to the GIG locator JavaScript failed with a local CA certificate verification error; browser access remains available.
- Filtered curl request for the GIG locator search handler stalled while streaming the JavaScript; the locator page itself remains available.
- Initial GIG bulk capture completed A.1, then reused stale pagination state for A.2 and returned zero rows with the previous 3,272 count; the pass was stopped before indexing misleading output.
- Corrected GIG capture launched without elevated Brave permission and failed at snap-confine startup; rerun with escalated browser execution.
- Git staging failed because the workspace exposes `.git` as read-only; Git could not create `.git/index.lock`.
