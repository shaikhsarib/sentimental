import pytest
from engines.metacognition_engine import MetacognitionEngine
from engines.crisis_database import CrisisDatabase
import os

def test_metacognition_evaluation():
    engine = MetacognitionEngine()
    
    reactions = [
        {"persona_id": "genz", "virality_risk": 9, "reaction": "Brutal!", "trigger_phrase": "cringe"},
        {"persona_id": "conservative", "virality_risk": 2, "reaction": "Whatever.", "trigger_phrase": "cringe"}
    ]
    
    # Ground truth is HIGH risk
    report = engine.evaluate_swarm_performance(reactions, "HIGH", "HIGH")
    
    assert "swarm_accuracy" in report
    assert "lessons_learned" in report
    
    # GenZ (9) vs HIGH (8) = error 1 (Accurate)
    # Conservative (2) vs HIGH (8) = error 6 (Mistake)
    mistakes = [p for p in report["agent_grades"] if p["status"] == "MISTAKE"]
    assert len(mistakes) == 1
    assert mistakes[0]["persona_id"] == "conservative"

def test_crisis_database_init(tmp_path):
    # Test initialization with a temporary database
    db_file = tmp_path / "test_crisis.db"
    db = CrisisDatabase(str(db_file))
    
    # Ensure tables are created
    cursor = db.db.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='crises'")
    assert cursor.fetchone() is not None

def test_crisis_database_similarity():
    # Use real DB but read-only check
    db_path = os.path.join(os.path.dirname(__file__), "..", "data", "sentimental.db")
    if not os.path.exists(db_path):
        pytest.skip("Main DB not found for similarity test")
        
    db = CrisisDatabase(db_path)
    # Similarity search should return a list
    results = db.find_similar_crises("liquidity crisis", "finance")
    assert isinstance(results, list)
