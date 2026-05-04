import random
from typing import List, Dict, Tuple
from collections import Counter

class CascadeSimulator:
    """
    SentiFlow V6 Sentiment Cascade Simulator.
    Implements Stochastic SEIR on the Influence Graph with Emotion Physics.
    Blueprint Page 32.
    """
    
    def __init__(self):
        # Base SEIR Constants (Page 32)
        self.BETA = 0.3   # Base infection rate
        self.SIGMA = 0.2  # Incubation rate (E -> I)
        self.GAMMA = 0.1  # Recovery rate (I -> R)
        
        # Emotion Physics Modulation (Page 32)
        self.EMOTION_MODIFIERS = {
            "anger": {"beta": 1.8, "gamma": 0.6},    # Spreads fast, lingers
            "outrage": {"beta": 2.2, "gamma": 0.4},  # Extremely contagious
            "fear": {"beta": 1.4, "gamma": 1.1},     # Spreads fast, fades fast
            "sadness": {"beta": 0.8, "gamma": 1.5},  # Spreads slow, fades fast
            "neutral": {"beta": 1.0, "gamma": 1.0}
        }

    def run_simulation(self, graph: Dict, initial_infected_count: int = 5, steps: int = 20) -> Dict:
        """
        Runs a stochastic sentiment cascade over the graph topology.
        """
        nodes = graph["nodes"]
        edges = graph["edges"]
        
        # Adjacency list for fast lookup
        adj = {n["id"]: [] for n in nodes}
        for e in edges:
            adj[e["source"]].append((e["target"], e["weight"]))

        # Initialize States
        # 0: S, 1: E, 2: I, 3: R
        states = {n["id"]: 0 for n in nodes}
        node_data = {n["id"]: n for n in nodes}
        
        # Seed initial infection
        seed_ids = random.sample([n["id"] for n in nodes], min(len(nodes), initial_infected_count))
        for sid in seed_ids:
            states[sid] = 2 # Infected
            
        history = []
        
        for t in range(steps):
            new_states = states.copy()
            counts = Counter(states.values())
            
            history.append({
                "step": t,
                "S": counts[0],
                "E": counts[1],
                "I": counts[2],
                "R": counts[3]
            })
            
            for node_id, state in states.items():
                emotion = node_data[node_id].get("emotion", "neutral").lower()
                mod = self.EMOTION_MODIFIERS.get(emotion, self.EMOTION_MODIFIERS["neutral"])
                
                # S -> E (Exposed by neighbors)
                if state == 0:
                    # Calculate infection probability from neighbors
                    total_pressure = 0
                    for neighbor_id, weight in adj[node_id]:
                        if states[neighbor_id] == 2: # Neighbor is Infected
                            total_pressure += weight
                    
                    if total_pressure > 0:
                        infection_prob = 1 - (1 - (self.BETA * mod["beta"]))**total_pressure
                        if random.random() < infection_prob:
                            new_states[node_id] = 1 # Exposed
                
                # E -> I (Processing complete)
                elif state == 1:
                    if random.random() < self.SIGMA:
                        new_states[node_id] = 2 # Infected
                
                # I -> R (Fatigue/Recovery)
                elif state == 2:
                    if random.random() < (self.GAMMA * mod["gamma"]):
                        new_states[node_id] = 3 # Recovered
            
            states = new_states
            
        return {
            "history": history,
            "final_states": states,
            "metadata": {
                "r_naught": self._calculate_r0(history),
                "peak_infection": max(h["I"] for h in history),
                "total_affected": history[-1]["I"] + history[-1]["R"]
            }
        }

    def _calculate_r0(self, history: List[Dict]) -> float:
        """Crude estimation of R0 based on growth rate."""
        if len(history) < 2: return 0.0
        # Average growth in first 5 steps
        growth_rates = []
        for i in range(1, min(6, len(history))):
            prev = history[i-1]["I"] + history[i-1]["E"]
            curr = history[i]["I"] + history[i]["E"]
            if prev > 0:
                growth_rates.append(curr / prev)
        
        return round(sum(growth_rates)/len(growth_rates), 2) if growth_rates else 1.0
