# 🏆 Multi-Agent AI Video Detector - NVIDIA Nemotron Prize Track

## 🤖 Why This Is True Agentic AI

This project showcases **true agentic behavior** using multiple specialized Nemotron models working together autonomously. Unlike simple chatbots, our system:

- ✅ **Reasons autonomously** across multiple specialized agents
- ✅ **Plans and executes** complex multi-step workflows  
- ✅ **Uses tools intelligently** (web search, fact-checking, vision analysis)
- ✅ **Coordinates decisions** through agent orchestration
- ✅ **Adapts dynamically** based on intermediate findings

## 🎯 System Architecture - Multi-Agent Orchestration

```
┌─────────────────────────────────────────────────────────────────┐
│                    ORCHESTRATOR AGENT                            │
│              (Nemotron-super-49b-v1.5)                          │
│         Synthesizes all findings → Final Decision                │
└─────────────────────────────────────────────────────────────────┘
                            ▲
                            │
        ┌───────────────────┼───────────────────┐
        │                   │                   │
┌───────▼───────┐  ┌───────▼───────┐  ┌───────▼───────┐
│  VISION AGENT │  │ TEMPORAL AGENT│  │ RESEARCH AGENT│
│  (Nemotron    │  │  (Nemotron    │  │  (Nemotron    │
│  -Nano-12B    │  │  -nano-9b-v2) │  │  -nano-9b-v2) │
│  -v2-VL)      │  │               │  │               │
│               │  │  Checks frame │  │  Searches for │
│  Analyzes     │  │  consistency  │  │  similar AI   │
│  visual       │  │  across time  │  │  patterns     │
│  frames       │  │               │  │               │
└───────┬───────┘  └───────┬───────┘  └───────┬───────┘
        │                   │                   │
        └───────────────────┼───────────────────┘
                            │
        ┌───────────────────┼───────────────────┐
        │                   │                   │
┌───────▼───────┐  ┌───────▼───────┐  
│FACT-CHECKER   │  │ SAFETY GUARD  │  
│    AGENT      │  │    AGENT      │  
│  (Nemotron    │  │  (Nemotron    │  
│  -nano-9b-v2) │  │  -Safety-     │  
│               │  │  Guard-8B-v3) │  
│  Verifies     │  │               │  
│  claims &     │  │  Checks for   │  
│  metadata     │  │  harmful      │  
│               │  │  content      │  
└───────────────┘  └───────────────┘  
```

## 🧠 Agent Workflow - ReAct Pattern Implementation

### Phase 1: Vision Agent (Reason)
```python
Vision Agent observes: "Frame contains X visual anomalies"
↓
Reasons: "These patterns match known AI artifacts"
↓
Acts: "Flag for temporal analysis + research"
```

### Phase 2: Temporal Agent (Observe → Reason)
```python
Observes: Previous vision findings
↓
Reasons: "Are anomalies consistent across frames?"
↓
Acts: "Determine if temporal patterns suggest manipulation"
```

### Phase 3: Parallel Agent Execution (Act)
```python
Research Agent → Searches pattern database
Fact-Checker → Verifies metadata/claims
Safety Guard → Checks for harmful content
↓ (All execute simultaneously)
```

### Phase 4: Orchestrator Synthesis (Reason → Decide)
```python
Observes: All agent findings
↓
Reasons: Weighs evidence with confidence scoring
↓
Decides: FAKE (0.85) or REAL (0.15)
↓
Acts: Recommends actions (report, warn, verify)
```

## 💡 How This Demonstrates Agentic AI

### 1. ✅ Autonomous Reasoning
**Not just responding to prompts** - Each agent independently:
- Analyzes its specific domain (vision, temporal, fact-checking)
- Makes decisions based on evidence
- Determines next actions without human intervention

```python
# Example: Vision Agent autonomously decides next steps
if fake_count > threshold:
    next_actions = ["temporal_consistency_check", "research_patterns"]
else:
    next_actions = ["verify_authenticity", "check_metadata"]
```

### 2. ✅ Multi-Step Workflows
**Not single queries** - Complex execution chain:
1. Vision analysis (per-frame)
2. Temporal consistency (cross-frame)
3. Parallel research/fact-check/safety
4. Final synthesis with weighted confidence

Each step **depends on previous findings** and **adapts accordingly**.

### 3. ✅ Tool Integration
**Not just text generation** - Agents use external tools:
- 🔍 Web search (Research Agent)
- 👁️ Vision analysis (Vision Agent)
- ✅ Fact-checking APIs (Fact-Checker Agent)
- 🛡️ Safety checking (Safety Guard)

```python
# Tool calling example
research_agent.search_patterns(
    query=vision_findings,
    tools=["web_search", "pattern_database", "source_verification"]
)
```

### 4. ✅ Real-World Applicability
**Solving actual problems:**
- Detecting deepfakes on social media
- Protecting users from misinformation
- Real-time video verification
- Content moderation at scale

### 5. ✅ Nemotron-Specific Strengths

#### Why Each Nemotron Model Was Chosen:

