"""Assembling a Verdict from a score and its evidence.

The analysers decide *how suspicious* something is. This decides what the
user is told about it — so the wording of a scam warning is identical whether
it came from the language model or from the local keyword scan.
"""

from __future__ import annotations

from .calibration import calibrate
from .guidance import DEGRADED_NOTE, advice_for, headline_for
from .verdict import CheckKind, Signal, Thresholds, Verdict

# Long titles and sender names come straight from page scraping.
MAX_SOURCE_LENGTH = 160


def assemble(
    kind: CheckKind,
    *,
    score: float,
    signals: list[Signal],
    thresholds: Thresholds,
    note: str | None = None,
    source: str | None = None,
    platform: str | None = None,
    degraded: bool = False,
    apply_calibration: bool = True,
) -> Verdict:
    """Build the finished Verdict a user will read."""
    final_score = calibrate(score, signals) if apply_calibration else max(0.0, min(1.0, score))
    risk = thresholds.risk_for(final_score)
    headline, summary = headline_for(kind, risk)

    if degraded:
        summary = f"{summary} {DEGRADED_NOTE}"

    return Verdict(
        kind=kind,
        risk=risk,
        score=final_score,
        headline=headline,
        summary=summary,
        # Strongest evidence first: it is what the reader sees without scrolling.
        signals=sorted(signals, key=_severity_rank),
        advice=advice_for(kind, risk),
        source=(source or "").strip()[:MAX_SOURCE_LENGTH] or None,
        platform=platform,
        analysis_note=(note or "").strip() or None,
        degraded=degraded,
    )


_SEVERITY_ORDER = {"high": 0, "medium": 1, "low": 2}


def _severity_rank(signal: Signal) -> int:
    return _SEVERITY_ORDER.get(signal.severity.value, 3)
