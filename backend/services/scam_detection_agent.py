"""
Scam Detection Agent - Protects seniors from financial fraud
Uses Nemotron models to detect scam patterns in videos and messages
"""
import logging
from typing import Dict, Any, Optional, List
from dataclasses import dataclass
from enum import Enum

logger = logging.getLogger(__name__)


class ScamType(Enum):
    """Types of scams commonly targeting seniors"""
    FINANCIAL_URGENCY = "financial_urgency"  # "Act now or lose money"
    IMPERSONATION = "impersonation"  # Fake family/authority
    TECH_SUPPORT = "tech_support"  # Fake Microsoft/Apple support
    PRIZE_LOTTERY = "prize_lottery"  # "You won something"
    ROMANCE_SCAM = "romance_scam"  # Fake romantic interest
    INVESTMENT_FRAUD = "investment_fraud"  # Fake investment opportunities
    CHARITY_SCAM = "charity_scam"  # Fake charity appeals
    GRANDPARENT_SCAM = "grandparent_scam"  # "Grandchild in trouble"


@dataclass
class ScamIndicators:
    """Indicators that suggest potential scam"""
    urgency_language: bool = False  # "Act now", "Limited time"
    financial_request: bool = False  # Asking for money/info
    authority_impersonation: bool = False  # Claims to be IRS, bank, etc.
    emotional_manipulation: bool = False  # Fear, guilt, excitement
    personal_info_request: bool = False  # SSN, passwords, etc.
    suspicious_links: bool = False  # Shortened URLs, misspelled domains
    grammatical_errors: bool = False  # Poor grammar/spelling
    unknown_sender: bool = False  # Not in contacts
    pressure_tactics: bool = False  # Threats, consequences
    too_good_to_be_true: bool = False  # Unrealistic promises


