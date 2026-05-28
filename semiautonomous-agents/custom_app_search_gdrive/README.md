# Paramount Drive Search — Vertex AI

AI-powered semantic search across Google Drive, secured by Google OAuth 2.0 and enforced by Drive ACL. Built with FastAPI + Vertex AI Search (Discovery Engine) and deployed to Cloud Run.

---

## Overview

Users sign in with their Paramount Google account. On every search the backend fires two parallel Discovery Engine calls — one for results (fast, no AI generation) and one for an AI summary. Results stream immediately via SSE; the AI summary card populates separately once generation finishes. All results are filtered server-side: users only see files they have Drive access to.

---

## Architecture

```
Browser
  │  1. google.accounts.id.initialize  ──► Google Auth
  │     → ID token (JWT)
  │  2. google.accounts.oauth2.initTokenClient (cloud-platform scope)
  │     → OAuth access token
  │
  │  3. POST /api/search { query, credential, access_token }
  ▼
FastAPI (Cloud Run)
  ├── verify_oauth2_token(credential)  ──► Google Auth public keys
  ├── GET /oauth2/v3/tokeninfo          ──► validate access token, confirm email match
  │
  └── ThreadPoolExecutor(max_workers=2)
        ├── POST :search  (fast — no summarySpec)   ──► Vertex AI Search
        │     → SSE: { type: "results", data: { results, total, user } }
        └── POST :search  (summary — summarySpec)   ──► Vertex AI Search
              → SSE: { type: "summary", data: { summaryText } }
```

### Why two parallel calls?

Discovery Engine's AI summary generation (Grounded Generation) adds 1–3 s of latency. By issuing a fast call without `summarySpec` and a second call with only `summarySpec`, file results appear in ~400 ms while the summary card loads in parallel. The user never stares at a blank screen.

### Why user tokens, not a service account?

Vertex AI Search Workspace datastores (Drive connector) enforce Drive ACL by checking the caller's identity. Service accounts receive `PERMISSION_DENIED`. The user's own OAuth access token must be passed as `Authorization: Bearer` on every Discovery Engine request.

---

## Auth Flow

| Step | From | To | What happens |
|------|------|----|--------------|
| 1 | Browser | Google Auth | GSI popup — user authenticates, grants `cloud-platform` scope |
| 2 | Google Auth | Browser | ID token (JWT) + access token issued, held **in memory only** |
| 3 | Browser | FastAPI | `POST /api/search` — query + both tokens sent over HTTPS |
| 4 | FastAPI | Google Auth | `verify_oauth2_token()` — cryptographic JWT signature check |
| 5 | FastAPI | Google Auth | `GET /tokeninfo` — validates access token, confirms email match |
| 6 | FastAPI | Vertex AI Search | Two parallel `default_search:search` calls with `Bearer <user_token>` |
| 7 | Vertex AI Search | FastAPI | ACL-filtered results + AI summary returned |
| 8 | FastAPI | Browser | SSE: `results` event first, then `summary` event |

Tokens are never stored — they live only in browser memory for the duration of the session.

---

## Project Structure

```
custom_app_search_gdrive/
├── app/
│   └── main.py          # FastAPI — auth verification, parallel DE calls, SSE stream
├── static/
│   └── index.html       # Single-page app — GSI, OAuth token flow, result rendering
├── Dockerfile
├── deploy.sh
└── README.md
```

### `app/main.py` key functions

| Function | Purpose |
|----------|---------|
| `_verify_token(credential)` | Verifies Google ID token signature via `google-auth` |
| `_get_token_email(access_token)` | Calls `/oauth2/v3/tokeninfo` to validate the access token |
| `_stream(req)` | Generator — yields SSE events through the full auth + search pipeline |

### `static/index.html` key functions

| Function | Purpose |
|----------|---------|
| `initGSI(cid)` | Initializes Google Identity Services and OAuth token client |
| `handleCredentialResponse(resp)` | Receives ID token after sign-in; triggers access token request |
| `handleTokenResponse(tokenResp)` | Stores access token; transitions to search screen |
| `doSearch()` | Reads query, POSTs to `/api/search`, reads SSE stream |
| `handleStreamEvent(ev)` | Routes `log` / `results` / `summary` / `error` events |
| `renderResults(data)` | Renders result cards with SVG file icons; shows summary placeholder |
| `renderSummary(text)` | Populates the AI summary card when generation completes |
| `getFileIcon(mime)` | Returns colored inline SVG for Docs / Sheets / Slides / PDF / Folder / Image |
| `switchTab(name)` | Toggles Steps ↔ Flow Diagram tab; triggers SVG draw-in animation on entry |
| `openAuthFlow()` / `closeAuthFlow()` | Auth overlay open/close (Esc and backdrop-click supported) |
| `logEntry(level, step, tag, msg, detail)` | Appends entry to the live event log panel (right column) |
| `safeSnippet(s)` | Decodes HTML entities, strips all tags except `<b>` and `<em>` |

---

## Configuration

| Environment Variable | Description | Default |
|---|---|---|
| `PROJECT_ID` | GCP project number or ID | `254356041555` |
| `ENGINE_ID` | Discovery Engine engine ID | `vais-workspace_1779830576232` |
| `GOOGLE_OAUTH_CLIENT_ID` | OAuth 2.0 Web Client ID | *(required)* |

