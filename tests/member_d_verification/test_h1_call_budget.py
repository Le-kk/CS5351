"""H1: real SDK requests, without network, obey one per-run admission budget."""
from __future__ import annotations

import asyncio
import json
import threading
from concurrent.futures import ThreadPoolExecutor
from contextlib import nullcontext, suppress
from types import SimpleNamespace
from typing import get_args

import pytest
from openai import InternalServerError
from pydantic import BaseModel

from tradingagents.llm_clients import budget_transport as wire_module
from tradingagents.llm_clients.factory import create_tier_client
from tradingagents.runapi.budget import (
    ACTIVE_BUDGET,
    BudgetProtocolError,
    RunBudgetController,
    RunBudgetExhausted,
    budget_cause,
    validate_budget_manifest,
)
from tradingagents.runapi.execution import run_analysis_api
from tradingagents.runapi.input_service import freeze_no_portfolio
from tradingagents.runapi.result import StopReason

STATE = {"final_rating": "Hold", "final_trade_decision": "Rating: Hold"}


def configuration(cap=2, provider="openai_compatible"):
    return {"call_cap": cap, "llm_provider": provider,
            "backend_url": "https://example.test/v1", "quick_think_llm": "deepseek-v4-flash",
            "deep_think_llm": "deepseek-v4-flash", "llm_max_retries": 7}


@pytest.fixture
def wire(monkeypatch):
    requests = []

    def response(request):
        payload = json.loads(request.content)
        requests.append(payload)
        message = {"role": "assistant", "content": "Rating: Hold"}
        if payload.get("tools"):
            name = payload["tools"][0]["function"]["name"]
            message["tool_calls"] = [{"id": "fixture-call", "type": "function",
                                      "function": {"name": name, "arguments": '{"rating":"Hold"}'}}]
        return wire_module.http.Response(200, json={"id": "fixture", "object": "chat.completion",
            "model": "deepseek-v4-flash", "choices": [{"index": 0, "message": message,
            "finish_reason": "tool_calls" if payload.get("tools") else "stop"}],
            "usage": {"prompt_tokens": 2, "completion_tokens": 1, "total_tokens": 3}})

    original = wire_module.BudgetTransport
    monkeypatch.setattr(wire_module, "BudgetTransport",
                        lambda budget: original(budget, wire_module.http.MockTransport(response)))
    return requests


def llm(budget, provider="openai_compatible"):
    cfg = configuration(budget.call_cap, provider)
    token = ACTIVE_BUDGET.set(budget)
    try:
        return create_tier_client(cfg, "quick").get_llm()
    finally:
        ACTIVE_BUDGET.reset(token)


def test_six_stop_reasons():
    assert set(get_args(StopReason)) == {"MODEL_FAILURE", "DATA_FAILURE", "BUDGET",
                                         "INTERNAL_ERROR", "PERSISTENCE_ERROR", "INTERRUPTED"}


def test_atomic_last_slot_and_run_isolation():
    budget = RunBudgetController(8, "first")
    for _ in range(7):
        budget.invalidate(budget.reserve())
    barrier = threading.Barrier(4)

    def attempt(_):
        barrier.wait()
        try:
            return budget.reserve()
        except RunBudgetExhausted:
            return None

    with ThreadPoolExecutor(max_workers=4) as pool:
        results = list(pool.map(attempt, range(4)))
    assert sum(x is not None for x in results) == 1
    assert budget.audit()["granted"] == 8
    assert budget.audit()["denied"] == 3
    other = RunBudgetController(1, "second")
    assert other.reserve().controller_run_id == "second"


def test_invalidated_grant_not_refunded_and_tokens_not_forgeable():
    budget = RunBudgetController(1, "first")
    ticket = budget.reserve()
    other = RunBudgetController(1, "second")
    with pytest.raises(BudgetProtocolError):
        other.dispatch(ticket)
    budget.invalidate(ticket)
    with pytest.raises(BudgetProtocolError):
        budget.dispatch(ticket)
    with pytest.raises(RunBudgetExhausted):
        budget.reserve()
    assert budget.audit() == {"call_cap": 1, "granted": 1, "dispatched": 0, "invalidated": 1, "denied": 1}


def test_consumption_reuse_rejected_and_seal_waits_for_inflight():
    budget = RunBudgetController(1, "run")
    ticket = budget.reserve()
    budget.dispatch(ticket)
    with pytest.raises(BudgetProtocolError):
        budget.dispatch(ticket)
    with ThreadPoolExecutor(max_workers=1) as pool:
        sealed = pool.submit(budget.seal)
        assert not sealed.done()
        budget.finish()
        assert sealed.result(timeout=2)["dispatched"] == 1
    with pytest.raises(BudgetProtocolError):
        budget.reserve()


