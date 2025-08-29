from enum import Enum
from typing import NamedTuple, List, Tuple, Dict, Any
import math
import json

# --- 1. Core Logic Types (from previous implementation) ---
class Belnap(Enum):
    T = "True"
    F = "False" 
    B = "Both"    # Contradiction
    N = "Neither" # Unknown

class Evidence(NamedTuple):
    source: str
    belief: Belnap
    weight: float

class Decision(NamedTuple):
    prop: str
    truth: Belnap
    confidence: float
    reasoning: str

class ToneStyle(Enum):
    CASUAL = "casual"
    EXPERT = "expert" 
    EMPATHETIC = "empathetic"
    NEUTRAL = "neutral"

# --- 2. Enhanced Evidence Database ---
evidence_db = {
    "Stressed(User)": [
        Evidence("HeartRateMonitor", Belnap.T, 0.85),
        Evidence("JournalEntry", Belnap.T, 0.75),
        Evidence("SleepPattern", Belnap.T, 0.60)
    ],
    "Likes(Hiking)": [
        Evidence("UserSurvey", Belnap.T, 0.80),
        Evidence("PastBookings", Belnap.T, 0.70),
        Evidence("FriendComment", Belnap.F, 0.30),
        Evidence("WeatherPreference", Belnap.T, 0.50)
    ],
    "Dislikes(Crowds)": [
        Evidence("UserSurvey", Belnap.T, 0.85),
        Evidence("LocationHistory", Belnap.T, 0.75),
        Evidence("SocialMedia", Belnap.T, 0.65),
        Evidence("EventAttendance", Belnap.F, 0.40)
    ],
    "Prefers(Outdoors)": [
        Evidence("ActivityHistory", Belnap.T, 0.90),
        Evidence("PhotoAnalysis", Belnap.T, 0.70),
        Evidence("WeatherCorrelation", Belnap.T, 0.60)
    ]
}

activities_db = {
    "MeditationRetreat": {
        "crowdiness": 0.1,
        "outdoor": 0.3,
        "physical": 0.2,
        "stress_relief": 0.9
    },
    "MountainHike": {
        "crowdiness": 0.3,
        "outdoor": 1.0,
        "physical": 0.8,
        "stress_relief": 0.7
    },
    "ShortHike": {
        "crowdiness": 0.6,
        "outdoor": 0.9,
        "physical": 0.5,
        "stress_relief": 0.6
    },
    "UrbanWalk": {
        "crowdiness": 0.7,
        "outdoor": 0.6,
        "physical": 0.4,
        "stress_relief": 0.4
    },
    "MallShopping": {
        "crowdiness": 0.9,
        "outdoor": 0.0,
        "physical": 0.3,
        "stress_relief": 0.1
    },
    "BeachWalk": {
        "crowdiness": 0.4,
        "outdoor": 1.0,
        "physical": 0.4,
        "stress_relief": 0.8
    }
}

# --- 3. Core Reasoning Functions ---
def decide(prop: str, verbose: bool = False) -> Decision:
    """Enhanced decide with detailed reasoning trace."""
    evs = evidence_db.get(prop, [])
    
    if not evs:
        reasoning = f"No evidence found for {prop}"
        if verbose:
            print(f"  🔍 {reasoning}")
        return Decision(prop, Belnap.N, 0.0, reasoning)
    
    t_weight = sum(e.weight for e in evs if e.belief == Belnap.T)
    f_weight = sum(e.weight for e in evs if e.belief == Belnap.F)
    b_weight = sum(e.weight for e in evs if e.belief == Belnap.B)
    total = t_weight + f_weight + b_weight
    
    if verbose:
        print(f"  🔍 Evidence for {prop}:")
        for e in evs:
            print(f"    - {e.source}: {e.belief.value} (weight={e.weight})")
        print(f"    Totals: T={t_weight:.2f}, F={f_weight:.2f}, B={b_weight:.2f}")
    
    if total == 0:
        reasoning = f"All evidence has zero weight"
        return Decision(prop, Belnap.N, 0.0, reasoning)
    
    # Determine truth value
    if t_weight > 0 and f_weight > 0:
        truth = Belnap.B
        reasoning = f"Contradiction: both supporting ({t_weight:.2f}) and opposing ({f_weight:.2f}) evidence"
    elif t_weight > f_weight:
        truth = Belnap.T
        reasoning = f"Supported: {t_weight:.2f} > {f_weight:.2f}"
    elif f_weight > t_weight:
        truth = Belnap.F
        reasoning = f"Opposed: {f_weight:.2f} > {t_weight:.2f}"
    else:
        truth = Belnap.N
        reasoning = f"Balanced or unknown: T={t_weight:.2f}, F={f_weight:.2f}"
    
    # Calculate confidence using sigmoid
    if total > 0:
        net_evidence = abs(t_weight - f_weight)
        confidence = 1 / (1 + math.exp(-4 * (net_evidence / total - 0.1)))
    else:
        confidence = 0.0
    
    if verbose:
        print(f"    ⚖️  Result: {truth.value} (confidence={confidence:.2f}) - {reasoning}")
    
    return Decision(prop, truth, confidence, reasoning)

