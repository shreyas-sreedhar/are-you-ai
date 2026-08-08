"""The local history."""

from __future__ import annotations

from core.verdict import CheckKind, Risk
from storage.activity_log import ActivityLog
from tests.conftest import make_verdict


def test_a_recorded_verdict_reads_back(activity_log: ActivityLog):
    verdict = make_verdict(source="Aunt Mabel")
    assert activity_log.record(verdict)

    rows = activity_log.recent()
    assert len(rows) == 1
    assert rows[0]["source"] == "Aunt Mabel"
    assert rows[0]["kind"] == "message"
    assert rows[0]["signals"][0]["label"] == "Something odd"
    assert rows[0]["degraded"] is False


def test_newest_first(activity_log: ActivityLog):
    from datetime import datetime, timedelta, timezone

    base = datetime(2026, 1, 1, tzinfo=timezone.utc)
    for offset, source in enumerate(["oldest", "middle", "newest"]):
        activity_log.record(
            make_verdict(source=source, checked_at=base + timedelta(hours=offset))
        )

    assert [row["source"] for row in activity_log.recent()] == [
        "newest",
        "middle",
        "oldest",
    ]


def test_limit_and_kind_filter(activity_log: ActivityLog):
    activity_log.record(make_verdict(kind=CheckKind.MESSAGE))
    activity_log.record(make_verdict(kind=CheckKind.VIDEO))
    activity_log.record(make_verdict(kind=CheckKind.VIDEO))

    assert len(activity_log.recent(limit=2)) == 2
    assert len(activity_log.recent(kind=CheckKind.VIDEO)) == 2
    assert len(activity_log.recent(kind=CheckKind.ARTICLE)) == 0


def test_summary_counts(activity_log: ActivityLog):
    activity_log.record(make_verdict(kind=CheckKind.MESSAGE, risk=Risk.DANGER, score=0.9))
    activity_log.record(make_verdict(kind=CheckKind.VIDEO, risk=Risk.SAFE, score=0.1))
    activity_log.record(make_verdict(kind=CheckKind.VIDEO, risk=Risk.CAUTION, score=0.5))

    summary = activity_log.summary()
    assert summary["total_checks"] == 3
    assert summary["by_kind"] == {"video": 2, "message": 1, "article": 0}
    assert summary["by_risk"] == {"safe": 1, "caution": 1, "danger": 1}
    assert summary["warnings_last_24h"] == 2
    assert summary["last_checked_at"] is not None


def test_old_warnings_fall_out_of_the_24h_count(activity_log: ActivityLog):
    from datetime import datetime, timedelta, timezone

    long_ago = datetime.now(timezone.utc) - timedelta(days=9)
    activity_log.record(make_verdict(risk=Risk.DANGER, checked_at=long_ago))

    summary = activity_log.summary()
    assert summary["total_checks"] == 1
    assert summary["warnings_last_24h"] == 0


def test_empty_log_summarises_cleanly(activity_log: ActivityLog):
    summary = activity_log.summary()
    assert summary["total_checks"] == 0
    assert summary["last_checked_at"] is None
    assert activity_log.recent() == []


def test_clear_forgets_everything(activity_log: ActivityLog):
    activity_log.record(make_verdict())
    activity_log.clear()
    assert activity_log.recent() == []
    # And the file is still usable afterwards.
    assert activity_log.record(make_verdict())


def test_a_half_written_row_is_skipped_not_fatal(activity_log: ActivityLog):
    """Expected when the process is killed mid-append."""
    activity_log.record(make_verdict(source="good"))
    with activity_log.path.open("a", encoding="utf-8") as handle:
        handle.write("2026-01-01T00:00:00+00:00,message,danger,not-a-number\n")

    rows = activity_log.recent()
    assert [row["source"] for row in rows] == ["good"]


def test_a_disabled_log_writes_nothing(tmp_path):
    log = ActivityLog(tmp_path, enabled=False)
    assert log.record(make_verdict()) is False
    assert log.recent() == []
    assert log.summary()["total_checks"] == 0
    assert not (tmp_path / "checks.csv").exists()
