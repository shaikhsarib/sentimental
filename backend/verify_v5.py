import sys
import os

# Add backend to path
sys.path.append(os.path.join(os.getcwd(), "backend"))

try:
    import networkx as nx
    print("[OK] NetworkX Loaded")
    
    from engines.metacognition_engine import MetacognitionEngine
    meta = MetacognitionEngine()
    print("[OK] MetacognitionEngine Initialized")
    
    from engines.crisis_database import CrisisDatabase
    cdb = CrisisDatabase("engines/test_crisis.db")
    print("[OK] CrisisDatabase/ChromaDB Initialized")
    
    from services.graph_store import GraphStore
    gs = GraphStore("storage", None, None, None)
    dummy_graph = {
        "nodes": [{"id": "Node1", "label": "Node 1", "weight": 1, "betweenness": 0}, {"id": "Node2", "label": "Node 2", "weight": 2, "betweenness": 0.5}],
        "edges": [{"source": "Node1", "target": "Node2", "weight": 1}]
    }
    metrics = gs.compute_metrics(dummy_graph)
    print(f"[OK] Graph Metrics Computed with NetworkX: {list(metrics.keys())}")
    
    print("\n[SUCCESS] V5 SYSTEM INTEGRITY VERIFIED")
except Exception as e:
    print(f"[ERROR] Verification Failed: {e}")
    sys.exit(1)
