"""Local persistence."""

from functools import lru_cache

from config.settings import settings

from .activity_log import ActivityLog


@lru_cache
def get_activity_log() -> ActivityLog:
    return ActivityLog(settings.data_dir, enabled=settings.activity_log_enabled)


__all__ = ["ActivityLog", "get_activity_log"]
