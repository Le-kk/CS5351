# Permission Model (Member B design)

Status: architecture draft (revised 2026-11-12 per review B3-06; implementation-aligned 2026-11-24; governance status corrected to baseline `32ec858`, 2026-11-25). Describes **application roles during a run** and **per-coding-agent-role file rights**, kept separate. E implements enforcement. **Root `AGENTS.md` exists** as startup/ownership/verification guidance (conventions, not an ACL); the project covenant `.agent/rules.md` is startup-read (not auto-injected); `.opencode/rules.md` is the shared role prompt. The **`.opencode` role-permission package now exists and is configured** (`.opencode/permissions.jsonc` + launcher `scripts/run_role_agent.py`), E-native-verified on OpenCode V1 1.19.5 (69 passing cases, matching policy/rules/covenant hashes). **But that control is active only when a session is started through the explicit compatible launcher/profile**; ordinary sessions are not retroactively governed, this documentation session has **not** been shown to run the strict B profile, and **OS ACLs, authenticated member identity, unrestricted-host bypass and continuous symlink isolation remain outside the guarantee**. **Seven required check names (E-reported; administrative endpoint HTTP 401, not directly inspected here):** `required tests`, `ruff (strict, full repo)`, `dependency check`, `ai-log updated`, `requirements schema`, `type check`, `security checks`; hosted outcomes observed. **Paused approval enforcement (separate):** `test approval` tooling exists but is **not** required — test-plan pre-approval is deliberately **paused** per `AGENTS.md`. See §4a and `risk-list.md` R-GOV.

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

Deny-precedence: as **B's intended protection outcome** (design intent), **deny wins** over any allow; a more-specific deny overrides a broader allow. `§4a` records the **as-built native** algorithm, which differs (last matching rule wins) and reaches the same intended outcomes only by a deliberate rule ordering. All roles: **never readable** `.env`, `.env.enterprise*`, auth/token stores, real portfolio files, logs with real holdings, `.venv`, home-directory config, Git credential data; **symlink escapes excluded** consistently for every role. **Human-only (no coding agent writes):** `.opencode/rules.md`.

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

