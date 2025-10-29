# 🏆 NVIDIA Nemotron Prize Track Submission

## Project: AI Video Detector with Multi-Agent System

### 🎯 Category: Best Use of NVIDIA Nemotron

---

## 🤖 What Makes This Agentic AI?

Unlike traditional AI systems that simply respond to prompts, our system demonstrates **true agentic behavior**:

### ✅ Autonomous Reasoning
- 6 specialized agents that independently analyze their domains
- Each agent makes decisions without human intervention
- Agents determine their own next actions based on evidence

### ✅ Multi-Step Workflows
- Complex 6-phase pipeline: Vision → Temporal → Research/Fact-Check/Safety → Orchestration
- Dependencies between agents (temporal agent depends on vision findings)
- Parallel execution for efficiency
- Adaptive workflow that changes based on intermediate results

### ✅ Tool Integration
- **Vision analysis** using Nemotron-Nano-12B-v2-VL
- **Web search** capabilities (Research Agent)
- **Fact-checking** APIs (Fact-Checker Agent)
- **Safety scanning** with specialized model

### ✅ Real-World Applicability
Solves critical social media problem:
- Detects AI-generated deepfakes in real-time
- Prevents misinformation spread
- Protects users on YouTube & Facebook
- Production-ready Chrome extension

### ✅ Nemotron-Specific Strengths

**Why we chose Nemotron models:**

| Agent | Model | Why This Model? |
|-------|-------|----------------|
| Vision Agent | `nemotron-nano-12b-v2-vl` | Multi-modal VLM perfect for video frame analysis |
| Temporal Agent | `nemotron-nano-9b-v2` | Fast reasoning for real-time consistency checks |
| Research Agent | `nemotron-nano-9b-v2` | Excellent at structured outputs & tool calling |
| Fact-Checker | `nemotron-nano-9b-v2` | Optimized for verification tasks |
| Safety Guard | `nemotron-safety-guard-8b-v3` | Purpose-built for content safety |
| Orchestrator | `nemotron-super-49b-v1.5` | Advanced reasoning for complex synthesis |

**4 different Nemotron models working together!** This shows deep integration, not just using one model.

---

## 🎬 Demo Video Script

### Opening (0:00-0:30)
"Hi judges! I'm demonstrating a multi-agent AI system using 4 different NVIDIA Nemotron models to detect deepfakes in real-time."

### Architecture Overview (0:30-1:00)
[Show diagram]
"Our system uses 6 specialized agents:
- Vision Agent analyzes frames
- Temporal Agent checks consistency  
- Research, Fact-Checker, and Safety agents run in parallel
- Orchestrator synthesizes all findings"

### Live Demo (1:00-2:00)
[Open Chrome extension on YouTube]
"Watch as agents work together:
1. Vision Agent detects facial anomalies
2. Temporal Agent finds impossible motion
3. Research Agent matches known AI patterns
4. Orchestrator makes final decision: FAKE with 85% confidence"

[Show console logs]
"You can see each agent reasoning in real-time"

### Agent Reasoning (2:00-2:30)
[Show API response]
"The response includes full reasoning chain from all 6 agents, showing autonomous decision-making at each step"

### Why Nemotron (2:30-3:00)
"This showcases Nemotron's strength in agentic AI:
- Multi-modal vision-language reasoning
- Fast real-time analysis
- Specialized safety checking
- Complex multi-agent orchestration"

---

## 📊 Key Metrics

| Metric | Value |
|--------|-------|
| **Number of Agents** | 6 specialized agents |
| **Nemotron Models Used** | 4 different models |
| **Workflow Type** | ReAct Pattern (Reason → Act → Observe) |
| **Execution Mode** | Parallel + Sequential |
| **Real-time Processing** | ✅ Yes (5-second intervals) |
| **Multi-platform** | ✅ YouTube & Facebook |
| **Production Ready** | ✅ Chrome extension + API |

---

## 🔥 Innovation Highlights

### 1. First Video Deepfake Detector Using Multi-Agent Nemotron
No existing system uses multiple Nemotron models in an agent orchestration pattern for video analysis.

### 2. Real-Time Social Media Protection
Works live on YouTube and Facebook Reels - protecting users as they browse.

### 3. True Agentic Behavior
Not just "AI that calls functions" - genuine multi-agent reasoning with:
- Inter-agent dependencies
- Dynamic workflow adaptation
- Autonomous next-action determination

### 4. ReAct Pattern Implementation
Proper Reason → Act → Observe loops:
```
Vision Agent: 
  Reason: "Detects facial morphing"
  Act: "Flag for temporal analysis"
  
Temporal Agent:
  Observe: Vision findings
  Reason: "Motion is physically impossible"
  Act: "Recommend research patterns"
  
Research Agent:
  Observe: Temporal + Vision findings
  Reason: "Matches known AI generation signatures"
  Act: "Escalate to orchestrator"
```

### 5. Multi-Modal Reasoning
Combines:
- Vision analysis (frames)
- Text analysis (metadata, claims)
- Web search (pattern matching)
- Safety checking (harm detection)

---

## 🎯 Hackathon Judge Checklist

