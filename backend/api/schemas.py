"""Request and response shapes for the HTTP API.

Responses are deliberately thin: every check returns a `Verdict` from
`core.verdict`, unchanged. There is no per-feature response model to keep in
sync with the domain model, because there is no per-feature answer.
"""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field

from core.verdict import Verdict

__all__ = [
    "FramePayload",
    "VideoCheckRequest",
    "MessageCheckRequest",
    "ArticleCheckRequest",
    "HealthResponse",
    "ActivitySummary",
    "Verdict",
]


class FramePayload(BaseModel):
    image: str = Field(
        ...,
        description="Base64 JPEG or PNG, with or without a data: URL prefix",
    )
    timestamp: float | None = Field(
        None, ge=0, description="Position in the video, in seconds"
    )


class VideoCheckRequest(BaseModel):
    frames: list[FramePayload] = Field(
        ...,
        min_length=1,
        max_length=12,
        description="Consecutive frames from one video. Two or more enables "
        "the sequence check, which catches far more than a single still.",
    )
    title: str | None = Field(None, max_length=500)
    video_id: str | None = Field(None, max_length=200)
    platform: str | None = Field(None, max_length=40, examples=["youtube"])


class MessageCheckRequest(BaseModel):
    text: str = Field(..., min_length=1, max_length=8000)
    sender: str | None = Field(None, max_length=200)
    platform: str | None = Field(None, max_length=40, examples=["facebook"])


class ArticleCheckRequest(BaseModel):
    text: str = Field(..., min_length=1, max_length=20000)
    title: str | None = Field(None, max_length=500)
    url: str | None = Field(None, max_length=2000)


class HealthResponse(BaseModel):
    status: str = "ok"
    version: str
    model_configured: bool = Field(
        ..., description="Whether a NIM API key is present. False means checks will fail."
    )
    activity_log_enabled: bool


class ActivitySummary(BaseModel):
    total_checks: int
    by_kind: dict[str, int]
    by_risk: dict[str, int]
    warnings_last_24h: int
    last_checked_at: str | None = None


class ActivityEntry(BaseModel):
    """A past verdict, as stored. Looser than Verdict because it is history."""

    checked_at: str
    kind: str
    risk: str
    score: float
    platform: str | None = None
    source: str | None = None
    headline: str
    summary: str
    signals: list[dict[str, Any]] = Field(default_factory=list)
    advice: list[str] = Field(default_factory=list)
    degraded: bool = False
