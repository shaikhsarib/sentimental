import pytest
from services.simulation_runner import SimulationRunner
from services.graph_store import GraphStore
from engines.crisis_database import CrisisDatabase
import os
from unittest.mock import AsyncMock

@pytest.fixture
def runner():
    # Use a mock/temp DB if possible, or just a dummy path
    db = CrisisDatabase(":memory:")
    return SimulationRunner(db)

@pytest.fixture
def graph_store(tmp_path):
    return GraphStore(str(tmp_path), None, None, None)

@pytest.mark.asyncio
async def test_simulation_runner_shield(runner, mock_call_llm):
    # Test shield simulation with mocked LLM
    content = "A sudden liquidity crisis strikes the sector."
    result = await runner.run_shield(content, "post", "finance")
    
    assert "risk_level" in result
    assert "persona_reactions" in result
    # Shield mode should return specific structure
    assert result["mode"] == "shield"

def test_graph_store_build(graph_store):
    texts = ["Alice knows Bob.", "Bob knows Charlie."]
    graph = graph_store.build_graph_from_texts(texts)
    
    # Check nodes
    node_ids = [n["id"] for n in graph["nodes"]]
    assert "alice" in node_ids
    assert "bob" in node_ids
    assert "charlie" in node_ids
    
    # Check edges
    assert len(graph["edges"]) >= 2

def test_graph_store_metrics(graph_store):
    graph = {
        "nodes": [{"id": "a"}, {"id": "b"}, {"id": "c"}],
        "edges": [{"source": "a", "target": "b", "weight": 1}, {"source": "b", "target": "c", "weight": 2}]
    }
    metrics = graph_store.compute_metrics(graph)
    
    assert metrics["node_count"] == 3
    assert metrics["edge_count"] == 2
    assert metrics["world_cohesion"] > 0
    assert len(metrics["top_nodes"]) > 0
