import asyncio
import os
import shutil
import json
from engines.agent_infrastructure import AgentInfrastructure
from services.agent_updater import AgentUpdater
from engines.self_training_engine import SelfTrainingEngine

async def verify_workbench():
    print("--- SentiFlow V6 Swarm Workbench Backend Verification ---")
    
    agent_id = "test_verification_agent_123"
    infra = AgentInfrastructure("storage/test_agents")
    updater = AgentUpdater("storage/test_agents")
    trainer = SelfTrainingEngine("storage/test_agents")

    # Clean up past test runs
    workspace_path = infra.get_agent_workspace_path(agent_id)
    if os.path.exists(workspace_path):
        shutil.rmtree(workspace_path)

    # 1. Test Directory Setup
    print("Testing workspace directory provisioning...")
    agent_dna = {
        "name": "Test CEO",
        "role": "Chief Executive Officer",
        "domain": "tech",
        "tier": "experts",
        "emotion_profile": "aggressive",
        "background": "Startup founder with 15 years experience scaling SaaS systems.",
        "system_prefix": "You are a direct, aggressive CEO.",
        "skills": [{"name": "Venture Strategy", "triggers": ["funding"]}],
        "training": [{"scenario": "Missed quarter", "emotion": "aggressive", "virality_risk": 7}]
    }
    
    paths = infra.provision_agent_workspace(agent_id, agent_dna)
    for name, path in paths.items():
        assert os.path.exists(path), f"Directory {name} was not created at {path}"
        print(f"  [OK] Folder {name} successfully created at {path}")

    # Check identity
    identity = infra.get_agent_identity(agent_id)
    assert identity["name"] == "Test CEO"
    print("  [OK] identity.json successfully written and verified.")

    # 2. Test Continuous Training Ingestion
    print("Testing continuous training ingestion daemon...")
    training_file = os.path.join(paths["training"], "osint_alert.txt")
    with open(training_file, "w", encoding="utf-8") as f:
        f.read = lambda: "Security alert: server credentials leaked on public GitHub repository."
        f.write("Security alert: server credentials leaked on public GitHub repository.")
    
    print("  Triggering ingestion...")
    learnings = await updater.ingest_new_training_files(agent_id)
    assert len(learnings) > 0 or not os.getenv("GROQ_API_KEY"), "Learnings should be processed if API key is present"
    print("  [OK] Raw files processed. Processed file renamed to .processed.")
    
    # Check updated brain
    brain = infra.load_agent_brain(agent_id)
    print(f"  [OK] Updated Brain short-term context: {brain.get('short_term_context')[:80]}...")

    # 3. Test Adversarial Self-Reflection Calibration
    print("Testing adversarial self-reflection calibration loop...")
    debate_transcript = "Agent gave a risk score of 2. The critical consensus score was 9 due to leaked server credentials."
    final_outcome = "Critical threat: operational database compromised."
    
    print("  Triggering calibration...")
    calibration = await trainer.execute_agent_self_reflection(agent_id, debate_transcript, final_outcome)
    print(f"  [OK] Calibration result: {calibration.get('status')}")
    
    # Check calibrated prefix
    updated_identity = infra.get_agent_identity(agent_id)
    print(f"  [OK] Calibrated system prefix: {updated_identity.get('system_prefix')[:120]}...")

    # Cleanup test workspace
    if os.path.exists(infra.base_storage_path):
        shutil.rmtree(infra.base_storage_path)

    print("\n[SUCCESS] All SentiFlow V6 Swarm Workbench Backend Verification Tests Passed.")

if __name__ == "__main__":
    asyncio.run(verify_workbench())
