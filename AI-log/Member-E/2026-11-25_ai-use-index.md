# Selected AI-use record — structured team event index

Date: 2026-11-25. Role: E. Task: E9.

## Original user request

> 现在请完成E9，把各成员AI日志里记录的对于项目的重要更新、测量等事件写入，记住不要放原始的材料，而是描述：**E9 — `docs/ai-use-log.yaml` — Course-required repository artifact; missing.\*\***
>   Build a structured index from the available original-language `AI-log/` records, linking important tasks, interventions, changes and verification evidence. Collect outstanding member records. This is mainly aggregation/formatting, but missing source conversations cannot be invented.

## Public assistant reply

> 我会汇总各成员 AI 日志中的重要更新、测量、修复和验证事件，写成结构化 YAML 索引，只保留事件描述和来源链接。同时列出缺失的记录，不补造对话或证据。

## Work summary

Created the English structured event index from the available A–E folder inventory: 35 substantive Markdown records and four provenance JSON indexes, covering 21 important events. The YAML contains descriptions and source/evidence references rather than copied conversation turns, tool payloads or patches. Source hashes identify the snapshot; source-reported outcomes remain attributed reports, not newly executed acceptance tests. Added discovery guidance to the AI-log README. This E9 task's own record is excluded from its source snapshot to avoid self-referential hashes.

A's folder contains only an empty README. Outstanding-record items cover A's original records, B's supervising-decision coverage, C's partial exports/historical acceptance evidence, D's local-only measurement harnesses/configuration, E's selected-extract/raw-evidence limits and all contributors' confirmation. No contributor was contacted or approved by this aggregation task, and missing conversations were not reconstructed.

Important distinctions retained: historical GOV-004 PASS is disputed by later review; D's baseline/after/attribution and E's optimization are separate populations; input/output/total units and incomplete attempts remain explicit; successive 50/62/69 permission snapshots are not summed. Earlier cumulative repair counts are not counted twice. No original source record, application code, permission configuration, workflow or remote setting was changed. Full write payloads/internal reasoning are omitted.

## Observed validation

YAML parsed with duplicate-key rejection. All 39 source paths/hashes, 21 unique event IDs/source references, 48 artifact references and six outstanding-record items checked successfully. Baseline/optimized mean arithmetic was checked without treating cross-series measurements as a controlled experiment. README links and YAML whitespace checked. No live model, product regression or independent semantic acceptance was run for this aggregation-only change.

Current file lengths (not added-line counts):

- `docs/ai-use-log.yaml`: 937 lines.
- `AI-log/README.md`: 15 lines.

## Delivery status addendum — 2026-11-25

The original 39-source/21-event validation describes the earlier inventory only. The delivery cleanup refreshes A/C sources and newer E events against main 761918e; current counts and hashes are in docs/ai-use-log.yaml. No historical validation is relabelled as current.
