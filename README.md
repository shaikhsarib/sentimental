# SentiFlow V6: Institutional Intelligence Terminal 🛡️🛰️
### The World's First Million-Agent Narrative Contagion Platform

**SentiFlow V6** is a high-fidelity narrative simulation and strategic intelligence platform designed for institutional-grade risk assessment. It marks a fundamental leap from persona-based analysis to **Massive-Scale Synthetic Population Simulation.**

> [!IMPORTANT]
> **V6 UPGRADE COMPLETE.** The platform now supports document-grounded entity extraction, million-agent swarm generation, and multi-perspective strategic synthesis.

---

## 🏛️ V6 Institutional Architecture

### 1. Million-Agent Swarm Factory
Every noun phrase in an uploaded document (PDF/TXT/MD) becomes an agent candidate. 
- **Entity DNA Extraction**: NER + pattern matching identifies real-world entities.
- **Synthetic Multiplier**: 100 entities → 1,000,000+ agents with unique skills and training.

### 2. Hierarchical Consensus Protocol (HCP)
V6 replaces simple voting with a three-layer weighted protocol (Blueprint Page 17):
- **Mass Layer (0.2)**: Statistical aggregation of 1M+ agent analyses.
- **Representative Layer (0.3)**: 100-500 stratified agents reason in detail.
- **Arbiter Layer (0.5)**: A 70B "Synthesis Judge" performs final adversarial arbitration.

### 3. Emotion Physics & SEIR-Kinetics
Narrative contagion is now governed by physical properties (Blueprint Page 32):
- **Anger**: 1.8x infection rate, 0.6x recovery (spreads fast, lingers).
- **Fear**: 1.4x infection rate, 1.1x recovery (spikes fast, fades fast).
- **Sadness**: 0.8x infection rate (slow spread).

### 4. Perspective Synthesis Gateway
Post-simulation, stakeholders can query the collective swarm through 6 specialized lenses:
- **Businessman** (ROI/Moat) // **Investor** (TAM/Exit) // **Engineer** (Scale/Feasibility)
- **Policy Maker** (Regulation) // **Student** (Accessibility) // **Academic** (Rigor)

---

## 🛠️ Technical Implementation (V6)

### 🧠 Core Engines (`/backend/engines/`)
- **`agent_factory.py`**: [NEW] High-scale synthetic persona generator.
- **`v6_graph_builder.py`**: [NEW] Constructs influence networks based on agent hierarchy.
- **`cascade_simulator.py`**: [NEW] Runs the Emotion Physics SEIR model on agent graphs.
- **`query_engine.py`**: [NEW] Multi-perspective strategic synthesis engine.
- **`sentimental_db.py`**: [NEW] SQLite V6 Schema with WAL mode for concurrency.

### 📂 Repository Architecture

#### Backend: Tactical Intelligence Engine (`/backend`)
*   **`main.py`**: Upgraded with V6 Institutional endpoints.
*   **`services/export_service.py`**: [NEW] Generates Institutional Strategic Briefs (PDF).

#### Frontend: Industrial Workspace Terminal (`/frontend`)
*   **`pages/V6Upload.jsx`**: Document-to-Entity extraction dashboard.
*   **`pages/V6Debate.jsx`**: Operation Room for Hierarchical Consensus visualization.
*   **`pages/V6Query.jsx`**: Perspective-aware Swarm Intelligence Gateway.

---

## 🚀 Quick Start (V6 Institutional)

### 1. Initialize the Environment
Ensure your `.env` contains a valid `GROQ_API_KEY`.

### 2. Launch the Platform
**Backend:**
```powershell
cd backend
python main.py
```

**Frontend:**
```powershell
cd frontend
npm run dev
```

### 3. Run V6 Verification
To verify the million-agent factory and emotion physics:
```powershell
python backend/test_v6_graph_cascade.py
```

---

## 🛡️ Security Posture
SentiFlow V6 maintains production-grade defenses:
- **Rate Limiting**: RPM/Burst management via `llm_semaphore`.
- **Input Sanitization**: Mandatory truncation and sanitization for all ingestion.
- **CORS Lockdown**: Strict origin white-listing (ports 5173/5174).

---

**Built for the next generation of Crisis Intelligence.** 🚀
