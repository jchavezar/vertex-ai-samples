# 08 - ADK Agent: Internal vs External Insight Comparator

**Version:** 1.1.0  
**Last Updated:** 2026-04-04  
**Status:** Production

**Navigation**: [Index](00-INDEX.md) | [01-GCP](01-SETUP-GCP.md) | [02-Entra](02-SETUP-ENTRA.md) | [03-WIF](03-SETUP-WIF.md) | [04-Discovery](04-SETUP-DISCOVERY.md) | **08-Agent** | [Testing](TESTING.md)

---

## Prerequisites

All previous setup steps must be complete:

| From | Variable | Purpose |
|------|----------|---------|
| [01-SETUP-GCP.md](01-SETUP-GCP.md) | `PROJECT_ID`, `PROJECT_NUMBER` | Agent deployment |
| [01-SETUP-GCP.md](01-SETUP-GCP.md) | `STAGING_BUCKET` | Agent Engine staging |
| [02-SETUP-ENTRA.md](02-SETUP-ENTRA.md) | `TENANT_ID`, `OAUTH_CLIENT_ID` | Authorization |
| [02-SETUP-ENTRA.md](02-SETUP-ENTRA.md) | `OAUTH_CLIENT_SECRET` | Token exchange |
| [03-SETUP-WIF.md](03-SETUP-WIF.md) | `WIF_POOL_ID` | Token exchange |
| [03-SETUP-WIF.md](03-SETUP-WIF.md) | `entra-provider` | **MUST use this provider** |
| [04-SETUP-DISCOVERY.md](04-SETUP-DISCOVERY.md) | `ENGINE_ID`, `DATA_STORE_ID` | SharePoint search |

---

## Outputs

| Variable | Example | Used In |
|----------|---------|---------|
| `REASONING_ENGINE_RES` | `projects/.../reasoningEngines/...` | [TESTING.md](TESTING.md) |
| `AUTH_ID` | `sharepointauth2` | [TESTING.md](TESTING.md) |

---

## Overview

Deploys an ADK Agent to Gemini Enterprise that compares internal SharePoint documents with external web sources using a single `compare_insights` tool.

```
+===============================================================================+
|                        InsightComparator Agent                                 |
|                        (gemini-2.5-flash-lite)                                |
|                                                                                |
|   +-----------------------------------------------------------------------+   |
|   |                       compare_insights tool                            |   |
|   |                                                                        |   |
|   |   Executes BOTH searches concurrently:                                |   |
|   |                                                                        |   |
|   |   +---------------------------+   +---------------------------+       |   |
|   |   |      SharePoint Search    |   |      Google Search        |       |   |
|   |   |      (Discovery Engine)   |   |      (Gemini Grounding)   |       |   |
|   |   |                           |   |                           |       |   |
|   |   |  - WIF token exchange     |   |  - gemini-2.5-flash-lite  |       |   |
|   |   |  - ACL-aware results      |   |  - googleSearch tool      |       |   |
|   |   |  - dataStoreSpecs         |   |  - Public web grounding   |       |   |
|   |   +---------------------------+   +---------------------------+       |   |
|   |                 |                           |                          |   |
|   |                 +-------------+-------------+                          |   |
|   |                               |                                        |   |
|   |                               v                                        |   |
|   |                   +------------------------+                           |   |
|   |                   |  Structured Response   |                           |   |
|   |                   |  - internal_findings   |                           |   |
|   |                   |  - external_findings   |                           |   |
|   |                   +------------------------+                           |   |
|   +-----------------------------------------------------------------------+   |
|                                                                                |
+===============================================================================+
```

---

## Development Timeline

| Date | Time | Phase | Action |
|------|------|-------|--------|
| 2026-04-04 | 08:46 | Setup | Environment configuration |
| 2026-04-04 | 09:20 | Code | Agent + tools implementation |
| 2026-04-04 | 09:29 | Test | Local testing (test_local.py) |
| 2026-04-04 | 09:31 | Deploy | First Agent Engine deployment |
| 2026-04-04 | 10:37 | Fix | Authorization scope (user_impersonation) |
| 2026-04-04 | 12:47 | Fix | WIF provider audience mismatch |
| 2026-04-04 | 13:17 | Deploy | Final deployment with entra-provider |
| 2026-04-04 | 13:20 | Verify | Production verified working |

---

## WIF Provider Configuration

**Critical:** The agent must use `entra-provider` (with `api://` audience) for WIF token exchange.

```
+-----------------------------------------------------------------------+
|                    WIF AUDIENCE MATCHING                               |
|                                                                        |
|   Authorization Token                 WIF Provider                     |
|   (from sharepointauth2)              (for agent)                      |
|                                                                        |
|   aud: "api://7868d053-..."    --->   entra-provider                  |
|                                        (expects api:// prefix)         |
|                                                                        |
|   GE Login Token                      WIF Provider                     |
|   (from user login)                   (for GE)                         |
|                                                                        |
|   aud: "7868d053-..."          --->   ge-login-provider               |
|                                        (NO api:// prefix)              |
+-----------------------------------------------------------------------+
```

### Environment Variable

```bash
# .env - MUST use entra-provider for agent
WIF_PROVIDER_ID=entra-provider
```

---

## Step 1: Configure Environment

```bash
cd sharepoint_wif_portal
cp .env.example .env
```

Edit `.env`:

