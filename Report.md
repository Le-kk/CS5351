# CS5351 Project Process Report

Assembly draft — 2026-11-25. This is the single D6 assembly location, not final course acceptance. Source-attributed A/D supplied writing is included below; E integration synthesis is labelled. B/C final personal reports/reflections, all confirmed names/student IDs, actual relative contributions and final source/semantic acceptance remain pending. Word/page compliance must be checked on the final rendered document; no invented contribution percentages or author approvals are supplied.

## Team and contributions

A: requirements; B: architecture (supplied D5 identifies Leung Kwan Kit, 57611829); C: verification; D: implementation/baseline evaluation; E: governance/integration and leadership. Remaining names, IDs, actual hours/story points and agreed contribution ratios must be confirmed by the team.

## Process and current integration synthesis — E

The team extended an existing TradingAgents baseline rather than claiming the upstream multi-agent application as new work. A elicited and validated typed requirements; B recorded candidates, interfaces and invariants; C contributed independent negative tests, repair verification and an honest evidence/debt register; D supplied baseline/evaluation records and implementation inputs; E integrated gates, traceability, AI-use records and the presentation interface. Authoritative adoption and independent acceptance remain separate from implementation.

Reviews exposed mismatches among requirement wording, code and tests: budget vocabulary, corrected-only findings, distinct-case evaluation counts, REVIEW/PASSED contradictions and leading disclaimer placement. These were resolved through owner decisions and executable negative examples, with history retained rather than rewriting prior failures. Exact requirement adoption, semantic profile/threshold and final approval gaps remain identified in the registry and C's delivery records.

The product boundary freezes confirmed portfolio inputs, preserves missing-versus-empty semantics, invokes the existing graph, checks outcomes and publishes a manifest/report/events record. The browser is an adapter around that boundary. Refresh originally lost the selected run while background work continued; the repaired frontend remembers only the run ID, shows active work and preserves interrupted history. No false completion or missing-usage zero is introduced.

Efficiency work first reduced duplicated debate context and encouraged concise intermediate reports. A later opt-in compact evidence format changed existing calls without adding a summarizer or truncating saved reports. The NVDA/2026-11-24 developer comparison used 130,787 total tokens in the control and 96,160/95,023 in the final candidates (mean 95,591.5, 26.91% lower). Model/tool/data variability and one-case sample size prevent universal or semantic-quality claims. This is not an enforced cumulative TOKEN_BUDGET.

The seven existing required check names remain stable. The regression summary now covers frontend build/audit as well as Python regression and clean installation. Schema validation is structural, type coverage is scoped, application security scanning is explicit, and AI-log gating checks updates rather than certifying conversation quality. Prior test approval remains paused as a required merge check. Native role-permission history is tied to its original policy hashes; path-equivalent updates need renewed native verification before claiming those old probes certify the new policy.

Current source is physically under src/ and tests under test/offline and test/live, with legacy aliases to preserve the baseline interfaces. Historical reports, raw transcript source copies and failing evidence are retained. History contains superseded launch material, not discarded defects. This co-evolution is supported by the trace matrix, source manifests and AI-use index; it does not replace final owner review.

## Requirements contribution — supplied Member A report

Source: [Member A report](docs/submission/member-a/a-written-report-2026-11-25.md). Its dated statements are the author's supplied account, not newly remeasured assertions.

## Specification of a Portfolio-Aware Research System: Requirement Elicitation, Formal Registry Construction and Machine-Checkable Acceptance Criteria

**Member A — CS5351 Software Engineering Project**

---

### Abstract

This report documents Member A's contribution to the CS5351 project: the elicitation, structure, formalisation and machine-checking of the software requirements for a portfolio-aware extension of the TradingAgents research system (version 0.7.1). The work produced a version-controlled requirement registry comprising thirty-six active entries and three withdrawn identifiers, expressed in a schema-validated YAML artefact, together with a twenty-nine-rule validator and a thirty-two-case negative-fixture suite that empirically falsifies the validator's claims. The report sets out the elicitation method, the representation decisions (identifier stability, typed criteria, MoSCoW prioritisation, Given/When/Then fit criteria), the defect-detection regime, and an explicit account of what the artefact does and does not establish. A central methodological finding is that the validator itself is a claim requiring test: three successive external review rounds identified defects not only in the requirements text but in the checking apparatus, including a citation rule that could not resolve multi-segment identifiers and a parameter rule that could not see the names it purported to check. The report argues that requirements engineering for safety-adjacent systems must treat the verification tooling as part of the deliverable, and must distinguish conformance from adoption.

