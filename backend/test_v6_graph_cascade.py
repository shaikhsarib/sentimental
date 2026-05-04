import asyncio
import json
from engines.agent_factory import AgentFactory
from engines.entity_extractor import ExtractedEntity
from engines.v6_graph_builder import V6GraphBuilder
from engines.cascade_simulator import CascadeSimulator

async def test_graph_cascade():
    print("STARTING SENTIFLOW V6 PHASE 4: GRAPH & CASCADE TEST")
    
    # 1. Setup
    factory = AgentFactory(domain="TECHNOLOGY")
    graph_builder = V6GraphBuilder()
    simulator = CascadeSimulator()
    
    # 2. Mock Entities
    entities = [
        ExtractedEntity(id="e1", name="SentiFlow Corp", type="ORGANIZATION"),
        ExtractedEntity(id="e2", name="Market Regulators", type="ORGANIZATION"),
        ExtractedEntity(id="e3", name="Adversarial Hackers", type="ORGANIZATION")
    ]
    
    # 3. Generate Swarm (50 agents for graph density)
    print("--- Generating Swarm ---")
    swarm = factory.generate_swarm(entities, target_count=50)
    print(f"Generated {len(swarm)} agents.")
    
    # 4. Build Graph
    print("--- Building Influence Graph ---")
    graph = graph_builder.build_influence_graph(swarm)
    print(f"Graph Built: {len(graph['nodes'])} nodes, {len(graph['edges'])} edges.")
    print(f"Graph Density: {graph['metadata']['density']:.4f}")
    
    # 5. Run Cascade (with different emotions to see physics)
    print("--- Running Cascade Simulation (Emotion Physics) ---")
    
    # Run 1: High Anger Seed
    print("\nScenario 1: Anger-Driven Contagion")
    for agent in swarm[:5]: 
        agent["emotion_profile"] = "anger"
    results_anger = simulator.run_simulation(graph, initial_infected_count=3)
    print(f"R0 Estimate: {results_anger['metadata']['r_naught']}")
    print(f"Peak Infection: {results_anger['metadata']['peak_infection']}")
    print(f"Total Affected: {results_anger['metadata']['total_affected']}")
    
    # Run 2: High Sadness Seed
    print("\nScenario 2: Sadness-Driven Contagion")
    for agent in swarm[:5]: 
        agent["emotion_profile"] = "sadness"
    results_sad = simulator.run_simulation(graph, initial_infected_count=3)
    print(f"R0 Estimate: {results_sad['metadata']['r_naught']}")
    print(f"Peak Infection: {results_sad['metadata']['peak_infection']}")
    print(f"Total Affected: {results_sad['metadata']['total_affected']}")
    
    print("\nV6 PHASE 4 TEST COMPLETE")

if __name__ == "__main__":
    asyncio.run(test_graph_cascade())
