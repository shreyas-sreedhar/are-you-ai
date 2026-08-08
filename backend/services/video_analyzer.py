"""Deciding whether a video was made by a computer."""

from __future__ import annotations

import logging
from dataclasses import dataclass

from config.settings import settings
from core.assembler import assemble
from core.envelope import EnvelopeError, parse_envelope
from core.calibration import evidence_summary
from core.prompts import video_frame_prompt, video_sequence_prompt
from core.verdict import CheckKind, Verdict
from services.nim_client import NimUnavailable, nim_client
from utils.images import prepare_frame

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class FrameInput:
    """One frame grabbed from a playing video."""

    image: str
    timestamp: float | None = None


class VideoAnalyzer:
    """Checks one or more frames from the same video.

    A single frame is enough to catch melted hands and garbled signage. Most
    generated video, though, only gives itself away *between* frames — an
    object that is there and then is not — so the extension sends a short
    burst and this falls through to the sequence prompt whenever it can.
    """

    async def check(
        self,
        frames: list[FrameInput],
        *,
        title: str | None = None,
        video_id: str | None = None,
        platform: str | None = None,
    ) -> Verdict:
        if not frames:
            raise ValueError("at least one frame is required")

        selected = frames[: settings.max_frames_per_check]
        images = [prepare_frame(frame.image, settings.max_frame_size) for frame in selected]
        timestamps = [frame.timestamp for frame in selected]

        context = _context_block(title=title, video_id=video_id, platform=platform)

        if len(images) >= 2:
            prompt = video_sequence_prompt(
                context, frame_count=len(images), gap_ms=_average_gap_ms(timestamps)
            )
            captions = [
                f"Frame {index + 1}{_at(timestamp)}:"
                for index, timestamp in enumerate(timestamps)
            ]
        else:
            prompt = video_frame_prompt(context)
            captions = None

        try:
            reply = await nim_client.complete(
                prompt,
                images=images,
                image_captions=captions,
                max_tokens=1800 if len(images) >= 2 else 1200,
            )
            envelope = parse_envelope(reply)
        except EnvelopeError as exc:
            # Unlike a message, there is no local fallback for a video frame.
            # Guessing "looks real" here would be the most harmful thing we
            # could do, so the caller surfaces "cannot check right now".
            logger.warning("video check: unreadable model reply (%s)", exc)
            raise NimUnavailable("the model reply could not be read") from exc

        verdict = assemble(
            CheckKind.VIDEO,
            score=envelope.score,
            signals=envelope.signals,
            thresholds=settings.thresholds,
            note=envelope.note,
            source=title,
            platform=platform,
        )

        logger.info(
            "video check: %s frames, raw=%.2f final=%.2f (%s) -> %s",
            len(images),
            envelope.score,
            verdict.score,
            evidence_summary(envelope.signals),
            verdict.risk.value,
        )
        return verdict


def _at(timestamp: float | None) -> str:
    return "" if timestamp is None else f" at {timestamp:.2f} seconds"


def _average_gap_ms(timestamps: list[float | None]) -> float:
    known = [value for value in timestamps if value is not None]
    if len(known) < 2:
        return 0.0
    span = known[-1] - known[0]
    return abs(span) * 1000 / (len(known) - 1)


def _context_block(
    *, title: str | None, video_id: str | None, platform: str | None
) -> str:
    lines = []
    if title:
        lines.append(f"Video title: {title}")
    if platform:
        lines.append(f"Platform: {platform}")
    if video_id:
        lines.append(f"Video ID: {video_id}")
    if not lines:
        return ""
    return "CONTEXT:\n" + "\n".join(lines) + "\n"


video_analyzer = VideoAnalyzer()
