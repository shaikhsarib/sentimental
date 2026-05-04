import asyncio
import random
import numpy as np
from typing import List, Dict, Callable, Optional
from collections import Counter

class SwarmShardManager:
    """
    SentiFlow V6 Shard Manager.
    Manages millions of agents by splitting them into manageable shards 
    and processing them with strict concurrency control.
    """
    
    def __init__(self, batch_size: int = 50, max_workers: int = 10):
        self.batch_size = batch_size
        self.max_workers = max_workers
        self.semaphore = asyncio.Semaphore(max_workers)

    def shard_agents(self, agents: List[Dict]) -> List[List[Dict]]:
        """Split a massive agent list into shards (Blueprint Page 15)."""
        return [agents[i:i + self.batch_size] for i in range(0, len(agents), self.batch_size)]

    async def process_shards(self, shards: List[List[Dict]], process_fn: Callable) -> List[Dict]:
        """
        Process all shards asynchronously with concurrency control.
        """
        async def process_one(shard):
            async with self.semaphore:
                # We pass the semaphore to the process_fn or rely on it here
                return await process_fn(shard)
        
        tasks = [process_one(shard) for shard in shards]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        all_results = []
        for r in results:
            if isinstance(r, list):
                all_results.extend(r)
            elif isinstance(r, Exception):
                print(f"[SHARD ERROR] Task failed: {r}")
                
        return all_results

    def aggregate_results(self, results: List[Dict], sample_size: int = 1000) -> Dict:
        """
        Statistical aggregation for massive result sets (Blueprint Page 15-16).
        Calculates position distribution, risk mean/std, and consensus.
        """
        if not results:
            return {}

        # If results are too many, sample for statistical significance
        sample = random.sample(results, min(len(results), sample_size))
        
        positions = Counter(r.get("position", "NEUTRAL") for r in sample)
        risks = [r.get("virality_risk", 5) for r in sample]
        confidences = [r.get("confidence", 5) for r in sample]
        emotions = Counter(r.get("emotion_detected", "neutral") for r in sample)

        risk_mean = float(np.mean(risks))
        risk_std = float(np.std(risks))
        
        # Simple consensus calculation: weight of the majority position
        total_votes = len(sample)
        majority_pos, majority_count = positions.most_common(1)[0]
        consensus_score = majority_count / total_votes

        return {
            "total_agents": len(results),
            "sample_size": len(sample),
            "position_distribution": dict(positions),
            "emotion_distribution": dict(emotions),
            "risk_stats": {
                "mean": round(risk_mean, 2),
                "std": round(risk_std, 2),
                "majority_position": majority_pos
            },
            "consensus_score": round(consensus_score, 3),
            "confidence_mean": round(float(np.mean(confidences)), 2)
        }
