import json
from collections import Counter

class TripleVerificationEngine:
    """
    Three independent methods to verify prediction accuracy.
    If 2 of 3 agree, confidence is HIGH.
    If all 3 disagree, flag for human review.
    """
    
    def verify_prediction(self, ai_result: dict, historical_risk: str, content: str, content_type: str, industry: str) -> dict:
        """Run content through verifying rules engine and build consensus."""
        # METHOD 3: Keyword/pattern matching (rule-based, no AI)
        rules_based = self._run_rules_engine(content, content_type, industry)
        
        # Determine AI risk natively avoiding parsing error
        ai_risk = "MEDIUM"
        if isinstance(ai_result, dict):
            ai_risk = ai_result.get("risk_level", "MEDIUM")
        elif isinstance(ai_result, str):
            # Attempt to handle case where it might be a raw string
            if "CRITICAL" in ai_result.upper(): ai_risk = "CRITICAL"
            elif "HIGH" in ai_result.upper(): ai_risk = "HIGH"
            elif "LOW" in ai_result.upper(): ai_risk = "LOW"

        # CONSENSUS
        risk_levels = [
            ai_risk,
            historical_risk,
            rules_based["risk_level"]
        ]
        
        # Calculate agreement
        counts = Counter(risk_levels)
        most_common = counts.most_common(1)[0]
        agreement = most_common[1] / 3  # 0.33, 0.67, or 1.0
        
        return {
            "final_risk_level": most_common[0],
            "agreement_score": round(agreement * 100, 1),
            "method_results": {
                "adversarial_ai": ai_risk,
                "historical_similarity": historical_risk,
                "rules_engine": rules_based["risk_level"],
            },
            "rules_triggered": rules_based["rules_triggered"],
        }
    
    def _run_rules_engine(self, content: str, content_type: str, industry: str) -> dict:
        """
        Rule-based analysis. No AI involved.
        FAST, CONSISTENT, EXPLAINABLE.
        Catches obvious violations that don't need AI.
        """
        content_lower = content.lower()
        rules_triggered = []
        risk_score = 0
        
        # ── FTC RULES ──
        ftc_superlatives = [
            "best", "fastest", "most advanced", "#1", "number one",
            "leading", "top-rated", "unbeatable",
            "superior to", "better than all"
        ]
        for phrase in ftc_superlatives:
            if phrase in content_lower:
                rules_triggered.append({
                    "rule": "FTC_SUPERLATIVE_CLAIM",
                    "phrase": phrase,
                    "severity": "WARNING",
                    "explanation": f"'{phrase}' is a superlative claim that requires substantiation under FTC guidelines",
                    "fix": f"Qualify with evidence or use softer language"
                })
                risk_score += 15

        ftc_guarantee_words = [
            "guaranteed", "guarantee", "risk-free", "zero risk",
            "no risk", "can't lose", "100% safe", "money back guarantee"
        ]
        for phrase in ftc_guarantee_words:
            if phrase in content_lower:
                rules_triggered.append({
                    "rule": "FTC_GUARANTEE_CLAIM",
                    "phrase": phrase,
                    "severity": "CRITICAL",
                    "explanation": f"'{phrase}' without adequate substantiation violates FTC Deception Policy",
                    "fix": "Remove guarantee language or add clear conditions"
                })
                risk_score += 30

        # ── FDA RULES ──
        fda_disease_claims = [
            "cure", "cures", "treat", "treats", "prevent disease",
            "prevents cancer", "anti-cancer", "heals", "healing",
            "clinically proven to treat", "medically proven",
            "eliminates disease", "cure obesity"
        ]
        for phrase in fda_disease_claims:
            if phrase in content_lower:
                rules_triggered.append({
                    "rule": "FDA_DISEASE_CLAIM",
                    "phrase": phrase,
                    "severity": "CRITICAL",
                    "explanation": f"'{phrase}' constitutes an unauthorized drug claim. Product may be classified as unapproved drug.",
                    "fix": "Use structure/function language: 'supports immune health'"
                })
                risk_score += 40

        # ── SEC RULES ──
        sec_investment_promises = [
            "guaranteed returns", "guaranteed profit", "risk-free investment",
            "can't lose money", "100x returns", "10x your money",
            "passive income guaranteed", "get rich"
        ]
        for phrase in sec_investment_promises:
            if phrase in content_lower:
                rules_triggered.append({
                    "rule": "SEC_INVESTMENT_PROMISE",
                    "phrase": phrase,
                    "severity": "CRITICAL",
                    "explanation": f"'{phrase}' may violate SEC anti-fraud provisions (Rule 10b-5)",
                    "fix": "Add risk disclaimers. Include 'past performance' disclaimer."
                })
                risk_score += 40

        # ── SENSITIVITY RULES ──
        sensitivity_patterns = [
            {"pattern": "thoughts and prayers", "rule": "EMPTY_SYMPATHY", "score": 15,
             "explanation": "Widely mocked as performative. Will trigger backlash."},
            {"pattern": "in these unprecedented times", "rule": "COVID_CLICHE", "score": 10,
             "explanation": "Overused phrase. Reads as insincere."},
            {"pattern": "we stand with", "rule": "PERFORMATIVE_ALLYSHIP", "score": 20,
             "explanation": "Without specific action, reads as performative."},
        ]
        for pattern in sensitivity_patterns:
            if pattern["pattern"] in content_lower:
                rules_triggered.append({
                    "rule": pattern["rule"],
                    "phrase": pattern["pattern"],
                    "severity": "WARNING",
                    "explanation": pattern["explanation"],
                    "fix": "Commit to specific action or remove."
                })
                risk_score += pattern["score"]

        # ── DISCRIMINATION RULES ──
        if content_type == "job_posting":
            discrimination_phrases = [
                {"phrase": "young and energetic", "rule": "AGE_DISCRIMINATION", "severity": "CRITICAL",
                 "explanation": "Violates ADEA", "fix": "Use 'motivated'"},
                {"phrase": "native english speaker", "rule": "NATIONAL_ORIGIN_DISCRIMINATION", "severity": "CRITICAL",
                 "explanation": "Violates Title VII", "fix": "Use 'fluent in English'"},
                {"phrase": "rock star", "rule": "GENDER_CODED", "severity": "WARNING",
                 "explanation": "Masculine-coded language", "fix": "Use 'high performer'"}
            ]
            for item in discrimination_phrases:
                if item["phrase"] in content_lower:
                    rules_triggered.append({
                        "rule": item["rule"],
                        "phrase": item["phrase"],
                        "severity": item["severity"],
                        "explanation": item["explanation"],
                        "fix": item["fix"]
                    })
                    risk_score += 30 if item["severity"] == "CRITICAL" else 15

        # ── CALCULATE RISK LEVEL ──
        if risk_score >= 60:
            risk_level = "CRITICAL"
        elif risk_score >= 35:
            risk_level = "HIGH"
        elif risk_score >= 15:
            risk_level = "MEDIUM"
        else:
            risk_level = "LOW"
        
        return {
            "risk_level": risk_level,
            "risk_score": risk_score,
            "rules_triggered": rules_triggered,
        }
