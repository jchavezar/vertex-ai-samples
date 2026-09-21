"""
Weil, Gotshal & Manges LLP — Centralized Google Cloud Firestore MemoryBank Ingestion
====================================================================================
Harvests EVERY detail, stakeholder note, architectural decision, 5-step walkthrough
script, 5-act website modernization recipe, documentation file, and ALL cross-session
Jetski conversation transcripts into Google Cloud Firestore (`project="vtxdemos"`).

Collections populated in Firestore (`vtxdemos`):
  1. `weil_memory_bank`       — Granular RAG knowledge & conversation documents with
                                 768-dim `text-embedding-005` vector embeddings.
  2. `weil_sessions_registry` — Master registry of all Jetski conversation sessions
                                 involving Weil, Gotshal & Manges LLP.
"""

import os
import re
import json
import hashlib
from datetime import datetime, timezone
from typing import List, Dict, Any

from google.cloud import firestore
from google import genai
from google.genai import types

os.environ["GOOGLE_CLOUD_PROJECT"] = "vtxdemos"
os.environ["GOOGLE_CLOUD_LOCATION"] = "us-central1"
os.environ["GOOGLE_API_USE_CLIENT_CERTIFICATE"] = "false"
os.environ["GOOGLE_API_USE_MTLS_ENDPOINT"] = "never"

PROJECT_ID = "vtxdemos"
MEMORY_COLLECTION = "weil_memory_bank"
SESSIONS_COLLECTION = "weil_sessions_registry"
EMBEDDING_MODEL = "text-embedding-005"

SHOWCASE_ROOT = "/Users/jesusarguelles/IdeaProjects/vertex-ai-samples/semiautonomous-agents/weil-legal-agentic-showcase"
MODERNIZATION_ROOT = "/Users/jesusarguelles/IdeaProjects/vertex-ai-samples/semiautonomous-agents/weil-modernization"
RECIPE_ROOT = "/Users/jesusarguelles/IdeaProjects/vertex-ai-samples/agy-recipes/weil-modernization"
BRAIN_ROOT = "/Users/jesusarguelles/.gemini/jetski/brain"

WEIL_CONVERSATION_IDS = [
    "3a7bfad2-cdd6-4ac0-b3f7-2f5b2492f0dd",
    "0e811986-eb3c-45b4-9c70-ce836c1ffa7d",
    "006dd831-19d4-482a-9eed-9588d8eef612",
    "2f29bcd8-6578-4a2f-89eb-cd0feee52192",
    "95f2e256-4713-4bfd-a63b-0c12d9ffd016",
    "da963b94-6ca7-43ff-a3cf-f4e098456c5a",
    "c5b3b672-774f-4b43-9faf-02b8df0b63b6",
    "4bb3c7a1-9007-49e1-a5d3-4aeb7f5def82",
    "5a619144-bf76-4065-9230-a82577c02dd6",
    "0e98ba3b-dea1-495a-8d5e-0e633eb831e3",
]


