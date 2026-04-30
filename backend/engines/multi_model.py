import asyncio
import os
import httpx
import json
import yaml
from typing import List, Dict, Optional
from tenacity import retry, stop_after_attempt, wait_exponential

# ─── TAXONOMY LOADER ───
TAXONOMY_PATH = os.path.join(os.path.dirname(__file__), "taxonomy.yaml")

class TaxonomyManager:
    """Manages the tiered agent taxonomy and model routing."""
    def __init__(self, yaml_path: str):
        self.yaml_path = yaml_path
        self.data = self._load_yaml()
        self.personas = self._flatten_personas()

    def _load_yaml(self) -> dict:
        try:
            with open(self.yaml_path, "r", encoding="utf-8") as f:
                return yaml.safe_load(f)
        except Exception as e:
            print(f"[TAXONOMY ERROR] Failed to load {self.yaml_path}: {e}")
            return {"tiers": {}}

    def _flatten_personas(self) -> dict:
        """Flattens nested tiers into a single lookup for performance."""
        flat = {}
        tiers = self.data.get("tiers", {})
        for tier_name, tier_config in tiers.items():
            tier_model = tier_config.get("model", "llama-3.1-8b-instant")
            tier_temp = tier_config.get("temperature", 0.7)
            
            for pid, pconfig in tier_config.get("personas", {}).items():
                flat[pid] = {
                    **pconfig,
                    "tier": tier_name,
                    "model": pconfig.get("model", tier_model),
                    "temperature": pconfig.get("temperature", tier_temp),
                    "persona_id": pid
                }
        return flat

    def get_persona(self, persona_id: str) -> Optional[dict]:
        return self.personas.get(persona_id)

# Initialize global manager
taxonomy = TaxonomyManager(TAXONOMY_PATH)

@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=2, max=10)
)
async def call_llm_with_settings(prompt: str, model: str, temperature: float) -> dict:
    """Make the API call to Groq for speed."""
    local_model = os.getenv("LOCAL_MODEL")
    use_local = os.getenv("USE_LOCAL_MODEL", "").lower() in ("1", "true", "yes")
    if use_local and local_model:
        return await call_ollama(prompt, local_model, temperature)

    key = os.getenv("GROQ_API_KEY")
    if not key or "your-key" in key:
        # Fallback to local Ollama if Groq is not configured
        return await call_ollama(prompt, "llama-3.1-8b-instant", temperature)
        
    url = "https://api.groq.com/openai/v1/chat/completions"
    headers = {"Authorization": f"Bearer {key}", "Content-Type": "application/json"}
    payload = {
        "model": model,
        "response_format": {"type": "json_object"},
        "temperature": temperature,
        "messages": [
            {"role": "system", "content": "You must respond ONLY with valid JSON."},
            {"role": "user", "content": prompt}
        ]
    }
    
    async with httpx.AsyncClient(timeout=25.0) as client:
        try:
            resp = await client.post(url, headers=headers, json=payload)
            resp.raise_for_status()
            content = resp.json()["choices"][0]["message"]["content"]
            return json.loads(content)
        except Exception as e:
            print(f"[LLM Error] {e}")
            return {"error": str(e), "triggered": False}

async def call_ollama(prompt: str, model: str, temperature: float) -> dict:
    url = "http://localhost:11434/api/chat"
    payload = {
        "model": model,
        "stream": False,
        "format": "json",
        "options": {"temperature": temperature},
        "messages": [{"role": "user", "content": prompt}]
    }
    async with httpx.AsyncClient(timeout=60.0) as client:
        try:
            resp = await client.post(url, json=payload)
            resp.raise_for_status()
            content = resp.json()["message"]["content"]
            return json.loads(content)
        except Exception as e:
            print(f"[Ollama Error] {e}")
            return {"error": str(e), "triggered": False}