class ScamDetectionAgent:
    """
    Specialized agent for detecting scams targeting seniors
    Uses Nemotron models for analysis
    """
    
    # Common scam keywords and phrases
    URGENCY_KEYWORDS = [
        "urgent", "immediately", "act now", "limited time", "expires today",
        "last chance", "final notice", "within 24 hours", "right now"
    ]
    
    FINANCIAL_KEYWORDS = [
        "send money", "wire transfer", "gift cards", "bitcoin", "cryptocurrency",
        "bank account", "credit card", "social security number", "ssn",
        "routing number", "verify account", "confirm payment", "transfer funds"
    ]
    
    AUTHORITY_KEYWORDS = [
        "irs", "social security", "medicare", "fbi", "police", "sheriff",
        "bank of america", "wells fargo", "chase bank", "microsoft", "apple",
        "amazon", "paypal", "government", "federal", "department"
    ]
    
    EMOTIONAL_KEYWORDS = [
        "emergency", "crisis", "danger", "arrest", "lawsuit", "suspended",
        "frozen account", "unusual activity", "security breach", "hacked",
        "grandson", "granddaughter", "jail", "hospital", "accident"
    ]
    
    PRIZE_KEYWORDS = [
        "you won", "congratulations", "winner", "prize", "lottery", "sweepstakes",
        "claim your", "free gift", "selected", "chosen", "lucky"
    ]
    
    def __init__(self):
        self.scam_database = self._load_scam_database()
    
    def _load_scam_database(self) -> Dict[str, List[str]]:
        """Load database of known scam patterns"""
        return {
            "common_scams": [
                "IRS tax scam",
                "Social Security suspension scam",
                "Grandparent emergency scam",
                "Tech support scam",
                "Romance scam",
                "Prize/lottery scam",
                "Charity scam",
                "Investment fraud"
            ],
            "red_flags": [
                "Requests for immediate payment",
                "Asks for gift cards or wire transfers",
                "Claims account will be closed/suspended",
                "Uses fear or urgency tactics",
                "Requests personal information",
                "Too good to be true offers"
            ]
        }
    
    async def analyze_content(
        self,
        content: str,
        content_type: str = "text",  # "text", "video_title", "message"
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Analyze content for scam indicators
        
        Args:
            content: Text content to analyze
            content_type: Type of content (text, video_title, message)
            context: Additional context (sender info, platform, etc.)
            
        Returns:
            Analysis with scam risk score and recommendations
        """
        logger.info(f"🛡️ Analyzing content for scam indicators ({content_type})")
        
        # Step 1: Quick pattern matching
        indicators = self._detect_indicators(content)
        
        # Step 2: Use Nemotron for deeper analysis
        from services.nim_client import NIMClient
        nim_client = NIMClient()
        
        prompt = self._build_scam_analysis_prompt(content, content_type, indicators, context)
        
        try:
            analysis = await nim_client.generate_text(
                prompt=prompt,
                max_tokens=800,
                temperature=0.2,  # Low temperature for consistent detection
                model=nim_client.MODELS["nano"]  # Fast nano model
            )
            
            # Parse analysis
            scam_risk = self._extract_risk_score(analysis)
            scam_types = self._identify_scam_types(content, analysis)
            
            # Generate senior-friendly warning
            warning = self._generate_senior_warning(scam_risk, scam_types, indicators)
            
            # Recommend actions
            recommended_actions = self._recommend_actions(scam_risk, scam_types)
            
            return {
                "scam_risk_score": scam_risk,
                "risk_level": self._categorize_risk(scam_risk),
                "detected_scam_types": scam_types,
                "indicators": indicators,
                "senior_friendly_warning": warning,
                "recommended_actions": recommended_actions,
                "detailed_analysis": analysis,
                "safe_to_proceed": scam_risk < 0.3
            }
            
        except Exception as e:
            logger.error(f"Error in scam analysis: {e}", exc_info=True)
            # Fail safe - if AI analysis fails, use pattern matching
            return self._fallback_analysis(indicators)
    
    def _detect_indicators(self, content: str) -> ScamIndicators:
        """Detect scam indicators using pattern matching"""
        content_lower = content.lower()
        
        indicators = ScamIndicators()
        
        # Check for urgency language
        indicators.urgency_language = any(
            keyword in content_lower for keyword in self.URGENCY_KEYWORDS
        )
        
        # Check for financial requests
        indicators.financial_request = any(
            keyword in content_lower for keyword in self.FINANCIAL_KEYWORDS
        )
        
        # Check for authority impersonation
        indicators.authority_impersonation = any(
            keyword in content_lower for keyword in self.AUTHORITY_KEYWORDS
        )
        
        # Check for emotional manipulation
        indicators.emotional_manipulation = any(
            keyword in content_lower for keyword in self.EMOTIONAL_KEYWORDS
        )
        
        # Check for prize/lottery language
        indicators.too_good_to_be_true = any(
            keyword in content_lower for keyword in self.PRIZE_KEYWORDS
        )
        
        # Check for personal info requests
        info_requests = ["password", "pin", "social security", "ssn", "account number"]
        indicators.personal_info_request = any(
            keyword in content_lower for keyword in info_requests
        )
        
        # Check for suspicious links
        indicators.suspicious_links = "http" in content_lower and (
            "bit.ly" in content_lower or 
            ".tk" in content_lower or
            "tinyurl" in content_lower
        )
        
        return indicators
    
    def _build_scam_analysis_prompt(
        self,
        content: str,
        content_type: str,
        indicators: ScamIndicators,
        context: Optional[Dict[str, Any]]
    ) -> str:
        """Build prompt for Nemotron analysis"""
        
        context_info = ""
        if context:
            if "sender" in context:
                context_info += f"\nSender: {context['sender']}"
            if "platform" in context:
                context_info += f"\nPlatform: {context['platform']}"
            if "sender_verified" in context:
                context_info += f"\nSender Verified: {context['sender_verified']}"
        
        indicators_detected = []
        if indicators.urgency_language:
            indicators_detected.append("Urgency language detected")
        if indicators.financial_request:
            indicators_detected.append("Financial request detected")
        if indicators.authority_impersonation:
            indicators_detected.append("Authority impersonation detected")
        if indicators.emotional_manipulation:
            indicators_detected.append("Emotional manipulation detected")
        if indicators.personal_info_request:
            indicators_detected.append("Personal information request detected")
        
        indicators_str = "\n- ".join(indicators_detected) if indicators_detected else "None detected"
        
        prompt = f"""You are a scam detection expert protecting elderly users from fraud.

CONTENT TYPE: {content_type}
{context_info}

CONTENT TO ANALYZE:
"{content}"

INITIAL INDICATORS DETECTED:
- {indicators_str}

YOUR TASK:
Analyze this content for potential scams targeting seniors. Consider:

1. Is this content trying to manipulate emotions (fear, urgency, greed)?
2. Does it request money, personal information, or immediate action?
3. Does it impersonate authority figures (IRS, bank, family member)?
4. Are there red flags common in senior-targeted scams?
5. Is this language typical of legitimate communications?

COMMON SCAMS TO WATCH FOR:
- Grandparent scam (fake emergency from grandchild)
- IRS/Social Security scams
- Tech support scams
- Romance scams
- Prize/lottery scams
- Investment fraud

Provide your analysis in simple terms:
1. Scam risk level (LOW, MEDIUM, HIGH, CRITICAL)
2. Type of scam if detected
3. Specific red flags
4. Why this might be a scam OR why it seems legitimate
5. Simple advice for the user

Be conservative - it's better to warn about something legitimate than miss a real scam."""

        return prompt
    
    def _extract_risk_score(self, analysis: str) -> float:
        """Extract risk score from analysis"""
        analysis_lower = analysis.lower()
        
        if "critical" in analysis_lower or "definitely a scam" in analysis_lower:
            return 0.95
        elif "high risk" in analysis_lower or "likely a scam" in analysis_lower:
            return 0.80
        elif "medium risk" in analysis_lower or "suspicious" in analysis_lower:
            return 0.60
        elif "low risk" in analysis_lower or "possibly legitimate" in analysis_lower:
            return 0.30
        else:
            return 0.50  # Default to medium if unclear
    
    def _identify_scam_types(self, content: str, analysis: str) -> List[str]:
        """Identify types of scams detected"""
        scam_types = []
        content_lower = content.lower()
        analysis_lower = analysis.lower()
        
        combined = content_lower + " " + analysis_lower
        
        if any(word in combined for word in ["grandchild", "grandson", "granddaughter", "emergency", "jail"]):
            scam_types.append("Grandparent Emergency Scam")
        
        if any(word in combined for word in ["irs", "tax", "social security"]):
            scam_types.append("Government Impersonation Scam")
        
        if any(word in combined for word in ["microsoft", "apple", "tech support", "computer"]):
            scam_types.append("Tech Support Scam")
        
        if any(word in combined for word in ["won", "prize", "lottery", "sweepstakes"]):
            scam_types.append("Prize/Lottery Scam")
        
        if any(word in combined for word in ["romance", "love", "relationship", "dating"]):
            scam_types.append("Romance Scam")
        
        if any(word in combined for word in ["invest", "profit", "returns", "opportunity"]):
            scam_types.append("Investment Fraud")
        
        if any(word in combined for word in ["charity", "donation", "help", "disaster"]):
            scam_types.append("Charity Scam")
        
        if not scam_types and any(word in combined for word in ["bank", "account", "verify", "suspended"]):
            scam_types.append("Account Verification Scam")
        
        return scam_types if scam_types else ["Generic Financial Fraud"]
    
    def _categorize_risk(self, score: float) -> str:
        """Categorize risk score into simple levels"""
        if score >= 0.8:
            return "CRITICAL"
        elif score >= 0.6:
            return "HIGH"
        elif score >= 0.4:
            return "MEDIUM"
        else:
            return "LOW"
    
    def _generate_senior_warning(
        self,
        risk_score: float,
        scam_types: List[str],
        indicators: ScamIndicators
    ) -> str:
        """Generate clear, simple warning for seniors"""
        
        if risk_score >= 0.8:
            warning = "🚨 **STOP! This looks like a SCAM.**\n\n"
            warning += "Do NOT send money or share personal information.\n\n"
        elif risk_score >= 0.6:
            warning = "⚠️ **BE CAREFUL! This might be a scam.**\n\n"
            warning += "Think carefully before taking any action.\n\n"
        elif risk_score >= 0.4:
            warning = "⚡ **Caution: Some warning signs detected.**\n\n"
            warning += "Double-check before proceeding.\n\n"
        else:
            warning = "✓ **This seems okay, but stay alert.**\n\n"
        
        # Add specific warnings
        if scam_types:
            warning += f"**Type:** {scam_types[0]}\n\n"
        
        if indicators.urgency_language:
            warning += "• They want you to act FAST - scammers use urgency to trick you\n"
        
        if indicators.financial_request:
            warning += "• They're asking for MONEY - legitimate companies don't ask like this\n"
        
        if indicators.authority_impersonation:
            warning += "• They claim to be from an official organization - verify independently\n"
        
        if indicators.emotional_manipulation:
            warning += "• They're trying to scare or excite you - this is a manipulation tactic\n"
        
        return warning
    
    def _recommend_actions(self, risk_score: float, scam_types: List[str]) -> List[Dict[str, str]]:
        """Recommend actions based on risk level"""
        actions = []
        
        if risk_score >= 0.6:
            actions.append({
                "action": "do_not_respond",
                "label": "Do NOT Respond",
                "description": "Do not reply or take any action"
            })
            actions.append({
                "action": "verify_independently",
                "label": "Verify Independently",
                "description": "Call the official number (look it up yourself, don't use their number)"
            })
            actions.append({
                "action": "alert_family",
                "label": "Tell Your Family",
                "description": "Show this to a family member or friend"
            })
            actions.append({
                "action": "report",
                "label": "Report This Scam",
                "description": "Report to Facebook/YouTube and local authorities"
            })
        else:
            actions.append({
                "action": "verify",
                "label": "Verify First",
                "description": "Check with someone you trust before proceeding"
            })
            actions.append({
                "action": "research",
                "label": "Look It Up",
                "description": "Search online for this company or person"
            })
        
        return actions
    
    def _fallback_analysis(self, indicators: ScamIndicators) -> Dict[str, Any]:
        """Fallback analysis if AI fails"""
        # Count indicators
        indicator_count = sum([
            indicators.urgency_language,
            indicators.financial_request,
            indicators.authority_impersonation,
            indicators.emotional_manipulation,
            indicators.personal_info_request,
            indicators.suspicious_links,
            indicators.too_good_to_be_true
        ])
        
        risk_score = min(indicator_count * 0.2, 0.95)
        
        return {
            "scam_risk_score": risk_score,
            "risk_level": self._categorize_risk(risk_score),
            "detected_scam_types": ["Potential Scam"],
            "indicators": indicators,
            "senior_friendly_warning": self._generate_senior_warning(risk_score, [], indicators),
            "recommended_actions": self._recommend_actions(risk_score, []),
            "detailed_analysis": "Analysis based on pattern matching",
            "safe_to_proceed": risk_score < 0.3
        }

