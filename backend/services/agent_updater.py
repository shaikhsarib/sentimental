import os
import json
import time
from typing import Dict, List
from engines.agent_infrastructure import AgentInfrastructure
from engines.multi_model import call_llm_with_settings

class AgentUpdater:
    """
    SentiFlow V6 Continuous Learning and Training Daemon (Blueprint Phase 3).
    Monitors each agent's `/training` subdirectory and integrates incoming information
    into their cognitive `/brain` memory.
    """
    def __init__(self, base_storage_path: str = "storage/agents"):
        self.infra = AgentInfrastructure(base_storage_path)

    async def ingest_new_training_files(self, agent_id: str) -> List[Dict]:
        """
        Scan the agent's `/training` subdirectory for raw text files (.txt, .md, .json)
        and integrate them into the agent's brain memory.
        Moves/renames processed files to prevent duplicate training.
        """
        workspace = self.infra.get_agent_workspace_path(agent_id)
        training_dir = os.path.join(workspace, "training")
        
        if not os.path.exists(training_dir):
            return []

        identity = self.infra.get_agent_identity(agent_id)
        if not identity:
            return []

        processed_learnings = []
        for filename in os.listdir(training_dir):
            # Skip logs and processed files
            if filename == "history.json" or filename.startswith(".") or filename.endswith(".processed"):
                continue

            file_path = os.path.join(training_dir, filename)
            if not os.path.isfile(file_path):
                continue

            # Read content
            try:
                with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                    raw_content = f.read()
            except Exception as e:
                print(f"[UPDATER ERROR] Failed to read {filename} for agent {agent_id}: {e}")
                continue

            if not raw_content.strip():
                continue

            # Process the file via LLM
            learning = await self._process_learning_content(identity, filename, raw_content)
            processed_learnings.append(learning)

            # Update Agent Brain
            brain = self.infra.load_agent_brain(agent_id)
            brain["memories"].append({
                "timestamp": int(time.time()),
                "source_file": filename,
                "learning_summary": learning.get("summary", ""),
                "key_takeaways": learning.get("key_takeaways", []),
                "emotional_impact": learning.get("emotional_impact", "neutral"),
                "virality_risk_delta": learning.get("virality_risk_delta", 0)
            })
            # Keep short_term_context updated
            brain["short_term_context"] = f"Learned from {filename}: {learning.get('summary', '')}. {brain.get('short_term_context', '')}"[:4000]
            self.infra.save_agent_brain(agent_id, brain)

            # Update Ingested History
            history = self.infra.load_agent_training_history(agent_id)
            history.append({
                "timestamp": int(time.time()),
                "event": f"Ingested {filename}",
                "summary": learning.get("summary", ""),
                "status": "COMPLETED"
            })
            self.infra.save_agent_training_history(agent_id, history)

            # Mark file as processed
            try:
                processed_path = os.path.join(training_dir, f"{filename}.processed")
                if os.path.exists(processed_path):
                    os.remove(processed_path)
                os.rename(file_path, processed_path)
            except Exception as e:
                print(f"[UPDATER ERROR] Failed to rename processed file {filename}: {e}")

        return processed_learnings

    async def _process_learning_content(self, identity: Dict, source_name: str, content: str) -> Dict:
        """Process incoming raw information relative to the agent's specific role & background."""
        model = "llama-3.1-8b-instant"  # Keep it ultra fast and cost-effective
        temp = 0.5

        prompt = f"""You are simulating the cognitive processing of an agent learning new information.
Agent Profile:
- Name: {identity.get('name')}
- Role: {identity.get('role')}
- Domain: {identity.get('domain')}
- Background: {identity.get('background')}
- Personality: {identity.get('personality')}
- Core Logic: {identity.get('behavioral_logic')}

Incoming Document ({source_name}):
\"\"\"{content[:4000]}\"\"\"

Task:
Read this document from the perspective of your role and background. Determine how it affects your current understanding of the environment.

Respond strictly in valid JSON:
{{
    "summary": "1-2 sentence summary of what you learned",
    "key_takeaways": ["takeaway 1 relative to your role", "takeaway 2 relative to your role"],
    "emotional_impact": "how this makes you feel (e.g. anger, fear, outrage, shock, amusement, neutral)",
    "virality_risk_delta": 0 // integer -2 to +2 showing how this changes your risk tolerance or alert level
}}
"""
        try:
            return await call_llm_with_settings(prompt, model, temp)
        except Exception as e:
            print(f"[LLM Ingestion Error] {e}")
            return {
                "summary": f"Ingested raw text from {source_name}.",
                "key_takeaways": ["Raw content processed."],
                "emotional_impact": "neutral",
                "virality_risk_delta": 0
            }
