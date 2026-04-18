import asyncio
import json
from .multi_model import call_llm_with_settings

class MacroSimulationEngine:
    """
    Narrative Time-Skip Simulator
    Multi-stage pipeline for factions, tensions, and timelines.
    """
    
    async def run_time_skip_simulation(self, world_text: str, objective: str = "") -> dict:
        """Analyze large texts and extrapolate branching macro-outcomes."""

        base_text = world_text[:10000]
        objective_text = objective.strip() or "General horizon scan"

        stage_1 = """
You are a systems analyst. Extract factions and pressures.
Return JSON with keys: extracted_factions (array), pressure_points (array), core_tension (string).
"""
        stage_2 = """
You are a political forecaster. Given factions and pressure points, derive 3 tensions.
Return JSON with keys: tension_map (array of objects with title, drivers, risk_level).
"""
        stage_3 = """
You are the Macro-Simulation Time-Skip Engine.
Provide JSON with:
extracted_factions, core_tension, timeline_A, timeline_B, timeline_C.
Each timeline must include title, description, societal_outcome, probability.
"""

        try:
            factions = await call_llm_with_settings(
                prompt=f"{stage_1}\nSOURCE:\n{base_text}",
                model="llama-3.3-70b-versatile",
                temperature=0.4,
            )

            tensions = await call_llm_with_settings(
                prompt=f"{stage_2}\nFACTIONS:\n{json.dumps(factions)}",
                model="llama-3.3-70b-versatile",
                temperature=0.5,
            )

            outcomes = await call_llm_with_settings(
                prompt=f"{stage_3}\nOBJECTIVE:\n{objective_text}\nFACTIONS:\n{json.dumps(factions)}\nTENSIONS:\n{json.dumps(tensions)}\nSOURCE:\n{base_text}",
                model="llama-3.3-70b-versatile",
                temperature=0.6,
            )

            return outcomes
        except Exception as e:
            return {"error": str(e)}

