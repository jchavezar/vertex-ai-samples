# SharePoint WIF Portal - ADK Agent

**Internal vs External Insight Comparator**

ADK Agent that compares SharePoint documents (internal) with Google Search results (external) using a single `compare_insights` tool.

**Version:** 1.1.0  
**Date:** 2026-04-04  
**Last Deployed:** 2026-04-04 13:17 UTC

---

## Features

- **Single Tool Design** - `compare_insights` executes both searches concurrently
- **SharePoint Search** - Discovery Engine with WIF token exchange (ACL-aware)
- **Google Search** - Gemini with googleSearch grounding
- **Structured Output** - Internal findings, external findings, synthesis
- **Dynamic AUTH_ID** - Auto-detects from `tool_context.state` keys
- **Agent Engine Env Vars** - Uses `CLOUD_ML_PROJECT_ID` when deployed

---

## Architecture

```
+===============================================================================+
|                        Gemini Enterprise                                       |
|                                                                                |
|   User Query --> InsightComparator Agent (gemini-2.5-flash-lite)              |
|                         |                                                      |
|                         v                                                      |
|               +-------------------+                                            |
|               | compare_insights  |                                            |
|               | (single tool)     |                                            |
|               +--------+----------+                                            |
|                        |                                                       |
|           +------------+------------+                                          |
|           |                         |                                          |
|           v                         v                                          |
|   +---------------+         +---------------+                                  |
|   | SharePoint    |         | Google Search |                                  |
|   | (WIF/ACL)     |         | (grounding)   |                                  |
|   +---------------+         +---------------+                                  |
|           |                         |                                          |
|           v                         v                                          |
|   Internal Docs             Public Web                                         |
|           |                         |                                          |
|           +------------+------------+                                          |
|                        |                                                       |
|                        v                                                       |
|              +------------------+                                              |
|              | Structured Output|                                              |
|              |                  |                                              |
|              | Internal Findings|                                              |
|              | External Findings|                                              |
|              | Synthesis        |                                              |
|              +------------------+                                              |
+===============================================================================+
```

---

## WIF Provider (Critical)

The agent must use `entra-provider` (with `api://` audience) for WIF token exchange.

```
Authorization Token              WIF Provider
(from sharepointauth2)           (in .env)
                    
aud: "api://7868d053..."   -->   WIF_PROVIDER_ID=entra-provider
                                 (expects api:// prefix)
```

---

## Setup

### 1. Prerequisites

- GCP project with Discovery Engine enabled
- SharePoint datastore configured
- WIF pool with two providers:
  - `ge-login-provider` - for GE login (no api://)
  - `entra-provider` - for agent WIF (with api://)
- Microsoft Entra ID app with `user_impersonation` scope

### 2. Configure Environment

```bash
cp .env.example .env
# Edit .env - ensure WIF_PROVIDER_ID=entra-provider
```

### 3. Install Dependencies

```bash
uv sync
```

### 4. Test Locally

```bash
uv run python test_local.py
```

---

## Deployment

### 1. Deploy to Agent Engine

```bash
uv run python deploy.py
# Save REASONING_ENGINE_RES to .env
```

### 2. Test Remote

```bash
uv run python test_remote.py
```

### 3. Register Authorization

```bash
./register_auth.sh
```

### 4. Register Agent

```bash
./register_agent.sh
```

---

## Configuration

| Variable | Value | Description |
|----------|-------|-------------|
| `PROJECT_NUMBER` | REDACTED_PROJECT_NUMBER | GCP project number |
| `ENGINE_ID` | gemini-enterprise | Discovery Engine |
| `DATA_STORE_ID` | sharepoint-data-def-connector_file | SharePoint datastore |
| `WIF_POOL_ID` | sp-wif-pool-v2 | WIF pool |
| `WIF_PROVIDER_ID` | **entra-provider** | MUST be entra-provider |
| `AUTH_ID` | sharepointauth2 | Authorization resource |

---

## Files

| File | Version | Purpose |
|------|---------|---------|
| `agent.py` | 1.1.0 | Agent + compare_insights tool |
| `discovery_engine.py` | 1.1.0 | WIF exchange + DE client |
| `__init__.py` | - | Exports root_agent |

---

## Token Flow

```
+----------------+     +---------------+     +-----------------+
| Microsoft      |     | WIF/STS       |     | Discovery       |
| Entra ID       |---->| Token Exchange|---->| Engine          |
| (api:// aud)   |     | (entra-prov)  |     | (ACL search)    |
+----------------+     +---------------+     +-----------------+
```