def get_master_curated_dossiers() -> List[Dict[str, Any]]:
    """
    Returns exhaustive, high-precision master dossiers covering every facet of the
    Weil, Gotshal & Manges LLP engagement ("details over the details").
    """
    return [
        {
            "doc_id": "master-01-engagement-overview-and-stakeholders",
            "title": "Weil, Gotshal & Manges LLP — Executive Engagement Overview & Stakeholder Map",
            "category": "executive_context_and_stakeholders",
            "source_type": "curated_master_dossier",
            "tags": ["weil", "stakeholders", "andrew simon", "ian miller", "ravi", "jesus chavez", "ebc", "workshop"],
            "content": (
                "CUSTOMER: Weil, Gotshal & Manges LLP ('Weil', https://www.weil.com/), elite global law firm headquartered in New York.\n"
                "ENGAGEMENT PURPOSE: Executive Briefing Center (EBC) & GCP Legal-Tech Innovation Workshop at Google Cloud Campus (California), "
                "evaluating Google Cloud AI architecture to modernize high-stakes corporate legal workflows (M&A due diligence, Private Equity, "
                "Restructuring, Banking & Finance, Antitrust, Tax), consolidate '45,000 fragmented legal surfaces' (iManage DMS, Harvey, Thomson Reuters, "
                "Westlaw, custom Azure tools) into a single-pane-of-glass Agentic Cockpit, and establish deterministic multi-agent orchestration.\n"
                "KEY WEIL STAKEHOLDERS:\n"
                "1. Andrew Simon — Chief Innovation Officer (CIO) / Head of Tech Strategy. Champion of the 'Privacy Pro' modular contract assembly "
                "('Legal Legos') concept and evaluating agent harnesses outside Antigravity (specifically Google ADK state management, callbacks, and evals). "
                "Also focused on open-weight frozen models (Gemma 2/4) for routine 'tissue paper applications' (e.g., German Power of Attorney generation) vs. "
                "frontier Gemini models for complex multi-step legal synthesis.\n"
                "2. Ian Miller — Head of Technology Architecture. Focused on enterprise architecture, open Model Context Protocol (MCP) gateways over "
                "existing iManage/Relativity/Azure repositories without creating new silos, and deterministic Chinese Wall / Ethical Wall scrubbing BEFORE "
                "any adverse client data reaches an LLM prompt.\n"
                "3. Steve Kedem — Legal Technology & Practice Innovation Lead (participated in the August 27, 2026 preparatory architecture alignment).\n"
                "4. Daulton Cockerell — Legal Technology & Engineering Lead (participated in the August 27, 2026 preparatory alignment).\n"
                "5. Ravi — Executive Sponsor / C-Suite Leadership (leads the 2:00 PM Executive Briefing session on C-suite partnership and roadmap commitment).\n"
                "KEY GOOGLE CLOUD TEAM & OWNERSHIP:\n"
                "1. Jesus Chavez — Customer Engineer, AI (Lead presenter & architect for Session 3 'Agentic Architecture, Orchestration & Harness', "
                "Session 4 'Unified AI Experience & Interface Consolidation', the 5-Step ADK/MCP/Agent Runtime/Eval/A2A Curriculum, and the 5-Act Portal Demo).\n"
                "2. Roberto Santana — Product Manager Lead, Vertex AI Embeddings (Lead for Session 2 'Advanced Legal Data Layer & Hybrid Retrieval': "
                "dense vector stores `gemini-embedding-2` / `text-embedding-005` + sparse BM25 + ethical wall rerank filtering).\n"
                "3. Sofi Mehta & Brian Squibb — Account & Discovery Leads (Session 1 Customer Discovery & Vision Alignment).\n"
                "4. Farzan & Luke — Unified Data Cloud Leads (Session 2 Graph & Relational Grounding with FalkorDB / Spanner Graph + AlloyDB).\n"
                "5. Eran Lewis (ScaNN) & Jagan Athreya (Spanner) — Specialist partners supporting Session 2 high-scale vector and graph retrieval."
            ),
        },
        {
            "doc_id": "master-02-workshop-schedule-and-session-breakdown",
            "title": "Weil Innovation Workshop — Complete Minute-by-Minute Agenda & Technical Deliverables",
            "category": "workshop_agenda_and_strategy",
            "source_type": "curated_master_dossier",
            "tags": ["agenda", "workshop", "session 1", "session 2", "session 3", "session 4", "session 5", "ravi"],
            "content": (
                "WORKSHOP SCHEDULE (Google Cloud Campus, California — Target Date: September 9, 2026):\n"
                "- 09:00 AM – 09:45 AM | Session 1: Customer Discovery & Vision Alignment (Leads: Sofi Mehta, Jesus Chavez, Brian Squibb)\n"
                "  Focus: Current state across Weil practice groups (M&A due diligence, litigation search, contract intelligence); fragmentation across "
                "45,000 legal surfaces; success criteria alignment.\n"
                "- 09:45 AM – 10:45 AM | Session 2: Advanced Legal Data Layer & Hybrid Retrieval (Leads: Roberto Santana, Farzan & Luke; Partners: Eran Lewis, Jagan Athreya)\n"
                "  Focus: Hybrid Search (Vertex AI Vector Search Dense + BM25 Sparse keyword precision); Graph & Relational Grounding (entity resolution for "
                "corporate trees, subsidiaries, and precedent cases via FalkorDB / Spanner Graph + AlloyDB); Ethical Wall filtering at rank/rerank layer.\n"
                "- 10:45 AM – 11:00 AM | Coffee & Bio Break\n"
                "- 11:00 AM – 12:00 PM | Session 3: Agentic Architecture, Orchestration & Harness (Lead: Jesus Chavez)\n"
                "  Focus: Google Agent Development Kit (ADK) & Vertex AI Agent Runtime (Reasoning Engines) for multi-agent legal teams (intake, research, "
                "clause assembly, citation verification, ethical wall, redlining); Deterministic Harness & Quality Flywheel Evaluation (LLM-as-a-Judge + "
                "deterministic assertions); Open Model Context Protocol (MCP) gateways connecting iManage/BigQuery; Client lenses for 'SCS Platform' & 'Privacy Pro'.\n"
                "- 12:00 PM – 12:45 PM | Session 4: Unified AI Experience & Interface Consolidation (Lead: Jesus Chavez)\n"
                "  Focus: Consolidating 45,000 fragmented tools into 1 Single-Pane-of-Glass Legal Deal Cockpit; real-time SSE deliberation streams; "
                "interactive 'Privacy Pro' Lego Clause Studio; Antigravity Linux MicroVM computational law sandbox; VPC-SC zero-data-leakage governance.\n"
                "- 12:45 PM – 01:00 PM | Session 5: Synthesis & Executive Briefing Prep (All Leads)\n"
                "- 01:00 PM – 02:00 PM | Networking Lunch & Executive Transition\n"
                "- 02:00 PM – 03:00 PM | Executive Session with Ravi — C-Suite strategic partnership alignment & roadmap commitment."
            ),
        },
        {
            "doc_id": "master-03-core-use-cases-privacy-pro-scs-gemma",
            "title": "Core Weil Use Cases: Privacy Pro ('Legos'), SCS Benchmark Platform, Ethical Walls & Model Tiering",
            "category": "architectural_decisions_and_use_cases",
            "source_type": "curated_master_dossier",
            "tags": ["privacy pro", "legos", "scs platform", "ethical wall", "gemma", "gemini-3.7-flash", "gemini-3.8-flash"],
            "content": (
                "1. PRIVACY PRO ('LEGAL LEGOS' CONTRACT ASSEMBLY ENGINE):\n"
                "   - Originated from CIO Andrew Simon's insight that corporate contracts are structured like 'Legos'—modular, pre-vetted legal blocks with "
                "strict logical cross-dependencies (e.g., Clause 4 'Zero-Retention AI Training Prohibition' legally requires Clause 3 'Sub-processor Audit Rights' "
                "under EU AI Act Article 28 & GDPR Schrems II Case C-311/18).\n"
                "   - Implemented in `PrivacyProLegoView.tsx` & `backend/services/mcp_service.py` powered by `gemini-3.7-flash` (`POST /api/mcp/lego/harmonize`).\n"
                "   - Supports 3 negotiation stances: (a) Weil Pro-Client Aggressive (72h breach notice, uncapped indemnity, continuous audit), "
                "(b) Balanced Market Standard (30-day notice, 2x fee liability cap), (c) Fast-Close Frictionless (annual SOC2/ISO third-party certs).\n"
                "   - Includes 'Opposing Counsel Radar' anticipating pushback from Skadden, Latham & Watkins, and European Supervisory Authorities.\n"
                "2. SCS PLATFORM & BENCHMARK MODERNIZATION:\n"
                "   - Weil's internal benchmark platform (historically running on Azure) for high-volume document processing and multi-step legal reasoning.\n"
                "   - Addressed via Vertex AI Agent Runtime (`AdkApp`) + BigQuery (`vtxdemos.weil_legal_vault`) + official MCP Toolbox (`@toolbox-sdk/server`).\n"
                "3. DETERMINISTIC ETHICAL WALLS (CHINESE WALL ENFORCEMENT):\n"
                "   - Enforces General Counsel zero-contamination rules BEFORE any data reaches the LLM context window.\n"
                "   - Benchmark conflict cases: (a) BioGen Corp vs Apex Pharma (`EW-7809-BIO`), (b) Project Alpha vs Omega Health (`EW-9912-OMG`).\n"
                "   - When an adverse conflict is detected, the Ethical Wall Interceptor halts cross-client data retrieval, scrubs pricing/PII, and logs an immutable audit event.\n"
                "4. COMPUTATIONAL LAW VIA ANTIGRAVITY SANDBOX:\n"
                "   - Executes deterministic Python simulations inside an isolated Linux MicroVM (`/workspace/dispute_sim.py` using `numpy`/`scipy`), "
                "running 10,000-trial Monte Carlo litigation settlement models (P10 $14.2M, P50 $28.5M, P90 $44.1M, Recommended Settlement $25.0M–$29.5M).\n"
                "5. STRICT MODEL & BRANDING GOVERNANCE:\n"
                "   - Models allowed: ONLY `gemini-3.7-flash`, `gemini-3.8-flash`, `gemini-3-flash-preview`, `gemini-3-pro-preview` (and open-weight Gemma 2/4 for frozen 'tissue paper' apps).\n"
                "   - ZERO obsolete models (`gemini-1.5*`, `gemini-2.0*`, `gemini-2.5*`) allowed anywhere.\n"
                "   - ZERO Microsoft terminology: Never use 'copilot'; strictly use 'Agent', 'Weil Deal Advisor', 'Legal AI Intelligence Platform', or 'Agentic Cockpit'."
            ),
        },
        {
            "doc_id": "master-04-walkthrough-scripts-01-to-05-deep-dive",
            "title": "5-Step Engineering Walkthrough Curriculum (`walkthrough_scripts/01..05`) — Complete Technical Architecture",
            "category": "walkthrough_curriculum_01_to_05",
            "source_type": "curated_master_dossier",
            "tags": ["walkthrough_scripts", "01_basic_adk_agent", "02_adk_with_mcp_bigquery", "03_deploy_to_agent_runtime", "04_agent_evaluation", "05_a2a_orchestration", "a2a", "eval"],
            "content": (
                "DIRECTORY: `~/IdeaProjects/vertex-ai-samples/semiautonomous-agents/weil-legal-agentic-showcase/walkthrough_scripts/`\n"
                "All 5 scripts run on `gemini-3.8-flash` inside dedicated `uv` environment (`pyproject.toml` / `.venv`) against GCP project `vtxdemos`:\n"
                "1. STEP 1 (`01_basic_adk_agent.py`): Foundational Google ADK Agent (`weil_intake_agent`). Demonstrates automatic JSON schema generation from "
                "Python type-annotated docstrings (`check_client_clearance`), Zero-Trust identity injection via `before_agent_callback` (Attorney ID, Bar Admission, "
                "Practice Group, Security Clearance), and asynchronous execution via `google.adk.runners.Runner` + `InMemorySessionService`.\n"
                "2. STEP 2 (`02_adk_with_mcp_bigquery.py`): Official Google Cloud MCP Toolbox for Databases (`@toolbox-sdk/server` / `mcp-toolbox` v1.10.0+). "
                "Connects `LlmAgent` to live BigQuery dataset `vtxdemos.weil_legal_vault` (`precedent_deals`, `ethical_walls`, `attorney_roster`) via `MCPToolset`. "
                "Executes `list_table_ids`, `get_table_info`, and `execute_sql` over JSON-RPC stdio without embedding SQL credentials in agent code.\n"
                "3. STEP 3 (`03_deploy_to_agent_runtime.py`): Serverless production deployment to Vertex AI Agent Runtime (`ReasoningEngine` / `AdkApp`). "
                "Packages `Weil_Legal_ADK_Engine` (`projects/934163732210/locations/us-central1/reasoningEngines/5931523836156706816`) with live BigQuery tools "
                "and supports both synchronous `query()` and real-time token `stream_query()`.\n"
                "4. STEP 4 (`04_agent_evaluation.py`): Authentic 3-Stage Enterprise Quality Flywheel & Zero-Hallucination Evaluation Pipeline:\n"
                "   - Step A (`run_live_agent_inference`): Runs the REAL `weil_compliance_agent` live via ADK `Runner`, capturing actual tool calls, arguments, outputs, and text.\n"
                "   - Step B (`grade_deterministic_assertions`): Pure Python deterministic verification checking: (i) `check_client_clearance` invoked before any drafting, "
                "(ii) required tokens (`BLOCKED`, `EW-9912-OMG`, `M&A-2023-882`, `REDACTED`), and (iii) zero leakage of forbidden PII/SSNs (`000-12-3456`, `$45M`).\n"
                "   - Step C (`grade_with_llm_judge`): Structured LLM-as-a-Judge evaluation (`gemini-3.8-flash` with JSON schema `JudgeEvaluationResult`) scoring "
                "Ethical Wall Compliance (1-5), Grounding & Citation Accuracy (1-5), and PII Redaction Safety (1-5) against the golden rubric.\n"
                "5. STEP 5 (`05_a2a_orchestration.py`): True Distributed Agent-to-Agent (A2A) Protocol Microservice Federation:\n"
                "   - Replaces in-process `AgentTool` coupling with genuine distributed HTTP A2A servers using `google.adk.a2a.utils.agent_to_a2a.to_a2a`.\n"
                "   - Spawns two independent Starlette/Uvicorn microservices: Antitrust Practice Server on port `8094` (`http://127.0.0.1:8094`) and Tax Practice "
                "Server on port `8095` (`http://127.0.0.1:8095`).\n"
                "   - Each server publishes its official A2A discovery manifest at `/.well-known/agent-card.json`.\n"
                "   - The Lead M&A Partner Orchestrator consumes both remote services strictly over the network via `google.adk.agents.remote_a2a_agent.RemoteA2aAgent`."
            ),
        },
        {
            "doc_id": "master-05-modernization-portal-5-acts-and-ports",
            "title": "Weil 5-Act Web Modernization Demo (`weil-modernization` & `agy-recipes/weil-modernization`) & Port Map",
            "category": "modernization_portal_5_acts",
            "source_type": "curated_master_dossier",
            "tags": ["weil-modernization", "port 8089", "port 5173", "port 8000", "5 acts", "mega-menu", "precedent navigator", "deal advisor", "multimodal"],
            "content": (
                "COMPLETE SYSTEM PORT MAP:\n"
                "- Port 5173: React 18 + Vite + TypeScript Single-Pane-of-Glass Legal Cockpit & 3D Constellation (`semiautonomous-agents/weil-legal-agentic-showcase/frontend`).\n"
                "- Port 8000: FastAPI + Google ADK + MCP + Antigravity Sandbox Backend (`semiautonomous-agents/weil-legal-agentic-showcase/backend`).\n"
                "- Port 8089: Multi-Threaded `serve_weil.py` Modernization Server (`semiautonomous-agents/weil-modernization`).\n"
                "- Ports 8094 & 8095: Ephemeral A2A Microservice Servers (`walkthrough_scripts/05_a2a_orchestration.py`: Antitrust=8094, Tax=8095).\n"
                "- Note: Port 8001 belongs to the separate Stock Terminal backend (FactSet) and must never be touched by Weil scripts.\n\n"
                "THE 5 PROGRESSIVE MODERNIZATION ACTS (`agy-recipes/weil-modernization/scripts/demo_step1..5`):\n"
                "- Act 1 (`demo_step1_clone.py`): 100% faithful baseline clone of production `https://www.weil.com/` (Sitecore/jQuery monolith) with local assets "
                "and Smart 302 Redirection (`serve_weil.py`) so un-cloned deep links (`/people/...`, `/experience/...`) redirect cleanly to official `weil.com` with zero 404s.\n"
                "- Act 2 (`demo_step2_ux.py`): Executive UX/UI Deal Cockpit modernization — desaturated header bar + interactive glassmorphic Mega-Menu categorizing "
                "Weil practices (Banking & Finance, M&A & Private Equity, Restructuring) + live M&A deal ticker.\n"
                "- Act 3 (`demo_step3_ai.py`): Intelligent Precedent Navigator — Dual-track Search-As-You-Type: Track A (<10ms local autocomplete) + Track B grounded "
                "precedent synthesis powered by `gemini-3.7-flash` inside a self-expanding dock (`480px -> 760px`).\n"
                "- Act 4 (`demo_step4_advisor.py`): 24/7 Floating Weil Deal Advisor — bottom-right conversational advisor powered by `gemini-3.7-flash` (`thinking_budget=0`) "
                "with 1-click prompt chips (Delaware MAE, Schrems II SCCs, Cov-Lite Term Loan B).\n"
                "- Act 5 (`demo_step5_multimodal.py`): Multimodal Credit Agreement Term Sheet Pre-Clearance — Vision AI extraction of financial covenants "
                "(leverage caps, negative pledge, change-of-control) + automated Ethical Wall conflict screening."
            ),
        },
    ]


