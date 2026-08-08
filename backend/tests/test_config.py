"""Configuration, and the promises .env.example makes about it."""

from __future__ import annotations

import re
from pathlib import Path

import pytest

from config.settings import Settings, settings

REPO_ROOT = Path(__file__).resolve().parents[2]
ENV_EXAMPLE = REPO_ROOT / ".env.example"


def test_env_example_exists():
    assert ENV_EXAMPLE.exists(), "committed .env.example is the setup contract"


def test_env_example_documents_every_setting():
    """A setting missing from .env.example is a setting nobody will find."""
    documented = ENV_EXAMPLE.read_text(encoding="utf-8").upper()
    missing = [
        name for name in Settings.model_fields if name.upper() not in documented
    ]
    assert not missing, f"undocumented settings: {missing}"


def test_env_example_holds_no_real_key():
    """Guards against a real key being pasted in and committed."""
    text = ENV_EXAMPLE.read_text(encoding="utf-8")
    match = re.search(r"^NIM_API_KEY=(.*)$", text, re.MULTILINE)
    assert match, "NIM_API_KEY must be present"

    value = match.group(1).strip()
    assert value.startswith("your_"), "placeholder value expected"
    assert not value.startswith("nvapi-"), "a real NVIDIA key is in .env.example"


@pytest.mark.parametrize(
    ("key", "expected"),
    [("", False), ("   ", False), ("your_nvidia_nim_api_key_here", False), ("nvapi-abc", True)],
)
def test_nim_configured_rejects_the_placeholder(key, expected, monkeypatch):
    """An unedited .env must read as 'not configured', not as a broken key."""
    probe = Settings(nim_api_key=key)
    assert probe.nim_configured is expected


def test_thresholds_come_from_settings():
    assert settings.thresholds.caution == settings.caution_threshold
    assert settings.thresholds.danger == settings.danger_threshold


def test_data_dir_is_absolute():
    """Relative paths resolve differently under `python main.py` and uvicorn."""
    assert settings.data_dir.is_absolute()


def test_design_tokens_are_in_sync():
    """The extension's copy of brand/tokens.css must not have drifted."""
    source = REPO_ROOT / "brand" / "tokens.css"
    copy = REPO_ROOT / "extension" / "styles" / "tokens.css"

    assert source.exists() and copy.exists()
    assert source.read_text(encoding="utf-8") in copy.read_text(encoding="utf-8"), (
        "run: python scripts/sync_brand.py"
    )
