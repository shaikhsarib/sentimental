import asyncio
import json
import os
import sys
from dotenv import load_dotenv

# Add the backend and engines directory to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from engines.crisis_database import CrisisDatabase
from engines.accuracy_engine import TripleVerificationEngine
from engines.multi_model import run_all_personas
from engines.graph_simulation import GraphSimulation
from engines.macro_simulation import MacroSimulationEngine

load_dotenv()

async def run_analysis():
    content = """Eatlytic is a high-fidelity, AI-powered food intelligence platform designed to decode complex nutrition labels and expose misleading marketing claims. It is specifically engineered for the Indian market to address metabolic health by providing transparency through "Food Intelligence."

1. Core Mission & Philosophy
Transparency: It aims to strip away marketing "lies" (e.g., flagging hidden sugars like Maltodextrin in "Sugar-Free" products) to reveal a product's true health impact.
High-Fidelity Extraction: Built on the "Blind Photocopier" principle, ensuring 100% data extraction accuracy from labels before any health rules are applied.
Indian-First Design: Specifically optimized to handle the unique dietary patterns and diverse scripts (English, Hindi, Tamil) found in India.
2. Key Features
AI Health Scoring: Provides a 1-10 health score and a clear verdict tailored to specific Health Personas (e.g., Diabetic Care, Pregnancy Safe, Child Safety, Athletes).
NOVA Classification: Categorizes foods (NOVA 1-4) to explicitly flag Ultra-Processed Foods (UPF).
Marketing Lie Detector: Automatically identifies and warns against deceptive claims common on industrial food packaging.
Voice Logging: Allows users to log meals naturally via speech (e.g., "two scrambled eggs and toast").
Reporting: Generates professional PDF health reports and Shareable Social Media Cards for Instagram and WhatsApp.
3. Technical Architecture
Vision Pipeline: Uses OpenCV for advanced image enhancement (deblurring/denoising) and EasyOCR for script-aware text extraction.
AI Intelligence: Powered by Llama 3.3 (70B) via Groq for near-instant semantic analysis and ingredient risk assessment.
Backend: A high-performance FastAPI (Python) infrastructure, containerized with Docker for zero-cold-start responsiveness.
Ecosystem: Seamlessly integrated with WhatsApp for mobile-first utility, while offering a B2B API for enterprise-scale food analysis.
4. User Experience
The application features a premium, interactive web interface using modern design principles (Glassmorphism, dynamic animations) and high-quality fonts like Fraunces and Nunito. It includes real-time camera quality feedback, AR-style scanning reticles, and clear interactive "Score Orbs" for simplified data visualization."""

    # 1. SHIELD MODE ANALYSIS
    verifier = TripleVerificationEngine()
    rules_result = verifier._run_rules_engine(content, "product_manual", "health_tech")

    # 2. SEIR GRAPH CASCADE
    graph_sim = GraphSimulation(population=10000000)
    # We estimate virality risk based on rules
    v_risk = 4 if rules_result['risk_level'] == 'LOW' else 8
    cascade = graph_sim.simulate_cascade(max_virality_score=v_risk)

    # 3. MACRO TIME-SKIP
    macro_sim = MacroSimulationEngine()
    try:
        # Note: This is an async call to the LLM agent
        macro_outcomes = await macro_sim.run_time_skip_simulation(content)
    except Exception as e:
        macro_outcomes = {"error": str(e)}

    report = {
        "target": "Eatlytic Platform Overview",
        "risk_assessment": rules_result,
        "market_explosion_projection": cascade,
        "future_macro_timelines": macro_outcomes
    }

    print(json.dumps(report, indent=4))

if __name__ == "__main__":
    asyncio.run(run_analysis())
