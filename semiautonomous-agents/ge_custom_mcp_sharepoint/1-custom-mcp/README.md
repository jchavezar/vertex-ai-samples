## Option 1 — Custom SharePoint MCP on Cloud Run

You own the code. Cloud Run hosts a FastMCP server exposing 7 canonical read tools mapped to Microsoft Graph. Gemini Enterprise calls it via BYO_MCP, forwarding the per-user Entra Bearer token in the `Authorization` header. The server uses the user's delegated token for every Graph call, so SharePoint ACLs are enforced at source.

```mermaid
flowchart LR
  user(["User in GE chat"]):::user
  ge["Gemini Enterprise — BYO_MCP datastore"]:::ge
  cr["Cloud Run — FastMCP /mcp"]:::cr
  graph[("Microsoft Graph /sites /drives /search")]:::sp

  user --> ge -->|Authorization: Bearer <user_token>| cr --> graph

  classDef user fill:#FBBC04,stroke:#F29900,stroke-width:3px,color:#000
  classDef ge fill:#4285F4,stroke:#1967D2,stroke-width:2px,color:#fff
  classDef cr fill:#FF6F00,stroke:#E65100,stroke-width:2px,color:#fff
  classDef sp fill:#1F6FEB,stroke:#0B3D91,stroke-width:2px,color:#fff
```

---

### Tool surface (7 canonical read tools)

| Tool | Purpose | Graph endpoint |
|---|---|---|
| `search(query)` | Free-text retrieval primitive. Required by GE BYO-MCP for silent dispatch. | `POST /search/query` (entityTypes=driveItem) |
| `fetch(id)` | Single-doc retrieval by id. Returns markdown + url. Required by GE BYO-MCP. | `GET /drives/{id}/items/{itemId}` + downloadUrl |
| `list_sites(search?)` | List/search SharePoint sites the user can see. | `GET /sites?search=...` |
| `list_libraries(site_id)` | List document libraries (drives) in a site. | `GET /sites/{id}/drives` |
| `list_files(library_id, folder?)` | List children of a folder. | `GET /drives/{id}/root[:/path:]/children` |
| `read_file(file_id)` | Download a file and convert PDF/docx → markdown (vision for images). | `GET /drives/{id}/items/{itemId}/content` + MarkItDown |
| `search_content(query)` | Cross-tenant Graph Search across document content (not just names). | `POST /search/query` |

Write tools (`create_folder`, `upload_file`, `share_file`, etc.) are intentionally kept in `tools/sharepoint.py` but **not registered** with the MCP server in this scaffold and are out of scope for the eval. Flip a feature flag (`MCP_ENABLE_WRITES=1`) to expose them.

---

### What changed from `ms365-mcp-server`

`ms365-mcp-server/` is the upstream skeleton this option reuses. The changes for GE BYO-MCP:

| Concern | `ms365-mcp-server` (upstream) | This option |
|---|---|---|
| Auth flow | MSAL **device code** (single-user, in-memory) | Entra **authorization code** (per-user, GE forwards Bearer) |
| Token source | `MSALAuthManager.get_access_token()` (cached in process) | Per-request `Authorization: Bearer` header captured by middleware |
| `/mcp` endpoint | None (only stdio) | Added — StreamableHTTP for GE BYO_MCP, with full `Tool.model_dump(by_alias=True, exclude_none=True)` (the 5-part silent-search recipe) |
| `protocolVersion` | n/a | `"2025-06-18"` (required for `ToolAnnotations` to take effect in GE) |
| Tool annotations | none | `ToolAnnotations(readOnlyHint=True, idempotentHint=True, openWorldHint=True)` on every read tool |
| Canonical `search` / `fetch` | none | Added with explicit `outputSchema` (OpenAI deep-research convention, silent retrieval flag for GE) |
| Doc → markdown | none (returns raw bytes or text) | `doc_reader.py` adds PyMuPDF + MarkItDown + Gemini-vision image callback (borrowed from `accenture_stream_assist/.../mcp_sharepoint.py`) |
| Write tools | exposed | present in source, **not registered** by default (gated by `MCP_ENABLE_WRITES`) |

The 5-part recipe is documented in `~/.claude/projects/.../memory/ge_custom_mcp_confirmation_fix.md` (and applied in [`atlassian-jira-integration/option-a-custom-mcp-portal/jira_server/server.py`](../../atlassian-jira-integration/option-a-custom-mcp-portal/jira_server/server.py)). This server follows the same pattern.

---

### Deploy

```bash
# 1. Configure Entra app for OAuth authorization-code flow (TODO: see auth.py docstring)
export AZURE_CLIENT_ID="<your-entra-app-id>"
export AZURE_TENANT_ID="<your-tenant-id>"
export AZURE_REDIRECT_URI="https://<ge-redirect-host>/oauth/callback"

# 2. Configure GCP target
export GOOGLE_CLOUD_PROJECT="vtxdemos"
export GOOGLE_CLOUD_LOCATION="us-central1"

# 3. Build + deploy Cloud Run
./deploy.sh

# 4. Register in Agent Registry (used by GE BYO_MCP)
export MCP_SERVER_URL="https://sharepoint-mcp-XXXXX-uc.a.run.app/mcp"
./register_in_ge.sh
```

After registration the connector will appear in Gemini Enterprise as a BYO_MCP datastore. Attach it to your GE app; the silent-search recipe (annotations + outputSchema + canonical search/fetch) means tool calls dispatch without per-call confirmation popups.

---

### Local dev

```bash
pip install -r requirements.txt
export AZURE_CLIENT_ID=... AZURE_TENANT_ID=...
python server.py  # listens on :8080, /mcp endpoint
```

You can probe `/mcp` with the test client pattern from `../atlassian-jira-integration/option-a-custom-mcp-portal/utils/test_client.py`.

---

### Open TODOs in this scaffold

- `auth.py` — implement the actual Entra OAuth authorization-code helper (only the per-request Bearer middleware is wired today).
- `tools/sharepoint.py` — `list_libraries`, `list_files`, `read_file`, `search_content` are present as direct ports; `search` and `fetch` live in `tools/search.py` and dispatch via Graph `/search/query` and `/drives/{id}/items/{itemId}`.
- `doc_reader.py` — Gemini-vision callback is wired but the `MarkItDown` import + `fitz` are placeholders until you `pip install markitdown pymupdf google-genai`.
- `eval/runners/run_custom_mcp.py` — TODO, end-to-end harness against the deployed Cloud Run URL.