# --- 4. Natural Language Explanation Generator ---
class ExplanationGenerator:
    def __init__(self, tone: ToneStyle = ToneStyle.NEUTRAL):
        self.tone = tone
        self._load_templates()
    
    def _load_templates(self):
        self.templates = {
            ToneStyle.CASUAL: {
                "context_stress_high": "You seem pretty stressed right now (I'm {confidence}% confident based on {sources}).",
                "context_stress_medium": "You're showing some signs of stress (confidence: {confidence}%).",
                "context_stress_low": "You appear relatively calm right now.",
                "recommendation": "I picked **{option}** because it's great for {primary_reason}. {secondary_reasons}",
                "confidence_high": "I'm quite confident about this choice.",
                "confidence_medium": "I'm moderately confident in this recommendation.",
                "confidence_low": "I'm somewhat uncertain, but this seems like the best option.",
                "contradiction": "I know you have {factor}, but {resolution}.",
                "filtered": "I ruled out **{option}** since {reason}.",
                "summary": "Perfect for {key_benefit}!"
            },
            ToneStyle.EXPERT: {
                "context_stress_high": "Elevated stress indicators detected (confidence: {confidence}%, sources: {sources}).",
                "context_stress_medium": "Moderate stress signals observed (confidence: {confidence}%).",
                "context_stress_low": "Baseline stress levels detected.",
                "recommendation": "**{option}** selected for optimal {primary_reason}. {secondary_reasons}",
                "confidence_high": "High confidence recommendation.",
                "confidence_medium": "Moderate confidence level.",
                "confidence_low": "Lower confidence due to limited data.",
                "contradiction": "Conflicting evidence for {factor} resolved via {resolution}.",
                "filtered": "**{option}** eliminated: {reason}.",
                "summary": "Optimized for {key_benefit}."
            },
            ToneStyle.EMPATHETIC: {
                "context_stress_high": "I can see you're going through a stressful time right now (I'm {confidence}% confident based on {sources}).",
                "context_stress_medium": "You might be feeling a bit overwhelmed lately (confidence: {confidence}%).",
                "context_stress_low": "You seem to be in a good headspace right now.",
                "recommendation": "I think **{option}** would be really good for you because it excels at {primary_reason}. {secondary_reasons}",
                "confidence_high": "I feel quite sure this is a great choice for you.",
                "confidence_medium": "This seems like a solid option for your situation.",
                "confidence_low": "I'm not entirely sure, but I think this might help you.",
                "contradiction": "I understand you have {factor}, but I believe {resolution}.",
                "filtered": "I didn't suggest **{option}** because {reason}, and I want to respect your preferences.",
                "summary": "Thoughtfully chosen for {key_benefit}."
            },
            ToneStyle.NEUTRAL: {
                "context_stress_high": "Current stress level: high (confidence: {confidence}%, sources: {sources}).",
                "context_stress_medium": "Current stress level: moderate (confidence: {confidence}%).",
                "context_stress_low": "Current stress level: low.",
                "recommendation": "**{option}** recommended for {primary_reason}. {secondary_reasons}",
                "confidence_high": "High confidence.",
                "confidence_medium": "Moderate confidence.",
                "confidence_low": "Low confidence.",
                "contradiction": "Contradiction in {factor} resolved: {resolution}.",
                "filtered": "Filtered: **{option}** - {reason}.",
                "summary": "Selected for {key_benefit}."
            }
        }

    def generate_explanation(self, reasoning_trace: Dict[str, Any]) -> str:
        components = []
        
        # Context
        context = self._generate_context(reasoning_trace.get("user_state", {}))
        if context:
            components.append(context)
        
        # Main recommendation
        rec = self._generate_recommendation(reasoning_trace)
        components.append(rec)
        
        # Confidence
        conf = self._generate_confidence(reasoning_trace.get("confidence", 0))
        components.append(conf)
        
        # Handle contradictions
        contradictions = self._generate_contradictions(reasoning_trace.get("contradictions", []))
        if contradictions:
            components.append(contradictions)
        
        # Filtered items (limit to most important)
        filtered = self._generate_filtered(reasoning_trace.get("filtered_out", [])[:2])
        if filtered:
            components.append(filtered)
        
        return " ".join(components)

    def generate_summary(self, reasoning_trace: Dict[str, Any]) -> str:
        """Generate a one-line summary for quick UI display."""
        evidence = reasoning_trace.get("evidence", [])
        if not evidence:
            return "Recommended activity"
        
        primary = max(evidence, key=lambda x: x.get("weight", 0))
        key_benefit = primary.get("factor", "general wellness")
        
        template = self.templates[self.tone]["summary"]
        return template.format(key_benefit=key_benefit)

    def _generate_context(self, user_state: Dict[str, Any]) -> str:
        if not user_state:
            return ""
        
        stress_level = user_state.get("stress_level", "unknown")
        confidence = int(user_state.get("confidence", 0) * 100)
        sources = user_state.get("sources", ["multiple indicators"])
        
        template_key = f"context_stress_{stress_level}"
        template = self.templates[self.tone].get(template_key, "")
        
        return template.format(
            confidence=confidence,
            sources=", ".join(sources[:3])  # Limit to 3 sources for readability
        )

    def _generate_recommendation(self, trace: Dict[str, Any]) -> str:
        decision = trace.get("decision", "Unknown")
        option = decision.replace("Recommend ", "") if "Recommend " in decision else decision
        
        evidence = trace.get("evidence", [])
        if not evidence:
            return f"**{option}** recommended."
        
        primary = max(evidence, key=lambda x: x.get("weight", 0))
        primary_reason = primary.get("factor", "unknown benefits")
        
        secondary = [e for e in evidence if e != primary][:2]
        if secondary:
            secondary_text = "Also beneficial for " + " and ".join([
                e.get("factor", "unknown") for e in secondary
            ]) + "."
        else:
            secondary_text = ""
        
        template = self.templates[self.tone]["recommendation"]
        return template.format(
            option=option,
            primary_reason=primary_reason,
            secondary_reasons=secondary_text
        )

    def _generate_confidence(self, confidence: float) -> str:
        conf_percent = int(confidence * 100)
        
        if conf_percent >= 80:
            template_key = "confidence_high"
        elif conf_percent >= 60:
            template_key = "confidence_medium"
        else:
            template_key = "confidence_low"
        
        return self.templates[self.tone][template_key]

    def _generate_contradictions(self, contradictions: List[Dict[str, Any]]) -> str:
        if not contradictions:
            return ""
        
        parts = []
        template = self.templates[self.tone]["contradiction"]
        
        for contradiction in contradictions[:2]:  # Limit to 2 most important
            factor = contradiction.get("factor", "conflicting preferences")
            resolution = contradiction.get("resolution", "other factors took precedence")
            parts.append(template.format(factor=factor, resolution=resolution))
        
        return " ".join(parts)

    def _generate_filtered(self, filtered_out: List[Dict[str, Any]]) -> str:
        if not filtered_out:
            return ""
        
        parts = []
        template = self.templates[self.tone]["filtered"]
        
        for filtered_item in filtered_out:
            option = filtered_item.get("option", "alternative option")
            reason = filtered_item.get("reason", "did not meet criteria")
            parts.append(template.format(option=option, reason=reason))
        
        return " ".join(parts)

