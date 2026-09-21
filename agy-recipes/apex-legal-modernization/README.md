# Recipe: Apex Global Law LLP Portal Modernization (5-Act Demo)

This recipe automates the setup, step-by-step execution, and teardown of the **Apex Global Law LLP** (`https://apexgloballaw.example.com/`) modernization showcase in 5 high-impact progressive acts designed for **Marcus Vance** (Chief Innovation Officer), **Elena Rostova** (Tech Architecture Lead), and practice partners.

---

## 🎯 The 5 Demonstration Acts

| Act | Objective | Command |
| :--- | :--- | :--- |
| **Act 1: Baseline Corporate Portal** | 100% self-contained corporate baseline (`apexgloballaw.example.com` legacy monolith) with local inline assets, New York corporate branding, and synthetic authority resolution at `http://localhost:8089/`. | `python3 agy-recipes/apex-legal-modernization/scripts/demo_step1_clone.py` |
| **Act 2: UX/UI Modernization** | Desaturation of top bar and replacement with an interactive glassmorphic Mega-Menu categorizing Apex Global Law's core practices (*Banking & Finance*, *M&A & Private Equity*, *Restructuring*) alongside a live deal ticker. | `python3 agy-recipes/apex-legal-modernization/scripts/demo_step2_ux.py` |
| **Act 3: AI Feature 1 (Precedent Navigator)** | Dual-track *Search-As-You-Type*: Track A (<10ms autocomplete) + Track B grounded precedent retrieval and executive synthesis powered by **Gemini 3.8 Flash** inside a self-expanding dock (480px &rarr; 760px). | `python3 agy-recipes/apex-legal-modernization/scripts/demo_step3_ai.py` |
| **Act 4: AI Feature 2 (24/7 Apex Deal AI Advisor)** | Floating conversational deal advisor in the bottom-right corner powered by **Gemini 3.8 Flash** (`thinking_budget=0` for instant un-truncated briefs), with one-click chips for frequent queries (Delaware MAE, Schrems II, Cov-Lite). | `python3 agy-recipes/apex-legal-modernization/scripts/demo_step4_advisor.py` |
| **Act 5: AI Feature 3 (Multimodal Pre-Clearance)** | Multimodal Vision AI covenant extraction from credit agreement Term Sheets (leverage caps, negative pledge, change-of-control) and deterministic Ethical Wall conflict certification (`APEX-NY-2026-CLEARANCE-PASS`). | `python3 agy-recipes/apex-legal-modernization/scripts/demo_step5_multimodal.py` |

---

## 🏛️ Architecture & Resources

- **Master Code Location:** `semiautonomous-agents/apex-legal-portal-modernization`
- **Local Server:** `serve_portal.py` (Multi-threaded `ThreadingHTTPServer`, Port `8089`)
- **Modular Feature Injector:** `inject_feature.py`
- **LLM Synthesis Engine:**
  - `gemini-3.8-flash` (Precedent Synthesis, Deal AI Advisor & Multimodal) via Vertex AI (`vtxdemos` on `global`, 2026 Next-Gen Model Standard) with `gemini-3.1-flash-lite` & offline fallback
- **Standalone Local Authority Pages:**
  - Deep practice and precedent links (`/practices/...`, `/precedents/...`) render self-contained local authority briefs (`200 OK`, zero external network redirects, zero 404 errors).

---

## 🚀 Quick Execution Commands

```bash
# Step 1: Baseline Corporate Portal
python3 agy-recipes/apex-legal-modernization/scripts/demo_step1_clone.py

# Step 2: Modern UX/UI Deal Navigation & Mega-Menu
python3 agy-recipes/apex-legal-modernization/scripts/demo_step2_ux.py

# Step 3: Intelligent Precedent Navigator (AI Search)
python3 agy-recipes/apex-legal-modernization/scripts/demo_step3_ai.py

# Step 4: 24/7 Floating Deal AI Advisor
python3 agy-recipes/apex-legal-modernization/scripts/demo_step4_advisor.py

# Step 5: Multimodal Term Sheet Pre-Clearance
python3 agy-recipes/apex-legal-modernization/scripts/demo_step5_multimodal.py

# Teardown / Port Cleanup
python3 agy-recipes/apex-legal-modernization/scripts/teardown.py
```