**Keywords:** requirements engineering; acceptance criteria; traceability; schema validation; negative testing; AI-assisted software development

---

### 1. Introduction

TradingAgents v0.7.1 is a multi-agent large-language-model system that produces equity research reports through a graph of specialised agents (market, news, social and fundamentals analysts; a bull/bear research debate; risk management; a portfolio manager). The system in its baseline form accepts no portfolio context, records no per-run provenance, and provides no deterministic guarantee that a delivered rating is machine-readable.

The CS5351 project extends this system with an optional portfolio input and an auditable reporting layer. Responsibility for the specification was allocated to Member A. The task as stated in the project brief was to decide which requirements form the final set, to record each with a stable identifier, a type, a MoSCoW priority and a testable fit criterion, and to produce a scope statement suitable for adoption by the team.

This report describes how that task was executed, using the IEEE 830 recommendation practice for software requirements specifications (IEEE, 1998) and the ISO/IEC/IEEE 29148 standard for requirements engineering (ISO/IEC/IEEE, 2018) as the reference vocabulary for structure, verifiability and traceability. It also reports, candidly, the defects in the work, because the requirement artefacts were subjected to three rounds of independent external review and every finding in those rounds was confirmed against the source materials.

Section 2 describes the elicitation method. Section 3 sets out the representation and the validator design. Section 4 reports the defect-detection regime and what it found. Section 5 discusses threats to validity and the limits of what the artefact establishes. Section 6 concludes.

### 2. Method

#### 2.1 Elicitation

Requirements were elicited from four source classes, each recorded with a source reference in the registry so that a later reader can distinguish an observation from an inference:

1. **Course documentation.** The project brief and its gate specification named obligations (for example the AI-use log gate and the schema-validation gate) that the team had not yet expressed as requirements.
2. **Baseline code observation.** Each entry's `baseline` field records what the current code actually does, with file and symbol references, so that a requirement claiming a gap is distinguishable from one describing existing behaviour. For instance, `REQ-TA-FR-003` (checkpoint and resume) records that resume already works via per-node SQLite checkpoints, whereas `REQ-TA-FR-001` (evidence identifiers) records that nothing currently assigns such an identifier.
3. **Peer review.** Three rounds of external review by a team member acting as independent reviewer produced more usable defect reports than any self-check, and are treated in Section 4 as primary evidence.
4. **Open questions.** Where a decision belonged to another member (for example whether a CI gate becomes a registry entry, or whether declining a portfolio prompt should prevent even a local file read), the item was recorded as a numbered open question rather than resolved unilaterally.

This fourth mechanism proved the most important. A requirement set produced by one author will contain commitments that exceed that author's authority; recording them as explicit open questions with named owners preserves the information without fabricating a decision.

#### 2.2 Conflict resolution

Baseline documents contained contradictions, the most consequential being a scope statement that excluded portfolio input while the test profiles required a portfolio to exist. Resolution followed a stated rule: the requirement text governs, superseded documents retain historical status, and any change to acceptance population belongs to the member who owns verification rather than to the requirements author.

#### 2.3 What was deliberately not done

Where a decision exceeded A's authority, no entry was invented. Two such cases are recorded openly: the portfolio confirmation flow (no active entry owns the confirm/decline/EOF sequence, although the code emits an `input.consent` event) and the holdings-minimisation obligation (present only as an unregistered candidate). Both are carried as open questions with candidate identifiers, so that the gap is visible in the matrix instead of being concealed by citing an unrelated requirement.

### 3. Representation

#### 3.1 Registry structure

The registry is a single YAML document validated against a JSON Schema (draft 2020-12) that constrains structure but not meaning. Each requirement carries an immutable identifier of the form `REQ-TA-<CLASS>-<NNN>`, a title, a type drawn from a controlled vocabulary mapped to ISO/IEC 25010 quality characteristics, a MoSCoW priority, a status, a normative statement, a Given/When/Then fit criterion, a trade-off statement, dependencies and source references.

Three representation decisions deserve justification:

