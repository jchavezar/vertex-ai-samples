<p align="center">
  <img alt="Stock Terminal Next-Gen" src="./diagram.jpeg" width="100%">
</p>

<div align="center">

[![License](https://img.shields.io/badge/License-Apache_2.0-0F172A?style=for-the-badge&logoColor=38BDF8&labelColor=1E293B)](https://opensource.org/licenses/Apache-2.0)
[![React](https://img.shields.io/badge/React-19.0-0F172A?style=for-the-badge&logo=react&logoColor=61DAFB&labelColor=1E293B)](https://react.dev/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115-0F172A?style=for-the-badge&logo=fastapi&logoColor=009688&labelColor=1E293B)](https://fastapi.tiangolo.com/)
[![Google ADK](https://img.shields.io/badge/Google_ADK-Agent_Kit-0F172A?style=for-the-badge&logo=googlecloud&logoColor=4285F4&labelColor=1E293B)](https://cloud.google.com/vertex-ai)
[![FactSet](https://img.shields.io/badge/FactSet-MCP-0F172A?style=for-the-badge&logo=data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iMjQiIGhlaWdodD0iMjQiIHZpZXdCb3g9IjAgMCAyNCAyNCIgZmlsbD0ibm9uZSIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIj48Y2lyY2xlIGN4PSIxMiIgY3k9IjEyIiByPSIxMCIgZmlsbD0iIzAwOTZEOSIvPjwvc3ZnPg==&logoColor=0096D9&labelColor=1E293B)](https://developer.factset.com/)
[![Vercel AI](https://img.shields.io/badge/Vercel_AI-SDK_v3-0F172A?style=for-the-badge&logo=vercel&logoColor=FFFFFF&labelColor=1E293B)](https://sdk.vercel.ai/)

</div>

<blockquote>
  <p><b>NEURAL INTELLIGENCE TERMINAL:</b> Stock Terminal Next-Gen is a high-performance financial analysis platform powered by Google's Agent Development Kit (ADK). It orchestrates multiple AI agents with real-time FactSet data feeds, Google Search, and code interpretation capabilities—all streaming through the Vercel AI SDK protocol for instant, reactive UI updates.</p>
</blockquote>

<br/>

## System Architecture

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                              USER INTERFACE                                  │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │  React 19 + TypeScript + Zustand + Framer Motion + Recharts        │   │
│  │  • Chat Container (floating/docked)    • Neural Link Dashboard     │   │
│  │  • Agent Graph Visualization           • Comps Analysis Arena      │   │
│  │  • Real-time Streaming Markdown        • Performance Charts        │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                    │                                         │
│                    Vercel AI SDK Protocol (Types 0,2,9,a)                   │
│                                    │                                         │
└────────────────────────────────────┼─────────────────────────────────────────┘
                                     │
                                     ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                           FASTAPI BACKEND                                    │
│  ┌──────────────────┐  ┌──────────────────┐  ┌──────────────────────────┐  │
│  │   ADK Runner     │  │  Smart Agent     │  │  Multi-Agent Workflows   │  │
│  │   Session Mgmt   │  │  Tool Observer   │  │  • Discovery Agent       │  │
│  │   Auth/OAuth     │  │  Stream Handler  │  │  • Research Agent        │  │
│  │                  │  │                  │  │  • Synthesis Agent       │  │
│  └──────────────────┘  └──────────────────┘  └──────────────────────────┘  │
│                                    │                                         │
└────────────────────────────────────┼─────────────────────────────────────────┘
                                     │
         ┌───────────────────────────┼───────────────────────────┐
         │                           │                           │
         ▼                           ▼                           ▼
┌─────────────────┐      ┌─────────────────────┐      ┌──────────────────┐
│  Google Gemini  │      │   FactSet MCP       │      │  Google Search   │
│  • 2.5 Flash    │      │   • Fundamentals    │      │  Real-time News  │
│  • 2.5 Pro      │      │   • Global Prices   │      │  Market Intel    │
│  • 3.0 Preview  │      │   • Ownership       │      │                  │
│                 │      │   • 20+ APIs        │      │                  │
└─────────────────┘      └─────────────────────┘      └──────────────────┘
```

<br/>

## Key Features

<details open>
<summary><kbd>FEATURE 1</kbd> <b>Multi-Agent ADK Orchestration</b></summary>
<br/>

<table>
  <tr>
    <td valign="top">
      <kbd>ARCHITECTURE</kbd> <b>Google ADK (Agent Development Kit)</b> powers the neural intelligence backbone.<br/><br/>
      <kbd>AGENTS</kbd> Multiple specialized agents work in concert:<br/>
      • <b>Smart Agent</b> - Primary orchestrator with tool access<br/>
      • <b>Neural Link Agent</b> - News & trend synthesis<br/>
      • <b>Comps Agent</b> - Competitive analysis<br/>
      • <b>Research Agent</b> - Deep dive analysis<br/><br/>
      <kbd>TOOLS</kbd> 20+ FactSet APIs + Google Search + Code Interpreter<br/><br/>
      <kbd>RESULT</kbd> Real-time financial analysis with sub-second response times.
    </td>
  </tr>
</table>

</details>

<br/>

<details open>
<summary><kbd>FEATURE 2</kbd> <b>Vercel AI SDK Streaming Protocol</b></summary>
<br/>

<table>
  <tr>
    <td valign="top">
      <kbd>PROTOCOL</kbd> Uses Vercel AI SDK Data Stream Protocol v1 for real-time communication.<br/><br/>
      <kbd>TYPE 0</kbd> <code>0:"text"</code> - Streaming text responses<br/><br/>
      <kbd>TYPE 2</kbd> <code>2:[{widget}]</code> - Data payloads (charts, stats, topology)<br/><br/>
      <kbd>TYPE 9</kbd> <code>9:{tool_call}</code> - Tool invocation notifications<br/><br/>
      <kbd>TYPE a</kbd> <code>a:{tool_result}</code> - Tool execution results with latency<br/><br/>
      <kbd>BENEFIT</kbd> Instant UI updates as the AI thinks—no waiting for complete responses.
    </td>
  </tr>
</table>

**Protocol Example:**
```
Backend yields:
  "0:\"Analyzing NVDA...\"\n"
  "9:{\"toolCallId\":\"abc\",\"toolName\":\"FactSet_Fundamentals\"}\n"
  "a:{\"toolCallId\":\"abc\",\"result\":{\"pe_ratio\":45.2}}\n"
  "2:[{\"type\":\"chart\",\"title\":\"NVDA Revenue\",\"data\":[...]}]\n"
  "0:\"Analysis complete!\"\n"
```

</details>

<br/>

<details open>
<summary><kbd>FEATURE 3</kbd> <b>FactSet MCP Integration</b></summary>
<br/>

<table>
  <tr>
    <td valign="top">
      <kbd>PROTOCOL</kbd> <b>Model Context Protocol (MCP)</b> connects to FactSet's enterprise APIs.<br/><br/>
      <kbd>TOOLS</kbd> 20+ financial data APIs available:<br/>
      • <code>FactSet_Fundamentals</code> - Company fundamentals<br/>
      • <code>FactSet_GlobalPrices</code> - Real-time pricing<br/>
      • <code>FactSet_Ownership</code> - Institutional holdings<br/>
      • <code>FactSet_People</code> - Executive data<br/>
      • <code>FactSet_CalendarEvents</code> - Earnings, dividends<br/>
      • <code>FactSet_Estimates</code> - Analyst estimates<br/>
      • ... and 15+ more<br/><br/>
      <kbd>AUTH</kbd> OAuth 2.0 with automatic token refresh<br/><br/>
      <kbd>PERFORMANCE</kbd> HTTP/2 multiplexing for parallel API calls
    </td>
  </tr>
</table>

</details>

<br/>

<details open>
<summary><kbd>FEATURE 4</kbd> <b>Dynamic Widget Generation</b></summary>
<br/>

<table>
  <tr>
    <td valign="top">
      <kbd>SCHEMA</kbd> Pydantic V2 models define type-safe widget structures.<br/><br/>
      <kbd>TYPES</kbd> Available widget types:<br/>
      • <b>ChartWidget</b> - Line, bar, pie, area charts (Recharts)<br/>
      • <b>StatsWidget</b> - Key metrics with trend indicators<br/>
      • <b>TextResponse</b> - Formatted markdown content<br/>
      • <b>AgentThinking</b> - Reasoning trace display<br/><br/>
      <kbd>FLOW</kbd> Backend generates → Protocol Type 2 → Zustand store → Auto-render
    </td>
  </tr>
</table>

**Widget Schema Example:**
```python
class ChartWidget(BaseModel):
    type: Literal["chart"] = "chart"
    title: str
    chart_type: Literal["line", "bar", "pie", "area"]
    data: List[DataPoint]
    ticker: Optional[str]
```

</details>

<br/>

<details open>
<summary><kbd>FEATURE 5</kbd> <b>Agent Graph Visualization</b></summary>
<br/>

<table>
  <tr>
    <td valign="top">
      <kbd>LIBRARY</kbd> <b>@xyflow/react</b> with Dagre layout for automatic graph positioning.<br/><br/>
      <kbd>NODES</kbd> Visual representation of agent execution:<br/>
      • <b>User</b> - Input node (blue)<br/>
      • <b>Agent</b> - Processing nodes (purple)<br/>
      • <b>Tool</b> - API call nodes (orange)<br/><br/>
      <kbd>METRICS</kbd> Real-time latency tracking per node<br/><br/>
      <kbd>TOPOLOGY</kbd> Extracted from Type 2 protocol events and rendered live
    </td>
  </tr>
</table>

</details>

<br/>

## Project Structure

```
stock-terminal-next/
├── backend/
│   ├── src/
│   │   ├── main.py                    # FastAPI app (800+ lines)
│   │   ├── protocol.py                # Vercel AI SDK protocol helpers
│   │   ├── schemas.py                 # Pydantic widget models
│   │   ├── smart_agent.py             # ADK Smart Agent factory
│   │   ├── neural_link_agent.py       # News/trends synthesis
│   │   ├── adk_comps_workflow.py      # Multi-agent comps analysis
│   │   ├── factset_core.py            # FactSet MCP integration
│   │   ├── market_data.py             # yfinance price fetching
│   │   └── tool_utils.py              # DelegatingTool wrapper
│   ├── pyproject.toml
│   └── .env                           # Environment variables
│
├── frontend/
│   ├── src/
│   │   ├── App.tsx                    # Root component
│   │   ├── context/
│   │   │   └── ChatContext.tsx        # useChat hook integration
│   │   ├── store/
│   │   │   └── dashboardStore.ts      # Zustand global state
│   │   ├── components/
│   │   │   ├── chat/
│   │   │   │   ├── ChatContainer.tsx  # Floating/docked chat
│   │   │   │   ├── AgentGraph.tsx     # Graph visualization
│   │   │   │   └── TraceLog.tsx       # Execution timeline
│   │   │   └── dashboard/
│   │   │       ├── DashboardView.tsx  # Main dashboard
│   │   │       ├── PerformanceChart.tsx
│   │   │       └── NeuralLinkView.tsx
│   │   └── index.css                  # Tailwind styles
│   ├── package.json
│   └── vite.config.ts
│
├── docs/
│   ├── comprehensive_mcp_report.md    # FactSet API test results
│   └── adk_schema_test_report.md      # ADK validation report
│
├── tests/
│   └── comps_analysis_test.py
│
├── diagram.jpeg                       # Architecture diagram
├── .env.example                       # Environment template
└── README.md
```

<br/>

## Getting Started

<blockquote>
  <p><b>PREREQUISITES:</b> Ensure you have Python 3.11+, Node.js 18+, and valid API credentials before proceeding.</p>
</blockquote>

<br/>

<details open>
<summary><kbd>PHASE 1</kbd> <b>Environment Configuration</b></summary>
<br/>

<table>
  <tr>
    <td valign="top">
      <kbd>EXECUTE</kbd> Copy the environment template:<br/>
      <code>cp .env.example .env</code><br/><br/>
      <kbd>CONFIGURE</kbd> Update <code>.env</code> with your credentials:
      <br/><br/>
<pre><code># Server Configuration
PORT=8001
FRONTEND_PORT=5173
FRONTEND_URL=http://localhost:5173
CORS_ORIGINS=http://localhost:5173

# FactSet OAuth (required for financial data)
FS_CLIENT_ID=your_factset_client_id
FS_CLIENT_SECRET=your_factset_secret
FS_REDIRECT_URI=http://localhost:8001/auth/callback

# Google Cloud (required for Gemini)
GOOGLE_API_KEY=your_google_api_key
GOOGLE_CLOUD_PROJECT=your_project_id
GOOGLE_CLOUD_LOCATION=us-central1
GOOGLE_GENAI_USE_VERTEXAI=true

# Vertex AI Search (optional - for RAG)
VAIS_PROJECT_ID=your_project_id
VAIS_LOCATION=global
VAIS_COLLECTION=default_collection
VAIS_ENGINE=stock-terminal-engine
VAIS_SERVING_CONFIG=default_config</code></pre>
    </td>
  </tr>
</table>

</details>

<br/>

<details open>
<summary><kbd>PHASE 2</kbd> <b>Backend Setup</b></summary>
<br/>

<table>
  <tr>
    <td valign="top">
      <kbd>EXECUTE</kbd> Navigate to backend directory:<br/>
      <code>cd backend</code><br/><br/>
      <kbd>VENV</kbd> Create and activate virtual environment:<br/>
      <code>python -m venv .venv</code><br/>
      <code>source .venv/bin/activate</code><br/><br/>
      <kbd>INSTALL</kbd> Install dependencies (using uv for speed):<br/>
      <code>uv pip install -r pyproject.toml</code><br/><br/>
      <i>Or with pip:</i><br/>
      <code>pip install -e .</code><br/><br/>
      <kbd>RUN</kbd> Start the FastAPI server:<br/>
      <code>uvicorn src.main:app --reload --port 8001</code><br/><br/>
      <kbd>VERIFY</kbd> Server running at <code>http://localhost:8001</code>
    </td>
  </tr>
</table>

**Key Dependencies:**
```
fastapi, uvicorn, pydantic>=2.0
google-genai, google-adk
mcp, httpx, httpx-sse
python-dotenv, yfinance
```

</details>

<br/>

<details open>
<summary><kbd>PHASE 3</kbd> <b>Frontend Setup</b></summary>
<br/>

<table>
  <tr>
    <td valign="top">
      <kbd>EXECUTE</kbd> Navigate to frontend directory:<br/>
      <code>cd frontend</code><br/><br/>
      <kbd>INSTALL</kbd> Install npm packages:<br/>
      <code>npm install</code><br/><br/>
      <kbd>RUN</kbd> Start the development server:<br/>
      <code>npm run dev</code><br/><br/>
      <kbd>ACCESS</kbd> Open <code>http://localhost:5173</code> in your browser
    </td>
  </tr>
</table>

**Key Dependencies:**
```
react@18, react-dom
ai@^3.0.19 (Vercel AI SDK)
zustand (state management)
framer-motion (animations)
recharts (charting)
@xyflow/react (graph visualization)
tailwindcss, typescript, vite
```

</details>

<br/>

<details open>
<summary><kbd>PHASE 4</kbd> <b>FactSet Authentication</b></summary>
<br/>

<table>
  <tr>
    <td valign="top">
      <kbd>NAVIGATE</kbd> Visit <code>http://localhost:8001/auth/factset/url</code><br/><br/>
      <kbd>AUTHORIZE</kbd> Complete OAuth flow with your FactSet credentials<br/><br/>
      <kbd>CALLBACK</kbd> You'll be redirected back with tokens stored automatically<br/><br/>
      <kbd>VERIFY</kbd> Check status at <code>http://localhost:8001/auth/factset/status</code><br/><br/>
      <kbd>NOTE</kbd> Tokens auto-refresh; sessions stored in SQLite
    </td>
  </tr>
</table>

</details>

<br/>

## Usage Examples

<blockquote>
  <p><b>INTERACTION:</b> Type natural language queries in the chat interface. The AI orchestrator will automatically invoke the appropriate tools.</p>
</blockquote>

### Basic Stock Analysis
```
User: "Show me a chart of AAPL stock price"

→ Backend streams ChartWidget (Protocol Type 2)
→ Frontend useChat hook catches data block
→ Zustand store updates activeWidget
→ Dashboard renders Recharts LineChart
```

### Comparative Analysis
```
User: "Compare NVDA with its top competitors"

→ Discovery Agent: finds AMD, INTC, AVGO via Google Search
→ 3x Parallel Research Agents: deep dive each peer
→ Synthesis: aggregates into battlecard format
→ Frontend renders CompsAnalysisView grid
```

### Neural Intelligence
```
User: "What's the market sentiment on TSLA?"

→ Neural Link Agent activates
  → News Agent: official news + analyst moves
  → Rumor Agent: Reddit, Twitter, StockTwits scan
→ Returns NeuralCard[] with sentiment scores
→ Dashboard shows trend indicators
```

<br/>

## API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/chat` | POST | Main streaming chat endpoint |
| `/comps` | POST | Multi-agent comps analysis (SSE stream) |
| `/neural_link/trends/{ticker}` | GET | Neural trends for ticker |
| `/neural_link/deep_dive/{ticker}/{category}` | GET | Deep dive analysis |
| `/news_hub/{ticker}` | GET | SemiAI news videos |
| `/auth/factset/url` | GET | FactSet OAuth URL |
| `/auth/factset/callback` | GET | OAuth callback handler |
| `/auth/factset/status` | GET | Check auth status |

<br/>

## State Management

The frontend uses **Zustand** for global state with reactive updates:

```typescript
interface DashboardState {
  // Ticker
  ticker: string;                    // Current symbol (default: 'FDS')
  tickerData: any | null;            // Company info

  // Views
  activeView: string;                // Snapshot, Profile, Valuation...
  currentView: 'dashboard' | 'neural_link' | 'advanced_search';

  // Widgets
  activeWidget: WidgetData | null;   // Currently displayed widget
  chartOverride: any | null;         // Override chart from AI

  // Chat UI
  chatDockPosition: 'floating' | 'left' | 'right';
  isChatOpen: boolean;
  isChatMaximized: boolean;

  // Execution Metrics
  topology: ProcessorTopology | null;  // Agent graph data
  nodeDurations: Record<string, number>;
  executionPath: string[];

  // Theme
  theme: 'light' | 'dark';
}
```

<br/>

## Supported Models

| Model | ID | Use Case |
|-------|-----|----------|
| Gemini 2.5 Flash | `gemini-2.5-flash` | Fast responses (default) |
| Gemini 2.5 Flash Lite | `gemini-2.5-flash-lite` | Cost-optimized |
| Gemini 3.0 Flash Preview | `gemini-3-flash-preview` | Latest features |

<br/>

## Security

<blockquote>
  <p><b>ZERO-LEAK POLICY:</b> This project follows strict secret management protocols. Never commit credentials.</p>
</blockquote>

**Implemented Protections:**
- OAuth 2.0 with automatic token refresh
- CORS restricted to configured origins
- Pydantic validation on all inputs
- Session isolation per user
- `.env` excluded from version control

**Recommended for Production:**
- Rate limiting on `/chat` endpoint
- API key rotation schedule
- Request logging and audit trail
- mTLS for service-to-service communication

<br/>

## Testing

```bash
# Run backend tests
cd backend
pytest tests/

# Run specific test
pytest tests/comps_analysis_test.py -v

# Test FactSet integration
pytest src/test_factset.py -v
```

**Test Coverage:**
- `comps_analysis_test.py` - Comps workflow integration
- `test_factset.py` - FactSet API connectivity
- `test_discovery.py` - Peer discovery logic
- `test_insights_latency.py` - Performance benchmarks

<br/>

## Performance

| Metric | Value |
|--------|-------|
| First Token Latency | < 500ms |
| Tool Execution | 1-3s per API call |
| Full Analysis | 5-15s (parallel tools) |
| UI Update Frequency | Real-time (streaming) |
| HTTP/2 Multiplexing | 6+ concurrent requests |

<br/>

## Documentation

- [FactSet MCP Test Report](./docs/comprehensive_mcp_report.md) - 41 queries tested, 97.6% success rate
- [ADK Schema Validation](./docs/adk_schema_test_report.md) - Tool schema compliance report

<br/>

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

<br/>

## License

This project is licensed under the Apache 2.0 License - see the [LICENSE](LICENSE) file for details.

<br/>

---

<div align="center">
  <sub>Built with Google ADK, FactSet MCP, and Vercel AI SDK</sub>
</div>
