"""Durable per-attempt accounting for the GOV-004 replay harness (R3).

The runner used to accumulate outcomes in memory and write one evidence JSON
only after *every* selected case finished. A later abort (validation, execution
or serialization error) then discarded the record of cases already started, and
the next invocation's reuse check saw nothing -- so a formal slot could be
silently re-run.

This module makes each attempt durable on its own:

* :func:`preflight_slots` validates the whole selected cohort *before* dispatch:
  one planned slot per case/trial, not already started. Nothing runs on failure.
* :func:`claim_start` atomically appends a versioned ``STARTED`` record *before*
  the case is invoked; a reused run ID is refused (exclusive claim).
* :func:`record_outcome` writes the attempt's terminal outcome independently and
  atomically, so a later case's failure cannot erase an earlier start/outcome.
* :func:`ingest_starts` lets the scorer see retained, unresolved starts and
  count them as noncompleted rather than completed.

All writes go through a temp-file replace in the harness evidence directory and
are unique per run ID, so two starts within one second cannot overwrite.
"""

from __future__ import annotations

import contextlib
import json
import os
import tempfile
from pathlib import Path

try:  # POSIX file locking; the harness runs on Linux/macOS.
    import fcntl
except ImportError:  # pragma: no cover - non-POSIX fallback
    fcntl = None

STARTS_SCHEMA_VERSION = 2
STARTS_FILENAME = "gov004_starts.json"
LOCK_FILENAME = ".gov004_starts.lock"


class ReplayError(RuntimeError):
    """A preflight or claim failure that must stop the replay before dispatch."""


def _starts_path(evidence_root: str | Path) -> Path:
    return Path(evidence_root) / STARTS_FILENAME


@contextlib.contextmanager
def _exclusive_lock(evidence_root: str | Path):
    """A cross-process exclusive lock guarding the start-ledger read-modify-write.

    ``os.replace`` makes a single write atomic, but claim/update is a read, check,
    append and write; without mutual exclusion two processes that both read before
    either writes can both "succeed" while one record is lost. An OS advisory lock
    serialises those critical sections (bounded by the lock file). If no locking
    primitive is available the harness fails closed rather than risk double
    dispatch.
    """
    if fcntl is None:  # pragma: no cover - non-POSIX
        raise ReplayError("Cross-process locking unavailable; refusing exclusive claim")
    root = Path(evidence_root)
    root.mkdir(parents=True, exist_ok=True)
    lock_path = root / LOCK_FILENAME
    with open(lock_path, "a+", encoding="utf-8") as handle:
        try:
            fcntl.flock(handle.fileno(), fcntl.LOCK_EX)
            yield
        finally:
            with contextlib.suppress(OSError):
                fcntl.flock(handle.fileno(), fcntl.LOCK_UN)


def _read_json(path: Path, default):
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        return default


