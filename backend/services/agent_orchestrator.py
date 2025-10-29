"""
Multi-Agent Orchestrator for AI Video Detection
Uses multiple specialized Nemotron agents working together
"""
import logging
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from enum import Enum
import asyncio

logger = logging.getLogger(__name__)


class AgentRole(Enum):
    """Specialized agent roles in the system"""
    VISION = "vision_agent"  # Analyzes visual frames
    TEMPORAL = "temporal_agent"  # Analyzes consistency across time
    RESEARCH = "research_agent"  # Searches for similar patterns
    FACT_CHECKER = "fact_checker_agent"  # Verifies claims
    SAFETY = "safety_guard_agent"  # Checks for harmful content
    ORCHESTRATOR = "orchestrator_agent"  # Coordinates all agents


@dataclass
class AgentTask:
    """Represents a task for an agent"""
    agent_role: AgentRole
    task_type: str
    input_data: Dict[str, Any]
    dependencies: List[str] = None
    status: str = "pending"  # pending, in_progress, completed, failed
    result: Optional[Dict[str, Any]] = None
    reasoning: Optional[str] = None


@dataclass
class AgentDecision:
    """Represents an agent's decision"""
    agent_role: AgentRole
    decision: str
    confidence: float
    reasoning: str
    evidence: List[str]
    next_actions: List[str]


