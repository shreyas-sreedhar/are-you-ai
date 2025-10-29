"""API route handlers."""
import logging
from fastapi import APIRouter, HTTPException
from typing import List

from api.models import (
    FrameAnalysisRequest,
    FrameAnalysisResponse,
    BatchAnalysisRequest,
    BatchAnalysisResponse,
    HealthResponse,
    AnalyzeTextRequest,
    AnalyzeTextResponse,
    AvatarGenerateRequest,
    AvatarGenerateResponse,
)
from services.frame_analyzer import FrameAnalyzer
from services.news_analyzer import NewsAnalyzer
from services.agent_orchestrator import AgentOrchestrator
from config.settings import settings

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1", tags=["analysis"])

# Initialize analyzers (singleton instances)
frame_analyzer = FrameAnalyzer()
news_analyzer = NewsAnalyzer()
agent_orchestrator = AgentOrchestrator()


@router.post("/analyze-frame", response_model=FrameAnalysisResponse)
async def analyze_frame(request: FrameAnalysisRequest) -> FrameAnalysisResponse:
    """
    Analyze a single video frame for AI-generated content.
    
    Args:
        request: Frame analysis request with base64 image and metadata
        
    Returns:
        Analysis results with confidence score and detected inconsistencies
    """
    try:
        logger.info(
            f"Received frame analysis request (video_id={request.video_id}, "
            f"timestamp={request.timestamp})"
        )
        
        result = await frame_analyzer.analyze_frame(
            base64_frame=request.frame,
            video_id=request.video_id,
            timestamp=request.timestamp,
            video_title=request.video_title
        )
        
        # Convert inconsistencies to proper format
        inconsistencies = []
        for inc in result.get("inconsistencies", []):
            if isinstance(inc, dict):
                inconsistencies.append({
                    "type": inc.get("type", "unknown"),
                    "severity": inc.get("severity", "medium"),
                    "description": inc.get("description", ""),
                    "location": inc.get("location")
                })
        
        response = FrameAnalysisResponse(
            confidence_score=result["confidence_score"],
            is_likely_fake=result["is_likely_fake"],
            inconsistencies=inconsistencies,
            reasoning=result["reasoning"],
            error=result.get("error")
        )
        
        return response
        
    except Exception as e:
        logger.error(f"Error in analyze_frame endpoint: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error during frame analysis: {str(e)}"
        )


@router.post("/analyze-batch", response_model=BatchAnalysisResponse)
async def analyze_batch(request: BatchAnalysisRequest) -> BatchAnalysisResponse:
    """
    Analyze multiple video frames in batch.
    
    Args:
        request: Batch analysis request with list of frames
        
    Returns:
        Batch analysis results with overall confidence and per-frame results
    """
    try:
        logger.info(f"Received batch analysis request with {len(request.frames)} frames")
        
        # Convert request models to dictionaries
        frames_data = [
            {
                "frame": frame.frame,
                "video_id": frame.video_id,
                "timestamp": frame.timestamp,
                "video_title": frame.video_title
            }
            for frame in request.frames
        ]
        
        result = await frame_analyzer.analyze_batch(frames_data)
        
        # Convert frame results to response models
        frame_results = []
        for frame_result in result["frame_results"]:
            inconsistencies = []
            for inc in frame_result.get("inconsistencies", []):
                if isinstance(inc, dict):
                    inconsistencies.append({
                        "type": inc.get("type", "unknown"),
                        "severity": inc.get("severity", "medium"),
                        "description": inc.get("description", ""),
                        "location": inc.get("location")
                    })
            
            frame_results.append(
                FrameAnalysisResponse(
                    confidence_score=frame_result["confidence_score"],
                    is_likely_fake=frame_result["is_likely_fake"],
                    inconsistencies=inconsistencies,
                    reasoning=frame_result["reasoning"],
                    error=frame_result.get("error")
                )
            )
        
        response = BatchAnalysisResponse(
            overall_confidence=result["overall_confidence"],
            frame_results=frame_results,
            summary=result["summary"]
        )
        
        return response
        
    except Exception as e:
        logger.error(f"Error in analyze_batch endpoint: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error during batch analysis: {str(e)}"
        )


