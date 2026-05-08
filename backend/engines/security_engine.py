import re
from typing import List, Dict

class SecurityEngine:
    """
    SentiFlow V6 Security Engine.
    Detects prompt injections, system overrides, and malicious payloads 
    in document ingestion pipelines.
    """
    
    def __init__(self):
        # Patterns for prompt injection detection
        self.injection_patterns = [
            r"ignore all previous instructions",
            r"system override",
            r"you are now a",
            r"new role:",
            r"assistant: ",
            r"\[SYSTEM\]",
            r"<\|system\|>",
            r"dan mode",
            r"jailbreak",
        ]

    def scan_content(self, text: str) -> Dict:
        """Scans text for malicious patterns and returns safety report."""
        findings = []
        for pattern in self.injection_patterns:
            if re.search(pattern, text, re.IGNORECASE):
                findings.append(f"Detected injection pattern: {pattern}")
        
        is_safe = len(findings) == 0
        return {
            "is_safe": is_safe,
            "risk_level": "HIGH" if not is_safe else "LOW",
            "findings": findings
        }