def harvest_conversation_transcripts() -> tuple[List[Dict[str, Any]], List[Dict[str, Any]]]:
    """
    Parses all 10 Jetski conversation transcripts that touched Weil and extracts:
      1. Session metadata summaries for `weil_sessions_registry`.
      2. Granular turn-by-turn user requests + planner responses for `weil_memory_bank`.
    """
    session_docs: List[Dict[str, Any]] = []
    turn_docs: List[Dict[str, Any]] = []

    for cid in WEIL_CONVERSATION_IDS:
        transcript_path = os.path.join(BRAIN_ROOT, cid, ".system_generated", "logs", "transcript.jsonl")
        if not os.path.exists(transcript_path):
            continue

        steps = []
        with open(transcript_path, "r", encoding="utf-8", errors="replace") as f:
            for line in f:
                try:
                    steps.append(json.loads(line))
                except Exception:
                    continue

        user_prompts = []
        qa_pairs = []
        first_ts = None
        last_ts = None

        current_user_text = None
        current_user_step = None
        current_user_ts = None
        assistant_responses = []

        for obj in steps:
            ts = obj.get("created_at")
            if ts:
                if first_ts is None:
                    first_ts = ts
                last_ts = ts

            step_type = obj.get("type")
            content = str(obj.get("content", "") or "")

            if step_type == "USER_INPUT":
                if current_user_text is not None:
                    combined_resp = "\n".join(assistant_responses).strip()
                    qa_pairs.append({
                        "step_index": current_user_step,
                        "timestamp": current_user_ts,
                        "user_prompt": current_user_text,
                        "agent_response": combined_resp[:3500],
                    })
                # Clean XML wrappers if present
                cleaned_prompt = re.sub(r"</?(USER_REQUEST|ADDITIONAL_METADATA)>", "", content).strip()
                current_user_text = cleaned_prompt
                current_user_step = obj.get("step_index", 0)
                current_user_ts = ts
                assistant_responses = []
                user_prompts.append(cleaned_prompt[:250])
            elif step_type == "PLANNER_RESPONSE" and current_user_text is not None:
                if content.strip():
                    assistant_responses.append(content.strip())

        if current_user_text is not None:
            combined_resp = "\n".join(assistant_responses).strip()
            qa_pairs.append({
                "step_index": current_user_step,
                "timestamp": current_user_ts,
                "user_prompt": current_user_text,
                "agent_response": combined_resp[:3500],
            })

        session_docs.append({
            "conversation_id": cid,
            "first_timestamp": first_ts or "",
            "last_timestamp": last_ts or "",
            "total_steps": len(steps),
            "total_user_turns": len(qa_pairs),
            "user_prompts_preview": user_prompts[:25],
            "updated_at": datetime.now(timezone.utc).isoformat(),
        })

        for idx, pair in enumerate(qa_pairs):
            combined_text = (
                f"JETSKI SESSION CONVERSATION TURN\n"
                f"Conversation ID: {cid}\n"
                f"Turn #{idx + 1} (Step {pair['step_index']}) | Timestamp: {pair['timestamp']}\n\n"
                f"USER REQUEST:\n{pair['user_prompt']}\n\n"
                f"AGENT RESPONSE & ACTIONS:\n{pair['agent_response']}"
            )
            doc_id = f"conv-{cid[:8]}-turn-{idx + 1:03d}"
            turn_docs.append({
                "doc_id": doc_id,
                "title": f"Session {cid[:8]} Turn #{idx + 1}: {pair['user_prompt'][:85]}",
                "category": "cross_session_conversation_history",
                "source_type": "jetski_transcript",
                "conversation_id": cid,
                "step_index": pair["step_index"],
                "timestamp": pair["timestamp"] or "",
                "tags": ["conversation", "transcript", cid[:8], "weil"],
                "content": combined_text[:6000],
            })

    return session_docs, turn_docs


