import json
import re
from typing import Dict, Any
from engines.multi_model import call_llm_with_settings


class GraphRAGEngine:
    """
    Lightweight GraphRAG engine that retrieves evidence from the graph + documents
    and optionally synthesizes a grounded answer.
    """

    def __init__(self, graph_store: Any, db: Any):
        self.graph_store = graph_store
        self.db = db

    def build_context(self, project_id: str, query: str, doc_limit: int = 5, memory_limit: int = 6) -> Dict:
        insights = self.graph_store.get_graph_insights(project_id, query=query)
        memories = self.graph_store.get_memory_nodes(project_id, limit=memory_limit)
        documents = self.db.search_documents(query, limit=doc_limit)
        facts = (insights.get("search") or {}).get("facts", [])

        return {
            "query": query,
            "graph_metrics": insights.get("metrics", {}),
            "top_nodes": insights.get("top_nodes", [])[:5],
            "top_bridges": insights.get("top_bridges", [])[:5],
            "facts": facts[:8],
            "memories": memories,
            "documents": documents
        }

    def format_context(self, context: Dict) -> str:
        doc_lines = [
            f"- {doc.get('title')}: {doc.get('snippet')}" for doc in context.get("documents", [])
        ]
        memory_lines = [
            f"- {mem.get('label') or mem.get('id')} (importance: {mem.get('importance', 0)})"
            for mem in context.get("memories", [])
        ]
        fact_lines = [f"- {fact}" for fact in context.get("facts", [])]
        node_lines = [
            f"- {node.get('label') or node.get('id')} (betweenness: {node.get('betweenness', 0)})"
            for node in context.get("top_nodes", [])
        ]

        return "\n".join([
            "GRAPH FACTS:",
            *fact_lines,
            "\nTOP NODES:",
            *node_lines,
            "\nMEMORIES:",
            *memory_lines,
            "\nDOCUMENTS:",
            *doc_lines
        ])

    async def synthesize(self, query: str, context: Dict, model: str = "llama-3.1-8b-instant") -> Dict:
        context_text = self.format_context(context)
        prompt = f"""You are a GraphRAG analyst. Use only the provided evidence to answer.

QUERY:
{query}

EVIDENCE:
{context_text}

Return JSON:
{{
  \"answer\": \"string\",
  \"citations\": [\"string\"],
  \"confidence\": 0.0
}}
"""
        response = await call_llm_with_settings(prompt, model, 0.3)
        if isinstance(response, str):
            match = re.search(r"\{.*\}", response, re.DOTALL)
            if match:
                return json.loads(match.group(0))
        return response