**Identifier stability and non-reuse.** Withdrawn identifiers (`REQ-TA-FR-002`, `REQ-TA-NFR-SAFETY-001`, `REQ-TA-NFR-SAFETY-002`) are retained in a withdrawal list with reasons and may never be reassigned. This is required for traceability: a reader who searches for a withdrawn identifier must find a reason, not silence. A corollary is that numbering must not skip, because an absent number reads as a reserved or deleted requirement.

**Typed criteria rather than prose.** Every entry states a metric, a threshold and a verification method. Where a requirement is an invariant, the entry additionally names the code components that enforce it. This separation was forced by a review finding: an earlier version named a requirement as the enforcer when the actual enforcement was a service class, which is a category error rather than a citation error.

**Separation of proposal from adoption.** The document status remained `proposed_for_adoption` throughout. This is deliberate: a schema validation pass proves internal consistency, not team consent, and conflating the two is the requirements-engineering analogue of accepting a unit test as a user-acceptance test.

#### 3.2 The validator as a first-class deliverable

Because the registry is generated from a script and checked by a validator, the validator's correctness is itself a requirement. The validator implements twenty-nine rules, including bidirectional reference resolution (every identifier cited in prose must resolve, and every declared parameter must actually be cited by exactly the entries that claim to use it), withdrawal preservation, MoSCoW ordering, and completeness of the Given/When/Then form.

### 4. Defect detection

#### 4.1 Negative fixtures

A validator claim is worthless without a case that attempts to violate it. The project therefore maintains a negative-fixture harness in which each case asserts three properties: non-zero exit, exit for the stated reason, and absence of an unrelated failure such as a missing module or a traceback. Thirty-two cases are executed. The three-property assertion matters because a crash produces a non-zero exit code while proving nothing about the rule.

#### 4.2 Findings across three review rounds

Three rounds of external review produced fifteen findings across requirements text, enforcement references, acceptance criteria and validator coverage. All were confirmed. Table 1 summarises the material ones.

**Table 1. Representative confirmed defects and their root causes**

| Finding | Root cause | Class |
|---|---|---|
| Scope cited a withdrawn GUI identifier as the consent requirement | Labels were assigned by position, not by consulting the registry | Editorial, but concealed a real gap |
| Persistence clauses cited `REQ-TA-INV-012`, which never existed | The reference rule inspected structured fields only, never prose | Tooling gap masking a content defect |
| An invariant named itself as its enforcer | A rule required some identifier to be present, so the nearest one was chosen | Incentive defect: the check rewarded passing, not correctness |
| Deleting a freshness parameter still validated | The parameter pattern permitted one prefix segment, so three-segment names never matched | Tooling gap |
| A multi-segment identifier in prose passed unchecked | The citation pattern was hard-coded to a single namespace segment instead of using the schema's own grammar | Tooling gap |
| A null list entry produced a traceback rather than a finding | Cross-record rules assumed every entry was a mapping with an identifier | Resilience gap |

Two observations follow. First, the tooling defects are not incidental: they were the mechanism by which substantive defects survived inspection. A citation rule that cannot see prose permits a phantom reference indefinitely. Second, the self-referential enforcer arose because the rule required *an* identifier rather than *the correct* one; the remedy was structural — the schema now separates a requirement crosswalk from a list of enforcing code components, so that satisfying the check no longer requires choosing an unrelated requirement.

### 5. Discussion and threats to validity

**Construct validity.** A fit criterion is only as good as the measurement it names. Several criteria depend on quantities not yet measured (the token budget has no adopted figure and is recorded as `open`; the quality threshold is to be measured). Recording an unmeasured threshold as provisional is honest but does not constitute a testable requirement; this is a residual weakness.

**Internal validity.** Self-assessment was demonstrably unreliable. Every round of independent review found defects that the author's own checks had passed, including defects introduced while fixing the previous round. This supports treating independent review as a control, not a courtesy.

**External validity.** Thirty-two negative fixtures demonstrate that the validator rejects thirty-two specific defect classes. They do not demonstrate that no other defect class exists, and they cannot detect a well-formed but semantically wrong requirement; two such defects were found only by human reading.

**What the artefact does not establish.** The registry is not adopted. No implementation is claimed: twenty-six entries are `proposed` and ten `partial`. No acceptance test result is claimed by the author. The trace matrix assembled by Member E must not treat a schema pass as evidence of implementation.

