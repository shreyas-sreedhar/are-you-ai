"""The domain model and the wording built on top of it."""

from __future__ import annotations

import pytest

from core.assembler import MAX_SOURCE_LENGTH, assemble
from core.guidance import DEGRADED_NOTE, advice_for, headline_for
from core.verdict import CheckKind, Risk, Severity, Thresholds
from tests.conftest import make_signal

THRESHOLDS = Thresholds(caution=0.35, danger=0.70)


@pytest.mark.parametrize(
    ("score", "expected"),
    [
        (0.0, Risk.SAFE),
        (0.34, Risk.SAFE),
        (0.35, Risk.CAUTION),  # boundaries are inclusive at the bottom
        (0.69, Risk.CAUTION),
        (0.70, Risk.DANGER),
        (1.0, Risk.DANGER),
    ],
)
def test_risk_boundaries(score, expected):
    assert THRESHOLDS.risk_for(score) is expected


def test_every_kind_and_risk_has_copy():
    """A missing string here would render as a KeyError in front of a user."""
    for kind in CheckKind:
        for risk in Risk:
            headline, summary = headline_for(kind, risk)
            assert headline and summary
            assert advice_for(kind, risk)


def test_copy_follows_the_house_rules():
    for kind in CheckKind:
        for risk in Risk:
            headline, summary = headline_for(kind, risk)
            assert "!" not in headline and "!" not in summary
            assert not headline.endswith("."), headline
            for line in advice_for(kind, risk):
                assert line.endswith("."), line


def test_assemble_produces_a_complete_verdict():
    verdict = assemble(
        CheckKind.MESSAGE,
        score=0.9,
        signals=[make_signal(Severity.HIGH)],
        thresholds=THRESHOLDS,
        note="Because of the gift cards.",
        source="Unknown number",
        platform="facebook",
    )
    assert verdict.risk is Risk.DANGER
    assert verdict.headline == "This looks like a scam"
    assert verdict.advice
    assert verdict.analysis_note == "Because of the gift cards."
    assert verdict.is_concerning


def test_assemble_calibrates_by_default():
    verdict = assemble(
        CheckKind.VIDEO, score=0.95, signals=[], thresholds=THRESHOLDS
    )
    assert verdict.score == pytest.approx(0.15)
    assert verdict.risk is Risk.SAFE


def test_calibration_can_be_skipped_for_pre_scored_input():
    verdict = assemble(
        CheckKind.MESSAGE,
        score=0.95,
        signals=[],
        thresholds=THRESHOLDS,
        apply_calibration=False,
    )
    assert verdict.score == pytest.approx(0.95)


def test_degraded_verdicts_say_so():
    verdict = assemble(
        CheckKind.MESSAGE,
        score=0.8,
        signals=[make_signal(Severity.HIGH)],
        thresholds=THRESHOLDS,
        degraded=True,
    )
    assert verdict.degraded
    assert DEGRADED_NOTE in verdict.summary


def test_strongest_evidence_is_listed_first():
    verdict = assemble(
        CheckKind.VIDEO,
        score=0.9,
        signals=[
            make_signal(Severity.LOW, "Low"),
            make_signal(Severity.HIGH, "High"),
            make_signal(Severity.MEDIUM, "Medium"),
        ],
        thresholds=THRESHOLDS,
    )
    assert [signal.label for signal in verdict.signals] == ["High", "Medium", "Low"]


def test_scraped_titles_are_truncated():
    verdict = assemble(
        CheckKind.VIDEO,
        score=0.1,
        signals=[],
        thresholds=THRESHOLDS,
        source="x" * 500,
    )
    assert len(verdict.source) == MAX_SOURCE_LENGTH


def test_blank_source_becomes_none():
    verdict = assemble(
        CheckKind.VIDEO, score=0.1, signals=[], thresholds=THRESHOLDS, source="   "
    )
    assert verdict.source is None


def test_to_row_is_json_ready():
    row = assemble(
        CheckKind.VIDEO,
        score=0.8,
        signals=[make_signal(Severity.HIGH)],
        thresholds=THRESHOLDS,
    ).to_row()
    assert isinstance(row["checked_at"], str)
    assert row["signals"][0]["severity"] == "high"
