"""Keeping the score honest about the evidence behind it.

Vision models are eager. Asked "is this AI-generated?", they will often return
0.8 and then list three observations that amount to "the lighting is nice".
The original build shipped with this problem: ordinary cooking videos came
back flagged, and a detector that cries wolf is worse than no detector,
because the user learns to dismiss it.

So the score is capped by the strength of the evidence the model itself
produced. A confident claim with nothing to point at is not a confident claim.
"""

from __future__ import annotations

from .verdict import Severity, Signal

# Applied when the model's stated confidence outruns its own evidence.
_NO_EVIDENCE_CEILING = 0.15
_LOW_ONLY_FACTOR = 0.4
_SINGLE_MEDIUM_FACTOR = 0.7


def calibrate(score: float, signals: list[Signal]) -> float:
    """Scale a model's raw score down to what its evidence supports.

    The score is never scaled *up*: a model that says "this is fine" while
    listing three impossibilities is a case for reading the note, not for
    overriding it.
    """
    score = max(0.0, min(1.0, score))

    if not signals:
        return min(score, _NO_EVIDENCE_CEILING)

    severities = [signal.severity for signal in signals]

    if Severity.HIGH in severities:
        return score

    mediums = severities.count(Severity.MEDIUM)

    if mediums == 0:
        # Only low-severity observations: interesting, not damning.
        return score * _LOW_ONLY_FACTOR

    if mediums == 1 and len(severities) == 1:
        return score * _SINGLE_MEDIUM_FACTOR

    return score


def evidence_summary(signals: list[Signal]) -> str:
    """A short description of what the evidence adds up to, for logs."""
    if not signals:
        return "no signals"
    counts = {level: 0 for level in Severity}
    for signal in signals:
        counts[signal.severity] += 1
    return ", ".join(f"{count} {level.value}" for level, count in counts.items() if count)