### 6. Conclusion

The contribution is a requirement artefact whose value lies less in its thirty-six entries than in its supporting apparatus: an immutable identifier scheme, machine-checkable criteria, a validator whose failure modes are themselves tested, and an explicit register of what remains undecided and whose decision it is. The principal methodological lesson is that in AI-assisted requirements work the verification tooling must be reviewed as rigorously as the requirements, because a permissive checker silently converts defects into apparent compliance.

---

### References

IEEE. (1998). *IEEE Recommended Practice for Software Requirements Specifications* (IEEE Std 830-1998). Institute of Electrical and Electronics Engineers.

ISO/IEC. (2011). *Systems and software engineering — Systems and software Quality Requirements and Evaluation (SQuaRE) — System and software quality models* (ISO/IEC 25010:2011). International Organization for Standardization.

ISO/IEC/IEEE. (2018). *Systems and software engineering — Life cycle processes — Requirements engineering* (ISO/IEC/IEEE 29148:2018). International Organization for Standardization.

IEEE. (2017). *IEEE Standard for System, Software, and Hardware Verification and Validation* (IEEE Std 1012-2016). Institute of Electrical and Electronics Engineers.

Meyer, B. (1992). Applying "design by contract". *Computer*, 25(10), 40–51.

Project artefacts (primary sources, repository `kelepawuqiusi/CS5351`):

- Member A. *Requirement registry* — `docs/req/requirements.yaml`, schema 1.2.0; 36 active entries, 3 withdrawn.
- Member A. *Registry schema* — `docs/req/req-schema.json`, version 1.2.0.
- Member A. *Validator* — `docs/req/validate.py`, 29 rules.
- Member A. *Negative-fixture harness and specification* — `docs/req/negative-fixtures-check.py`, `docs/req/negative-fixtures.md`, 32 cases.
- Member A. *Change log and source notes* — `docs/req/change-log.md`, `docs/req/requirement-source-notes.md`.
- Member A. *Handoff to E* — `docs/req/a2-handoff-to-member-e-2026-11-25.md`.
- Member A. *Selected AI-use records* — `AI-log/Member-A/`.
- Member B. *Provisional semantic crosswalk* — `docs/architecture/traceability-inputs-member-b.md` §2.
- TradingAgents v0.7.1 source tree, as observed at the baseline revisions cited in each registry entry.


## Architecture contribution — assembly pending

Use the canonical blueprint, ADRs, candidate table, interfaces, invariants and B's annotated D5 transcript. A final member-authored narrative/reflection and confirmation remain pending; the integration summary above is not a substitute author signature.

## Verification contribution — assembly pending

Member C's current verification report, requirement mapping, evidence index, review memo, debt register and bug diary provide the evidence base. Their historical source bindings and failures are preserved. Final personal reflection/full D5 export and delivery-SHA acceptance remain pending.

## Baseline and evaluation contribution — supplied Member D report

Source: [Member D report](docs/submission/member-d/written-report-2026-11-25.md). Its original attribution and dated measurement limits are retained.

## Member D — Baseline Measurement and Evaluation Evidence

Formal write-up of assigned work for the team final report. Evidence is drawn from the
records in `AI-log/Member-D/` (`2026-11-13_05-02-00.md`, `2026-11-23_15-25-00.md`,
`2026-11-23_16-15-00.md`, `2026-11-23_20-10-00.md`) and from the requirement registry
`docs/req/requirements.yaml`.

### 1. Role and scope

My assigned role in Section 3 of the plan is "baseline and evaluation": measure latency and
token consumption of the TradingAgents pipeline under one frozen configuration, repeat the
measurement after the team's code changes, and supply the evaluation counting rules that make
every reported number reproducible and auditable. Design decisions about the graph, the
interfaces and the CI gates belong to A, B, C and E; my contribution is the measurement
instrument, the before/after evidence, the attribution of cost to pipeline stages, and the
feasibility assessment of the cost and performance requirements.

The work addresses `REQ-TA-NFR-PERF-001`, `REQ-TA-NFR-PERF-002`, `REQ-TA-NFR-COST-001`,
`REQ-TA-NFR-COST-002`, `REQ-TA-NFR-COST-003` and `REQ-TA-NFR-EVAL-001`. All of these are
`Should` or `Could` in the registry, and all of them are stated in terms of a measured quantity
that did not exist before this work.