# --- 5. Integrated Reasoning Pipeline with Explanations ---
class RecommendationWithExplanation(NamedTuple):
    activity: str
    score: float
    metadata: Dict[str, Any]
    rank: int
    explanation: str
    summary: str
    reasoning_trace: Dict[str, Any]

def recommend_activities_with_explanations(
    tone: ToneStyle = ToneStyle.NEUTRAL,
    verbose: bool = True
) -> List[RecommendationWithExplanation]:
    """Complete recommendation system with integrated explanations."""
    
    if verbose:
        print("=" * 60)
        print("🧠 EXPLAINABLE AI REASONING SYSTEM")
        print("=" * 60)
    
    # Step 1: Make logical decisions
    decisions = {
        "stressed": decide("Stressed(User)", verbose),
        "likes_hiking": decide("Likes(Hiking)", verbose),
        "dislikes_crowds": decide("Dislikes(Crowds)", verbose),
        "prefers_outdoors": decide("Prefers(Outdoors)", verbose)
    }
    
    if verbose:
        print(f"\n📊 DECISIONS SUMMARY:")
        for key, dec in decisions.items():
            print(f"  {key}: {dec.truth.value} (conf={dec.confidence:.2f})")
    
    # Step 2: Apply filtering and scoring
    candidate_activities = list(activities_db.items())
    filtered_out = []
    scored_activities = []
    
    for activity, metadata in candidate_activities:
        # Crowd filtering
        crowd_level = metadata["crowdiness"]
        dislike_confidence = decisions["dislikes_crowds"].confidence
        adaptive_threshold = 0.5 - (dislike_confidence * 0.3)
        
        if crowd_level > adaptive_threshold:
            reason = f"crowdiness level ({crowd_level:.1f}) exceeds tolerance threshold ({adaptive_threshold:.2f})"
            filtered_out.append({"option": activity, "reason": reason})
            if verbose:
                print(f"  ❌ {activity} filtered: {reason}")
            continue
        
        if verbose:
            print(f"  ✅ {activity} passed crowd filter")
        
        # Calculate score
        base_score = 0.5
        evidence_factors = []
        
        # Stress relief bonus
        if decisions["stressed"].truth == Belnap.T and decisions["stressed"].confidence > 0.7:
            stress_bonus = metadata["stress_relief"] * decisions["stressed"].confidence * 0.4
            base_score += stress_bonus
            evidence_factors.append({
                "factor": "stress relief potential",
                "value": metadata["stress_relief"],
                "weight": 0.4,
                "contribution": stress_bonus
            })
        
        # Outdoor preference bonus
        if decisions["prefers_outdoors"].truth == Belnap.T:
            outdoor_bonus = metadata["outdoor"] * decisions["prefers_outdoors"].confidence * 0.3
            base_score += outdoor_bonus
            evidence_factors.append({
                "factor": "outdoor preference alignment",
                "value": metadata["outdoor"],
                "weight": 0.3,
                "contribution": outdoor_bonus
            })
        
        # Hiking preference (with contradiction handling)
        hiking_decision = decisions["likes_hiking"]
        if hiking_decision.truth == Belnap.T and metadata["physical"] > 0.5:
            hiking_bonus = metadata["physical"] * hiking_decision.confidence * 0.2
            base_score += hiking_bonus
            evidence_factors.append({
                "factor": "physical activity alignment",
                "value": metadata["physical"],
                "weight": 0.2,
                "contribution": hiking_bonus
            })
        elif hiking_decision.truth == Belnap.B:  # Contradiction case
            small_bonus = 0.05
            base_score += small_bonus
            evidence_factors.append({
                "factor": "physical activity (conservative)",
                "value": metadata["physical"],
                "weight": 0.05,
                "contribution": small_bonus
            })
        
        scored_activities.append((activity, base_score, metadata, evidence_factors))
    
    # Step 3: Generate recommendations with explanations
    scored_activities.sort(key=lambda x: x[1], reverse=True)
    generator = ExplanationGenerator(tone)
    recommendations = []
    
    for i, (activity, score, metadata, evidence) in enumerate(scored_activities[:3]):
        # Build reasoning trace
        contradictions = []
        if decisions["likes_hiking"].truth == Belnap.B:
            contradictions.append({
                "factor": "mixed feelings about hiking activities",
                "resolution": "conservative approach taken due to other strong factors"
            })
        
        user_state = {
            "stress_level": "high" if decisions["stressed"].truth == Belnap.T and decisions["stressed"].confidence > 0.8 else "moderate",
            "confidence": decisions["stressed"].confidence,
            "sources": ["heart rate monitor", "journal entries", "sleep patterns"]
        }
        
        reasoning_trace = {
            "decision": f"Recommend {activity}",
            "confidence": min(score / 2.0, 1.0),  # Normalize to [0,1]
            "user_state": user_state,
            "evidence": evidence,
            "contradictions": contradictions,
            "filtered_out": filtered_out
        }
        
        # Generate explanations
        explanation = generator.generate_explanation(reasoning_trace)
        summary = generator.generate_summary(reasoning_trace)
        
        recommendation = RecommendationWithExplanation(
            activity=activity,
            score=score,
            metadata=metadata,
            rank=i + 1,
            explanation=explanation,
            summary=summary,
            reasoning_trace=reasoning_trace
        )
        
        recommendations.append(recommendation)
        
        if verbose:
            print(f"\n🏆 #{i+1}: {activity} (score={score:.2f})")
            print(f"   📝 {summary}")
            print(f"   💬 {explanation}")
    
    if verbose:
        print("=" * 60)
    
    return recommendations

# --- 6. Demo and Testing ---
if __name__ == "__main__":
    print("Testing all tone styles:\n")
    
    for tone in [ToneStyle.CASUAL, ToneStyle.EXPERT, ToneStyle.EMPATHETIC, ToneStyle.NEUTRAL]:
        print(f"🎭 {tone.value.upper()} TONE:")
        print("=" * 50)
        
        recommendations = recommend_activities_with_explanations(
            tone=tone,
            verbose=False  # Set to True for full pipeline trace
        )
        
        for rec in recommendations:
            print(f"#{rec.rank}: {rec.activity}")
            print(f"Summary: {rec.summary}")
            print(f"Explanation: {rec.explanation}")
            print(f"Score: {rec.score:.2f}\n")
        
        print("\n")