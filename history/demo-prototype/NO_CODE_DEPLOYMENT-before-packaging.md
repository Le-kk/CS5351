# Research Presentation Console

This exported English frontend is served by the local Python backend at http://127.0.0.1:8766. It performs real model calls only after Validate, Confirm and Start. Model credentials stay in the project's existing backend configuration; do not put secrets in frontend files.

## Start

Double-click `Start Research Console.command` in this folder. Keep its terminal window open. Stop with Control-C. The launcher reuses the configured project Python environment. Set CONSOLE_PYTHON to another installed project interpreter if needed.

For manual setup, install the project's declared dependencies in a virtual environment, run `npm ci --ignore-scripts` then `npm run build` here, and from the project repository run:

    python -m demo.console --port 8766 --frontend-dir ../../nocode/build --open

This is a local presentation deployment, not an Internet-hosted service.

## Demonstration

1. Select ticker/date, analysts, research/risk rounds and the configured models. Optional model-request limit counts requests, not tokens.
2. Select no portfolio, explicit empty portfolio, or paste/upload validated JSON. Positions use the `positions` field, not `holdings`.
3. Validate the configuration, inspect its fingerprint and confirm it. Changing settings requires another confirmation.
4. Start a real run. View the actual analyst reports, Bull/Bear debate, trader plan, risk debate and provider token counts as stages finish.
5. Open Results & Files to preview/download Markdown, HTML, manifest, discussions and events. Run history survives backend restart; interrupted runs are labelled INTERRUPTED.

Only sanitized public reports are exported, not hidden reasoning, system prompts or raw tool arguments. Missing token counts are not zero. COMPLETED/PASSED is the existing output check, not proof every financial statement is correct. Historical news, social and macro feeds can be unavailable; the console preserves those limitations.

## Verified live example — 2026-11-25

Run 20261125T070128Z-bc0a6376: NVDA, 2026-01-09, all four analysts, one research and one risk round, no portfolio, request cap 30. Real configured model CS5351/DeepSeek-V4-Flash. Completed in 84 seconds, 20 dispatched requests, 88,116 input tokens, 13,125 output tokens, 101,241 total. Output check PASSED, rating Hold. Twelve stage records and final/evidence files were produced. Some external feeds remained unavailable. This single run is functional verification, not a controlled token-reduction experiment.

The original frontend and earlier demo were backed up under the project's ignored `.local-review/nocode-integration-backup/`. Original canonical reports and provenance are retained; the console HTML is a presentation copy without promotional logo/footer.

## Final local checks

Full offline suite: 2,003 passed, 2 skipped, 1 deselected, 100 subtests passed. Ruff passed. Bandit on demo/ found no medium/high issues. Frontend production build passed (bundle-size and Browserslist freshness warnings remain). Negative HTTP probes reject missing CSRF and unknown file IDs. Browser HTML preview and actual HTML download verified.