### 2. Method

**Frozen configuration.** Ticker NVDA, analysis date 2026-01-09, the four analysts (market,
news, social and fundamentals), one research-debate round, one risk-discussion round,
checkpoints disabled, sequential execution, provider `deepseek`, and both model tiers set to
`CS5351/DeepSeek-V4-Flash` served by the CityU shared gateway. The configuration was held
identical across the baseline cohort and the after-build cohort, so any difference between
them is attributable to the code revision and not to the model, the endpoint or the budget.
The registry requires exactly this discipline: `REQ-TA-NFR-EVAL-001` rule 6 permits a comparison
only when the run records match on `config` and `prompt_hash`, or when exactly one factor is
declared as changed.

**Measurement instrument.** Token figures were read from the token counters of a
`StatsCallbackHandler` attached directly to the graph, not from the CLI live panel. The panel
is a display surface, not an accounting surface: on the first baseline run it reported
106.2k input and 20.0k output against measured values of 114.9k and 24.1k, an undercount of
about 13% and 17% respectively. Reporting from the panel would therefore have overstated the
effect of any later change. The instrument choice is recorded in both measurement records and
is treated as part of the method, not as an implementation detail.

**Run accounting.** Only runs that reached a terminal state with a usable result entered the
cohort. Runs that stalled were counted, named and excluded, and the number excluded is reported
beside every average. This is the counting rule later written into `REQ-TA-NFR-EVAL-001`
rule 1: no run is ever removed from the completion denominator.

### 3. Before/after results

The baseline cohort was taken at revision `2c22ef9`; the after-build cohort at `98b82c9`, after
23 commits from the other members.

| Stage | Run | s | Tokens in | Tokens out | Total | Calls | Decision |
|---|---|---|---|---|---|---|---|
| Before | B1 | 117.6 | 114,911 | 24,100 | 139,011 | 16 | `Overweight` |
| Before | B2 | 110.6 | 116,314 | 22,468 | 138,782 | 17 | `Overweight` |
| After | A1 | 114.3 | 129,533 | 23,906 | 153,439 | 18 | `Hold` |
| After | A2 | 117.0 | 130,424 | 24,090 | 154,514 | 17 | `Overweight` |
| After | A3 | 111.8 | 115,820 | 21,403 | 137,223 | 17 | `Hold` |

Averages: input 115,613 → 125,259 (+8.3%), output 23,284 → 23,133 (−0.6%), total
138,897 → 148,392 (+6.8%), calls 16.5 → 17.3, wall clock 114.1 s → 114.4 s (+0.2%).
Two stalled runs were excluded and are reported as `INCOMPLETE`, not as slow completions.

The result that matters for interpretation is the shape of the change, not its size. Output
tokens and latency are flat; input tokens carry almost the whole delta. The pipeline therefore
did not become slower or more verbose in its answers, it began reading more per call: resolved
instrument context, portfolio context, expanded grounding prose in system prompts, and
structured-output schemas on bound calls. The after cohort also shows a wide spread — A3
consumed 13.7k fewer input tokens than A1 and A2 under an identical configuration — so a
single run would have supported almost any conclusion, including the wrong one. Reporting the
range and the number of excluded runs is the reason the delta can be read as a real change rather
than as noise (Henderson et al., 2018; Bouthillier et al., 2021).

Decision labels varied across identical configurations (`Overweight`, `Hold`, `Overweight`,
`Hold`) while the configuration and prompts were fixed. This is recorded as reproducibility
variance of the model, not as an effect of the code change; `REQ-TA-NFR-EVAL-001` rule 6 requires
exactly this separation, and treating label flips as a regression would have been a category
error.

### 4. Attribution

A separate diagnostic run (revision `98b82c9`, same configuration) attributed every model call
to its owning node: 16 calls, 122,324 input, 22,642 output, 144,966 total, 113.5 s. This run is
diagnostic and is excluded from the cohort averages by design.

The largest single consumer is the Market Analyst at 35,080 tokens (24.2%), followed by the
neutral risk debator (16,108), the bear researcher (14,876), the conservative debator (13,230),
the fundamentals analyst (11,128), the aggressive debator (10,376), the bull researcher
(10,367), the portfolio manager (9,191), the research manager (7,794), the news analyst (7,040),
the trader (6,981) and the sentiment analyst (2,795). Aggregated by stage, the analyst tool
loops account for 38.7%, the three risk debators for 27.4%, the researchers for 17.4%, and the
research manager, trader and portfolio manager together for 16.5%.

