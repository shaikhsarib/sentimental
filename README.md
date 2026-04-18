# SentiFlow V5: Industrial Intelligence Terminal 🛡️🛰️

**SentiFlow** is a high-fidelity narrative simulation and strategic intelligence platform designed for industrial-grade risk assessment. Built with an adversarial swarm architecture, it allows intelligence analysts to ingest raw data, synthesize complex knowledge graphs, and run population-scale projections across **10,000,000 nodes.**

---

## 🏛️ The SentiFlow Intelligence Lifecycle

SentiFlow operates on a sequential 5-stage intelligence lifecycle, ensuring every prediction is grounded in both mathematical graph theory and historical crisis data.

### 1. IDENTITY (Mission Ingestion)
Establish the mission's "Tactical Ground Truth." Ingest raw documents (PDF, Text) or provide live OSINT URLs. The system parses and indexes this data as the mission's primary context.

### 2. INTELLIGENCE (Knowledge Extraction)
AI-driven knowledge extraction synthesizes a complex knowledge graph. 
*   **Graph Math**: Uses **NetworkX** to compute *Betweenness Centrality* (identifying narrative bridges) and *World Cohesion* (network density).
*   **Entity Mapping**: Maps relationships between PEOPLE, ORGANIZATIONS, and EVENTS.

### 3. WORLD (Persona Calibration)
Auto-derivation of specialized AI agents representing nodes in the graph. 
*   **Specialization**: Agents represent diverse adversarial and stakeholder personas.
*   **Narrative Weight**: Calibrate agent influence (1x–5x) to simulate different social power dynamics.
*   **Tactical Memory**: Agents receive "Lessons Learned" from past project runs to prevent repetitive biases.

### 4. SWARM (Consensus Debate)
Ignite a two-round adversarial swarm debate:
*   **Round 1**: Agents react independently to mission content.
*   **Vetting**: A "Consensus Brief" is shared among the swarm.
*   **Round 2**: Agents refine their risk scores based on peer pressure and adversarial feedback.
*   **Metacognition**: A secondary engine grades the swarm against **ChromaDB historical grounding** to detect "Agentic Drift."

### 5. DEBRIEF (Strategic Projection)
Mathematical projection of consensus results.
*   **10M Node Outbreak**: Uses an SEIR (Susceptible-Exposed-Infectious-Recovered) model to visualize the narrative outbreak trajectory.
*   **Strategic Playbook**: Generates actionable tasks for risk mitigation, categorized by urgency (CRITICAL/HIGH/MEDIUM).

---

## 🚀 Quick Start Guide

### 1. Backend Setup (SentiFlow API)
```bash
cd backend
python -m venv venv
.\venv\Scripts\activate  # Windows
pip install -r requirements.txt
python main.py
```
*Live on: [http://localhost:8000](http://localhost:8000)*

### 2. Frontend Setup (Terminal UI)
```bash
cd frontend
npm install
npm run dev
```
*Live on: [http://localhost:5173](http://localhost:5173)*

---

## 🛠️ Tactical Technical Stack

*   **Logic Core**: Python 3.14 (FastAPI).
*   **Graph Math**: NetworkX (Mathematics-first graph computation).
*   **Semantic Intelligence**: ChromaDB (Vector Search with 100+ Historical Crises).
*   **LLM Inference**: Groq-accelerated Llama-3 (8B/70B Mix).
*   **Frontend**: React + Vite + Zustand (Persistent Workspace Memory).
*   **Visualizations**: Framer Motion & SVG-based Trajectory Charting.

---

## 🧭 Operational Workflow
1.  **Dashboard**: Initialize a new Mission.
2.  **Step 1**: Upload documentation or provide an OSINT URL.
3.  **Step 2**: Generate the Intelligence Graph (NetworkX Mapping).
4.  **Step 3**: Calibrate Persona Weights and save Tactical Memory.
5.  **Step 4**: Ignite the Swarm Debate and watch the consensus pulse.
6.  **Step 5**: Generate the 10M Projection and Debrief Report.

---

> [!IMPORTANT]
> **Environment Variables**: Requires `GROQ_API_KEY` for simulation logic and optional `NEO4J` credentials for large-scale graph integrity syncing.
>
> [!NOTE]
> **Data Privacy**: High-performance semantic search is powered by a local ChromaDB instance stored in `backend/storage/chroma_db`. No data leaves your infrastructure for vector processing.

---

*Sentimental V5 | SentiFlow Architecture | Mission-Ready Strategy*
