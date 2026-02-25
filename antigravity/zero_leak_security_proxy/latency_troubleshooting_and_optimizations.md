# LLM Security Proxy SharePoint - Latency Troubleshooting & Optimizations

## Problem Overview (The ~53 Second Bottleneck)
Based on execution latency profiles and agent reasoning traces, the average turnaround time has been severely inflated (e.g., 52.72 seconds), largely driven by an inefficient search loop, processing large irrelevant documents, and massive context window bloat during final synthesis.

### Specific Bottlenecks Identified

1. **A Massive LLM Synthesis Bottleneck (18.63s):** 
   The largest contributor to the delay is the final synthesis step. Forcing the LLM to read and reason across a massive wall of text (~79,311 total tokens) to generate a complex, structured JSON response requires significant compute time.
2. **Inefficient "Trial and Error" Searching:**
   The agent struggles to map contextual natural language queries to Microsoft Graph API's strict keyword search, leading to repetitive loops. Each failed search adds latency for the Graph API call and the subsequent LLM evaluation.
3. **Processing Large, Irrelevant Documents & Token Bloat:**
   The agent triggers `_read_document_content()` which downloads and runs `MarkItDown` to OCR entire files without checking relevance. Extracting text from 50+ pages of dense corporate documents causes massive token bloat that chokes the final synthesis step.
4. **Delayed Fallback to Web Research (4.79s):**
   The system spends vast amounts of time failing internally before triggering public web research, rather than doing it in parallel.

---

## The Proposed "Just-In-Time Compression" Architecture

Since syncing the SharePoint instance into a separate Vector DB (e.g., Vertex AI Search) is not feasible, the MCP server must be transformed from a "dumb pipe" into a smart **Just-In-Time Compression Layer**. 

### 1. Optimize the Search Tool: Inline Query Transformation
When the agent calls `search_sharepoint_documents`, the MCP server uses a fast, lightweight model (like `gemini-2.5-flash`) inline to translate the natural language intent into optimized SharePoint **KQL (Keyword Query Language)** before executing the Graph API call.

### 2. The "Hit Highlights" First-Pass (Zero-Download Context)
The `/search/query` endpoint of Microsoft Graph automatically returns `summary` and `hitHighlights` fields. The MCP `search_document` tool should prioritize returning these highlights to the LLM. Often, the main agent can synthesize an answer *just by reading the search hit highlights*, completely skipping the OCR download step.

### 3. Inline "Map-Reduce" Extraction (Fixing the 79k Token Killer)
The `read_document_content(item_id)` tool should **never** return raw text to the main agent. Instead, it should implement inline compression:
1. Tool downloads the PDF and runs `MarkItDown`.
2. The Tool makes a blocking call to a fast sub-agent (`gemini-2.5-flash`): *"Here is a raw document. Extract only the paragraphs related to [User Intent]."*
3. The Tool returns the **compressed response** back to the Main Agent.
This reduces the synthesis context payload from 80k tokens to <1,000 tokens, drastically dropping latency.

### 4. Implement a "Parallel Retrieval" Tool
Expose a tool like `parallel_search_and_evaluate(queries: list[str])`. The Main Agent can batch potential queries simultaneously. The MCP server asynchronously executes all Graph API calls in parallel, merges the results, and returns the top unique documents instantly.

## Next Steps
This strategic redesign ensures we maintain precise intelligence while slashing token overhead and latency without requiring large scale offline synchronization processes.
