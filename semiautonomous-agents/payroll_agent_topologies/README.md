# Payroll API Agent Topologies: Accuracy, Latency & Scale Analysis

This folder contains a fully functional prototype comparing different agent topologies using the **Google Agent Development Kit (ADK) 2.0** and **Model Context Protocol (MCP)** to handle high-frequency, concurrent payroll inquiries.

## 1. Executive Summary & Concurrency Challenge

When serving **148,000 concurrent payroll queries**, the design of the agentic topology directly determines your Google Cloud cost, rate limits (TPM/RPM), latency, and execution reliability. 

There are two primary topologies built in this prototype:
1. **Topology 1 (Single Monolithic Agent):** A single LLM agent equipped with all 24 payroll tools.
2. **Topology 2 (Orchestration Workflow):** A router agent that classifies the request and routes it to one of four specialized sub-agents.

Below is the comparative analysis based on actual execution benchmarks of the prototype.

---

## 2. Benchmark Results (Actual Execution)

Given the cross-domain query:
> *"Hi, I am employee EMP101. What is my current accrued PTO balance, and do I have any pending reimbursement claims?"*

| Metric / Attribute | Topology 1: Single Agent | Topology 2: Workflow Router |
| :--- | :--- | :--- |
| **Execution Latency** | **5.94 seconds** 🟢 | **14.57 seconds** 🔴 |
| **Response Accuracy** | **100% (Complete)** 🟢<br>• Accrued PTO: 80 hrs<br>• Claims: No pending, last client lunch paid | **50% (Incomplete)** ⚠️<br>• Accrued PTO: 80 hrs<br>• Claims: Unanswered (No tool access) |
| **LLM Turns Required** | 1 routing/planning turn + 1 summary turn | 1 routing turn + 1 specialized agent planning/summary turn |
| **Token Consumption** | High per-call input overhead (loads all 24 tool definitions) | Low per-call tool overhead, but double LLM invocation overhead |
| **Behavior under Cross-Domain Queries** | Seamlessly chains multiple tools. | Fails to answer queries crossing domain boundaries. |

---

## 3. Topologies Deep-Dive

