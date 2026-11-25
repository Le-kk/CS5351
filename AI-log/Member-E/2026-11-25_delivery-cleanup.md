# Delivery inventory cleanup — 2026-11-25

Selected source excerpts; internal reasoning, full code/write and tool payloads omitted.

## User request (verbatim)

> 请按上述建议进行更新、提交或删除

## Assistant public reply (verbatim)

> 我会先更新 E1、E9 和相关日志，提交有用的交付材料；旧清单、回复和重复测试会先备份到本地归档，再从工作目录移出。只删除 `.DS_Store`，并检查提交中不含过时材料或私密数据。

## Work and limits

Baseline main 761918e, after PR37 repairs and PR38 requirement text. Backed up all
21 substantive untracked files, with SHA-256 manifest, in ignored local storage.
Archived nine obsolete/redundant documents or developer tests; deleted seven
untracked .DS_Store files. No tracked source or existing test was deleted.
Refreshed E1 assessments/registry hashes and E9 source inventory/events, including
A's six records, C's actual filenames and requirement-verification record, current
B hash and newer E work. Preserved original log excerpts and appended dated
status notes; did not rewrite historical tests or invent signatures/adoption.

Published historical token reports with a primary-report/summary relationship and
JSON delivery metadata. Original numeric/configuration measurement values remain
unchanged; no new model measurement or quality/budget acceptance is claimed.
Archived H2/H4 test files are not added back into the delivery or CI selection.
Older reply proposals and gap lists are not current governance instructions.

Validation is document-only: exact active/withdrawn requirement coverage, local
links, source hashes, event/source identity, declared available artifacts, token
arithmetic and unchanged historical measurement values. The concrete integrity
summary accompanies the delivery. No product code, workflow, dependencies or
branch-protection rules changed; no model replay or independent acceptance was
performed. GitHub submission is reported separately after actual checks.

Integrity summary: `docs/verification/delivery-cleanup-2026-11-25.json`.
