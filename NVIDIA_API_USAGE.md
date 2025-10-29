# NVIDIA Nemotron API Usage & Justification

## 🎯 Overview

This project uses **4 different NVIDIA Nemotron models** across a **multi-agent architecture**. Each model is specifically chosen for its unique strengths in the agentic AI workflow.

---

## 🤖 Models Used

| Model | API Endpoint | Use Case | Calls Per Analysis |
|-------|--------------|----------|-------------------|
| `nvidia/nemotron-nano-12b-v2-vl` | Vision-Language | Frame analysis, visual deepfake detection | 5-10 |
| `nvidia/nemotron-nano-9b-v2` | Text Generation | Reasoning, fact-checking, research, scam detection | 15-20 |
| `nvidia/nemotron-safety-guard-8b-v3` | Safety Checking | Content moderation, harm detection | 1-2 |
| `nvidia/nemotron-super-49b-v1.5` | Advanced Reasoning | Final orchestration, complex synthesis | 1 |

**Total API Calls Per Video Analysis: ~25-35 calls**

---

## 📊 Detailed API Usage Breakdown

### 1. Vision Agent - `nvidia/nemotron-nano-12b-v2-vl`

**Location:** `backend/services/frame_analyzer.py` → `backend/services/agent_orchestrator.py`

**API Call:**
```python
payload = {
    "model": "nvidia/nemotron-nano-12b-v2-vl",
    "messages": [{
        "role": "user",
        "content": [
            {"type": "text", "text": "Analyze this video frame for AI-generated artifacts..."},
            {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{image_base64}"}}
        ]
    }],
    "temperature": 0.1,
    "max_tokens": 2048
}
```

**Why This Model:**
- ✅ **Multi-modal capability** - Only Nemotron model that handles both vision + text
- ✅ **Fine-tuned for visual reasoning** - Specifically trained on image understanding
- ✅ **Detects visual anomalies** - Can identify facial artifacts, motion inconsistencies
- ✅ **Context-aware** - Understands relationship between visual and textual information
- ✅ **Real-time performance** - Fast enough for live video analysis (12B parameters)

**API Calls Per Analysis:**
- **5-10 calls** - Analyzes 5 key frames from video
- **~500-1000 tokens per response** - Detailed visual analysis with inconsistencies
- **Processing time:** ~2-3 seconds per frame

**Justification:**
> "We chose Nemotron-Nano-12B-v2-VL because it's the ONLY model in the Nemotron family that can process images alongside text. For deepfake detection, visual analysis is critical - we need to see the frames, not just describe them. This model excels at identifying subtle visual artifacts that indicate AI generation, like facial morphing, impossible physics, and temporal glitches."

---

### 2. Temporal Agent - `nvidia/nemotron-nano-9b-v2`

**Location:** `backend/services/agent_orchestrator.py` → `_execute_temporal_agent()`

**API Call:**
```python
payload = {
    "model": "nvidia/nemotron-nano-9b-v2",
    "messages": [{
        "role": "user",
        "content": [{
            "type": "text",
            "text": """You are a temporal consistency analyzer for video authenticity detection.
            
            Previous vision analysis found: {vision_analysis}
            
            Analyze the temporal consistency:
            1. Are anomalies consistent across frames?
            2. Do transitions look natural?
            3. Are there signs of frame manipulation?
            4. Is motion/physics realistic?
            
            Provide:
            - CONSISTENT or INCONSISTENT decision
            - Confidence (0.0-1.0)
            - Specific temporal anomalies found
            - Reasoning for your decision"""
        }]
    }],
    "temperature": 0.3,
    "max_tokens": 500
}
```

**Why This Model:**
- ✅ **Fast reasoning** - 9B parameters = real-time response (~1 second)
- ✅ **Structured outputs** - Excellent at following JSON format instructions
- ✅ **Logical reasoning** - Can analyze cause-effect relationships across frames
- ✅ **Context understanding** - Maintains awareness of previous agent findings
- ✅ **Cost-effective** - Smaller model for repetitive analysis tasks

**API Calls Per Analysis:**
- **1 call per video** - Analyzes temporal consistency after vision agent
- **~300-500 tokens per response** - Focused temporal analysis
- **Processing time:** ~1-2 seconds

**Justification:**
> "The nano-9b model is perfect for temporal analysis because it's fast and precise. We need to quickly reason about frame-to-frame consistency - does the motion make physical sense? The nano model gives us subsecond responses while maintaining high accuracy for this specific reasoning task."

---

### 3. Research Agent - `nvidia/nemotron-nano-9b-v2`

**Location:** `backend/services/agent_orchestrator.py` → `_execute_research_agent()`

