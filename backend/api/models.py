"""Pydantic models for API request/response schemas."""
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any


class FrameAnalysisRequest(BaseModel):
    """Request model for single frame analysis."""
    frame: str = Field(..., description="Base64 encoded image string")
    video_id: Optional[str] = Field(None, description="YouTube video ID")
    timestamp: Optional[float] = Field(None, description="Timestamp in seconds")
    video_title: Optional[str] = Field(None, description="Video title")


class InconsistencyItem(BaseModel):
    """Model for an individual inconsistency/artifact."""
    type: str = Field(..., description="Type of artifact detected")
    severity: str = Field(..., description="Severity level: low, medium, or high")
    description: str = Field(..., description="Detailed description of the issue")
    location: Optional[str] = Field(None, description="Area of frame where detected")


class FrameAnalysisResponse(BaseModel):
    """Response model for single frame analysis."""
    confidence_score: float = Field(..., ge=0.0, le=1.0, description="Confidence score (0=real, 1=fake)")
    is_likely_fake: bool = Field(..., description="Whether the frame is likely AI-generated")
    inconsistencies: List[InconsistencyItem] = Field(default_factory=list, description="List of detected issues")
    reasoning: str = Field(..., description="Detailed explanation of findings")
    error: Optional[str] = Field(None, description="Error message if analysis failed")


class BatchFrameItem(BaseModel):
    """Model for a frame in batch analysis."""
    frame: str = Field(..., description="Base64 encoded image string")
    video_id: Optional[str] = Field(None, description="YouTube video ID")
    timestamp: Optional[float] = Field(None, description="Timestamp in seconds")
    video_title: Optional[str] = Field(None, description="Video title")


class BatchAnalysisRequest(BaseModel):
    """Request model for batch frame analysis."""
    frames: List[BatchFrameItem] = Field(..., min_items=1, description="List of frames to analyze")


class BatchAnalysisResponse(BaseModel):
    """Response model for batch frame analysis."""
    overall_confidence: float = Field(..., ge=0.0, le=1.0, description="Average confidence across all frames")
    frame_results: List[FrameAnalysisResponse] = Field(..., description="Individual frame analysis results")
    summary: str = Field(..., description="Summary of batch analysis")


class HealthResponse(BaseModel):
    """Response model for health check."""
    status: str = Field(..., description="Service status")
    nim_api_configured: bool = Field(..., description="Whether NIM API is configured")


# --- News/Text analysis ---
class AnalyzeTextRequest(BaseModel):
    """Request model for news/fake-text analysis."""
    title: Optional[str] = Field(None, description="Optional article title")
    content: str = Field(..., description="Article content or claim text")
    urls: Optional[List[str]] = Field(default=None, description="Optional URLs referenced in the article")


class Citation(BaseModel):
    title: Optional[str] = None
    url: Optional[str] = None
    source: Optional[str] = None
    snippet: Optional[str] = None


class Claim(BaseModel):
    text: str
    span: Optional[List[int]] = None
    salience: Optional[float] = None


class AnalyzeTextResponse(BaseModel):
    overall_verdict: str = Field(..., description="LIKELY_FAKE | LIKELY_REAL | INCONCLUSIVE")
    confidence: float = Field(..., ge=0.0, le=1.0)
    key_findings: List[str] = Field(default_factory=list)
    claims: List[Claim] = Field(default_factory=list)
    sources: List[Citation] = Field(default_factory=list)
    reasoning: str = Field(...)
    executive_summary: Optional[str] = None


class SequenceFrameItem(BaseModel):
    """Model for a frame in sequence analysis."""
    frame: str = Field(..., description="Base64 encoded image string")
    timestamp: float = Field(..., description="Timestamp in seconds")


class SequenceAnalysisRequest(BaseModel):
    """Request model for frame sequence analysis."""
    frames: List[SequenceFrameItem] = Field(..., min_items=2, description="List of consecutive frames (2-5 frames)")
    video_id: Optional[str] = Field(None, description="YouTube video ID")
    video_title: Optional[str] = Field(None, description="Video title")


class TemporalInconsistency(BaseModel):
    """Model for a temporal inconsistency detected across frames."""
    frame_range: str = Field(..., description="Timestamp range where issue occurs")
    type: str = Field(..., description="Type of temporal violation")
    severity: str = Field(..., description="Severity level: low, medium, or high")
    description: str = Field(..., description="Detailed description of the physical impossibility")
    affected_frames: List[int] = Field(default_factory=list, description="Frame indices where issue is visible")
    location: Optional[str] = Field(None, description="Area of frame where detected")


class SequenceAnalysisResponse(BaseModel):
    """Response model for frame sequence analysis."""
    confidence_score: float = Field(..., ge=0.0, le=1.0, description="Confidence score (0=real, 1=fake)")
    is_likely_fake: bool = Field(..., description="Whether the sequence indicates AI-generated content")
    temporal_inconsistencies: List[TemporalInconsistency] = Field(default_factory=list, description="Detected temporal issues")
    frame_by_frame_notes: List[str] = Field(default_factory=list, description="Notes for each frame transition")
    reasoning: str = Field(..., description="Detailed explanation focusing on temporal inconsistencies")
    summary: Optional[str] = Field(None, description="Executive summary for investors")
    error: Optional[str] = Field(None, description="Error message if analysis failed")


class SmartVideoAnalysisRequest(BaseModel):
    """Request model for smart video analysis."""
    video_id: str = Field(..., description="YouTube video ID")
    frames: List[BatchFrameItem] = Field(..., min_items=1, description="All extracted frames from video")
    analysis_mode: str = Field("investor_demo", description="Analysis mode (investor_demo, detailed)")


class SmartVideoAnalysisResponse(BaseModel):
    """Response model for smart video analysis."""
    video_id: str = Field(..., description="YouTube video ID")
    duration_analyzed: str = Field(..., description="Duration of video analyzed")
    overall_verdict: str = Field(..., description="LIKELY FAKE, LIKELY REAL, or INCONCLUSIVE")
    confidence: float = Field(..., ge=0.0, le=1.0, description="Overall confidence score")
    key_findings: List[str] = Field(default_factory=list, description="Key findings for investors")
    executive_summary: str = Field(..., description="2-3 sentence summary for investors")
    detailed_report: Dict[str, Any] = Field(default_factory=dict, description="Detailed technical report")
    timestamp_markers: List[float] = Field(default_factory=list, description="Timestamps where issues detected")


# --- Avatar generation ---
class AvatarGenerateRequest(BaseModel):
    persona: str = Field("nvidia_omniverse", description="Avatar persona profile")
    context: str = Field(..., description="Short reasoning or summary to drive avatar generation")


class AvatarGenerateResponse(BaseModel):
    avatar_url: str = Field(..., description="Data URL or hosted URL for the avatar asset")
    avatar_type: str = Field(..., description="image | video | glb")
    reasoning: str | None = None