def _atomic_write(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, temporary = tempfile.mkstemp(prefix=path.name + ".", suffix=".tmp", dir=path.parent)
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as handle:
            handle.write(json.dumps(payload, indent=2, ensure_ascii=False) + "\n")
        os.replace(temporary, path)
    except BaseException:
        with contextlib.suppress(OSError):
            os.unlink(temporary)
        raise


def load_starts(evidence_root: str | Path) -> list[dict]:
    """The retained start records, or ``[]`` only when the ledger file is absent.

    A present-but-empty (``{}``), null, wrong-schema or malformed ledger fails
    closed rather than being treated as "no evidence" (R3-03). Every record's
    identity/status/timestamp is validated so starts are never silently dropped
    and no path can escape the evidence root.
    """
    path = _starts_path(evidence_root)
    if not path.exists():
        return []
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ReplayError("Start ledger is unreadable or malformed") from exc
    if not isinstance(data, dict) or data.get("kind") != "formal" \
            or data.get("schema_version") != STARTS_SCHEMA_VERSION:
        raise ReplayError("Unrecognised start-record schema; refuse to mix populations")
    starts = data.get("starts")
    if not isinstance(starts, list):
        raise ReplayError("Start record is malformed")
    seen = set()
    for record in starts:
        _validate_start_record(record, seen)
    return starts


def _validate_start_record(record, seen: set) -> None:
    from tradingagents.runapi.context import validate_run_id

    if not isinstance(record, dict):
        raise ReplayError("Start record entry must be an object")
    run_id = record.get("run_id")
    try:
        validate_run_id(run_id)
    except (ValueError, TypeError) as exc:
        raise ReplayError("Start record has an unsafe or missing run ID") from exc
    if run_id in seen:
        raise ReplayError("Duplicate run ID in the start ledger")
    seen.add(run_id)
    if not isinstance(record.get("case_id"), str) or not record["case_id"]:
        raise ReplayError("Start record lacks a case_id")
    if str(record.get("trial")) not in {"1", "2"}:
        raise ReplayError("Start record has an invalid trial")
    if record.get("status") not in {"STARTED", "RESOLVED"}:
        raise ReplayError("Start record has an invalid status")
    started = record.get("started_at_utc")
    if not isinstance(started, str) or not started.strip():
        raise ReplayError("Start record lacks a start timestamp")


def _save_starts(evidence_root: str | Path, starts: list[dict]) -> None:
    _atomic_write(_starts_path(evidence_root), {
        "kind": "formal", "schema_version": STARTS_SCHEMA_VERSION, "starts": starts,
    })


def _started_run_ids(evidence_root: str | Path) -> set[str]:
    ids = {s.get("run_id") for s in load_starts(evidence_root)}
    # Also treat any completed outcome file's run IDs as started (legacy evidence).
    for path in sorted(Path(evidence_root).glob("gov004_*.json")):
        if path.name in {STARTS_FILENAME, "gov004_scores.json"}:
            continue
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            continue
        for row in data.get("cases", []) if isinstance(data, dict) else []:
            if isinstance(row, dict) and row.get("run_id"):
                ids.add(row["run_id"])
    return ids - {None}


def preflight_slots(evidence_root: str | Path, planned: list[dict]) -> None:
    """Validate every selected slot before dispatch (R3-01, R3-04, R3-06).

    ``planned`` is a list of ``{case_id, run_id, trial}``. A missing/duplicate
    planned run ID, or one already started, raises :class:`ReplayError`; no case
    is executed and no start record is written on failure.
    """
    planned_ids = [slot.get("run_id") for slot in planned]
    if any(not isinstance(run_id, str) or not run_id for run_id in planned_ids):
        raise ReplayError("Every selected slot needs a declared run ID")
    if len(set(planned_ids)) != len(planned_ids):
        raise ReplayError("Duplicate planned run ID across selected slots")
    cells = [(slot.get("case_id"), str(slot.get("trial"))) for slot in planned]
    if len(set(cells)) != len(cells):
        raise ReplayError("Two selected slots share a case/trial")
    already = _started_run_ids(evidence_root) & set(planned_ids)
    if already:
        raise ReplayError(
            f"Cohort slot(s) already started; record retries separately: {sorted(already)}")


def claim_start(evidence_root: str | Path, *, case_id: str, run_id: str, trial: str,
                started_at_utc: str, model_config: dict | None = None,
                controls: dict | None = None) -> dict:
    """Persist a STARTED record before the case runs; refuse a reused run ID.

    The read-check-append-write is performed under an exclusive cross-process
    lock, so two concurrent callers cannot both claim the same or distinct IDs and
    lose a record (R3-02/R3-06). The trusted ``model_config``/``controls`` captured
    BEFORE dispatch are retained in the versioned start metadata so a pending
    start is not automatically ineligible for lacking a fixed configuration later.
    """
    from tradingagents.runapi.context import validate_run_id

    validate_run_id(run_id)
    with _exclusive_lock(evidence_root):
        starts = load_starts(evidence_root)
        if any(s.get("run_id") == run_id for s in starts):
            raise ReplayError(f"Run ID {run_id} was already claimed")
        record = {
            "case_id": case_id, "run_id": run_id, "trial": str(trial),
            "started_at_utc": started_at_utc, "status": "STARTED", "outcome": None,
            "model_config": dict(model_config or {}), "controls": dict(controls or {}),
        }
        starts.append(record)
        _save_starts(evidence_root, starts)
    return record


def record_outcome(evidence_root: str | Path, *, run_id: str, outcome: dict) -> Path:
    """Persist one attempt's outcome as its own uniquely named evidence file.

    The file is keyed by run ID (not a shared timestamp), so two attempts that
    begin in the same second never overwrite each other. The run ID is validated
    and confined to the evidence root before any IO; the attempt must be claimed
    with a matching case/trial, and an existing outcome may not be silently
    overwritten. The matching STARTED record is marked resolved under the same
    exclusive lock used by :func:`claim_start`.
    """
    from tradingagents.runapi.context import validate_run_id

    validate_run_id(run_id)
    if not isinstance(outcome, dict):
        raise ReplayError("Outcome must be a mapping")
    if outcome.get("run_id") not in (None, run_id):
        raise ReplayError("Outcome run_id conflicts with the claimed run ID")
    root = Path(evidence_root).resolve()
    evidence_path = (root / f"gov004_attempt_{run_id}.json").resolve()
    if not evidence_path.is_relative_to(root):
        raise ReplayError("Outcome path escapes the evidence root")
    with _exclusive_lock(evidence_root):
        starts = load_starts(evidence_root)
        claimed = next((s for s in starts if s.get("run_id") == run_id), None)
        if claimed is None:
            raise ReplayError(f"Outcome for unclaimed run ID {run_id}")
        if outcome.get("case_id") not in (None, claimed.get("case_id")):
            raise ReplayError("Outcome case_id conflicts with the claimed slot")
        if str(outcome.get("trial")) not in ("None", str(claimed.get("trial"))):
            raise ReplayError("Outcome trial conflicts with the claimed slot")
        if evidence_path.exists():
            raise ReplayError(f"Outcome for {run_id} was already recorded; refusing overwrite")
        _atomic_write(evidence_path, {
            "kind": "formal", "schema_version": STARTS_SCHEMA_VERSION, "cases": [outcome],
        })
        claimed["status"] = "RESOLVED"
        claimed["outcome"] = outcome.get("outcome")
        _save_starts(evidence_root, starts)
    return evidence_path


def dispatch_slots(evidence_root: str | Path, planned: list[dict], run_fn,
                   *, started_at_fn=None) -> list[dict]:
    """Preflight the whole cohort, then claim+run+record each slot durably (R3).

    ``planned`` is a list of ``{case_id, trial, run_id}`` (plus any opaque payload
    the caller's ``run_fn`` needs). Preflight runs before *any* dispatch. Each
    attempt is claimed before ``run_fn`` is called and its outcome recorded
    independently; an ordinary exception is caught and retained as a noncompleted
    start. ``KeyboardInterrupt``/``SystemExit`` stop subsequent dispatch after the
    current start/known outcome is preserved, then propagate.

    ``started_at_fn`` yields the actual per-start timestamp (defaults to now).
    """
    preflight_slots(evidence_root, planned)
    stamp_fn = started_at_fn or _utcnow
    records = []
    for slot in planned:
        claim_start(evidence_root, case_id=slot["case_id"], run_id=slot["run_id"],
                    trial=str(slot["trial"]), started_at_utc=stamp_fn(),
                    model_config=slot.get("model_config"), controls=slot.get("controls"))
        try:
            record = run_fn(slot)
        except (KeyboardInterrupt, SystemExit):
            # Preserve the start that is actually known, then stop dispatching.
            # The start remains unresolved; no application outcome is invented.
            raise
        except Exception as exc:  # ordinary harness failure: retain a noncompleted start
            record = _error_record(slot, exc)
            record_outcome(evidence_root, run_id=slot["run_id"], outcome=record)
            records.append(record)
            continue
        record.setdefault("trial", str(slot["trial"]))
        record_outcome(evidence_root, run_id=slot["run_id"], outcome=record)
        records.append(record)
        if record.get("stop_reason") == "INTERRUPTED":
            # An application-reported interruption is an operator stop: retain this
            # known attempt, then stop before any further (paid) dispatch.
            break
    return records


def _utcnow() -> str:
    from datetime import UTC, datetime

    return datetime.now(UTC).isoformat().replace("+00:00", "Z")


def _error_record(slot: dict, exc: BaseException) -> dict:
    """A noncompleted outcome record for an exception raised by the harness call.

    This is *harness* evidence (the case was attempted but the harness call
    failed); it is not a claim that the application itself returned INTERNAL_ERROR.
    """
    return {
        "case_id": slot["case_id"], "run_id": slot["run_id"],
        "trial": str(slot["trial"]), "outcome": "ERROR",
        "stop_reason": None, "final_rating": None,
        "output_check": None, "findings": [], "challenge_marker": None,
        "challenge_reached_model": None,
        "prompt_capture": {"model_calls": 0, "calls": []},
        "model_config": {}, "report_path": None, "manifest_path": None,
        "run_dir": None, "source_revision": None,
        "error": f"{type(exc).__name__}: harness failure",
        "harness_error": f"{type(exc).__name__}", "notes": [],
    }


def ingest_starts(evidence_root: str | Path) -> list[dict]:
    """Retained starts as scorer-ingestible noncompleted placeholders.

    The scorer must count every started slot in its denominator. A still-open
    (unresolved) start is exposed as ``outcome=ERROR`` with ``stop_reason=None``
    and ``harness_status="STARTED"`` -- it is *pending harness metadata*, not a
    fabricated COMPLETED result and not an invented application stop reason. A
    resolved start whose outcome file exists is counted via that file; a resolved
    start whose file is missing is surfaced here as noncompleted (never completed).
    """
    placeholders = []
    root = Path(evidence_root)
    for start in load_starts(evidence_root):
        resolved = start.get("status") == "RESOLVED"
        outcome_file = root / f"gov004_attempt_{start.get('run_id')}.json"
        has_file = resolved and outcome_file.is_file()
        if resolved and not has_file:
            error = "outcome file missing"
        elif not resolved:
            error = "start not resolved"
        else:
            error = None
        completed = has_file and start.get("outcome")
        placeholders.append({
            "case_id": start.get("case_id"),
            "run_id": start.get("run_id"),
            "trial": str(start.get("trial")),
            "outcome": start.get("outcome") if completed else "ERROR",
            "stop_reason": None,
            "final_rating": None, "output_check": None,
            "findings": [], "challenge_marker": None, "challenge_reached_model": None,
            "prompt_capture": {"model_calls": 0, "calls": []},
            "model_config": dict(start.get("model_config") or {}),
            "controls": dict(start.get("controls") or {}),
            "report_path": None, "manifest_path": None,
            "run_dir": None, "source_revision": None,
            "error": error,
            "harness_status": "RESOLVED" if has_file else "STARTED",
            "started_at_utc": start.get("started_at_utc"),
            "notes": ["retained start metadata; not a completed result"],
            "unresolved_start": not has_file,
        })
    return placeholders