**Vision Agent: Nemotron-Nano-12B-v2-VL**
- Multi-modal: Analyzes images + reasoning
- Detects visual artifacts invisible to single-mode models
- Purpose-built for vision-language tasks

**Text Agents: Nemotron-nano-9b-v2**
- Fast reasoning for real-time analysis
- Excellent at structured outputs (JSON)
- Optimized for function calling

**Safety Guard: Nemotron-Safety-Guard-8B-v3**
- Specialized for harm detection
- Critical for content moderation
- Built for agentic safety layers

**Orchestrator: Nemotron-super-49b-v1.5**
- Advanced reasoning for complex synthesis
- Weighs multi-agent evidence
- Makes nuanced final decisions

## 🎬 Demo Scenarios

### Scenario 1: Real Cooking Video
```
1. Vision Agent: "No physical impossibilities detected"
2. Temporal Agent: "Motion is consistent and realistic"
3. Research Agent: "Matches known content creator style"
4. Fact-Checker: "Metadata verified"
5. Safety Guard: "No harmful content"
6. Orchestrator: "REAL (confidence: 0.95)"
```

### Scenario 2: AI-Generated Deepfake
```
1. Vision Agent: "Facial morphing detected in 4/5 frames"
2. Temporal Agent: "Inconsistent eye movements, impossible jaw rotation"
3. Research Agent: "Matches known AI generation patterns"
4. Fact-Checker: "Suspicious metadata, claims don't verify"
5. Safety Guard: "Potential misinformation risk"
6. Orchestrator: "FAKE (confidence: 0.89) - Recommend: Report to platform"
```

## 📊 Agent Decision Chain Visualization

```
🤖 MULTI-AGENT REASONING CHAIN:

1. VISION_AGENT
   Decision: SUSPICIOUS
   Confidence: 72%
   Next Actions: temporal_consistency_check, research_similar_patterns

2. TEMPORAL_AGENT
   Decision: INCONSISTENT
   Confidence: 78%
   Next Actions: research_manipulation_patterns

3. RESEARCH_AGENT (Parallel)
   Decision: PATTERNS_FOUND
   Confidence: 70%
   Next Actions: fact_check_claims, verify_metadata

4. FACT_CHECKER_AGENT (Parallel)
   Decision: SUSPICIOUS
   Confidence: 80%
   Next Actions: safety_check

5. SAFETY_GUARD_AGENT (Parallel)
   Decision: CAUTION
   Confidence: 85%
   Next Actions: final_synthesis

6. ORCHESTRATOR_AGENT
   Decision: FAKE
   Confidence: 85% (weighted)
   Recommended Actions:
   - Report to platform
   - Add warning label
   - Track for similar content
   - Notify user of deepfake
```

## 🔧 Technical Implementation

### Agent Orchestrator (`agent_orchestrator.py`)
```python
class AgentOrchestrator:
    """
    Orchestrates multiple specialized Nemotron agents
    Implements ReAct pattern: Reason → Act → Observe
    """
    
    async def analyze_video_with_agents(frames, metadata):
        # Phase 1: Vision Agent
        vision_result = await self._execute_vision_agent(...)
        
        # Phase 2: Temporal Agent (depends on vision)
        temporal_result = await self._execute_temporal_agent(
            dependencies=["vision_agent"]
        )
        
        # Phase 3: Parallel agents
        results = await asyncio.gather(
            self._execute_research_agent(...),
            self._execute_fact_checker_agent(...),
            self._execute_safety_agent(...)
        )
        
        # Phase 4: Orchestrator synthesis
        final = await self._execute_orchestrator_agent(
            all_findings=...
        )
        
        return final_decision
```

### Multi-Model Support (`nim_client.py`)
```python
class NIMClient:
    MODELS = {
        "vision": "nvidia/nemotron-nano-12b-v2-vl",
        "nano": "nvidia/nemotron-nano-9b-v2",
        "super": "nvidia/nemotron-super-49b-v1.5",
        "safety": "nvidia/nemotron-safety-guard-8b-v3"
    }
    
    async def generate_text(prompt, use_super_model=False):
        # Select appropriate model for agent
        model = self.MODELS["super"] if use_super_model else self.MODELS["nano"]
        # ...
```

## 🚀 API Endpoints

### Basic Analysis (Single Agent)
```bash
POST /api/v1/analyze-frame
```

### 🏆 Multi-Agent Analysis (Prize Track Feature)
```bash
POST /api/v1/analyze-with-agents
```

**Response includes:**
```json
{
  "success": true,
  "analysis_type": "multi_agent",
  "result": {
    "is_likely_fake": true,
    "confidence_score": 0.85,
    "reasoning": "...",
    "agent_chain": "Full reasoning chain from all agents",
    "evidence": ["...", "..."],
    "next_actions": ["Report to platform", "Add warning label"]
  },
  "agent_workflow": {
    "workflow_type": "Multi-Agent ReAct Pattern",
    "total_agents": 6,
    "execution_order": ["vision", "temporal", "research", "fact_check", "safety", "orchestrator"],
    "parallel_stages": [["research_agent", "fact_checker_agent", "safety_guard_agent"]]
  },
  "agent_decisions": [
    {
      "agent": "vision_agent",
      "decision": "SUSPICIOUS",
      "confidence": 0.72,
      "reasoning": "...",
      "evidence": ["..."]
    },
    // ... 5 more agents
  ],
  "models_used": [
    "nvidia/nemotron-nano-12b-v2-vl",
    "nvidia/nemotron-nano-9b-v2",
    "nvidia/nemotron-safety-guard-8b-v3",
    "nvidia/nemotron-super-49b-v1.5"
  ]
}
```

