# SentiFlow V6 Reproduction Guide

This document provides exact instructions to replicate the SentiFlow V6 "Million-Agent" simulations.

## 💻 Hardware Requirements
- **OS**: Windows / Linux / macOS
- **CPU**: 4+ Cores (for sharding parallelism)
- **RAM**: 8GB+ (for 1M agent metadata storage)
- **Disk**: 500MB (for local vector and relational databases)

## 🔑 External Dependencies
- **Groq API Key**: Required for 70B Arbiter and Representative reasoning.
- **Python 3.10+**: Core runtime.

## 🛠️ Step-by-Step Replication

### 1. Environment Setup
```bash
git clone https://github.com/shaikhsarib/sentimental
cd sentimental
pip install -r backend/requirements.txt
```

### 2. Configuration
Create a `.env` file in the `backend/` directory:
```env
GROQ_API_KEY=your_key_here
MAX_CONCURRENT_LLM_CALLS=2
```

### 3. Execution
To reproduce the 'Million-Agent' simulation results:
```bash
python backend/test_v6_e2e.py
```

## 💰 API Cost Projection (Groq)
- **Mass Layer (Statistical Abstraction)**: ~100 LLM calls (Archetype reasoning).
- **Representative Layer**: ~100 LLM calls (High-fidelity sample).
- **Arbiter Layer**: 1 LLM call (Deep synthesis).
- **Total Cost per Project**: ~$0.05 - $0.20 (depending on Groq token pricing).

---
**Note**: The "1 Million Agents" claim is supported via Statistical Projection across Archetype DNA, ensuring computational feasibility without compromising narrative depth.