The mechanism behind the cost is visible inside the analyst tool loop: input per call grows
from 1,952 to 9,786 to 19,461 across successive rounds, because each round re-sends the
accumulated tool transcript to the model. Stage-level aggregation alone would have hidden this
quadratic behaviour, and the per-call trace is what allowed the team to target it.

One methodological defect surfaced here and is recorded rather than hidden: the graph labels
every react-agent call with the generic node name `agent`, so per-node attribution is only
possible by recovering the owner from the `checkpoint_ns` prefix. Any future attribution
figure produced without that recovery is unreliable.

### 5. Requirement feasibility

I assessed the cost and performance requirements against the code and answered A's two
question sets (`2026-11-23_20-10-00.md`, items D1–D12). Three conclusions changed the registry
or should change it:

1. `COST-002` (cumulative token admission) cannot be enforced in this semester's code without
   an estimation layer the run cannot defensibly provide. It was downgraded from `Must` to
   `Should` and restated as detection-only, recorded as decision D-4 in the registry entry.
2. `PERF-002` (time-budget handling) cannot meet a 2 s cancellation allowance. A cancelled
   call is not interruptible in flight — the two measured stalls each blocked for more than
   ten minutes with no timeout raised — so the allowance must describe a cooperative
   between-step check plus an explicit in-flight allowance, or the criterion is untestable.
3. `PERF-001`'s `RUN_TIME_CAP` must be fixed from measurement, as its own `open` field states.
   The observed maximum is 117.0 s with a minimum of 110.6 s across five completed runs, so a
   120 s cap has no margin and would fail on ordinary variance. A cap of 150 s with the
   measured spread recorded beside it is the defensible choice.

`COST-003` (early debate convergence) is stated in a form the current state cannot support:
only free-text `bull_history`/`bear_history` and a final rating exist, with no structured
per-round stance, so convergence cannot be detected deterministically. I recommended descoping
it rather than claiming a signal that does not exist.

### 6. Evaluation counting rules and open items

`REQ-TA-NFR-EVAL-001` defines completion rate over all runs started, quality scores over
`COMPLETED` runs only reported beside the completion rate, stop reasons for `INCOMPLETE` runs,
`N_EVAL` counting distinct cases rather than attempts, and refusal of undeclared multi-factor
comparisons. These rules exist because the naive alternative — reporting an average over
whatever runs happened to finish — silently deletes failures from the denominator, which is the
single most common defect in reported evaluation tables (Sculley et al., 2015).

Two obligations are still open and are mine, not the team's: the counting script named in the
registry's `open` field, and the rubric, critical items, evaluation profile and
`QUALITY_THRESHOLD`, which the registry assigns jointly to D and E. Until those exist, no
counting result is an acceptance result, and the registry says so explicitly.

### 7. Limitations

The measured cohort predates the current `main` (`761918e` at the time of writing). Two later
revisions matter: `aa3b02d` (perf: reduce repeated intermediate analysis context) and
`b091418` (opt-in per-run call budget, `call_cap`). The first changes exactly the quantity this
work measures — it adds the configuration key `concise_intermediate_reports`, defaulting to
`True` — so the after numbers describe `98b82c9` and must not be presented as properties of
the current tree. A run performed today with the same ticker, model and round counts is therefore
**not** the same configuration: one recorded key now differs, and under `REQ-TA-NFR-EVAL-001`
rule 6 that is a controlled change requiring the factor to be named, not a repeatability
comparison. The later `27f05f1` and `dc6f2ee` add population validation and legacy
export coverage and do not alter per-call context, so they do not invalidate the vintage
statement either way. The second change, `call_cap`, is opt-in and defaults to `None`, so it
leaves the measured cohort untouched while making any budgeted cohort non-comparable to it. The
second establishes that a formal budgeted cohort must freeze the same `call_cap` in its
evidence configuration; my cohort ran unbudgeted (`call_cap = None`), which is the correct
baseline state but is not comparable to any budgeted cohort.

