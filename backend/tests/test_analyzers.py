"""The analysers, with the model replaced by a recording stub."""

from __future__ import annotations

import base64
import json
from io import BytesIO

import pytest
from PIL import Image

from core.verdict import CheckKind, Risk, Severity
from services.article_analyzer import ArticleAnalyzer
from services.message_analyzer import MessageAnalyzer
from services.nim_client import NimUnavailable
from services.video_analyzer import FrameInput, VideoAnalyzer


def a_frame() -> str:
    buffer = BytesIO()
    Image.new("RGB", (320, 240), "blue").save(buffer, format="JPEG")
    return base64.b64encode(buffer.getvalue()).decode()


class StubModel:
    """Stands in for NimClient.complete, recording what it was asked."""

    def __init__(self, reply: str | Exception):
        self.reply = reply
        self.prompts: list[str] = []
        self.image_counts: list[int] = []

    async def __call__(self, prompt, *, images=None, image_captions=None, **kwargs):
        self.prompts.append(prompt)
        self.image_counts.append(len(images or []))
        if isinstance(self.reply, Exception):
            raise self.reply
        return self.reply


def envelope(score=0.5, signals=(), note="Because of what I saw.") -> str:
    return json.dumps({"score": score, "signals": list(signals), "note": note})


def high_signal(label="Fingers merge together"):
    return {"label": label, "detail": "Her fingers join into one shape.", "severity": "high"}


@pytest.fixture
def patch_model(monkeypatch):
    def apply(module, reply):
        stub = StubModel(reply)
        monkeypatch.setattr(module.nim_client, "complete", stub)
        return stub

    return apply


# --- video -----------------------------------------------------------------


async def test_one_frame_uses_the_single_frame_prompt(patch_model):
    from services import video_analyzer as module

    stub = patch_model(module, envelope(0.1))
    verdict = await VideoAnalyzer().check([FrameInput(image=a_frame(), timestamp=1.0)])

    assert verdict.kind is CheckKind.VIDEO
    assert stub.image_counts == [1]
    assert "one frame from a video" in stub.prompts[0]


async def test_several_frames_use_the_sequence_prompt(patch_model):
    from services import video_analyzer as module

    stub = patch_model(module, envelope(0.9, [high_signal()]))
    frames = [FrameInput(image=a_frame(), timestamp=i * 0.2) for i in range(3)]
    verdict = await VideoAnalyzer().check(frames, title="Cat does a backflip")

    assert stub.image_counts == [3]
    assert "consecutive frames" in stub.prompts[0]
    assert "200 milliseconds apart" in stub.prompts[0]
    assert verdict.risk is Risk.DANGER
    assert verdict.source == "Cat does a backflip"


async def test_frames_beyond_the_cap_are_dropped(patch_model):
    from config.settings import settings
    from services import video_analyzer as module

    stub = patch_model(module, envelope(0.1))
    frames = [FrameInput(image=a_frame(), timestamp=float(i)) for i in range(12)]
    await VideoAnalyzer().check(frames)

    assert stub.image_counts == [settings.max_frames_per_check]


async def test_a_confident_model_with_no_evidence_is_not_believed(patch_model):
    from services import video_analyzer as module

    patch_model(module, envelope(0.95, []))
    verdict = await VideoAnalyzer().check([FrameInput(image=a_frame())])

    assert verdict.risk is Risk.SAFE
    assert verdict.score == pytest.approx(0.15)


async def test_video_has_no_fallback_and_says_so(patch_model):
    from services import video_analyzer as module

    patch_model(module, NimUnavailable("down"))
    with pytest.raises(NimUnavailable):
        await VideoAnalyzer().check([FrameInput(image=a_frame())])


async def test_an_unreadable_reply_is_not_treated_as_a_clean_bill(patch_model):
    from services import video_analyzer as module

    patch_model(module, "I'm sorry, I can't help with that.")
    with pytest.raises(NimUnavailable):
        await VideoAnalyzer().check([FrameInput(image=a_frame())])


async def test_no_frames_is_a_programming_error():
    with pytest.raises(ValueError):
        await VideoAnalyzer().check([])


# --- message ---------------------------------------------------------------


async def test_message_check_uses_the_model(patch_model):
    from services import message_analyzer as module

    stub = patch_model(module, envelope(0.8, [high_signal("Demands secrecy")]))
    verdict = await MessageAnalyzer().check(
        "Grandma, please don't tell anyone.", sender="Unknown", platform="facebook"
    )

    assert verdict.kind is CheckKind.MESSAGE
    assert verdict.risk is Risk.DANGER
    assert verdict.degraded is False
    assert "Sender as shown to the reader: Unknown" in stub.prompts[0]


async def test_the_keyword_scan_briefs_the_model(patch_model):
    from services import message_analyzer as module

    stub = patch_model(module, envelope(0.2))
    await MessageAnalyzer().check("Please send $500 in gift cards urgently.")

    assert "pay in a way you cannot undo" in stub.prompts[0]


async def test_local_high_severity_findings_survive_a_quiet_model(patch_model):
    """The model can be wrong about gift cards. The scan is not."""
    from services import message_analyzer as module

    patch_model(module, envelope(0.05, []))
    verdict = await MessageAnalyzer().check(
        "Hi! Please buy gift cards and send the codes right away, it's urgent."
    )

    labels = [signal.label for signal in verdict.signals]
    assert any("cannot undo" in label for label in labels)
    assert verdict.risk is not Risk.SAFE


async def test_an_ordinary_message_stays_safe(patch_model):
    from services import message_analyzer as module

    patch_model(module, envelope(0.05, []))
    verdict = await MessageAnalyzer().check("Lunch on Sunday? The kids will come too.")

    assert verdict.risk is Risk.SAFE
    assert verdict.signals == []


async def test_message_check_falls_back_when_the_model_is_down(patch_model):
    from services import message_analyzer as module

    patch_model(module, NimUnavailable("down"))
    verdict = await MessageAnalyzer().check(
        "Grandma I'm in jail and need bail money, send gift cards. Don't tell mom."
    )

    assert verdict.degraded is True
    assert verdict.risk is Risk.DANGER
    assert verdict.advice  # still tells the user what to do
    assert any(signal.severity is Severity.HIGH for signal in verdict.signals)


async def test_fallback_on_an_unreadable_reply_too(patch_model):
    from services import message_analyzer as module

    patch_model(module, "not json")
    verdict = await MessageAnalyzer().check("send gift cards now")
    assert verdict.degraded is True


async def test_empty_message_is_a_programming_error():
    with pytest.raises(ValueError):
        await MessageAnalyzer().check("   ")


# --- article ---------------------------------------------------------------


async def test_article_check(patch_model):
    from services import article_analyzer as module

    stub = patch_model(
        module, envelope(0.85, [high_signal("Contradicts known facts")])
    )
    verdict = await ArticleAnalyzer().check(
        "Scientists confirm the moon is made of cheese.",
        title="Moon Cheese Confirmed",
        url="https://example.com/moon",
    )

    assert verdict.kind is CheckKind.ARTICLE
    assert verdict.risk is Risk.DANGER
    assert verdict.platform == "web"
    assert "Headline: Moon Cheese Confirmed" in stub.prompts[0]


async def test_article_has_no_fallback(patch_model):
    from services import article_analyzer as module

    patch_model(module, NimUnavailable("down"))
    with pytest.raises(NimUnavailable):
        await ArticleAnalyzer().check("Some claim.")
