import asyncio
import os
import httpx
import json
from typing import List, Dict
from tenacity import retry, stop_after_attempt, wait_exponential

PERSONA_MODEL_ROUTING = {
    "activist": {
        "model": "llama-3.1-8b-instant",  # Groq model mapping
        "temperature": 0.9,     
        "system_prefix": "You are deeply passionate about social justice. You've seen too many brands exploit causes for profit. You're tired and you're not going to be nice about it.",
    },
    "conservative": {
        "model": "llama-3.1-8b-instant",
        "temperature": 0.6,     
        "system_prefix": "You hold traditional values deeply. You believe corporations should sell products, not push ideologies. You're a loyal customer until a brand disrespects your values.",
    },
    "journalist": {
        "model": "llama-3.1-8b-instant",
        "temperature": 0.4,     
        "system_prefix": "You are a meticulous investigative journalist. You look for contradictions, hypocrisy, and misleading claims. You build threads with evidence.",
    },
    "genz": {
        "model": "llama-3.1-8b-instant",
        "temperature": 0.95,    
        "system_prefix": "You're 20, chronically online, and you can smell corporate cringe from a mile away. You communicate in memes, sarcasm, and brutal honesty.",
    },
    "competitor": {
        "model": "llama-3.1-8b-instant",
        "temperature": 0.3,     
        "system_prefix": "You work at the biggest rival company. You're reading this content looking for ANYTHING you can use against them in sales calls, battle cards, or competitive blog posts.",
    },
    "regulator": {
        "model": "llama-3.3-70b-versatile",
        "temperature": 0.2,     
        "system_prefix": "You spent 15 years at the FTC. You know every regulation by heart. You evaluate content strictly against legal frameworks. You do not speculate - you cite specific rules.",
    },
    "parent": {
        "model": "llama-3.1-8b-instant",
        "temperature": 0.7,     
        "system_prefix": "You're a parent of three kids under 12. Every piece of content you see, you ask: 'Is this safe for my children? Is this appropriate? Would I want my kids seeing this?'",
    },
    "legal": {
        "model": "llama-3.3-70b-versatile",
        "temperature": 0.2,
        "system_prefix": "You are in-house legal counsel. You look for contractual risk, claims exposure, and compliance issues with conservative judgment.",
    },
    "investor": {
        "model": "llama-3.1-8b-instant",
        "temperature": 0.3,
        "system_prefix": "You are a skeptical investor. You care about reputational risk, earnings impact, and regulatory blowback.",
    },
    "community_manager": {
        "model": "llama-3.1-8b-instant",
        "temperature": 0.6,
        "system_prefix": "You manage online communities. You look for tone issues, moderation blowups, and flashpoints that turn into dogpiles.",
    },
    "creator": {
        "model": "llama-3.1-8b-instant",
        "temperature": 0.8,
        "system_prefix": "You are a creator who makes reaction content. You look for viral hooks and public contradictions.",
    },
    "supply_chain": {
        "model": "llama-3.1-8b-instant",
        "temperature": 0.4,
        "system_prefix": "You are a supply chain and operations lead. You care about sourcing claims, labor ethics, and delivery credibility.",
    },
}

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
        return await call_ollama(prompt, "llama3.1", temperature)
        
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
    
    async with httpx.AsyncClient(timeout=15.0) as client:
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
    """Run a single persona analysis with optional 'Lessons Learned' for self-correction."""
    config = PERSONA_MODEL_ROUTING.get(persona_id)
    if not config: return {"triggered": False, "persona_id": persona_id}

    objective_text = objective.strip() or "General risk scan"
    
    # Inject Self-Correction memory if available
    lesson_text = ""
    if lessons:
        lesson_text = "\n[SELF-CORRECTION DATA - LEARNED FROM PAST MISTAKES]:\n" + "\n".join([f"- {L}" for L in lessons])
    
    prompt = f"""{config['system_prefix']}
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
    # Default persona name
    result["persona_name"] = persona_id.capitalize()
    return result

async def run_synthesized_persona(persona: dict, content: str, content_type: str, objective: str, consensus_brief: str = None, lessons: List[str] = None) -> dict:
    """Run simulation for a synthesized agent with self-correcting logic."""
    # Synthesized personas are higher quality; use a stronger model
    model = "llama-3.3-70b-versatile" 
    
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
    "strategic_implication": "how this changes the world model"
}}

If the content is irrelevant to your role, set triggered to false.
"""
    result = await call_llm_with_settings(prompt, model, 0.7)
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
    """Legacy: Run all generic personas in parallel."""
    tasks = [
        run_individual_persona(pid, content, content_type, objective)
        for pid in PERSONA_MODEL_ROUTING.keys()
    ]
    results = await asyncio.gather(*tasks, return_exceptions=True)
    valid_results = [r for r in results if isinstance(r, dict) and r.get("triggered", False)]
    return valid_results
