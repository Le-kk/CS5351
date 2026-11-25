# English project demo

A local browser presentation of the **current version only**. Earlier behavior
is explained orally in the built-in presenter notes; no old application version
is launched. No production CLI, run contract, workflow or dependencies are changed.

## Start

From the repository root, using an environment with the project's declared
runtime dependencies installed:

```sh
python -m demo --open
```

Open **http://127.0.0.1:8765**. To use another port:

```sh
python -m demo --port 8766 --open
```

On macOS, `Start Demo.command` in this folder is a double-click launcher. It
prefers the repository's `.venv` when present, otherwise `python3`. It does not
install packages or edit model settings. If dependencies are missing, activate
your existing project environment or install the declared project dependencies.
A running server keeps its run state in memory; restarting creates a new session.
Stop the server with Ctrl+C in its terminal.

## Modes: what is real, and what is scripted?

**Scripted walkthrough is the default.** Analyst outputs and SDK response usage
are synthetic. It exercises the real `PortfolioInputService`, immutable
`RunContext`, explicit confirmation, `run_analysis_api`, output checker,
finalizer, redactor and Markdown/HTML publication. The call-limit scenario uses
the actual `RunBudgetController` and `BudgetTransport` underneath an actual SDK
client, whose only transport is a local `MockTransport`. No network/model/vendor
request is made. Eight scripted stages are a presentation fixture, not the
production graph's call count or a semantic-quality experiment.

**Live analysis** is a deliberate opt-in:

```sh
python -m demo --allow-live --open
```

Select “Live analysis” in the UI, review inputs and check the consent box. This
uses the actual graph and configured providers; API/vendor costs may apply and
portfolio facts can reach model providers. Existing `.env`/exported
`TRADINGAGENTS_*` model/provider configuration is used privately, never returned
to the browser. Do not paste credentials into the demo. Both model tiers must
use supported `deepseek`/`openai_compatible` clients for the current call-cap
profile. Without a call cap, normal supported provider behavior is retained.
Injected review/model/data failures are available only in scripted mode.

Each run gets isolated results and memory under ignored `.local-review/demo/`;
cache is isolated to the demo session. Live rounds are fixed at one research and
one risk round, with four analysts, English output and concise context enabled.
Checkpoint resume is disabled. This is the presentation profile, not a claim of
formal semantic acceptance. Live usage is observed provider usage; missing usage
is not zero. No live cancellation or hard wall-time ceiling is introduced.

## Suggested five-minute presentation

1. **Prepare inputs:** switch between no portfolio (unknown), explicit empty
   portfolio (known flat), and a synthetic position (cash unknown). Inspect JSON.
2. **Reject an input:** “Try invalid input” submits valid JSON missing quantity;
   the real schema check rejects it before dispatch. A custom JSON file may also
   be selected; use synthetic data, up to 32 KB.
3. **Freeze and confirm:** inspect mode/date/filename/fingerprint. A run cannot
   start until consent. Cancel keeps dispatch count zero. Changing controls
   invalidates the pending confirmation; new inputs must be reviewed again.
4. **Run:** observe labelled scripted/provider usage and stage activity. The
   report tab embeds the actual published HTML. Evidence shows safe run fields;
   absolute machine paths are omitted from the UI. Download actual Markdown or
   manifest JSON when needed. PASSED is Q1-Q4 only, not factual correctness.
5. **Show guardrails:** choose “Stop at the call limit” (default limit 2), then
   observe `INCOMPLETE / BUDGET`, no final rating, `NOT_RUN`, and actual counters.
   A limit of 0 dispatches no requests; 8 permits the eight-stage fixture to finish.
   Choose “Unreadable rating” to see `REVIEW / NEEDS_REVIEW`, or a model/core-data
   failure to see typed incomplete outcomes. Model prose cannot set the verdict.
6. **Explain efficiency:** use the historical chart separately from this run.
   It reads checked-in evidence: one same-day control of 160,826 total tokens,
   three optimized runs averaging 104,459, a reduction of 35.05%. NVDA/date/model
   and limitations are visible. Historical series are not new live measurements;
   no general reduction or unchanged-quality guarantee is made. A call cap is
   not a token ceiling. Token reduction is not formal semantic acceptance.

## Local boundaries

The server binds only to `127.0.0.1`, validates Host/Origin, requires a session
CSRF token and JSON for mutations, limits request/file size, and serves only
fixed assets and registered run artifacts. No arbitrary filesystem browser,
remote asset loader or credential endpoint exists. The report iframe is sandboxed.
The generated complete report keeps its production CSP and trusted inline CSS.
These controls are for a local presentation adapter, not public hosting or a
replacement for OS/user isolation. Do not expose it with a public tunnel.

Tests: `python -m pytest -q tests/member_d_verification/test_presentation_demo.py`.
The HTTP probe permits only loopback while retaining the suite's external-network
ban. Other developer probes use exclusively mocked SDK transport. Existing C
acceptance tests and production checks are unchanged.