Three further limits apply. Average latency, not a 20-run maximum, is what five runs can
establish, so `PERF-001` remains unproven by this evidence and is stated as a provisional
threshold. The stalled runs were observed on a different network path to the gateway than the
baseline, so their cause is recorded as infrastructure instability rather than as a code
defect, although the absence of a read timeout is a real code-level gap. Finally the attribution
run is a single run: the Pareto ordering is robust enough to direct design work, but the
individual percentages are not stable to the decimal.

**Change control.** The requirement entries cited above were read at `origin/main` `761918e`;
`docs/req/requirements.yaml` has been amended six times since the measured cohort. A quotation of
a priority, a status or a provisional threshold is therefore pinned to that revision, not to the
live file. If an entry changes again, the evidence does not become wrong — it becomes evidence
for a superseded statement, and the correct response is a dated note in the record rather than a
silent edit of the numbers.

### References

- Xiao, Y., Sun, E., Luo, D., & Wang, W. (2024). *TradingAgents: Multi-Agents LLM Financial
  Trading Framework.* arXiv:2412.20138.
- Henderson, P., Islam, R., Bachman, P., Pineau, J., Precup, D., & Meger, D. (2018). Deep
  reinforcement learning that matters. *Proceedings of AAAI-18*.
- Bouthillier, X., Delaunay, P., Bronzi, M., et al. (2021). Accounting for variance in machine
  learning benchmarks. *Proceedings of MLSys 2021*.
- Sculley, D., Holt, G., Golovin, D., et al. (2015). Hidden technical debt in machine learning
  systems. *Advances in Neural Information Processing Systems 28*.
- ACM (2020). *Artifact Review and Badging — Version 1.1.* Association for Computing Machinery.
- Team repository evidence: `kelepawuqiusi/CS5351@2c22ef9` and `@98b82c9`; requirement entries
  `REQ-TA-NFR-REPRO-001`, `PERF-001`, `PERF-002`, `COST-001`–`COST-003`, `EVAL-001` in
  `docs/req/requirements.yaml`; call-budget scope in `docs/code-governance/h1-call-budget.md`.


## Individual reflections

### Member A — supplied reflection

## Individual reflection — Member A

**CS5351 Software Engineering Project — requirements lead**

### What I did

My assignment was to decide the final requirement set for the portfolio-aware extension of TradingAgents v0.7.1 and to record each requirement with a stable identifier, a type, a priority and a criterion that someone else could actually test. I produced a registry of thirty-six active entries and three withdrawn identifiers, written as a schema-validated YAML file and generated by a script rather than edited by hand. I also wrote a validator with twenty-nine rules and a suite of thirty-one deliberately broken registry copies that each must fail, because a checker that has never been shown to reject anything is not evidence of anything.

### What I learned

The first thing I learned is that the checking apparatus is part of the deliverable. Three rounds of review by a teammate acting as an independent reviewer found defects in my requirements text, but the more serious findings were in my validator: a rule that inspected only structured fields and never the prose, so a citation to a requirement that did not exist passed indefinitely; and a rule that required *some* identifier to name an enforcer, which meant the previous author's habit of naming the nearest requirement could satisfy the check while being wrong. I had written those rules myself and they had all passed. I now treat an independent reviewer as a control, not a courtesy.

The second thing I learned was about the boundary of my own authority. Several times the honest answer was not a requirement but a question with a named owner: whether declining a portfolio prompt should prevent even reading the file, whether two CI gates become entries, whether the task profiles or the prose table defines the test population. Early on I resolved such points by picking the most plausible reading, and that produced a citation to a withdrawn GUI requirement as if it were the consent requirement. Recording the gap as an open question made the defect visible and was more useful to the team than a confident entry would have been.

### What I would do differently

I would have written the negative fixtures before the validator, not after. Almost every defect the reviewers found corresponds to a fixture I added only after being told. I also underestimated how much of the work is wording: a threshold stated as "about ninety per cent" survived three readings because it looked precise, and the correct figure was 94.51%, computed from the counts already in the document.

Finally, I am clear about what the artefact does not show. The registry status stayed `proposed_for_adoption`; twenty-six entries are proposed and ten partial, and none is implemented. A schema pass is not adoption and is not a test result. The value of the work is the apparatus and the register of what remains undecided, not the count of entries.

*(Word count, body only: approximately 420 words.)*


### Member B

Pending member-authored 300–500-word reflection and confirmed identity.

### Member C

Pending member-authored 300–500-word reflection and confirmed identity.

