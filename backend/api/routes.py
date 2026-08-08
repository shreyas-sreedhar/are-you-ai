"""HTTP routes.

Three checks, one verdict, one activity log. The symmetry is the point: a new
kind of check is a new analyser and one route, not a new subsystem.
"""

from __future__ import annotations

import logging

from fastapi import APIRouter, HTTPException, Query, Response, status

from api.schemas import (
    ActivityEntry,
    ActivitySummary,
    ArticleCheckRequest,
    HealthResponse,
    MessageCheckRequest,
    VideoCheckRequest,
)
from config.settings import APP_VERSION, settings
from core.verdict import CheckKind, Verdict
from services.article_analyzer import article_analyzer
from services.message_analyzer import message_analyzer
from services.nim_client import NimUnavailable
from services.video_analyzer import FrameInput, video_analyzer
from storage import get_activity_log
from utils.images import InvalidFrame

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1")

# What the user is told when the model is unreachable and there is no local
# fallback. Written to the same standard as everything in core.guidance.
UNAVAILABLE_MESSAGE = (
    "RUAI cannot check this right now. Please try again in a moment. "
    "Until then, treat what you are looking at with extra care."
)


@router.get("/health", response_model=HealthResponse, tags=["system"])
async def health() -> HealthResponse:
    """Is the service up, and is it actually able to answer?"""
    return HealthResponse(
        status="ok",
        version=APP_VERSION,
        model_configured=settings.nim_configured,
        activity_log_enabled=settings.activity_log_enabled,
    )


@router.post("/check/video", response_model=Verdict, tags=["checks"])
async def check_video(request: VideoCheckRequest) -> Verdict:
    """Was this video made by a computer?"""
    try:
        verdict = await video_analyzer.check(
            [FrameInput(image=frame.image, timestamp=frame.timestamp) for frame in request.frames],
            title=request.title,
            video_id=request.video_id,
            platform=request.platform,
        )
    except InvalidFrame as exc:
        raise HTTPException(status.HTTP_422_UNPROCESSABLE_ENTITY, str(exc)) from exc
    except NimUnavailable as exc:
        logger.warning("video check unavailable: %s", exc)
        raise HTTPException(status.HTTP_503_SERVICE_UNAVAILABLE, UNAVAILABLE_MESSAGE) from exc

    get_activity_log().record(verdict)
    return verdict


@router.post("/check/message", response_model=Verdict, tags=["checks"])
async def check_message(request: MessageCheckRequest) -> Verdict:
    """Is this message a scam?

    Never returns 503: when the model is unreachable this falls back to the
    local pattern scan and marks the verdict as degraded.
    """
    verdict = await message_analyzer.check(
        request.text, sender=request.sender, platform=request.platform
    )

    # Only concerning messages are kept. A log of every ordinary message a
    # person receives would be surveillance, not protection.
    if verdict.is_concerning:
        get_activity_log().record(verdict)

    return verdict


@router.post("/check/article", response_model=Verdict, tags=["checks"])
async def check_article(request: ArticleCheckRequest) -> Verdict:
    """Does this story hold up?"""
    try:
        verdict = await article_analyzer.check(
            request.text, title=request.title, url=request.url
        )
    except NimUnavailable as exc:
        logger.warning("article check unavailable: %s", exc)
        raise HTTPException(status.HTTP_503_SERVICE_UNAVAILABLE, UNAVAILABLE_MESSAGE) from exc

    get_activity_log().record(verdict)
    return verdict


@router.get("/activity/summary", response_model=ActivitySummary, tags=["activity"])
async def activity_summary() -> ActivitySummary:
    return ActivitySummary(**get_activity_log().summary())


@router.get("/activity/recent", response_model=list[ActivityEntry], tags=["activity"])
async def activity_recent(
    limit: int = Query(20, ge=1, le=200),
    kind: CheckKind | None = Query(None, description="Filter to one kind of check"),
) -> list[ActivityEntry]:
    return [ActivityEntry(**row) for row in get_activity_log().recent(limit=limit, kind=kind)]


@router.delete(
    "/activity",
    status_code=status.HTTP_204_NO_CONTENT,
    response_class=Response,
    tags=["activity"],
)
async def clear_activity() -> Response:
    """Erase the local history. The user's record is theirs to delete."""
    get_activity_log().clear()
    return Response(status_code=status.HTTP_204_NO_CONTENT)
