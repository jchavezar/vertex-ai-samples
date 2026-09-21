# Weil Legal Agentic Architecture: Educational Script Series

This directory contains standalone, self-contained educational Python scripts specifically structured for **Andrew Simon (CIO)** and **Ian Miller (Head of Tech Architecture)** at **Weil, Gotshal & Manges LLP**.

Each script addresses the fundamental engineering questions behind enterprise agentic systems, running exclusively on **Gemini 3.8 Flash** (`gemini-3.8-flash`) within Google Cloud project `vtxdemos`.

---

## Dedicated `uv` Environment (Isolated to this folder)

This directory has its own self-contained virtual environment `.venv` powered by `uv`, ensuring it doesn't collide with the root project or any other system packages:

```bash
cd ~/IdeaProjects/vertex-ai-samples/semiautonomous-agents/weil-legal-agentic-showcase/walkthrough_scripts

# Run any script with uv directly:
uv run python 01_basic_adk_agent.py
uv run python 02_adk_with_mcp_bigquery.py

# Or activate manually:
source .venv/bin/activate
python 01_basic_adk_agent.py
```

---

## The 5-Step Curriculum

### Step 1: The Foundational ADK Agent
* **File:** `01_basic_adk_agent.py`
* **What it demonstrates:**
  - Defining an `Agent` in Google ADK with explicit instructions.
  - Automatic JSON Schema generation from Python type-annotated docstrings (`check_client_clearance`).
  - Zero-Trust session context injection via `before_agent_callback`.
  - Local runtime execution using `google.adk.runners.Runner`.
* **Execution:**
  ```bash
  python3 walkthrough_scripts/01_basic_adk_agent.py
  ```

---

### Step 2: Decoupled Tool Integration via Official Google Cloud MCP Toolbox for Databases
* **Files:** `02_adk_with_mcp_bigquery.py`
* **What it demonstrates:**
  - Connecting Google ADK to the **official Google Cloud MCP Toolbox for Databases** (`@toolbox-sdk/server` / `mcp-toolbox` v1.10.0+).
  - Executing standard MCP database tools: `list_table_ids`, `get_table_info`, and `execute_sql`.
  - Autonomous multi-tool execution with `gemini-3.8-flash` synthesizing live BigQuery precedent data from `vtxdemos.weil_legal_vault`.
* **Execution:**
  ```bash
  python3 walkthrough_scripts/02_adk_with_mcp_bigquery.py
  ```

---

### Step 3: Production Deployment to Vertex AI Agent Runtime (Reasoning Engines)
* **File:** `03_deploy_to_agent_runtime.py`
* **What it demonstrates:**
  - Packaging the ADK Agent into a deployable container class (`WeilManagedLegalEngine`).
  - Native integration with Google Cloud BigQuery (`vtxdemos.weil_legal_vault`) using GCP IAM identity.
  - Auto-detection of existing active Reasoning Engines in `vtxdemos` (us-central1) for instant presentation without 5-8 minute cold build delays.
  - Implementing `query()` and `stream_query()` contracts with live token streaming.
  - Enterprise deployment specifications for both `agents-cli deploy` and `reasoning_engines.ReasoningEngine.create`.
* **Execution:**
  ```bash
  python3 walkthrough_scripts/03_deploy_to_agent_runtime.py
  ```

---

### Step 4 (Enterprise Add-on): Authentic 3-Stage Quality Flywheel & Zero-Hallucination Evaluation
* **File:** `04_agent_evaluation.py`
* **What it demonstrates:**
  - **Step A (`run_live_agent_inference`)**: Executes the real Google ADK agent (`weil_compliance_agent` on `gemini-3.8-flash`) live via ADK `Runner` with genuine tools (`check_client_clearance` + live BigQuery `query_bigquery_deals`).
  - **Step B (`grade_deterministic_assertions`)**: Deterministic Python verification asserting that `check_client_clearance` ran before any drafting, required citations (`M&A-2023-882`, `EW-9912-OMG`) are present, and forbidden PII (`000-12-3456`, `$45M`) is 100% redacted.
  - **Step C (`grade_with_llm_judge`)**: Structured `gemini-3.8-flash` LLM-as-a-Judge evaluation scoring Ethical Wall Compliance (1-5), Grounding & Citation Accuracy (1-5), and PII Redaction Safety (1-5).
* **Execution:**
  ```bash
  uv run python 04_agent_evaluation.py
  ```

---

### Step 5 (Enterprise Add-on): True Distributed Agent-to-Agent (A2A) Microservice Federation
* **File:** `05_a2a_orchestration.py`
* **What it demonstrates:**
  - True distributed A2A protocol microservice federation across independent network processes (not in-process `AgentTool` coupling).
  - Exposes standalone Starlette/Uvicorn A2A HTTP servers via `to_a2a()` on port `8094` (Antitrust Practice Server) and port `8095` (Tax Practice Server).
  - Performs live HTTP capability discovery against `/.well-known/agent-card.json`.
  - Orchestrates cross-practice M&A due diligence from the Lead M&A Partner Agent over the network via `RemoteA2aAgent`.
* **Execution:**
  ```bash
  uv run python 05_a2a_orchestration.py
  ```

---

## Key Takeaway for Weil Leadership
> *"We do not build monolithic, black-box prompts. We build decoupled, specialist agents coordinated by a deterministic harness, accessing enterprise data through the Model Context Protocol, and hosted serverlessly on Vertex AI Agent Runtime."*
