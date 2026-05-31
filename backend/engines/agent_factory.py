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
    Uses 'Archetype DNA' to ensure scalability via statistical abstraction.
    """
    
    def __init__(self, domain: str = "GENERAL"):
        self.domain = domain
        self.skill_engine = SkillEngine()
        self.archetypes = {} # archetype_id -> agent_dna
        from engines.agent_infrastructure import AgentInfrastructure
        self.infra = AgentInfrastructure()

    def generate_swarm(self, entities: List[ExtractedEntity], target_count: int = 1000, max_archetypes: int = 100) -> List[Dict]:
        """
        Million-Agent Generation Pipeline (Blueprint Page 5).
        Uses Statistical Abstraction (Phase 1 Fix).
        """
        # 1. Generate core Archetypes
        archetype_count = min(max_archetypes, target_count)
        self.archetypes = self._generate_archetypes(entities, archetype_count)
        
        # 2. Instantiate full swarm as lightweight clones
        swarm = []
        archetype_ids = list(self.archetypes.keys())
        
        for i in range(target_count):
            arch_id = archetype_ids[i % len(archetype_ids)]
            base_dna = self.archetypes[arch_id]
            
            # Clone with unique ID but shared archetype reference
            agent = base_dna.copy()
            agent["agent_id"] = str(uuid.uuid4())
            agent["archetype_id"] = arch_id
            # Add slight 'noise' to synthetic agents for statistical variance
            if agent["is_synthetic"]:
                agent["variance_factor"] = random.uniform(0.9, 1.1)
            
            swarm.append(agent)
            
            # Provision dynamic workspace directories (limit to first 250 to keep simulation fast)
            if i < 250:
                self.infra.provision_agent_workspace(agent["agent_id"], agent)
                
        return swarm

    def _generate_archetypes(self, entities: List[ExtractedEntity], count: int) -> Dict[str, Dict]:
        """Create a diverse pool of Archetype DNA."""
        archetypes = {}
        
        # 1. Entity-based archetypes
        for entity in entities:
            for emotion in ["aggressive", "cautious", "optimistic", "pessimistic", "neutral"]:
                arch_id = f"arch_ent_{entity.id}_{emotion}"
                archetypes[arch_id] = self._create_agent_dna(
                    name=f"{entity.name} ({emotion})",
                    role=entity.type,
                    tier=1 if entity.type in ["ROLE", "ORGANIZATION"] else 2,
                    emotion=emotion,
                    is_synthetic=False,
                    source_id=entity.id
                )
        
        # 2. Synthetic archetypes to fill the pool
        while len(archetypes) < count:
            role_base = random.choice(["User", "Expert", "Observer", "Critic", "Stakeholder"])
            template = random.choice(ROLE_TEMPLATES)
            role_name = template.format(role=role_base, domain=self.domain)
            emotion = random.choice(["aggressive", "cautious", "optimistic", "pessimistic", "neutral"])
            arch_id = f"arch_syn_{uuid.uuid4().hex[:6]}"
            
            archetypes[arch_id] = self._create_agent_dna(
                name=f"Archetype_{arch_id[-4:]}",
                role=role_name,
                tier=random.randint(2, 3),
                emotion=emotion,
                is_synthetic=True
            )
            
        return archetypes

    def _create_agent_dna(self, name: str, role: str, tier: int, emotion: str, is_synthetic: bool, source_id: str = None) -> Dict:
        """Create a core DNA profile."""
        skills = self.skill_engine.generate_skills(self.domain)
        training = self.skill_engine.generate_training(self.domain, emotion)
        
        return {
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
            "variance_factor": 1.0
        }
