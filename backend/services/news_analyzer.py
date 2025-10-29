"""News/claim analysis service using NIM reasoning models."""
import logging
from typing import Any, Dict, List, Optional

from services.nim_client import NIMClient, extract_json_from_response

logger = logging.getLogger(__name__)


class NewsAnalyzer:
    def __init__(self) -> None:
        self.nim = NIMClient()

    async def analyze_text(self, content: str, title: Optional[str] = None, urls: Optional[List[str]] = None) -> Dict[str, Any]:
        try:
            api = await self.nim.analyze_text(text=content, title=title)
            raw = api["raw_response"]
            data = extract_json_from_response(raw)

            # Normalize
            overall = data.get("overall_verdict", "INCONCLUSIVE")
            conf = float(data.get("confidence", 0.5) or 0.5)
            key_findings = data.get("key_findings", []) or []
            claims = data.get("claims", []) or []
            sources = data.get("sources", []) or []
            reasoning = data.get("reasoning", raw)
            summary = data.get("executive_summary")

            # Guardrails
            conf = max(0.0, min(1.0, conf))

            return {
                "overall_verdict": overall,
                "confidence": conf,
                "key_findings": key_findings,
                "claims": claims,
                "sources": sources,
                "reasoning": reasoning,
                "executive_summary": summary,
            }
        except Exception as e:
            logger.error("News analysis failed: %s", e)
            return {
                "overall_verdict": "INCONCLUSIVE",
                "confidence": 0.0,
                "key_findings": [],
                "claims": [],
                "sources": [],
                "reasoning": f"Error: {e}",
                "executive_summary": None,
            }


