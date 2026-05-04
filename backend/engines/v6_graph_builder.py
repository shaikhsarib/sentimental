import math
import random
from typing import List, Dict, Tuple

class V6GraphBuilder:
    """
    SentiFlow V6 Influence Graph Builder.
    Constructs complex networks of agents based on tier, domain, and skills.
    Blueprint Page 30.
    """
    
    def __init__(self):
        # Constants from Page 30
        self.MAX_EDGES_PER_NODE = 10
        self.DOMAIN_MATCH_BONUS = 1.5
        self.TIER_INFLUENCE_WEIGHTS = {
            1: 2.0,  # Executive/Elite
            2: 1.0,  # Specialist
            3: 0.5   # Population
        }

    def build_influence_graph(self, agents: List[Dict]) -> Dict:
        """
        Builds a weighted graph of agent relationships.
        Edges represent the probability and strength of sentiment contagion.
        """
        nodes = []
        edges = []
        
        # 1. Prepare Nodes
        for agent in agents:
            nodes.append({
                "id": agent["agent_id"],
                "name": agent["name"],
                "tier": agent["tier"],
                "domain": agent["domain"],
                "emotion": agent.get("emotion_profile", "neutral"),
                "influence": self.TIER_INFLUENCE_WEIGHTS.get(agent["tier"], 1.0)
            })

        # 2. Build Edges (Contagion Paths)
        # For a million agents, we use a k-nearest-neighbor or domain-cluster approach
        # For this implementation, we simulate the "Small World" network property
        for i, agent_a in enumerate(agents):
            potential_neighbors = []
            
            # Sample potential neighbors (performance optimization for large swarms)
            sample_size = min(len(agents), 100)
            candidates = random.sample(range(len(agents)), sample_size)
            
            for j in candidates:
                if i == j: continue
                agent_b = agents[j]
                
                # Calculate Influence Weight (Blueprint Page 31)
                weight = self._calculate_weight(agent_a, agent_b)
                
                if weight > 0.3: # Threshold for relationship formation
                    potential_neighbors.append((agent_b["agent_id"], weight))
            
            # Keep only the strongest connections
            potential_neighbors.sort(key=lambda x: x[1], reverse=True)
            for neighbor_id, w in potential_neighbors[:self.MAX_EDGES_PER_NODE]:
                edges.append({
                    "source": agent_a["agent_id"],
                    "target": neighbor_id,
                    "weight": round(w, 3)
                })

        return {
            "nodes": nodes,
            "edges": edges,
            "metadata": {
                "node_count": len(nodes),
                "edge_count": len(edges),
                "density": len(edges) / (len(nodes) * (len(nodes)-1)) if len(nodes) > 1 else 0
            }
        }

    def _calculate_weight(self, a: Dict, b: Dict) -> float:
        """Weight = (Tier Factor) * (Domain Match) * (Skill Similarity)"""
        # 1. Domain Match
        domain_factor = self.DOMAIN_MATCH_BONUS if a["domain"] == b["domain"] else 0.8
        
        # 2. Tier Delta (Low tiers follow high tiers)
        # If B is higher tier than A, weight is higher
        tier_a = a.get("tier", 3)
        tier_b = b.get("tier", 3)
        tier_factor = 1.0
        if tier_b < tier_a: # B is more elite than A
            tier_factor = 1.5
        elif tier_b > tier_a: # B is less elite than A
            tier_factor = 0.5
            
        # 3. Skill Similarity (Jaccard-ish)
        skills_a = {s["skill_name"] for s in a.get("skills", [])}
        skills_b = {s["skill_name"] for s in b.get("skills", [])}
        
        if not skills_a or not skills_b:
            skill_factor = 0.5
        else:
            intersection = len(skills_a.intersection(skills_b))
            union = len(skills_a.union(skills_b))
            skill_factor = (intersection / union) + 0.5
            
        # Combine
        weight = (tier_factor * domain_factor * skill_factor) / 3.0
        return min(weight, 1.0)
