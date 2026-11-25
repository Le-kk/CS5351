# Submission contents and build instructions

Owner: team; assembled by Member E. Updated: 25 November 2026 (Asia/Hong_Kong).

This guide describes the tracked repository delivery, not the presenter's private working directory. Source inspection baseline: `fe9c3c6` (main after PR #50). This guide is added after that baseline; select a later committed revision containing this file when creating the final archive. Record that full revision alongside the archive. Contributor acceptance, course acceptance and a complete final archive are not inferred from this inventory.

## 1. Package inventory and authoritative paths

- `README.md`: project overview and quick start. `LICENSE` and `CHANGELOG.md`: retained upstream attribution/license and change history.
- `Report.md`, `Report.pdf`, `report-assets/`: integrated team report, rendered report and referenced figures/source metadata. The report includes five identities, agreed contributions and five reflections. The current PDF has 25 pages; original historical measurements retain their cited revisions.
- `AGENTS.md`, `Prompt.md`, `.agent/rules.md`, `.opencode/`: development entry instructions, human approval procedure, covenant, role rules and local permission configuration. These files are distinct from product prompts and GitHub merge checks.
- `architecture-blueprint.md`: canonical architecture blueprint. `docs/architecture/`: its pointer, contracts, invariants, ADRs, policies and the canonical `trace-matrix.md`.
- `docs/req/`: requirements registry, JSON schema, validator and requirement decisions. Schema validity does not mean the proposed registry has been adopted.
- `docs/code-governance/`, `docs/review-memo.md`, `docs/debt-register.md`, `docs/bug-diary.md`: constraints, dependency governance, review, known debt and defects.
- `src/tradingagents/`, `src/cli/`, `src/demo/`: application, interactive terminal entry and local presentation backend. `main.py` is a legacy graph entry, not the recommended complete product boundary.
- `test/offline/`, `test/live/`: deterministic regressions, opt-in live evaluation and harness checks. `scripts/ci/` and `.github/workflows/`: enforcement scripts and workflows. `scripts/run_role_agent.py` and `scripts/verify_role_permissions.py`: optional coding-agent permission tooling; not needed to run the product.
- `prompts/`: versioned snapshots of runtime instruction fragments. `assets/` and package assets support the existing application/documentation; the local presentation interface is not included.
- `AI-log/`, `docs/ai-use-log.yaml`: original-language selected records and structured event index. `transcripts/`: separately annotated D5 evidence and its completeness/privacy notes. Selected AI-use logs do not replace full required transcripts.
- `docs/verification/`, `docs/reviews/`: dated test plans, results and scoped evidence. `docs/submission/`: member writing, reflections, delivery checklist and this guide.
- `history/`: superseded material with provenance; not the current startup guide, acceptance contract or latest PASS evidence.
- `pyproject.toml`, `requirements.txt`, `.env.example`, `.env.enterprise.example`: packaging/dependency declarations and credential-free configuration templates. `Dockerfile` and `docker-compose.yml` are retained alternate deployment material; the Python installation below is the delivery procedure checked here, not a fresh Docker certification.

Root `tradingagents`, `cli`, `demo` and `tests` are compatibility symlinks to canonical paths. The legacy C-live test path and live conftest also use links. Preserve symlinks when extracting; do not create competing editable source copies. Use canonical paths for edits. Windows users need a symlink-capable checkout/extractor (or WSL); a flattened archive is not an equivalent layout.

## 2. Installation from a clean extraction

Use Python 3.12 for the reference installation and type-check configuration. CI also tests Python 3.11, 3.13 and 3.14. Internet access is needed to obtain dependencies. Run commands from the extracted project root, containing `pyproject.toml`.

```sh
python3.12 -m venv .venv
source .venv/bin/activate
python -m pip install -e '.[dev]'
python -m pip check
python -c "import tradingagents, cli.main, demo.console; print('imports OK')"
tradingagents --help
```

On Windows PowerShell, activate with `.venv\Scripts\Activate.ps1` instead of `source`. The `bedrock` extra is optional: install `'.[dev,bedrock]'` only when using that provider. A missing optional AWS integration can otherwise produce the documented optional test skip.

These are repeatable installation steps, not a claim of bit-for-bit dependency reproducibility: runtime dependencies include version ranges and no complete frozen environment is promised. For a delivery rerun, retain the Python/platform versions and `python -m pip freeze` output outside the source archive, after checking that it exposes no private package URLs. Exact model responses also depend on provider versions, live data and memory state.

An optional wheel build checks packaging without making model calls:

```sh
python -m pip wheel --no-deps --wheel-dir /tmp/cs5351-wheels .
```

