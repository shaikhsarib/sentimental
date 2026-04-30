import asyncio
import json
import re
import time
import uuid
from collections import Counter
from typing import Dict, List, Optional

from engines.accuracy_engine import TripleVerificationEngine
from engines.crisis_database import CrisisDatabase
from engines.graph_simulation import GraphSimulation
from engines.macro_simulation import MacroSimulationEngine
from engines.metacognition_engine import MetacognitionEngine
from engines.multi_model import run_all_personas, run_individual_persona, run_synthesized_persona, taxonomy
from engines.consensus_engine import ConsensusEngine


class SimulationRunner:
    def __init__(self, crisis_db: CrisisDatabase):
        self.crisis_db = crisis_db
        self.verifier = TripleVerificationEngine()
        self.graph_sim = GraphSimulation(population=10000000)
        self.macro_sim = MacroSimulationEngine()
        self.meta_engine = MetacognitionEngine()
        self.consensus_engine = ConsensusEngine()

    async def run_shield(self, content: str, content_type: str = "general", industry: str = "general", objective: str = "General behavioral scan", on_persona_result=None, custom_personas=None, calibration_overrides=None, lessons: List[Dict] = None) -> Dict:
        """Step 4: Execute grounded swarm simulation."""
        start_time = time.time()

        similar_crises = self.crisis_db.find_similar_crises(content, industry, limit=3)
        historical_risk = "HIGH" if similar_crises else "LOW"

        # Simulation logic
        # Round 1: Initial Independent Reactions
        round1_reactions = []
        if custom_personas:
            tasks = []
            for p in custom_personas:
                # Filter lessons for this specific persona
                persona_lessons = [L["lesson"] for L in lessons if L["persona_id"] == p.get("persona_id") or L["persona_id"] == p.get("name")] if lessons else None
                tasks.append(run_synthesized_persona(p, content, content_type, objective, lessons=persona_lessons))
        else:
            tasks = []
            for pid in taxonomy.personas.keys():
                persona_lessons = [L["lesson"] for L in lessons if L["persona_id"] == pid] if lessons else None
                tasks.append(run_individual_persona(pid, content, content_type, objective, lessons=persona_lessons))
        
        for coro in asyncio.as_completed(tasks):
            res = await coro
            if isinstance(res, dict) and res.get("triggered"):
                round1_reactions.append(res)

        # Generate Consensus Briefing
        consensus_text = "; ".join([f"{r.get('persona_name')}: {r.get('reaction')[:100]} (Risk: {r.get('virality_risk')})" for r in round1_reactions])
        
        # Round 2: The Swarm Debate (Consensus Pass)
        personas_reactions = []
        if custom_personas:
            tasks = []
            for p in custom_personas:
                persona_lessons = [L["lesson"] for L in lessons if L["persona_id"] == p.get("persona_id") or L["persona_id"] == p.get("name")] if lessons else None
                tasks.append(run_synthesized_persona(p, content, content_type, objective, consensus_brief=consensus_text, lessons=persona_lessons))
            for coro in asyncio.as_completed(tasks):
                res = await coro
                if isinstance(res, dict) and res.get("triggered"):
                    # Apply Calibration Overrides (Phase 9)
                    if calibration_overrides and res.get("persona_id") in calibration_overrides:
                        weight = calibration_overrides[res["persona_id"]]
                        res["virality_risk"] = min(10, res.get("virality_risk", 1) * weight)
                    
                    personas_reactions.append(res)
                    if on_persona_result:
                        await on_persona_result(res)
        else:
            personas_reactions = round1_reactions # Fallback for legacy generic personas

        max_virality = max([r.get("virality_risk", 1) for r in personas_reactions], default=1)
        triggered_phrases = [
            {
                "phrase": r.get("trigger_phrase", ""),
                "which_personas_triggered": [r.get("persona_id")],
                "why_dangerous": r.get("reaction"),
            }
            for r in personas_reactions
            if r.get("trigger_phrase")
        ]

        ai_risk = "CRITICAL" if max_virality >= 8 else ("HIGH" if max_virality >= 6 else ("MEDIUM" if max_virality >= 4 else "LOW"))
        ai_unified = {"risk_level": ai_risk}

        verification = self.verifier.verify_prediction(
            ai_result=ai_unified,
            historical_risk=historical_risk,
            content=content,
            content_type=content_type,
            industry=industry,
        )

        # Extract emotions from agent reactions for sentiment-modulated SEIR
        detected_emotions = [r.get("emotion", "neutral") for r in personas_reactions if r.get("emotion")]
        graph_timeline = self.graph_sim.simulate_cascade(max_virality, emotions=detected_emotions)

        # PART 5: Agentic Metacognition (Evaluation)
        evaluation = self.meta_engine.evaluate_swarm_performance(
            reactions=personas_reactions,
            final_verdict=verification["final_risk_level"],
            historical_grounding=historical_risk
        )

        # PART 4: Silent Consensus Protocol (SCP)
        consensus = self.consensus_engine.evaluate_consensus(personas_reactions)

        processing_ms = int((time.time() - start_time) * 1000)

        return {
            "analysis_id": str(uuid.uuid4()),
            "mode": "shield",
            "processing_ms": processing_ms,
            "risk_level": verification["final_risk_level"],
            "confidence": consensus["agreement_score"],
            "consensus": consensus,
            "verification": {
                "agreement_score": verification["agreement_score"],
                "method_results": verification["method_results"],
            },
            "evaluation": evaluation,
            "graph_cascade": graph_timeline,
            "similar_historical_crises": [
                {
                    "brand": c.get("brand"),
                    "date": c.get("date"),
                    "summary": c.get("crisis_summary"),
                    "impact": c.get("revenue_impact"),
                }
                for c in similar_crises
            ],
            "regulatory_issues": [
                {
                    "framework": r.get("rule", "REGULATION"),
                    "severity": r.get("severity", "WARNING"),
                    "problematic_phrase": r.get("phrase", ""),
                    "explanation": r.get("explanation", ""),
                    "how_to_fix": r.get("fix", ""),
                }
                for r in verification["rules_triggered"]
            ],
            "trigger_phrases": triggered_phrases,
            "persona_reactions": personas_reactions,
        }

    async def run_macro(self, content: str, objective: str = "") -> Dict:
        start_time = time.time()
        macro_results = await self.macro_sim.run_time_skip_simulation(content, objective)
        processing_ms = int((time.time() - start_time) * 1000)
        return {
            "mode": "macro",
            "processing_ms": processing_ms,
            "macro_outcomes": macro_results,
        }

    async def run_full(self, content: str, content_type: str, industry: str, objective: str = "", on_persona_result=None, custom_personas=None, lessons: List[Dict] = None) -> Dict:
        shield_task = self.run_shield(content, content_type, industry, objective, on_persona_result=on_persona_result, custom_personas=custom_personas, lessons=lessons)
        macro_task = self.run_macro(content, objective)
        shield_result, macro_result = await asyncio.gather(shield_task, macro_task)
        return {
            "shield": shield_result,
            "macro": macro_result,
        }

    async def synthesize_personas_from_graph(self, project_id: str, graph: Dict) -> List[Dict]:
        """Step 3: Generate detailed persona profiles for graph entities."""
        from engines.multi_model import call_llm_with_settings
        
        nodes = graph.get("nodes", [])
        # Only synthesize for entities likely to be agents (Person/Group)
        potential_agents = [n for n in nodes if n.get("type") in ["PERSON", "GROUP", "ORGANIZATION", "ENTITY"]]
        
        personas = []
        for node in potential_agents[:10]: # Limit for demo/cost
            prompt = f"""Synthesize a tactical persona profile for this entity found in the mission graph.
ENTITY: {node["id"]}
TYPE: {node.get("type")}
DESCRIPTION: {node.get("description")}

Return JSON:
{{
  "persona_id": "{node["id"]}",
  "name": "{node["id"]}",
  "role": "...",
  "personality": "...",
  "behavioral_logic": "How they react to pressure",
  "background": "..."
}}"""
            res = await call_llm_with_settings(prompt, "llama-3.1-8b-instant", 0.7)
            if isinstance(res, str):
                try:
                    clean = re.search(r"\{.*\}", res, re.DOTALL).group(0)
                    personas.append(json.loads(clean))
                except: continue
            else:
                personas.append(res)
        
        return personas

    async def chat_with_persona(self, persona: Dict, mission_context: str, user_message: str) -> Dict:
        """Step 5: Interactive debriefing with a synthesized agent."""
        from engines.multi_model import call_llm_with_settings
        
        prompt = f"""You are acting as the specialized persona: {persona['name']}
ROLE: {persona.get('role')}
BACKGROUND: {persona.get('background')}
PERSONALITY: {persona.get('personality')}
LOGIC: {persona.get('behavioral_logic')}

MISSION CONTEXT: {mission_context}

The user is asking you a question about the operation. Respond in your authentic voice.
USER MESSAGE: {user_message}

Return JSON:
{{
  "persona_id": "{persona['persona_id']}",
  "response": "...",
  "mood": "..."
}}"""
        result = await call_llm_with_settings(prompt, "llama-3.3-70b-versatile", 0.7)
        result["persona_id"] = persona.get("persona_id", persona['name'])
        return result

    async def generate_strategic_summary(self, project_name: str, objective: str, reactions: List[Dict]) -> Dict:
        """Step 5 Synthesis: Turn raw swarm data into strategic intelligence."""
        from engines.multi_model import call_llm_with_settings
        
        # Aggregated stats for the prompt
        avg_virality = sum([r.get('virality_risk', 1) for r in reactions]) / len(reactions) if reactions else 0
        emotions = [r.get('emotion', 'Neutral') for r in reactions]
        emotion_counts = Counter(emotions)
        
        prompt = f"""You are the Sentimental Strategic Intelligence Synthesizer.
Analyze the following swarm simulation results and provide an Industrial-Grade Strategic Briefing.

PROJECT: {project_name}
MISSION OBJECTIVE: {objective}
SWARM DATA: {json.dumps(reactions, indent=2)}

Respond with strictly valid JSON:
{{
  "executive_summary": "Concise high-level overview of the mission outcome",
  "risk_scorecard": {{
    "total_risk": {avg_virality}, // 1-10
    "primary_friction": "The core entity or node that caused the most controversy",
    "consensus_level": "Level of agreement among agents (High/Medium/Low)"
  }},
  "mitigation_playbook": [
    {{
      "step": "Title of tactical action",
      "action": "Detailed instruction on how to resolve this specific risk",
      "urgency": "CRITICAL/HIGH/MEDIUM"
    }}
  ],
  "narrative_trajectory": "Prediction of how this narrative evolves in 72 hours"
}}
"""
        summary = await call_llm_with_settings(prompt, "llama-3.3-70b-versatile", 0.3)
        
        # Phase 12: Inject 10M Population Projection
        if isinstance(summary, dict) and "risk_scorecard" in summary:
            cascade_data = self.graph_sim.simulate_cascade(int(avg_virality))
            summary["risk_scorecard"]["population_cascade"] = cascade_data
            
        return summary
