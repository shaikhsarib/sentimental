# SentiFlow V5: Industrial Intelligence Terminal 🛡️🛰️

**SentiFlow** is a high-fidelity narrative simulation and strategic intelligence platform designed for industrial-grade risk assessment. It utilizes an **Adversarial Swarm Architecture** to ingest raw data, synthesize complex knowledge graphs, and run population-scale projections across **10,000,000 nodes**.

---

## 🏛️ Project Vision & SentiFlow Architecture

SentiFlow transforms behavioral simulation from a passive dashboard into an active intelligence engine. It is designed to detect "Agentic Drift" and "Narrative Funnels" before they manifest in real-world crises.

### The 5 intelligence Pillars
1.  **IDENTITY (Mission Ingestion)**: Ingest raw documents or OSINT URLs. Sets the Tactical Ground Truth.
2.  **INTELLIGENCE (Knowledge Extraction)**: NetworkX-powered graph synthesis. Maps the "World Model" and detects bridging nodes.
3.  **WORLD (Persona Synthesis)**: Auto-derivation of specialized AI agents. Injects "Tactical Memory" (Lessons Learned) to sharpen simulation accuracy.
4.  **SWARM (Consensus Debate)**: A 2-round adversarial debate where agents pressure-test each other's risk assessments.
5.  **DEBRIEF (Strategic Projection)**: SEIR-modeled trajectory of the narrative outbreak with an actionable mitigation playbook.

---

## 📂 Exhaustive File Structure Analysis

### 🛡️ Backend: Tactical Intelligence Engine (`/backend`)
The backend is an asynchronous Python environment built for high-performance inference and mathematical modeling.

#### Core Entry & Config
*   **`main.py`**: The central command post. Manages FastAPI routes, CORS, and dependency initialization.
*   **`requirements.txt`**: Complete dependency manifest (FastAPI, NetworkX, ChromaDB, etc.).
*   **`Procfile` / `railway.json` / `runtime.txt`**: Deployment configurations for production environments.

#### 🧠 Engines (`/backend/engines/`)
The algorithmic heart of the platform.
*   **`accuracy_engine.py`**: Validates agent responses against factual grounding.
*   **`crisis_database.py`**: Manages the local Proprietary Data Moat (SQLite + ChromaDB) containing 100+ historical crises.
*   **`graph_simulation.py`**: Implementation of the **10M-node outbreak model** (SEIR trajectory).
*   **`macro_simulation.py`**: High-level statistical projection of narrative spread.
*   **`metacognition_engine.py`**: The "Self-Correction Loop." Detects agentic drift using adversarial grading.
*   **`multi_model.py`**: Routing logic for LLMs. Assigns high-stakes roles to 70B models and generic personas to 8B models.
*   **`test_crisis.db`**: Local SQLite instance for testing database integrity.

#### ⚙️ Services (`/backend/services/`)
Data orchestration and mission persistence.
*   **`graph_store.py`**: Primary interface for **NetworkX**. Computes betweenness centrality and world cohesion.
*   **`project_store.py`**: Manages the lifecycle of Missions/Projects.
*   **`run_store.py`**: Handles the storage and retrieval of simulation results.
*   **`simulation_runner.py`**: The state machine that executes the 2-round swarm debate protocol.

#### 🧪 Hardening Suite (`/backend/tests/`)
*   **`conftest.py`**: Shared fixtures and mocked LLM/Storage environments for isolation.
*   **`test_engines.py`**: Unit tests for Metacognition, Accuracy, and Database logic.
*   **`test_services.py`**: Integration tests for Graph Building and Simulation flows.
*   **`test_api.py`**: End-to-end endpoint validation (Health, Projects, Simulation Start).
*   **`run_tests.ps1` / `test.sh`**: One-click automation scripts to run the full hardening suite.

#### 🛠️ Utilities & Support (`/backend/scripts/`, `/backend/storage/`, `/backend/training/`)
*   **`verify_v5.py`**: Automated heartbeat check for all project sub-systems.
*   **`analyze_eatlytic.py`**: Legacy cross-platform analysis script.
*   **`storage/`**: (Git Ignored) Local persistence of project-specific JSON data and OSINT uploads.

---

### 🛰️ Frontend: Industrial Workspace Terminal (`/frontend`)
A modern React 19 application built with a focus on professional, persistent workbench interaction.

#### Core UI Layer (`/frontend/src/`)
*   **`App.jsx` / `main.jsx`**: Root application routing and initialization.
*   **`store/useStore.js`**: Platform "Memory." Uses **Zustand** with `localStorage` persistence to ensure workspace continuity.
*   **`styles/index.css`**: The Industrial Design System. Defines glassmorphism, blueprint grids, and tactical color palettes.

#### 🧩 Components (`/frontend/src/components/`)
Modular UI blocks used across the workspace.
*   **`Sidebar.jsx`**: Persistent navigation for Project Meta, Run History, and Workspace modes.
*   **`WorkbenchPanel.jsx`**: Contextual right-side drawer for Node Inspection and Simulation Reporting.
*   **`DebriefReport.jsx`**: Structured strategic summary visualization.
*   **`PersonaFeed.jsx`**: Real-time ticker for live agent debate during Swarm runs.
*   **`PopulationChart.jsx`**: High-fidelity trajectory charting for the 10M node outbreak model.

#### 📄 Pages (`/frontend/src/pages/`)
*   **`OperationRoom.jsx`**: The "Three-Pane Workspace." The main operational terminal.
*   **`Dashboard.jsx`**: Mission initialization center.
*   **`Extraction.jsx`**: Dedicated view for OSINT and document ingestion.
*   **`Sandbox.jsx`**: Experimental area for persona calibration.

---

## 🚀 Operational Workflow

1.  **Initialize**: Execute `Dashboard.jsx` to create a new Mission.
2.  **Ingest**: Upload raw intelligence via `Extraction.jsx`.
3.  **Synthesize**: Use `graph_store.py` to map the world model into a Knowledge Graph.
4.  **Execute**: Ignite the `simulation_runner.py` to trigger the multi-agent Swarm debate.
5.  **Project**: Analyze the trajectory in the **Debrief Workbench**.

---

## 🛠️ Tactical Technical Stack
*   **Inference**: Groq-accelerated Llama-3 (8B/70B Multi-Pass).
*   **Graph**: NetworkX + SVG Force-Directed Layout.
*   **Memory**: ChromaDB (Vector) + SQLite (Relational) + Zustand (UI State).
*   **Hardening**: Pytest (Automated Regression Testing).

---

> [!CAUTION]
> **Data Security**: Local persistence via `backend/storage` is highly recommended for sensitive intelligence work. Ensure `.gitignore` is active for these directories.

*Sentimental V5 | SentiFlow Architecture | Mission-Ready Strategy*
