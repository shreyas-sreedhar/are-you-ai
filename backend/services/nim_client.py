"""NVIDIA NIM API client for vision-language model interactions."""
import httpx
import logging
from typing import Dict, Any, Optional, List
import base64
from io import BytesIO
from PIL import Image

from config.settings import settings

logger = logging.getLogger(__name__)


class NIMClient:
    """Client for interacting with NVIDIA NIM API."""
    
    def __init__(self):
        self.api_key = settings.nim_api_key
        self.api_endpoint = settings.nim_api_endpoint
        self.model_name = settings.nim_model_name
        self.timeout = 60.0  # 60 second timeout for API calls
        
    async def analyze_frame(
        self, 
        image: Image.Image,
        video_id: Optional[str] = None,
        timestamp: Optional[float] = None,
        video_title: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Analyze a video frame for AI-generated artifacts using Nemotron model.
        
        Args:
            image: PIL Image object to analyze
            video_id: Optional YouTube video ID
            timestamp: Optional timestamp in seconds
            video_title: Optional video title for context
            
        Returns:
            Dictionary containing analysis results from the model
            
        Raises:
            httpx.HTTPError: If API request fails
            ValueError: If API response is invalid
        """
        # Convert image to base64 for API
        buffer = BytesIO()
        image.save(buffer, format="JPEG", quality=85)
        image_bytes = buffer.getvalue()
        image_base64 = base64.b64encode(image_bytes).decode("utf-8")
        
        # Construct the prompt for artifact detection
        context_info = ""
        if video_title:
            context_info += f"Video Title: {video_title}\n"
        if timestamp is not None:
            context_info += f"Timestamp: {timestamp:.2f}s\n"
        if video_id:
            context_info += f"Video ID: {video_id}\n"
        
        prompt = f"""Analyze this video frame for AI-generated or manipulated content. 
Focus on PHYSICAL IMPOSSIBILITIES and MOTION INCONSISTENCIES that indicate AI generation:

CRITICAL INDICATORS (High Priority - Focus Here):
1. **Physically Impossible Motions**: 
   - Objects moving in ways that defy physics (e.g., handles rotating impossibly, objects floating, unnatural joint movements)
   - Human body parts bending in anatomically impossible ways
   - Objects passing through each other or defying gravity
   - Unnatural momentum or inertia violations

2. **Motion Inconsistencies**:
   - Objects or people moving at different speeds than their force would allow
   - Jerky, unnatural motion patterns or impossible coordination
   - Impossibly smooth or perfectly synchronized movements (too robotic)
   - Temporal glitches where objects appear to teleport or skip frames unnaturally

3. **Physical Reality Violations**:
   - Objects with impossible weight distribution or balance
   - Hair, clothing, or flexible materials moving against physics
   - Liquids or fluids with impossible behavior
   - Objects maintaining impossible shapes or positions

4. **Data and Temporal Inconsistencies**:
   - Objects appearing/disappearing between frames
   - Illogical cause-and-effect (e.g., action happens before its cause)
   - Objects changing properties inconsistently
   - Mathematically perfect motion patterns (unnaturally smooth/robotic)

5. **Anatomical and Biological Impossibilities**:
   - Facial features morphing or shifting unnaturally during movement (not just expressions)
   - ANATOMICALLY IMPOSSIBLE hand/finger positions (joints bending backwards, fingers in physically impossible angles)
   - Body parts moving in ways that violate joint mechanics
   - Unnatural eye movements or blinks (not just camera angle making hands look unusual)
   
   CRITICAL: A hand looking "unusual" from angle or editing is NOT an anatomical impossibility.
   Only flag if joints are bending in ways that are PHYSICALLY IMPOSSIBLE for human anatomy.

MINOR INDICATORS (Ignore unless very severe):
- Lighting inconsistencies (only if clearly impossible for the physics shown)
- Edge artifacts or blurring (ignore minor cases) 
- Background anomalies (ignore unless showing impossible movement)

CRITICAL: DO NOT FLAG THESE AS FAKE (Normal Video Editing):
- Cooking videos with cuts, speed changes, or editing transitions
- DIY videos with jump cuts or timegaps
- Videos with intentional camera movements or shake
- Videos with color grading, LUTs, or cinematic effects
- Videos with text overlays, graphics, or annotations
- Videos with smooth pouring motions (this is normal editing/positioning)
- Hand positioning that might look unusual but is physically possible
- Materials that look slightly unusual (different materials exist)
- Perfect precision in actions (skilled humans or multiple takes create this)

ONLY FLAG AS FAKE if:
1. Motion is PHYSICALLY IMPOSSIBLE (not just unusual)
2. Multiple HIGH severity issues that cannot be explained by editing
3. Clear evidence of AI generation (morphing faces, impossible physics)

{context_info}
Provide your analysis in the following JSON format:
{{
    "confidence_score": <float 0.0 (clearly real/normal editing) to 1.0 (clearly AI/impossible). 
                        Use 0.0-0.3 for "unusual but explainable", 0.7+ only for clear impossibilities>,
    "is_likely_fake": <boolean>,
    "inconsistencies": [
        {{
            "type": "<specific physical impossibility or motion violation>",
            "severity": "<low|medium|high - based on how impossible the motion is>",
            "description": "<detailed description of the PHYSICAL IMPOSSIBILITY - what makes this movement physically wrong?>",
            "location": "<area of frame where detected>"
        }}
    ],
    "reasoning": "<detailed explanation focusing on physical impossibilities, motion violations, and why the movement defies physics>"
}}

CRITICAL INSTRUCTIONS:
- Only flag inconsistencies if they represent PHYSICAL IMPOSSIBILITIES or CLEAR MOTION VIOLATIONS
- Ignore minor lighting, edge artifacts, or background issues unless they directly indicate physical impossibility
- Real videos can have lighting quirks; AI often creates physically impossible motions
- Focus on: "Is this motion physically possible?" not "Does the lighting look off?"
- Be strict: Only report issues where physics/motion is clearly violated"""
        
        # Prepare the API request payload
        payload = {
            "model": self.model_name,
            "messages": [
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": prompt
                        },
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/jpeg;base64,{image_base64}"
                            }
                        }
                    ]
                }
            ],
            "temperature": 0.1,  # Lower temperature for more consistent results
            "max_tokens": 2048
        }
        
        # Headers for NIM API
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        try:
            logger.info(f"Sending frame analysis request to NIM API (model: {self.model_name})")
            
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(
                    self.api_endpoint,
                    json=payload,
                    headers=headers
                )
                response.raise_for_status()
                
                result = response.json()
                
                # Extract the response content
                if "choices" not in result or len(result["choices"]) == 0:
                    raise ValueError("Invalid API response: no choices found")
                
                content = result["choices"][0]["message"]["content"]
                
                logger.debug(f"NIM API response received: {content[:200]}...")
                
                return {
                    "raw_response": content,
                    "full_response": result
                }
                
        except httpx.HTTPStatusError as e:
            logger.error(f"HTTP error from NIM API: {e.response.status_code} - {e.response.text}")
            raise
        except httpx.TimeoutException:
            logger.error("NIM API request timed out")
            raise
        except Exception as e:
            logger.error(f"Unexpected error calling NIM API: {e}")
            raise

    async def analyze_text(self, text: str, title: Optional[str] = None) -> Dict[str, Any]:
        """Analyze text/article for misinformation using a reasoning model.
        Returns raw response content and full response."""
        context = ""
        if title:
            context += f"Title: {title}\n"

        prompt = f"""You are a professional fact-checking system.
Analyze the following article/claim for misinformation. Extract checkable claims, verify them using reliable knowledge, and provide a concise summary.

INPUT METADATA\n{context}

STRICT JSON OUTPUT ONLY:\n{{
  "overall_verdict": "<LIKELY_FAKE|LIKELY_REAL|INCONCLUSIVE>",
  "confidence": <0.0-1.0>,
  "key_findings": ["..."],
  "claims": [{{"text":"...","span":[start,end],"salience":0.0}}],
  "sources": [{{"title":"...","url":"...","source":"...","snippet":"..."}}],
  "reasoning": "<short reasoning>",
  "executive_summary": "<2-3 sentences>"
}}

TEXT:\n{text}
"""

        payload = {
            "model": getattr(settings, "nim_model_name", "meta/llama-3.1-70b-instruct"),
            "messages": [{"role": "user", "content": [{"type": "text", "text": prompt}]}],
            "temperature": 0.2,
            "max_tokens": 2048
        }

        headers = {"Authorization": f"Bearer {self.api_key}", "Content-Type": "application/json"}

        async with httpx.AsyncClient(timeout=self.timeout) as client:
            response = await client.post(self.api_endpoint, json=payload, headers=headers)
            response.raise_for_status()
            result = response.json()
            if "choices" not in result or not result["choices"]:
                raise ValueError("Invalid NIM response: no choices")
            content = result["choices"][0]["message"]["content"]
            return {"raw_response": content, "full_response": result}

    async def analyze_frame_sequence(
        self,
        frames: List[Image.Image],
        timestamps: List[float],
        video_id: Optional[str] = None,
        video_title: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Analyze a sequence of consecutive frames for temporal inconsistencies.
        This catches AI artifacts that single-frame analysis misses.
        
        Args:
            frames: List of PIL Image objects (3-5 consecutive frames)
            timestamps: List of timestamps corresponding to each frame
            video_id: Optional YouTube video ID
            video_title: Optional video title
            
        Returns:
            Dictionary containing temporal analysis results
        """
        if len(frames) != len(timestamps):
            raise ValueError("Number of frames must match number of timestamps")
        
        if len(frames) < 2:
            raise ValueError("Need at least 2 frames for temporal analysis")
        
        # Convert all frames to base64
        frame_base64_list = []
        for frame in frames:
            buffer = BytesIO()
            frame.save(buffer, format="JPEG", quality=85)
            image_bytes = buffer.getvalue()
            frame_base64_list.append(base64.b64encode(image_bytes).decode("utf-8"))
        
        # Calculate frame intervals
        frame_interval = (timestamps[-1] - timestamps[0]) / (len(timestamps) - 1) if len(timestamps) > 1 else 0.2
        frame_interval_ms = frame_interval * 1000
        
        # Construct context info
        context_info = ""
        if video_title:
            context_info += f"Video Title: {video_title}\n"
        if video_id:
            context_info += f"Video ID: {video_id}\n"
        context_info += f"Frame Sequence: {len(frames)} frames, {frame_interval_ms:.0f}ms apart\n"
        context_info += f"Timestamps: {', '.join([f'{t:.2f}s' for t in timestamps])}\n"
        
        prompt = f"""You are analyzing a SEQUENCE of {len(frames)} consecutive video frames taken {frame_interval_ms:.0f}ms apart.

PRIMARY TASK: Detect TEMPORAL INCONSISTENCIES and MOTION VIOLATIONS across frames.

CRITICAL: Compare frames frame-by-frame to detect physically impossible transitions.

FRAME-TO-FRAME ANALYSIS CHECKLIST:
1. **Motion Continuity**: Does object motion follow physics between frames?
   - Check velocity consistency (sudden speed changes without force)
   - Check trajectory logic (objects changing direction impossibly)
   - Verify momentum is maintained (objects can't accelerate without force)

2. **Object Persistence**: Do objects maintain identity across frames?
   - Objects appearing/vanishing without reason
   - Objects morphing shape unnaturally between frames
   - Parts of objects becoming inconsistent or glitching

3. **Spatial Coherence**: Do positions make sense frame-to-frame?
   - Objects teleporting (position jumps that exceed possible speed)
   - Depth inconsistencies (things moving wrong in 3D space)
   - Scale changes that don't match perspective or distance

4. **Physical Realism**: Does physics hold between frames?
   - Gravity violations (things falling up, floating without support)
   - Impossible joint movements (limbs bending wrong, anatomically impossible)
   - Material behavior violations (solid objects bending like fluid)
   - Objects passing through each other

5. **Causal Consistency**: Do actions have proper cause-effect?
   - Effects happening before causes (impossible timing)
   - Reactions without proper timing or force application
   - Missing intermediate states (objects skipping physical steps)

6. **Anatomical Continuity**: For people/faces, does anatomy make sense?
   - Face features shifting unnaturally during speech/movement
   - Impossible hand/finger positions between frames
   - Body parts that don't move realistically together
   - Facial expressions changing in physically impossible ways

IGNORE THESE (NOT AI ARTIFACTS - Real video can have these):
- Color grading or filters applied consistently across frames
- Intentional effects like beauty filters, Instagram filters, TikTok effects
- Compression artifacts (blocky pixels, slight blur) - if consistent
- Camera shake or motion blur from camera movement
- Depth of field blur (background/foreground blurring)
- Legitimate cuts or transitions (sudden scene changes are OK)
- Intentional speed changes (slow-motion, time-lapse)
- Green screen backgrounds (if chroma keying is consistent)
- Text overlays, emojis, or graphic elements

CRITICAL: Only flag issues if they represent IMPOSSIBLE PHYSICS or TEMPORAL GLITCHES.
Real videos with filters are NOT fake. Focus on what's PHYSICALLY IMPOSSIBLE between frames.

{context_info}
Provide your analysis in the following JSON format:
{{
    "confidence_score": <float between 0.0 (clearly real/physical) and 1.0 (clearly AI-generated/impossible)>,
    "is_likely_fake": <boolean>,
    "temporal_inconsistencies": [
        {{
            "frame_range": "<timestamp range where issue occurs>",
            "type": "<specific temporal violation>",
            "severity": "<low|medium|high>",
            "description": "<detailed description of the PHYSICAL IMPOSSIBILITY between frames>",
            "affected_frames": [<list of frame indices where issue visible>],
            "location": "<area of frame where detected>"
        }}
    ],
    "frame_by_frame_notes": [
        "Frame 0→1: [observation]",
        "Frame 1→2: [observation]",
        ...
    ],
    "reasoning": "<detailed explanation focusing on temporal inconsistencies, motion violations, and why transitions defy physics>",
    "summary": "<2-3 sentence executive summary for investors>"
}}

IMPORTANT SCORING RULES:
1. If you say "could be", "might be", "unusual but" → confidence_score = 0.0-0.3
2. If you say "impossible", "violates", "defies" → confidence_score = 0.7-1.0
3. Cooking/DIY videos with smooth motions or edited cuts → confidence_score = 0.0-0.2 (NOT fake)
4. Normal video editing quirks → confidence_score = 0.0-0.2 (NOT fake)

Be VERY strict - only report PHYSICAL IMPOSSIBILITIES. Real videos can have visual quirks."""
        
        # Prepare content array with all frames
        content = [
            {
                "type": "text",
                "text": prompt
            }
        ]
        
        # Add all frames as image content
        for i, frame_base64 in enumerate(frame_base64_list):
            content.append({
                "type": "text",
                "text": f"Frame {i+1} (timestamp: {timestamps[i]:.2f}s):"
            })
            content.append({
                "type": "image_url",
                "image_url": {
                    "url": f"data:image/jpeg;base64,{frame_base64}"
                }
            })
        
        payload = {
            "model": self.model_name,
            "messages": [
                {
                    "role": "user",
                    "content": content
                }
            ],
            "temperature": 0.1,
            "max_tokens": 4096  # More tokens for detailed temporal analysis
        }
        
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        try:
            logger.info(f"Analyzing frame sequence ({len(frames)} frames) for temporal inconsistencies")
            
            async with httpx.AsyncClient(timeout=self.timeout * 2) as client:  # Longer timeout for sequences
                response = await client.post(
                    self.api_endpoint,
                    json=payload,
                    headers=headers
                )
                response.raise_for_status()
                
                result = response.json()
                
                if "choices" not in result or len(result["choices"]) == 0:
                    raise ValueError("Invalid API response: no choices found")
                
                content_response = result["choices"][0]["message"]["content"]
                
                logger.debug(f"Frame sequence analysis received: {content_response[:300]}...")
                
                return {
                    "raw_response": content_response,
                    "full_response": result
                }
                
        except httpx.HTTPStatusError as e:
            logger.error(f"HTTP error from NIM API during sequence analysis: {e.response.status_code}")
            raise
        except httpx.TimeoutException:
            logger.error("NIM API request timed out during sequence analysis")
            raise
        except Exception as e:
            logger.error(f"Unexpected error in frame sequence analysis: {e}")
            raise


def extract_json_from_response(text: str) -> Dict[str, Any]:
    """
    Extract JSON from model response text, handling markdown code blocks.
    
    Args:
        text: Response text that may contain JSON in code blocks
        
    Returns:
        Parsed JSON dictionary
        
    Raises:
        ValueError: If JSON cannot be extracted or parsed
    """
    import json
    import re
    
    # Try to extract JSON from markdown code blocks
    json_match = re.search(r'```(?:json)?\s*(\{.*?\})\s*```', text, re.DOTALL)
    if json_match:
        json_str = json_match.group(1)
    else:
        # Try to find JSON object directly
        json_match = re.search(r'\{.*\}', text, re.DOTALL)
        if json_match:
            json_str = json_match.group(0)
        else:
            raise ValueError("No JSON found in response")
    
    try:
        return json.loads(json_str)
    except json.JSONDecodeError as e:
        logger.error(f"Failed to parse JSON from response: {e}")
        logger.debug(f"JSON string: {json_str}")
        raise ValueError(f"Invalid JSON in response: {str(e)}")

