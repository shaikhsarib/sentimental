import asyncio
import random
from typing import List, Dict, Optional
from collections import Counter
from engines.swarm_shard_manager import SwarmShardManager
from engines.multi_model import run_synthesized_persona, run_synthesis_judge
from engines.consensus_engine import ConsensusEngine
from engines.v6_graph_builder import V6GraphBuilder
from engines.cascade_simulator import CascadeSimulator

class MillionDebateEngine:
    """
    SentiFlow V6 Million-Agent Debate Orchestrator.
    Implements Three-Layer Hierarchical Consensus (Blueprint Page 17).
    """
    
    def __init__(self, shard_manager: SwarmShardManager):
        self.shard_manager = shard_manager
        self.consensus_engine = ConsensusEngine()
        self.graph_builder = V6GraphBuilder()
        self.cascade_simulator = CascadeSimulator()

    async def run_million_debate(self, agents: List[Dict], content: str, content_type: str, intent: str) -> Dict:
        """
        Full V6 Debate Pipeline.
        """
        # 1. LAYER 1: MASS CONSENSUS (All Agents - Independent Analysis)
        print(f"[V6] Starting Mass Consensus for {len(agents)} agents...")
        shards = self.shard_manager.shard_agents(agents)
        
        async def process_shard(shard_agents):
            tasks = [
                run_synthesized_persona(agent, content, content_type, intent)
                for agent in shard_agents
            ]
            return await asyncio.gather(*tasks, return_exceptions=True)

        mass_results = await self.shard_manager.process_shards(shards, process_shard)
        mass_results = [r for r in mass_results if isinstance(r, dict) and r.get("triggered")]
        
        aggregation = self.shard_manager.aggregate_results(mass_results)
        
        # 2. LAYER 2: REPRESENTATIVE DEBATE (Sampled 100-500 Agents)
        print(f"[V6] Starting Representative Debate (Layer 2)...")
        # Stratified sampling: 20 executives, 50 specialists, 30 external
        rep_agents = self._sample_representative_agents(agents, count=100)
        
        rep_results = []
        for agent in rep_agents:
            res = await run_synthesized_persona(agent, content, content_type, intent)
            if res.get("triggered"):
                rep_results.append(res)

        # 3. LAYER 3: DETAILED ARBITRATION (Judge Verdict)
        print(f"[V6] Starting Institutional Arbitration (Layer 3)...")
        debate_transcript = "\n".join([
            f"AGENT {r.get('persona_name')}: {r.get('reaction')} (RISK: {r.get('virality_risk')})" 
            for r in rep_results[:50] # Top 50 for the judge
        ])
        
        # In a real V6 implementation, we'd pull historical context from CrisisDatabase
        judge_verdict = await run_synthesis_judge(content, debate_transcript, "V6 Swarm Context")

        # 4. HIERARCHICAL CONSENSUS CALCULATION
        final_consensus = self._calculate_hierarchical_consensus(
            aggregation, 
            rep_results, 
            judge_verdict
        )

        # 5. GRAPH & CASCADE SIMULATION (NEW Phase 4)
        print(f"[V6] Building Influence Graph and Running Cascade...")
        influence_graph = self.graph_builder.build_influence_graph(agents)
        cascade_results = self.cascade_simulator.run_simulation(influence_graph)

        return {
            "aggregation": aggregation,
            "representative_debate": rep_results,
            "judge_verdict": judge_verdict,
            "consensus": final_consensus,
            "graph": influence_graph,
            "cascade": cascade_results,
            "total_processed": len(mass_results)
        }

    def _sample_representative_agents(self, agents: List[Dict], count: int) -> List[Dict]:
        """Sample agents across tiers and domains (Stratified)."""
        tier1 = [a for a in agents if a.get("tier") == 1]
        tier2 = [a for a in agents if a.get("tier") == 2]
        tier3 = [a for a in agents if a.get("tier") == 3]
        
        sample = []
        sample.extend(random.sample(tier1, min(len(tier1), int(count * 0.2))))
        sample.extend(random.sample(tier2, min(len(tier2), int(count * 0.5))))
        sample.extend(random.sample(tier3, min(len(tier3), int(count * 0.3))))
        
        return sample

    def _calculate_hierarchical_consensus(self, aggregation: Dict, rep_results: List[Dict], judge: Dict) -> Dict:
        """
        Weighted Hierarchical Consensus (Blueprint Page 17-18).
        Weights: Mass 0.2, Representative 0.3, Detailed 0.5
        """
        weights = {"mass": 0.2, "rep": 0.3, "judge": 0.5}
        
        # Mass Score (from majority position)
        mass_score = aggregation.get("consensus_score", 0.5)
        
        # Representative Score (from majority position)
        rep_positions = Counter(r.get("position", "NEUTRAL") for r in rep_results)
        rep_majority_count = rep_positions.most_common(1)[0][1] if rep_results else 0
        rep_score = rep_majority_count / len(rep_results) if rep_results else 0.5
        
        # Judge Score (Confidence)
        judge_score = judge.get("confidence_in_verdict", 0.7)
        
        # Final Weighted Score
        final_confidence = (
            mass_score * weights["mass"] +
            rep_score * weights["rep"] +
            judge_score * weights["judge"]
        )
        
        # Majority Position (Weighted Vote)
        # For simplicity, we use the Judge's verdict as the anchor for the position
        return {
            "final_confidence": round(final_confidence, 3),
            "is_polarized": aggregation.get("consensus_score", 0) < 0.6,
            "layer_scores": {
                "mass": mass_score,
                "representative": rep_score,
                "judge": judge_score
            }
        }
