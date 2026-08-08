"""Reading model replies that are not quite what we asked for."""

from __future__ import annotations

import json

import pytest

from core.envelope import EnvelopeError, parse_envelope
from core.verdict import Severity

CLEAN = '{"score": 0.8, "signals": [], "note": "Nothing to add."}'


def test_reads_a_clean_reply():
    envelope = parse_envelope(CLEAN)
    assert envelope.score == 0.8
    assert envelope.note == "Nothing to add."


def test_reads_a_fenced_reply():
    envelope = parse_envelope(f"Here you go:\n```json\n{CLEAN}\n```\nHope that helps!")
    assert envelope.score == 0.8


def test_strips_a_thinking_block():
    reply = f"<think>Let me consider the hands... {{not json}}</think>\n{CLEAN}"
    assert parse_envelope(reply).score == 0.8


def test_ignores_prose_after_the_object():
    # A greedy regex would swallow the trailing brace and fail to parse.
    envelope = parse_envelope(f"{CLEAN}\n\nNote: consider {{another thing}} too.")
    assert envelope.score == 0.8


def test_braces_inside_strings_do_not_end_the_object():
    reply = '{"score": 0.4, "note": "the caption read {LIVE}", "signals": []}'
    assert parse_envelope(reply).note == "the caption read {LIVE}"


def test_escaped_quotes_inside_strings():
    reply = '{"score": 0.2, "note": "she said \\"hello\\" clearly", "signals": []}'
    assert parse_envelope(reply).score == 0.2


@pytest.mark.parametrize(
    ("raw", "expected"),
    [
        (0.75, 0.75),
        ("0.75", 0.75),
        (75, 0.75),  # answered on a 0-100 scale
        ("75%", 0.75),
        (1.4, 1.0),  # clamped
        (-3, 0.0),
        ("not a number", 0.5),
        (None, 0.5),
    ],
)
def test_score_coercion(raw, expected):
    envelope = parse_envelope(json.dumps({"score": raw, "signals": []}))
    assert envelope.score == pytest.approx(expected)


def test_accepts_the_older_key_names():
    reply = """{
      "confidence": 0.9,
      "inconsistencies": [
        {"type": "Melting fingers", "description": "Her hand changes shape.", "severity": "HIGH"}
      ],
      "reasoning": "Several impossible transitions."
    }"""
    envelope = parse_envelope(reply)
    assert envelope.score == 0.9
    assert envelope.note == "Several impossible transitions."
    assert envelope.signals[0].label == "Melting fingers"
    assert envelope.signals[0].severity is Severity.HIGH


def test_signals_flattened_to_strings_still_survive():
    reply = '{"score": 0.5, "signals": ["The sign text is unreadable."]}'
    signal = parse_envelope(reply).signals[0]
    assert signal.detail == "The sign text is unreadable."
    assert signal.severity is Severity.MEDIUM


def test_unknown_severity_falls_back_to_medium():
    reply = '{"score": 0.5, "signals": [{"label": "x", "detail": "y", "severity": "catastrophic"}]}'
    assert parse_envelope(reply).signals[0].severity is Severity.MEDIUM


def test_signals_without_text_are_dropped():
    reply = '{"score": 0.5, "signals": [{"severity": "high"}, 42, null]}'
    assert parse_envelope(reply).signals == []


@pytest.mark.parametrize("reply", ["", "   ", "I cannot help with that.", "{unterminated"])
def test_unusable_replies_raise(reply):
    with pytest.raises(EnvelopeError):
        parse_envelope(reply)


def test_non_object_json_raises():
    with pytest.raises(EnvelopeError):
        parse_envelope("[1, 2, 3]")


def test_broken_json_raises():
    with pytest.raises(EnvelopeError):
        parse_envelope('{"score": 0.5, "signals": [,]}')
