"""Acceptance probes for REQ-TA-GOV-004; all fixtures use temporary copies."""
from __future__ import annotations

import importlib.util
import subprocess
import sys
from pathlib import Path

import pytest
import yaml

ROOT = Path(__file__).resolve().parents[3]
GATE = ROOT / "scripts/ci/check_requirement_schema.py"
REGISTRY = ROOT / "docs/req/requirements.yaml"
SCHEMA = ROOT / "docs/req/req-schema.json"
VALIDATOR = ROOT / "docs/req/validate.py"


def run_gate(registry=REGISTRY, schema=SCHEMA, validator=VALIDATOR, cwd=None):
    return subprocess.run(
        [sys.executable, str(GATE), "--registry", str(registry), "--schema", str(schema), "--validator", str(validator)],
        capture_output=True, text=True, check=False, cwd=cwd,
    )


def assert_blocked(result, name):
    assert result.returncode != 0
    findings = [line for line in result.stdout.splitlines() if line.startswith("FAIL ")]
    assert len(findings) == 1, result.stdout + result.stderr
    assert name in findings[0]
    assert "PASS requirements schema" not in result.stdout


def write_fixture(tmp_path, mutate):
    doc = yaml.safe_load(REGISTRY.read_text())
    mutate(doc)
    path = tmp_path / "registry.yaml"
    path.write_text(yaml.safe_dump(doc, allow_unicode=True, sort_keys=False))
    return path


def test_current_registry_passes_from_another_working_directory(tmp_path):
    result = run_gate(cwd=tmp_path)
    assert result.returncode == 0, result.stdout + result.stderr
    assert "PASS requirements schema" in result.stdout


@pytest.mark.parametrize("case", ["missing_key", "invalid_priority", "missing_schema", "invalid_yaml", "validator_raises"])
def test_five_required_negative_fixtures(tmp_path, case):
    registry, schema, validator = REGISTRY, SCHEMA, VALIDATOR
    expected = "REQ_VALIDATION_FAILED"
    if case == "missing_key":
        registry = write_fixture(tmp_path, lambda d: d.pop("requirements"))
    elif case == "invalid_priority":
        registry = write_fixture(tmp_path, lambda d: d["requirements"][0].update(priority="Essential"))
    elif case == "missing_schema":
        schema = tmp_path / "missing.json"
        expected = "REQ_SCHEMA_MISSING"
    elif case == "invalid_yaml":
        registry = tmp_path / "broken.yaml"
        registry.write_text("requirements: [\n")
    else:
        validator = tmp_path / "raises.py"
        validator.write_text("raise RuntimeError('planted validator execution failure')\n")
        expected = "REQ_VALIDATOR_ERROR"
    assert_blocked(run_gate(registry, schema, validator), expected)


def test_schema_valid_but_cross_record_invalid_still_fails(tmp_path):
    def duplicate(d):
        d["requirements"].append(d["requirements"][0].copy())
    registry = write_fixture(tmp_path, duplicate)
    assert_blocked(run_gate(registry), "REQ_VALIDATION_FAILED")


@pytest.mark.parametrize("kind", ["registry", "validator", "schema_json", "schema_definition", "duplicate_yaml", "empty_output", "zero_errors_bad_exit", "empty_registry_summary"])
def test_incomplete_or_broken_audits_fail_closed(tmp_path, kind):
    registry, schema, validator = REGISTRY, SCHEMA, VALIDATOR
    expected = "REQ_VALIDATOR_ERROR"
    if kind == "registry":
        registry = tmp_path / "missing.yaml"
        expected = "REQ_REGISTRY_MISSING"
    elif kind == "validator":
        validator = tmp_path / "missing.py"
        expected = "REQ_VALIDATOR_MISSING"
    elif kind.startswith("schema_"):
        schema = tmp_path / "bad.json"
        schema.write_text("{" if kind == "schema_json" else '{"type": 42}')
    elif kind == "duplicate_yaml":
        registry = tmp_path / "duplicates.yaml"
        registry.write_text("schema_version: 0.0.0\n" + REGISTRY.read_text())
        expected = "REQ_VALIDATION_FAILED"
    else:
        validator = tmp_path / "fake.py"
        code = ""
        expected = "REQ_VALIDATOR_INCOMPLETE"
        if kind == "zero_errors_bad_exit":
            code = "print('36 requirements; 3 withdrawn; 0 error(s), 0 warning(s)')\nraise SystemExit(1)\n"
            expected = "REQ_VALIDATION_FAILED"
        elif kind == "empty_registry_summary":
            code = "print('0 requirements; 0 withdrawn; 0 error(s), 0 warning(s)')\n"
            expected = "REQ_VALIDATION_FAILED"
        validator.write_text(code)
    assert_blocked(run_gate(registry, schema, validator), expected)


def test_validator_timeout_is_a_named_failure(tmp_path, capsys):
    spec = importlib.util.spec_from_file_location("schema_gate", GATE)
    gate = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(gate)
    validator = tmp_path / "slow.py"
    validator.write_text("import time\ntime.sleep(10)\n")
    assert gate.check(REGISTRY, SCHEMA, validator, timeout=0.05) == 1
    assert capsys.readouterr().out.count("FAIL REQ_VALIDATOR_TIMEOUT") == 1
