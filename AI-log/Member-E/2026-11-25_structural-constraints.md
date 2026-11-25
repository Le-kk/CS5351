# Selected AI-use record — structural constraints

Date: 2026-11-25. Role: E. Task: E3 structural governance document.

## Original user request

> 请完成该文档

Context: the requested document is `docs/code-governance/structural-constraints.md`, consolidating B's module boundaries and the actual source layout into explicit restrictions and enforcement expectations.

## Public assistant reply

> 我会把现有边界整理成英文文档，逐项注明限制、检查方式和覆盖缺口，并补充 AI 使用日志。

## Work and verification summary

Created the structural-constraints document with the source baseline, module map, seven groups of restrictions, existing CI/test references, review expectations and explicit enforcement gaps. Added this selected AI-use record. No implementation, tests, workflow, dependency or branch-protection behavior was changed. Test-plan pre-approval remains paused. Full file-write payloads are omitted; no internal reasoning is included.

Verification: all 16 relative document links resolve; 90 document lines have no trailing whitespace. Existing targeted layering tests: 7 passed. The first pytest startup was blocked by the installed rerun plugin attempting a localhost socket bind; rerunning with only that plugin disabled (`-p no:rerunfailures`) passed, with a non-fatal cache-write permission warning. No project test or configuration was changed. This is a documentation consolidation, not an independent acceptance or architecture approval receipt.
