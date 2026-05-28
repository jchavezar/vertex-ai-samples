# Cloud Run variant — working end-to-end

GE Custom-A2A → Cloud Run (FastAPI + ADK) → Google Drive **as the calling
user**. This is the recommended path. The OAuth bearer GE captures from the
user reaches the container unmodified, so the Drive tool calls
`drive.files.list` with the user's own access token.

## Layout

```
cloud-run/
├── README.md                   ← you are here
├── .env.example                ← copy to .env, fill in
├── Dockerfile                  ← used by `gcloud run deploy --source .`
├── requirements.txt
├── create_oauth_client.sh      ← prints the one-time console steps
├── create_authorization.py     ← creates the GE Authorization resource
├── deploy.py                   ← `gcloud run deploy` wrapper (two-pass)
├── register_ge_agent.py        ← POST/PATCH the GE agent registration
└── app/                        ← Python package mounted at /code/app/
    ├── __init__.py
    ├── main.py                 ← FastAPI + A2A JSON-RPC handler
    ├── agent.py                ← ADK LlmAgent
    └── drive_tool.py           ← reads user_token from session state
```

## Deploy in 5 steps

```bash
cp .env.example .env
# Edit .env: set PROJECT_ID, GEMINI_ENTERPRISE_APP_ID
```

1. **OAuth client.** Run `bash create_oauth_client.sh` and follow its
   instructions to create a Web-application OAuth client in the Cloud
   Console. Paste the client id + secret into `.env`.
2. **Authorization resource.** `python create_authorization.py` —
   creates the GE `Authorization` requesting `cloud-platform +
   drive.readonly`. Copy the printed `AGENT_AUTHORIZATION=...` line
   into `.env`.
3. **Deploy.** `python deploy.py` — two-pass `gcloud run deploy`. Writes
   `A2A_URL_CR=https://...run.app` back into `.env`.
4. **Register in GE.** `python register_ge_agent.py` — creates (or
   PATCHes, if `GE_AGENT_ID_CR` is set) the GE agent entry pointing at
   `A2A_URL_CR`. The card uses `preferredTransport: "JSONRPC"`.
5. **Try it.** Open your GE app, pick the new agent ("GE A2A Auth +
   Drive (Cloud Run)"), accept the OAuth consent, then:
   - `whoami` → returns your email + sub from the user OAuth token.
   - `list my Drive files` → returns your real Drive files.

## How the A2A bridge works (code map)

- **Agent card** is served at `GET /v1/card` from `app/main.py`. It
  advertises `preferredTransport: "JSONRPC"` — required by GE's harpoon
  proxy.
- **JSON-RPC entrypoint** is `POST /` (with `POST /v1/message:send`
  aliases). It extracts `Authorization: Bearer <token>`, calls
  `oauth2/v3/userinfo`, pushes `user_token` + identity into ADK session
  state, runs the LlmAgent, and returns an A2A `Message` payload as
  `{"jsonrpc":"2.0","id":<id>,"result":{...}}`.
- **`drive_search_files`** reads `user_token` from `tool_context.state`,
  builds a `google.oauth2.credentials.Credentials`, and calls Drive v3
  with `orderBy=modifiedTime desc`.

## Troubleshooting

| Symptom | Cause | Fix |
| --- | --- | --- |
| GE chat shows `Agent returned an error (404)` with `/v1/message:send` URL, no Cloud Run logs | Card transport is not `JSONRPC` | Confirm `register_ge_agent.py` is using `preferredTransport: "JSONRPC"` and re-run it. Harpoon fabricates the 404 client-side without ever sending a request. |
| `oauth2/v3/userinfo` returns 401 | OAuth client missing `cloud-platform` / `drive.readonly` scope on the consent screen | Add the scopes in the Branding / OAuth consent screen, re-consent in GE. |
| GE consent screen not appearing | Existing GE agent has a stale `authorizationConfig` | PATCH `authorizationConfig.agentAuthorization` via `register_ge_agent.py` with `GE_AGENT_ID_CR` set. |
| Cloud Run cold start times out the chat | Container start is slow | Increase `--min-instances=1` in `deploy.py`'s gcloud invocation. |
| Drive returns 403 / 404 | User hasn't actually granted `drive.readonly` (consent screen scope missing) | Re-publish the consent screen with the scope and re-consent. |

## What's different vs. `agent-runtime/`

- Cloud Run preserves headers; AE does not. That is the entire reason
  this variant works and the other does not.
- Cloud Run lets you serve any HTTP shape; AE's `A2aAgent` template
  pins the transport string to `http_json`, which GE refuses to invoke.
- Cloud Run cold-start budget is yours to tune; AE manages its own.
