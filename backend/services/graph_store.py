import json
import math
import os
import re
from collections import Counter
from typing import Dict, List, Optional, Tuple
import networkx as nx




_STOPWORDS = {
    "the", "and", "for", "with", "that", "this", "from", "your", "you", "are", "was",
    "were", "have", "has", "had", "will", "would", "can", "could", "should", "into",
    "over", "under", "about", "what", "when", "where", "which", "who", "their", "them",
    "then", "than", "more", "most", "also", "our", "out", "all", "any", "but", "not",
}


class GraphStore:
    def __init__(self, base_path: str, uri: Optional[str], user: Optional[str], password: Optional[str]):
        self.base_path = base_path
        self.uri = uri
        self.user = user
        self.password = password
        self.driver = None
        
        if uri and user and password:
            try:
                from neo4j import GraphDatabase
                self.driver = GraphDatabase.driver(uri, auth=(user, password))
            except ImportError:
                self.driver = None

    def _graph_path(self, project_id: str) -> str:
        return os.path.join(self.base_path, project_id, "graph.json")

    def _write_json(self, path: str, data: Dict) -> None:
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)

    def _read_json(self, path: str) -> Dict:
        if not os.path.exists(path):
            return {}
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)

    def build_graph_from_texts(self, texts: List[str], max_nodes: int = 40) -> Dict:
        tokens = []
        for text in texts:
            words = re.findall(r"[A-Za-z][A-Za-z\-]{2,}", text.lower())
            words = [w for w in words if w not in _STOPWORDS]
            tokens.extend(words)

        counts = Counter(tokens)
        top_terms = [term for term, _ in counts.most_common(max_nodes)]
        term_set = set(top_terms)

        nodes = [
            {"id": term, "label": term, "weight": counts[term]}
            for term in top_terms
        ]

        edges_map: Dict[Tuple[str, str], int] = {}
        for text in texts:
            words = re.findall(r"[A-Za-z][A-Za-z\-]{2,}", text.lower())
            words = [w for w in words if w in term_set]
            unique = list(dict.fromkeys(words))
            for i in range(len(unique)):
                for j in range(i + 1, len(unique)):
                    a, b = sorted([unique[i], unique[j]])
                    edges_map[(a, b)] = edges_map.get((a, b), 0) + 1

        edges = [
            {"source": a, "target": b, "weight": w}
            for (a, b), w in edges_map.items()
        ]

        return {"nodes": nodes, "edges": edges}

    def store_graph(self, project_id: str, graph: Dict) -> None:
        self._write_json(self._graph_path(project_id), graph)
        if not self.driver:
            return
        nodes = graph.get("nodes", [])
        edges = graph.get("edges", [])
        with self.driver.session() as session:
            # Scope to project_id to avoid wiping entire DB
            session.run("MATCH (n:Term {project_id: $pid}) DETACH DELETE n", pid=project_id)
            for node in nodes:
                session.run(
                    "MERGE (n:Term {id: $id, project_id: $pid}) SET n.label = $label, n.weight = $weight",
                    id=node["id"],
                    pid=project_id,
                    label=node.get("label", node["id"]),
                    weight=node.get("weight", 1),
                )
            for edge in edges:
                session.run(
                    "MATCH (a:Term {id: $source, project_id: $pid}), (b:Term {id: $target, project_id: $pid}) "
                    "MERGE (a)-[r:RELATES_TO]->(b) SET r.weight = $weight",
                    source=edge["source"],
                    target=edge["target"],
                    pid=project_id,
                    weight=edge.get("weight", 1),
                )

    def get_graph(self, project_id: str) -> Dict:
        graph = self._read_json(self._graph_path(project_id))
        if graph:
            return graph
        return {"nodes": [], "edges": []}

    def compute_metrics(self, graph: Dict) -> Dict:
        nodes = graph.get("nodes", [])
        edges = graph.get("edges", [])
        node_count = len(nodes)
        edge_count = len(edges)

        # Create NetworkX graph for advanced math
        G = nx.Graph()
        for node in nodes:
            G.add_node(node["id"], **node)
        for edge in edges:
            G.add_edge(edge.get("source"), edge.get("target"), weight=edge.get("weight", 1))

        # Core Graph Math
        degrees = dict(G.degree())
        betweenness = nx.betweenness_centrality(G)
        density = nx.density(G)
        
        # Identify "Bridging" nodes (High Betweenness)
        top_bridges = sorted(
            [{"id": n, "betweenness": round(b, 4)} for n, b in betweenness.items()],
            key=lambda x: x["betweenness"],
            reverse=True
        )[:5]

        top_nodes = sorted(
            [
                {
                    "id": node["id"],
                    "label": node.get("label", node["id"]),
                    "degree": degrees.get(node["id"], 0),
                    "betweenness": round(betweenness.get(node["id"], 0), 4),
                    "weight": node.get("weight", 1),
                }
                for node in nodes
            ],
            key=lambda n: (n["betweenness"], n["degree"]),
            reverse=True,
        )[:8]

        top_edges = sorted(
            [
                {
                    "source": edge.get("source"),
                    "target": edge.get("target"),
                    "weight": edge.get("weight", 1),
                }
                for edge in edges
            ],
            key=lambda e: e["weight"],
            reverse=True,
        )[:8]

        return {
            "node_count": node_count,
            "edge_count": edge_count,
            "density": round(density, 4),
            "top_nodes": top_nodes,
            "top_edges": top_edges,
            "top_bridges": top_bridges,
            "is_connected": nx.is_connected(G) if node_count > 0 else True
        }

    def get_graph_metrics(self, project_id: str) -> Dict:
        graph = self.get_graph(project_id)
        return self.compute_metrics(graph)

    async def generate_ontology(self, text: str) -> Dict:
        """Step 1: Extract Entity/Relation types from seeds."""
        from engines.multi_model import call_llm_with_settings
        
        prompt = f"""Analyze this text and define a Knowledge Graph Ontology (Schema).
Identifer potential entity types (e.g. PERSON, ORGANIZATION, EVENT, RISK_POINT) and relation types.
TEXT: {text[:5000]}

Return JSON: 
{{
  "entity_types": ["TYPE1", "TYPE2"],
  "relation_types": ["RELATION1", "RELATION2"],
  "mission_context": "Short summary of the world logic"
}}"""
        response = await call_llm_with_settings(prompt, "llama3-70b-8192", 0.1)
        # Parse logic if string
        if isinstance(response, str):
            try:
                # Basic cleanup if LLM returns markdown
                clean = re.search(r"\{.*\}", response, re.DOTALL).group(0)
                return json.loads(clean)
            except:
                return {"entity_types": ["PERSON", "ENTITY", "FLASHPOINT"], "relation_types": ["RELATES_TO"]}
        return response

    async def extract_entities(self, texts: List[str], ontology: Dict) -> Dict:
        """Step 2: Extract actual world nodes based on onto."""
        from engines.multi_model import call_llm_with_settings
        
        combined_text = "\n".join([t[:2000] for t in texts])
        prompt = f"""Extract knowledge graph entities and relations based on this ontology:
ONTOLOGY: {json.dumps(ontology)}
TEXT: {combined_text}

Return JSON:
{{
  "nodes": [{{"id": "UniqueName", "type": "TYPE_FROM_ONTOLOGY", "description": "brief info"}}],
  "links": [{{"source": "ID1", "target": "ID2", "type": "REL_TYPE"}}]
}}"""
        response = await call_llm_with_settings(prompt, "llama3-70b-8192", 0.1)
        if isinstance(response, str):
            try:
                clean = re.search(r"\{.*\}", response, re.DOTALL).group(0)
                return json.loads(clean)
            except:
                return {"nodes": [], "links": []}
        return response
