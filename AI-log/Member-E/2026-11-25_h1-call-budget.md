# Selected AI-use record — H1 call-budget implementation

Date: 2026-11-25. Role context: E coordination; user-authorized implementation and developer verification.

## Original user request

> 请尝试实施H1，不要修改不相关文件，如果修复失败请恢复原来的版本

## Public assistant reply

> 我会先核对 B 的预算控制设计和当前模型调用入口，在独立工作目录里实施 H1，保留本地 H4 等改动。修复会验证预算耗尽后停止新调用并返回 `BUDGET`；如果无法通过验证，就不将 H1 改动带回项目。

## Changes and interventions

Implemented an opt-in per-run call admission controller, single-use non-refunded grants and transport-level metering shared by both model tiers. Added explicit retry/unsupported-route handling, budget exception propagation, six-reason classification and budget-only manifest/reader compatibility. Kept default behavior legacy/unbudgeted and preserved H4. Added developer probes and a scope/activation/limits guide. No production budget was guessed; example cap 8 is a fixture/configuration choice. No cumulative token or time budget, H2/H3/H5 repair, workflow or dependency change is claimed.

Work was isolated from the primary checkout. Early probes exposed configuration deep-copy incompatibility with lock objects and response-stream cleanup for already-consumed synthetic responses; the implementation was corrected to use run-local binding and proper completion handling. Initial broad regression without loopback capability had seven authentication fixture failures; they were not skipped or weakened, and the final run used the authorized loopback-capable validation environment. Synthetic scorer tests verified explicit frozen-cap controls rather than accepting new-profile evidence silently.

The default graph and real SDK plain/tool/structured/reflection paths use synthetic HTTP transport responses, not paid model calls. The tested provider profile is synchronous deepseek/openai_compatible; unsupported async/providers reject before sending. Native SDK hidden retries are disabled. Gateway-internal retries, unrestricted custom integrations, token/time ceilings and independent C acceptance remain outside this verification.

Full code/write payloads and internal reasoning are omitted. Final file scope, source hashes and observed test outcomes are retained in the associated verification JSON. No user files are rolled back merely to make a test pass; unrelated primary-checkout changes remain preserved. No commit/push/PR update is made by this task.

## Final observed verification

37 H1 developer probes passed. Full default regression passed in both the existing tools environment and a fresh declared-dependency installation: 1,884 passed, two existing skips, one integration deselection and 100 passing subtests. Clean `pip check`, full-repository Ruff, mypy (15 files) and Bandit (107 application files, zero medium/high) passed. Clean native versions include OpenAI 3.59.0/LangChain OpenAI 1.8.5/httpx2 2.16.2; the existing environment used 3.16.2/1.6.3/2.13.0. The clean check was necessary because several shared-environment packages were below declared minima; the shared environment and project dependency declarations were not upgraded.

H1 scope is nine existing source/scorer files, three new implementation/test files, this log, one implementation guide and one verification JSON. The result-file baseline includes the previously verified H4 guard. Other local E9/handoff documents and original member logs remain outside scope. Source hashes are recorded; no raw provider payload, secret, full patch or invented human score is included.