### Topology 1: Single Agent + Monolithic MCP
*Code reference: [topology_1_single_agent.py](file:///usr/local/google/home/jesusarguelles/vertex-ai-samples/semiautonomous-agents/payroll_agent_topologies/topology_1_single_agent.py)*

In this topology, one agent has access to the full `McpToolset` exposing all 24 tools.

```
       [ User Query ]
             │
             ▼
┌─────────────────────────┐
│     LlmAgent (Root)     │ <─── Exposes all 24 tools (Monolithic MCP)
└────────────┬────────────┘
             │
      Chains Tool Calls
             │
             ▼
      [ Final Response ]
```

* **Pros:**
  * **Low Latency:** Minimum serial LLM reasoning steps.
  * **High Flexibility:** The model can easily chain multiple tools from different categories (e.g. checks PTO first, then pulls reimbursement history).
* **Cons:**
  * **Context Window Bloat:** Exposing 24 tool schemas adds ~4k tokens to the system prompt of every single session.
  * **Tool Confusion:** If tools have similar descriptions (e.g. `get_pay_stubs` vs `get_pay_calendar`), the LLM may occasionally select the wrong function.

---

### Topology 2: Workflow Router + Specialized Agents
*Code reference: [topology_2_workflow_agents.py](file:///usr/local/google/home/jesusarguelles/vertex-ai-samples/semiautonomous-agents/payroll_agent_topologies/topology_2_workflow_agents.py)*

In this topology, a parent `Workflow` uses a specialized Router Agent to classify the intent into one of four sub-agent domains:
1. **PROFILE:** Profile, address, salary history, 401(k), health tier.
2. **EARNINGS:** Paystubs, YTD earnings, W-4 settings, deductions.
3. **EXPENSES:** Direct deposit, reimbursements, bonuses.
4. **ATTENDANCE:** PTO balances, request leave.

```
                  [ User Query ]
                        │
                        ▼
            ┌───────────────────────┐
            │  payroll_router_agent │ (LLM Classification)
            └───────────┬───────────┘
                        │
                        ▼
              [ route_evaluator ]
                        │
         ┌──────────────┼──────────────┬──────────────┐
         ▼              ▼              ▼              ▼
     (PROFILE)     (EARNINGS)     (EXPENSES)    (ATTENDANCE)
   ┌───────────┐  ┌───────────┐  ┌───────────┐  ┌───────────┐
   │  Profile  │  │ Earnings  │  │ Expenses  │  │Attendance │
   │   Agent   │  │   Agent   │  │   Agent   │  │   Agent   │
   └─────┬─────┘  └─────┬─────┘  └─────┬─────┘  └─────┬─────┘
         │              │              │              │
         └──────────────┼──────────────┴──────────────┘
                        │
                        ▼
                [ Final Response ]
```

* **Pros:**
  * **Specialization:** Each subagent is small, has only 4-6 tools, eliminating tool confusion and reducing context window size.
  * **Access Isolation:** You can restrict sensitive tools (like `add_one_time_bonus` or `update_direct_deposit_settings`) to agents with stricter system instructions or extra validations.
* **Cons:**
  * **High Latency:** Requires multiple serial LLM roundtrips (Router -> Subagent -> Tool -> Response).
  * **Cross-Domain Failures:** If a user asks a compound question (e.g., PTO + Reimbursement), the router must choose only one branch, leaving part of the query unanswered.
  * **Quota Exhaustion:** Double LLM calls per query will trigger API quota rate limits (429) twice as fast.

---

## 4. Alternative Approach: Hybrid Deterministic Split-Router (Topology 3)

To solve the 148k concurrent request challenge, we propose **Topology 3: Deterministic Semantic Router with Parallel Subagent Fan-Out**.

Instead of using an LLM router to classify:
1. Use a **local fast classifier** (e.g. semantic embeddings, regex, or a lightweight keyword matching library) to identify which domains are mentioned in the query.
2. If multiple domains are flagged, use ADK's **`ParallelAgent`** or run multiple specialized sub-agents **concurrently** in the workflow.
3. Consolidate the parallel outputs using a **`JoinNode`** before returning the unified final response.

```
                          [ User Query ]
                                │
                                ▼
                     ┌─────────────────────┐
                     │ Fast Code Classifier│ (No LLM, sub-millisecond)
                     └──────────┬──────────┘
                                │
                 Identifies required sub-agents
                                │
                 ┌──────────────┴──────────────┐
                 ▼                             ▼
       ┌──────────────────┐          ┌──────────────────┐
       │ Expenses Agent   │          │ Attendance Agent │ (Executed in Parallel)
       └────────┬─────────┘          └────────┬─────────┘
                │                             │
                └──────────────┬──────────────┘
                               ▼
                        ┌─────────────┐
                        │  JoinNode   │ (Merges outputs)
                        └──────┬──────┘
                               ▼
                       [ Final Response ]
```

* **Why this is the best scale architecture:**
  * **Zero Router Latency:** Bypassing the LLM for classification saves ~4 seconds and 1 complete LLM turn.
  * **No Cross-Domain Failure:** If both PTO and Expenses are needed, both agents are fired concurrently.
  * **Parallel Execution:** Running the subagents in parallel keeps latency low even for compound questions.

---

## 5. Scaling to 148,000 Concurrency on GCP

Spawning local stdio processes for MCP servers (`StdioConnectionParams`) at a scale of 148k will fail due to OS resource limits (CPU/Memory saturation on the host).

### Production Architecture
1. **SSE Cloud Run MCP Server:**
   * Deploy the `payroll_mcp_server.py` as a serverless **Cloud Run** service using the Server-Sent Events (SSE) transport.
   * Auto-scale Cloud Run instances based on incoming request volumes.
2. **Vertex AI Agent Engine (Reasoning Engine):**
   * Package and deploy the ADK agents to **Vertex AI Agent Engine**.
   * Use **`StreamableHTTPConnectionParams`** in `McpToolset` pointing to the Cloud Run SSE endpoint.
3. **Context Caching:**
   * Use ADK's built-in **Context Caching** for the tool definitions. Because the 24 tools schemas are static, caching them on Vertex AI reduces input token cost by up to 90% and decreases TTFT (Time to First Token).

---

## 6. How to Run the Prototypes

Ensure you have initialized your Python environment with `uv`:
```bash
# Install dependencies
uv sync

# Run Topology 1 (Single Monolithic Agent)
uv run python topology_1_single_agent.py

# Run Topology 2 (Multi-Agent Workflow)
uv run python topology_2_workflow_agents.py
```