async def run_individual_persona(persona_id: str, content: str, content_type: str, objective: str, lessons: List[str] = None) -> dict:
    """Run a single persona analysis using the dynamic taxonomy."""
    config = taxonomy.get_persona(persona_id)
    if not config: 
        return {"triggered": False, "persona_id": persona_id, "error": "Persona not in taxonomy"}

    objective_text = objective.strip() or "General risk scan"
    
    # Inject Tactical Memory if available
    lesson_text = ""
    if lessons:
        lesson_text = "\n[TACTICAL MEMORY - LEARNED FROM PAST MISTAKES]:\n" + "\n".join([f"- {L}" for L in lessons])
    
    # Use Tier-specific system prompts from taxonomy
    system_prefix = config.get("system_prefix", "Analyze this content from your perspective.")
    
    prompt = f"""{system_prefix}
{lesson_text}

Analyze this content and respond AS THIS PERSONA:

CONTENT: \"\"\"{content}\"\"\"
CONTENT TYPE: {content_type}
USER OBJECTIVE: {objective_text}

Respond with strictly valid JSON:
{{
    "triggered": true,
    "reaction": "your authentic reaction in your voice",
    "trigger_phrase": "exact phrase that triggered you",
    "citation": "the specific snippet from the content that supports this reaction",
    "emotion": "primary emotion",
    "virality_risk": 5, // integer 1-10
    "follow_up_action": "what you do next",
    "platform": "where you post this reaction",
    "amplifies_to": ["which other personas share this"]
}}

If the content doesn't trigger you AT ALL, set triggered to false and explain briefly.
"""
    result = await call_llm_with_settings(prompt, config["model"], config["temperature"])
    result["persona_id"] = persona_id
    result["persona_name"] = config.get("name", persona_id)
    result["tier"] = config.get("tier", "unknown")
    return result

async def run_synthesized_persona(persona: dict, content: str, content_type: str, objective: str, consensus_brief: str = None, lessons: List[str] = None) -> dict:
    """Run simulation for a synthesized agent (usually Tier 1 Experts)."""
    # Synthesized personas default to high-reasoning 70B unless specified
    model = persona.get("model", "llama-3.3-70b-versatile")
    temp = persona.get("temperature", 0.4)
    
    objective_text = objective.strip() or "General analysis"
    
    debate_context = f"\nSWARM_CONSENSUS_SO_FAR: {consensus_brief}\nBased on this consensus, refine your initial risk assessment." if consensus_brief else ""
    
    lesson_text = ""
    if lessons:
        lesson_text = "\n[TACTICAL MEMORY - PAST PERFORMANCE FEEDBACK]:\n" + "\n".join([f"- {L}" for L in lessons])

    prompt = f"""You are acting as the specialized persona: {persona['name']}
ROLE: {persona.get('role', 'Agent')}
BACKGROUND: {persona.get('background', 'Unknown')}
PERSONALITY: {persona.get('personality', 'Neutral')}
LOGIC: {persona.get('behavioral_logic', 'Standard reasoning')}
{lesson_text}

MISSION CONTEXT: Analyze the following narrative/content and respond in your authentic voice.
{debate_context}

CONTENT: \"\"\"{content}\"\"\"
CONTENT TYPE: {content_type}
SIMULATION OBJECTIVE: {objective_text}

Respond with strictly valid JSON:
{{
    "triggered": true,
    "reaction": "your authentic response as this agent",
    "trigger_phrase": "specific aspect that caught your focus",
    "emotion": "primary psychological state",
    "virality_risk": 5, // 1-10 (adjust based on swarm consensus if applicable)
    "strategic_implication": "how this changes the world model",
    "citations": ["direct quotes or data points from the mission docs"]
}}

If the content is irrelevant to your role, set triggered to false.
"""
    result = await call_llm_with_settings(prompt, model, temp)
    result["persona_id"] = persona.get("persona_id", persona['name'])
    result["persona_name"] = persona['name']
    return result

async def run_grounded_swarm(custom_personas: list, content: str, content_type: str, objective: str = "") -> list:
    """Run simulation across a set of grounded synthesized agents."""
    tasks = [
        run_synthesized_persona(p, content, content_type, objective)
        for p in custom_personas
    ]
    results = await asyncio.gather(*tasks, return_exceptions=True)
    return [r for r in results if isinstance(r, dict) and r.get("triggered")]

async def run_all_personas(content: str, content_type: str, objective: str = "") -> list:
    """Legacy: Run all personas from the taxonomy in parallel."""
    tasks = [
        run_individual_persona(pid, content, content_type, objective)
        for pid in taxonomy.personas.keys()
    ]
    results = await asyncio.gather(*tasks, return_exceptions=True)
    valid_results = [r for r in results if isinstance(r, dict) and r.get("triggered", False)]
    return valid_results
