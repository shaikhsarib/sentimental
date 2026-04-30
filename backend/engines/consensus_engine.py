"""
SentiFlow V5: Silent Consensus Protocol (SCP) Engine
=====================================================
The core Trust Moat. This engine evaluates swarm agreement and REFUSES to
output a prediction when agent consensus is below a validated confidence threshold.

Instead of hallucinating, SentiFlow explicitly declares uncertainty and maps
the disagreement back to specific intelligence gaps that need to be filled.

Protocol Statuses:
  CONFIDENT         — High swarm agreement (>= 0.78). Prediction is trustworthy.
  UNCERTAIN         — Moderate agreement (0.50 - 0.78). Proceed with caution.
  INSUFFICIENT      — Low agreement (< 0.50). Refuse to predict. Return intelligence gaps.
  DEBATE_STALEMATE  — High variance in risk scores (> 0.35). Agents fundamentally disagree.
"""

import numpy as np
from typing import Dict, List, Optional, Tuple
from enum import Enum


class ConsensusStatus(str, Enum):
    """Consensus evaluation outcome."""
    CONFIDENT = "CONFIDENT"
    UNCERTAIN = "UNCERTAIN"
    INSUFFICIENT = "INSUFFICIENT_CONSENSUS"
    STALEMATE = "DEBATE_STALEMATE"


