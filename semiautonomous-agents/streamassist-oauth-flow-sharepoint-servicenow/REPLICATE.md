# Replicate end-to-end — copy-paste commands

This is the full set of commands to take a working pair of single-connector
demos (SharePoint + ServiceNow) and consolidate them into the combined
three-toggle portal.

> Prereqs: you've already replicated `streamassist-oauth-flow-sharepoint`
> and `streamassist-oauth-flow-servicenow` end-to-end (each one runs
> standalone). This guide assumes both connectors exist as Discovery Engine
> resources and that each user has consented to both at least once. If not,
> run those READMEs / REPLICATE.md guides first.

> Need: `gcloud` authenticated as a project admin (the `/api/grounding/web`
> backend endpoints use this token), Python 3.12+, Node 20+, `uv`, `npm`.

---

## 0 · Variables you need

```bash
# ── GCP / Discovery Engine ───────────────────────────────────────────────────
export PROJECT_NUMBER="<NUMERIC_PROJECT_NUMBER>"
export ENGINE_ID="<engine-that-already-has-sharepoint>"   # we'll add SN to this

# ── WIF (already exists) ─────────────────────────────────────────────────────
export WIF_POOL_ID="<sp-wif-pool-v2>"
export WIF_PROVIDER_ID="<entra-oidc-provider>"

# ── Microsoft Entra (Portal App + Connector App, already exist) ──────────────
export TENANT_ID="<ENTRA_TENANT_GUID>"
export PORTAL_APP_CLIENT_ID="<RAW_PORTAL_APP_GUID>"        # for VITE_CLIENT_ID
export SP_CONNECTOR_CLIENT_ID="<SP_CONNECTOR_APP_GUID>"

# ── SharePoint (already created) ─────────────────────────────────────────────
export SP_CONNECTOR_ID="<sharepoint-connector-id>"          # e.g. sharepoint-data-def-connector
export SHAREPOINT_DOMAIN="<contoso.sharepoint.com>"

# ── ServiceNow (already created) ─────────────────────────────────────────────
export SN_CONNECTOR_ID="<servicenow-connector-id>"          # e.g. servicenow-connector-1777047657
export SN_INSTANCE="<https://your-instance.service-now.com>"
export SN_OAUTH_CLIENT_ID="<sn-oauth-client-id>"
export SN_OAUTH_CLIENT_SECRET="<sn-oauth-client-secret>"

# ── Sanity check ────────────────────────────────────────────────────────────
TOKEN=$(gcloud auth print-access-token)
echo "Identity: $(gcloud config get-value account)"
echo "Project:  $PROJECT_NUMBER"
```

---

## 1 · Consolidate both connectors into one engine

The combined backend issues a single `streamAssist` call with a *union* of
SharePoint + ServiceNow `dataStoreSpecs`. That requires both sets of data
stores to be attached to the same engine.

**Read** the engine's current data stores, **append** the 5 ServiceNow ones,
**PATCH**:

```bash
NEW_LIST=$(curl -sS \
  -H "Authorization: Bearer $TOKEN" -H "X-Goog-User-Project: $PROJECT_NUMBER" \
  "https://discoveryengine.googleapis.com/v1alpha/projects/$PROJECT_NUMBER/locations/global/collections/default_collection/engines/$ENGINE_ID" \
  | jq -r '[.dataStoreIds[]?] + [
      "'$SN_CONNECTOR_ID'_incident",
      "'$SN_CONNECTOR_ID'_knowledge",
      "'$SN_CONNECTOR_ID'_catalog",
      "'$SN_CONNECTOR_ID'_users",
      "'$SN_CONNECTOR_ID'_attachment"
    ] | unique | tojson')

curl -sS -X PATCH \
  -H "Authorization: Bearer $TOKEN" -H "X-Goog-User-Project: $PROJECT_NUMBER" -H "Content-Type: application/json" \
  "https://discoveryengine.googleapis.com/v1alpha/projects/$PROJECT_NUMBER/locations/global/collections/default_collection/engines/$ENGINE_ID?updateMask=dataStoreIds" \
  -d "{\"dataStoreIds\": $NEW_LIST}" \
  | jq '.dataStoreIds | length, .dataStoreIds'
```

