"""The rule that stops the detector crying wolf."""

from __future__ import annotations

import pytest

from core.calibration import calibrate, evidence_summary
from core.verdict import Severity
from tests.conftest import make_signal


def test_confidence_without_evidence_is_capped():
    # The failure mode this exists for: model says 0.9, points at nothing.
    assert calibrate(0.9, []) == pytest.approx(0.15)


def test_low_severity_only_is_heavily_discounted():
    signals = [make_signal(Severity.LOW), make_signal(Severity.LOW, "Another")]
    assert calibrate(0.8, signals) == pytest.approx(0.32)


def test_a_lone_medium_signal_is_discounted():
    assert calibrate(0.8, [make_signal(Severity.MEDIUM)]) == pytest.approx(0.56)


def test_several_medium_signals_stand():
    signals = [make_signal(Severity.MEDIUM, f"Finding {i}") for i in range(3)]
    assert calibrate(0.8, signals) == pytest.approx(0.8)


def test_a_high_severity_signal_is_taken_at_face_value():
    assert calibrate(0.95, [make_signal(Severity.HIGH)]) == pytest.approx(0.95)


def test_calibration_never_raises_a_score():
    # A model saying "this is fine" while listing impossibilities is a case
    # for reading the note, not for overriding it.
    assert calibrate(0.1, [make_signal(Severity.HIGH)]) == pytest.approx(0.1)


@pytest.mark.parametrize(("raw", "expected"), [(1.7, 0.15), (-0.5, 0.0)])
def test_out_of_range_scores_are_clamped(raw, expected):
    assert calibrate(raw, []) == pytest.approx(expected)


def test_evidence_summary_reads_like_a_log_line():
    signals = [make_signal(Severity.HIGH), make_signal(Severity.LOW, "b")]
    assert evidence_summary(signals) == "1 high, 1 low"
    assert evidence_summary([]) == "no signals"
