# Test UI - InsightComparator Agent

**Version:** 1.0.0  
**Date:** 2026-04-04

Quick UI to login with Microsoft and test the agent with real SharePoint access.

---

## Architecture

```
+===============================================================+
|                         TEST UI                                |
|                                                                |
|   Browser (localhost:8080)                                     |
|   +----------------------------------------------------------+ |
|   |  [Login with Microsoft]                                   | |
|   |                                                           | |
|   |  Query: [________________________]  [Send]                | |
|   |                                                           | |
|   |  Response:                                                | |
|   |  +------------------------------------------------------+ | |
|   |  | ## Internal Findings (SharePoint)                    | | |
|   |  | ...                                                  | | |
|   |  | ## External Findings (Web)                           | | |
|   |  | ...                                                  | | |
|   |  +------------------------------------------------------+ | |
|   +----------------------------------------------------------+ |
|        |                                                       |
|        v                                                       |
|   FastAPI Server (:8080)                                       |
|        |                                                       |
|        +-- MSAL Login --> Microsoft Entra ID                   |
|        |                      |                                |
|        |                      v                                |
|        |                  JWT Token                            |
|        |                      |                                |
|        +-- /api/query --------+                                |
|                |                                               |
|                v                                               |
|        Agent Engine SDK                                        |
|                |                                               |
|                v                                               |
|        InsightComparator Agent                                 |
|                |                                               |
|        +-------+-------+                                       |
|        |               |                                       |
|        v               v                                       |
|   SharePoint      Google Search                                |
|   (with ACL)      (public)                                     |
+===============================================================+
```

---

## Quick Start

```bash
# 1. Navigate to test_ui
cd test_ui

# 2. Install dependencies
uv sync

# 3. Run server
uv run python server.py

# 4. Open browser
open http://localhost:8080

# 5. Click "Login with Microsoft"

# 6. Enter query and click "Send Query"
```

---

## What It Does

1. **Login** - Uses MSAL.js to authenticate with Microsoft Entra ID
2. **Get Token** - Acquires access token with `user_impersonation` scope
3. **Save Token** - Saves token to `/tmp/entra_token.txt` for CLI testing
4. **Query Agent** - Sends query to deployed Agent Engine with token

---

## Token for CLI Testing

After login, the token is saved to `/tmp/entra_token.txt`.

Use it with other test scripts:

```bash
# From parent directory
uv run python test_local.py --with-token
uv run python test_remote.py --with-token
```

---

## Prerequisites

From parent `.env`:

| Variable | Required |
|----------|----------|
| `PROJECT_ID` | Yes |
| `PROJECT_NUMBER` | Yes |
| `OAUTH_CLIENT_ID` | Yes |
| `TENANT_ID` | Yes |
| `REASONING_ENGINE_RES` | Yes |

---

## Entra ID Configuration

The app registration must have:

1. **SPA Platform** with redirect URI: `http://localhost:8080`
2. **Custom Scope**: `api://{client-id}/user_impersonation`
3. **Implicit Flow**: Enabled in manifest (`oauth2AllowIdTokenImplicitFlow: true`)

---

## Troubleshooting

| Issue | Solution |
|-------|----------|
| Login popup blocked | Allow popups for localhost |
| "Invalid redirect URI" | Add `http://localhost:8080` to SPA platform |
| Token not acquired | Check browser console for MSAL errors |
| SharePoint 403 | Token audience must match WIF provider |