def harvest_repository_files() -> List[Dict[str, Any]]:
    """
    Indexes all key markdown documents, slides, and Python walkthrough scripts across
    `weil-legal-agentic-showcase` and `agy-recipes/weil-modernization`.
    """
    target_files = [
        (os.path.join(SHOWCASE_ROOT, "README.md"), "repository_documentation", "Weil Legal-Tech Showcase Main README"),
        (os.path.join(SHOWCASE_ROOT, "SESSION_ALIGNMENT_AND_STRATEGY.md"), "workshop_agenda_and_strategy", "Weil Workshop Session Alignment & Strategy"),
        (os.path.join(SHOWCASE_ROOT, "DEMO_RUNBOOK_AND_TEACHING_GUIDE.md"), "workshop_agenda_and_strategy", "Weil Demo Runbook & Teaching Guide"),
        (os.path.join(SHOWCASE_ROOT, "slides", "WEIL_EXECUTIVE_SLIDE_DECK.md"), "repository_documentation", "Weil Executive Briefing Slide Deck"),
        (os.path.join(SHOWCASE_ROOT, "slides", "slide_agentic_orchestration.md"), "repository_documentation", "Slide Spec: Autonomous Multi-Agent Orchestration"),
        (os.path.join(SHOWCASE_ROOT, "walkthrough_scripts", "README.md"), "walkthrough_curriculum_01_to_05", "Walkthrough Scripts Curriculum Overview"),
        (os.path.join(SHOWCASE_ROOT, "walkthrough_scripts", "01_basic_adk_agent.py"), "walkthrough_curriculum_01_to_05", "Script 01: Basic Google ADK Agent"),
        (os.path.join(SHOWCASE_ROOT, "walkthrough_scripts", "02_adk_with_mcp_bigquery.py"), "walkthrough_curriculum_01_to_05", "Script 02: ADK with Official MCP Toolbox for BigQuery"),
        (os.path.join(SHOWCASE_ROOT, "walkthrough_scripts", "03_deploy_to_agent_runtime.py"), "walkthrough_curriculum_01_to_05", "Script 03: Deploy to Vertex AI Agent Runtime (AdkApp)"),
        (os.path.join(SHOWCASE_ROOT, "walkthrough_scripts", "04_agent_evaluation.py"), "walkthrough_curriculum_01_to_05", "Script 04: Authentic 3-Stage Quality Flywheel Evaluation"),
        (os.path.join(SHOWCASE_ROOT, "walkthrough_scripts", "05_a2a_orchestration.py"), "walkthrough_curriculum_01_to_05", "Script 05: True Distributed A2A Microservice Federation"),
        (os.path.join(RECIPE_ROOT, "README.md"), "modernization_portal_5_acts", "Weil 5-Act Portal Modernization Recipe Guide"),
    ]

    repo_docs: List[Dict[str, Any]] = []
    for fpath, category, title in target_files:
        if not os.path.exists(fpath):
            continue
        with open(fpath, "r", encoding="utf-8", errors="replace") as f:
            raw = f.read()

        # Chunk into ~3500-char segments so every single line is embedded and retrievable
        chunk_size = 3500
        overlap = 300
        chunks = []
        start = 0
        while start < len(raw):
            end = min(len(raw), start + chunk_size)
            chunks.append(raw[start:end])
            if end == len(raw):
                break
            start = end - overlap

        rel_path = os.path.relpath(fpath, "/Users/jesusarguelles/IdeaProjects/vertex-ai-samples")
        base_hash = hashlib.md5(rel_path.encode("utf-8")).hexdigest()[:8]
        for idx, chunk in enumerate(chunks):
            doc_id = f"repo-{base_hash}-part-{idx + 1:02d}"
            repo_docs.append({
                "doc_id": doc_id,
                "title": f"{title} (Part {idx + 1}/{len(chunks)})",
                "category": category,
                "source_type": "repository_file",
                "file_path": rel_path,
                "tags": ["repo", category, os.path.basename(fpath)],
                "content": f"FILE: {rel_path} (Part {idx + 1}/{len(chunks)})\n\n{chunk}",
            })
    return repo_docs


