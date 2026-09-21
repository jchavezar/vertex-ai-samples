# Google ADK (Agent Development Kit) Directory Structure

This directory follows the official Google ADK multi-agent convention for local inspection, testing, and deployment via the **ADK Web UI**.

```
adk_agents/
│
├── weil_deal_intake_agent/         # Agent 1: Conflict & Ethical Wall Clearance
│   ├── __init__.py                # Exports `root_agent`
│   ├── agent.py                   # Root Agent definition (gemini-3.8-flash)
│   ├── callbacks.py               # Session & Zero-Trust context injection
│   └── tools/
│       ├── __init__.py
│       ├── clearance_tool.py      # Hardcoded Ethical Wall check
│       └── bigquery_precedents.py # BigQuery Deal Precedent retriever
│
└── weil_ma_orchestrator/          # Agent 2: Multi-Agent M&A Collaboration
    ├── __init__.py                # Exports `root_agent`
    ├── agent.py                   # Root Orchestrator (delegates via AgentTool)
    └── subagents/
        ├── __init__.py
        ├── antitrust_agent.py     # Regulatory & CFIUS Specialist
        └── tax_agent.py           # Section 338 & Structuring Specialist
```

---

## How to Test Locally with ADK Web UI

### Option A: Launch the Web UI on Port 8088
From the project root directory, run:

```bash
python3 -m google.adk.cli web --port 8088 adk_agents
```

### What You Will See in the ADK Web UI:
1. Open your browser to: **`http://localhost:8088`**
2. In the top dropdown, select either:
   - **`weil_deal_intake_agent`**
   - **`weil_ma_orchestrator`**
3. Test Queries:
   - **Ethical Wall Breach Test:**
     `"Please run intake for prospective client 'Apex Capital' acquiring 'AlphaCorp'."`
     *(Watch the agent immediately trigger the Ethical Wall policy violation and halt).*
   - **Clearance & Precedent Benchmark:**
     `"Please run intake for Nexus Capital acquiring Zephyr Robotics and find precedent deal terms."`
     *(Watch the agent clear conflicts, query BigQuery, and present deal multiples).*
   - **Multi-Agent M&A Collaboration:**
     `"Analyze antitrust covenants and Section 338 tax implications for a $2.3B robotics acquisition."`
     *(Watch the orchestrator delegate to `antitrust_specialist` and `tax_specialist` and synthesize the results).*
