# CS5351 Portfolio-Aware Research System

A course extension of [TradingAgents](https://github.com/TauricResearch/TradingAgents), baseline v0.7.1. Team repository: [kelepawuqiusi/CS5351](https://github.com/kelepawuqiusi/CS5351). Upstream attribution and the original license are preserved; upstream work is not claimed as a team contribution.

The system produces research, not executable orders. Terminal and browser adapters enter the shared `run_analysis_api` boundary after explicit input confirmation. An immutable run context distinguishes missing portfolio information from a supplied empty account. The graph retains the existing analyst, research, trader and risk stages; deterministic checks and publication own the final run outcome and evidence. PASSED does not certify financial accuracy.

Recent local additions include an English real-model console, an opt-in compact intermediate evidence format, request timeouts and refresh recovery. A fixed NVDA case measured a 26.91% reduction against its same-day control; this is a small-sample observation, not an enforced token ceiling or general quality guarantee. See the linked verification report.

## Course deliverables and file organization

- `AGENTS.md`, `architecture-blueprint.md`, `Prompt.md`: coding-agent entry, canonical blueprint and static human-gated launch prompt.
- `Report.md`: single process-report assembly draft, with source-attributed member material; unresolved identities/contributions and missing member evidence are explicitly marked.
- `docs/req/`: requirement registry, JSON schema and validator. The registry's proposed status is preserved.
- `docs/architecture/`: ADRs, invariants, trace matrix, memory, permissions, runtime policies and evaluations. The blueprint pointer refers to the one root canonical blueprint.
- `docs/code-governance/`, `.opencode/`, `.agent/`: coding/verification constraints, scoped local permissions and covenant.
- `docs/review-memo.md`, `docs/debt-register.md`, `docs/bug-diary.md`: review, debt and defect records.
- `docs/ai-use-log.yaml` and `AI-log/`: structured task index and selected original-language conversations. They do not replace D5 full annotated transcripts.
- `src/tradingagents/`, `src/cli/`, `src/demo/`, `src/frontend/`: canonical application, terminal adapter, local demo backend and React frontend.
- `test/offline/`: deterministic tests and independent/developer verification. `test/live/`: opt-in live evaluation and its harness self-checks.
- `prompts/`: versioned snapshots of actual intermediate instruction fragments, not a replacement runtime loader.
- `transcripts/`: annotated D5 submission evidence. Collection is incomplete; see its index.
- `docs/submission/`: member reports/reflections and the delivery checklist.
- `history/`: superseded entry documents/export artifacts, with original paths and hashes. Dated review evidence stays at its cited location.

The root `tradingagents`, `cli`, `demo` and `tests` paths are compatibility symlinks to the canonical directories. The old C-live test path is also an alias excluded from recursive offline collection. There is one physical copy of each source/test. New edits should use `src/` and `test/`. Windows checkouts must support Git symlinks; otherwise use canonical installed package/test paths. Do not flatten links into competing editable source copies.

## Install and run

Python 3.11–3.14:

```sh
python -m venv .venv
source .venv/bin/activate
python -m pip install -e '.[dev]'
tradingagents
```

Configure provider credentials privately through the existing backend environment. Never commit `.env` or real holdings. The legacy root `main.py` can invoke real models; it is not an import smoke test.

Browser demo (Node 22.12+ or 24 recommended for its current build tools):

```sh
cd src/frontend
npm ci --ignore-scripts
npm run build
cd ../..
python -m demo.console --compact-evidence-handoff --open
```

Open http://127.0.0.1:8766. The service binds loopback only. Validate and confirm before any model execution. Refreshing does not cancel a run; its ID is remembered in that browser tab. Interrupted runs remain in local history with partial usage. See [demo deployment](src/demo/README.md).

## Tests and gates

```sh
# Deterministic offline suite; no live provider calls
python -m pytest -q test/offline
# Normal full collection: offline plus live-harness self-checks; paid replay remains skipped
python -m pytest -q
# Explicit paid semantic replay; configure and approve the cohort first
GOV004_LIVE=1 python -m pytest -q test/live/member_c_verification/test_gov004_live.py
python -m ruff check .
python -m mypy --config-file pyproject.toml
python scripts/ci/check_requirement_schema.py
python scripts/ci/check_workflow_permissions.py
python scripts/ci/check_security_scan.py
```

Seven existing required check names are preserved: `required tests`, `ruff (strict, full repo)`, `dependency check`, `ai-log updated`, `requirements schema`, `type check`, `security checks`. The regression summary also requires frontend build and high/critical npm audit. Dependency checks fail closed and use only documented, unexpired exceptions. AI-log checks cover canonical source/test paths and legacy important paths; log format is not certified. Type coverage remains scoped; security scanning now includes the demo. Contract tests remain in pytest. Test pre-approval is still paused as a required check; live semantic acceptance is not made mandatory by this reorganization. Workflow code and successful runs do not by themselves prove branch protection settings.

## Verification and remaining delivery work

See [delivery checklist](docs/submission/delivery-checklist-2026-11-25.md), [verification package](docs/verification/README.md), [token experiment](docs/verification/compact-evidence-handoff-2026-11-25.md), and [trace matrix](docs/architecture/trace-matrix.md). History, proposed interfaces and developer test passes are not owner adoption or independent acceptance. No missing raw conversation, approval, contribution percentage or semantic result is fabricated.
