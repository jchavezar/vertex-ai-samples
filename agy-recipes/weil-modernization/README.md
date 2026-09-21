# Recipe: Weil, Gotshal & Manges LLP Modernization (5-Act Demo)

This recipe automates the setup, step-by-step execution, and teardown of the **Weil, Gotshal & Manges LLP** (`https://www.weil.com/`) modernization showcase in 5 high-impact progressive acts designed for Andrew Simon (Chief Innovation Officer), Ian Miller (Tech Architecture Lead), and Weil practice partners.

---

## 🎯 The 5 Demonstration Acts

| Act | Objective | Command |
| :--- | :--- | :--- |
| **Act 1: Faithful Baseline Clone** | 100% faithful replication of the production portal (Sitecore/jQuery monolith) with local assets, corporate New York branding, and Smart 302 Redirection at `http://localhost:8089/`. | `python3 agy-recipes/weil-modernization/scripts/demo_step1_clone.py` |
| **Act 2: UX/UI Modernization** | Desaturation of top bar and replacement with an interactive glassmorphic Mega-Menu categorizing Weil's premier practices (*Banking & Finance*, *M&A & Private Equity*, *Restructuring*) alongside a live deal ticker. | `python3 agy-recipes/weil-modernization/scripts/demo_step2_ux.py` |
| **Act 3: AI Feature 1 (Precedent Navigator)** | Dual-track *Search-As-You-Type*: Track A (<10ms autocomplete) + Track B grounded precedent retrieval and executive synthesis powered by **Gemini 3.7 Flash** inside a self-expanding dock (480px &rarr; 760px). | `python3 agy-recipes/weil-modernization/scripts/demo_step3_ai.py` |
| **Act 4: AI Feature 2 (24/7 Weil Deal AI Advisor)** | Floating conversational deal advisor in the bottom-right corner powered by **Gemini 3.7 Flash** (with `thinking_budget=0` for instant un-truncated briefs), with one-click chips for frequent queries (Delaware MAE, Schrems II, Cov-Lite). | `python3 agy-recipes/weil-modernization/scripts/demo_step4_advisor.py` |
| **Act 5: AI Feature 3 (Multimodal Pre-Clearance)** | Multimodal Vision AI covenant extraction from credit agreement Term Sheets (leverage caps, negative pledge, change-of-control) and deterministic Ethical Wall conflict certification. | `python3 agy-recipes/weil-modernization/scripts/demo_step5_multimodal.py` |

---

## 🏛️ Architecture & Resources

- **Master Code Location:** `semiautonomous-agents/weil-modernization`
- **Local Server:** `serve_weil.py` (Multi-threaded `ThreadingHTTPServer`, Port `8089`)
- **Modular Feature Injector:** `inject_feature.py`
- **LLM Synthesis Engine:**
  - `gemini-3.7-flash` (Precedent Synthesis, Deal AI Advisor & Multimodal) via Vertex AI (`vtxdemos` on `global`, compliant with strict Zero-Obsolete-Model policy)
- **Smart 302 Redirection:**
  - Any deep un-cloned links (`/people/...`, `/experience/...`) redirect transparently to `https://www.weil.com/...` to eliminate 404 errors.

---

## 🚀 Quick Execution Commands

```bash
# Step 1: Faithful Baseline Clone
python3 agy-recipes/weil-modernization/scripts/demo_step1_clone.py

# Step 2: Modern UX/UI Deal Navigation & Mega-Menu
python3 agy-recipes/weil-modernization/scripts/demo_step2_ux.py

# Step 3: Intelligent Precedent Navigator (AI Search)
python3 agy-recipes/weil-modernization/scripts/demo_step3_ai.py

# Step 4: 24/7 Floating Deal AI Advisor
python3 agy-recipes/weil-modernization/scripts/demo_step4_advisor.py

# Step 5: Multimodal Term Sheet Pre-Clearance
python3 agy-recipes/weil-modernization/scripts/demo_step5_multimodal.py

# Teardown / Port Cleanup
python3 agy-recipes/weil-modernization/scripts/teardown.py
```