You should see all 10+ data stores returned (5 SP + 5 SN + whatever else was
already attached). Discovery Engine apps support up to 50 data stores per
engine; if your engine is already at the limit, [create a new one](#new-engine-route)
instead.

> **`workforceIdentityPoolProvider` already set?** It's set per-engine, not
> per-connector. If you previously did the SharePoint or ServiceNow REPLICATE
> guide on this same engine, you've already done it. If not, follow §5 of the
> ServiceNow REPLICATE guide.

### New-engine route

If you'd rather create a fresh engine with just SP + SN attached:

```bash
NEW_ENGINE_ID="combined-portal-$(date +%s)"

curl -sS -X POST \
  -H "Authorization: Bearer $TOKEN" -H "X-Goog-User-Project: $PROJECT_NUMBER" -H "Content-Type: application/json" \
  "https://discoveryengine.googleapis.com/v1alpha/projects/$PROJECT_NUMBER/locations/global/collections/default_collection/engines?engineId=$NEW_ENGINE_ID" \
  -d "{
    \"displayName\": \"$NEW_ENGINE_ID\",
    \"solutionType\": \"SOLUTION_TYPE_SEARCH\",
    \"industryVertical\": \"GENERIC\",
    \"appType\": \"APP_TYPE_INTRANET\",
    \"searchEngineConfig\": {
      \"searchTier\": \"SEARCH_TIER_ENTERPRISE\",
      \"searchAddOns\": [\"SEARCH_ADD_ON_LLM\"]
    },
    \"dataStoreIds\": [
      \"${SP_CONNECTOR_ID}_file\",
      \"${SP_CONNECTOR_ID}_page\",
      \"${SP_CONNECTOR_ID}_comment\",
      \"${SP_CONNECTOR_ID}_event\",
      \"${SP_CONNECTOR_ID}_attachment\",
      \"${SN_CONNECTOR_ID}_incident\",
      \"${SN_CONNECTOR_ID}_knowledge\",
      \"${SN_CONNECTOR_ID}_catalog\",
      \"${SN_CONNECTOR_ID}_users\",
      \"${SN_CONNECTOR_ID}_attachment\"
    ]
  }" | jq .
```

Then set `ENGINE_ID=$NEW_ENGINE_ID` and complete §5 of the ServiceNow
REPLICATE guide to attach the WIF provider to the new engine.

---

## 2 · Lock down the assistant — the hallucination fix

The default assistant has `WEB_GROUNDING_TYPE_GOOGLE_SEARCH` enabled and no
system instruction. Replace both:

```bash
curl -sS -X PATCH \
  -H "Authorization: Bearer $TOKEN" -H "X-Goog-User-Project: $PROJECT_NUMBER" -H "Content-Type: application/json" \
  "https://discoveryengine.googleapis.com/v1alpha/projects/$PROJECT_NUMBER/locations/global/collections/default_collection/engines/$ENGINE_ID/assistants/default_assistant?updateMask=webGroundingType,generationConfig.systemInstruction" \
  -d @- <<'JSON' | jq '.webGroundingType, .generationConfig.systemInstruction.additionalSystemInstruction[:200] + "..."'
{
  "webGroundingType": "WEB_GROUNDING_TYPE_DISABLED",
  "generationConfig": {
    "systemInstruction": {
      "additionalSystemInstruction": "STRICT GROUNDING RULES:\n\n1. Use ONLY information that appears VERBATIM in the retrieved snippets. Do not paraphrase loosely; do not extrapolate; do not embellish.\n\n2. NEVER fabricate identifiers. This includes CVE IDs (e.g. CVE-2024-001), incident numbers (INC0001234), knowledge base IDs (KB0001234), ticket numbers, employee IDs, contract numbers, or ANY structured identifier. If the source describes a vulnerability or item but does not give it an ID, describe it WITHOUT inventing one.\n\n3. NEVER add example IDs, sample data, or placeholder values to make a table or list look more complete.\n\n4. If your answer requires structured data (table, list of incidents, etc.) and the sources do not contain that structured data verbatim, present the information as prose instead, OR say so explicitly: 'The source documents describe these findings but do not assign IDs to them.'\n\n5. If retrieval returns no relevant documents, respond exactly: 'No matching documents were found in the selected connectors. Try rephrasing or enabling another connector.'\n\n6. Do not use prior knowledge, training data, or web sources. Every concrete fact must trace to a snippet."
    }
  }
}
JSON
```

You only need to do this once. The frontend's **Google Search** toggle calls
`POST /api/grounding/web` which re-PATCHes this same field. The backend swaps
between two instructions:

- `GROUNDED_INSTRUCTION` (web OFF) — strict, no prior knowledge, no web
- `WEB_AUGMENTED_INSTRUCTION` (web ON) — prefers connectors but allows web; still bans fake IDs

Both instructions are defined in `backend/main.py` if you want to tune them.

---

## 3 · Backend

```bash
cd backend
uv venv --python 3.12
uv pip install -e .

cp .env.example .env
# Edit .env — fill in PROJECT_NUMBER, ENGINE_ID, WIF_*, TENANT_ID,
# SHAREPOINT_*, SERVICENOW_* / SN_OAUTH_*. The example file has every var documented.

uv run python main.py
# → Uvicorn running on http://0.0.0.0:8004
```

### Run the smoke tests

```bash
# Connector list
curl -sS http://localhost:8004/api/connectors | jq .
# → {"sharepoint": {...}, "servicenow": {...}}

# Web-grounding toggle round-trip
curl -sS http://localhost:8004/api/grounding/web | jq .
curl -sS -X POST http://localhost:8004/api/grounding/web \
  -H "Content-Type: application/json" -d '{"enabled":true}' | jq .
curl -sS -X POST http://localhost:8004/api/grounding/web \
  -H "Content-Type: application/json" -d '{"enabled":false}' | jq .
```

If `/api/grounding/web` returns `403 discoveryengine.assistants.get denied`,
the active `gcloud` account isn't a project admin — `gcloud auth login` as a
user with `roles/discoveryengine.editor` (or higher) on the project.

### Deployment note

The backend's `_admin_token()` shells out to `gcloud auth print-access-token`,
which works for local dev but not in a container. For Cloud Run / Cloud
Functions, replace `_admin_token()` with one of:

- A service account that has `discoveryengine.assistants.update`, accessed via ADC
- Workload Identity in GKE
- Impersonation of an admin SA via `google.auth.impersonated_credentials`

The user-facing endpoints (`/api/sharepoint/*`, `/api/servicenow/*`, `/api/search`)
all use the WIF token chain, which works fine without admin credentials.

---

## 4 · Frontend

```bash
cd frontend
npm install

cp .env.example .env
# VITE_CLIENT_ID = your Portal App client ID (raw GUID, no api:// prefix)
# VITE_TENANT_ID = your Entra tenant ID

npm run dev    # → http://localhost:5177
```

The Vite dev server proxies `/api/*` to `localhost:8004`. To run on a
different backend port, edit both `frontend/vite.config.ts` (proxy target)
and `backend/.env` (`BACKEND_PORT`).

---

## 5 · End-to-end smoke test (manual)

1. Open http://localhost:5177
2. Click **Sign in with Microsoft**, complete MSAL login
3. Toggle **SharePoint** ON
   - If `Needs consent` shows up: click **Connect**, complete the popup
   - Status flips to `ACTIVE` (green chip)
4. Toggle **ServiceNow** ON, repeat consent if needed
5. Toggle **Google Search** OFF (it should already be off after §2)
6. Type *"summarize the latest IT security assessment"* → search
7. Expect:
   - Answer in prose form (no fabricated CVE table)
   - Source cards with the actual SharePoint document(s)
   - Snippet bubbles under each card showing highlighted excerpts
   - No orange "ungrounded" warning

8. Now toggle **ServiceNow** OFF, **Google Search** ON
9. Same query — answer should pull from web sources too, with sources from
   web search appearing in the cards

---

## Failure-mode lookup

| Symptom | Likely cause | Fix |
|---|---|---|
| `RuntimeError: SHAREPOINT_CONNECTOR_ID` at backend startup | Missing required env var | Fill in `backend/.env` from `.env.example` |
| `/api/connectors` returns only one connector | One connector is `_ENABLED=false` | Set both to `true` and restart |
| `/api/grounding/web` returns 403 | Active gcloud account lacks `discoveryengine.assistants.update` | `gcloud auth login` as a project admin |
| Search returns *"No matching documents…"* even with docs | Toggle is ON but consent never completed (`connected: false`) | Click **Connect** on the chip, complete consent |
| Search returns 200 with answer but `sources_count: 0` | Citation parser bug or DE didn't return references | Check `tail -f /tmp/combined-backend.log` for the raw response shape |
| Hallucinated IDs reappear after a restart | Someone reverted the assistant config | Re-run §2 |
| Frontend shows old chip state after toggle | Hot reload didn't catch the state change | Hard reload (Cmd+Shift+R) |
| `address already in use` on backend startup | Old uvicorn still bound to 8004 | `pkill -9 -f "streamassist-oauth-flow-sharepoint-servicenow.*main.py"` |

For the conceptual flow, see **[FLOW.md](FLOW.md)** and **[AUTH_SEQUENCE.md](AUTH_SEQUENCE.md)**.
