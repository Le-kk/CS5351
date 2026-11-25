# Specification of a Portfolio-Aware Research System: Requirement Elicitation, Formal Registry Construction and Machine-Checkable Acceptance Criteria

**Member A — CS5351 Software Engineering Project**

---

## Abstract

This report documents Member A's contribution to the CS5351 project: the elicitation, structure, formalisation and machine-checking of the software requirements for a portfolio-aware extension of the TradingAgents research system (version 0.7.1). The work produced a version-controlled requirement registry comprising thirty-six active entries and three withdrawn identifiers, expressed in a schema-validated YAML artefact, together with a twenty-nine-rule validator and a thirty-two-case negative-fixture suite that empirically falsifies the validator's claims. The report sets out the elicitation method, the representation decisions (identifier stability, typed criteria, MoSCoW prioritisation, Given/When/Then fit criteria), the defect-detection regime, and an explicit account of what the artefact does and does not establish. A central methodological finding is that the validator itself is a claim requiring test: three successive external review rounds identified defects not only in the requirements text but in the checking apparatus, including a citation rule that could not resolve multi-segment identifiers and a parameter rule that could not see the names it purported to check. The report argues that requirements engineering for safety-adjacent systems must treat the verification tooling as part of the deliverable, and must distinguish conformance from adoption.

**Keywords:** requirements engineering; acceptance criteria; traceability; schema validation; negative testing; AI-assisted software development

---

## 1. Introduction

TradingAgents v0.7.1 is a multi-agent large-language-model system that produces equity research reports through a graph of specialised agents (market, news, social and fundamentals analysts; a bull/bear research debate; risk management; a portfolio manager). The system in its baseline form accepts no portfolio context, records no per-run provenance, and provides no deterministic guarantee that a delivered rating is machine-readable.

The CS5351 project extends this system with an optional portfolio input and an auditable reporting layer. Responsibility for the specification was allocated to Member A. The task as stated in the project brief was to decide which requirements form the final set, to record each with a stable identifier, a type, a MoSCoW priority and a testable fit criterion, and to produce a scope statement suitable for adoption by the team.

This report describes how that task was executed, using the IEEE 830 recommendation practice for software requirements specifications (IEEE, 1998) and the ISO/IEC/IEEE 29148 standard for requirements engineering (ISO/IEC/IEEE, 2018) as the reference vocabulary for structure, verifiability and traceability. It also reports, candidly, the defects in the work, because the requirement artefacts were subjected to three rounds of independent external review and every finding in those rounds was confirmed against the source materials.

Section 2 describes the elicitation method. Section 3 sets out the representation and the validator design. Section 4 reports the defect-detection regime and what it found. Section 5 discusses threats to validity and the limits of what the artefact establishes. Section 6 concludes.

## 2. Method

### 2.1 Elicitation

Requirements were elicited from four source classes, each recorded with a source reference in the registry so that a later reader can distinguish an observation from an inference:

1. **Course documentation.** The project brief and its gate specification named obligations (for example the AI-use log gate and the schema-validation gate) that the team had not yet expressed as requirements.
2. **Baseline code observation.** Each entry's `baseline` field records what the current code actually does, with file and symbol references, so that a requirement claiming a gap is distinguishable from one describing existing behaviour. For instance, `REQ-TA-FR-003` (checkpoint and resume) records that resume already works via per-node SQLite checkpoints, whereas `REQ-TA-FR-001` (evidence identifiers) records that nothing currently assigns such an identifier.
3. **Peer review.** Three rounds of external review by a team member acting as independent reviewer produced more usable defect reports than any self-check, and are treated in Section 4 as primary evidence.
4. **Open questions.** Where a decision belonged to another member (for example whether a CI gate becomes a registry entry, or whether declining a portfolio prompt should prevent even a local file read), the item was recorded as a numbered open question rather than resolved unilaterally.

This fourth mechanism proved the most important. A requirement set produced by one author will contain commitments that exceed that author's authority; recording them as explicit open questions with named owners preserves the information without fabricating a decision.

### 2.2 Conflict resolution

Baseline documents contained contradictions, the most consequential being a scope statement that excluded portfolio input while the test profiles required a portfolio to exist. Resolution followed a stated rule: the requirement text governs, superseded documents retain historical status, and any change to acceptance population belongs to the member who owns verification rather than to the requirements author.

