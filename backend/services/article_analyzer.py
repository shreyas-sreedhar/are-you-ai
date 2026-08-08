"""Deciding whether a story or forwarded claim holds up."""

from __future__ import annotations

import logging

from config.settings import settings
from core.assembler import assemble
from core.envelope import EnvelopeError, parse_envelope
from core.prompts import article_prompt
from core.verdict import CheckKind, Verdict
from services.nim_client import NimUnavailable, nim_client

logger = logging.getLogger(__name__)

MAX_ARTICLE_LENGTH = 12000


class ArticleAnalyzer:
    async def check(
        self,
        text: str,
        *,
        title: str | None = None,
        url: str | None = None,
    ) -> Verdict:
        text = (text or "").strip()
        if not text:
            raise ValueError("article text is required")

        context = _context_block(title=title, url=url)

        try:
            reply = await nim_client.complete(
                article_prompt(context, text=text[:MAX_ARTICLE_LENGTH]),
                temperature=0.2,
                max_tokens=1400,
            )
            envelope = parse_envelope(reply)
        except EnvelopeError as exc:
            # No local fallback: judging a claim needs world knowledge.
            logger.warning("article check: unreadable model reply (%s)", exc)
            raise NimUnavailable("the model reply could not be read") from exc

        verdict = assemble(
            CheckKind.ARTICLE,
            score=envelope.score,
            signals=envelope.signals,
            thresholds=settings.thresholds,
            note=envelope.note,
            source=title,
            platform="web",
        )

        logger.info(
            "article check: raw=%.2f final=%.2f -> %s",
            envelope.score,
            verdict.score,
            verdict.risk.value,
        )
        return verdict


def _context_block(*, title: str | None, url: str | None) -> str:
    lines = []
    if title:
        lines.append(f"Headline: {title}")
    if url:
        lines.append(f"Published at: {url}")
    if not lines:
        return ""
    return "CONTEXT:\n" + "\n".join(lines) + "\n"


article_analyzer = ArticleAnalyzer()