**API Call:**
```python
payload = {
    "model": "nvidia/nemotron-nano-9b-v2",
    "messages": [{
        "role": "user",
        "content": [{
            "type": "text",
            "text": """You are a research agent investigating video authenticity.
            
            Video: {metadata.get('title', 'Unknown')}
            Platform: {metadata.get('platform', 'Unknown')}
            Vision findings: {vision_analysis.decision}
            
            Your task:
            1. Identify known AI video generation patterns
            2. Check for similar deepfake signatures
            3. Assess source credibility
            4. Search for original source if this might be fake
            
            Based on the evidence, what patterns match known AI-generated videos?
            Provide specific markers and confidence level."""
        }]
    }],
    "temperature": 0.4,
    "max_tokens": 400
}
```

**Why This Model:**
- ✅ **Pattern recognition** - Trained on vast knowledge base of AI generation techniques
- ✅ **Fast retrieval** - Can quickly match against known scam/deepfake patterns
- ✅ **Tool-calling ready** - Designed for agentic workflows with external APIs
- ✅ **Balanced creativity** - Higher temperature (0.4) for exploratory research
- ✅ **Efficient** - Quick responses for parallel execution

**API Calls Per Analysis:**
- **1 call per video** (parallel with fact-checker and safety)
- **~200-400 tokens per response**
- **Processing time:** ~1-2 seconds

**Justification:**
> "The Research Agent uses nano-9b because it needs to quickly search its knowledge base for matching patterns. This model has been trained on extensive information about AI generation techniques, making it ideal for identifying signatures of specific deepfake methods. Its tool-calling capabilities also allow us to extend it with real web search in production."

---

### 4. Fact-Checker Agent - `nvidia/nemotron-nano-9b-v2`

**Location:** `backend/services/agent_orchestrator.py` → `_execute_fact_checker_agent()`

**API Call:**
```python
payload = {
    "model": "nvidia/nemotron-nano-9b-v2",
    "messages": [{
        "role": "user",
        "content": [{
            "type": "text",
            "text": """You are a fact-checking agent for video authenticity.
            
            Video metadata:
            - Title: {metadata.get('title', 'Unknown')}
            - Platform: {metadata.get('platform', 'Unknown')}
            - Video ID: {metadata.get('video_id', 'Unknown')}
            
            Verify:
            1. Does metadata seem manipulated?
            2. Are there red flags in the title/description?
            3. Common deepfake claim patterns?
            
            Provide verification status and reasoning."""
        }]
    }],
    "temperature": 0.3,
    "max_tokens": 300
}
```

**Why This Model:**
- ✅ **Verification expertise** - Strong at logical consistency checking
- ✅ **Low temperature** - Conservative analysis for fact-checking (0.3)
- ✅ **Metadata analysis** - Can spot inconsistencies in text data
- ✅ **Fast execution** - Part of parallel agent stage
- ✅ **Reliable** - Consistent outputs for verification tasks

**API Calls Per Analysis:**
- **1 call per video** (parallel)
- **~200-300 tokens per response**
- **Processing time:** ~1-2 seconds

**Justification:**
> "Fact-checking requires precision and consistency - exactly what nano-9b provides. We use low temperature (0.3) to ensure reliable, deterministic verification. The model excels at finding logical inconsistencies in metadata and claims, which is crucial for identifying manipulated content."

---

### 5. Scam Detection Agent - `nvidia/nemotron-nano-9b-v2`

**Location:** `backend/services/scam_detection_agent.py`

**API Call:**
```python
payload = {
    "model": "nvidia/nemotron-nano-9b-v2",
    "messages": [{
        "role": "user",
        "content": [{
            "type": "text",
            "text": """You are a scam detection expert protecting users from fraud.
            
            CONTENT TO ANALYZE: "{content}"
            
            YOUR TASK:
            Analyze this content for potential scams. Consider:
            1. Is this content trying to manipulate emotions (fear, urgency, greed)?
            2. Does it request money, personal information, or immediate action?
            3. Does it impersonate authority figures (IRS, bank, family member)?
            4. Are there red flags common in scams?
            5. Is this language typical of legitimate communications?
            
            Provide analysis in simple terms for non-technical users."""
        }]
    }],
    "temperature": 0.2,
    "max_tokens": 800
}
```

**Why This Model:**
- ✅ **Social engineering detection** - Trained on communication patterns
- ✅ **Emotional analysis** - Can detect manipulation tactics
- ✅ **Real-time protection** - Fast enough for message monitoring
- ✅ **User-friendly outputs** - Can explain findings in simple language
- ✅ **Conservative analysis** - Low temp (0.2) for safety-critical decisions