The wheel is an installable application artifact; it is not the complete course submission, which also includes tests, reports, governance and evidence. Use an appropriate temporary directory instead of `/tmp` on Windows.

## 3. Configuration and startup

Start with the empty templates; enter credentials only in private local configuration or environment variables. Do not put real keys in this guide, source, transcripts, screenshots or a shell command that will be published. Use credentials only for the selected provider. An OpenAI-compatible relay additionally needs its approved endpoint and model identifiers. Relevant environment names include `OPENAI_API_KEY`, `TRADINGAGENTS_LLM_PROVIDER`, `TRADINGAGENTS_LLM_BACKEND_URL`, `TRADINGAGENTS_DEEP_THINK_LLM` and `TRADINGAGENTS_QUICK_THINK_LLM`; see the templates and `src/tradingagents/default_config.py` for supported overrides. Optional macro/filing integrations have their own documented configuration.

For the delivered terminal interface:

```sh
tradingagents
```

Follow the prompts to select the analysis configuration, choose a portfolio or no-portfolio mode, and confirm inputs before model execution. Use synthetic JSON portfolios for demonstrations; never package a real account. No-portfolio means holdings are unknown, while an explicitly supplied empty portfolio means a known flat book. Model execution and market-data access require reachable services and may incur charges. Running `main.py` can also call models; it is not an installation smoke test.

The optional presentation backend is included; its separately maintained frontend/build is deliberately excluded. CLI installation and offline testing do not require that frontend. If the presenter has the local build, use its actual absolute directory:

```sh
python -m demo.console --frontend-dir /absolute/path/to/local/build --compact-evidence-handoff --open
```

It binds to loopback `127.0.0.1`, normally port 8766. Use `--port 8767` if the default is occupied, or `--state-dir /private/local/run-state` to choose a private state directory. These paths are placeholders to replace, not archive contents. Starting the server does not start a paid analysis; explicit input confirmation is required. The compact-handoff option is enabled only by this flag or equivalent configuration; it is not a universal application default. See [backend instructions](../../src/demo/README.md).

## 4. Verification commands and interpretation

After installing the development extra, the following commands need no provider credentials and do not request a paid live replay:

```sh
python -m pytest -q test/offline
python -m pytest -q
python -m ruff check .
python -m mypy --config-file pyproject.toml
python scripts/ci/check_requirement_schema.py
python scripts/ci/check_workflow_permissions.py
python scripts/ci/check_security_scan.py
python scripts/ci/check_ai_log_updated.py --self-test
python scripts/ci/check_required_tests.py --self-test
python scripts/ci/check_dependencies.py --self-test
```

The first pytest command runs the offline subset; the second adds live-harness self-checks. The configured default excludes `integration` tests. Actual live semantic replay remains skipped unless explicitly enabled. Review counts, skips and deselections rather than equating a green command with execution of every possible test. Loopback HTTP/security tests require the environment to permit local socket binding.

At the PR #50 source snapshot, local full collection recorded **2,034 passed, 2 skipped, 1 deselected and 100 passed subtests**. The skips were optional AWS support and opt-in live semantic replay. All seven required hosted checks passed on that PR. These are dated results, not a promise that future dependency resolution, source changes or live services reproduce identical counts. The supplied report's earlier 1,976-test result belongs to its separately pinned inspected source.

Dependency self-tests test gate behavior; they do not run a vulnerability audit. Full installation consistency, vulnerability auditing and change-based dependency review run on the full route of `.github/workflows/ci.yml`. Pure document PRs instead validate document formats, links and applicable report/index integrity without installing application dependencies; mixed, protected and unknown changes run full checks, as do main/version pushes. See [document-only CI](../code-governance/document-only-ci.md). That job uses a disposable environment, audits installed dependencies and excludes this local project distribution from public-package lookup. Do not uninstall the project in the presenter's working environment to imitate CI. New-dependency and AI-log change checks also require Git base/head history, which a source archive without `.git` does not provide. Use a repository checkout/PR for those checks.

The required GitHub names are `required tests`, `ruff (strict, full repo)`, `dependency check`, `ai-log updated`, `requirements schema`, `type check` and `security checks`. Each fixed name verifies its applicable route; a successful document-only summary does not mean code tests or dependency audit ran. Test-plan pre-approval remains paused as a required merge check, and live semantic acceptance is not a required automatic gate. Do not describe either as passed simply because ordinary CI succeeded.

A paid replay is separate and must use an explicitly approved, configured cohort:

```sh
GOV004_LIVE=1 python -m pytest -q test/live/member_c_verification/test_gov004_live.py
```

