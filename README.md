# SentiFlow V5: Industrial Intelligence Terminal 🛡️🛰️

**SentiFlow** is a high-fidelity narrative simulation and strategic intelligence platform designed for industrial-grade risk assessment. Built with an **Adversarial Swarm Architecture**, it allows intelligence analysts to ingest raw data, synthesize complex knowledge graphs, and run population-scale projections across **10,000,000 nodes.**

---

## 🏛️ Project Vision & SentiFlow Architecture

SentiFlow transforms behavioral simulation from a passive dashboard into an active intelligence engine. It is designed to detect "Agentic Drift" and "Narrative Funnels" before they manifest in real-world crises.

### The Intelligence Lifecycle
The platform follows a strict 5-stage pipeline to ensure grounded, verifiable results:

1.  **IDENTITY (Mission Ingestion)**: Ingest raw docs/URLs. Sets the Tactical Ground Truth.
2.  **INTELLIGENCE (Knowledge Extraction)**: NetworkX-powered graph synthesis. Detects bridging nodes and world cohesion.
3.  **WORLD (Persona Synthesis)**: Auto-derivation of specialized AI agents. Injects "Tactical Memory" (Lessons Learned) to sharpen simulation accuracy over time.
4.  **SWARM (Consensus Debate)**: A 2-round adversarial debate where agents pressure-test each other's risk assessments.
5.  **DEBRIEF (Strategic Projection)**: SEIR-modeled trajectory of the narrative outbreak with an actionable mitigation playbook.

---

## 📂 Repository Architecture & File Structure

SentiFlow V5 is organized into a decoupled full-stack environment.

### 🛡️ Backend: Tactical Intelligence Engine (`/backend`)
*   **`main.py`**: Command post for FastAPI routes and system initialization.
*   **`engines/`**: The algorithmic logic core.
    *   `metacognition_engine.py`: Self-correction logic that grades swarm performance.
    *   `crisis_database.py`: Vector-search (ChromaDB) access to 100+ historical crises.
    *   `multi_model.py`: Orchestrates Grover-accelerated LLM routing (8B/70B models).
    *   `graph_simulation.py`: Math-heavy population projection logic.
*   **`services/`**: Orchestration and state management.
    *   `simulation_runner.py`: The simulation state machine (Shield/Macro modes).
    *   `graph_store.py`: NetworkX-based graph storage and metric computation.
    *   `project_store.py` / `run_store.py`: Persistent storage handlers.
*   **`tests/`**: The Hardening Suite.
    *   `test_engines.py`: Validates accuracy and metacognition logic.
    *   `test_api.py`: Validates endpoint security and input constraints.
*   **`run_tests.ps1` / `test.sh`**: One-click test runners for Windows and Bash.

### 🛰️ Frontend: High-Fidelity Workspace (`/frontend`)
*   **`src/store/useStore.js`**: Zustand persistent state. Survives refreshes.
*   **`src/components/`**: Modular Workspace Atoms.
    *   `Sidebar.jsx`: Unified project navigation and mission history.
    *   `WorkbenchPanel.jsx`: Contextual inspector for nodes, persona feeds, and reports.
*   **`src/pages/`**: Main Terminal Views.
    *   `OperationRoom.jsx`: The Three-Pane mission workbench.
    *   `Dashboard.jsx`: Home base for mission initialization.
*   **`src/styles/index.css`**: Industrial-grade CSS with custom design tokens.

---

## 🛠️ Technical Stack

*   **Logic Core**: Python 3.14 (FastAPI).
*   **Graph Math**: NetworkX (Mathematics-first graph computation).
*   **Semantic Intelligence**: ChromaDB (Vector Search with 100+ Historical Crises).
*   **LLM Inference**: Groq-accelerated Llama-3 (8B/70B Mixed Precision).
*   **Frontend**: React 19 + Vite 8 + Zustand (Persistent Workspace Memory).
*   **Testing**: Pytest (Full Backend Coverage).

---

## 🚀 Quick Start

### 1. Backend
```bash
cd backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python main.py
```

### 2. Frontend
```bash
cd frontend
npm install
npm run dev
```

---

> [!IMPORTANT]
> **Environment Variables**: Ensure `GROQ_API_KEY` is set in your `.env` file for simulation logic to function.
>
> [!TIP]
> **Industrial Hardening**: Run `./backend/run_tests.ps1` before any major deployment to ensure 100% logic integrity.

---

*Sentimental V5 | SentiFlow Architecture | Mission-Ready Strategy*
