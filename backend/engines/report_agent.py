import json
import re
from typing import Dict, Any
from engines.multi_model import call_llm_with_settings


class ReportAgent:
    """
    Tool-augmented report agent that blends debate results with GraphRAG evidence.
    """

    def __init__(self, graph_rag_engine: Any, export_service: Any):
        self.graph_rag_engine = graph_rag_engine
        self.export_service = export_service

    async def generate_report(self, project_id: str, debate_data: Dict, queries: Dict) -> Dict:
        base_report = self.export_service.generate_report_markdown(project_id, debate_data, queries)
        context = self.graph_rag_engine.build_context(
            project_id,
            "Key entities, relationships, and risks",
            doc_limit=4,
            memory_limit=6
        )
        context_text = self.graph_rag_engine.format_context(context)

        prompt = f"""You are the SentiFlow V6 Senior Intelligence Arbiter. 
Your goal is to produce an 'Industrial-Grade Strategic Addendum' that complements the raw debate data with deep-graph evidence.

EVIDENCE (GraphRAGE context):
{context_text}

DEBATE SUMMARY:
{json.dumps(debate_data.get('aggregation', {}), indent=2)}

Produce a high-fidelity intelligence report in strictly valid JSON format:
{{
  "executive_summary": "One-paragraph high-impact summary of the threat landscape",
  "key_entities": [
    {{"entity": "Entity Name", "role": "Strategic Role", "risk_contribution": "Description"}}
  ],
  "risk_signals": [
    {{"signal": "Signal Name", "strength": "0-100", "description": "Why it matters"}}
  ],
  "tactical_playbook": [
    {{"phase": "Immediate/Short-Term/Long-Term", "action": "Specific tactical move", "outcome": "Expected result"}}
  ],
  "narrative_trajectory": "Forecasting how the narrative evolves over the next 72 hours based on Graph evidence",
  "confidence_score": 0.0
}}
"""
        response = await call_llm_with_settings(prompt, "llama-3.3-70b-versatile", 0.3)
        if isinstance(response, str):
            match = re.search(r"\{.*\}", response, re.DOTALL)
            if match:
                try:
                    response = json.loads(match.group(0))
                except:
                    pass

        return {
            "base_report": base_report,
            "addendum": response,
            "evidence": context
        }
