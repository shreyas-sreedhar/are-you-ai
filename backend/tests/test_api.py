"""The HTTP surface, end to end, with the model stubbed."""

from __future__ import annotations

import base64
import json
from io import BytesIO

import pytest
from PIL import Image


def a_frame() -> str:
    buffer = BytesIO()
    Image.new("RGB", (200, 150), "green").save(buffer, format="JPEG")
    return base64.b64encode(buffer.getvalue()).decode()


def stub_reply(score=0.1, signals=(), note="A note."):
    payload = json.dumps({"score": score, "signals": list(signals), "note": note})

    async def complete(prompt, **kwargs):
        return payload

    return complete


@pytest.fixture
def model(monkeypatch):
    """Replace the shared NIM client's complete() for every analyser."""

    def apply(score=0.1, signals=()):
        from services import nim_client as module

        monkeypatch.setattr(module.nim_client, "complete", stub_reply(score, signals))

    return apply


HIGH = {"label": "Fingers merge", "detail": "Her fingers join together.", "severity": "high"}


def test_health(client):
    body = client.get("/api/v1/health").json()
    assert body["status"] == "ok"
    assert body["version"]
    assert body["model_configured"] is True


def test_root_lists_the_three_checks(client):
    body = client.get("/").json()
    assert body["name"] == "RUAI"
    assert len(body["checks"]) == 3


def test_video_check_returns_a_verdict(client, model):
    model(score=0.9, signals=[HIGH])
    response = client.post(
        "/api/v1/check/video",
        json={"frames": [{"image": a_frame(), "timestamp": 1.0}], "title": "A clip", "platform": "youtube"},
    )
    assert response.status_code == 200

    verdict = response.json()
    assert verdict["kind"] == "video"
    assert verdict["risk"] == "danger"
    assert verdict["headline"]
    assert verdict["advice"]
    assert verdict["signals"][0]["severity"] == "high"


def test_message_check_returns_a_verdict(client, model):
    model(score=0.05)
    response = client.post(
        "/api/v1/check/message",
        json={"text": "Are we still on for Sunday lunch?", "sender": "Jean"},
    )
    assert response.status_code == 200
    assert response.json()["risk"] == "safe"


def test_article_check_returns_a_verdict(client, model):
    model(score=0.8, signals=[HIGH])
    response = client.post(
        "/api/v1/check/article", json={"text": "The moon is cheese.", "title": "Cheese"}
    )
    assert response.status_code == 200
    assert response.json()["kind"] == "article"


def test_a_broken_frame_is_a_422(client, model):
    model()
    response = client.post(
        "/api/v1/check/video", json={"frames": [{"image": "not-an-image"}]}
    )
    assert response.status_code == 422


def test_video_check_says_so_when_the_model_is_down(client, monkeypatch):
    from services import nim_client as module

    async def unavailable(prompt, **kwargs):
        raise module.NimUnavailable("down")

    monkeypatch.setattr(module.nim_client, "complete", unavailable)

    response = client.post("/api/v1/check/video", json={"frames": [{"image": a_frame()}]})
    assert response.status_code == 503
    # And says it in words the reader can act on.
    assert "extra care" in response.json()["detail"]


def test_message_check_still_answers_when_the_model_is_down(client, monkeypatch):
    from services import nim_client as module

    async def unavailable(prompt, **kwargs):
        raise module.NimUnavailable("down")

    monkeypatch.setattr(module.nim_client, "complete", unavailable)

    response = client.post(
        "/api/v1/check/message",
        json={"text": "Send $500 in gift cards immediately or you will be arrested."},
    )
    assert response.status_code == 200

    verdict = response.json()
    assert verdict["degraded"] is True
    assert verdict["risk"] == "danger"
    assert verdict["advice"]


@pytest.mark.parametrize(
    "payload",
    [
        {"frames": []},
        {"frames": [{"image": a_frame()}] * 13},
        {},
    ],
)
def test_video_request_validation(client, payload):
    assert client.post("/api/v1/check/video", json=payload).status_code == 422


def test_message_request_validation(client):
    assert client.post("/api/v1/check/message", json={"text": ""}).status_code == 422


def test_activity_records_checks_and_summarises(client, model):
    model(score=0.9, signals=[HIGH])
    client.post("/api/v1/check/video", json={"frames": [{"image": a_frame()}], "title": "Clip"})

    summary = client.get("/api/v1/activity/summary").json()
    assert summary["total_checks"] == 1
    assert summary["by_kind"]["video"] == 1
    assert summary["warnings_last_24h"] == 1

    recent = client.get("/api/v1/activity/recent").json()
    assert recent[0]["source"] == "Clip"
    assert recent[0]["risk"] == "danger"


def test_ordinary_messages_are_not_logged(client, model):
    """A record of every message someone receives is surveillance."""
    model(score=0.02)
    client.post("/api/v1/check/message", json={"text": "See you Sunday."})

    assert client.get("/api/v1/activity/summary").json()["total_checks"] == 0


def test_concerning_messages_are_logged(client, model):
    model(score=0.9, signals=[HIGH])
    client.post("/api/v1/check/message", json={"text": "Send gift cards now.", "sender": "X"})

    assert client.get("/api/v1/activity/summary").json()["total_checks"] == 1


def test_activity_can_be_filtered_and_limited(client, model):
    model(score=0.9, signals=[HIGH])
    for index in range(3):
        client.post(
            "/api/v1/check/video",
            json={"frames": [{"image": a_frame()}], "title": f"Clip {index}"},
        )

    assert len(client.get("/api/v1/activity/recent?limit=2").json()) == 2
    assert len(client.get("/api/v1/activity/recent?kind=message").json()) == 0
    assert client.get("/api/v1/activity/recent?limit=0").status_code == 422


def test_history_can_be_erased(client, model):
    model(score=0.9, signals=[HIGH])
    client.post("/api/v1/check/video", json={"frames": [{"image": a_frame()}]})

    assert client.delete("/api/v1/activity").status_code == 204
    assert client.get("/api/v1/activity/summary").json()["total_checks"] == 0
