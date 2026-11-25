# Member A — A2 handoff for E: final requirement identity and adoption

Prepared 25 November 2026 (Asia/Hong_Kong). Reference: A's branch `req-a-h3-h5-v2`, based on upstream main `761918e` (which already contains E's H3/H5 follow-up `dc6f2ee`).

## Status

- **A2 — Partial.** Registry identity, adoption status, final IDs, acceptance criteria and the `SEL-TA-*` crosswalk are supplied below. **One item is not mine to close:** whether `SEL-TA-GOV-003` and `SEL-TA-GOV-006` become registry entries is still undecided (OQ-10), and the confirmation-flow requirement does not exist yet (OQ-16).
- **A1 — Ready.** Six dated records and a provenance index are in [`AI-log/Member-A/`](../AI-log/Member-A/).

## 1. Authoritative revision and adoption status

| Item | Value |
|---|---|
| `docs/req/requirements.yaml` | 36 active entries, 3 withdrawn IDs, `schema_version` 1.2.0 |
| `docs/req/req-schema.json` | 1.2.0 |
| `document.status` | **`proposed_for_adoption` — unchanged.** No five-member adoption record exists, so it is not and must not be set to `adopted`. |
| A's branch | `req-a-h3-h5-v2`, one commit on top of `761918e` (pending A's own push; no merge or adoption implied) |
| Upstream main at time of writing | `761918e` — contains E's H3/H5 follow-up `dc6f2ee`; **does not yet contain** this branch |

```
python3 docs/req/validate.py                 36 requirements; 3 withdrawn; 0 error(s), 0 warning(s)   exit 0
python3 docs/req/negative-fixtures-check.py  all 32 negative fixtures fail correctly                   exit 0
ruff check .                                 All checks passed
```

**A schema pass is not adoption and not proof of implementation.** 26 of the 36 active entries are `status: proposed` and 10 are `partial`; none is `implemented`. The validator proves the registry is internally consistent and that 32 stated failure modes are caught — nothing more.

## 2. Wording that governs semantic evaluation, negative cases and safety review

A single rule, stated because it has already caused a defect: **the requirement text in `requirements.yaml` governs; `selected-requirements.md` is a historical working selection, not the specification.**

- `SEL-TA-*` is the team's earlier selection (12 Nov). It remains the implemented baseline C's tests exercise, but it is **not** the adopted requirement set.
- Where the two disagree, the `REQ-TA-*` entry wins for acceptance. Where a `SEL-TA-*` obligation has **no** `REQ-TA-*` counterpart, that obligation is **not in the specification** — see §3.

## 3. Crosswalk: `SEL-TA-*` → `REQ-TA-*`

**Provenance of this table matters.** It is derived from Member B's provisional crosswalk in `docs/architecture/traceability-inputs-member-b.md` §2 (relationship values: same / partial / none-clash / proposed-only). B wrote that table as *provisional* and *candidate*. **A has checked every row against the current registry and corrected four rows**; the corrections are marked **[A]**. Rows are matched **by meaning, never by numeric suffix** — `SEL-TA-FR-003` is input freezing whereas `REQ-TA-FR-003` is checkpoint/resume.

| `SEL-TA-*` | Meaning | `REQ-TA-*` | Coverage | Note |
|---|---|---|---|---|
| FR-001 | discover/select portfolio file | **none** | **no coverage** | No active entry. Candidate `REQ-TA-FR-009` not created (OQ-16). |
| FR-002 | explicit confirmation | **none** | **no coverage** | `REQ-TA-FR-002` is a **withdrawn GUI** entry. |
| FR-003 | validate and freeze snapshot | `REQ-TA-INV-014` | **partial** **[A]** | Input freezing, immutable snapshot and fingerprint. `REQ-TA-FR-003` is resume — a different obligation. |
| FR-004 | propagate context, invent no holdings | `REQ-TA-FR-007` (pt. 3), `REQ-TA-INV-003` | **partial** | No ownership wording. `REQ-TA-FR-004` is point-in-time evidence. |
| FR-005 | ratings vs actions | `REQ-TA-FR-007`, `REQ-TA-INV-001`, `REQ-TA-ARCH-002` | **partial** | Rating meaning; `REVIEW` never passes. |
| FR-006 | deterministic input provenance | `REQ-TA-NFR-REPRO-001`, `REQ-TA-INV-014` | **partial** | Run record carries the fingerprint. |
| FR-007 | output-check authority (Q1–Q4) | `REQ-TA-ARCH-002`, `REQ-TA-INV-001` | **partial** | R1–R8 rules and their enforcement components. |
| NFR-001 | typed external-failure handling | `REQ-TA-NFR-001`, `REQ-TA-RUN-001` | **partial** **[A]** | B listed only NFR-001; the typed stop-reason vocabulary lives in RUN-001, so a reader of NFR-001 alone would miss half the obligation. |
| NFR-002 | structured observability | `REQ-TA-NFR-OBS-001` | **partial** | JSONL events, one terminal event. |
| NFR-003 | credentials **and** holdings privacy | `REQ-TA-SEC-002` | **partial (reduced)** | `SEC-002` covers **credentials only**. The **holdings-minimisation half maps to no registered entry**; only candidate `INV-010` clause 2, which is not in the registry. |
| NFR-004 | immutable fresh-run artifacts | `REQ-TA-NFR-REPRO-001` | **partial** | Per-run ID, refuse overwrite, publication-failure exception. |
| NFR-005 | cohesive integration, no prompts in agents | `REQ-TA-ARCH-001` | **partial** | Vendors behind one routing point; layering. |
| NFR-006 | transparent evaluation population | `REQ-TA-NFR-EVAL-001` | **partial** | Started-run accounting. |
| GOV-001 | test-plan prior approval | `REQ-TA-GOV-002` | **partial** | Stated as a requirement; **the gate is paused** and not a required merge check. |
| GOV-002 | registry schema validation | `REQ-TA-GOV-004` | **same** **[A]** | B recorded this as "misfiled/partial" in an earlier draft; the registry entry now exists and the CI job `requirements schema` is reported implemented. |
| GOV-003 | CI lint/test/dependency gates | **none** | **no coverage** | **Open (OQ-10).** A has not added an entry. |
| GOV-004 | semantic evaluation gate | `REQ-TA-GOV-001` | **partial** | `REQ-TA-GOV-004` is schema validation — **not** semantic evaluation. This collision is the most common source of confusion. |
| GOV-005 | AI-use log before merge | `REQ-TA-GOV-003` | **same** | Gate exists per E; A's own compliance is E's call. |
| GOV-006 | permissions / branch protection | **none** | **no coverage** | **Open (OQ-10).** |

