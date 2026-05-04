import re
from typing import List, Dict, Optional
from engines.multi_model import call_llm_with_settings

class QueryEngine:
    """
    SentiFlow V6 Multi-Perspective Query Engine.
    Synthesizes swarm insights from specific professional lenses.
    Blueprint Page 34.
    """
    
    def __init__(self):
        self.PERSPECTIVES = {
            "businessman": {
                "focus": ["ROI", "Competitive Moat", "Market Opportunity", "Operational Risk"],
                "tone": "Direct, strategic, profit-oriented",
                "model": "llama-3.3-70b-versatile"
            },
            "investor": {
                "focus": ["TAM", "Exit Multiples", "Capital Efficiency", "Downside Protection"],
                "tone": "Analytical, risk-adjusted, skeptical",
                "model": "llama-3.3-70b-versatile"
            },
            "engineer": {
                "focus": ["Feasibility", "Scalability", "Edge Cases", "Technical Debt"],
                "tone": "Pragmatic, detail-oriented, skeptical",
                "model": "llama-3.1-8b-instant"
            },
            "policy": {
                "focus": ["Regulation", "Public Interest", "Precedent", "Ethical Impact"],
                "tone": "Formal, comprehensive, long-term",
                "model": "llama-3.3-70b-versatile"
            },
            "student": {
                "focus": ["Learning Curve", "Accessibility", "Career Relevance", "Fundamentals"],
                "tone": "Curious, clear, simple",
                "model": "llama-3.1-8b-instant"
            },
            "university": {
                "focus": ["Academic Rigor", "Citations", "Reproducibility", "Theoretic Novelty"],
                "tone": "Academic, formal, peer-reviewed style",
                "model": "llama-3.3-70b-versatile"
            }
        }

    async def query_swarm(self, query: str, perspective: str, debate_results: Dict) -> Dict:
        """
        Queries the million-agent swarm from a specific lens.
        """
        p_config = self.PERSPECTIVES.get(perspective.lower())
        if not p_config:
            raise ValueError(f"Invalid perspective: {perspective}")

        # 1. Extract context from debate results
        judge_verdict = debate_results.get("judge_verdict", {}).get("consolidated_verdict", "")
        top_voices = debate_results.get("representative_debate", [])[:10]
        consensus = debate_results.get("consensus", {})
        
        voices_transcript = "\n".join([
            f"AGENT {v['persona_name']} ({v['position']}): {v['reaction']}"
            for v in top_voices
        ])

        # 2. Build Perspective-Aware Prompt
        prompt = f"""
SYSTEM: You are the SentiFlow V6 Query Engine, acting from the perspective of a {perspective.upper()}.
Your focus areas are: {", ".join(p_config['focus'])}.
Tone: {p_config['tone']}.

SWARM DEBATE CONTEXT:
Arbiter Verdict: {judge_verdict}
Consensus Confidence: {consensus.get('final_confidence', 0.5)}
Key Swarm Voices:
{voices_transcript}

USER QUERY:
{query}

YOUR TASK:
Synthesize an answer to the query based strictly on the swarm's debate and the consolidated verdict. 
View the situation through the lens of a {perspective}.
Identify 3-5 specific 'Strategic Insights' or 'Critical Risks'.

Respond in strictly valid JSON:
{{
    "synthesis": "string",
    "perspective": "{perspective}",
    "strategic_insights": ["string"],
    "critical_risks": ["string"],
    "swarm_alignment": 0.0 to 1.0
}}
"""
        try:
            import json
            response = await call_llm_with_settings(prompt, p_config["model"], 0.7)
            if isinstance(response, str):
                match = re.search(r'\{.*\}', response, re.DOTALL)
                if match:
                    return json.loads(match.group(0))
            return response
        except Exception as e:
            print(f"[ERROR] Swarm Query failed: {e}")
            return {"error": str(e)}
