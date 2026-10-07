# 🌟 Google Agent Development Kit (ADK) — Real-Time Intelligence Showcase

A clean, production-grade demonstration of the **Google Agent Development Kit (ADK)** using pure Python. This project is specifically organized for live demonstrations where you show the code directly in your IDE (VS Code, PyCharm, or Zed) and run real-time multi-tool interactions in the integrated terminal.

---

## 🎯 What This Demo Showcases

1. **Pure Python ADK Architecture**: No unnecessary wrappers or bloated frameworks — just clean, readable Google ADK code (`google.adk.agents.Agent` and `google.adk.runners.InMemoryRunner`).
2. **Real-World Live Tools (Zero API Keys Needed)**:
   - 📈 `get_stock_quote`: Real-time stock / ETF price, day change, and trading metrics via live market feeds.
   - 🏢 `get_company_profile`: Corporate background, industry, sector, market cap, and business summary.
   - 🌍 `get_live_weather`: Live worldwide weather, temperature (°C/°F), wind speed, and conditions via Open-Meteo.
   - 🪙 `get_crypto_quote`: Live cryptocurrency pricing and 24-hour trends (Bitcoin, Ethereum, Solana, etc.).
3. **Real-Time Event Streaming**:
   - Live visual cues when the agent triggers tool calls.
   - Live inspection of raw tool execution results returned to the agent.
   - Streaming token synthesis and markdown rendering in the terminal.
4. **Multi-Turn Stateful Sessions**:
   - `InMemorySessionService` maintains conversational memory across questions (e.g., follow-up queries comparing figures).

---

## 📂 Project Structure (IDE View)

When presenting in your IDE, the codebase is cleanly partitioned into three key files:

```
adk-realtime-intelligence/
├── app/
│   ├── __init__.py
│   ├── agent.py          # 🧠 The ADK Agent definition, model config, and tool bindings
│   └── tools.py          # 🔧 Pure Python function tools with typed docstrings
├── main.py               # 🚀 Real-time interactive CLI runner streaming ADK events
├── .env                  # ⚙️ Local Vertex AI configuration (gitignored)
├── .env.example          # 📄 Environment template
├── pyproject.toml        # 📦 Packaging configuration
├── requirements.txt      # 📋 Python dependencies
└── README.md             # 📖 Walkthrough & presentation guide
```

---

## ⚡ Quick Start

### 1. Ensure Prerequisites
Make sure your Google Cloud credentials are authenticated:
```bash
gcloud auth application-default login
```

### 2. Configure Environment
Copy `.env.example` to `.env` (already done by default in this workspace):
```bash
cp .env.example .env
```
Contents:
```env
GOOGLE_GENAI_USE_VERTEXAI=True
GOOGLE_CLOUD_PROJECT=vtxdemos
GOOGLE_CLOUD_LOCATION=global
MODEL_NAME=gemini-3.8-flash
```

### 3. Run Options

#### Option A: Official Google ADK Web UI (Currently Live on Port 8085)
- **Web UI & Playground**: [http://127.0.0.1:8085/dev-ui/](http://127.0.0.1:8085/dev-ui/)
- **FastAPI Swagger Docs**: [http://127.0.0.1:8085/docs](http://127.0.0.1:8085/docs)
- **Launch Command**:
  ```bash
  adk web --port 8085 .
  ```

#### Option B: Live Streaming CLI Runner (In Your IDE Terminal)
```bash
python main.py
```
*(Or with uv: `uv run python main.py`)*

---

## 🎤 IDE Presentation Walkthrough (Speaking Points)

When presenting the code to an audience, follow this recommended 3-step walkthrough:

### Step 1: Show `app/tools.py` (How ADK Handles Tools)
- **Point out**: "In Google ADK, tools are simply native Python functions."
- **Highlight**:
  - Type annotations (`ticker: str -> Dict[str, Any]`).
  - Google-style docstrings (`Args`, `Returns`).
  - Explain: *"ADK automatically converts these docstrings and type hints into Gemini tool definitions (OpenAPI JSON schemas). Developers do not need to write boilerplate schemas manually."*
- Show that these functions make real HTTP calls to live services with zero API key friction.

### Step 2: Show `app/agent.py` (The Agent Definition)
- **Point out**: "Here is the core ADK `Agent` instance (`root_agent`)."
- **Highlight**:
  ```python
  root_agent = Agent(
      name="realtime_intelligence_agent",
      model="gemini-3.8-flash",
      instruction=SYSTEM_INSTRUCTION,
      tools=[get_stock_quote, get_company_profile, get_live_weather, get_crypto_quote],
  )
  ```
- **Explain**:
  - `model`: Uses Google's state-of-the-art **Gemini 3.8 Flash** via Vertex AI for high-speed multi-tool reasoning.
  - `instruction`: Clear system guidelines instructing the agent to ground answers with real-time data.
  - `tools`: Direct array of Python functions.

### Step 3: Show `main.py` & Run Live
- **Point out**: "ADK separates the agent definition from the execution runner."
- **Highlight**:
  - `InMemoryRunner(agent=root_agent, app_name="adk_realtime_app")`
  - `runner.session_service.create_session(...)` — maintains session history across questions.
  - `async for event in runner.run_async(...)` — the event stream yielding function calls, function responses, and generated tokens in real time.
- **Run the demo**: Open the terminal pane in your IDE, run `python main.py`, and choose:
  - **Option 1**: Multi-tool parallel execution:
    > *"What is Alphabet (GOOGL) trading at right now compared to Apple (AAPL), and what is the current weather in Tokyo?"*
    *(Watch the agent trigger two stock queries and one weather query concurrently!)*
  - **Option 2**: Crypto & Equities pulse:
    > *"Give me the live price of Bitcoin (BTC) and Ethereum (ETH), plus Nvidia (NVDA) stock."*
  - **Custom Prompt**: Ask any follow-up question in the same session to demonstrate context retention!

---

## 🔒 Security & Zero-Leak Protocol
- `.gitignore` enforces the strict zero-leak exclusion policy (`.env`, `credentials.json`, `*.pem`, `*.key`).
- No private API keys or secrets are required for the real-time tools.
