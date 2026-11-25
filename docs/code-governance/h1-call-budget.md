# H1 — per-run model-request budget

Date: 2026-11-25. Baseline: main `345d983` plus the already locally verified H4 guard. This change implements the call-budget slice of B's interface contract §15, without the full R1–R8 checker or cumulative token admission.

## Behavior and activation

Default behavior remains unbudgeted. Set `config["call_cap"]` to an explicit non-negative integer when calling `run_analysis_api`, or set `TRADINGAGENTS_CALL_CAP` for the standard configuration/CLI. A value of 0 allows no model requests; `None` disables the feature. The architecture's value 8 is a test/example value, not a measured production default.

```sh
TRADINGAGENTS_CALL_CAP=8 tradingagents
```

Choose supported model tiers in the CLI: both must use `deepseek` or `openai_compatible`. Other providers are rejected before model dispatch in this first profile. Direct legacy graph construction with an enabled cap is refused; use the shared application entry. No API signature, exported symbol or RunResult field changes are required. The separate H4 result guard is preserved.

Both tiers, tool-bound calls, structured-output calls, free-text fallback and memory reflection share one controller. A granted reservation is single-use and bound to its controller; invalidating an unsent reservation never returns capacity. Grants/denials are atomic across threads. The controller is bound through a run-local ContextVar during construction; models retain the metered transport. The controller is not placed in copied configuration, frozen portfolio input or checkpoint state.

Enforcement is at the actual SDK HTTP transport, below bound tools/parsers. SDK retries and transport connect retries are disabled. A separate application retry consumes another slot; a refused attempt sends nothing. Reaching the exact cap after the last needed call is a normal completion. A refused required call produces `INCOMPLETE/BUDGET`, null rating, `NOT_RUN` and empty findings; fallback/memory handlers preserve the admission exception and public finalization also checks the authoritative denial count.

The controller seals before publishing its final counters and waits for issued response streams to close. No new wall-clock cancellation guarantee is introduced. Unsent grants are invalidated at seal without refund. Streams/clients are cleaned up after the graph returns. Independent runs have independent counters. A fresh API invocation gets a fresh budget; this does not decide unresolved checkpoint/resume identity policy.

## Supported scope and limits

The tested profile uses synchronous SDK requests through the in-tree tier factory for `deepseek` and `openai_compatible`. Async model dispatch is explicitly rejected before network access; it is not silently unmetered. HTTP redirects are not followed in this profile. Gateway-internal retries and arbitrary user-injected code/custom clients bypassing the in-tree factory are outside the client-side guarantee. Such custom integration requires separate verification; merely passing a cap does not sandbox arbitrary Python/network code.

The transport family is selected from the SDK's public default client (httpx or httpx2); unsupported client families fail closed. Native tests exercise the installed OpenAI SDK 3.16.2 and LangChain OpenAI client against synthetic HTTP responses, including both supported provider classes. A separate clean declared-dependency environment also passed with OpenAI SDK 3.59.0, LangChain OpenAI 1.8.5 and httpx2 2.16.2. Other SDK versions require revalidation. No real model, vendor replay or human semantic scoring is claimed by these tests.

This is a **model request-count cap**, not a token or elapsed-time cap. It does not set a TOKEN_BUDGET, introduce token upper-bound estimation or implement the proposed cumulative token ledger. Financial quality, H2/H3/H5 and final requirement adoption remain separate.

## Artifacts and failure precedence

Disabled runs retain legacy manifest `schema_version: "1"` with no budget/rule-version fields. Enabled runs write `schema_version: 2`, `check_rules_version: 1` (legacy Q1–Q4), and `run_budget` containing exactly `call_cap`, `granted`, `dispatched`, `invalidated`, `denied`. Effective configuration records the actual cap. Markdown/HTML body and a fixed-field budget event expose safe counters, not prompts, credentials or raw portfolio input.

Critical report/manifest publication failure remains `PERSISTENCE_ERROR`; the budget event/diagnostic retains the secondary call-limit cause. A failed publication is not claimed durable. Existing terminal-event rules remain unchanged.

The scorer explicitly recognizes the new budget-only manifest and six stop reasons. Unknown versions, inconsistent counters, mismatched cap and budget fields in legacy records are rejected. A formal budgeted cohort must explicitly freeze the same `call_cap`, and its evidence model configuration must retain that cap; absent/mismatched controls fail eligibility. Existing unbudgeted cohorts remain legacy. This reader compatibility is not a new semantic rubric or adoption of a production cap. Do not activate a budgeted formal replay without preparing its declared profile and evidence accordingly.

The source-based `prompt_hash` can change because the structured helper source changed, even though financial prompt instructions were not rewritten. Use fresh source/hash controls for a new replay; do not relabel historical evidence as this version.

## Verification and review

Run the developer probes and existing regressions in the declared development environment:

```sh
python -m pytest -q tests/member_d_verification/test_h1_call_budget.py
python -m pytest -q
python -m ruff check .
python -m mypy --config-file pyproject.toml
python scripts/ci/check_security_scan.py
```

Tests include valid/denied calls, last-slot concurrency, independent concurrent API runs, no refund/reuse/cross-run tickets, stream completion, native plain/tools/structured routes, actual reflection, suppressed SDK retries under HTTP 500, memory/fallback propagation, persistence precedence, default graph construction, explicit async/provider rejection, legacy compatibility and synthetic scorer positive/negative evidence. They are developer regressions, not C's independent acceptance. The default full suite still excludes integration and opt-in paid live replay; optional Bedrock may be skipped.

New files increase the configured type scope from 14 to 15 files and application scan inventory from 105 to 107. Earlier counts are dated baselines. See [verification record](../verification/h1-call-budget-2026-11-25.json) and the [developer tests](../../tests/member_d_verification/test_h1_call_budget.py). CI settings, branch protection, paused test pre-approval and unrelated application mechanisms are unchanged.

Sources: B's [interface contracts](../architecture/interface-contracts.md) §15/§16.7; public [HTTPX transport documentation](https://www.python-httpx.org/advanced/transports/) and [SDK retry configuration](https://github.com/openai/openai-python/blob/main/README.md#retries). Runtime behavior is verified against installed SDKs rather than inferred from filenames or wrappers.
