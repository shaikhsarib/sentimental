import re
from typing import Dict, List
from engines.multi_model import call_llm_with_settings

class DomainAnalyzer:
    """
    SentiFlow V6 Domain Analyzer.
    Detects industry domain, core sentiment, and granular emotion profile.
    """
    
    DOMAINS = ["TECHNOLOGY", "FINANCE", "HEALTHCARE", "LEGAL", "MARKETING", "GENERAL"]
    
    EMOTIONS = [
        "anger", "outrage", "fear", "disgust", "anxiety", 
        "sadness", "amusement", "shock", "contempt", "resignation", "neutral"
    ]

    async def analyze(self, text: str) -> Dict:
        """Perform full domain and emotion analysis."""
        prompt = f"""
SYSTEM: You are the SentiFlow V6 Domain & Emotion Analyzer.
Analyze the document text to determine the primary domain and the dominant emotional response it will trigger.

TEXT:
{text[:4000]}

Respond in strictly valid JSON:
{{
  "domain": "TECHNOLOGY|FINANCE|HEALTHCARE|LEGAL|MARKETING",
  "sentiment": "POSITIVE|NEGATIVE|NEUTRAL",
  "score": -1.0 to 1.0,
  "top_emotions": ["emotion1", "emotion2"],
  "complexity_score": 1-10,
  "keywords": ["word1", "word2"]
}}
"""
        try:
            import json
            response = await call_llm_with_settings(prompt, "llama-3.1-8b-instant", 0.2)
            if isinstance(response, str):
                match = re.search(r'\{.*\}', response, re.DOTALL)
                if match:
                    return json.loads(match.group(0))
            return response if isinstance(response, dict) else {}
        except Exception as e:
            print(f"[ERROR] Domain analysis failed: {e}")
            return {"domain": "GENERAL", "sentiment": "NEUTRAL", "top_emotions": ["neutral"]}

    def get_emotion_multiplier(self, emotion: str) -> Dict[str, float]:
        """
        Emotion physics constants from Blueprint Page 9.
        """
        multipliers = {
            "anger": {"beta": 1.8, "sigma": 1.5, "gamma": 0.6},
            "outrage": {"beta": 2.0, "sigma": 1.8, "gamma": 0.5},
            "fear": {"beta": 1.5, "sigma": 1.3, "gamma": 0.7},
            "disgust": {"beta": 1.4, "sigma": 1.2, "gamma": 0.8},
            "anxiety": {"beta": 1.3, "sigma": 1.1, "gamma": 0.75},
            "sadness": {"beta": 0.8, "sigma": 0.7, "gamma": 1.3},
            "amusement": {"beta": 1.6, "sigma": 1.4, "gamma": 1.1},
            "shock": {"beta": 1.7, "sigma": 1.6, "gamma": 0.9},
            "contempt": {"beta": 1.2, "sigma": 1.0, "gamma": 0.85},
            "resignation": {"beta": 0.5, "sigma": 0.4, "gamma": 1.5},
            "neutral": {"beta": 1.0, "sigma": 1.0, "gamma": 1.0}
        }
        return multipliers.get(emotion.lower(), multipliers["neutral"])
