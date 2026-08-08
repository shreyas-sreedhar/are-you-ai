"""The local scan — the answer when the model cannot be reached."""

from __future__ import annotations

import pytest

from core.verdict import Severity
from services.scam_signals import PATTERNS, scan

GRANDPARENT_SCAM = (
    "Grandma it's me, I was in a car accident and I'm in jail. Please don't "
    "tell mom. I need $2000 for bail money today, send it as gift cards."
)

ORDINARY_MESSAGE = (
    "Hi Mum, the kids loved the photos you sent. We'll call you on Sunday "
    "after lunch. Let me know if you need anything from the shops."
)


def test_a_textbook_scam_scores_high():
    result = scan(GRANDPARENT_SCAM)
    assert result.score >= 0.7
    assert "family_emergency" in result.matched_keys
    assert "irreversible_payment" in result.matched_keys
    assert any(signal.severity is Severity.HIGH for signal in result.signals)


def test_an_ordinary_family_message_scores_zero():
    result = scan(ORDINARY_MESSAGE)
    assert result.score == 0.0
    assert result.signals == []


def test_empty_input_is_safe():
    assert scan("").score == 0.0
    assert scan("   ").matched_keys == frozenset()


def test_matching_respects_word_boundaries():
    # The original build flagged this: "now" matched inside "know".
    assert scan("Let me know how you are getting on.").score == 0.0
    # And "ssn" inside a longer word.
    assert scan("The lesson was fun.").score == 0.0


def test_curly_apostrophes_still_match():
    straight = scan("Please don't tell anyone about this")
    curly = scan("Please don’t tell anyone about this")
    assert curly.matched_keys == straight.matched_keys
    assert "family_emergency" in curly.matched_keys


def test_pressure_plus_payment_scores_above_the_parts():
    payment_only = scan("You can pay with a gift card.")
    pressure_only = scan("This is urgent, you must act now.")
    both = scan("This is urgent, pay with a gift card immediately.")
    assert both.score > payment_only.score + pressure_only.score - 0.01


def test_score_is_capped():
    everything = " ".join(phrase for pattern in PATTERNS for phrase in pattern.phrases)
    assert scan(everything).score <= 0.95


def test_prompt_summary_is_readable():
    assert scan(ORDINARY_MESSAGE).summary_for_prompt == "nothing"
    assert "cannot undo" in scan("send gift cards").summary_for_prompt


@pytest.mark.parametrize(
    ("text", "expected_key"),
    [
        ("Your account has been suspended, verify now", "fear"),
        ("Congratulations, you won the lottery!", "unearned_prize"),
        ("This is the IRS calling about your taxes", "impersonates_authority"),
        ("Click here: bit.ly/x8fj2", "disguised_link"),
        ("Guaranteed return of 40% every month", "too_good_to_be_true"),
        ("Please share your one-time code with me", "asks_for_secrets"),
    ],
)
def test_each_tactic_is_recognised(text, expected_key):
    assert expected_key in scan(text).matched_keys


def test_every_signal_is_written_in_plain_language():
    """The details are shown to the reader verbatim, so they are held to the
    same standard as everything in core.guidance."""
    for pattern in PATTERNS:
        assert pattern.detail.endswith("."), pattern.key
        assert pattern.label[0].isupper(), pattern.key
        assert "!" not in pattern.detail, pattern.key
        # Nothing longer than two sentences.
        assert pattern.detail.count(".") <= 2, pattern.key
