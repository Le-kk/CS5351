# Document-only PR routing

Implemented 25 November 2026. The seven branch-protection check names remain unchanged. No application behavior, live semantic gate or paused prior-approval policy is changed.

## Routing

`ci_scope.py` reads the complete Git diff from the merge base to the PR head; it does not rely on a truncated API file list. A PR uses the document route only when every changed file is explicitly allowed. Renames are inspected as deletion plus addition, including the original path. Empty/unknown changes, executable files, symlinks and submodules do not qualify. Classification failure blocks summaries; it does not silently approve a skip. Pushes to main/version branches continue to run full CI, including documentation-only merges.

Allowed document changes are non-executable regular Markdown/text at the root or under docs, AI-log, transcripts and history; document media under docs/report-assets; JSON figure/evidence metadata under report-assets; root Report.pdf; and the structured docs/ai-use-log.yaml index. Root requirements.txt is explicitly protected. Other JSON/YAML is conservatively treated as full CI.

Always full: src, test and legacy application/test aliases, scripts, prompts, workflows/.github, .opencode, .agent, AGENTS.md, Prompt.md, docs/req and docs/code-governance, dependency declarations and unknown files. A README change mixed with any of these is a full PR. Governance/requirement Markdown is deliberately protected even though its extension is textual.

## Checks on document PRs

The classify/documents/summary jobs use the hosted Ubuntu runner's existing Python standard library and Ruby standard-library safe YAML parser. There is no package-install command, application import, provider call or pytest execution on this route. A missing parser or execution error fails validation. Full code PRs retain the existing installations, Python-version matrix, clean install, Ruff, type, schema, dependency, security and log checks.

Document validation checks changed UTF-8 text, NUL/conflict markers, balanced Markdown fences, local link/reference targets, JSON/SVG parsing and PDF signature/trailer. Deleting/renaming documents also checks existing tracked Markdown for links to the removed paths, without failing on unrelated historical broken links. External links are syntax-checked only; no remote link requests or heading-fragment checks are claimed. Binary image rendering, complete PDF layout and scientific/requirement meaning still need human review.

The root Markdown/PDF report must be updated together, and the PDF hash must match report-assets/integration-verification.json. An AI-log/index change validates safe YAML structure, source paths and source hashes; newly added selected member records must be indexed. This checks integrity, not truthfulness, completeness or course acceptance of the logged conversation.

## Fixed names and intentional skips

The workers have separate names; their results feed seven always-running summaries with the existing required names: required tests; ruff (strict, full repo); dependency check; ai-log updated; requirements schema; type check; security checks.

On a full run, each summary requires its actual upstream workers to succeed. Failure, cancellation, skip, absent result or failed classification is rejected. On a document PR, every summary requires successful classification, successful document validation, and exactly skipped results for every full-only worker. An unexpected success/failure/cancellation/missing worker result is rejected. Thus the required name reports that its applicable route was verified; it does not falsely claim pytest, Ruff, audit or live replay executed on a document PR. Workflow-level paths-ignore is not used, so required names do not disappear just because paths changed.

This uses GitHub's documented [job conditions and needs behavior](https://docs.github.com/en/actions/how-tos/write-workflows/choose-when-workflows-run/control-jobs-with-conditions) and [always-running dependent jobs](https://docs.github.com/en/actions/how-tos/write-workflows/choose-what-workflows-do/use-jobs). Branch protection does not need new names. As before, an authorized edit to the workflow itself is not made tamper-proof merely by storing it in the repository.

## Verification

```sh
python -m pytest -q test/offline/member_d_verification/test_docs_ci.py
python -m ruff check .
python scripts/ci/check_workflow_permissions.py
```

The independent negative cases cover mixed/protected files, code-to-document renames, file modes, malformed classifier/summary input, failed or absent document checks, unapproved worker skips, broken local links, document deletion, malformed text/JSON/SVG/PDF, mismatched report pairs and stale/invalid AI-use indexes. The current E14 PR diff was also replayed locally using the system Python with no application dependency installation: docs classification and document validation passed. A fresh hosted document-only PR remains the proof of actual GitHub skip/report behavior after this workflow is merged.
