import random
import uuid
from typing import List, Dict, Optional
from dataclasses import dataclass, asdict
from engines.entity_extractor import ExtractedEntity
from engines.skill_engine import SkillEngine

ROLE_TEMPLATES = [
    "Junior {role}", "Senior {role}", "Lead {role}", "Principal {role}",
    "{role} Specialist", "{role} Consultant", "{role} Advisor",
    "Freelance {role}", "Contract {role}", "Remote {role}",
    "{domain} {role}", "{domain} Senior {role}", "{domain} Lead {role}",
    "Global {role}", "Regional {role}", "Local {role}",
    "Chief {role}", "VP of {role}", "Head of {role}",
    "Former {role}", "Aspiring {role}", "Retired {role}",
    "{role} Advocate", "{role} Critic", "{role} Analyst",
    "Independent {role}", "Affiliated {role}", "External {role}",
    "{role} (AI-Enhanced)", "{role} (Human-in-Loop)", "{role} (Autonomous)",
    "Ethical {role}", "Rogue {role}", "Whistleblower {role}",
    "Shadow {role}", "Ghost {role}", "Undercover {role}"
]

class AgentFactory:
    """
    SentiFlow V6 Agent Factory.
    Generates 100K-10M agents from real entities and synthetic templates.
    """
    
    def __init__(self, domain: str = "GENERAL"):
        self.domain = domain
        self.skill_engine = SkillEngine()

    def generate_swarm(self, entities: List[ExtractedEntity], target_count: int = 1000) -> List[Dict]:
        """
        Million-Agent Generation Pipeline (Blueprint Page 5).
        """
        swarm = []
        
        # 1. Base agents from real entities (x5 emotion variants)
        for entity in entities:
            for emotion in ["aggressive", "cautious", "optimistic", "pessimistic", "neutral"]:
                swarm.append(self._create_agent(
                    name=f"{entity.name} ({emotion})",
                    role=entity.type,
                    tier=1 if entity.type in ["ROLE", "ORGANIZATION"] else 2,
                    emotion=emotion,
                    is_synthetic=False,
                    source_id=entity.id
                ))
        
        # 2. Fill with synthetic agents if target not met
        remaining = target_count - len(swarm)
        if remaining > 0:
            for _ in range(remaining):
                role_base = random.choice(["User", "Expert", "Observer", "Critic", "Stakeholder"])
                template = random.choice(ROLE_TEMPLATES)
                role_name = template.format(role=role_base, domain=self.domain)
                
                swarm.append(self._create_agent(
                    name=f"Agent_{uuid.uuid4().hex[:6]}",
                    role=role_name,
                    tier=random.randint(2, 3),
                    emotion=random.choice(["aggressive", "cautious", "optimistic", "pessimistic", "neutral"]),
                    is_synthetic=True
                ))
                
        return swarm

    def _create_agent(self, name: str, role: str, tier: int, emotion: str, is_synthetic: bool, source_id: str = None) -> Dict:
        """Create a single agent profile with skills and training."""
        agent_id = str(uuid.uuid4())
        
        # Phase 2: Add Skills & Training
        skills = self.skill_engine.generate_skills(self.domain)
        training = self.skill_engine.generate_training(self.domain, emotion)
        
        return {
            "agent_id": agent_id,
            "name": name,
            "role": role,
            "domain": self.domain,
            "tier": tier,
            "type": "SYNTHETIC" if is_synthetic else "PERSON",
            "emotion_profile": emotion,
            "is_synthetic": 1 if is_synthetic else 0,
            "source_entity_id": source_id,
            "skills": skills,
            "training": training,
            "accuracy_score": 0.0,
            "created_at": None 
        }