| Requirement | Status | Evidence |
|------------|--------|----------|
| **Autonomous reasoning** | ✅ | 6 agents make independent decisions |
| **Multi-step workflows** | ✅ | 6-phase pipeline with dependencies |
| **Tool integration** | ✅ | Vision, search, fact-check, safety tools |
| **Real-world applicability** | ✅ | Chrome extension on social media |
| **Nemotron strengths** | ✅ | 4 models chosen for specific capabilities |
| **Agent visualization** | ✅ | Full reasoning chain in API response |
| **ReAct pattern** | ✅ | Reason→Act→Observe loops implemented |

---

## 💻 Quick Start for Judges

### 1. Clone & Setup
```bash
git clone <repo>
cd are-you-ai
```

### 2. Backend Setup
```bash
cd backend
pip install -r requirements.txt

# Add your NVIDIA NIM API key to .env
echo "NIM_API_KEY=your_key_here" > .env

python main.py
```

### 3. Load Extension
1. Open Chrome → `chrome://extensions/`
2. Enable "Developer mode"
3. Click "Load unpacked" → Select `extension/` folder

### 4. Test Multi-Agent System
```bash
# Option 1: Test API directly
curl -X POST http://localhost:8000/api/v1/analyze-with-agents \
  -H "Content-Type: application/json" \
  -d @test_payload.json

# Option 2: Use extension on YouTube/Facebook
# Go to any video → Click "Start" button
```

### 5. View Agent Reasoning
Check backend console for real-time agent logs:
```
🤖 Starting multi-agent video analysis
👁️ Vision Agent: Analyzing frames...
⏱️ Temporal Agent: Checking consistency...
🔍 Research Agent: Searching patterns...
✅ Multi-agent analysis complete!
```

---

## 📈 Technical Architecture

### Agent Communication Flow
```
User Request
    ↓
[API Endpoint: /analyze-with-agents]
    ↓
[Agent Orchestrator]
    ↓
┌───────────┬─────────────┬──────────────┐
│  Phase 1  │   Phase 2   │   Phase 3    │
│  Vision   │  Temporal   │  Research +  │
│  Agent    │  Agent      │  Fact-Check +│
│           │  (depends   │  Safety      │
│           │   on 1)     │  (parallel)  │
└───────────┴─────────────┴──────────────┘
    ↓           ↓              ↓
    └───────────┴──────────────┘
                ↓
         [Phase 4: Orchestrator]
         Synthesizes & Decides
                ↓
         Final Decision + 
         Full Reasoning Chain
```

### Code Highlights

**Agent Orchestrator** (`agent_orchestrator.py`)
```python
async def analyze_video_with_agents(frames, metadata):
    # Sequential phase
    vision = await execute_vision_agent()
    temporal = await execute_temporal_agent(vision)
    
    # Parallel phase
    research, fact_check, safety = await asyncio.gather(
        execute_research_agent(vision),
        execute_fact_checker_agent(vision),
        execute_safety_agent(vision)
    )
    
    # Final synthesis
    final = await execute_orchestrator_agent({
        vision, temporal, research, fact_check, safety
    })
    
    return final
```

**Multi-Model NIM Client** (`nim_client.py`)
```python
MODELS = {
    "vision": "nvidia/nemotron-nano-12b-v2-vl",
    "nano": "nvidia/nemotron-nano-9b-v2",
    "super": "nvidia/nemotron-super-49b-v1.5",
    "safety": "nvidia/nemotron-safety-guard-8b-v3"
}

async def generate_text(prompt, use_super_model=False):
    model = MODELS["super"] if use_super_model else MODELS["nano"]
    # ... make API call with selected model
```

---

## 🎨 UI Features

### Chrome Extension
- **Start/Stop** analysis with one click
- **Real-time badge** showing FAKE/REAL status
- **Details overlay** with full agent reasoning
- **Multi-platform** support (YouTube + Facebook)

### API Response
- **Agent decisions** from all 6 agents
- **Reasoning chain** showing thought process
- **Evidence list** with specific findings
- **Next actions** recommended by orchestrator
- **Workflow visualization** of agent execution

---

## 🌟 Why This Wins

### 1. Deep Nemotron Integration
Uses **4 different Nemotron models**, each chosen for specific strengths:
- Vision-language multi-modal reasoning
- Fast real-time text analysis  
- Specialized safety checking
- Advanced orchestration

### 2. True Agentic System
Not a chatbot with functions - genuine agent behavior:
- Autonomous decision-making
- Multi-agent coordination
- Dynamic workflow adaptation
- Tool integration

### 3. Real-World Impact
Solves critical problem:
- Deepfakes spreading on social media
- Misinformation at scale
- User protection
- Content moderation

### 4. Production Ready
Not just a prototype:
- Chrome extension with 1000+ users potential
- API ready for integration
- Multi-platform support
- Comprehensive error handling

### 5. Excellent Documentation
- Clear architecture diagrams
- Full API documentation
- Agent reasoning explanations
- Demo video & quick start guide

---

## 📞 Contact & Demo

**GitHub**: [Repo Link]
**Live Demo**: [Video Link]
**API Docs**: See `AGENTIC_SYSTEM.md`

**For judges**: Full source code available, live demo ready, happy to answer questions!

---

## 🏆 Conclusion

This project showcases **true agentic AI** using NVIDIA Nemotron:

✅ **Autonomous reasoning** - agents think independently
✅ **Multi-step workflows** - complex task decomposition
✅ **Tool integration** - uses APIs intelligently
✅ **Real-world impact** - protects social media users
✅ **Nemotron excellence** - 4 models working together

**This is what agentic AI should be** - not just answering questions, but reasoning, planning, and taking action! 🚀


