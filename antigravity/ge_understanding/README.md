<div align="center">
  <img src="https://capsule-render.vercel.app/api?type=waving&color=0f172a&height=200&section=header&text=GE%20UNDERSTANDING&fontSize=60&fontAlignY=38&desc=Insight%20Engine&descAlignY=58&descAlign=62" width="100%" alt="HEADER" />
</div>

<br/>

<div align="center">
  <h3>SYSTEM STATUS: <strong>ONLINE</strong> // SECURITY_LEVEL: <strong>SIGMA</strong></h3>
  <p>
    <em>A powerful system for reasoning over enterprise knowledge bases and extracting actionable insights.</em>
  </p>
</div>

<br/>

## 🪐 ARCHITECTURE & SPECS

> **Core Engine:** FastAPI (Backend) | React, Vite, TS (Frontend)

This module handles complex queries against structured and unstructured datastores.

```mermaid
graph TD
    User([User]) -->|Interacts| UI[Frontend: React/Vite]
    UI -->|API Requests| API[Backend: FastAPI]
    API -->|LLM Reasoning| Model[Google Gemini Pro]
    Model -->|Search/Retrieval| DB[(Vector Datastore)]
```

## 📂 PROJECT STRUCTURE

```text
ge_understanding/
├── backend/            # FastAPI Backend & LLM Routing (Python, uv)
├── frontend/           # Modern React/Vite User Interface
├── docs/               # Architecture diagrams and documentation
└── README.md           # This file
```

## 🚀 QUICK START GUIDE

### 1. Backend Ignition

The backend leverages `uv` for ultra-fast dependency management.

```bash
cd ge_understanding/backend
uv sync
uv run main.py
```

### 2. Frontend Launch

The frontend operates on Vite for HMR and rapid development.

```bash
cd ge_understanding/frontend
npm install
npm run dev
```

## 🛡️ SECURITY PROTOCOLS

- **Zero-Leak Compliant:** `.env` structures are sealed and isolated.
- **Identity:** Authenticated operations only.

<br/>

<div align="center">
  <img src="https://capsule-render.vercel.app/api?type=waving&color=0f172a&height=100&section=footer" width="100%" />
  <p>POWERED_BY: <strong>GEMINI_2.5_PRO</strong> // ARCHITECTURE: <strong>NEO_MONOLITH</strong></p>
</div>
