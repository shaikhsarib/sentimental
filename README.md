# SentiFlow V5: Industrial Intelligence Terminal 🛡️🛰️

**SentiFlow** is a high-fidelity narrative simulation and strategic intelligence platform designed for industrial-grade risk assessment. Built with an **Adversarial Swarm Architecture**, it allows intelligence analysts to quantify risk using the **Narrative R0 Index** and run population-scale projections across **10,000,000 nodes.**

---

## 🏛️ The "Trust Moat": Silent Consensus Protocol (SCP)

Unlike generic AI tools that hallucinate a prediction for every prompt, SentiFlow implements the **Silent Consensus Protocol**. 

If the internal agent swarm (Experts vs. Population) fails to reach a validated confidence threshold (0.78 agreement), the system **refuses to predict**. Instead, it outputs a **Strategic Stalemate Report**, identifying specific "Intelligence Gaps" that must be filled to achieve certainty. This "Refusal-as-a-Feature" is what makes SentiFlow industrial-grade.

---

## 🛠️ Tactical Technical Stack

*   **Intelligence Core**: Python 3.14 (FastAPI) + **70B Expert Routing**.
*   **Consensus Engine**: SCP-validated variance detection and bimodal clustering.
*   **Epidemiological Moat**: **SEIR-Kinetics** model for 10M-node population projection.
*   **Semantic Memory**: ChromaDB (Vector Search) + **Moat Fuel** (20+ Seeded Historical Crises).
*   **Infrastructure**: Dockerized, Rate-Limited, and Security-Sanitized.

---

## 📂 Repository Architecture (V5 Update)

### 🛡️ Backend: Tactical Intelligence Engine (`/backend`)

#### 🧠 V5 Engines (`/backend/engines/`)
*   **`consensus_engine.py`**: [NEW] Implements the Silent Consensus Protocol.
*   **`taxonomy.yaml`**: [NEW] Dynamic tiered agent configuration (Experts/Population/Validators).
*   **`crisis_database.py`**: Grounding engine with 20+ historical crisis "Memories".
*   **`graph_simulation.py`**: Upgraded SEIR model with sentiment-modulated kinetics.
*   **`multi_model.py`**: 70B Expert routing logic via Groq Llama-3.3.

#### 🧪 Validation Suite (`/backend/`)
*   **`validate_accuracy.py`**: [NEW] Automated benchmark harness to prove prediction accuracy.
*   **`seed_moat.py`**: [NEW] Bulk-seeder for historical data injection.

### 🛰️ Frontend: Industrial Workspace Terminal (`/frontend`)

#### 🧩 V5 Components (`/frontend/src/components/`)
*   **`ConsensusRefused.jsx`**: [NEW] "War Room" UI for handling high-uncertainty states.
*   **`PopulationChart.jsx`**: [UPGRADED] Real-time SEIR kinetics visualization.
*   **`DebriefReport.jsx`**: Integrated SCP verdict tracking and risk scorecard.

---

## 🚀 Quick Start (V5 Runtime)

### 1. Initialize the Moat (One-time)
```powershell
cd backend
python seed_moat.py
```

### 2. Start the Terminal
**Terminal A (Backend):**
```powershell
cd backend
python main.py
```

**Terminal B (Frontend):**
```powershell
cd frontend
npm run dev
```

### 3. Run Validation
To generate your first Strategic Accuracy Report:
```powershell
cd backend
python validate_accuracy.py
```

---

## 🛡️ Security Posture
SentiFlow V5 includes production-grade defenses:
- **Rate Limiting**: RPM/Burst management to prevent API abuse.
- **Input Sanitization**: Mandatory truncation and null-byte removal for all ingestion.
- **Request Size Capping**: Rejection of oversized payloads to prevent resource exhaustion.
- **CORS Lockdown**: Strict origin white-listing for enterprise environments.

---

**Built for the next generation of Crisis Intelligence.** 🚀
