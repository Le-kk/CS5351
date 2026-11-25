"""Per-run call admission; opt-in and independent of frozen input identity."""
from __future__ import annotations

from collections.abc import Callable
from contextvars import ContextVar
from dataclasses import dataclass
from threading import Condition
from typing import Any
from uuid import uuid4


class RunBudgetExhausted(Exception):
    """A required request was refused before transport dispatch."""


class BudgetProtocolError(Exception):
    """Invalid reservation lifecycle or unsupported metering route."""


@dataclass(frozen=True)
class Reservation:
    id: str
    controller_run_id: str


def budget_cause(exc: BaseException | None) -> RunBudgetExhausted | BudgetProtocolError | None:
    seen = set()
    while exc is not None and id(exc) not in seen:
        seen.add(id(exc))
        if isinstance(exc, (RunBudgetExhausted, BudgetProtocolError)):
            return exc
        exc = exc.__cause__ or exc.__context__
    return None


class RunBudgetController:
    def __init__(self, call_cap: int, run_id: str):
        if type(call_cap) is not int or call_cap < 0:
            raise ValueError("call_cap must be a non-negative integer")
        self.call_cap = call_cap
        self.run_id = run_id
        self._condition = Condition()
        self._states: dict[str, tuple[Reservation, str]] = {}
        self._denied = 0
        self._active = 0
        self._sealed = False
        self._resources: tuple[Any, Any, Callable] | None = None

    def reserve(self) -> Reservation:
        with self._condition:
            if self._sealed:
                raise BudgetProtocolError("Call budget is sealed")
            if len(self._states) >= self.call_cap:
                self._denied += 1
                raise RunBudgetExhausted(f"calls limit reached (call_cap={self.call_cap})")
            reservation = Reservation(uuid4().hex, self.run_id)
            self._states[reservation.id] = (reservation, "GRANTED")
            return reservation

    def _transition(self, reservation: Reservation, state: str) -> None:
        entry = self._states.get(reservation.id)
        if (reservation.controller_run_id != self.run_id or entry is None
                or entry[0] is not reservation or entry[1] != "GRANTED"):
            raise BudgetProtocolError("Reservation is foreign or already used")
        self._states[reservation.id] = (reservation, state)

    def dispatch(self, reservation: Reservation) -> None:
        with self._condition:
            if self._sealed:
                raise BudgetProtocolError("Call budget is sealed")
            self._transition(reservation, "CONSUMED")
            self._active += 1

    def invalidate(self, reservation: Reservation) -> None:
        with self._condition:
            if self._sealed:
                raise BudgetProtocolError("Call budget is sealed")
            self._transition(reservation, "INVALIDATED")

    def finish(self) -> None:
        with self._condition:
            if self._active <= 0:
                raise BudgetProtocolError("No active request to finish")
            self._active -= 1
            self._condition.notify_all()

    def resources(self, factory: Callable) -> tuple[Any, Any, Callable]:
        with self._condition:
            if self._resources is None:
                self._resources = factory()
            return self._resources

    def seal(self) -> dict:
        with self._condition:
            self._sealed = True
            self._states = {key: (res, "INVALIDATED" if state == "GRANTED" else state)
                            for key, (res, state) in self._states.items()}
            self._condition.wait_for(lambda: self._active == 0)
            return self.audit()

    def close(self) -> None:
        if self._resources:
            self._resources[2]()

    def audit(self) -> dict:
        with self._condition:
            states = [state for _, state in self._states.values()]
            return {"call_cap": self.call_cap, "granted": len(states),
                    "dispatched": states.count("CONSUMED"),
                    "invalidated": states.count("INVALIDATED"), "denied": self._denied}


def validate_budget_manifest(manifest: dict) -> None:
    """Recognize legacy Q1–Q4 or this budget-only format; fail closed."""
    if manifest.get("schema_version") == "1":
        if ("check_rules_version" in manifest or "run_budget" in manifest
                or manifest.get("stop_reason") == "BUDGET"):
            raise ValueError("Legacy manifest cannot contain budget/version extensions")
        return
    if type(manifest.get("schema_version")) is not int or manifest["schema_version"] != 2:
        raise ValueError("Unsupported or missing manifest schema_version")
    if type(manifest.get("check_rules_version")) is not int or manifest["check_rules_version"] != 1:
        raise ValueError("Unsupported check_rules_version")
    audit = manifest.get("run_budget")
    keys = {"call_cap", "granted", "dispatched", "invalidated", "denied"}
    if not isinstance(audit, dict) or set(audit) != keys:
        raise ValueError("Missing or invalid call budget audit")
    if any(type(audit[k]) is not int or audit[k] < 0 for k in keys):
        raise ValueError("Invalid call budget counter")
    if not (audit["dispatched"] + audit["invalidated"] == audit["granted"] <= audit["call_cap"]):
        raise ValueError("Inconsistent call budget accounting")
    config = manifest.get("effective_config")
    if not isinstance(config, dict) or type(config.get("call_cap")) is not int or config["call_cap"] != audit["call_cap"]:
        raise ValueError("Effective call_cap disagrees with audit")
    if manifest.get("stop_reason") == "BUDGET" and not audit["denied"]:
        raise ValueError("BUDGET requires a denied request")
    if audit["denied"] and (manifest.get("run_outcome") != "INCOMPLETE"
                           or manifest.get("stop_reason") not in {"BUDGET", "PERSISTENCE_ERROR"}):
        raise ValueError("Denied required request cannot be reported completed")


ACTIVE_BUDGET: ContextVar[RunBudgetController | None] = ContextVar("run_call_budget", default=None)
