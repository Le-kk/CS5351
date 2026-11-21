# Fresh live evidence —21 November2026

Current-source execution finished: 10/10 selected cases;15/15 retained started attempts completed (five earlier same-provider runs outside the selected cohort). No start or completed historical attempt was discarded. The source snapshot is117 files; `source-inventory.json` pins the dirty working-tree content.

**Human formal acceptance: PENDING. Historical F8 PASS: UNVERIFIED.** `gov004_scores.json` is an intentionally unfilled human-review template (null scores), not an accepted score sheet. `ai-review-proposed-scores.json` contains28 AI-proposed cells with exact report citations/rationales. Its mechanical scorer result is PASS, but this is NOT Member C acceptance. The narrow rubric does NOT test general financial arithmetic: final reports contain numeric errors and a Fundamentals fiscal-period contradiction retained for review.

Start with `review-facts.json`, `cohort.json`, `gov004_starts.json` and `rescore-results.json`. Per-attempt JSON plus trial aggregates are durability mirrors; the scorer deduplicates identical records. `prior-cohort.json`/`prior-source-inventory.json` explain the five prior attempts, and reports/manifests retain original bytes. `integrity.json` pins package files; integrity is not semantic approval.

The package contains Markdown/HTML reports, immutable manifests, event logs and captured prompt digests/counts/marker hits. It excludes raw state dumps, memory, vendor caches, credentials and unredacted native agent exports. Prompt capture establishes exposure to the selected synthetic news challenge; it does not contain full raw prompts. Diagnostics under `diagnostics/` are separate targeted L1/L2 execution records, including observed failures before clarification. They are not mixed into the fixed-profile 15-attempt denominator. Driver copies document the synthetic fixtures; their original private output paths need adjustment to reproduce elsewhere.

Recheck from the repository using Python in the project virtual environment:

```bash
GOV004_EVIDENCE_DIR="$PWD/docs/reviews/evidence/live-verification-2026-11-21" .venv/bin/python tests/member_c_verification/live/score_gov004.py
# Expected: PENDING until independent human scoring is supplied.
GOV004_EVIDENCE_DIR="$PWD/docs/reviews/evidence/live-verification-2026-11-21" .venv/bin/python tests/member_c_verification/live/score_gov004.py docs/reviews/evidence/live-verification-2026-11-21/ai-review-proposed-scores.json
# Mechanical AI-proposal check only. Does not establish human approval.
```

Member C should inspect the full narratives and captured exposure, then create a separate approved score sheet with a real reviewer identity, chronology/approval reference and all 28 applicable 0/1 cells. Keep this original template and AI proposal as provenance. No numeric validator was implemented; see the [numeric extension proposal](../../../architecture/proposals/numeric-validation-extension-plan-2026-11-21.md) and [repair review](../../remediation-r1-r5-2026-11-21.md).
