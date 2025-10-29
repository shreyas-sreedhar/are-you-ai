"""Lightweight client to call our FastAPI endpoints from Python (for batch jobs, tests)."""
from __future__ import annotations

import httpx
from typing import Any, Dict, List, Optional

from config.settings import settings


class BackendClient:
    def __init__(self, base_url: Optional[str] = None, timeout: float = 60.0) -> None:
        self.base_url = base_url or settings.backend_base_url
        self.timeout = timeout

    async def analyze_frame(self, frame_b64: str, timestamp: float = 0.0, video_id: Optional[str] = None, title: Optional[str] = None) -> Dict[str, Any]:
        payload = {"frame": frame_b64, "timestamp": timestamp, "video_id": video_id, "video_title": title}
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            r = await client.post(f"{self.base_url}/api/v1/analyze-frame", json=payload)
            r.raise_for_status()
            return r.json()

    async def analyze_sequence(self, frames: List[Dict[str, Any]], video_id: Optional[str] = None, title: Optional[str] = None) -> Dict[str, Any]:
        payload = {"frames": frames, "video_id": video_id, "video_title": title}
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            r = await client.post(f"{self.base_url}/api/v1/analyze-sequence", json=payload)
            r.raise_for_status()
            return r.json()

    async def analyze_text(self, content: str, title: Optional[str] = None) -> Dict[str, Any]:
        payload = {"content": content, "title": title}
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            r = await client.post(f"{self.base_url}/api/v1/analyze-text", json=payload)
            r.raise_for_status()
            return r.json()


