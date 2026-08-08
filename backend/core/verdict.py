"""The one thing RUAI produces.

Every check — a video frame, a chat message, a news article — ends up as a
`Verdict`. Same shape, same three risk levels, same fields. That is the whole
architectural idea: the analysers differ, the answer does not, so every
surface (extension overlay, popup, dashboard, web app) renders one component.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from enum import Enum
from typing import Any

from pydantic import BaseModel, Field


class CheckKind(str, Enum):
    """What was checked. Deliberately small and closed."""

    VIDEO = "video"
    MESSAGE = "message"
    ARTICLE = "article"


class Risk(str, Enum):
    """How worried the user should be.

    Three levels, not five. A fourth level would be a decision the reader has
    to make; three is an answer they can act on.
    """

    SAFE = "safe"
    CAUTION = "caution"
    DANGER = "danger"


class Severity(str, Enum):
    """How much a single piece of evidence should count."""

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


@dataclass(frozen=True)
class Thresholds:
    """Where the score stops being reassuring and starts being a warning."""

    caution: float = 0.35
    danger: float = 0.70

    def risk_for(self, score: float) -> Risk:
        if score >= self.danger:
            return Risk.DANGER
        if score >= self.caution:
            return Risk.CAUTION
        return Risk.SAFE


DEFAULT_THRESHOLDS = Thresholds()


class Signal(BaseModel):
    """One piece of evidence, written so a non-technical reader can judge it."""

    label: str = Field(..., description="Short noun phrase, e.g. 'Asks for gift cards'")
    detail: str = Field(..., description="One plain sentence explaining the signal")
    severity: Severity = Field(default=Severity.MEDIUM)


class Verdict(BaseModel):
    """The answer to 'should I trust this?'."""

    kind: CheckKind
    risk: Risk
    score: float = Field(
        ..., ge=0.0, le=1.0, description="0 = nothing suspicious, 1 = certainly not genuine"
    )

    headline: str = Field(..., description="The one line shown in the largest type")
    summary: str = Field(..., description="One or two plain sentences under the headline")
    signals: list[Signal] = Field(default_factory=list)
    advice: list[str] = Field(default_factory=list, description="What to do next")

    source: str | None = Field(None, description="Video title, sender name, or article title")
    platform: str | None = Field(None, description="youtube, facebook, instagram, web…")
    checked_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    analysis_note: str | None = Field(
        None, description="The model's own reasoning. Shown collapsed, for the curious."
    )
    degraded: bool = Field(
        False,
        description="True when the model was unreachable and local heuristics answered instead",
    )

    @property
    def is_concerning(self) -> bool:
        return self.risk in (Risk.CAUTION, Risk.DANGER)

    def to_row(self) -> dict[str, Any]:
        """Flatten for the activity log."""
        return {
            "checked_at": self.checked_at.isoformat(),
            "kind": self.kind.value,
            "risk": self.risk.value,
            "score": round(self.score, 4),
            "source": self.source or "",
            "platform": self.platform or "",
            "headline": self.headline,
            "summary": self.summary,
            "signals": [s.model_dump(mode="json") for s in self.signals],
            "advice": self.advice,
            "degraded": self.degraded,
        }