**Candidate-only obligations with no `SEL-TA-*` counterpart** (proposed, not implemented): `RUN-001`; `FR-001`, `FR-004`, `FR-005`, `FR-006`, `FR-008`; `NFR-002`, `NFR-PERF-001..002`, `NFR-COST-001..003`; `SEC-001`, `SEC-003`; `ARCH-001`, `ARCH-002`; `INV-001..008`, `INV-014`; `GOV-001`, `GOV-003`, `GOV-004`. `FR-003` is candidate-and-implemented-by-baseline (resume already works), but it is not a `SEL-TA-*` obligation.

### 3.1 Corrections A made to B's table, and why

| Row | B's version | A's correction | Reason |
|---|---|---|---|
| FR-003 | "none/clash" | `INV-014` — **partial** | B's table had no entry for input freezing at all. It is `INV-014`'s subject; the entry did not exist in that form when B wrote the table. |
| NFR-001 | `NFR-001` only | `NFR-001` + `RUN-001` — partial | The typed stop reasons are RUN-001's contract. |
| GOV-002 | "partial / misfiled" in an earlier draft | **same** | The `GOV-004` entry exists and its gate is implemented. |
| GOV-003 | `REQ-TA-GOV-003` (mapped to the AI-log gate) | **none** | B matched the suffix. `GOV-003` is the AI-use log; CI lint/test/dependency gates are a different obligation and have **no** entry. |

## 4. Withdrawn and deliberately deferred items

**Withdrawn — never reuse these IDs:**

| ID | Reason |
|---|---|
| `REQ-TA-FR-002` | GUI out of scope; a GUI is a feature, not a quality attribute |
| `REQ-TA-NFR-SAFETY-001` | Research-only scope: no position sizing is validated |
| `REQ-TA-NFR-SAFETY-002` | Research-only scope; replaced by `REQ-TA-FR-007` part 3 |

**Deliberately deferred / not in the registry — do not invent a row for them:**

| Item | Why absent | Owner |
|---|---|---|
| Portfolio confirmation flow (confirm/decline/EOF, `input.consent`) | No active entry owns it. Correcting a mis-citation exposed the gap; recorded as **OQ-16**, candidate `REQ-TA-FR-009` | A to propose, B to confirm the event contract |
| Holdings minimisation | Only candidate `INV-010` clause 2; not in the registry | A/B |
| Architecture `INV-11`, `INV-14` as `REQ-TA-*` entries | Not registered; cited by architecture ID and marked unregistered (**OQ-16b**). `INV-009…013` are held back pending D's Q-8d | A/D |
| `SEL-TA-GOV-003`, `SEL-TA-GOV-006` | Not added; A declined to sweep three gates in on one partial answer (**OQ-10**) | A + E |
| Token-admission contract | Stated as proposed obligation only; no design, no implementation | B/D (design), C (acceptance) |

## 5. Answered requests from E's document

- **A1 AI-use records** — supplied, six dated files plus provenance index. One project session was located in the tool's local SQLite history; unrelated directories were not read. Paths redacted, tool output omitted, tails of long assistant messages truncated in place.
- **Are the withdrawn IDs still needed in the matrix?** Yes, as rows marked *withdrawn*, so a reader who greps a deleted ID finds a reason rather than nothing.
- **Which `GOV-004` is which?** `REQ-TA-GOV-004` = registry schema validation. The team's `SEL-TA-GOV-004` = semantic evaluation, which is A's `REQ-TA-GOV-001`. Every further `GOV-004` mention in the architecture should say which one it means.

## 6. Unresolved, with owner

| # | Item | Owner |
|---|---|---|
| 1 | Five-member adoption record (`document.status` stays `proposed_for_adoption` until it exists) | Whole team |
| 2 | Confirmation-flow requirement (OQ-16) | A proposes, B confirms |
| 3 | `SEL-TA-GOV-003` / `-006` as entries (OQ-10) | A + E |
| 4 | Fixture-profile authority (OQ-17): structured `assignment` declared authoritative, prose rows still inconsistent for `INV-014` and `SEC-002` | C decides population |
| 5 | D has not answered D1–D12 or Q-8d | D |
| 6 | C has not answered C3–C10 or crosswalk X1–X7 | C |
| 7 | `TOKEN_BUDGET` has no adopted number; `state: open` | A/E/D |

**No approval is claimed and none exists.** Nothing above is a substitute for the five-member adoption record or for C's independent semantic acceptance.
