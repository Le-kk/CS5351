# Self-approval and automatic PR review records

## Two separate stages

1. Before product implementation: an authorized member may approve their own test plan using `/approve-tests <full plan SHA>`. Timing, scope, plan/test fingerprints and the baseline roster still apply. Receipt schema 2 records the PR author and `review_kind: self_review` or `peer_review` accurately. Self-approval does not retroactively approve code already written. Governance changes use `/approve-governance <full SHA>` from the confirmed governance roster; the PR author may issue it when the explicit governance self-review flag is enabled.
2. After implementation and successful CI: the PR author posts `/self-review <full current SHA>`. The `PR self-review records` workflow collects facts and generates `docs/review-memo.md` plus `review-receipt.json` as a downloadable Actions artifact. These are self-review records, not native GitHub approving Reviews.

Example with optional human judgments (plain JSON after the first line):

```text
/self-review <full current 40-character SHA>
{
  "requirements": "I checked the behavior against the listed acceptance criteria.",
  "architecture": "I checked the changed boundaries against the referenced ADR.",
  "code_and_tests": "I inspected the normal, boundary and negative cases.",
  "security": "I checked the relevant secret and input boundaries.",
  "efficiency": "I reviewed the measured costs; remaining limitations are recorded.",
  "verdict": "APPROVE"
}
```

Write only judgments actually made. Optional fields may be omitted; omitted assessments are explicitly reported as not assessed. The command alone means a self-declared APPROVE request, not automatic certification of requirements, architecture or quality. If any of the five required checks is missing, unfinished, skipped, failed or bound to another SHA, the generated verdict is CHANGES REQUIRED, not APPROVE. Human-requested REJECT/CHANGES REQUIRED remains visible.

## Automatically collected information

- Requirement references found in the PR description and changed test plans; their presence does not establish registry acceptance or implementation completeness.
- Changed architecture files, code/test file inventory and added/deleted line counts.
- Required check names, results, links and start/completion timestamps for the exact reviewed SHA.
- Reviewer identity, PR author, comment/time, reviewed revision and receipt workflow run.
- Human-supplied judgments separately from collected facts. Application latency, model quality, token usage and cost are not inferred from CI durations.

## File retention and merge limitations

Download the artifact and retain its `docs/review-memo.md` and JSON receipt in the delivery evidence. The workflow deliberately has read-only repository permissions: it does not directly commit to protected main or create a fake peer approval. Automatic file generation is implemented here; automatic merging/archiving into main is not. Use the repository's normal review process when archiving records. A final submission should consolidate per-PR memos rather than overwrite earlier evidence.

The user requested zero mandatory native GitHub approving Reviews while preserving PRs and required CI. Once the repository setting is applied, any current collaborator with write permission can merge an eligible PR, including their own. This removes the independent-review guarantee; self-review is recorded as such, not disguised as peer review. A record covers its source SHA; a later source change needs a new self-review. No statement here treats self-review as independent verification or claims that it satisfies every course requirement by itself.

Only a new comment by a real, roster-authorized PR author on an open main-targeting PR is accepted. Bots, stale SHAs, other users' commands and incomplete inventories are rejected. The workflow parses metadata only and never executes PR code or calls a model.
