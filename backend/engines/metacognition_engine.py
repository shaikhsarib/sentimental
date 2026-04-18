import json
from collections import Counter
from typing import List, Dict

class MetacognitionEngine:
    """
    The Self-Correction Loop.
    Grades agent performance by comparing swarm results to historical grounding.
    """
    
    def evaluate_swarm_performance(self, reactions: List[Dict], final_verdict: str, historical_grounding: str) -> Dict:
        """
        Analyze which agents were 'Right' vs 'Wrong' based on the consensus and historical reality.
        """
        performance_report = []
        lessons_learned = []
        
        # Risk priority mapping
        risk_map = {"CRITICAL": 10, "HIGH": 8, "MEDIUM": 5, "LOW": 2, "NONE": 0}
        target_score = risk_map.get(final_verdict, 5)
        grounding_score = risk_map.get(historical_grounding, 5)
        
        # Calculate SWARM ACCURACY
        for rx in reactions:
            persona_id = rx.get("persona_id")
            rx_score = rx.get("virality_risk", 5)
            
            # Error = Difference from final consolidated verdict
            error = abs(rx_score - target_score)
            
            # Drift = Difference from historical truth (biases)
            # Positive drift means over-reacting relative to reality
            drift_value = rx_score - grounding_score
            
            status = "ACCURATE"
            if error > 3:
                status = "MISTAKE"
            elif drift_value >= 4:
                status = "OVER_SENSITIVE"
            elif drift_value <= -4:
                status = "UNDER_SENSITIVE"
                
            performance_report.append({
                "persona_id": persona_id,
                "score": rx_score,
                "error": error,
                "drift_value": drift_value,
                "status": status,
                "feedback": self._generate_agent_feedback(persona_id, status, rx.get("reaction", ""))
            })
            
            if status != "ACCURATE":
                # Create a persistent lesson for this project's tactical memory
                lessons_learned.append({
                    "persona_id": persona_id,
                    "lesson": f"In previous simulations similar to this, your risk assessment was {status.lower().replace('_', ' ')}. You gave a score of {rx_score} while reality showed {grounding_score}. Adjust your threshold for {rx.get('trigger_phrase', 'similar topics')}."
                })
        
        return {
            "swarm_accuracy": self._calculate_swarm_accuracy(performance_report),
            "aggregate_drift": round(sum(p["drift_value"] for p in performance_report) / len(performance_report), 2) if performance_report else 0,
            "agent_grades": performance_report,
            "lessons_learned": lessons_learned
        }
        
    def _generate_agent_feedback(self, persona_id: str, status: str, reaction: str) -> str:
        if status == "ACCURATE":
            return f"Excellent grounding. {persona_id.capitalize()} correctly identified the narrative weight."
        if status == "MISTAKE":
            return f"{persona_id.capitalize()} was an outlier. The logic drifted too far from the swarm consensus."
        if status == "OVER_SENSITIVE":
            return f"{persona_id.capitalize()} demonstrated structural bias, over-reacting to a low-risk trigger."
        if status == "UNDER_SENSITIVE":
            return f"{persona_id.capitalize()} failed to detect the critical risk threshold identified in historical data."
        return "Insight recorded."

    def _calculate_swarm_accuracy(self, report: List[Dict]) -> float:
        if not report: return 0.0
        correct = sum(1 for r in report if r["status"] == "ACCURATE")
        return round((correct / len(report)) * 100, 1)