### Member D — supplied reflection

## Individual Reflection — Member D

My task looked simple at the start: run the system twice and report the numbers. It turned out
that almost none of the difficulty was in running it. The difficulty was deciding what a number
means, and refusing to report ones I could not defend.

The first thing I had to unlearn was trusting the interface. The CLI panel is convenient and it
was what I reached for first, but it reported 106.2k input tokens where the graph had actually
consumed 114.9k. If I had used the panel, an 8% increase would have looked like a 20% increase
and someone would have spent a week chasing a problem that did not exist. That single
discrepancy taught me to attach the counter to the computation rather than to the display, and
to state in the record which one I used.

The second lesson was about variance. Three runs under one frozen configuration produced
137.2k, 153.4k and 154.5k total tokens. One run would have let me tell any story I liked. I
reported the spread and the two stalled runs I excluded instead of quietly averaging them away,
because a number that hides its denominator is not evidence, it is decoration. A teammate can
disagree with my spread; they cannot recompute a number I never gave them.

The third lesson came from attribution. Grouping cost by stage told us roughly where the tokens
went, but only the per-call trace showed why: input inside the analyst loop grows from about
2k to 19k as each round re-sends the accumulated transcript. I also found that the graph labels
every agent call with the same generic node name, so the owner has to be recovered from the
checkpoint prefix. That was my own tooling being wrong, and I would have published a
misleading table if I had not checked it.

The last lesson was harder and more useful: measuring is a service, not a conclusion. Three of
the performance and cost requirements turned out to be unenforceable in this semester's code,
and one of them was mine to say so about. Telling the team that a requirement I had helped
write could not be met was less comfortable than reporting a clean average, but a cap that
fails on ordinary variance is worse than an honest provisional cap. I also learned to separate
a measurement defect from an infrastructure defect when two calls hung for ten minutes, because
the record has to be usable by someone who was not there.

What I would do differently: freeze and verify the measurement harness in its own reviewed
file before the first run, and repeat the attribution before quoting decimals. What I keep:
report the denominator, the exclusions and the range, every time.


### Member E — user-requested draft, author confirmation pending

Working on this project helped me develop both technical and teamwork skills. As the team leader, I was involved in coordinating tasks, integrating contributions, and checking whether the final system met the project requirements. Through this process, I learned that completing individual features is only one part of software engineering. Keeping requirements, implementation, tests, and evidence consistent is equally important.

One important lesson was how to break complex problems into smaller tasks. At first, issues such as report quality, token usage, and governance seemed closely connected and difficult to manage. I learned to separate them into specific problems, identify what evidence was needed, and verify each change before moving forward. This made the work easier to understand and reduced the risk of changing unrelated functionality.

I also learned to manage several tasks in parallel. For example, documentation could progress while tests were running, and integration work could continue while waiting for another member's clarification. However, parallel work required clear boundaries. Without them, different members or AI sessions could produce overlapping changes or use different versions of the same requirement.

Another valuable experience was using AI to automate development tasks. AI helped with code inspection, test generation, documentation, and repetitive checks. I became better at giving specific instructions, defining the scope of a task, and asking for verifiable results. I also learned that automation does not remove the need for human judgment. A passing test does not guarantee that a financial explanation is correct, and a reported token reduction does not automatically apply to every configuration. I needed to examine the evidence and communicate these limitations honestly.

There were also weaknesses in my leadership. I should have distributed tasks more evenly. Some responsibilities became concentrated in a small number of members, especially during integration. In future projects, I would agree on clearer ownership, review workloads regularly, and identify dependencies earlier.

Time management was another area for improvement. Too much integration and verification happened close to the deadline. This left less time for review, rehearsal, and unexpected problems. I should have set earlier internal deadlines and reserved a separate period for final testing and delivery.

Overall, this project taught me to approach software development as a coordinated process rather than a collection of coding tasks. In future teamwork, I will combine smaller, clearly defined tasks with more balanced delegation and earlier verification.

## Final assembly controls

Confirm names/IDs and relative contributions; supply B/C personal inputs; check five D5 submissions and collective pipeline coverage; bind verification to final SHA; resolve actual semantic/approval gaps honestly; count the final text (maximum 10,000 words) and render to verify more than 15 pages at 12-point single spacing. This draft does not claim those criteria are already met.