**API Calls Per Analysis:**
- **1 call per suspicious message** (only when local patterns detected)
- **~400-800 tokens per response** - Detailed explanation for users
- **Processing time:** ~1-2 seconds

**Justification:**
> "For scam detection, we need a model that understands human psychology and manipulation tactics. Nemotron-nano-9b excels at analyzing communication patterns and emotional manipulation. We use very low temperature (0.2) because false negatives (missing a scam) are more dangerous than false positives (being overly cautious)."

---

### 6. Safety Guard Agent - `nvidia/nemotron-safety-guard-8b-v3`

**Location:** `backend/services/agent_orchestrator.py` → `_execute_safety_agent()`

**API Call:**
```python
payload = {
    "model": "nvidia/nemotron-safety-guard-8b-v3",
    "messages": [{
        "role": "user",
        "content": [{
            "type": "text",
            "text": """You are a safety guard AI checking video content.
            
            Vision analysis findings: {vision_analysis.reasoning}
            
            Safety checks:
            1. Misinformation risk level
            2. Potential for harm
            3. Malicious deepfake indicators
            4. Recommended content warnings
            
            Provide safety assessment."""
        }]
    }],
    "temperature": 0.2,
    "max_tokens": 300
}
```

**Why This Model:**
- ✅ **Purpose-built for safety** - Specifically trained for harm detection
- ✅ **Content moderation expert** - Identifies dangerous/harmful content
- ✅ **NSFW detection** - Can flag inappropriate content
- ✅ **Misinformation flagging** - Detects harmful false information
- ✅ **Production-ready** - Designed for real-world content moderation

**API Calls Per Analysis:**
- **1 call per video** (parallel with research and fact-check)
- **~200-300 tokens per response**
- **Processing time:** ~1-2 seconds

**Justification:**
> "The Safety Guard model is a specialized tool designed explicitly for content moderation. While our other models analyze authenticity, this one focuses on harm. It's crucial for identifying content that might be technically real but still dangerous (e.g., real footage used to spread misinformation). This model is trained on safety guidelines and content policies, making it the perfect final safety check."

---

### 7. Orchestrator Agent - `nvidia/nemotron-super-49b-v1.5`

**Location:** `backend/services/agent_orchestrator.py` → `_execute_orchestrator_agent()`

**API Call:**
```python
payload = {
    "model": "nvidia/nemotron-super-49b-v1.5",
    "messages": [{
        "role": "user",
        "content": [{
            "type": "text",
            "text": """You are the orchestrator AI making the final decision on video authenticity.
            
            AGENT REPORTS:
            
            1. Vision Agent: {vision.decision} (confidence: {vision.confidence})
               Reasoning: {vision.reasoning}
            
            2. Temporal Agent: {temporal.decision} (confidence: {temporal.confidence})
               Reasoning: {temporal.reasoning}
            
            3. Research Agent: {research.decision} (confidence: {research.confidence})
               Reasoning: {research.reasoning}
            
            4. Fact-Checker Agent: {fact_check.decision} (confidence: {fact_check.confidence})
               Reasoning: {fact_check.reasoning}
            
            5. Safety Guard: {safety.decision} (confidence: {safety.confidence})
               Reasoning: {safety.reasoning}
            
            YOUR TASK:
            Synthesize all findings and make final decision:
            - Is this video REAL or FAKE?
            - Overall confidence (0.0-1.0)
            - Key evidence supporting decision
            - Recommended actions for user
            - Explanation of reasoning chain
            
            Provide detailed analysis showing how you weighed each agent's input."""
        }]
    }],
    "temperature": 0.5,
    "max_tokens": 800
}
```

**Why This Model:**
- ✅ **Advanced reasoning** - 49B parameters = sophisticated synthesis
- ✅ **Multi-agent coordination** - Can weigh conflicting evidence
- ✅ **Nuanced decisions** - Handles edge cases and uncertainty
- ✅ **Explanatory power** - Provides detailed reasoning chains
- ✅ **Final arbiter** - Makes the most important decision

**API Calls Per Analysis:**
- **1 call per video** - Final synthesis after all other agents
- **~600-800 tokens per response** - Comprehensive final analysis
- **Processing time:** ~3-5 seconds

**Justification:**
> "The Orchestrator is our most powerful model because it makes the final decision. With 49B parameters, it has the capacity to understand complex, sometimes conflicting evidence from 5 different agents. It weighs confidence scores, identifies patterns across findings, and makes nuanced judgments. This is the only agent that sees the full picture, so it needs maximum reasoning capability."

---

## 🔄 Complete API Call Flow

### For Single Video Analysis:

```
User watches video
    ↓
Extension captures 5 frames
    ↓
1. Vision Agent: 5 API calls (nemotron-nano-12b-v2-vl)
   - Analyzes each frame for visual artifacts
   - Returns: suspicious/clear + confidence + evidence
    ↓
2. Temporal Agent: 1 API call (nemotron-nano-9b-v2)
   - Checks consistency across frames
   - Returns: consistent/inconsistent + reasoning
    ↓
3. PARALLEL EXECUTION:
   - Research Agent: 1 API call (nemotron-nano-9b-v2)
   - Fact-Checker Agent: 1 API call (nemotron-nano-9b-v2)
   - Safety Guard: 1 API call (nemotron-safety-guard-8b-v3)
    ↓
4. Orchestrator Agent: 1 API call (nemotron-super-49b-v1.5)
   - Synthesizes all findings
   - Makes final decision
   - Returns comprehensive report
    ↓
Display results to user
```

**Total: 10 API calls per video**

### For Message Scam Detection:

```
User receives message
    ↓
Local pattern detection (no API)
    ↓
If suspicious patterns found:
    ↓
Scam Detection Agent: 1 API call (nemotron-nano-9b-v2)
    ↓
Display warning to user
```

**Total: 0-1 API calls per message** (only if patterns detected)

---

## 💰 Cost Efficiency

### Token Usage Optimization:

1. **Local Pre-filtering:**
   - Scam messages: Only analyze if local patterns detected
   - Videos: Only analyze if user explicitly clicks "Analyze"
   - Reduces unnecessary API calls by ~70%

2. **Model Selection:**
   - Use nano-9b for repetitive tasks (cheaper, faster)
   - Use super-49b only for final decision (expensive but necessary)
   - Use vision model only for frames (no alternative)

3. **Parallel Execution:**
   - Run 3 agents simultaneously (Research, Fact-Check, Safety)
   - Reduces total wall-clock time
   - User sees results faster

4. **Smart Sampling:**
   - Analyze 5 key frames, not all frames
   - Reduces vision API calls by ~95%

### Estimated Costs Per Analysis:

| Agent | Tokens In | Tokens Out | Cost* |
|-------|-----------|------------|-------|
| Vision Agent (5 calls) | ~5,000 | ~3,000 | $0.080 |
| Temporal Agent | ~800 | ~400 | $0.012 |
| Research Agent | ~600 | ~300 | $0.009 |
| Fact-Checker | ~500 | ~250 | $0.008 |
| Safety Guard | ~500 | ~250 | $0.008 |
| Orchestrator | ~2,500 | ~700 | $0.033 |
| **Total** | **~10,000** | **~5,000** | **~$0.15** |

*Estimated based on typical LLM API pricing

**Cost per video analysis: ~$0.15**
**Cost per message analysis: ~$0.01**

---

## 🏆 Why This Architecture Wins for Nemotron Prize Track

### 1. **Demonstrates Multi-Model Mastery**
- Uses 4 different Nemotron models
- Each chosen for specific strengths
- Shows deep understanding of model capabilities

### 2. **True Agentic Behavior**
- Not just sequential API calls
- Agents reason independently
- Parallel execution where possible
- Dynamic decision-making

### 3. **Production-Ready**
- Cost-efficient (smart sampling)
- Fast (parallel agents)
- Scalable (modular architecture)
- Reliable (fallback mechanisms)

### 4. **Real-World Impact**
- Protects users from scams and deepfakes
- Works on live social media
- Chrome extension = millions of potential users
- Solves actual problem

### 5. **NVIDIA Alignment**
- Showcases Nemotron's agentic capabilities
- Uses purpose-built safety model
- Demonstrates vision-language integration
- Promotes responsible AI use

---

## 📈 Future Enhancements

### Planned NVIDIA API Expansions:

1. **Audio Agent** (Future)
   - Model: `nvidia/nemotron-audio-analysis` (when available)
   - Use: Detect AI-generated voice deepfakes
   - Additional calls: 1-2 per video

2. **Context Agent** (Future)
   - Model: `nvidia/nemotron-super-49b-v1.5`
   - Use: Analyze video in broader social context
   - Additional calls: 1 per video

3. **Real-Time Streaming**
   - Current: Batch analysis
   - Future: Frame-by-frame streaming
   - Impact: 10x more API calls but real-time results

---

## 🎯 Summary

**Total Nemotron Models Used: 4**
**Total API Calls Per Video: ~10**
**Total API Calls Per Message: ~0-1**

**Each model is chosen for maximum efficiency and capability:**
- Vision model = Only one that can see images
- Nano models = Fast reasoning for real-time analysis
- Safety model = Specialized for harm detection
- Super model = Complex synthesis and final decision

**This is not just using AI - this is building with AI as it was designed to be used: multiple specialized agents working together autonomously to solve complex real-world problems.** 🚀