- **Present at `14b06a5` (2026-11-25):** root `AGENTS.md` (startup/ownership/verification guidance); `docs/code-governance/{verification-constraints.md,test-approval-policy.yaml,self-review-workflow.md,types-and-security-coverage.md,requirements-schema-gate.md,dependency-*,public-api-contract.json}`; CI helpers in `scripts/ci/` (`check_test_approval.py`, `check_ai_log_updated.py`, `check_required_tests.py`, `check_dependencies.py`, `check_requirement_schema.py`, `check_workflow_permissions.py`, `check_security_scan.py`, `build_pr_self_review.py`); workflows `.github/workflows/{ci,test-approval,test-approval-complete,pr-self-review,release-assets}.yml`. Additional CI jobs `type check`, `security checks`, `requirements schema` are implemented and hosted-verified.
- **Configured and E-native-verified (baseline `32ec858`), conditional on explicit compatible activation:** the `.opencode` role-permission package (`.opencode/permissions.jsonc` profiles A–E, `.opencode/rules.md` shared role prompt, `.agent/rules.md` covenant) exists; launcher `scripts/run_role_agent.py` selects a profile and checks version/resolved policy/prompt before a **fresh** session; native probes (`scripts/verify_role_permissions.py`) retain an E7 record of **69 passing cases** on OpenCode **1.19.5** with matching policy/rules/covenant hashes. The per-role table in §2.2 states the **intended** rights; §4a states the **as-built** native capabilities and limits. This documentation session has **not** been shown to run the strict B profile.
- **Still outside the guarantee:** OS-level ACL/sandbox, authenticated member identity, unrestricted-host bypass, race-free symlink isolation (the launcher's symlink guard is a startup check) and tamper-proof CI. `.opencode/rules.md` is human-only for writes; an agent may not relax policy or switch tools to evade a denial. The CI **workflow-permission checks** validate CI tokens/trusted checkouts — **not** per-agent filesystem controls.
- **Paused approval (separate from the CI checks):** the `test approval` tooling exists but is **not** a required check; test-plan pre-approval is **paused** by the user's instruction (a PR merged with a failed approval check, 24 November review, I24 03).
- E wires/owns the per-role whitelists in `.opencode/permissions.jsonc`; a denied access attempt must be **blocked and logged without changing the file**. **A denied operation must never be reported as successfully executed. A negative probe passes when the expected denial occurs and the protected target remains unchanged.**
- Branch protection: seven check names (`required tests`, `ruff (strict, full repo)`, `dependency check`, `ai-log updated`, `requirements schema`, `type check`, `security checks`) are **E-reported** as required with strict up-to-date protection retained; hosted job/probe outcomes are observed (review evidence), but the administrative setting could not be independently read (HTTP 401) and remains **E-reported**, not verified by this session. ADR-for-safety-change review remains the intent. B's ADRs remain the architecture contribution.

## 4a. As-built native capabilities and limits (E-native config on OpenCode V1 1.19.5)

This records what the configured native profiles actually do at baseline `32ec858`; it is verified by E's retained native probes, not reproduced by this documentation session, and it is **active only under the explicit launcher**.

- **Rule precedence is as-built "last matching rule wins"**, not blanket deny-wins. The configuration puts each role's broad deny **before** path allowances and sensitive denies **last**, so the intended protection outcomes in §1–§2 hold *by ordering* — a future edit that reorders rules can silently change an outcome; re-run the probes after any change.
- **Activation:** start through `python scripts/run_role_agent.py <A|B|C|D|E> [--check]` from the repository root. The launcher sets `OPENCODE_CONFIG`, removes inline overrides, requests pure mode, checks the executable version (currently pinned `1.19.5`) and the resolved native rules/prompt, and starts a **fresh** session; a failed check refuses startup and does not resume an existing session. Merely starting an unrelated session does not load this policy.
- **Startup vs prompt:** operating rules (`.opencode/rules.md`) load as the **role prompt**; the covenant (`.agent/rules.md`) is **startup-read, not automatically injected**. `Prompt.md` H1/H2/H3 are human launch gates — they are **not** authenticated or recorded automatically, and a permission grant is not a human approval.
- **Actual role capabilities (strict B):** shell, Git, test execution, broad search, delegation, web and unspecified tools (incl. MCP) are **denied**; B's edit whitelist excludes `docs/architecture/proposals/implementation-prompt-pack-2026-11-24.md` and `docs/req/README.md`, and the review directory is not explicitly readable. Each role may update its own `AI-log/Member-<role>/` records (authenticity rules in `AGENTS.md`). Denied operations are handed to an authorized human/session; do not bypass with another tool or edit policy.
- **Bounded scope:** a local-tool control only — no OS sandbox, no authenticated member identity, no project MCP integration, no new required merge check. The internal tool-output external-directory allowance and host context are not certified as a universal information-flow sandbox.

## 5. Permitted/denied examples (document examples) — F5
- **Startup reads:** A/B/C/D/E can all read `AGENTS.md`, `Prompt.md`, `architecture-blueprint.md`, `docs/architecture/**` → permitted.
- **E writes `docs/architecture/trace-matrix.md`** → permitted (E sole owner); **B writes it** → denied.
- **D writes `tests/test_output_check.py`** → **denied** (D lacks test-write) unless an E-recorded extra authorization exists.
- **C writes `tests/...`** → permitted (C owns tests).
- **Any agent edits `.opencode/rules.md`** → **denied** (human-only).
- **Any agent reads `.env` or a real portfolio file** → denied.

## 6. Out of scope
No exposure/account validation, no broker credentials handling, no new web auth surface. Governance is **configured and E-native-verified but only conditionally active** under the explicit launcher; OS-level enforcement, member identity and tamper-proof CI are not claimed (see §4a).
