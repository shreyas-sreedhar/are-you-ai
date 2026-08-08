"""A local record of everything RUAI has checked.

One table, not two. The previous build kept videos.csv and messages.csv with
different columns, which meant the dashboard had to special-case each feature
and could never show them on one timeline. Since every check now produces the
same Verdict, every check is one row.

This is personal data — it is a list of what someone watched and who messaged
them — so it stays in a local file, is git-ignored, and is never sent
anywhere.
"""

from __future__ import annotations

import csv
import json
import logging
import threading
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Iterable

from core.verdict import CheckKind, Risk, Verdict

logger = logging.getLogger(__name__)

COLUMNS = (
    "checked_at",
    "kind",
    "risk",
    "score",
    "platform",
    "source",
    "headline",
    "summary",
    "signals",
    "advice",
    "degraded",
)


class ActivityLog:
    """Append-only CSV of verdicts."""

    def __init__(self, data_dir: Path, *, enabled: bool = True) -> None:
        self.enabled = enabled
        self.path = Path(data_dir) / "checks.csv"
        self._lock = threading.Lock()
        if self.enabled:
            self._ensure_file()

    def _ensure_file(self) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        if not self.path.exists():
            with self.path.open("w", newline="", encoding="utf-8") as handle:
                csv.writer(handle).writerow(COLUMNS)
            logger.info("activity log created at %s", self.path)

    # --- writing ---------------------------------------------------------

    def record(self, verdict: Verdict) -> bool:
        """Append a verdict. Never raises: logging must not break a check."""
        if not self.enabled:
            return False

        row = verdict.to_row()
        try:
            with self._lock, self.path.open("a", newline="", encoding="utf-8") as handle:
                csv.writer(handle).writerow(
                    [
                        row["checked_at"],
                        row["kind"],
                        row["risk"],
                        row["score"],
                        row["platform"],
                        row["source"],
                        row["headline"],
                        row["summary"],
                        json.dumps(row["signals"]),
                        json.dumps(row["advice"]),
                        row["degraded"],
                    ]
                )
            return True
        except OSError as exc:
            logger.error("could not write to activity log: %s", exc)
            return False

    def clear(self) -> None:
        """Forget everything. The user's history is theirs to delete."""
        if not self.enabled:
            return
        with self._lock:
            self.path.unlink(missing_ok=True)
            self._ensure_file()

    # --- reading ---------------------------------------------------------

    def _rows(self) -> Iterable[dict[str, Any]]:
        if not self.enabled or not self.path.exists():
            return []

        try:
            with self._lock, self.path.open("r", newline="", encoding="utf-8") as handle:
                raw_rows = list(csv.DictReader(handle))
        except OSError as exc:
            logger.error("could not read activity log: %s", exc)
            return []

        parsed: list[dict[str, Any]] = []
        for raw in raw_rows:
            try:
                parsed.append(
                    {
                        "checked_at": raw["checked_at"],
                        "kind": raw["kind"],
                        "risk": raw["risk"],
                        "score": float(raw["score"] or 0.0),
                        "platform": raw["platform"] or None,
                        "source": raw["source"] or None,
                        "headline": raw["headline"],
                        "summary": raw["summary"],
                        "signals": json.loads(raw["signals"] or "[]"),
                        "advice": json.loads(raw["advice"] or "[]"),
                        "degraded": str(raw["degraded"]).lower() == "true",
                    }
                )
            except (KeyError, ValueError, json.JSONDecodeError) as exc:
                # A half-written final row is expected if the process was
                # killed mid-append. Skip it rather than failing the read.
                logger.debug("skipping malformed activity row: %s", exc)

        return parsed

    def recent(self, limit: int = 20, kind: CheckKind | None = None) -> list[dict[str, Any]]:
        rows = list(self._rows())
        if kind is not None:
            rows = [row for row in rows if row["kind"] == kind.value]
        rows.sort(key=lambda row: row["checked_at"], reverse=True)
        return rows[:limit]

    def summary(self) -> dict[str, Any]:
        """Counts for the dashboard."""
        rows = list(self._rows())
        cutoff = (datetime.now(timezone.utc) - timedelta(days=1)).isoformat()

        by_kind = {kind.value: 0 for kind in CheckKind}
        by_risk = {risk.value: 0 for risk in Risk}
        recent_warnings = 0

        for row in rows:
            if row["kind"] in by_kind:
                by_kind[row["kind"]] += 1
            if row["risk"] in by_risk:
                by_risk[row["risk"]] += 1
            if row["risk"] in (Risk.CAUTION.value, Risk.DANGER.value) and row["checked_at"] >= cutoff:
                recent_warnings += 1

        return {
            "total_checks": len(rows),
            "by_kind": by_kind,
            "by_risk": by_risk,
            "warnings_last_24h": recent_warnings,
            "last_checked_at": max((row["checked_at"] for row in rows), default=None),
        }
