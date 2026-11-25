"""Run-ID isolated, staged report/manifest publication with one commit point."""

from __future__ import annotations

import json
import os
import shutil
from contextlib import suppress
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path

from tradingagents.dataflows.symbols import safe_ticker_component

from .context import validate_run_id


@dataclass(frozen=True)
class PublishedArtifacts:
    run_dir: Path
    report_path: Path
    manifest_path: Path
    terminal_event_durable: bool


class PersistenceError(OSError):
    pass


def _build_terminal_row(event_sink, terminal_outcome: str) -> dict:
    """Build a terminal row for a sink that lacks the staging protocol.

    Uses the sink's own ``build_terminal`` when available; otherwise constructs a
    row from its public fields with a valid timestamp and the sink's redactor. It
    is written only into the staged events file, then emitted to the live sink
    after the rename succeeds.
    """
    builder = getattr(event_sink, "build_terminal", None)
    if builder is not None:
        return builder(terminal_outcome)
    now = datetime.now(UTC).isoformat().replace("+00:00", "Z")
    row = {"run_id": getattr(event_sink, "run_id", None),
           "ticker": getattr(event_sink, "ticker", None), "node": "output",
           "ts": now, "elapsed_ms": 0,
           "event": "run.terminal", "event_outcome": terminal_outcome}
    redactor = getattr(event_sink, "redactor", None)
    if redactor:
        row = redactor.scrub(row)
    return row


def _write_events(event_sink, path, terminal_row: dict) -> bool:
    """Write the staged events file, tolerating a legacy ``write_to(path)`` sink.

    A sink whose ``write_to`` accepts ``terminal_override`` writes the terminal in
    the staged file directly. A genuine old-signature sink does not; for it we
    write the sink's events, then append the terminal row to the staged file so
    ``terminal_event.durable=true`` is truthful. If that cannot be done the
    function reports ``False`` (non-durable), never a false success.
    """
    try:
        accepted = event_sink.write_to(path, terminal_override=terminal_row)
        return bool(accepted)
    except TypeError:
        pass
    if not event_sink.write_to(path):
        return False
    try:
        existing = path.read_text(encoding="utf-8") if path.exists() else ""
        marker = '"event": "run.terminal"'
        if marker not in existing:
            with path.open("a", encoding="utf-8") as handle:
                handle.write(json.dumps(terminal_row, ensure_ascii=False) + "\n")
        # Confirm the terminal is actually present in the staged file.
        text = path.read_text(encoding="utf-8")
        return any(json.loads(line).get("event") == "run.terminal"
                   for line in text.splitlines() if line.strip())
    except (OSError, json.JSONDecodeError, ValueError):
        return False


