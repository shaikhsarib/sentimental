import os
import json
import time
from typing import Dict, List, Optional
from engines.agent_infrastructure import AgentInfrastructure
from engines.multi_model import call_llm_with_settings

class SelfTrainingEngine:
    """
    SentiFlow V6 Adversarial Self-Reflection & Calibration Engine (Blueprint Phase 4).
    Forces agents to analyze their past mistakes and optimize their own debate prompts
    to prevent sugarcoating and ensure direct, genuine reasoning.
    """
    def __init__(self, base_storage_path: str = "storage/agents"):
        self.infra = AgentInfrastructure(base_storage_path)

    async def execute_agent_self_reflection(self, agent_id: str, debate_transcript: str, final_outcome: str) -> Dict:
        """
        Force a single agent to self-reflect on their past debate performance.
        Loads past identity, reviews their reaction in the transcript, compares it to the final outcome,
        and generates self-calibrated prompts.
        """
        identity = self.infra.get_agent_identity(agent_id)
        if not identity:
            return {"status": "error", "message": "Agent identity not found"}

        reflection_data = self.infra.load_agent_reflection(agent_id)
        
        model = "llama-3.1-8b-instant"  # Quick reflection engine
        temp = 0.3

        prompt = f"""You are the internal cognitive metacognitor for the agent: {identity.get('name')}.
Your sole job is to review this agent's recent debate performance, identify where they got biased, sugarcoated their response, or made a mistake, and calibrate their system prompt.

Agent Profile:
- Role: {identity.get('role')}
- Domain: {identity.get('domain')}
- Background: {identity.get('background')}
- Personality: {identity.get('personality')}
- Current System Prefix: {identity.get('system_prefix')}

The Debate Transcript:
\"\"\"{debate_transcript[:3000]}\"\"\"

Adjudicated Swarm Outcome (Ground Truth):
\"{final_outcome}\"

Task:
1. Find where this agent reacted in the debate.
2. Determine if their assessment was over-sensitive, under-sensitive, sugarcoated, or accurate compared to the adjudicated outcome.
3. Write a revised, calibrated "system_prefix" that injects strict behavioral instructions to correct this bias (e.g. "Do not sugarcoat X", "Ensure you pay attention to Y").

Respond strictly in valid JSON:
{{
    "status": "calibrated",
    "assessment_of_mistake": "1-2 sentences on what mistake or sugarcoating occurred, if any",
    "was_sugarcoated": true, // or false
    "calibrated_system_prefix": "your complete updated system_prefix containing all original info PLUS specific anti-bias corrections"
}}
"""
        try:
            calibration = await call_llm_with_settings(prompt, model, temp)
            if calibration.get("status") == "calibrated" and calibration.get("calibrated_system_prefix"):
                # Save the new system prefix to identity
                new_prefix = calibration["calibrated_system_prefix"]
                identity["system_prefix"] = new_prefix
                
                # Update identity.json
                identity_path = os.path.join(self.infra.get_agent_workspace_path(agent_id), "data", "identity.json")
                with open(identity_path, "w", encoding="utf-8") as f:
                    json.dump(identity, f, indent=4)

                # Log reflection details
                reflection_data["reflection_count"] += 1
                reflection_data["past_verdicts"].append({
                    "timestamp": int(time.time()),
                    "final_outcome": final_outcome,
                    "was_sugarcoated": calibration.get("was_sugarcoated", False),
                    "assessment": calibration.get("assessment_of_mistake", "")
                })
                self.infra.save_agent_reflection(agent_id, reflection_data)

                return {
                    "status": "success",
                    "agent_id": agent_id,
                    "was_sugarcoated": calibration.get("was_sugarcoated", False),
                    "assessment": calibration.get("assessment_of_mistake", "")
                }
            return {"status": "failed", "message": "Failed to parse calibration payload"}
        except Exception as e:
            print(f"[SELF-TRAIN ERROR] Reflection failed for {agent_id}: {e}")
            return {"status": "error", "message": str(e)}
