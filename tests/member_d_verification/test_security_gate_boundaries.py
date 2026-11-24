"""Negative security/permission probes; synthetic data only, no network."""
from __future__ import annotations

import importlib.util
import inspect
import json
import subprocess
import sys
from dataclasses import fields
from pathlib import Path
from unittest.mock import MagicMock

import pytest

ROOT = Path(__file__).resolve().parents[2]


def load_gate(name):
    spec = importlib.util.spec_from_file_location(name, ROOT / "scripts/ci" / f"{name}.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_committed_api_surface():
    import tradingagents.runapi as api
    from tradingagents.runapi.execution import run_analysis_api
    from tradingagents.runapi.result import RunResult
    contract = json.loads((ROOT / "docs/code-governance/public-api-contract.json").read_text())
    assert sorted(api.__all__) == contract["exports"]
    signature = inspect.signature(run_analysis_api)
    assert list(signature.parameters) == contract["parameters"]
    assert {name: param.kind.name for name, param in signature.parameters.items()} == contract["parameter_kinds"]
    assert {name: ("required" if param.default is inspect.Parameter.empty else repr(param.default))
            for name, param in signature.parameters.items()} == contract["parameter_defaults"]
    assert [f.name for f in fields(RunResult)] == contract["result_fields"]


def test_api_contract_changes_need_an_ai_log_update():
    gate = load_gate("check_ai_log_updated")
    assert gate.is_critical("docs/code-governance/public-api-contract.json")


def test_unconfirmed_input_has_zero_dispatch():
    from tradingagents.runapi.execution import run_analysis_api
    from tradingagents.runapi.input_service import freeze_no_portfolio
    factory = MagicMock(side_effect=AssertionError("must not dispatch before confirmation"))
    with pytest.raises(ValueError, match="confirmed"):
        run_analysis_api(freeze_no_portfolio("NVDA", "2026-01-09"), graph_factory=factory)
    factory.assert_not_called()


@pytest.mark.parametrize("url", ["file:///tmp/{ticker}", "https://evil.example/{ticker}", "http://api.stocktwits.com/{ticker}"])
def test_stocktwits_untrusted_initial_url_is_never_opened(monkeypatch, url):
    from tradingagents.dataflows.vendors import stocktwits
    monkeypatch.setattr(stocktwits, "_API", url)
    opener = MagicMock(side_effect=AssertionError("unsafe URL opened"))
    monkeypatch.setattr(stocktwits, "urlopen", opener)
    assert "URL rejected" in stocktwits.fetch_stocktwits_messages("NVDA")
    opener.assert_not_called()


@pytest.mark.parametrize("url", ["file:///tmp/{sub}", "https://evil.example/{sub}", "http://www.reddit.com/{sub}"])
def test_reddit_untrusted_initial_url_is_never_opened(monkeypatch, url):
    from tradingagents.dataflows.vendors import reddit
    monkeypatch.setattr(reddit, "_RSS", url)
    opener = MagicMock(side_effect=AssertionError("unsafe URL opened"))
    monkeypatch.setattr(reddit, "urlopen", opener)
    assert reddit._fetch_subreddit_rss("NVDA", "stocks", 5, 1) is None
    opener.assert_not_called()


def test_untrusted_xml_entity_is_rejected_without_crashing(monkeypatch):
    from tradingagents.dataflows.vendors import reddit
    response = MagicMock()
    response.__enter__.return_value = response
    response.read.return_value = b'<!DOCTYPE feed [<!ENTITY x "EXPANDED">]><feed>&x;</feed>'
    monkeypatch.setattr(reddit, "urlopen", MagicMock(return_value=response))
    assert reddit._fetch_subreddit_rss("NVDA", "stocks", 5, 1) is None


@pytest.mark.parametrize("case", ["pr_write", "head_checkout", "foreign_checkout", "shell_event", "implicit_permissions"])
def test_workflow_permission_negative_fixtures(case):
    gate = load_gate("check_workflow_permissions")
    doc = {"on": {"pull_request_target": {}}, "permissions": {"contents": "read", "checks": "write"},
           "jobs": {"test": {"steps": [{"uses": "actions/checkout@v7", "with": {"ref": "${{ github.event.repository.default_branch }}"}}]}}}
    if case == "pr_write":
        doc["on"] = {"pull_request": {}}
        doc["permissions"] = {"contents": "write"}
    elif case == "head_checkout":
        doc["jobs"]["test"]["steps"][0]["with"]["ref"] = "${{ github.event.pull_request.head.sha }}"
    elif case == "foreign_checkout":
        doc["jobs"]["test"]["steps"][0]["with"]["repository"] = "attacker/repo"
    elif case == "shell_event":
        doc["jobs"]["test"]["steps"].append({"run": "echo '${{ github.event.comment.body }}'"})
    else:
        doc.pop("permissions")
    assert gate.findings(doc, "fixture.yml")


def test_valid_workflow_permission_fixture():
    gate = load_gate("check_workflow_permissions")
    assert not gate.findings({"on": {"pull_request": {}}, "permissions": {"contents": "read"}, "jobs": {"test": {"steps": []}}}, "fixture.yml")


@pytest.mark.parametrize("defect", ["empty", "missing_file", "finding", "parse_error"])
def test_security_scan_requires_real_complete_report(tmp_path, defect):
    gate = load_gate("check_security_scan")
    path = tmp_path / "app.py"
    report = {"errors": [], "results": [], "metrics": {str(path): {}, "_totals": {}}}
    if defect == "empty":
        report = {}
    elif defect == "missing_file":
        report["metrics"] = {"_totals": {}}
    elif defect == "finding":
        report["results"] = [{"test_id": "B602"}]
    else:
        report["errors"] = [{"filename": str(path)}]
    assert gate.validate_report(report, {path})


def test_bandit_rejects_real_shell_injection_fixture(tmp_path):
    fixture = tmp_path / "unsafe.py"
    fixture.write_text('import subprocess\nsubprocess.run(input(), shell=True)\n')
    result = subprocess.run([sys.executable, "-m", "bandit", "-ll", "-f", "json", str(fixture)], capture_output=True, text=True, check=False, timeout=30)
    assert result.returncode != 0
    report = json.loads(result.stdout)
    assert any(r["test_id"] == "B602" for r in report["results"])


@pytest.mark.parametrize("comment", ["# nosec", "# nosec B602", "# nosec B310"])
def test_new_or_blanket_scanner_suppression_is_rejected(tmp_path, comment):
    gate = load_gate("check_security_scan")
    path = tmp_path / "app.py"
    path.write_text(f"print('fixture') {comment}\n")
    assert gate.nosec_findings({path}, tmp_path)
