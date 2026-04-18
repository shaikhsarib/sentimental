# Sentimental V5: Industrial Intelligence Terminal 🛡️

**Sentimental** is a high-fidelity narrative simulation and strategic intelligence platform. Built with the **MiroFlow** logic, it allows you to ingest raw data, synthesize knowledge graphs, and run "Adversarial Swarm Debates" to predict how a narrative will outbreak across a population of **10,000,000 nodes.**

---

## 🏛️ The V5 "MiroFlow" Architecture

Sentimental operates on a sequential 5-stage intelligence lifecycle:

1.  **IDENTITY (Mission Ingestion)**: Ingest raw documents, PDFs, or live OSINT URLs to establish the mission's ground truth.
2.  **INTELLIGENCE (Knowledge Extraction)**: AI extracts a complex knowledge graph (PEOPLE, ORGS, EVENTS) to map the narrative landscape.
3.  **WORLD (Persona Calibration)**: The system synthesizes 10-30+ specialized AI personas derived from the graph. You calibrate their "Narrative Weight" before the simulation.
4.  **SWARM (Consensus Debate)**: Agents enter a two-round debate protocol. They react independently, share consensus, and refine their risk predictions in real-time.
5.  **DEBRIEF (Massive Projection)**: The swarm consensus is mathematically projected across 10 million nodes, providing viral trajectory charts and mitigation playbooks.

---

## 🚀 Quick Start Guide

### 1. Backend Setup
```bash
cd backend
python -m venv venv
.\venv\Scripts\activate  # Windows
pip install -r requirements.txt
python main.py
```
*Live on: http://localhost:8000*

### 2. Frontend Setup
```bash
cd frontend
npm install
npm run dev
```
*Live on: http://localhost:5173*

---

## 🛠️ Tactical Features
- **Swarm Debate Protocol**: Multi-agent reasoning for hyper-accurate risk synthesis.
- **Massive 10M Projection**: SEIR mathematical modeling of narrative outbreaks.
- **Neural Command Map**: Interactive, heat-mapped 2D graph with selective label clarity.
- **OSINT Ingestion**: Direct URL intelligence gathering.
- **Blueprint UI**: Pure-white "Scientific" aesthetic with industrial minimalist design.

---

## 🧭 Operational Workflow
1.  **Dashboard**: Create a new Mission.
2.  **Step 1**: Upload a document or provide a URL.
3.  **Step 2**: Click "GENERATE_INTELLIGENCE_GRAPH."
4.  **Step 3**: Calibrate agent weights and select a Scenario Template.
5.  **Step 4**: Launch the **SWARM** and watch the Command Map pulse.
6.  **Step 5**: Click "GENERATE_MISSION_INTELLIGENCE" for the 10M projection and strategic debrief.

---

> [!IMPORTANT]
> **Environment Variables**: Requires `GROQ_API_KEY` for LLM inference and optional `NEO4J` credentials for large-scale graph persistence.