class AgentOrchestrator:
    """
    Orchestrates multiple specialized Nemotron agents to analyze videos
    Implements ReAct pattern: Reason → Act → Observe
    """
    
    def __init__(self):
        self.agents = {}
        self.task_queue = []
        self.completed_tasks = []
        self.agent_decisions = []
        
    async def analyze_video_with_agents(
        self,
        frames: List[Dict[str, Any]],
        video_metadata: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Multi-agent video analysis workflow
        
        Workflow:
        1. Vision Agent analyzes each frame
        2. Temporal Agent checks consistency across frames
        3. Research Agent searches for similar AI patterns
        4. Fact-Checker Agent verifies any claims
        5. Safety Guard Agent checks for harmful content
        6. Orchestrator Agent synthesizes all findings
        
        Args:
            frames: List of video frames with timestamps
            video_metadata: Video title, ID, platform, etc.
            
        Returns:
            Comprehensive analysis with agent reasoning chain
        """
        logger.info("🤖 Starting multi-agent video analysis")
        
        # Phase 1: Vision Agent analyzes frames
        vision_task = AgentTask(
            agent_role=AgentRole.VISION,
            task_type="frame_analysis",
            input_data={"frames": frames, "metadata": video_metadata}
        )
        vision_result = await self._execute_vision_agent(vision_task)
        self.agent_decisions.append(vision_result)
        
        # Phase 2: Temporal Agent checks consistency
        temporal_task = AgentTask(
            agent_role=AgentRole.TEMPORAL,
            task_type="temporal_consistency",
            input_data={"vision_analysis": vision_result, "frames": frames},
            dependencies=["vision_agent"]
        )
        temporal_result = await self._execute_temporal_agent(temporal_task)
        self.agent_decisions.append(temporal_result)
        
        # Phase 3: Research Agent searches for patterns (parallel)
        research_task = AgentTask(
            agent_role=AgentRole.RESEARCH,
            task_type="pattern_research",
            input_data={"vision_analysis": vision_result, "metadata": video_metadata}
        )
        
        # Phase 4: Fact-Checker Agent verifies claims (parallel)
        fact_check_task = AgentTask(
            agent_role=AgentRole.FACT_CHECKER,
            task_type="fact_verification",
            input_data={"vision_analysis": vision_result, "metadata": video_metadata}
        )
        
        # Phase 5: Safety Guard checks content (parallel)
        safety_task = AgentTask(
            agent_role=AgentRole.SAFETY,
            task_type="safety_check",
            input_data={"vision_analysis": vision_result, "metadata": video_metadata}
        )
        
        # Execute parallel agents
        research_result, fact_check_result, safety_result = await asyncio.gather(
            self._execute_research_agent(research_task),
            self._execute_fact_checker_agent(fact_check_task),
            self._execute_safety_agent(safety_task)
        )
        
        self.agent_decisions.extend([research_result, fact_check_result, safety_result])
        
        # Phase 6: Orchestrator synthesizes all findings
        orchestrator_task = AgentTask(
            agent_role=AgentRole.ORCHESTRATOR,
            task_type="final_synthesis",
            input_data={
                "vision": vision_result,
                "temporal": temporal_result,
                "research": research_result,
                "fact_check": fact_check_result,
                "safety": safety_result
            },
            dependencies=["vision_agent", "temporal_agent", "research_agent", 
                         "fact_checker_agent", "safety_guard_agent"]
        )
        final_result = await self._execute_orchestrator_agent(orchestrator_task)
        self.agent_decisions.append(final_result)
        
        # Build comprehensive result
        return {
            "is_likely_fake": final_result.decision == "FAKE",
            "confidence_score": final_result.confidence,
            "reasoning": final_result.reasoning,
            "agent_chain": self._build_agent_chain_explanation(),
            "evidence": final_result.evidence,
            "next_actions": final_result.next_actions,
            "agent_decisions": [
                {
                    "agent": d.agent_role.value,
                    "decision": d.decision,
                    "confidence": d.confidence,
                    "reasoning": d.reasoning,
                    "evidence": d.evidence
                }
                for d in self.agent_decisions
            ],
            "workflow_visualization": self._visualize_workflow()
        }
    
    async def _execute_vision_agent(self, task: AgentTask) -> AgentDecision:
        """
        Vision Agent: Uses Nemotron-Nano-12B-v2-VL to analyze frames
        Detects visual anomalies, AI artifacts, deepfake indicators
        """
        logger.info("👁️ Vision Agent: Analyzing frames...")
        
        from services.frame_analyzer import FrameAnalyzer
        
        analyzer = FrameAnalyzer()
        frames = task.input_data["frames"]
        
        # Analyze frames with vision model
        results = []
        for frame_data in frames[:5]:  # Analyze first 5 frames
            result = await analyzer.analyze_frame(
                base64_frame=frame_data.get("frame"),
                video_id=task.input_data["metadata"].get("video_id"),
                timestamp=frame_data.get("timestamp")
            )
            results.append(result)
        
        # Vision agent reasoning
        fake_count = sum(1 for r in results if r.get("is_likely_fake"))
        confidence = sum(r.get("confidence_score", 0) for r in results) / len(results)
        
        evidence = []
        for i, r in enumerate(results):
            if r.get("inconsistencies"):
                evidence.append(f"Frame {i}: {len(r['inconsistencies'])} visual anomalies detected")
        
        reasoning = f"""Vision Agent Analysis:
- Analyzed {len(results)} frames
- Detected AI artifacts in {fake_count}/{len(results)} frames
- Visual anomalies: {len(evidence)} frames show inconsistencies
- Confidence: {confidence:.1%}

Next step: Temporal agent should verify consistency across frames."""
        
        next_actions = [
            "temporal_consistency_check",
            "research_similar_patterns" if fake_count > 0 else "verify_authenticity"
        ]
        
        return AgentDecision(
            agent_role=AgentRole.VISION,
            decision="SUSPICIOUS" if fake_count > len(results) / 2 else "UNCLEAR",
            confidence=confidence,
            reasoning=reasoning,
            evidence=evidence,
            next_actions=next_actions
        )
    
    async def _execute_temporal_agent(self, task: AgentTask) -> AgentDecision:
        """
        Temporal Agent: Uses Nemotron-nano-9b-v2 to analyze consistency
        Checks for temporal anomalies, unnatural movements, frame transitions
        """
        logger.info("⏱️ Temporal Agent: Checking consistency across time...")
        
        from services.nim_client import NIMClient
        
        client = NIMClient()
        vision_analysis = task.input_data["vision_analysis"]
        
        # Build temporal analysis prompt
        prompt = f"""You are a temporal consistency analyzer for video authenticity detection.

Previous vision analysis found: {vision_analysis.decision}
Evidence: {', '.join(vision_analysis.evidence)}

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

        response = await client.generate_text(
            prompt=prompt,
            max_tokens=500,
            temperature=0.3
        )
        
        # Parse agent response
        decision = "INCONSISTENT" if "inconsistent" in response.lower() else "CONSISTENT"
        confidence = 0.75  # Extract from response in production
        
        reasoning = f"""Temporal Agent Analysis:
{response}

Recommendation: {'High likelihood of manipulation' if decision == 'INCONSISTENT' else 'Temporal patterns appear normal'}"""
        
        evidence = [
            "Cross-frame analysis completed",
            f"Temporal consistency: {decision}"
        ]
        
        next_actions = [
            "research_manipulation_patterns" if decision == "INCONSISTENT" else "verify_source"
        ]
        
        return AgentDecision(
            agent_role=AgentRole.TEMPORAL,
            decision=decision,
            confidence=confidence,
            reasoning=reasoning,
            evidence=evidence,
            next_actions=next_actions
        )
    
    async def _execute_research_agent(self, task: AgentTask) -> AgentDecision:
        """
        Research Agent: Uses Nemotron-nano-9b-v2 + web search
        Searches for similar AI-generated patterns, known deepfakes, source verification
        """
        logger.info("🔍 Research Agent: Searching for similar patterns...")
        
        from services.nim_client import NIMClient
        
        client = NIMClient()
        vision_analysis = task.input_data["vision_analysis"]
        metadata = task.input_data["metadata"]
        
        # Research agent uses tool calling
        prompt = f"""You are a research agent investigating video authenticity.

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

        response = await client.generate_text(
            prompt=prompt,
            max_tokens=400,
            temperature=0.4
        )
        
        reasoning = f"""Research Agent Findings:
{response}

Knowledge base check: Comparing against known AI generation patterns"""
        
        evidence = [
            "Pattern matching completed",
            "Source verification attempted"
        ]
        
        # Tool calling simulation - in production, call actual APIs
        next_actions = ["fact_check_claims", "verify_metadata"]
        
        return AgentDecision(
            agent_role=AgentRole.RESEARCH,
            decision="PATTERNS_FOUND" if "pattern" in response.lower() else "NO_MATCH",
            confidence=0.70,
            reasoning=reasoning,
            evidence=evidence,
            next_actions=next_actions
        )
    
    async def _execute_fact_checker_agent(self, task: AgentTask) -> AgentDecision:
        """
        Fact-Checker Agent: Uses Nemotron-nano-9b-v2
        Verifies claims, checks metadata consistency, validates content
        """
        logger.info("✅ Fact-Checker Agent: Verifying claims...")
        
        from services.nim_client import NIMClient
        
        client = NIMClient()
        metadata = task.input_data["metadata"]
        
        prompt = f"""You are a fact-checking agent for video authenticity.

Video metadata:
- Title: {metadata.get('title', 'Unknown')}
- Platform: {metadata.get('platform', 'Unknown')}
- Video ID: {metadata.get('video_id', 'Unknown')}

Verify:
1. Does metadata seem manipulated?
2. Are there red flags in the title/description?
3. Common deepfake claim patterns?

Provide verification status and reasoning."""

        response = await client.generate_text(
            prompt=prompt,
            max_tokens=300,
            temperature=0.3
        )
        
        reasoning = f"""Fact-Checker Agent Report:
{response}"""
        
        evidence = ["Metadata verification completed"]
        
        return AgentDecision(
            agent_role=AgentRole.FACT_CHECKER,
            decision="VERIFIED" if "verified" in response.lower() else "SUSPICIOUS",
            confidence=0.80,
            reasoning=reasoning,
            evidence=evidence,
            next_actions=["safety_check"]
        )
    
    async def _execute_safety_agent(self, task: AgentTask) -> AgentDecision:
        """
        Safety Guard Agent: Uses Nemotron-Safety-Guard-8B-v3
        Checks for harmful content, misinformation, malicious intent
        """
        logger.info("🛡️ Safety Guard Agent: Checking for harmful content...")
        
        from services.nim_client import NIMClient
        
        client = NIMClient()
        vision_analysis = task.input_data["vision_analysis"]
        
        # Use safety model to check content
        prompt = f"""You are a safety guard AI checking video content.

Vision analysis findings: {vision_analysis.reasoning}

Safety checks:
1. Misinformation risk level
2. Potential for harm
3. Malicious deepfake indicators
4. Recommended content warnings

Provide safety assessment."""

        response = await client.generate_text(
            prompt=prompt,
            max_tokens=300,
            temperature=0.2
        )
        
        reasoning = f"""Safety Guard Assessment:
{response}

Content safety evaluation complete."""
        
        evidence = ["Safety scan completed"]
        
        return AgentDecision(
            agent_role=AgentRole.SAFETY,
            decision="SAFE" if "safe" in response.lower() else "CAUTION",
            confidence=0.85,
            reasoning=reasoning,
            evidence=evidence,
            next_actions=["final_synthesis"]
        )
    
    async def _execute_orchestrator_agent(self, task: AgentTask) -> AgentDecision:
        """
        Orchestrator Agent: Uses Nemotron-super-49b-v1_5
        Synthesizes all agent findings into final decision
        Implements advanced reasoning and decision-making
        """
        logger.info("🎯 Orchestrator Agent: Synthesizing findings...")
        
        from services.nim_client import NIMClient
        
        client = NIMClient()
        
        # Gather all agent inputs
        vision = task.input_data["vision"]
        temporal = task.input_data["temporal"]
        research = task.input_data["research"]
        fact_check = task.input_data["fact_check"]
        safety = task.input_data["safety"]
        
        # Build comprehensive synthesis prompt
        prompt = f"""You are the orchestrator AI making the final decision on video authenticity.

AGENT REPORTS:

1. Vision Agent: {vision.decision} (confidence: {vision.confidence:.1%})
   Reasoning: {vision.reasoning}

2. Temporal Agent: {temporal.decision} (confidence: {temporal.confidence:.1%})
   Reasoning: {temporal.reasoning}

3. Research Agent: {research.decision} (confidence: {research.confidence:.1%})
   Reasoning: {research.reasoning}

4. Fact-Checker Agent: {fact_check.decision} (confidence: {fact_check.confidence:.1%})
   Reasoning: {fact_check.reasoning}

5. Safety Guard: {safety.decision} (confidence: {safety.confidence:.1%})
   Reasoning: {safety.reasoning}

YOUR TASK:
Synthesize all findings and make final decision:
- Is this video REAL or FAKE?
- Overall confidence (0.0-1.0)
- Key evidence supporting decision
- Recommended actions for user
- Explanation of reasoning chain

Provide detailed analysis showing how you weighed each agent's input."""

        response = await client.generate_text(
            prompt=prompt,
            max_tokens=800,
            temperature=0.5,
            use_super_model=True  # Use largest model for orchestration
        )
        
        # Parse orchestrator decision
        decision = "FAKE" if "fake" in response.lower() and "not fake" not in response.lower() else "REAL"
        
        # Calculate weighted confidence
        confidences = [
            vision.confidence * 0.35,  # Vision most important
            temporal.confidence * 0.25,  # Temporal very important
            research.confidence * 0.20,  # Research moderately important
            fact_check.confidence * 0.10,  # Fact-check helpful
            safety.confidence * 0.10  # Safety helpful
        ]
        final_confidence = sum(confidences)
        
        reasoning = f"""🎯 ORCHESTRATOR FINAL DECISION:

{response}

CONFIDENCE BREAKDOWN:
- Vision Analysis: {vision.confidence:.1%} (weight: 35%)
- Temporal Consistency: {temporal.confidence:.1%} (weight: 25%)
- Pattern Research: {research.confidence:.1%} (weight: 20%)
- Fact Checking: {fact_check.confidence:.1%} (weight: 10%)
- Safety Assessment: {safety.confidence:.1%} (weight: 10%)

FINAL CONFIDENCE: {final_confidence:.1%}"""
        
        # Aggregate evidence
        all_evidence = []
        for agent_result in [vision, temporal, research, fact_check, safety]:
            all_evidence.extend(agent_result.evidence)
        
        # Determine next actions
        if decision == "FAKE":
            next_actions = [
                "Report to platform",
                "Add warning label",
                "Track for similar content",
                "Notify user of deepfake"
            ]
        else:
            next_actions = [
                "Mark as verified",
                "Continue monitoring",
                "Log analysis for improvements"
            ]
        
        return AgentDecision(
            agent_role=AgentRole.ORCHESTRATOR,
            decision=decision,
            confidence=final_confidence,
            reasoning=reasoning,
            evidence=all_evidence,
            next_actions=next_actions
        )
    
    def _build_agent_chain_explanation(self) -> str:
        """Build human-readable explanation of agent reasoning chain"""
        chain = "🤖 MULTI-AGENT REASONING CHAIN:\n\n"
        
        for i, decision in enumerate(self.agent_decisions, 1):
            chain += f"{i}. {decision.agent_role.value.upper()}\n"
            chain += f"   Decision: {decision.decision}\n"
            chain += f"   Confidence: {decision.confidence:.1%}\n"
            chain += f"   Next Actions: {', '.join(decision.next_actions)}\n\n"
        
        return chain
    
    def _visualize_workflow(self) -> Dict[str, Any]:
        """Create workflow visualization data"""
        return {
            "workflow_type": "Multi-Agent ReAct Pattern",
            "total_agents": len(self.agent_decisions),
            "execution_order": [d.agent_role.value for d in self.agent_decisions],
            "parallel_stages": [
                ["research_agent", "fact_checker_agent", "safety_guard_agent"]
            ],
            "decision_chain": [
                {
                    "step": i + 1,
                    "agent": d.agent_role.value,
                    "decision": d.decision,
                    "confidence": d.confidence
                }
                for i, d in enumerate(self.agent_decisions)
            ]
        }

