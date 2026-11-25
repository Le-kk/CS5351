"""Bounded JSONL lifecycle events; never accepts model or portfolio payloads."""

from __future__ import annotations

import json
import os
import time
from contextlib import suppress
from datetime import UTC, datetime
from pathlib import Path


class EventSink:
    def __init__(self, run_id: str, ticker: str, redactor=None):
        self.run_id = run_id
        self.ticker = ticker
        self.redactor = redactor
        self.started = time.monotonic()
        self.events: list[dict] = []
        self._terminal_added = False
        # Stage-private tentative terminal: built during publication and only
        # revealed to callers when the critical commit resolves (R5).
        self._tentative_terminal: dict | None = None

    def emit(self, node: str, event: str, event_outcome: str) -> dict:
        if node not in {"input", "engine", "output"}:
            raise ValueError("event node must be input, engine, or output")
        if event == "run.terminal":
            if self._terminal_added or self._tentative_terminal is not None:
                raise ValueError("only one terminal event may be recorded")
            self._terminal_added = True
        entry = {
            "run_id": self.run_id, "ticker": self.ticker, "node": node,
            "ts": datetime.now(UTC).isoformat().replace("+00:00", "Z"),
            "elapsed_ms": max(0, int((time.monotonic() - self.started) * 1000)),
            "event": event, "event_outcome": event_outcome,
        }
        if self.redactor:
            entry = self.redactor.scrub(entry)
        self.events.append(entry)
        return entry

    def build_terminal(self, event_outcome: str) -> dict:
        """Build (but do not record) a terminal event row for this sink."""
        entry = {
            "run_id": self.run_id, "ticker": self.ticker, "node": "output",
            "ts": datetime.now(UTC).isoformat().replace("+00:00", "Z"),
            "elapsed_ms": max(0, int((time.monotonic() - self.started) * 1000)),
            "event": "run.terminal", "event_outcome": event_outcome,
        }
        if self.redactor:
            entry = self.redactor.scrub(entry)
        return entry

    def stage_tentative_terminal(self, event_outcome: str) -> dict:
        """Build a caller-invisible terminal candidate for the staging commit.

        The candidate is included in any immediate ``write_to`` (so the staged
        ``events.jsonl`` carries the intended logical outcome), but it is not in
        ``self.events`` and so is not visible to a caller inspecting the sink.
        A later :meth:`commit_terminal` or :meth:`discard_tentative_terminal`
        resolves it; a caller cannot see a terminal it has not committed.
        """
        if self._terminal_added or self._tentative_terminal is not None:
            raise ValueError("only one terminal event may be recorded")
        entry = self.build_terminal(event_outcome)
        self._tentative_terminal = entry
        return entry

    def commit_terminal(self) -> dict:
        """Reveal the staged terminal to callers once publication succeeded."""
        if self._tentative_terminal is None:
            raise ValueError("no tentative terminal to commit")
        entry = self._tentative_terminal
        self._tentative_terminal = None
        # Mark the single-terminal state so a later emit/stage cannot add a second.
        self._terminal_added = True
        self.events.append(entry)
        return entry

    def discard_tentative_terminal(self) -> None:
        """Drop the staged terminal after a failed publication (R5)."""
        self._tentative_terminal = None

    def _terminal_for_write(self) -> dict | None:
        return self._tentative_terminal

    def write_to(self, path: Path, *, terminal_override: dict | None = None) -> bool:
        temporary = path.with_name(path.name + ".tmp")
        staged = terminal_override if terminal_override is not None else self._terminal_for_write()
        try:
            temporary.write_text("".join(json.dumps(event, ensure_ascii=False) + "\n"
                                               for event in [*self.events, *([staged] if staged else [])]),
                                 encoding="utf-8")
            os.replace(temporary, path)
            return True
        except OSError:
            with suppress(OSError):
                temporary.unlink(missing_ok=True)
            return False
