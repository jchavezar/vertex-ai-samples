# Weil, Gotshal & Manges LLP — 5-Act Corporate Portal Modernization

> **Presenter / Google Cloud Lead**: Jesus Chavez (Customer Engineer, AI)  
> **Port**: `8089` (`http://localhost:8089/`)  
> **Foundation Model**: `gemini-3.7-flash` on Vertex AI (Strict Zero-Obsolete-Model Policy)

---

## 📌 Overview

This directory contains the 5-Act progressive modernization showcase for **Weil, Gotshal & Manges LLP** (`https://www.weil.com/`), transforming a traditional Sitecore / jQuery web monolith into a real-time **Legal Deal & Regulatory Intelligence Cockpit**.

---

## 🎯 The 5 Demonstration Acts

| Act | Feature Injected | Command |
| :--- | :--- | :--- |
| **Act 1** | **Faithful Baseline Clone** (`weil.com` Sitecore/jQuery monolith with local assets & Smart 302 Redirection) | `python3 inject_feature.py reset` |
| **Act 2** | **UX/UI Deal Cockpit** (Glassmorphic Mega-Menu across Banking & Finance, M&A/PE, Restructuring + Live Deal Ticker) | `python3 inject_feature.py inject modern_header_ux` |
| **Act 3** | **AI Feature 1: Precedent Navigator** (<10ms Search-As-You-Type + dynamic `480px → 760px` dock with live `gemini-3.7-flash` synthesis) | `python3 inject_feature.py inject modern_header_ai` |
| **Act 4** | **AI Feature 2: 24/7 Weil Deal AI Advisor** (Floating conversational deal advisor with instant Delaware MAE, Schrems II & Cov-Lite chips) | `python3 inject_feature.py inject ai_advisor` |
| **Act 5** | **AI Feature 3: Multimodal Term Sheet Pre-Clearance** (Laser scan covenant extraction & deterministic Ethical Wall clearance token) | `python3 inject_feature.py inject ai_multimodal_deal` |

---

## 🛠️ Building & Running From Scratch

### 1. Prerequisites

- Python `3.11+`
- Google Cloud SDK authenticated with Vertex AI permissions:
  ```bash
  gcloud auth application-default login
  gcloud config set project vtxdemos
  ```

### 2. Re-Clone Baseline Assets (Optional — `./site` is already included)

If building from a completely clean state without `./site`:

```bash
cd semiautonomous-agents/weil-modernization
python3 clone_weil.py
```

### 3. Launch the Multi-Threaded Portal Server (Port `8089`)

```bash
cd semiautonomous-agents/weil-modernization
python3 serve_weil.py
```

### 4. API Endpoints Served by `serve_weil.py`

- `GET /api/suggest?q=<term>`: Sub-10ms autocomplete across Weil practice groups and landmark deals.
- `GET /api/search?q=<query>`: Grounded precedent synthesis via `gemini-3.7-flash`.
- `POST /api/advisor`: 24/7 Weil Deal Intelligence AI Advisor (`thinking_budget=0` for sub-1.5s responses).
- `POST /api/multimodal-deal`: Credit agreement covenant extraction & Ethical Wall verification token (`WEIL-NY-2026-APEX-CLEARANCE-PASS`).

For the full presenter script and talking points, see **[JETSKI_DEMO_SCRIPT.md](JETSKI_DEMO_SCRIPT.md)**.
