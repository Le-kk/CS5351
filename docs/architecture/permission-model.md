# Permission Model (Member B design)

Status: architecture draft (revised 2026-11-12 per review B3-06; implementation-aligned 2026-11-24; governance status corrected to baseline `2efbf0f`). Describes **application roles during a run** and **per-coding-agent-role file rights**, kept separate. E implements enforcement. The OpenCode permission package (`AGENTS.md`, `.opencode/permissions.jsonc`, `.agent/`) is **still absent**, so **OpenCode per-role permission enforcement is not installed** — separate from the CI checks below. **Requirements schema gate (implemented, verified):** a `requirements schema` job exists in `.github/workflows/ci.yml` running `scripts/ci/check_requirement_schema.py` (wrapping A's validator) and `tests/member_d_verification/test_requirement_schema_gate.py`; it was verified locally/hosted, and E **reports** it is a required main check (strict protection retained). The exact required-check setting is **E-reported** — this session could not independently read the administrative endpoint (HTTP 401). **Paused approval enforcement (separate):** the `test approval` tooling exists but is **not** a required check; PR 16 merged with a failed approval check. See `risk-list.md` R-GOV.

Source: `SEL-TA-GOV-006` (B permission design; E enforcement). Ownership follows the team allocation recorded in `docs/architecture/evaluation-logbook.md`; the previously cited `docs/project-deliverables-and-ownership.md` is **not present** in the checkout.

## 1. Role separation

| Role | Who | Reads | Writes |
|---|---|---|---|
| **End user (application)** | Terminal user | Their selected portfolio file (via the service); own reports/logs | Reports/logs/manifest under results dir; never secrets |
| **Application runtime** | Process during a run | The one frozen snapshot; own inputs | Results artifacts, event sink, manifest (write-once) |
| **Coding agent** | OpenCode acting for A/B/C/D/E | Per-role whitelist (below) | Per-role whitelist (below) |
| **Human reviewer** | Team/E | Per course | Governance/CI config, final assembly |

Application roles and coding-agent roles are not conflated: a run gains no development permissions; a coding agent gains no access to real holdings.

## 2. Per coding-agent-role profiles (default-deny)

Deny precedence: **deny wins** over any allow; a more-specific deny overrides a broader allow. All roles: **never readable** `.env`, `.env.enterprise*`, auth/token stores, real portfolio files, logs with real holdings, `.venv`, home-directory config, Git credential data; **symlink escapes excluded** consistently for every role. **Human-only (no coding agent writes):** `.opencode/rules.md`.

### 2.1 Common startup READ set (all coding-agent roles) — F5
Every coding-agent role must read the governance/blueprint startup set; these paths are **readable by all A/B/C/D/E** (still subject to the secret denies above):
```
AGENTS.md, Prompt.md, architecture-blueprint.md, docs/architecture/**,
docs/project-deliverables-and-ownership.md (if present; currently absent from the checkout)
```
This makes the startup reading order runnable under default-deny without opening secret paths.

### 2.2 Role write/extra-read profiles
| Role (owner) | Writable (in-role) | Extra reads (beyond common) | Explicitly denied writable | Phase approval |
|---|---|---|---|---|
| **A — Requirements** | `docs/req/**` | `tradingagents/**`, `cli/**`, `tests/**` | everything else writable (arch/code/tests/governance) | A publishes final D1 |
| **B — Architecture** | approved B set: root `architecture-blueprint.md`, `docs/architecture/adr/**`, the 13 approved architecture files | `tradingagents/**`, `cli/**`, `tests/**`, `docs/req/**` | `docs/req/**`, `tradingagents/**`, `cli/**`, `tests/**`, `pyproject.toml`, `AGENTS.md`, `Prompt.md`, `Report.md`, `.github/**`, `.agent/**`, `.opencode/**`, **`docs/architecture/trace-matrix.md` (E-owned)**, review docs, transcripts | approved write plan |
| **C — Verification** | `tests/**`, `docs/verification/**`, `docs/review-memo.md`, `docs/bug-diary.md`, `docs/debt-register.md` | `tradingagents/**`, `cli/**`, `docs/req/**` | `tradingagents/**`, `cli/**`, `docs/req/**`, architecture (read only), governance/CI, transcripts | test-plan approval (GOV-001) before impl |
| **D — Implementation** | `tradingagents/**`, `cli/**`, `prompts/**`, `docs/experiments/**` | `tests/**` (read), `docs/req/**` | **`tests/**` writes (does NOT auto-receive test-write)**, `docs/req/**`, architecture (read only), governance/CI, `.opencode/rules.md`, transcripts | C's approved tests; E's gates |
| **E — Governance** | `AGENTS.md`, `.opencode/permissions.jsonc` (not `rules.md`), `.github/**`, `docs/code-governance/**`, **`docs/architecture/trace-matrix.md` (E-owned)**, `docs/ai-use-log.yaml`, `transcripts/index.md`, `README.md`, `Report.md` (final edit), `docs/submission/**`, `submission/**` | everything (read), subject to secret denies | `tradingagents/**`, `cli/**`, `tests/**`, `docs/req/**`, the 13 B-owned architecture files (**B-owned; E collects, does not edit**), `prompts/**` | human-authorized |

**Trace-matrix authority (F5):** E is the **sole writer** of `docs/architecture/trace-matrix.md`; it is **removed from B's writable deny set only in E's column** and is **not** in B's writable set. To reconcile deny precedence, the file has exactly one owning role (E) with an explicit write allow; no other role (including B) has a writable allow for it, and any broad deny applied to `docs/architecture/**` for other roles simply keeps it unwritable for them. E's broad read is enumerated by the common startup set (§2.1) plus the role's own/governance paths — not a vague "everything".

**Covenant/verification ownership:** `docs/code-governance/verification-constraints.md` → owner **C** (write); `.agent/rules.md` → owner **E**; `docs/code-governance/structural-constraints.md` → owner **E**. Every required governance/covenant file has one authorized writer; none defaults to nobody.

**Critical rule (B3-06):** D running the coding agent does **not** automatically receive write authority over `tests/**`. Test writes by D require an **explicit, recorded extra authorization** (E-recorded, human-approved exception with rationale), preserving C's independent-verification separation. The same recording applies if roles rotate.

## 3. Application-run data policy (separate from coding agents)

- `PORTFOLIO_DIR` defaults to `<project-root>/portfolios`; discovery **non-recursive**, regular `.json`, deterministic filename order, **symlinks excluded**. Do not search home/credentials/arbitrary folders.
- Explicit `--portfolio PATH` may point outside `PORTFOLIO_DIR`; parent not scanned.
- Selected file read **once**, frozen; not re-read after freeze; source read-only.
- Secrets never emitted; central `Redactor` masks keys/OAuth access+refresh tokens/bearer values.

## 4. Enforcement (E) and denied-write behaviour (GOV-006)

- **Present at `a62b801`:** `docs/code-governance/{verification-constraints.md,test-approval-policy.yaml,self-review-workflow.md,dependency-*}`; CI helpers in `scripts/ci/` (`check_test_approval.py`, `check_ai_log_updated.py`, `check_required_tests.py`, `check_dependencies.py`, `build_pr_self_review.py`); workflows `.github/workflows/{ci,test-approval,test-approval-complete,pr-self-review,release-assets}.yml`.
- **Absent / paused (separate from the schema gate):** the OpenCode permission package (`AGENTS.md`, `.opencode/permissions.jsonc`, `.opencode/rules.md`, `.agent/rules.md`) is not present, so per-role file rights below are **design intent only**. The `test approval` tooling exists but is **not** a required check; a PR merged with a failed approval check (24 November review, I24 03). **Requirements schema gating, by contrast, is now implemented** (`requirements schema` CI job + checker + tests) and E-reported as a required main check (administrative endpoint not independently readable — HTTP 401).
- E wires per-role whitelists into `.opencode/permissions.jsonc` and CI. A denied access attempt must be **blocked and logged without changing the file**. This draft does **not** claim a demonstrated permission denial. (The requirements-schema CI gate is implemented; the OpenCode permission chain is not.)
- Branch protection: the `requirements schema` job is E-reported as required alongside the original four with strict up-to-date protection retained; the exact administrative required-check setting could not be independently read (HTTP 401) and remains **E-reported**, not verified by this session. ADR-for-safety-change review remains the intent. B's ADRs remain the architecture contribution.

## 5. Permitted/denied examples (document examples) — F5
- **Startup reads:** A/B/C/D/E can all read `AGENTS.md`, `Prompt.md`, `architecture-blueprint.md`, `docs/architecture/**` → permitted.
- **E writes `docs/architecture/trace-matrix.md`** → permitted (E sole owner); **B writes it** → denied.
- **D writes `tests/test_output_check.py`** → **denied** (D lacks test-write) unless an E-recorded extra authorization exists.
- **C writes `tests/...`** → permitted (C owns tests).
- **Any agent edits `.opencode/rules.md`** → **denied** (human-only).
- **Any agent reads `.env` or a real portfolio file** → denied.

## 6. Out of scope
No exposure/account validation, no broker credentials handling, no new web auth surface. No claim of installed governance.