### 2.3 What was deliberately not done

Where a decision exceeded A's authority, no entry was invented. Two such cases are recorded openly: the portfolio confirmation flow (no active entry owns the confirm/decline/EOF sequence, although the code emits an `input.consent` event) and the holdings-minimisation obligation (present only as an unregistered candidate). Both are carried as open questions with candidate identifiers, so that the gap is visible in the matrix instead of being concealed by citing an unrelated requirement.

## 3. Representation

### 3.1 Registry structure

The registry is a single YAML document validated against a JSON Schema (draft 2020-12) that constrains structure but not meaning. Each requirement carries an immutable identifier of the form `REQ-TA-<CLASS>-<NNN>`, a title, a type drawn from a controlled vocabulary mapped to ISO/IEC 25010 quality characteristics, a MoSCoW priority, a status, a normative statement, a Given/When/Then fit criterion, a trade-off statement, dependencies and source references.

Three representation decisions deserve justification:

**Identifier stability and non-reuse.** Withdrawn identifiers (`REQ-TA-FR-002`, `REQ-TA-NFR-SAFETY-001`, `REQ-TA-NFR-SAFETY-002`) are retained in a withdrawal list with reasons and may never be reassigned. This is required for traceability: a reader who searches for a withdrawn identifier must find a reason, not silence. A corollary is that numbering must not skip, because an absent number reads as a reserved or deleted requirement.

**Typed criteria rather than prose.** Every entry states a metric, a threshold and a verification method. Where a requirement is an invariant, the entry additionally names the code components that enforce it. This separation was forced by a review finding: an earlier version named a requirement as the enforcer when the actual enforcement was a service class, which is a category error rather than a citation error.

**Separation of proposal from adoption.** The document status remained `proposed_for_adoption` throughout. This is deliberate: a schema validation pass proves internal consistency, not team consent, and conflating the two is the requirements-engineering analogue of accepting a unit test as a user-acceptance test.

### 3.2 The validator as a first-class deliverable

Because the registry is generated from a script and checked by a validator, the validator's correctness is itself a requirement. The validator implements twenty-nine rules, including bidirectional reference resolution (every identifier cited in prose must resolve, and every declared parameter must actually be cited by exactly the entries that claim to use it), withdrawal preservation, MoSCoW ordering, and completeness of the Given/When/Then form.

## 4. Defect detection

### 4.1 Negative fixtures

A validator claim is worthless without a case that attempts to violate it. The project therefore maintains a negative-fixture harness in which each case asserts three properties: non-zero exit, exit for the stated reason, and absence of an unrelated failure such as a missing module or a traceback. Thirty-two cases are executed. The three-property assertion matters because a crash produces a non-zero exit code while proving nothing about the rule.

### 4.2 Findings across three review rounds

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

## 5. Discussion and threats to validity

**Construct validity.** A fit criterion is only as good as the measurement it names. Several criteria depend on quantities not yet measured (the token budget has no adopted figure and is recorded as `open`; the quality threshold is to be measured). Recording an unmeasured threshold as provisional is honest but does not constitute a testable requirement; this is a residual weakness.

**Internal validity.** Self-assessment was demonstrably unreliable. Every round of independent review found defects that the author's own checks had passed, including defects introduced while fixing the previous round. This supports treating independent review as a control, not a courtesy.

**External validity.** Thirty-two negative fixtures demonstrate that the validator rejects thirty-two specific defect classes. They do not demonstrate that no other defect class exists, and they cannot detect a well-formed but semantically wrong requirement; two such defects were found only by human reading.

**What the artefact does not establish.** The registry is not adopted. No implementation is claimed: twenty-six entries are `proposed` and ten `partial`. No acceptance test result is claimed by the author. The trace matrix assembled by Member E must not treat a schema pass as evidence of implementation.

## 6. Conclusion

The contribution is a requirement artefact whose value lies less in its thirty-six entries than in its supporting apparatus: an immutable identifier scheme, machine-checkable criteria, a validator whose failure modes are themselves tested, and an explicit register of what remains undecided and whose decision it is. The principal methodological lesson is that in AI-assisted requirements work the verification tooling must be reviewed as rigorously as the requirements, because a permissive checker silently converts defects into apparent compliance.

---

## References

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