class Decision(BaseModel):
    rating: str


@pytest.mark.parametrize("provider", ["deepseek", "openai_compatible"])
@pytest.mark.parametrize("mode", ["plain", "tools", "structured"])
def test_native_bound_routes_count_once_and_exact_cap_can_complete(wire, mode, provider, monkeypatch):
    monkeypatch.setenv("DEEPSEEK_API_KEY", "synthetic-fixture-key")
    budget = RunBudgetController(1, "run")
    model = llm(budget, provider)
    assert model.max_retries == 0
    runnable = model
    if mode == "tools":
        runnable = model.bind_tools([{"type": "function", "function": {
            "name": "Decision", "parameters": Decision.model_json_schema()}}])
    elif mode == "structured":
        runnable = model.with_structured_output(Decision)
    runnable.invoke("synthetic")
    assert len(wire) == budget.audit()["dispatched"] == 1
    assert budget.audit()["denied"] == 0
    with pytest.raises(Exception) as raised:
        runnable.invoke("synthetic next")
    assert isinstance(budget_cause(raised.value), RunBudgetExhausted)
    assert len(wire) == 1
    budget.seal()
    budget.close()


def test_structured_refusal_is_not_swallowed_by_free_text_fallback(wire):
    from tradingagents.agents.structured import invoke_structured_or_freetext
    budget = RunBudgetController(0, "run")
    model = llm(budget)
    with pytest.raises(RunBudgetExhausted):
        invoke_structured_or_freetext(model.with_structured_output(Decision), model,
                                     "synthetic", lambda x: x.rating, "fixture")
    assert wire == []
    assert budget.audit()["denied"] == 1
    budget.seal()
    budget.close()


def test_async_is_explicitly_rejected_without_an_unmetered_request(wire):
    budget = RunBudgetController(1, "run")
    model = llm(budget)
    with pytest.raises(Exception) as raised:
        asyncio.run(model.ainvoke("synthetic"))
    assert isinstance(budget_cause(raised.value), BudgetProtocolError)
    assert wire == []
    budget.seal()
    budget.close()


@pytest.mark.parametrize("count,cap,reason", [(2, 2, None), (3, 2, "BUDGET"), (1, 0, "BUDGET")])
def test_api_tiers_share_budget_publish_and_keep_legacy_checks(tmp_path, wire, count, cap, reason):
    config = {**configuration(cap), "results_dir": str(tmp_path)}

    def factory(selected_analysts, config, callbacks):
        return SimpleNamespace(quick=create_tier_client(config, "quick").get_llm(),
                               deep=create_tier_client(config, "deep").get_llm())

    def runner(graph, context):
        for i in range(count):
            (graph.quick if i % 2 else graph.deep).invoke("synthetic")
        return STATE

    result = run_analysis_api(freeze_no_portfolio("AAPL", "2026-01-09").confirm(),
                              config=config, graph_factory=factory, engine_runner=runner)
    assert result.stop_reason == reason
    assert len(wire) == min(count, cap)
    manifest = json.loads(__import__("pathlib").Path(result.manifest_path).read_text())
    validate_budget_manifest(manifest)
    assert manifest["schema_version"] == 2 and manifest["check_rules_version"] == 1
    assert manifest["run_budget"]["dispatched"] == len(wire)
    if reason:
        assert result.run_outcome == "INCOMPLETE" and result.final_rating is None
        assert result.output_check == "NOT_RUN" and result.findings == ()
    else:
        assert result.run_outcome == "COMPLETED" and result.output_check == "PASSED"


def test_swallowed_budget_refusal_still_stops_public_result(tmp_path):
    def runner(graph, context):
        with suppress(RunBudgetExhausted):
            graph.reserve()
        return STATE
    result = run_analysis_api(freeze_no_portfolio("AAPL", "2026-01-09").confirm(),
        config={"call_cap": 0, "results_dir": str(tmp_path)},
        graph_factory=lambda **kw: ACTIVE_BUDGET.get(), engine_runner=runner)
    assert result.stop_reason == "BUDGET"


def test_budget_stop_plus_publication_failure_keeps_primary_and_secondary(tmp_path, monkeypatch, caplog):
    from tradingagents.runapi import execution
    from tradingagents.runapi.events import EventSink
    from tradingagents.runapi.persist import PersistenceError
    context = freeze_no_portfolio("AAPL", "2026-01-09").confirm()
    sink = EventSink(context.run_id, context.ticker)
    monkeypatch.setattr(execution, "publish_run", lambda *a, **kw: (_ for _ in ()).throw(PersistenceError("fixture")))
    result = run_analysis_api(context, config={"call_cap": 0, "results_dir": str(tmp_path)}, event_sink=sink,
        graph_factory=lambda **kw: ACTIVE_BUDGET.get(),
        engine_runner=lambda graph, context: graph.reserve())
    assert result.stop_reason == "PERSISTENCE_ERROR"
    assert "secondary stop cause: BUDGET" in caplog.text
    assert sum(x["event"] == "run.terminal" for x in sink.events) == 1


