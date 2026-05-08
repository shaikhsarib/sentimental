import asyncio
import random
from typing import List, Dict, Optional
from collections import Counter
from engines.swarm_shard_manager import SwarmShardManager
from engines.multi_model import run_synthesized_persona, run_synthesis_judge
from engines.consensus_engine import ConsensusEngine
from engines.v6_graph_builder import V6GraphBuilder
from engines.cascade_simulator import CascadeSimulator
from engines.explainability_engine import ExplainabilityEngine
from engines.memory_engine import MemoryEngine
from services.audit_logger import AuditLogger
from services.graph_store import GraphStore

class MillionDebateEngine:
    """
    SentiFlow V6 Million-Agent Debate Orchestrator.
    Implements Three-Layer Hierarchical Consensus (Blueprint Page 17).
    Integrated with MemoryEngine for Zep Cloud-like long-term continuity.
    """
    
    def __init__(self, shard_manager: SwarmShardManager, graph_store: GraphStore):
        self.shard_manager = shard_manager
        self.graph_store = graph_store
        self.consensus_engine = ConsensusEngine()
        self.graph_builder = V6GraphBuilder()
        self.cascade_simulator = CascadeSimulator()
        self.explainability_engine = ExplainabilityEngine()
        self.memory_engine = MemoryEngine(graph_store)
        self.audit_logger = AuditLogger()

    async def run_million_debate(self, project_id: str, agents: List[Dict], content: str, content_type: str, intent: str) -> Dict:
        """
        Full V6 Debate Pipeline with Statistical Abstraction.
        """
        # 1. LAYER 1: MASS CONSENSUS (Statistical Abstraction)
        print(f"[V6] Running Mass Consensus (Abstraction Layer) for {len(agents)} agents...")
        
        # Group by Archetype ID (Phase 1 Fix)
        archetypes = {}
        for a in agents:
            arch_id = a.get("archetype_id", "default")
            if arch_id not in archetypes:
                archetypes[arch_id] = a
        
        print(f"[V6] Scaling 1M agents via {len(archetypes)} unique Archetype DNA profiles.")
        
        # Run reasoning on Archetype Leaders
        shards = self.shard_manager.shard_agents(list(archetypes.values()))
        
        async def process_shard(shard_agents):
            tasks = [
                run_synthesized_persona(agent, content, content_type, intent)
                for agent in shard_agents
            ]
            return await asyncio.gather(*tasks, return_exceptions=True)

        archetype_results = await self.shard_manager.process_shards(shards, process_shard)
        archetype_results = {r["archetype_id"]: r for r in archetype_results if isinstance(r, dict) and r.get("triggered")}
        
        # Statistical Projection: Map results back to full population
        mass_results = []
        for a in agents:
            arch_res = archetype_results.get(a.get("archetype_id"))
            if arch_res:
                # Clone result and apply variance
                cloned_res = arch_res.copy()
                cloned_res["agent_id"] = a["agent_id"]
                cloned_res["virality_risk"] *= a.get("variance_factor", 1.0) # Apply statistical noise
                mass_results.append(cloned_res)
        
        aggregation = self.shard_manager.aggregate_results(mass_results)
        
        # 2. LAYER 2: REPRESENTATIVE DEBATE (Sampled 100-500 Agents)
        print(f"[V6] Starting Representative Debate (Layer 2 - High Fidelity)...")
        # Stratified sampling continues to draw from the population
        rep_agents = self._sample_representative_agents(agents, count=100)
        
        rep_results = []
        for agent in rep_agents:
            # Fetch Memory Context (Zep-style Continuity)
            context = await self.memory_engine.get_agent_context(project_id, agent["agent_id"])
            enhanced_intent = f"{intent}\nPRIOR_CONTEXT: {context}"
            
            res = await run_synthesized_persona(agent, content, content_type, enhanced_intent)
            if res.get("triggered"):
                rep_results.append(res)
                # Store new memories from this interaction
                await self.memory_engine.extract_and_store_memories(
                    project_id, 
                    agent["agent_id"], 
                    res.get("reaction", "")
                )

        # 3. LAYER 3: DETAILED ARBITRATION (Judge Verdict)
        print(f"[V6] Starting Institutional Arbitration (Layer 3)...")
        debate_transcript = "\n".join([
            f"AGENT {r.get('persona_name')}: {r.get('reaction')} (RISK: {r.get('virality_risk')})" 
            for r in rep_results[:50] # Top 50 for the judge
        ])
        
        # In a real V6 implementation, we'd pull historical context from CrisisDatabase
        judge_verdict = await run_synthesis_judge(content, debate_transcript, "V6 Swarm Context")
        
        # Audit Log (Phase 5 Fix)
        self.audit_logger.log_event(
            "SESSION_ID", # In production, this would be the project ID
            "ARBITRATION_VERDICT",
            {"verdict": judge_verdict, "intent": intent}
        )

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

        # 6. EXPLAINABILITY (Phase 6 Fix)
        explanation = self.explainability_engine.explain_verdict(content, aggregation, judge_verdict)

        return {
            "aggregation": aggregation,
            "representative_debate": rep_results,
            "judge_verdict": judge_verdict,
            "consensus": final_consensus,
            "graph": influence_graph,
            "cascade": cascade_results,
            "explainability": explanation,
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
        
        # SCP: Silent Consensus Protocol
        # Evaluate using ConsensusEngine to detect polarization and intelligence gaps
        consensus_eval = self.consensus_engine.evaluate_consensus(rep_results)
        
        return {
            "final_confidence": round(final_confidence, 3),
            "status": consensus_eval.get("status", "UNCERTAIN"),
            "is_trustworthy": consensus_eval.get("is_trustworthy", False),
            "should_refuse": consensus_eval.get("should_refuse", False),
            "verdict": consensus_eval.get("verdict", ""),
            "intelligence_gaps": consensus_eval.get("intelligence_gaps", []),
            "layer_scores": {
                "mass": mass_score,
                "representative": rep_score,
                "judge": judge_score
            },
            "metrics": consensus_eval.get("metrics", {})
        }
