import random
from typing import List, Dict, Optional
from dataclasses import dataclass

@dataclass
class AgentSkill:
    name: str
    level: float # 0.0 - 1.0
    domain: str
    activation_triggers: List[str]

class SkillEngine:
    """
    SentiFlow V6 Skill & Training Engine.
    Handles domain-specific skill libraries and training generation.
    """
    
    SKILL_LIBRARY = {
        "TECHNOLOGY": [
            {"name": "System Architecture", "triggers": ["scalability", "microservices", "cloud", "architecture"]},
            {"name": "Code Review", "triggers": ["bug", "vulnerability", "security flaw", "code"]},
            {"name": "AI/ML Engineering", "triggers": ["model", "algorithm", "neural", "network", "ai"]},
            {"name": "DevOps", "triggers": ["ci/cd", "deployment", "infrastructure", "docker"]},
            {"name": "Security Engineering", "triggers": ["breach", "threat", "penetration", "security"]}
        ],
        "FINANCE": [
            {"name": "Financial Modeling", "triggers": ["dcf", "valuation", "forecast", "model"]},
            {"name": "Risk Management", "triggers": ["var", "stress test", "credit", "risk"]},
            {"name": "Trading Strategy", "triggers": ["algorithmic", "arbitrage", "market", "trading"]},
            {"name": "Regulatory Compliance", "triggers": ["sec", "finra", "gdpr", "compliance"]}
        ]
    }

    def generate_skills(self, domain: str, count: int = 3) -> List[Dict]:
        """Assign random skills from the domain library."""
        library = self.SKILL_LIBRARY.get(domain, self.SKILL_LIBRARY["TECHNOLOGY"])
        selected = random.sample(library, min(count, len(library)))
        return [{
            "skill_name": s["name"],
            "skill_level": round(random.uniform(0.6, 1.0), 2),
            "domain": domain,
            "activation_triggers": s["triggers"]
        } for s in selected]

    def generate_training(self, domain: str, emotion_profile: str) -> List[Dict]:
        """
        Generate synthetic training experiences (Blueprint Page 6-7).
        """
        scenarios = {
            "TECHNOLOGY": [
                "Product launch with unexpected technical debt",
                "Security breach discovered by external researcher",
                "Cloud outage affecting 50% of users"
            ],
            "FINANCE": [
                "Quarterly earnings miss by 30% with guidance cut",
                "Whistleblower alleges revenue recognition issues",
                "Major client bankruptcy wiping 20% of ARR"
            ]
        }
        
        emotion_mods = {
            "optimistic": {"risk_offset": -2, "outcome": "positive"},
            "pessimistic": {"risk_offset": 2, "outcome": "negative"},
            "aggressive": {"risk_offset": 1, "outcome": "combative"},
            "cautious": {"risk_offset": 1, "outcome": "protective"},
            "neutral": {"risk_offset": 0, "outcome": "balanced"}
        }

        domain_scenarios = scenarios.get(domain, ["General crisis scenario"])
        mod = emotion_mods.get(emotion_profile, emotion_mods["neutral"])
        
        training = []
        for scenario in domain_scenarios[:3]:
            risk = max(1, min(10, 5 + mod["risk_offset"] + random.randint(-1, 1)))
            training.append({
                "scenario": scenario,
                "emotion": emotion_profile,
                "virality_risk": risk,
                "outcome": mod["outcome"],
                "lesson": f"When facing {domain} {scenario.lower()}, prioritize {emotion_profile} response."
            })
        return training