```bash
# GCP
PROJECT_ID=sharepoint-wif-agent
PROJECT_NUMBER=REDACTED_PROJECT_NUMBER
LOCATION=us-central1
STAGING_BUCKET=gs://sharepoint-wif-agent-staging

# Discovery Engine
ENGINE_ID=gemini-enterprise
DATA_STORE_ID=sharepoint-data-def-connector_file

# WIF (Critical: entra-provider)
WIF_POOL_ID=sp-wif-pool-v2
WIF_PROVIDER_ID=entra-provider    # <-- MUST be entra-provider

# Authorization
AUTH_ID=sharepointauth2

# Entra ID
TENANT_ID=your-tenant-id
OAUTH_CLIENT_ID=your-client-id
OAUTH_CLIENT_SECRET=your-secret

# Agentspace
AS_APP=gemini-enterprise

# ADK
GOOGLE_GENAI_USE_VERTEXAI=True
GOOGLE_CLOUD_PROJECT=sharepoint-wif-agent
GOOGLE_CLOUD_LOCATION=us-central1
```

---

## Step 2: Install Dependencies

```bash
# Requires uv (https://github.com/astral-sh/uv)
uv sync
```

Dependencies installed:
- `google-cloud-aiplatform[adk,agent_engines]>=1.88.0`
- `google-cloud-discoveryengine>=0.13.0`
- `httpx>=0.28.0`
- `python-dotenv>=1.0.0`

---

## Step 3: Test Locally

```bash
uv run python test_local.py
```

Expected output:

```
============================================================
           LOCAL TESTING - InsightComparator Agent
============================================================

Phase 1: Direct Tool Testing
------------------------------------------------------------
Project Number: REDACTED_PROJECT_NUMBER
Engine ID:      gemini-enterprise
[Test] Calling Discovery Engine with service account...
[OK] Answer: Based on the documents...
[OK] Sources: 3

Phase 2: Agent Conversation Testing
------------------------------------------------------------
Agent:  InsightComparator
Model:  gemini-2.5-flash-lite
Tools:  ['compare_insights']

[Query] What are best practices for cloud security?
------------------------------------------------------------
## Internal Findings (SharePoint)
...

## External Findings (Web)
...
------------------------------------------------------------
```

---

## Step 4: Deploy to Agent Engine

```bash
uv run python deploy.py
```

Output:

```
=====================================
Deploying Insight Comparator Agent
=====================================
Project:  sharepoint-wif-agent
Location: us-central1
Staging:  gs://sharepoint-wif-agent-staging
=====================================
Creating Agent Engine deployment...
=====================================
Deployment Complete!
=====================================
Resource Name: projects/REDACTED_PROJECT_NUMBER/locations/us-central1/reasoningEngines/1452886418605998080
=====================================
```

Add to `.env`:

```bash
REASONING_ENGINE_RES=projects/REDACTED_PROJECT_NUMBER/locations/us-central1/reasoningEngines/1452886418605998080
```

---

## Step 5: Test Remote Deployment

```bash
uv run python test_remote.py
```

---

## Step 6: Register Authorization

```bash
chmod +x register_auth.sh
./register_auth.sh
```

**Critical scope in register_auth.sh:**

```bash
# Must include user_impersonation for WIF token exchange
"scopes": ["api://'${OAUTH_CLIENT_ID}'/user_impersonation"]
```

---

## Step 7: Register Agent to Agentspace

```bash
chmod +x register_agent.sh
./register_agent.sh
```

Agent appears in Gemini Enterprise UI.

---

## Agent Output Format

```markdown
## Internal Findings (SharePoint)
[Summary from internal_findings.answer]
- Key points from company documents
- Sources: [Document titles/links]

## External Findings (Web)
[Summary from external_findings.answer]
- Key points from public sources
- Sources: [Website titles/links]

## Synthesis
- What aligns between internal and external?
- What's unique to internal documents?
- What external context adds value?
- Recommendations
```

---

## Dynamic AUTH_ID Detection

The agent auto-detects AUTH_ID from `tool_context.state`:

```python
# Priority order:
1. AUTH_ID env var override
2. Pattern match "temp:*" keys (Agentspace runtime)
3. Common key names: sharepointauth, sharepointauth2, msauth
```

---

## Files Reference

| File | Version | Purpose |
|------|---------|---------|
| `agent/agent.py` | 1.0.1 | Agent + compare_insights tool |
| `agent/discovery_engine.py` | 1.0.0 | WIF token exchange + DE client |
| `deploy.py` | 1.0.0 | Deploy to Agent Engine |
| `test_local.py` | 1.0.0 | Pre-deployment testing |
| `test_remote.py` | 1.0.0 | Post-deployment testing |
| `register_auth.sh` | 1.0.0 | OAuth authorization |
| `register_agent.sh` | 1.0.0 | Agentspace registration |

---

## Troubleshooting

### WIF Audience Mismatch (403 on SharePoint)

**Error:**
```
WIF STS error: {"error":"invalid_grant","error_description":"The audience in ID Token [api://7868d053-...] does not match the expected audience."}
```

**Solution:**
```bash
# Change WIF_PROVIDER_ID to entra-provider
WIF_PROVIDER_ID=entra-provider

# Redeploy
uv run python deploy.py update
```

### Authorization Loop

**Error:** "The agent requires additional authorization for: sharepointauth2"

**Solution:** Add `user_impersonation` scope to authorization in `register_auth.sh`:

```bash
"scopes": ["api://${OAUTH_CLIENT_ID}/user_impersonation"]
```

### Agent Not Visible in GE

**Solution:** Verify `sharingConfig.scope = "ALL_USERS"` in agent registration.

---

## Update Workflow

```bash
# Edit agent code
vim agent/agent.py

# Test locally
uv run python test_local.py

# Deploy update
uv run python deploy.py update

# Test remotely
uv run python test_remote.py
```
