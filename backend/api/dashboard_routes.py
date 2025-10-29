"""Dashboard API routes for fetching analytics data"""
import logging
from fastapi import APIRouter, HTTPException
from typing import List, Dict, Any
from services.csv_storage import get_csv_storage

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/dashboard", tags=["dashboard"])

# Initialize CSV storage
csv_storage = get_csv_storage()


@router.get("/metrics")
async def get_metrics() -> Dict[str, int]:
    """Get dashboard metrics from CSV files"""
    try:
        metrics = csv_storage.get_metrics()
        return metrics
    except Exception as e:
        logger.error(f"Error fetching metrics: {e}", exc_info=True)
        # Return zeros on error
        return {
            "videos_protected": 0,
            "scams_detected": 0,
            "messages_analyzed": 0,
            "active_alerts": 0
        }


@router.get("/alerts")
async def get_alerts(limit: int = 20) -> List[Dict[str, Any]]:
    """Get recent alerts (suspicious videos and messages) from CSV files"""
    try:
        alerts = csv_storage.get_recent_alerts(limit=limit)
        return alerts
    except Exception as e:
        logger.error(f"Error fetching alerts: {e}", exc_info=True)
        return []


@router.get("/recent-videos")
async def get_recent_videos(limit: int = 20):
    """Get recently analyzed videos from CSV"""
    try:
        videos = csv_storage.get_all_videos()
        # Sort by timestamp, most recent first
        videos.sort(key=lambda x: x['timestamp'], reverse=True)
        return videos[:limit]
    except Exception as e:
        logger.error(f"Error fetching recent videos: {e}", exc_info=True)
        return []


@router.get("/recent-messages")
async def get_recent_messages(limit: int = 20):
    """Get recently analyzed messages from CSV"""
    try:
        messages = csv_storage.get_all_messages()
        # Sort by timestamp, most recent first
        messages.sort(key=lambda x: x['timestamp'], reverse=True)
        return messages[:limit]
    except Exception as e:
        logger.error(f"Error fetching recent messages: {e}", exc_info=True)
        return []