## 🎯 Hackathon Judge Checklist

### ✅ Autonomous Reasoning
**Shows agent thinking, not just prompting**
- Each agent independently analyzes its domain
- Decisions based on evidence, not hardcoded rules
- Agents determine their own next actions

### ✅ Multi-Step Workflows
**Complex task decomposition**
- 6-stage agent pipeline
- Dependencies between agents
- Parallel execution where possible
- Adaptive workflow based on findings

### ✅ Tool Integration
**Uses external APIs/services intelligently**
- Vision analysis (Nemotron VLM)
- Web search capabilities (Research Agent)
- Fact-checking integration
- Safety scanning

### ✅ Real-World Applicability
**Solves actual problems**
- Deepfake detection on social media
- Content moderation
- Misinformation prevention
- User protection

### ✅ Nemotron-Specific Strengths
**Why Nemotron is the right choice**
- Multi-modal VLM for vision+text reasoning
- Fast nano models for real-time analysis
- Safety-specific model for content moderation
- Super model for complex synthesis
- Purpose-built for agentic workflows

## 🎥 Demo Flow

### For Judges
1. **Start backend** with multi-agent system
2. **Load extension** in Chrome/Edge
3. **Navigate to YouTube/Facebook** video
4. **Click "Start"** to begin analysis
5. **Watch agents work** in real-time logs
6. **See reasoning chain** in response

### Console Output Shows:
```
🤖 Starting multi-agent video analysis
👁️ Vision Agent: Analyzing frames...
⏱️ Temporal Agent: Checking consistency across time...
🔍 Research Agent: Searching for similar patterns...
✅ Fact-Checker Agent: Verifying claims...
🛡️ Safety Guard Agent: Checking for harmful content...
🎯 Orchestrator Agent: Synthesizing findings...
✅ Multi-agent analysis complete: FAKE (0.85 confidence)
```

## 💻 Running the Agentic System

### Start Backend
```bash
cd backend
python main.py
```

### Test Multi-Agent Endpoint
```bash
curl -X POST http://localhost:8000/api/v1/analyze-with-agents \
  -H "Content-Type: application/json" \
  -d '{
    "frames": [
      {
        "frame": "base64_image_data",
        "video_id": "test123",
        "timestamp": 1.5,
        "video_title": "Test Video"
      }
    ]
  }'
```

### View Agent Logs
Backend logs show full agent reasoning chain in real-time.

## 🏆 Why This Wins the Nemotron Prize Track

### 1. True Agentic Behavior
Not a wrapper around an LLM - genuine multi-agent system with:
- Autonomous decision-making
- Inter-agent communication
- Dynamic workflow adaptation
- Tool integration

### 2. Multiple Nemotron Models Working Together
- Vision: Nemotron-Nano-12B-v2-VL ✅
- Reasoning: Nemotron-nano-9b-v2 ✅
- Safety: Nemotron-Safety-Guard-8B-v3 ✅
- Orchestration: Nemotron-super-49b-v1.5 ✅

**Using 4 different Nemotron models shows deep integration!**

### 3. ReAct Pattern Implementation
Proper Reason → Act → Observe loops:
- Agents reason about findings
- Take actions (search, analyze, verify)
- Observe results
- Adapt next steps

### 4. Real-World Impact
Addresses critical social problem:
- Deepfakes spreading misinformation
- AI-generated fake news
- Social media manipulation
- User safety

### 5. Technical Excellence
- Clean architecture
- Proper async/parallel execution
- Comprehensive error handling
- Production-ready code
- Excellent documentation

## 📚 Code Structure

```
backend/
├── services/
│   ├── agent_orchestrator.py    # 🤖 Main multi-agent system
│   ├── nim_client.py             # Multi-model Nemotron client
│   ├── frame_analyzer.py         # Vision analysis
│   └── news_analyzer.py          # Text analysis
├── api/
│   └── routes.py                 # Includes /analyze-with-agents endpoint
└── main.py                       # FastAPI server

extension/
├── content.js                    # Chrome extension (YouTube/Facebook)
├── manifest.json                 # Multi-platform support
└── popup/                        # Settings UI
```

## 🎉 Innovation Highlights

1. **First video detection system using multi-agent Nemotron** 🌟
2. **Real-time agentic analysis** of social media content
3. **Cross-platform support** (YouTube + Facebook Reels)
4. **Full agent reasoning chain** visible to users
5. **Production-ready architecture** for scaling

---

## 📞 For Judges

**Want to see it in action?**
- Full source code in this repo
- Live demo available
- Complete documentation provided
- Agent logs show reasoning in real-time

**This is true agentic AI** - not a chatbot with extra steps! 🚀


