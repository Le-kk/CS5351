"""Typed results and errors for the shared run boundary."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Literal

InputErrorKind = Literal[
    "MALFORMED_JSON", "MISSING_POSITIONS", "MISSING_QUANTITY", "NONFINITE_NUMBER",
    "WRONG_SCALAR_TYPE", "UNREADABLE_PATH", "AS_OF_MISMATCH", "FLAG_CONFLICT",
]
InputModeValue = Literal["NO_PORTFOLIO", "PORTFOLIO_PROVIDED"]
StopReason = Literal[
    "MODEL_FAILURE", "DATA_FAILURE", "BUDGET", "INTERNAL_ERROR", "PERSISTENCE_ERROR", "INTERRUPTED",
]
OutputCheck = Literal["PASSED", "NEEDS_REVIEW", "NOT_RUN"]
RunOutcome = Literal["COMPLETED", "INCOMPLETE"]
Rating = Literal["Buy", "Overweight", "Hold", "Underweight", "Sell", "REVIEW"]


class InputError(ValueError):
    """Safe, structured input failure; detail must never contain file contents."""

    def __init__(self, kind: InputErrorKind, detail: str, basename: str | None = None,
                 field: str | None = None):
        self.kind = kind
        self.basename = basename
        self.field = field
        self.detail = detail
        super().__init__(detail)

    def as_dict(self) -> dict:
        return {"kind": self.kind, "basename": self.basename, "field": self.field,
                "detail": self.detail}


@dataclass(frozen=True)
class Finding:
    rule: Literal["Q1", "Q2", "Q3", "Q4", "R1", "R2", "R3", "R4", "R5", "R6", "R7", "R8", "CHECK_ERROR"]
    status: Literal["BLOCKING", "CORRECTED"] = "BLOCKING"
    detail: str = ""

    def __post_init__(self):
        if self.status not in ("BLOCKING", "CORRECTED"):
            raise ValueError("Unknown finding status")

    def as_dict(self) -> dict:
        return {"rule": self.rule, "status": self.status, "detail": self.detail}


@dataclass(frozen=True)
class CheckResult:
    output_check: OutputCheck
    findings: tuple[Finding, ...] = field(default_factory=tuple)

    def __post_init__(self):
        if self.output_check not in ("PASSED", "NEEDS_REVIEW", "NOT_RUN"):
            raise ValueError("Unknown output check status")
        blocking = any(f.status == "BLOCKING" for f in self.findings)
        if self.output_check == "PASSED" and blocking:
            raise ValueError("PASSED check cannot contain blocking findings")
        if self.output_check == "NEEDS_REVIEW" and not blocking:
            raise ValueError("NEEDS_REVIEW requires at least one blocking finding")
        if self.output_check == "NOT_RUN" and self.findings:
            raise ValueError("NOT_RUN cannot contain findings")

    def as_dict(self) -> dict:
        return {"output_check": self.output_check,
                "findings": [finding.as_dict() for finding in self.findings]}


@dataclass(frozen=True)
class RunResult:
    run_id: str
    ticker: str
    analysis_date: str
    input_mode: InputModeValue
    run_outcome: RunOutcome
    stop_reason: StopReason | None
    final_rating: Rating | None
    output_check: OutputCheck
    findings: tuple[Finding, ...] = field(default_factory=tuple)
    manifest_path: str | None = None
    report_path: str | None = None

    def __post_init__(self):
        if self.run_outcome == "COMPLETED":
            if self.final_rating is None or self.stop_reason is not None:
                raise ValueError("COMPLETED requires a rating and no stop reason")
            if self.output_check == "NOT_RUN":
                raise ValueError("COMPLETED cannot have NOT_RUN output check")
            CheckResult(self.output_check, self.findings)
            if self.final_rating == "REVIEW" and self.output_check != "NEEDS_REVIEW":
                raise ValueError("REVIEW requires NEEDS_REVIEW")
        else:
            if self.final_rating is not None or self.stop_reason is None:
                raise ValueError("INCOMPLETE requires no rating and a stop reason")
            if self.output_check != "NOT_RUN" or self.findings:
                raise ValueError("INCOMPLETE requires NOT_RUN and no findings")

    def as_dict(self) -> dict:
        return {
            "run_id": self.run_id, "ticker": self.ticker,
            "analysis_date": self.analysis_date, "input_mode": self.input_mode,
            "run_outcome": self.run_outcome, "stop_reason": self.stop_reason,
            "final_rating": self.final_rating, "output_check": self.output_check,
            "findings": [finding.as_dict() for finding in self.findings],
            "manifest_path": self.manifest_path, "report_path": self.report_path,
        }


@dataclass(frozen=True)
class RunRecord:
    """One evaluation attempt; kept outside the run manifest."""
    attempt_id: str
    category: Literal["STARTED", "PRE_RUN_REJECTED", "PRE_RUN_CANCELLED"]
    run_outcome: RunOutcome | None = None
    output_check: OutputCheck | None = None
    stop_reason: StopReason | None = None
    controlled_change: dict | None = None
    case_id: str | None = None
    population_id: str | None = None
    source_revision: str | None = None
    prompt_hash: str | None = None
    configuration_fingerprint: str | None = None


@dataclass(frozen=True)
class EvaluationPopulation:
    """Explicit single-configuration population, not an acceptance verdict.

    The caller freezes these controls before execution and binds every started
    record to them. This validates declarations, not signatures or human approval.
    Comparisons require a separate agreed design and are refused here.
    """
    population_id: str
    source_revision: str
    prompt_hash: str
    configuration_fingerprint: str
    case_ids: tuple[str, ...]

    def __post_init__(self):
        import re

        for value in (self.population_id, self.source_revision):
            if not isinstance(value, str) or not value.strip():
                raise ValueError("Population needs nonblank identity and revision")
        for value in (self.prompt_hash, self.configuration_fingerprint):
            if not isinstance(value, str) or not re.fullmatch(r"[0-9a-f]{64}", value):
                raise ValueError("Population controls require SHA-256 fingerprints")
        if (not isinstance(self.case_ids, tuple) or not self.case_ids or
                any(not isinstance(case, str) or not case.strip() for case in self.case_ids) or
                len(set(self.case_ids)) != len(self.case_ids)):
            raise ValueError("Population requires unique nonblank case identities")


def summarize_records(records: list[RunRecord], *,
                      population: EvaluationPopulation | None = None) -> dict:
    """Summarize one population, keeping case identity separate from attempts.

    Legacy attempts without a case ID cannot establish a distinct-case count.
    Never infer case IDs from attempt ID spelling. Without explicit frozen
    population controls the population count is unknown, not a validated one.
    """
    seen = set()
    for record in records:
        if not isinstance(record.attempt_id, str) or not record.attempt_id.strip():
            raise ValueError("Invalid attempt identity")
        if record.attempt_id in seen:
            raise ValueError("Duplicate attempt identity")
        seen.add(record.attempt_id)
        if record.category not in ("STARTED", "PRE_RUN_REJECTED", "PRE_RUN_CANCELLED"):
            raise ValueError("Unknown attempt category")
        case = getattr(record, "case_id", None)
        if case is not None and (not isinstance(case, str) or not case.strip()):
            raise ValueError("Invalid case identity")
    started = [r for r in records if r.category == "STARTED"]
    if population is not None:
        for record in started:
            if getattr(record, "case_id", None) not in population.case_ids:
                raise ValueError("Case outside frozen population")
            for name in ("population_id", "source_revision", "prompt_hash",
                         "configuration_fingerprint"):
                if getattr(record, name, None) != getattr(population, name):
                    raise ValueError("Mixed or unbound population controls")
            if record.controlled_change:
                raise ValueError("Comparison populations require a separate approved interface")
    completed = [r for r in started if r.run_outcome == "COMPLETED"]
    incomplete = [r for r in started if r.run_outcome == "INCOMPLETE"]
    reasons: dict[str, int] = {}
    for record in incomplete:
        if record.stop_reason:
            reasons[record.stop_reason] = reasons.get(record.stop_reason, 0) + 1
    review_count = sum(r.output_check == "NEEDS_REVIEW" for r in completed)
    case_ids = [getattr(r, "case_id", None) for r in started]
    return {
        "distinct_case_count": len(set(case_ids)) if case_ids and all(case_ids) else None,
        "population_result_count": (1 if population is not None else None) if started else 0,
        "status": "INSUFFICIENT_EVIDENCE" if not completed else "AVAILABLE",
        "started_count": len(started), "completed_count": len(completed),
        "completion_fraction": len(completed) / len(started) if started else None,
        "needs_review_count": review_count, "incomplete_reason_counts": reasons,
        "pre_run_rejected": sum(r.category == "PRE_RUN_REJECTED" for r in records),
        "pre_run_cancelled": sum(r.category == "PRE_RUN_CANCELLED" for r in records),
    }
