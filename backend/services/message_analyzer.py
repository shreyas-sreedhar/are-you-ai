"""Deciding whether a message is a scam.

This is the check that matters most. Americans over 60 lose billions of
dollars a year to messages exactly like the ones this reads, and the loss is
usually irreversible by the time anyone else finds out. So this analyser is
built to still give an answer when the model is unreachable, and to lean
toward warning when money or secrets are involved.
"""

from __future__ import annotations

import logging

from config.settings import settings
from core.assembler import assemble
from core.calibration import calibrate
from core.envelope import EnvelopeError, parse_envelope
from core.prompts import message_prompt
from core.verdict import CheckKind, Severity, Signal, Verdict
from services.nim_client import NimUnavailable, nim_client
from services.scam_signals import scan

logger = logging.getLogger(__name__)

# How much weight the keyword scan keeps when the model has also answered.
# The scan is precise about payment and secrets but blind to context — it
# cannot tell "I changed my password" from "send me your password" — so it
# sets a floor rather than a verdict.
LOCAL_WEIGHT = 0.75

MAX_MESSAGE_LENGTH = 4000


class MessageAnalyzer:
    async def check(
        self,
        text: str,
        *,
        sender: str | None = None,
        platform: str | None = None,
    ) -> Verdict:
        text = (text or "").strip()
        if not text:
            raise ValueError("message text is required")

        scanned = scan(text[:MAX_MESSAGE_LENGTH])
        context = _context_block(sender=sender, platform=platform)

        try:
            reply = await nim_client.complete(
                message_prompt(
                    context,
                    message=text[:MAX_MESSAGE_LENGTH],
                    local_flags=scanned.summary_for_prompt,
                ),
                max_tokens=1000,
            )
            envelope = parse_envelope(reply)

        except (NimUnavailable, EnvelopeError) as exc:
            # The whole point of the keyword scan: an answer now beats a
            # perfect answer after the money has been wired.
            logger.warning("message check falling back to local scan: %s", exc)
            return assemble(
                CheckKind.MESSAGE,
                score=scanned.score,
                signals=scanned.signals,
                thresholds=settings.thresholds,
                source=sender,
                platform=platform,
                degraded=True,
                apply_calibration=False,
            )

        model_score = calibrate(envelope.score, envelope.signals)
        score = max(model_score, scanned.score * LOCAL_WEIGHT)

        # Keep the local high-severity findings even when the model missed
        # them: "asks for gift cards" is worth saying out loud every time.
        signals = _merge(
            envelope.signals,
            [signal for signal in scanned.signals if signal.severity is Severity.HIGH],
        )

        verdict = assemble(
            CheckKind.MESSAGE,
            score=score,
            signals=signals,
            thresholds=settings.thresholds,
            note=envelope.note,
            source=sender,
            platform=platform,
            apply_calibration=False,
        )

        logger.info(
            "message check: model=%.2f local=%.2f final=%.2f -> %s",
            model_score,
            scanned.score,
            verdict.score,
            verdict.risk.value,
        )
        return verdict


def _merge(primary: list[Signal], extra: list[Signal]) -> list[Signal]:
    """Combine signal lists, keeping the first wording of each finding."""
    seen = {signal.label.strip().lower() for signal in primary}
    merged = list(primary)
    for signal in extra:
        key = signal.label.strip().lower()
        if key not in seen:
            seen.add(key)
            merged.append(signal)
    return merged


def _context_block(*, sender: str | None, platform: str | None) -> str:
    lines = []
    if sender:
        lines.append(f"Sender as shown to the reader: {sender}")
    if platform:
        lines.append(f"Arrived on: {platform}")
    if not lines:
        return ""
    return "CONTEXT:\n" + "\n".join(lines) + "\n"


message_analyzer = MessageAnalyzer()
