import json
import re
from typing import List, Dict, Any
from engines.multi_model import call_llm_with_settings

class MemoryEngine:
    """
    SentiFlow V6 Memory Engine (Zep-like Long-Term Memory).
    Extracts facts and relationships from agent reasoning and persists them 
    to the Neo4j Knowledge Graph.
    """
    
    def __init__(self, graph_store: Any):
        self.graph_store = graph_store

    async def extract_and_store_memories(self, project_id: str, agent_id: str, reasoning_text: str):
        """
        Analyzes agent reasoning to extract core facts and store them as nodes/edges.
        """
        prompt = f"""Extract 2-3 core factual assertions or 'memories' from this agent's reasoning.
        Reasoning: {reasoning_text}
        
        Return JSON format:
        {{
          "memories": [
            {{
              "fact": "Short clear statement of fact",
              "related_concepts": ["Concept1", "Concept2"],
              "importance": 0.0-1.0
            }}
          ]
        }}"""
        
        try:
            response = await call_llm_with_settings(prompt, "llama-3.1-8b-instant", 0.1)
            if isinstance(response, str):
                response = json.loads(re.search(r"\{.*\}", response, re.DOTALL).group(0))
            
            for memory in response.get("memories", []):
                # Store memory as a node and link it to the agent
                memory_node_id = f"mem_{hash(memory['fact'])}"
                
                # Update local graph store
                graph = self.graph_store.get_graph(project_id)
                
                # Add Memory Node
                if not any(n["id"] == memory_node_id for n in graph["nodes"]):
                    graph["nodes"].append({
                        "id": memory_node_id,
                        "label": memory["fact"],
                        "type": "MEMORY",
                        "importance": memory["importance"]
                    })
                
                # Add "REMEMBERS" edge from Agent to Memory
                graph["edges"].append({
                    "source": agent_id,
                    "target": memory_node_id,
                    "type": "REMEMBERS",
                    "weight": memory["importance"]
                })
                
                # Link to concepts
                for concept in memory.get("related_concepts", []):
                    concept_id = f"concept_{concept.lower()}"
                    if not any(n["id"] == concept_id for n in graph["nodes"]):
                        graph["nodes"].append({
                            "id": concept_id,
                            "label": concept,
                            "type": "CONCEPT"
                        })
                    graph["edges"].append({
                        "source": memory_node_id,
                        "target": concept_id,
                        "type": "MENTIONS"
                    })
                
                # Persist
                self.graph_store.store_graph(project_id, graph)
                
        except Exception as e:
            print(f"[MemoryEngine] Error: {e}")

    async def get_agent_context(self, project_id: str, agent_id: str) -> str:
        """
        Retrieves relevant memories for an agent to include in their next reasoning step.
        This provides 'Temporal Continuity' like Zep Cloud.
        """
        # In a real implementation, we would use a vector search or graph traversal
        # For now, we'll traverse the graph for "REMEMBERS" links
        graph = self.graph_store.get_graph(project_id)
        relevant_memories = []
        
        for edge in graph.get("edges", []):
            if edge["source"] == agent_id and edge.get("type") == "REMEMBERS":
                memory_node = next((n for n in graph["nodes"] if n["id"] == edge["target"]), None)
                if memory_node:
                    relevant_memories.append(memory_node["label"])
        
        return "\n".join(relevant_memories) if relevant_memories else "No prior memories."