@router.get("/health", response_model=HealthResponse)
async def health_check() -> HealthResponse:
    """
    Health check endpoint to verify service status and configuration.
    
    Returns:
        Health status and configuration information
    """
    nim_api_configured = bool(settings.nim_api_key and settings.nim_api_key != "your_nvidia_nim_api_key_here")
    
    return HealthResponse(
        status="healthy",
        nim_api_configured=nim_api_configured
    )


@router.post("/analyze-text", response_model=AnalyzeTextResponse)
async def analyze_text(request: AnalyzeTextRequest) -> AnalyzeTextResponse:
    """Analyze news/article text for misinformation using NIM."""
    try:
        result = await news_analyzer.analyze_text(
            content=request.content,
            title=request.title,
            urls=request.urls,
        )
        return AnalyzeTextResponse(**result)
    except Exception as e:
        logger.error("Error in analyze_text: %s", e, exc_info=True)
        raise HTTPException(status_code=500, detail=f"Internal error: {e}")


@router.post("/avatar/generate", response_model=AvatarGenerateResponse)
async def avatar_generate(request: AvatarGenerateRequest) -> AvatarGenerateResponse:
    """Return a stub Omniverse-style avatar as a data URL so the frontend can render immediately.

    This is a temporary implementation. Replace with a real Omniverse Avatar service when available.
    """
    try:
        text = (request.context or "").strip()
        # For demo: return a lightweight public GLB that works with <model-viewer>
        glb_url = "https://modelviewer.dev/shared-assets/models/Astronaut.glb"
        return AvatarGenerateResponse(avatar_url=glb_url, avatar_type="glb", reasoning=text)
    except Exception as e:
        logger.error("Error in avatar_generate: %s", e, exc_info=True)
        raise HTTPException(status_code=500, detail=f"Internal error: {e}")


@router.post("/analyze-with-agents")
async def analyze_with_agents(request: BatchAnalysisRequest):
    """
    🤖 MULTI-AGENT ANALYSIS - Prize Track Feature!
    
    Uses multiple specialized Nemotron agents working together:
    1. Vision Agent (Nemotron-Nano-12B-v2-VL) - Analyzes frames
    2. Temporal Agent (Nemotron-nano-9b-v2) - Checks consistency
    3. Research Agent (Nemotron-nano-9b-v2) - Searches patterns
    4. Fact-Checker Agent (Nemotron-nano-9b-v2) - Verifies claims
    5. Safety Guard (Nemotron-Safety-Guard-8B-v3) - Checks safety
    6. Orchestrator (Nemotron-super-49b-v1.5) - Final decision
    
    Demonstrates:
    - ✅ Autonomous reasoning and multi-step problem-solving
    - ✅ Multi-agent orchestration
    - ✅ Tool integration (web search, fact-checking)
    - ✅ ReAct pattern (Reason → Act → Observe)
    """
    try:
        logger.info(f"🤖 Multi-agent analysis starting with {len(request.frames)} frames")
        
        # Convert request models to dictionaries for agent orchestrator
        frames_data = [
            {
                "frame": frame.frame,
                "video_id": frame.video_id,
                "timestamp": frame.timestamp,
                "video_title": frame.video_title
            }
            for frame in request.frames
        ]
        
        video_metadata = {
            "video_id": request.frames[0].video_id if request.frames else "unknown",
            "title": request.frames[0].video_title if request.frames else "Unknown Video",
            "platform": "youtube",  # Can be extracted from request
            "frame_count": len(request.frames)
        }
        
        # Run multi-agent analysis
        result = await agent_orchestrator.analyze_video_with_agents(
            frames=frames_data,
            video_metadata=video_metadata
        )
        
        logger.info(f"✅ Multi-agent analysis complete: {result['is_likely_fake']}")
        
        return {
            "success": True,
            "analysis_type": "multi_agent",
            "result": result,
            "agent_workflow": result.get("workflow_visualization"),
            "reasoning_chain": result.get("agent_chain"),
            "models_used": [
                "nvidia/nemotron-nano-12b-v2-vl",
                "nvidia/nemotron-nano-9b-v2",
                "nvidia/nemotron-safety-guard-8b-v3",
                "nvidia/nemotron-super-49b-v1.5"
            ]
        }
        
    except Exception as e:
        logger.error(f"Error in multi-agent analysis: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Multi-agent analysis failed: {str(e)}"
        )

