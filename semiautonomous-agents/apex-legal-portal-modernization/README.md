# Apex Global Law LLP — 5-Act Corporate Portal Modernization

> **Presenter / Google Cloud Lead**: Jesus Chavez (Customer Engineer, AI)  
> **Port**: `8089` (`http://localhost:8089/`)  
> **Foundation Model**: `gemini-3.8-flash` on Vertex AI (`location="global"`, 2026 Next-Gen Model Standard)

---

## 📌 Overview

This directory contains the 100% self-contained, offline-capable 5-Act progressive modernization showcase for **Apex Global Law LLP** (`https://apexgloballaw.example.com/`), transforming a traditional enterprise corporate law monolith into a real-time **Legal Deal & Regulatory Intelligence Cockpit**.

---

## 🎯 The 5 Demonstration Acts

| Act | Feature Injected | Command |
| :--- | :--- | :--- |
| **Act 1** | **Baseline Corporate Portal** (`apexgloballaw.example.com` synthetic legacy monolith with local inline assets & zero external links) | `python3 inject_feature.py reset` |
| **Act 2** | **UX/UI Deal Cockpit** (Glassmorphic Mega-Menu across Banking & Finance, M&A/PE, Restructuring + Live Deal Ticker) | `python3 inject_feature.py inject modern_header_ux` |
| **Act 3** | **AI Feature 1: Precedent Navigator** (<10ms Search-As-You-Type + dynamic `480px -> 760px` dock with live `gemini-3.8-flash` synthesis) | `python3 inject_feature.py inject modern_header_ai` |
| **Act 4** | **AI Feature 2: 24/7 Apex Deal AI Advisor** (Floating conversational deal advisor with instant Delaware MAE, Schrems II & Cov-Lite chips) | `python3 inject_feature.py inject ai_advisor` |
| **Act 5** | **AI Feature 3: Multimodal Term Sheet Pre-Clearance** (Laser scan covenant extraction & deterministic Ethical Wall clearance token) | `python3 inject_feature.py inject ai_multimodal_deal` |

---

## 🛠️ Building & Running From Scratch

### 1. Prerequisites

- Python `3.11+`
- Google Cloud SDK authenticated with Vertex AI permissions (optional — graceful offline fallback is built in):
  ```bash
  gcloud auth application-default login
  gcloud config set project vtxdemos
  ```

### 2. Reset Baseline Portal (Optional — `./site/index.html` is pre-populated)

```bash
cd semiautonomous-agents/apex-legal-portal-modernization
python3 inject_feature.py reset
```

### 3. Launch the Multi-Threaded Portal Server (Port `8089`)

```bash
cd semiautonomous-agents/apex-legal-portal-modernization
python3 serve_portal.py
```

### 4. API Endpoints Served by `serve_portal.py`

- `GET /api/suggest?q=<term>`: Sub-10ms autocomplete across Apex Global Law practice groups and representative mandates.
- `GET|POST /api/search`: Grounded precedent synthesis via `gemini-3.8-flash` (`location="global"`).
- `POST /api/advisor`: 24/7 Apex Deal Intelligence AI Advisor (`gemini-3.8-flash` for sub-1.5s responses).
- `POST /api/multimodal-deal`: Credit agreement covenant extraction & Ethical Wall verification token (`APEX-NY-2026-CLEARANCE-PASS`).
- `GET /practices/<slug>` & `GET /precedents/<slug>`: Self-contained synthetic authority briefs (zero external redirects, zero 404s).

For the full presenter script and talking points, see **[JETSKI_DEMO_SCRIPT.md](JETSKI_DEMO_SCRIPT.md)**.