def test_memory_reflection_and_graph_step_preserve_budget_exception(monkeypatch):
    from tradingagents.graph.trading_graph import TradingAgentsGraph
    from tradingagents.memory import settlement
    monkeypatch.setattr(settlement, "fetch_returns", lambda *a, **kw: (1, 1, 5, "2026-01-09"))
    memory = SimpleNamespace(settling=lambda **kw: nullcontext(True),
        get_pending_entries=lambda: [{"ticker": "AAPL", "date": "2026-01-01"}])
    def refuse(**kwargs):
        raise RunBudgetExhausted("calls limit")
    reflector = SimpleNamespace(reflect_on_final_decision=refuse)
    with pytest.raises(RunBudgetExhausted):
        settlement.settle_pending("AAPL", memory, reflector, {})
    graph = object.__new__(TradingAgentsGraph)
    graph.settle_all_pending = lambda **kw: refuse()
    with pytest.raises(RunBudgetExhausted):
        graph._memory_step({})


@pytest.mark.parametrize("value", [-1, True, 1.5, "bad"])
def test_invalid_cap_rejected(value):
    with pytest.raises(ValueError):
        RunBudgetController(value, "run")


def test_unsupported_provider_and_raw_boundary_fail_before_dispatch():
    with pytest.raises(ValueError, match="shared"):
        create_tier_client(configuration(), "quick")
    config = configuration()
    config.update(llm_provider="google")
    token = ACTIVE_BUDGET.set(RunBudgetController(1, "run"))
    try:
        with pytest.raises(ValueError, match="supports"):
            create_tier_client(config, "quick")
    finally:
        ACTIVE_BUDGET.reset(token)


@pytest.mark.parametrize("mutation", ["version", "rules", "counter", "refund", "missing", "legacy_budget"])
def test_manifest_reader_rejects_unknown_or_inconsistent_budget(mutation):
    manifest = {"schema_version": 2, "check_rules_version": 1, "run_outcome": "INCOMPLETE", "stop_reason": "BUDGET",
                "effective_config": {"call_cap": 1},
                "run_budget": {"call_cap": 1, "granted": 1, "dispatched": 1, "invalidated": 0, "denied": 1}}
    if mutation == "version":
        manifest["schema_version"] = 3
    elif mutation == "rules":
        manifest["check_rules_version"] = 2
    elif mutation == "counter":
        manifest["run_budget"]["denied"] = True
    elif mutation == "refund":
        manifest["run_budget"]["granted"] = 0
    elif mutation == "missing":
        manifest.pop("run_budget")
    else:
        manifest = {"schema_version": "1", "stop_reason": "BUDGET"}
    with pytest.raises(ValueError):
        validate_budget_manifest(manifest)


def test_sdk_error_has_no_hidden_retry_even_if_config_requested_seven(monkeypatch):
    sent = []
    original = wire_module.BudgetTransport
    def server_error(request):
        sent.append(request)
        return wire_module.http.Response(500, json={"error": {"message": "synthetic", "type": "server_error"}})
    monkeypatch.setattr(wire_module, "BudgetTransport", lambda b: original(b, wire_module.http.MockTransport(server_error)))
    budget = RunBudgetController(1, "run")
    model = llm(budget)
    with pytest.raises(InternalServerError):
        model.invoke("synthetic")
    assert len(sent) == 1
    with pytest.raises(Exception) as raised:
        model.invoke("application retry")
    assert isinstance(budget_cause(raised.value), RunBudgetExhausted)
    assert len(sent) == budget.audit()["dispatched"] == 1
    budget.seal()
    budget.close()


def test_actual_reflector_uses_the_same_metered_model(wire):
    from tradingagents.memory.reflection import Reflector
    budget = RunBudgetController(1, "run")
    reflector = Reflector(llm(budget))
    args = {"final_decision": "Hold", "raw_return": 0.1, "alpha_return": 0.1, "benchmark_name": "SPY", "holding_days": 5}
    reflector.reflect_on_final_decision(**args)
    with pytest.raises(Exception) as raised:
        reflector.reflect_on_final_decision(**args)
    assert isinstance(budget_cause(raised.value), RunBudgetExhausted)
    assert len(wire) == budget.audit()["dispatched"] == 1
    budget.seal()
    budget.close()


