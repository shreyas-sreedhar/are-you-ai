"""Shared test setup.

Settings are a process-wide singleton read at import time, so the environment
has to be arranged before anything under test is imported.
"""

from __future__ import annotations

import os
import tempfile
from pathlib import Path

import pytest

# Point the activity log at a scratch directory and make sure no real API key
# leaks in from the developer's shell.
_TMP = Path(tempfile.mkdtemp(prefix="ruai-tests-"))
os.environ["DATA_DIR"] = str(_TMP)
os.environ["NIM_API_KEY"] = "test-key-not-real"
os.environ["DEBUG"] = "false"

from config.settings import settings  # noqa: E402
from core.verdict import CheckKind, Severity, Signal, Verdict  # noqa: E402
from storage import get_activity_log  # noqa: E402


@pytest.fixture
def activity_log(tmp_path, monkeypatch):
    """An ActivityLog isolated to this test."""
    from storage.activity_log import ActivityLog

    return ActivityLog(tmp_path, enabled=True)


@pytest.fixture(autouse=True)
def _clean_shared_log():
    """Keep API tests from seeing each other's rows."""
    log = get_activity_log()
    log.clear()
    yield
    log.clear()


@pytest.fixture
def client():
    from fastapi.testclient import TestClient

    import main

    with TestClient(main.app) as test_client:
        yield test_client


def make_signal(severity: Severity = Severity.MEDIUM, label: str = "Something odd") -> Signal:
    return Signal(label=label, detail="A plain sentence about it.", severity=severity)


def make_verdict(**overrides) -> Verdict:
    defaults = dict(
        kind=CheckKind.MESSAGE,
        risk="caution",
        score=0.5,
        headline="Be careful with this message",
        summary="It uses pressure tactics.",
        signals=[make_signal()],
        advice=["Take your time."],
        source="Unknown sender",
        platform="facebook",
    )
    defaults.update(overrides)
    return Verdict(**defaults)


__all__ = ["make_signal", "make_verdict", "settings"]
