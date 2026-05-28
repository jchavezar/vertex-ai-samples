# ge_a2a_agent_adk_gdrive

End-to-end user OAuth delegation through Gemini Enterprise Custom-A2A: a
user signs in once via the GE consent screen, and a downstream ADK agent
calls Google APIs **as that user** — no service-account impersonation, no
DWD, no IAP.

Two deployment variants are provided side-by-side:

| Variant | Folder | Status | What runs the agent | User OAuth reaches agent? |
| --- | --- | --- | --- | --- |
| **Cloud Run** | [`cloud-run/`](cloud-run/) | Working, recommended | FastAPI + ADK on Cloud Run | Yes — `Authorization` header preserved verbatim |
| **Agent Runtime** | [`agent-runtime/`](agent-runtime/) | Reference only — see "Known limitations" below | ADK on Vertex AI Agent Runtime (`vertexai.preview.reasoning_engines.A2aAgent`) | No — AE proxy strips the user bearer and substitutes the AE SA token |

If you only want the customer to copy one thing, point them at
[`cloud-run/`](cloud-run/).

## Shared architecture

```
[user] → GE chat → GE OAuth consent (Authorization resource)
                                 │
                  Authorization: Bearer <ya29.user_token>
                                 ▼
       harpoon (GE Custom-A2A proxy, JSON-RPC only)
                                 │
                                 ▼
                  your A2A endpoint (Cloud Run or AE)
                                 │
                                 ▼
                    ADK LlmAgent + tools (Drive, Search, …)
```

The OAuth client requests `cloud-platform + drive.readonly` scopes in a
single token. `cloud-platform` satisfies the API-key-style pre-check GE
performs before forwarding; `drive.readonly` is what the Drive tool
actually consumes downstream.

## Why two variants?

The pattern is the same on both sides of the GE proxy. The difference is
what's downstream of the proxy:

- **Cloud Run** — a normal container. Headers come through unmodified, so
  the agent code can see the user's `ya29.*` access token and call any
  Google API on their behalf. This is what the working demo uses.
- **Agent Runtime** — a managed Vertex AI proxy sits in front of the
  container. It validates the inbound bearer (must be a Google OAuth
  token with `cloud-platform` scope), strips it, and re-signs the inner
  request as the AE service account. The agent therefore runs as the AE
  SA — fine for SA-scoped tools (Google Search grounding, Vertex AI),
  not fine for per-user Workspace access.

## Known limitations (Agent Runtime variant)

1. **Transport mismatch.** GE's harpoon proxy only invokes
   `preferredTransport: "JSONRPC"`. AE's `A2aAgent` validator rejects
   anything that isn't `http_json`. As a result the agent deploys
   successfully and the A2A endpoint is reachable directly, but GE chat
   returns a synthetic 404 without ever sending a request. (See the
   `feedback` memory `ge-custom-a2a-jsonrpc-only` for the diagnostic
   story.)
2. **User OAuth is stripped.** Even if the transport issue is resolved,
   the AE proxy substitutes the inbound `Authorization` header. The
   executor sees an AE SA-signed JWT, not the user's `ya29.*` token,
   so it cannot act as the user against Workspace APIs.

If/when both restrictions are lifted, the AE variant becomes a drop-in
replacement for the Cloud Run variant.

## Pick a variant and follow its README

- [`cloud-run/README.md`](cloud-run/README.md) — recommended path
- [`agent-runtime/README.md`](agent-runtime/README.md) — reference path

## Prerequisites (both variants)

- A Gemini Enterprise app (`GEMINI_ENTERPRISE_APP_ID`)
- Project IAM roles: Discovery Engine Admin, Cloud Run Admin (CR variant)
  or Vertex AI Admin (AE variant), Service Account User
- gcloud CLI authenticated to the target project, ADC available, billing
  enabled
- An OAuth2 web client in the same project (one-time manual step — see
  `create_oauth_client.sh` inside each variant)