def test_concurrent_api_runs_have_isolated_caps(tmp_path, wire):
    def run_one(_):
        def factory(**kw):
            return create_tier_client(kw["config"], "quick").get_llm()
        def runner(model, context):
            model.invoke("synthetic")
            return STATE
        return run_analysis_api(freeze_no_portfolio("AAPL", "2026-01-09").confirm(),
            config={**configuration(1), "results_dir": str(tmp_path)}, graph_factory=factory, engine_runner=runner)
    with ThreadPoolExecutor(max_workers=2) as pool:
        results = list(pool.map(run_one, range(2)))
    assert len(wire) == 2
    assert all(x.run_outcome == "COMPLETED" for x in results)
    assert results[0].run_id != results[1].run_id
    assert ACTIVE_BUDGET.get() is None


def test_disabled_budget_keeps_legacy_artifact_format(tmp_path):
    result = run_analysis_api(freeze_no_portfolio("AAPL", "2026-01-09").confirm(),
        config={"results_dir": str(tmp_path)}, graph_factory=lambda **kw: object(), engine_runner=lambda *a: STATE)
    manifest = json.loads(__import__("pathlib").Path(result.manifest_path).read_text())
    assert result.run_outcome == "COMPLETED"
    assert manifest["schema_version"] == "1"
    assert "run_budget" not in manifest and "check_rules_version" not in manifest
    assert "call_cap" not in manifest["effective_config"]
    validate_budget_manifest(manifest)


def test_budget_metadata_cannot_claim_a_different_effective_cap():
    manifest = {"schema_version": 2, "check_rules_version": 1, "run_outcome": "COMPLETED", "stop_reason": None,
        "effective_config": {"call_cap": 1},
        "run_budget": {"call_cap": 1, "granted": 1, "dispatched": 1, "invalidated": 0, "denied": 0}}
    validate_budget_manifest(manifest)
    manifest["effective_config"]["call_cap"] = 99
    with pytest.raises(ValueError, match="disagrees"):
        validate_budget_manifest(manifest)


@pytest.mark.parametrize("missing_cap", [False, True])
def test_formal_scorer_reads_budget_manifest_only_with_frozen_cap(tmp_path, monkeypatch, missing_cap):
    import hashlib
    from pathlib import Path

    from tests.member_b_remediation.test_r2_scorer_correspondence import _load_helper

    helper = _load_helper()
    root = tmp_path / "evidence"
    scorer = helper._fresh_scorer(root, monkeypatch)
    rows = []
    for case in helper.FIXED_CASES:
        marker = helper.CHALLENGE_MARKERS.get(case)
        for label in ("a", "b"):
            row = helper._make_run(root, case, f"{case}-{label}", challenge_marker=marker,
                                   challenge_reached=True if marker else None)
            path = Path(row["manifest_path"])
            manifest = json.loads(path.read_text())
            manifest.update(schema_version=2, check_rules_version=1,
                            run_budget={"call_cap": 2, "granted": 1, "dispatched": 1, "invalidated": 0, "denied": 0})
            manifest["effective_config"]["call_cap"] = 2
            path.write_text(json.dumps(manifest), encoding="utf-8")
            row["model_config"]["call_cap"] = 2
            row["manifest_sha256"] = hashlib.sha256(path.read_bytes()).hexdigest()
            rows.append(row)
    helper._write_evidence(root, "1", rows)
    cohort_path = root / "cohort.json"
    cohort = json.loads(cohort_path.read_text())
    if not missing_cap:
        cohort["call_cap"] = 2
    cohort_path.write_text(json.dumps(cohort), encoding="utf-8")
    scores = root / "gov004_scores.json"
    helper._scores_all_pass(scores, [r["run_id"] for r in rows])
    # Synthetic scorer fixtures only: not human semantic acceptance.
    assert scorer.main(["score", str(scores)]) == (1 if missing_cap else 0)


def test_default_graph_factory_wires_budget_without_copying_locks_into_config(tmp_path, wire):
    from tradingagents.default_config import DEFAULT_CONFIG
    config = {**DEFAULT_CONFIG, **configuration(1), "results_dir": str(tmp_path / "results"),
              "data_cache_dir": str(tmp_path / "cache"), "memory_log_path": str(tmp_path / "memory.md"),
              "checkpoint_enabled": False}
    def runner(graph, context):
        # Uses the real default graph constructor, clients, tool binding and memory wiring.
        # Scripted runner avoids live data/model evaluation.
        graph.quick_thinking_llm.invoke("synthetic")
        assert "_run_budget_controller" not in graph.config
        return STATE
    result = run_analysis_api(freeze_no_portfolio("AAPL", "2026-01-09").confirm(),
        config=config, selected_analysts=["market"], engine_runner=runner)
    assert result.run_outcome == "COMPLETED"
    assert len(wire) == 1