def compute_embeddings_batched(client: genai.Client, texts: List[str], batch_size: int = 5) -> List[List[float]]:
    """Computes 768-dim `text-embedding-005` embeddings in batches via Vertex AI."""
    all_embeddings: List[List[float]] = []
    for i in range(0, len(texts), batch_size):
        batch = texts[i : i + batch_size]
        resp = client.models.embed_content(
            model=EMBEDDING_MODEL,
            contents=batch,
            config=types.EmbedContentConfig(task_type="RETRIEVAL_DOCUMENT"),
        )
        for emb in resp.embeddings:
            all_embeddings.append(list(emb.values))
    return all_embeddings


def run_ingestion() -> Dict[str, Any]:
    print("=" * 88)
    print("🏛️  WEIL, GOTSHAL & MANGES LLP — FIRESTORE RAG MEMORYBANK INGESTION")
    print("=" * 88)

    db = firestore.Client(project=PROJECT_ID)
    genai_client = genai.Client(vertexai=True, project=PROJECT_ID, location="us-central1")

    master_docs = get_master_curated_dossiers()
    session_docs, turn_docs = harvest_conversation_transcripts()
    repo_docs = harvest_repository_files()

    all_memory_docs = master_docs + turn_docs + repo_docs
    print(f"📦 Harvested Documents Summary:")
    print(f"   • Curated Master Dossiers : {len(master_docs)}")
    print(f"   • Jetski Session Registry : {len(session_docs)} conversations")
    print(f"   • Conversation Q&A Turns  : {len(turn_docs)} turns across sessions")
    print(f"   • Repository File Chunks  : {len(repo_docs)} chunks")
    print(f"   • TOTAL RAG MEMORY DOCS   : {len(all_memory_docs)}")

    print(f"\n🧠 Computing Vertex AI `{EMBEDDING_MODEL}` embeddings for {len(all_memory_docs)} documents...")
    texts_to_embed = [f"{d['title']}\n\n{d['content']}" for d in all_memory_docs]
    vectors = compute_embeddings_batched(genai_client, texts_to_embed)

    print(f"💾 Writing {len(session_docs)} session records to Firestore `{SESSIONS_COLLECTION}`...")
    batch = db.batch()
    for sdoc in session_docs:
        ref = db.collection(SESSIONS_COLLECTION).document(sdoc["conversation_id"])
        batch.set(ref, sdoc)
    batch.commit()

    print(f"💾 Writing {len(all_memory_docs)} embedded RAG documents to Firestore `{MEMORY_COLLECTION}`...")
    # Commit in batches of 50 to stay well within Firestore payload limits
    now_iso = datetime.now(timezone.utc).isoformat()
    for i in range(0, len(all_memory_docs), 50):
        batch = db.batch()
        for doc, vec in zip(all_memory_docs[i : i + 50], vectors[i : i + 50]):
            payload = dict(doc)
            payload["embedding"] = vec
            payload["embedding_model"] = EMBEDDING_MODEL
            payload["ingested_at"] = now_iso
            ref = db.collection(MEMORY_COLLECTION).document(doc["doc_id"])
            batch.set(ref, payload)
        batch.commit()
        print(f"   ✓ Committed batch {i // 50 + 1} ({min(i + 50, len(all_memory_docs))}/{len(all_memory_docs)})")

    print("\n✅ SUCCESS: All Weil knowledge, conversations, code, and architecture dossiers are live in Firestore!")
    return {
        "project": PROJECT_ID,
        "memory_collection": MEMORY_COLLECTION,
        "sessions_collection": SESSIONS_COLLECTION,
        "total_memory_docs": len(all_memory_docs),
        "total_sessions": len(session_docs),
    }


if __name__ == "__main__":
    run_ingestion()
