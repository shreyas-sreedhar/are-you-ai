"""Frame analysis service that orchestrates AI artifact detection."""
import logging
import json
import re
from typing import Dict, Any, List, Optional
from PIL import Image

from services.nim_client import NIMClient, extract_json_from_response
from utils.image_processor import preprocess_frame
from config.settings import settings

logger = logging.getLogger(__name__)


class FrameAnalyzer:
    """Service for analyzing video frames for AI-generated content."""
    
    def __init__(self):
        self.nim_client = NIMClient()
        self.confidence_threshold = settings.confidence_threshold
        
    async def analyze_frame(
        self,
        base64_frame: str,
        video_id: Optional[str] = None,
        timestamp: Optional[float] = None,
        video_title: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Analyze a single frame for AI-generated artifacts.
        
        Args:
            base64_frame: Base64 encoded image string
            video_id: Optional YouTube video ID
            timestamp: Optional timestamp in seconds
            video_title: Optional video title
            
        Returns:
            Dictionary with analysis results:
            {
                "confidence_score": float,
                "is_likely_fake": bool,
                "inconsistencies": List[Dict],
                "reasoning": str
            }
        """
        try:
            # Preprocess the frame
            logger.info(f"Preprocessing frame (video_id={video_id}, timestamp={timestamp})")
            image = preprocess_frame(base64_frame, max_size=settings.max_frame_size)
            
            # Call NIM API for analysis
            logger.info("Calling NIM API for frame analysis")
            api_response = await self.nim_client.analyze_frame(
                image=image,
                video_id=video_id,
                timestamp=timestamp,
                video_title=video_title
            )
            
            # Parse the response
            raw_content = api_response["raw_response"]
            
            # Try to extract structured JSON from response
            try:
                analysis_result = extract_json_from_response(raw_content)
            except ValueError as e:
                logger.warning(f"Could not parse JSON from response: {e}. Using fallback parsing.")
                # Fallback: try to extract information using regex/heuristics
                analysis_result = self._parse_fallback_response(raw_content)
            
            # Normalize the result
            result = self._normalize_result(analysis_result, raw_content)
            
            logger.info(
                f"Analysis complete: confidence={result['confidence_score']:.2f}, "
                f"is_fake={result['is_likely_fake']}"
            )
            
            return result
            
        except Exception as e:
            logger.error(f"Error analyzing frame: {e}", exc_info=True)
            # Return error result instead of raising
            return {
                "confidence_score": 0.5,
                "is_likely_fake": False,
                "inconsistencies": [],
                "reasoning": f"Error during analysis: {str(e)}",
                "error": str(e)
            }
    
    async def analyze_batch(
        self,
        frames: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Analyze multiple frames in batch.
        
        Args:
            frames: List of frame objects with keys:
                - frame: base64 string
                - video_id: optional string
                - timestamp: optional float
                - video_title: optional string
                
        Returns:
            Dictionary with batch analysis results:
            {
                "overall_confidence": float,
                "frame_results": List[Dict],
                "summary": str
            }
        """
        logger.info(f"Starting batch analysis of {len(frames)} frames")
        
        frame_results = []
        for i, frame_data in enumerate(frames):
            logger.info(f"Analyzing frame {i+1}/{len(frames)}")
            result = await self.analyze_frame(
                base64_frame=frame_data["frame"],
                video_id=frame_data.get("video_id"),
                timestamp=frame_data.get("timestamp"),
                video_title=frame_data.get("video_title")
            )
            frame_results.append(result)
        
        # Calculate overall confidence (average)
        confidence_scores = [
            r["confidence_score"] for r in frame_results 
            if "error" not in r
        ]
        
        if confidence_scores:
            overall_confidence = sum(confidence_scores) / len(confidence_scores)
        else:
            overall_confidence = 0.5
        
        # Count frames likely fake
        fake_count = sum(1 for r in frame_results if r.get("is_likely_fake", False))
        
        # Generate summary
        summary = (
            f"Analyzed {len(frames)} frames. "
            f"Overall confidence: {overall_confidence:.2f}. "
            f"{fake_count} frames ({fake_count/len(frames)*100:.1f}%) likely contain AI-generated content."
        )
        
        logger.info(f"Batch analysis complete: {summary}")
        
        return {
            "overall_confidence": overall_confidence,
            "frame_results": frame_results,
            "summary": summary
        }
    
    def _normalize_result(self, analysis_result: Dict[str, Any], raw_reasoning: str) -> Dict[str, Any]:
        """
        Normalize and validate analysis result structure.
        
        Args:
            analysis_result: Parsed JSON from API response
            raw_reasoning: Raw response text for fallback
            
        Returns:
            Normalized result dictionary
        """
        # Extract inconsistencies first to assess severity
        inconsistencies = analysis_result.get("inconsistencies", [])
        if not isinstance(inconsistencies, list):
            inconsistencies = []
        
        # Filter inconsistencies: Only keep HIGH severity or MEDIUM with clear physical impossibilities
        filtered_inconsistencies = []
        high_severity_count = 0
        
        for inc in inconsistencies:
            if not isinstance(inc, dict):
                continue
            
            severity = inc.get("severity", "low").lower()
            description = inc.get("description", "").lower()
            
            # Keep HIGH severity issues
            if severity == "high":
                filtered_inconsistencies.append(inc)
                high_severity_count += 1
            # Keep MEDIUM only if clearly impossible
            elif severity == "medium":
                impossible_keywords = ["impossible", "violates", "defies", "cannot happen", 
                                     "anatomically impossible", "physically impossible"]
                if any(keyword in description for keyword in impossible_keywords):
                    filtered_inconsistencies.append(inc)
            # Filter LOW severity unless explicitly impossible
            elif severity == "low":
                impossible_keywords = ["impossible", "violates", "defies", "anatomically impossible", 
                                     "physically impossible"]
                if any(keyword in description for keyword in impossible_keywords):
                    filtered_inconsistencies.append(inc)
        
        # Extract confidence score
        confidence_score = analysis_result.get("confidence_score", 0.5)
        if not isinstance(confidence_score, (int, float)):
            try:
                confidence_score = float(confidence_score)
            except (ValueError, TypeError):
                confidence_score = 0.5
        
        # Reduce confidence if no high-severity issues (conservative approach)
        if high_severity_count == 0:
            if len(filtered_inconsistencies) == 0:
                confidence_score = max(0.0, confidence_score * 0.1)  # Reduce to 10% of original
            elif len(filtered_inconsistencies) < 2:
                confidence_score = max(0.0, confidence_score * 0.3)
            else:
                confidence_score = max(0.0, confidence_score * 0.5)
        
        # Clamp to [0, 1]
        confidence_score = max(0.0, min(1.0, confidence_score))
        
        # Determine if likely fake (more conservative)
        is_likely_fake = analysis_result.get("is_likely_fake", False)
        if not isinstance(is_likely_fake, bool):
            is_likely_fake = confidence_score >= self.confidence_threshold
        
        # Don't mark as fake if no high-severity issues
        if high_severity_count == 0 and len(filtered_inconsistencies) < 2:
            is_likely_fake = False
            confidence_score = min(confidence_score, 0.3)
        
        # Extract reasoning
        reasoning = analysis_result.get("reasoning", raw_reasoning)
        if not reasoning or not isinstance(reasoning, str):
            reasoning = raw_reasoning if raw_reasoning else "No reasoning provided."
        
        # Add note if inconsistencies were filtered
        if len(inconsistencies) > len(filtered_inconsistencies):
            reasoning += f"\n\nNote: {len(inconsistencies) - len(filtered_inconsistencies)} low-severity issues filtered as likely normal video editing/effects."
        
        return {
            "confidence_score": confidence_score,
            "is_likely_fake": is_likely_fake,
            "inconsistencies": filtered_inconsistencies,
            "reasoning": reasoning
        }
    
    def _parse_fallback_response(self, text: str) -> Dict[str, Any]:
        """
        Fallback parser for when JSON extraction fails.
        Uses regex to extract key information.
        
        Args:
            text: Raw response text
            
        Returns:
            Dictionary with extracted information
        """
        result = {
            "confidence_score": 0.5,
            "is_likely_fake": False,
            "inconsistencies": [],
            "reasoning": text
        }
        
        # Try to extract confidence score
        confidence_match = re.search(r'confidence[:\s]+([\d.]+)', text, re.IGNORECASE)
        if confidence_match:
            try:
                score = float(confidence_match.group(1))
                # Normalize if seems to be 0-100 scale
                if score > 1:
                    score = score / 100.0
                result["confidence_score"] = max(0.0, min(1.0, score))
            except ValueError:
                pass
        
        # Try to detect fake indicators
        fake_keywords = ["fake", "artificial", "synthetic", "ai-generated", "manipulated"]
        fake_count = sum(1 for keyword in fake_keywords if keyword.lower() in text.lower())
        
        if fake_count > 2:
            result["is_likely_fake"] = True
            result["confidence_score"] = min(1.0, result["confidence_score"] + 0.2)
        
        return result

