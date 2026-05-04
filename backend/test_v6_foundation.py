import asyncio
import os
from engines.document_processor import DocumentProcessor
from engines.entity_extractor import EntityExtractor
from engines.domain_analyzer import DomainAnalyzer
from engines.agent_factory import AgentFactory
from engines.sentimental_db import SentiDatabase
from engines.swarm_shard_manager import SwarmShardManager
from engines.million_debate_engine import MillionDebateEngine

async def test_foundation():
    print("STARTING SENTIFLOW V6 FOUNDATION TEST")
    
    # 1. Setup
    db = SentiDatabase("data/sentimental_v6.db")
    processor = DocumentProcessor()
    extractor = EntityExtractor()
    analyzer = DomainAnalyzer()
    shard_manager = SwarmShardManager(batch_size=5, max_workers=2) # Very conservative for rate limits
    debate_engine = MillionDebateEngine(shard_manager)
    
    pdf_path = "SENTIMENTAL_V6_BLUEPRINT.pdf"
    if not os.path.exists(pdf_path):
        print(f"Error: {pdf_path} not found.")
        return

    # 2. Extract Text
    print("--- Extracting Text ---")
    with open(pdf_path, "rb") as f:
        content = f.read()
    raw_text = processor.extract_text(content, pdf_path)
    print(f"Extracted {len(raw_text)} characters.")

    # 3. Domain Analysis
    print("--- Analyzing Domain & Emotion ---")
    domain_data = await analyzer.analyze(raw_text)
    print(f"Domain: {domain_data.get('domain')} | Sentiment: {domain_data.get('sentiment')}")

    # 4. Entity Extraction
    print("--- Extracting Entities ---")
    entities = await extractor.extract(raw_text[:5000], high_fidelity=True)
    print(f"Found {len(entities)} entities.")

    # 5. Agent Factory
    print("--- Generating Swarm ---")
    factory = AgentFactory(domain=domain_data.get("domain", "GENERAL"))
    # Limit entities to 2 for test to keep agent count low (2 * 5 variants = 10 agents)
    swarm = factory.generate_swarm(entities[:2], target_count=10) 
    print(f"Generated {len(swarm)} agents (v6 specs).")

    # 6. Debate Engine (NEW Phase 3)
    print("--- Running Million-Agent Debate (Phase 3) ---")
    debate_results = await debate_engine.run_million_debate(
        agents=swarm,
        content=raw_text[:1000], # Context sample
        content_type="pdf",
        intent="Analyze the feasibility of the V6 architecture."
    )
    print(f"Debate Complete. Consensus Confidence: {debate_results['consensus']['final_confidence']}")

    # 7. Database Storage
    print("--- Saving to SentiDatabase V6 ---")
    project_id = db.create_project(
        name="V6 Swarm Test", 
        description="Testing Phase 1, 2, & 3 engines",
        domain=domain_data.get("domain")
    )
    doc_id = db.add_document(project_id, "V6 Blueprint", raw_text, "pdf")
    db.save_agent_swarm(swarm)
    
    print(f"Project Created: {project_id}")
    print(f"Swarm Saved: {len(swarm)} agents")
    print("V6 FOUNDATION TEST COMPLETE")

if __name__ == "__main__":
    asyncio.run(test_foundation())