Read [the verification package](../verification/README.md) and its cohort/evidence requirements first. A populated API key alone does not establish evaluation readiness or independent acceptance. Do not run this command as part of archive smoke testing.

## 5. Known limitations at delivery

- The system provides research, not executable orders or verified financial advice. Deterministic `PASSED` is not proof of arithmetic, factual accuracy, evidence completeness or investment suitability.
- Vendor/network failures, unavailable news/social/macro data, absent filings, ambiguous vendor row meanings and historical point-in-time constraints remain possible. Disclose unavailable or unverified inputs; do not turn unavailable data into observed absence.
- Token reductions are small-sample, configuration-specific measurements. Input/output/total usage, entry point, analysts, debate rounds, ticker/date, model/provider and memory state must match for comparisons. A call-count cap or per-request timeout is not a cumulative token or total-run deadline guarantee.
- Mypy covers selected boundary/contract modules, not every source file. Bandit coverage and explicit security/API/privacy/permission probes have stated limits; a clean result is not a general security proof or operating-system sandbox.
- Local role permissions require the documented launcher/tool setup. Configuration presence and historical synthetic probes do not establish every member's deployed permissions or current owner acceptance.
- Registry adoption, formal semantic acceptance, complete D5 collection and remaining architecture/integration decisions must be checked against the current records. Report integration does not silently close them. See [delivery checklist](delivery-checklist-2026-11-25.md), [debt register](../debt-register.md) and [trace matrix](../architecture/trace-matrix.md).

## 6. Secrets, private data and evidence

Include only empty/example credential templates and deliberately reviewed evidence. Exclude actual `.env`/enterprise configuration, provider tokens, session/authentication stores, real holdings/account files, private run state, raw private sharing databases, dependency caches, virtual environments and local backups. `.gitignore` helps with normal staging; it neither removes already tracked secrets nor makes copying the whole working directory safe.

Selected public logs and transcripts may have documented privacy redactions. Preserve their provenance and scope; do not invent missing messages, approvals or measurement evidence. Review tracked evidence for identifying information before final submission. If an actual credential has been published, revoke/rotate it and follow an explicit history-remediation process; deleting a working-copy file alone is insufficient.

## 7. Final archive procedure and acceptance checklist

Create the archive only after this guide and all intended delivery changes are committed and reviewed. Do not zip the whole working directory: it contains local-only interface files, private state and ignored material. Git archive includes committed files, including dot-directories and symlinks, but not `.git`, untracked files, ignored files or uncommitted edits.

From the final clean delivery checkout, use a POSIX shell:

```sh
git status --short
git rev-parse HEAD > /tmp/CS5351-delivery-revision.txt
git archive --format=tar.gz --prefix=CS5351/ --output=/tmp/CS5351-submission.tar.gz HEAD
tar -tzf /tmp/CS5351-submission.tar.gz > /tmp/CS5351-submission-files.txt
shasum -a 256 /tmp/CS5351-submission.tar.gz > /tmp/CS5351-submission.sha256
```

If `git status --short` lists intended edits, stop and commit/review them before archiving. Keep the revision, checksum and file inventory alongside the archive; the archive checksum cannot be embedded into itself. Equivalent Windows tools may be used only if they preserve the linked layout. For a different required archive format, recheck the extracted symlinks and contents rather than assuming equivalence.

Before hand-in, the team must:

1. Confirm the full delivery revision, archive SHA-256 and inventory correspond to the same committed tree. Verify that this guide, `Report.md`, `Report.pdf`, figure assets, `src/`, `test/`, governance, logs and available transcripts are included.
2. Confirm that actual secrets, real portfolios, `.local-review/`, `.venv/`, caches, `src/frontend/`, `src/demo/static/` and `history/frontend/` are absent. Empty `.env.example` and `.env.enterprise.example` templates are intentional. Do not mistake synthetic portfolio fixtures or reviewed evidence for real account inputs.
3. Extract into a new directory, preserve symlinks, and perform the installation/import/help commands and offline/full default verification above. Record Python/platform versions, outcomes and declared skips. Do not reuse a private `.env` or start paid replay during this smoke check.
4. Reconcile the [delivery checklist](delivery-checklist-2026-11-25.md) with the actual files. Confirm member evidence, video delivery and owner sign-offs separately; the demonstration video and local frontend are not supplied by this repository archive.
5. Open the packaged PDF and check figure readability, five names/IDs, agreed contribution proportions and individual reflections. Historical results must retain their source/configuration qualifiers.

This document provides the build and packaging procedure. A final frozen submission archive and its fresh-extraction acceptance record are still to be produced from the team's chosen delivery revision; they are not fabricated by writing this guide.
