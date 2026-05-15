# firestore-rag-mcp

A custom MCP server for Gemini Enterprise that grounds answers on a Firestore-backed
PDF knowledge base. Reuses the docparse extraction + indexing pipeline.

```
┌──────────────┐   ┌──────────────────┐   ┌─────────────────────────┐
│ GCS PDFs     │──▶│ docparse extract │──▶│ GCS markdown (.txt)     │
└──────────────┘   └──────────────────┘   └────────────┬────────────┘
                                                       │
                                          ┌────────────▼────────────┐
                                          │ pipeline/  (Cloud Run   │
                                          │   job): chunk-by-page,  │
                                          │   embed text-emb-005,   │
                                          │   write Firestore       │
                                          │   {text, embedding,     │
                                          │    pdf_uri, page}       │
                                          └────────────┬────────────┘
                                                       │
┌──────────────────────────┐   bearer  ┌───────────────▼────────────┐
│ Gemini Enterprise        │──token ──▶│ mcp_server/  (Cloud Run)   │
│ Connected Data Store     │ ◀──tools──│ FastMCP StreamableHTTP     │
│ (custom MCP)             │           │ Google OAuth bearer auth   │
└──────────────────────────┘           │ tools: search_docs,        │
                                       │        list_documents      │
                                       └───────────────┬────────────┘
                                                       │ find_nearest
                                                       ▼
                                              Firestore vector index
```

## What's reused vs. new

| Layer        | Source                                                        | New here? |
|--------------|---------------------------------------------------------------|-----------|
| PDF extract  | `../docparse/` Cloud Run extractor                            | reused    |
| Indexer      | `../docparse-firestore-grounding/indexer/`                    | reused (slimmed) |
| Retrieval    | `firestore_search.py` (lifted from the ADK FunctionTool)      | reused    |
| **MCP server** | `mcp_server/server.py` — FastMCP StreamableHTTP + auth      | **new**   |
| **OAuth**    | `mcp_server/auth.py` — Google bearer-token validator          | **new**   |

## Layout

```
firestore-rag-mcp/
├── README.md
├── pipeline/                    # GCS markdown → Firestore vectors
│   ├── index_to_firestore.py
│   ├── requirements.txt
│   ├── Dockerfile
│   └── deploy_indexer_job.sh
└── mcp_server/                  # MCP server exposed to Gemini Enterprise
    ├── server.py                # FastMCP app + Starlette wiring
    ├── auth.py                  # Google OAuth bearer middleware
    ├── firestore_search.py      # vector search + corpus listing
    ├── requirements.txt
    ├── Dockerfile
    └── deploy_mcp_run.sh
```

## End-to-end setup

### 1. Index the corpus into Firestore

The two demo PDFs already live at
`gs://sharepoint-wif-docparse-in/` and have been extracted to markdown at
`gs://sharepoint-wif-docparse-out/`. Indexing them into a fresh collection:

```
cd pipeline
PROJECT=sharepoint-wif COLLECTION=mcp_docs ./deploy_indexer_job.sh
gcloud run jobs execute firestore-rag-mcp-indexer --region=us-central1 --project=sharepoint-wif
```

Then create the **single-field vector index** Firestore needs for
`find_nearest`:

```
gcloud firestore indexes composite create --project=sharepoint-wif --collection-group=mcp_docs --query-scope=COLLECTION --field-config=field-path=embedding,vector-config='{"dimension":768,"flat":{}}'
```

### 2. Create a Google OAuth 2.0 client

Console → APIs & Services → Credentials → **Create OAuth client ID** → Web app.

* **Authorized redirect URI** (exactly):
  `https://vertexaisearch.cloud.google.com/oauth-redirect`

Copy the **Client ID** and **Client Secret**.

> The MCP server validates incoming Google access tokens via
> `oauth2.googleapis.com/tokeninfo`. If you set `OAUTH_CLIENT_ID` on the Cloud
> Run service it will additionally enforce `audience == client_id`. Set
> `ALLOWED_DOMAIN=altostrat.com` (or similar) to restrict access to your
> Workspace tenant.

### 3. Deploy the MCP server

```
cd mcp_server
PROJECT=sharepoint-wif \
  COLLECTION=mcp_docs \
  OAUTH_CLIENT_ID="<the client id from step 2>" \
  ALLOWED_DOMAIN=altostrat.com \
  ./deploy_mcp_run.sh
```

Output prints the Cloud Run URL. Confirm with:

```
curl -s "$URL/healthz"           # → ok
curl -i "$URL/mcp/"              # → 401 missing_bearer_token  (good!)
```

### 4. Wire it into Gemini Enterprise

In the **MCP Server Configuration** form (your screenshot), fill:

| Field                     | Value                                                                 |
|---------------------------|-----------------------------------------------------------------------|
| MCP Server URL            | `https://<cloud-run-url>/mcp/`                                        |
| Authorization URL         | `https://accounts.google.com/o/oauth2/v2/auth`                        |
| Authorization URL Params  | *(leave empty)*                                                       |
| Token URL                 | `https://oauth2.googleapis.com/token`                                 |
| Client ID                 | *(from step 2)*                                                       |
| Client Secret             | *(from step 2)*                                                       |
| Scopes                    | `openid email profile`                                                |

Click **Login**, complete the Google consent. GE will store the refresh token
and call `tools/list` against your server. You should see `search_docs` and
`list_documents` show up under "Custom actions".

### 5. Try it

In Gemini Enterprise chat with this datastore selected, ask:
* *"What does Accenture say about the metaverse evolution?"*
* *"What competitive intelligence is in the SE pricing trends report?"*

Each answer comes back grounded with citations whose URI points at
`gs://.../<doc>.pdf` and the matching page number.

## Local dev

```
cd mcp_server
pip install -r requirements.txt
FIRESTORE_PROJECT=sharepoint-wif FIRESTORE_COLLECTION=mcp_docs python server.py
# In another terminal, bypass auth by leaving OAUTH_CLIENT_ID unset and
# passing any non-empty Bearer; tokeninfo will reject it. For local tool
# testing, comment out `app.add_middleware(GoogleBearerAuth)` in server.py
# or set ALLOWED_DOMAIN to a sentinel and call with a real `gcloud auth
# print-access-token` token.
```

## Notes

* **Transport:** GE only supports the new MCP **StreamableHTTP** transport
  (no SSE). FastMCP's `streamable_http_app()` is the right entry point.
* **Embedding model:** `text-embedding-005` (768-d) — must match what the
  Firestore vector index was created with.
* **Cross-project IAM:** if you deploy MCP in `vtxdemos` and Firestore lives
  in `sharepoint-wif`, grant the Cloud Run service account
  `roles/datastore.user` on `sharepoint-wif`.