The OAuth Client ID is also hardcoded in `static/index.html` as `window.APP_CONFIG.clientId`. It is a public identifier — embedding it in frontend code is safe and expected by Google.

---

## Prerequisites

1. **GCP project** with Vertex AI Search and Discovery Engine APIs enabled
2. **Workspace datastore** — Drive connector configured and indexed under a Discovery Engine app
3. **OAuth 2.0 Client ID** (Web application type) with:
   - Authorized JavaScript origin: your Cloud Run URL (and `http://localhost:8080` for local dev)
   - No redirect URI required (implicit token flow via GSI)
4. `gcloud` CLI authenticated with an account that has Cloud Build / Cloud Run permissions on the target project

---

## Local Development

```bash
pip install -r requirements.txt

export PROJECT_ID=254356041555
export ENGINE_ID=vais-workspace_1779830576232
export GOOGLE_OAUTH_CLIENT_ID=254356041555-9b04u6obh8efjp6erog7fj12fnviop71.apps.googleusercontent.com

uvicorn app.main:app --reload --port 8080
```

Open `http://localhost:8080`. You must have `http://localhost:8080` listed as an authorized JavaScript origin in the OAuth client, otherwise the Google Sign-In button will not render.

---

## Deployment

```bash
./deploy.sh
```

Or manually:

```bash
PROJECT=vtxdemos
REGION=us-central1
IMAGE=gcr.io/$PROJECT/vais-gdrive-search

gcloud builds submit --tag $IMAGE --project $PROJECT

gcloud run deploy vais-gdrive-search \
  --image $IMAGE \
  --platform managed \
  --region $REGION \
  --allow-unauthenticated \
  --set-env-vars "PROJECT_ID=254356041555,ENGINE_ID=vais-workspace_1779830576232,GOOGLE_OAUTH_CLIENT_ID=254356041555-9b04u6obh8efjp6erog7fj12fnviop71.apps.googleusercontent.com" \
  --project $PROJECT
```

> **First deploy:** Cloud Run assigns a URL only after the initial deploy. Deploy once, copy the URL, add it to the OAuth client's authorized JavaScript origins, then deploy again.

---

## API Reference

### `POST /api/search`

Streams Server-Sent Events over `text/event-stream`.

**Request body (JSON):**
```json
{
  "query": "quarterly earnings report",
  "credential": "<google-id-token>",
  "access_token": "<oauth-access-token>",
  "page_size": 10
}
```

**SSE event types:**

| `type` | Payload fields | Fired when |
|--------|---------------|------------|
| `log` | `level`, `step`, `tag`, `message`, `detail` | Each processing step (auth verify, API call, parse) |
| `results` | `data.results[]`, `data.total`, `data.user` | Fast DE call completes (~400 ms) |
| `summary` | `data.summaryText` | AI summary generation completes (~1–3 s) |
| `error` | `message` | Any failure (auth, API, token mismatch) |

**Result object schema (`data.results[]`):**
```json
{
  "title": "Q3 2024 Earnings Summary",
  "link": "https://docs.google.com/document/d/...",
  "snippet": "Revenue grew <b>14%</b> year-over-year...",
  "mime_type": "application/vnd.google-apps.document",
  "icon": "📝",
  "source": "Google Drive"
}
```

### `GET /health`

Returns `{"status": "ok"}`. Used by Cloud Run health checks.

---

## Discovery Engine Endpoint

```
POST https://discoveryengine.googleapis.com/v1alpha/projects/254356041555
     /locations/global/collections/default_collection
     /engines/vais-workspace_1779830576232
     /servingConfigs/default_search:search
```

---

## Troubleshooting

**`403 PERMISSION_DENIED` from Discovery Engine**
- Service accounts are blocked for Workspace datastores — only user OAuth tokens work.
- Confirm the user's Workspace account belongs to the org connected to the datastore.
- Confirm the `cloud-platform` scope was granted during sign-in.

**`Token mismatch — please sign in again`**
- The ID token and access token carry different email addresses.
- This is an intentional security check against token substitution attacks.
- Sign out and sign back in to get a fresh matching pair.

**`Token verification failed`**
- The ID token is expired (1-hour TTL) or the `GOOGLE_OAUTH_CLIENT_ID` in the server env does not match the client ID in the frontend.
- Both must reference the same OAuth Client ID.

**Sign-in button does not appear**
- The app origin is not listed in the OAuth client's "Authorized JavaScript origins".
- Add `http://localhost:8080` (local) or the Cloud Run URL (production) and wait ~5 minutes for the change to propagate.

**Empty results after a successful search**
- The user has no Drive files indexed in the datastore, or no files match the query.
- Confirm the Drive connector has finished indexing and the user has read access to at least some files in the connected Drive.

**AI summary card never appears**
- The summary call returned `summaryText: ""` — this happens when Discovery Engine's heuristics classify the query as non-summary-seeking (`ignoreNonSummarySeekingQuery: true` is set).
- File results are still displayed; the summary card is hidden when `summaryText` is empty.
