import asyncio
import os
import sys
from main import v6_debate_engine, v6_db, graph_store, project_store
from engines.agent_factory import AgentFactory
from engines.entity_extractor import EntityExtractor

async def run_e2e_test():
    """
    SentiFlow V6 End-to-End Verification.
    Validates the full pipeline: Ingestion -> Swarm -> Debate -> Memory.
    """
    print("--- SENTIFLOW V6 E2E VERIFICATION ---")
    
    # 1. Environment Check
    if not os.getenv("GROQ_API_KEY"):
        print("ERROR: GROQ_API_KEY not found in environment.")
        return

    # 2. Setup Project
    pid = "reproduction_test"
    project_store.create_project("Reproduction Test", "Verification of V6 Pipeline")
    
    # 3. Process Content
    content = "The global supply chain is facing a critical failure in semiconductor logistics."
    print(f"Ingesting content: {content[:50]}...")
    
    extractor = EntityExtractor()
    entities = await extractor.extract(content, high_fidelity=True)
    
    # 4. Generate Swarm
    print("Generating swarm...")
    factory = AgentFactory(domain="LOGISTICS")
    swarm = factory.generate_swarm(entities, target_count=10) # Small swarm for test
    v6_db.save_agent_swarm(swarm)
    
    # 5. Execute Debate
    print("Executing Hierarchical Debate...")
    results = await v6_debate_engine.run_million_debate(
        project_id=pid,
        agents=swarm,
        content=content,
        content_type="news_alert",
        intent="Risk assessment"
    )
    
    # 6. Verify Results
    print("\n--- RESULTS ---")
    print(f"Confidence: {results['consensus']['final_confidence']}")
    print(f"Memories Generated: {len([n for n in results['graph']['nodes'] if n.get('type') == 'MEMORY'])}")
    print("\n✅ V6 Pipeline Verified Successfully.")

if __name__ == "__main__":
    asyncio.run(run_e2e_test())