def publish_run(results_dir: str | Path, ticker: str, run_id: str,
                report_markdown: str, report_html: str | None,
                manifest: dict, event_sink, redactor, *, state_data: dict | None = None,
                message_log: str | None = None, terminal_outcome: str = "COMPLETED") -> PublishedArtifacts:
    safe_run_id = validate_run_id(run_id)
    root = Path(results_dir).resolve()
    safe_ticker = safe_ticker_component(ticker)
    staging_root = root / "_staging"
    final_dir = root / safe_ticker / safe_run_id
    staging_dir = staging_root / safe_run_id
    if not final_dir.resolve().is_relative_to(root) or not staging_dir.resolve().is_relative_to(root):
        raise ValueError("Run artifact paths must stay inside results_dir")
    staging_identity = None
    published = False
    try:
        staging_root.mkdir(parents=True, exist_ok=True)
        final_dir.parent.mkdir(parents=True, exist_ok=True)
        if final_dir.exists() or staging_dir.exists():
            raise FileExistsError("Run identifier already exists; refusing to overwrite artifacts.")
        staging_dir.mkdir()
        staging_identity = staging_dir.stat()
        reports = staging_dir / "reports"
        reports.mkdir()
        (reports / "complete_report.md").write_text(redactor.scrub(report_markdown), encoding="utf-8")
        if report_html is not None:
            (reports / "complete_report.html").write_text(redactor.scrub(report_html), encoding="utf-8")

        # These legacy-compatible sinks are deliberately best-effort and run-ID isolated.
        for filename, content in (("state.json", state_data), ("message_tool.log", message_log)):
            if content is None:
                continue
            try:
                destination = staging_dir / filename
                if filename.endswith(".json"):
                    destination.write_text(json.dumps(redactor.scrub(content), ensure_ascii=False,
                                                       sort_keys=True, indent=2) + "\n", encoding="utf-8")
                else:
                    destination.write_text(redactor.scrub(content), encoding="utf-8")
            except OSError:
                event_sink.emit("output", "output.persist", f"BEST_EFFORT_FAILED:{filename}")
        event_sink.emit("output", "output.persist", "STAGED")
        # The terminal is staged privately: the staged events.jsonl carries the
        # intended logical outcome, but the caller-visible sink only reveals it
        # after the critical commit below succeeds (R5).
        stage = getattr(event_sink, "stage_tentative_terminal", None)
        legacy_terminal = None
        if stage is not None:
            stage(terminal_outcome)
            terminal_durable = event_sink.write_to(staging_dir / "events.jsonl")
        else:
            # Legacy sink without staging: build the row for the staged file only;
            # it is emitted to the live sink after the rename succeeds.
            legacy_terminal = _build_terminal_row(event_sink, terminal_outcome)
            terminal_durable = _write_events(event_sink, staging_dir / "events.jsonl",
                                             legacy_terminal)
        safe_manifest = redactor.scrub({
            **manifest,
            "report_paths": {
                "markdown": "reports/complete_report.md",
                "html": "reports/complete_report.html" if report_html is not None else None,
            },
            "terminal_event": {"logical": "run.terminal", "durable": terminal_durable},
        })
        temporary_manifest = staging_dir / "manifest.json.tmp"
        temporary_manifest.write_text(
            json.dumps(safe_manifest, ensure_ascii=False, sort_keys=True, indent=2) + "\n",
            encoding="utf-8",
        )
        os.replace(temporary_manifest, staging_dir / "manifest.json")
        # Same-filesystem directory rename is the only publication action.
        if final_dir.exists():
            raise FileExistsError("Run directory appeared during publication; refusing overwrite.")
        os.rename(staging_dir, final_dir)
        published = True
        return PublishedArtifacts(final_dir, final_dir / "reports" / "complete_report.md",
                                  final_dir / "manifest.json", terminal_durable)
    except Exception as exc:
        # Only failures BEFORE the rename (nothing published) are critical.
        discard_terminal = getattr(event_sink, "discard_tentative_terminal", None)
        if discard_terminal is not None:
            discard_terminal()
        try:
            if (staging_identity is not None and not staging_dir.is_symlink()
                    and staging_dir.exists()
                    and os.path.samestat(staging_identity, staging_dir.stat())):
                shutil.rmtree(staging_dir)
        except OSError:
            pass
        if isinstance(exc, PersistenceError):
            raise
        raise PersistenceError("Could not publish the run artifacts.") from exc
    finally:
        # A caller-visible terminal reveal (``commit_terminal`` / legacy emit) is a
        # POST-commit sink callback: it runs only once the run is published and its
        # failure must not turn a successful, immutable publication into a
        # PERSISTENCE_ERROR. It is best-effort and cannot mutate the artifacts.
        if published:
            _reveal_terminal_after_commit(event_sink, legacy_terminal, terminal_outcome)


def _reveal_terminal_after_commit(event_sink, legacy_terminal, terminal_outcome):
    commit_terminal = getattr(event_sink, "commit_terminal", None)
    if commit_terminal is not None:
        with suppress(Exception):
            commit_terminal()
        return
    if legacy_terminal is not None:
        emit = getattr(event_sink, "emit", None)
        if emit is not None:
            with suppress(Exception):
                emit("output", "run.terminal", terminal_outcome)
