# Design — firestore-rag-mcp

## Why this exists

Gemini Enterprise now supports **custom MCP servers** as Connected Data
Stores. To prove the pattern end-to-end we need a server that:

1. Returns real, grounded retrieval results (not hardcoded JSON).
2. Speaks the **StreamableHTTP** transport GE requires (SSE is rejected).
3. Authenticates via the OAuth flow GE drives (redirect URI
   `https://vertexaisearch.cloud.google.com/oauth-redirect`).
4. Reuses an existing pipeline so we're demoing a real architecture, not a
   throwaway.

The closest existing project is `docparse-firestore-grounding/`, which
already extracts PDFs, embeds page-level chunks, and stores them in
Firestore. This project lifts that pipeline and exposes it as an MCP server
behind Google OAuth.

## OAuth choice — Google as the IdP

Building a self-hosted OAuth 2.0 server (auth code grant, JWT issuance,
refresh-token rotation) just to demo MCP is wasted code. Instead:

- Register a Google OAuth 2.0 Web client in the GCP project hosting MCP.
- Add `https://vertexaisearch.cloud.google.com/oauth-redirect` as an
  authorized redirect URI.
- GE drives the auth-code flow against `accounts.google.com`, exchanges at
  `oauth2.googleapis.com/token`, then attaches the resulting Google access
  token as `Authorization: Bearer <token>` on each MCP call.
- Our middleware validates that token via `oauth2.googleapis.com/tokeninfo`
  and (optionally) checks `audience == client_id` and the user's email
  domain.

This shifts identity, consent UX, refresh handling, and revocation onto
Google. The MCP code stays small.

## Why FastMCP StreamableHTTP

The official `mcp` Python SDK ships `FastMCP` with a
`streamable_http_app()` helper that returns a Starlette app. We mount it
under `/mcp/` and add:

- a `/healthz` route (Cloud Run probes, smoke tests)
- `GoogleBearerAuth` Starlette middleware (rejects unauthenticated calls
  before they reach the MCP transport).

`stateless_http=True` keeps each request self-contained — no in-memory
session affinity, which matters for Cloud Run autoscaling.

## Why text-embedding-005

The existing Firestore collection already uses `text-embedding-005`
(768-d), so the index doesn't need to be rebuilt. Keeping the same model
preserves comparability with the docparse-firestore-grounding agent
results (the eval baseline).

## What we deliberately did not build

- **Per-user ACLs.** GE forwards the user's identity in the access token
  (`info.email` after tokeninfo), but enforcing per-document ACLs needs an
  ACL store this demo doesn't have. Hooking it in later is a single check
  inside `vector_search`.
- **Re-ranker.** `docparse-firestore-grounding` mentions an optional
  Discovery Engine re-ranker. Skipped here to keep the dependency surface
  small; can be added with a single Vertex AI Ranking API call after
  `find_nearest`.
- **Custom OAuth server.** See "OAuth choice" above.
- **Frontend.** GE itself is the UI. No portal needed.

## Failure modes worth knowing

- `find_nearest` raises `FAILED_PRECONDITION` if the single-field vector
  index doesn't exist. README's `gcloud firestore indexes composite create`
  command fixes this.
- Cloud Run cold-starts on `genai.Client` and `firestore.Client` are
  noticeable (~600ms). `lru_cache` keeps both hot for warm instances.
- If you redeploy with a different embedding model, the index becomes
  invalid silently — search returns garbage. The dim must match.
- GE's "Reload custom actions" button calls `tools/list`. If auth is
  misconfigured the GE UI shows a generic error; check Cloud Run logs for
  the 401/403 response.
