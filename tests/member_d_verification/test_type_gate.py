"""Prove the real type checker accepts correct contracts and rejects invalid ones."""
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]


@pytest.mark.parametrize("value,exit_code", [('"COMPLETED"', 0), ('"BROKEN"', 1), ('123', 1)])
def test_literal_outcome_contract_is_checked(value, exit_code, tmp_path):
    code = f"from tradingagents.runapi.result import RunOutcome\noutcome: RunOutcome = {value}\n"
    fixture = tmp_path / "type_probe.py"
    fixture.write_text(code)
    result = subprocess.run(
        [sys.executable, "-m", "mypy", "--config-file", str(ROOT / "pyproject.toml"), str(fixture)],
        cwd=ROOT, capture_output=True, text=True, check=False, timeout=90,
    )
    assert result.returncode == exit_code, result.stdout + result.stderr
    if exit_code:
        assert "assignment" in result.stdout
