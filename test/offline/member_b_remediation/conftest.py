"""Member B remediation regressions (R1-R5); synthetic inputs only.

Every case here is offline: fake models, synthetic credentials/portfolios,
``tmp_path`` and no network. The shared upstream ``tests/conftest.py`` already
blanks ``TRADINGAGENTS_*`` and refuses sockets for tests not marked
``integration``.
"""

from __future__ import annotations


def pytest_configure(config):
    config.addinivalue_line("markers", "unit: fast isolated unit tests")
