"""Application configuration, loaded from the environment.

Every field here has a matching entry in `.env.example`. If you add one,
add it there too — that file is the contract with whoever runs this next.
"""

from __future__ import annotations

from functools import lru_cache
from pathlib import Path

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

from core.verdict import Thresholds

BACKEND_ROOT = Path(__file__).resolve().parent.parent

APP_NAME = "RUAI"
APP_VERSION = "1.0.0"
APP_DESCRIPTION = (
    "RUAI checks whether what someone is looking at is real: AI-generated "
    "video, scam messages, and false stories. Built for older adults."
)


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        # Read backend/.env first, then a repo-root .env, so a single file at
        # the top level works for someone running everything together.
        env_file=(BACKEND_ROOT.parent / ".env", BACKEND_ROOT / ".env"),
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # --- NVIDIA NIM ------------------------------------------------------
    nim_api_key: str = Field(
        default="",
        description="NVIDIA NIM API key. Get one at build.nvidia.com.",
    )
    nim_api_endpoint: str = "https://integrate.api.nvidia.com/v1/chat/completions"

    # Vision-language model: reads video frames.
    nim_vision_model: str = "nvidia/nemotron-nano-12b-v2-vl"
    # Text model: reads messages and articles. Small and fast, because a
    # scam warning that arrives after the user has replied is worthless.
    nim_text_model: str = "nvidia/nemotron-nano-9b-v2"

    nim_timeout_seconds: float = 60.0
    nim_max_retries: int = 2

    # --- Server ----------------------------------------------------------
    host: str = "127.0.0.1"
    port: int = 8000
    debug: bool = False

    # Origins allowed to call the API. Chrome extensions send their own
    # chrome-extension:// origin, which cannot be wildcarded, so the extension
    # is matched by regex instead (see main.py).
    allowed_origins: list[str] = Field(
        default_factory=lambda: ["http://localhost:3000", "http://127.0.0.1:3000"]
    )

    # --- Analysis --------------------------------------------------------
    max_frame_size: int = Field(
        default=1024, description="Longest edge of a frame sent to the model, in pixels"
    )
    max_frames_per_check: int = Field(
        default=5, description="Frames the extension may send in one video check"
    )

    # Where a score stops being reassuring and starts being a warning.
    caution_threshold: float = 0.35
    danger_threshold: float = 0.70

    # --- Storage ---------------------------------------------------------
    data_dir: Path = Field(
        default=BACKEND_ROOT / "data",
        description="Where the local activity log is written. Never leaves this machine.",
    )
    activity_log_enabled: bool = True

    @field_validator("data_dir", mode="before")
    @classmethod
    def _expand(cls, value: str | Path) -> Path:
        return Path(value).expanduser()

    @property
    def thresholds(self) -> Thresholds:
        return Thresholds(caution=self.caution_threshold, danger=self.danger_threshold)

    @property
    def nim_configured(self) -> bool:
        """Whether a key is present and is not the placeholder from .env.example."""
        key = self.nim_api_key.strip()
        return bool(key) and not key.startswith("your_")


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
