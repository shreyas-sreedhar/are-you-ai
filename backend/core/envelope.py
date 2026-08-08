"""Turning whatever the model actually said into the envelope we asked for.

Models are told to reply with JSON only. They frequently do not: they wrap it
in a markdown fence, prepend a sentence of throat-clearing, or emit a
`<think>` block first. This module is the single place that copes with that,
so the analysers can assume clean data.
"""

from __future__ import annotations

import json
import logging
import re
from typing import Any

from pydantic import BaseModel, Field, field_validator

from .verdict import Severity, Signal

logger = logging.getLogger(__name__)

_THINK_BLOCK = re.compile(r"<think>.*?</think>", re.DOTALL | re.IGNORECASE)
_CODE_FENCE = re.compile(r"```(?:json)?\s*(.*?)\s*```", re.DOTALL)

# Above this, a score was meant as a percentage. Below it, the model has
# simply overshot 1.0 and should be clamped — reading 1.4 as 1.4% would turn
# "certainly fake" into "nothing to see here".
PERCENT_THRESHOLD = 1.5


class EnvelopeError(ValueError):
    """The model's reply could not be read as the requested envelope."""


class ModelEnvelope(BaseModel):
    """The JSON contract shared by all three prompts."""

    score: float = Field(0.5, ge=0.0, le=1.0)
    signals: list[Signal] = Field(default_factory=list)
    note: str = ""

    @field_validator("score", mode="before")
    @classmethod
    def _coerce_score(cls, value: Any) -> float:
        """Accept "0.8", 80, and "80%" — models produce all three."""
        if isinstance(value, str):
            value = value.strip().rstrip("%").strip()
        try:
            score = float(value)
        except (TypeError, ValueError):
            return 0.5
        if score > PERCENT_THRESHOLD:
            score = score / 100.0
        return max(0.0, min(1.0, score))

    @field_validator("note", mode="before")
    @classmethod
    def _coerce_note(cls, value: Any) -> str:
        return "" if value is None else str(value)


def _strip_wrappers(text: str) -> str:
    text = _THINK_BLOCK.sub("", text)
    fenced = _CODE_FENCE.search(text)
    return fenced.group(1) if fenced else text


def _first_json_object(text: str) -> str:
    """Extract the first balanced {...} block.

    A greedy regex is wrong here: it swallows trailing commentary that happens
    to contain a brace. This walks the string instead, and ignores braces that
    appear inside string literals.
    """
    start = text.find("{")
    if start == -1:
        raise EnvelopeError("no JSON object in model reply")

    depth = 0
    in_string = False
    escaped = False

    for index in range(start, len(text)):
        char = text[index]

        if in_string:
            if escaped:
                escaped = False
            elif char == "\\":
                escaped = True
            elif char == '"':
                in_string = False
            continue

        if char == '"':
            in_string = True
        elif char == "{":
            depth += 1
        elif char == "}":
            depth -= 1
            if depth == 0:
                return text[start : index + 1]

    raise EnvelopeError("unterminated JSON object in model reply")


def _normalise_signals(raw: Any) -> list[dict[str, Any]]:
    """Coerce loosely-shaped signal entries into the ones Signal accepts."""
    if not isinstance(raw, list):
        return []

    signals: list[dict[str, Any]] = []
    for item in raw:
        if isinstance(item, str):
            # Some models flatten signals into a list of sentences.
            signals.append({"label": item[:60], "detail": item, "severity": "medium"})
            continue
        if not isinstance(item, dict):
            continue

        label = item.get("label") or item.get("type") or item.get("title")
        detail = item.get("detail") or item.get("description") or item.get("reason")
        if not (label or detail):
            continue

        severity = str(item.get("severity", "medium")).strip().lower()
        if severity not in {level.value for level in Severity}:
            severity = "medium"

        signals.append(
            {
                "label": str(label or detail)[:80],
                "detail": str(detail or label),
                "severity": severity,
            }
        )
    return signals


def parse_envelope(text: str) -> ModelEnvelope:
    """Read a model reply into a ModelEnvelope.

    Raises EnvelopeError when the reply contains no usable JSON at all; the
    caller decides whether to retry, fall back, or surface a degraded verdict.
    """
    if not text or not text.strip():
        raise EnvelopeError("empty model reply")

    candidate = _first_json_object(_strip_wrappers(text))

    try:
        data = json.loads(candidate)
    except json.JSONDecodeError as exc:
        logger.debug("unparseable model JSON: %s", candidate[:400])
        raise EnvelopeError(f"invalid JSON in model reply: {exc}") from exc

    if not isinstance(data, dict):
        raise EnvelopeError("model reply was not a JSON object")

    return ModelEnvelope(
        score=data.get("score", data.get("confidence", 0.5)),
        signals=_normalise_signals(
            data.get("signals") or data.get("inconsistencies") or []
        ),
        note=data.get("note") or data.get("reasoning") or "",
    )
