import re
import uuid
from typing import Dict, List, Optional
from dataclasses import dataclass, field
from engines.multi_model import call_llm_with_settings

@dataclass
class ExtractedEntity:
    id: str
    name: str
    type: str # PERSON, ORGANIZATION, ROLE, CONCEPT, PRODUCT, LOCATION, EVENT
    mentions: int = 1
    context_snippets: List[str] = field(default_factory=list)
    attributes: Dict = field(default_factory=dict)
    related_entities: List[str] = field(default_factory=list)

class EntityExtractor:
    """
    SentiFlow V6 Entity Extractor.
    Extracts people, organizations, roles, and concepts using a hybrid 
    Regex + LLM approach.
    """
    
    def __init__(self):
        # Patterns from Blueprint Page 4
        self.patterns = {
            "ROLE": r'\b(?:CEO|CTO|CFO|Head|VP|Director|Manager|Lead|Advisor|Consultant|Specialist|Analyst)\s+of\s+([A-Z][a-zA-Z\s]+)\b',
            "ORG": r'\b([A-Z][a-zA-Z0-9]*\s+(?:Inc|Corp|LLC|Ltd|Group|Holdings|Solutions|Technologies))\b',
            "CONCEPT": r'\"([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)\"',
            "PERSON": r'\b([A-Z][a-z]+\s+[A-Z][a-z]+)\b'
        }

    async def extract(self, text: str, high_fidelity: bool = True) -> List[ExtractedEntity]:
        """Run extraction pipeline."""
        entities = {}
        
        # 1. Regex Extraction
        for e_type, pattern in self.patterns.items():
            matches = re.finditer(pattern, text)
            for match in matches:
                name = match.group(0).strip()
                if name not in entities:
                    entities[name] = ExtractedEntity(
                        id=str(uuid.uuid4()),
                        name=name,
                        type=e_type,
                        context_snippets=[text[max(0, match.start()-50):min(len(text), match.end()+50)]]
                    )
                else:
                    entities[name].mentions += 1
        
        # 2. LLM High-Fidelity Extraction (Optional)
        if high_fidelity and len(text) > 100:
            llm_entities = await self._llm_extract(text[:8000]) # Sample for speed
            for le in llm_entities:
                name = le.get("name")
                if name and name not in entities:
                    entities[name] = ExtractedEntity(
                        id=str(uuid.uuid4()),
                        name=name,
                        type=le.get("type", "CONCEPT"),
                        attributes=le.get("attributes", {})
                    )
        
        return list(entities.values())

    async def _llm_extract(self, text: str) -> List[Dict]:
        """Use 70B model to extract deep entities and relationships."""
        prompt = f"""
SYSTEM: You are the SentiFlow V6 Entity Extraction Engine. 
Extract key players, organizations, roles, and defining concepts from the text below.

TEXT:
{text}

Respond in strictly valid JSON:
[
  {{
    "name": "string",
    "type": "PERSON|ORGANIZATION|ROLE|CONCEPT|PRODUCT",
    "attributes": {{ "power_level": 1-10, "bias": "string" }}
  }}
]
"""
        try:
            # Using 70B for extraction as per V6 specs
            import json
            response = await call_llm_with_settings(prompt, "llama-3.3-70b-versatile", 0.1)
            if isinstance(response, str):
                match = re.search(r'\[.*\]', response, re.DOTALL)
                if match:
                    return json.loads(match.group(0))
            return response if isinstance(response, list) else []
        except Exception as e:
            print(f"[ERROR] LLM Entity Extraction failed: {e}")
            return []
