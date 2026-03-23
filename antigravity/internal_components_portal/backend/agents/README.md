# The Internal Component Portal: Agent Swarm Architecture

Welcome to the ADK `backend/agents/` orchestration layer. 

This directory contains the brains of the Zero-Leak Portal. Instead of just one monolithic AI answering everything, the architecture utilizes a "Swarm" of highly specialized, isolated proxy agents. Each agent serves a unique purpose, governed by strict identity propagation and zero-leak environment protocols.

## Explore the Swarm

* **[The Intent Router & Orchestrator](docs/router.md)** (`agent.py` & `router_agent.py`)
  The multiplexing engine. Evaluates user intent and dynamically pipes session state across specialized proxies without losing history.
  
* **[The Security Proxy Agent](docs/security_proxy.md)** (`agent.py`)
  The iron-clad enterprise searcher. Connected to SharePoint via MCP, forces numerical fuzzing, entity redaction, and requires active Azure AD authentication.

* **[The ServiceNow Proxy Agent](docs/servicenow_proxy.md)** (`agent.py`)
  The IT Service Management specialist. Can self-heal missing infrastructure details using Google Web Search before writing destructive actions via the ServiceNow MCP.

* **[The Public Research Proxy](docs/public_research.md)** (`public_agent.py`)
  The ultra-fast internet gatherer. Runs outside the enterprise enclave utilizing `gemini-2.5-flash` active browsing to provide real-time global consensus and news.

* **[The Analytics & Latency Agents](docs/analytics_agents.md)** (`latency_chat_agent.py` & `analyze_latency_agent.py`)
  The performance engineers. Used strictly in the Telemetry tab to analyze execution JSON footprints and identify bottlenecked tools or TTFT drops.

## How It Works (The Execution Flow)

```mermaid
graph TD
    %% Styling Definitions
    classDef user fill:#2d3436,stroke:#b2bec3,stroke-width:2px,color:#fff,rx:15,ry:15;
    classDef auth fill:#6c5ce7,stroke:#a29bfe,stroke-width:3px,color:#fff,rx:10,ry:10;
    classDef router fill:#fdcb6e,stroke:#ffeaa7,stroke-width:3px,color:#2d3436,rx:10,ry:10,font-weight:bold;
    classDef proxy fill:#0984e3,stroke:#74b9ff,stroke-width:2px,color:#fff,rx:8,ry:8;
    classDef db fill:#00b894,stroke:#55efc4,stroke-width:2px,color:#fff,shape:cylinder;
    classDef telemetry fill:#e17055,stroke:#fab1a0,stroke-width:2px,color:#fff;
    classDef insight fill:#d63031,stroke:#ff7675,stroke-width:3px,color:#fff,rx:10,ry:10;

    User([👤 User Prompt]):::user --> Auth[🔐 Token Validation Layer]:::auth
    Auth --> Router[⚡ DeloitteRouterAgent \n gemini-2.5-flash]:::router
    
    %% Intent Detection
    Router -- "ACTION / SEARCH" --> SecurityProxy[🛡️ Security Proxy \n MCP: mcp_server]:::proxy
    Router -- "SERVICENOW" --> ServiceNowProxy[🛠️ ServiceNow Proxy \n MCP: servicenow_mcp]:::proxy
    Router -- "PUBLIC" --> PublicProxy[🌐 Public Research Proxy \n Tool: google_search]:::proxy

    %% Deep Dives
    SecurityProxy -.-> SharePoint[(SharePoint)]:::db
    ServiceNowProxy -.-> SNSystem[(ServiceNow Cloud)]:::db
    PublicProxy -.-> Web[(Public Internet)]:::db

    %% Observability
    SecurityProxy -.-> TelemetryLog[📈 Telemetry JSON Stream]:::telemetry
    ServiceNowProxy -.-> TelemetryLog
    
    %% Post Analysis
    TelemetryLog --> AnalyticsAgent[📊 Execution Insight AI \n latency_chat_agent.py]:::insight
    User -. "Queries Telemetry" .-> AnalyticsAgent
```

> **Note on Diagram Links**: GitHub renders Mermaid diagrams inside isolated `viewscreen` sandboxes, which breaks relative markdown links. Instead of clicking the diagram, use the stylized navigation grid below!

## 🔗 The Swarm Component Grid

| Agent Component | Core Function | Associated Documentation |
| :--- | :--- | :--- |
| **⚡ Intent Router** | Real-time classification & multiplexing | [docs/router.md](docs/router.md) |
| **🛡️ Security Proxy** | Zero-Leak PWC internal SharePoint search | [docs/security_proxy.md](docs/security_proxy.md) |
| **🛠️ ServiceNow Proxy** | Ticketing & Incident management | [docs/servicenow_proxy.md](docs/servicenow_proxy.md) |
| **🌐 Public Intelligence** | High-velocity public web browsing | [docs/public_research.md](docs/public_research.md) |
| **📊 Analytics Engine** | Telemetry execution JSON analysis | [docs/analytics_agents.md](docs/analytics_agents.md) |

## Core Tenets
1. **Zero-Leak Initialization**: MCP definitions are dynamically created per request (`uv run python -m ...`), terminating as soon as the session dies. No data leaks.

2. **Context Passing**: Swarms share memory in-memory via ADK `SessionService` instances isolated strictly via unique AppNames and Session IDs.
3. **Execution Streams**: All outputs are Server-Sent Events (SSE). We capture functions, tools, thoughts, and outputs in real-time, feeding UI elements.