class ConsensusEngine:
    """
    The Silent Consensus Protocol™ (SCP).
    
    Evaluates swarm debate results and determines whether the collective
    intelligence has reached sufficient agreement to produce a trustworthy prediction.
    
    Key Innovation: Rather than forcing a prediction from noisy agent data,
    SCP explicitly refuses to predict when confidence is low — and returns
    actionable intelligence gaps that explain WHY consensus failed.
    """

    # ─── THRESHOLDS ───
    CONFIDENCE_THRESHOLD = 0.78     # Minimum agreement score for CONFIDENT status
    UNCERTAIN_THRESHOLD = 0.50      # Minimum for UNCERTAIN (below = INSUFFICIENT)
    DISAGREEMENT_THRESHOLD = 0.35   # Max normalized variance before STALEMATE
    MIN_AGENTS_FOR_CONSENSUS = 3    # Need at least 3 agents for meaningful consensus

    def evaluate_consensus(self, reactions: List[Dict]) -> Dict:
        """
        Evaluate swarm consensus across all agent reactions.
        
        Args:
            reactions: List of agent reaction dicts from the swarm debate.
                       Each must contain at minimum: persona_id, virality_risk, reaction
        
        Returns:
            ConsensusResult with status, confidence metrics, and intelligence gaps.
        """
        if not reactions or len(reactions) < self.MIN_AGENTS_FOR_CONSENSUS:
            return self._build_result(
                status=ConsensusStatus.INSUFFICIENT,
                agreement_score=0.0,
                risk_variance=1.0,
                reactions=reactions or [],
                intelligence_gaps=[
                    {
                        "gap_type": "INSUFFICIENT_AGENTS",
                        "description": f"Only {len(reactions or [])} agents responded. Minimum {self.MIN_AGENTS_FOR_CONSENSUS} required for reliable consensus.",
                        "action": "Add more documents to the mission to generate additional specialized agents.",
                        "severity": "CRITICAL"
                    }
                ]
            )

        # ── Step 1: Extract risk vectors ──
        risk_scores = np.array([
            float(r.get("virality_risk", 5)) for r in reactions
        ])

        # ── Step 2: Compute agreement metrics ──
        agreement_score = self._compute_agreement_score(risk_scores)
        risk_variance = self._compute_normalized_variance(risk_scores)

        # ── Step 3: Detect polarization ──
        is_polarized, clusters = self._detect_polarization(risk_scores, reactions)

        # ── Step 4: Identify intelligence gaps ──
        intelligence_gaps = self._identify_intelligence_gaps(
            reactions, risk_scores, agreement_score, risk_variance, is_polarized, clusters
        )

        # ── Step 5: Determine consensus status ──
        if is_polarized and risk_variance > self.DISAGREEMENT_THRESHOLD:
            status = ConsensusStatus.STALEMATE
        elif agreement_score >= self.CONFIDENCE_THRESHOLD:
            status = ConsensusStatus.CONFIDENT
        elif agreement_score >= self.UNCERTAIN_THRESHOLD:
            status = ConsensusStatus.UNCERTAIN
        else:
            status = ConsensusStatus.INSUFFICIENT

        # ── Step 6: Compute directional consensus ──
        consensus_risk_level = self._classify_consensus_risk(risk_scores, status)

        return self._build_result(
            status=status,
            agreement_score=agreement_score,
            risk_variance=risk_variance,
            reactions=reactions,
            intelligence_gaps=intelligence_gaps,
            is_polarized=is_polarized,
            clusters=clusters,
            consensus_risk_level=consensus_risk_level,
        )

    def _compute_agreement_score(self, risk_scores: np.ndarray) -> float:
        """
        Compute agreement score using normalized inverse variance.
        
        Perfect agreement (all same) → 1.0
        Maximum disagreement → 0.0
        
        Uses a scaled sigmoid-like mapping from variance to agreement.
        """
        if len(risk_scores) < 2:
            return 0.0

        # Variance normalized to 0-1 range (max possible variance for 1-10 scale is ~20.25)
        variance = float(np.var(risk_scores))
        max_possible_variance = 20.25  # When half the agents say 1, half say 10
        
        normalized_var = min(1.0, variance / max_possible_variance)
        
        # Agreement = 1 - normalized_variance, with exponential decay
        # This makes agreement drop faster for moderate disagreement
        agreement = float(np.exp(-3.0 * normalized_var))
        
        return round(min(1.0, max(0.0, agreement)), 4)

    def _compute_normalized_variance(self, risk_scores: np.ndarray) -> float:
        """Compute variance normalized to 0-1 scale."""
        if len(risk_scores) < 2:
            return 1.0
        variance = float(np.var(risk_scores))
        max_possible_variance = 20.25
        return round(min(1.0, variance / max_possible_variance), 4)

    def _detect_polarization(
        self, risk_scores: np.ndarray, reactions: List[Dict]
    ) -> Tuple[bool, Optional[Dict]]:
        """
        Detect if agents are forming opposing clusters rather than
        converging to a shared assessment.
        
        Uses a simple bimodal detection: if the distribution has two peaks
        separated by > 3 points on the risk scale, it's polarized.
        """
        if len(risk_scores) < 4:
            return False, None

        sorted_scores = np.sort(risk_scores)
        median = float(np.median(sorted_scores))
        
        low_cluster = sorted_scores[sorted_scores <= median]
        high_cluster = sorted_scores[sorted_scores > median]

        if len(low_cluster) == 0 or len(high_cluster) == 0:
            return False, None

        low_mean = float(np.mean(low_cluster))
        high_mean = float(np.mean(high_cluster))
        gap = high_mean - low_mean

        is_polarized = gap > 3.0

        if is_polarized:
            # Identify which agents belong to which cluster
            low_agents = [
                r.get("persona_id", "unknown")
                for r in reactions
                if float(r.get("virality_risk", 5)) <= median
            ]
            high_agents = [
                r.get("persona_id", "unknown")
                for r in reactions
                if float(r.get("virality_risk", 5)) > median
            ]
            clusters = {
                "low_risk_cluster": {
                    "agents": low_agents,
                    "mean_risk": round(low_mean, 2),
                },
                "high_risk_cluster": {
                    "agents": high_agents,
                    "mean_risk": round(high_mean, 2),
                },
                "cluster_gap": round(gap, 2),
            }
            return True, clusters

        return False, None

    def _identify_intelligence_gaps(
        self,
        reactions: List[Dict],
        risk_scores: np.ndarray,
        agreement_score: float,
        risk_variance: float,
        is_polarized: bool,
        clusters: Optional[Dict],
    ) -> List[Dict]:
        """
        Map low-confidence signals back to specific missing data.
        This is what makes SCP actionable: instead of just saying "we don't know,"
        we say "here's WHAT we don't know and HOW to fix it."
        """
        gaps = []

        # Gap 1: High variance indicates conflicting interpretive frames
        if risk_variance > 0.20:
            outlier_agents = self._find_outlier_agents(reactions, risk_scores)
            if outlier_agents:
                gaps.append({
                    "gap_type": "CONFLICTING_FRAMES",
                    "description": f"Agents {', '.join(outlier_agents)} interpret the narrative through fundamentally different risk frameworks.",
                    "action": "Add more context documents that clarify the specific regulatory, cultural, or market context.",
                    "severity": "HIGH",
                    "outlier_agents": outlier_agents,
                })

        # Gap 2: Polarized clusters suggest missing mediating context
        if is_polarized and clusters:
            low_agents = clusters["low_risk_cluster"]["agents"]
            high_agents = clusters["high_risk_cluster"]["agents"]
            gaps.append({
                "gap_type": "POLARIZED_ASSESSMENT",
                "description": f"Agents are split into two camps: {low_agents} see low risk, {high_agents} see high risk. No middle ground.",
                "action": "Upload the target audience demographics and historical brand sentiment data to help agents contextualize.",
                "severity": "HIGH",
            })

        # Gap 3: Low agreement on trigger phrases indicates ambiguous content
        trigger_phrases = [r.get("trigger_phrase", "") for r in reactions if r.get("trigger_phrase")]
        unique_triggers = set(trigger_phrases)
        if len(unique_triggers) > len(reactions) * 0.7:
            gaps.append({
                "gap_type": "AMBIGUOUS_TRIGGERS",
                "description": "Agents are focusing on different aspects of the content. No convergent threat vector identified.",
                "action": "Narrow the simulation objective to a specific concern (e.g., 'regulatory risk' vs. 'brand perception').",
                "severity": "MEDIUM",
            })

        # Gap 4: Insufficient emotional signal diversity
        emotions = [r.get("emotion", "").lower() for r in reactions if r.get("emotion")]
        unique_emotions = set(emotions)
        if len(unique_emotions) <= 1 and len(reactions) > 3:
            gaps.append({
                "gap_type": "HOMOGENEOUS_RESPONSE",
                "description": "All agents produced the same emotional response. This may indicate prompt contamination or insufficient persona diversity.",
                "action": "Add domain-specific documents or use the Agent Taxonomy to include more diverse expert perspectives.",
                "severity": "MEDIUM",
            })

        # Gap 5: Missing data signal — low average confidence
        if agreement_score < self.UNCERTAIN_THRESHOLD:
            gaps.append({
                "gap_type": "LOW_CONFIDENCE",
                "description": "Overall swarm confidence is below the minimum threshold for reliable prediction.",
                "action": "Add more source documents, refine the mission objective, or increase agent count.",
                "severity": "CRITICAL",
            })

        return gaps

    def _find_outlier_agents(
        self, reactions: List[Dict], risk_scores: np.ndarray
    ) -> List[str]:
        """Identify agents whose risk scores deviate more than 1.5 IQR from the median."""
        if len(risk_scores) < 3:
            return []

        q1 = float(np.percentile(risk_scores, 25))
        q3 = float(np.percentile(risk_scores, 75))
        iqr = q3 - q1
        lower = q1 - 1.5 * iqr
        upper = q3 + 1.5 * iqr

        outliers = []
        for r, score in zip(reactions, risk_scores):
            if score < lower or score > upper:
                outliers.append(r.get("persona_id", "unknown"))
        return outliers

    def _classify_consensus_risk(
        self, risk_scores: np.ndarray, status: ConsensusStatus
    ) -> str:
        """
        Determine the consensus risk level.
        Only returns a definitive level if status is CONFIDENT.
        """
        if status == ConsensusStatus.INSUFFICIENT or status == ConsensusStatus.STALEMATE:
            return "INDETERMINATE"

        median_risk = float(np.median(risk_scores))

        if median_risk >= 8:
            return "CRITICAL"
        elif median_risk >= 6:
            return "HIGH"
        elif median_risk >= 4:
            return "MEDIUM"
        else:
            return "LOW"

    def _build_result(
        self,
        status: ConsensusStatus,
        agreement_score: float,
        risk_variance: float,
        reactions: List[Dict],
        intelligence_gaps: List[Dict],
        is_polarized: bool = False,
        clusters: Optional[Dict] = None,
        consensus_risk_level: str = "INDETERMINATE",
    ) -> Dict:
        """Build the structured consensus result."""
        risk_scores = [float(r.get("virality_risk", 5)) for r in reactions]

        result = {
            "status": status.value,
            "agreement_score": agreement_score,
            "risk_variance": risk_variance,
            "consensus_risk_level": consensus_risk_level,
            "is_trustworthy": status == ConsensusStatus.CONFIDENT,
            "should_refuse": status in (ConsensusStatus.INSUFFICIENT, ConsensusStatus.STALEMATE),

            "metrics": {
                "agent_count": len(reactions),
                "mean_risk": round(float(np.mean(risk_scores)), 2) if risk_scores else 0,
                "median_risk": round(float(np.median(risk_scores)), 2) if risk_scores else 0,
                "std_dev": round(float(np.std(risk_scores)), 2) if risk_scores else 0,
                "min_risk": int(min(risk_scores)) if risk_scores else 0,
                "max_risk": int(max(risk_scores)) if risk_scores else 0,
            },

            "intelligence_gaps": intelligence_gaps,
            "is_polarized": is_polarized,
        }

        if clusters:
            result["polarization_clusters"] = clusters

        # Generate human-readable verdict
        if status == ConsensusStatus.CONFIDENT:
            result["verdict"] = f"Swarm consensus is STRONG (agreement: {agreement_score:.0%}). Prediction is reliable."
        elif status == ConsensusStatus.UNCERTAIN:
            result["verdict"] = f"Swarm consensus is MODERATE (agreement: {agreement_score:.0%}). Prediction should be treated as directional only."
        elif status == ConsensusStatus.STALEMATE:
            result["verdict"] = f"DEBATE STALEMATE detected. Agents are fundamentally split on risk assessment. Additional context required."
        else:
            result["verdict"] = f"INSUFFICIENT CONSENSUS (agreement: {agreement_score:.0%}). SentiFlow refuses to predict. {len(intelligence_gaps)} intelligence gap(s) identified."

        return result
