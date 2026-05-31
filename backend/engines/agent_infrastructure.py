import os
import json
from typing import Dict, List, Optional

class AgentInfrastructure:
    """
    SentiFlow V6 Agent Infrastructure Manager.
    Provisions and manages dynamic local directories for each synthetic agent.
    Ensures isolated data, brain, skills, training, and self-reflection modules.
    """
    def __init__(self, base_storage_path: str = "storage/agents"):
        self.base_storage_path = os.path.abspath(base_storage_path)
        os.makedirs(self.base_storage_path, exist_ok=True)

    def get_agent_workspace_path(self, agent_id: str) -> str:
        """Get the absolute path to an agent's isolated workspace."""
        return os.path.join(self.base_storage_path, agent_id)

    def provision_agent_workspace(self, agent_id: str, agent_dna: Dict) -> Dict[str, str]:
        """
        Provision the 5 required directories for an agent (Blueprint Part 2).
        Returns a dictionary of absolute paths for each created directory.
        """
        agent_dir = self.get_agent_workspace_path(agent_id)
        subdirs = {
            "data": os.path.join(agent_dir, "data"),
            "brain": os.path.join(agent_dir, "brain"),
            "skills": os.path.join(agent_dir, "skills"),
            "training": os.path.join(agent_dir, "training"),
            "self_trained": os.path.join(agent_dir, "self_trained")
        }

        # Create directories on disk
        for name, path in subdirs.items():
            os.makedirs(path, exist_ok=True)

        # Write data/identity.json
        identity_path = os.path.join(subdirs["data"], "identity.json")
        identity_data = {
            "agent_id": agent_id,
            "name": agent_dna.get("name", f"Agent_{agent_id[:6]}"),
            "role": agent_dna.get("role", "Participant"),
            "domain": agent_dna.get("domain", "GENERAL"),
            "tier": agent_dna.get("tier", "population"),
            "type": agent_dna.get("type", "SYNTHETIC"),
            "emotion_profile": agent_dna.get("emotion_profile", "neutral"),
            "variance_factor": agent_dna.get("variance_factor", 1.0),
            "background": agent_dna.get("background", ""),
            "personality": agent_dna.get("personality", ""),
            "behavioral_logic": agent_dna.get("behavioral_logic", ""),
            "system_prefix": agent_dna.get("system_prefix", "")
        }
        with open(identity_path, "w", encoding="utf-8") as f:
            json.dump(identity_data, f, indent=4)

        # Write default skills and training
        self.save_agent_skills(agent_id, agent_dna.get("skills", []))
        self.save_agent_training_history(agent_id, agent_dna.get("training", []))

        # Create a default blank reflection log
        self.save_agent_reflection(agent_id, {
            "reflection_count": 0,
            "past_verdicts": [],
            "calibration_history": []
        })

        return subdirs

    def get_agent_identity(self, agent_id: str) -> Optional[Dict]:
        """Load agent identity from identity.json."""
        path = os.path.join(self.get_agent_workspace_path(agent_id), "data", "identity.json")
        if not os.path.exists(path):
            return None
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)

    def save_agent_skills(self, agent_id: str, skills: List[Dict]) -> None:
        """Save registered agent skills into /skills/skills.json."""
        path = os.path.join(self.get_agent_workspace_path(agent_id), "skills", "skills.json")
        with open(path, "w", encoding="utf-8") as f:
            json.dump(skills, f, indent=4)

    def load_agent_skills(self, agent_id: str) -> List[Dict]:
        """Load agent skills from /skills/skills.json."""
        path = os.path.join(self.get_agent_workspace_path(agent_id), "skills", "skills.json")
        if not os.path.exists(path):
            return []
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)

    def save_agent_training_history(self, agent_id: str, history: List[Dict]) -> None:
        """Save continuous learning logs into /training/history.json."""
        path = os.path.join(self.get_agent_workspace_path(agent_id), "training", "history.json")
        with open(path, "w", encoding="utf-8") as f:
            json.dump(history, f, indent=4)

    def load_agent_training_history(self, agent_id: str) -> List[Dict]:
        """Load agent continuous learning logs."""
        path = os.path.join(self.get_agent_workspace_path(agent_id), "training", "history.json")
        if not os.path.exists(path):
            return []
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)

    def save_agent_brain(self, agent_id: str, memory_log: Dict) -> None:
        """Save dynamic semantic memory context to /brain/memory_log.json."""
        path = os.path.join(self.get_agent_workspace_path(agent_id), "brain", "memory_log.json")
        with open(path, "w", encoding="utf-8") as f:
            json.dump(memory_log, f, indent=4)

    def load_agent_brain(self, agent_id: str) -> Dict:
        """Load agent dynamic semantic memory context."""
        path = os.path.join(self.get_agent_workspace_path(agent_id), "brain", "memory_log.json")
        if not os.path.exists(path):
            return {"memories": [], "short_term_context": ""}
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)

    def save_agent_reflection(self, agent_id: str, reflection: Dict) -> None:
        """Save adversarial calibration results to /self_trained/reflection_history.json."""
        path = os.path.join(self.get_agent_workspace_path(agent_id), "self_trained", "reflection_history.json")
        with open(path, "w", encoding="utf-8") as f:
            json.dump(reflection, f, indent=4)

    def load_agent_reflection(self, agent_id: str) -> Dict:
        """Load agent adversarial calibration history."""
        path = os.path.join(self.get_agent_workspace_path(agent_id), "self_trained", "reflection_history.json")
        if not os.path.exists(path):
            return {"reflection_count": 0, "past_verdicts": [], "calibration_history": []}
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
