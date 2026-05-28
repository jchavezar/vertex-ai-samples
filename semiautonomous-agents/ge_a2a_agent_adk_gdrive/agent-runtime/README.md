# Agent Runtime variant — reference path

ADK agent deployed to Vertex AI Agent Runtime as a native A2A endpoint,
registered in Gemini Enterprise through the same Custom-A2A path. This
variant is provided for completeness; **read the "Known limitations"
section before using it for a real demo**.

## Layout

```
agent-runtime/
├── README.md                   ← you are here
├── .env.example                ← copy to .env, fill in
├── create_oauth_client.sh      ← prints the one-time console steps
├── create_authorization.py     ← creates the GE Authorization resource
├── deploy.py                   ← vertexai.agent_engines.create(A2aAgent(...))
├── register_ge_agent.py        ← POST/PATCH the GE agent registration
└── agent/
    ├── __init__.py
    ├── agent.py                ← ADK LlmAgent + google_search tool
    ├── agent_executor.py       ← ADK ↔ a2a-sdk bridge with identity probe
    └── requirements.txt        ← bundled into the AE deployment
```

## Deploy in 5 steps

```bash
cp .env.example .env
# Edit .env: PROJECT_ID, LOCATION, STORAGE_BUCKET, GEMINI_ENTERPRISE_APP_ID
```

1. **OAuth client.** `bash create_oauth_client.sh` and follow the
   instructions. Paste credentials into `.env`.
2. **Authorization resource.** `python create_authorization.py` →
   copy `AGENT_AUTHORIZATION=...` into `.env`.
3. **Deploy.** `python deploy.py` — takes ~5 min the first time. Writes
   `REASONING_ENGINE_ID` + `A2A_URL` back into `.env`, and saves the
   fetched agent card to `agent_card.json`.
4. **Register in GE.** `python register_ge_agent.py` — uploads
   `agent_card.json` as the `jsonAgentCard` and binds the
   `AGENT_AUTHORIZATION`.
5. **Test directly with curl** (the GE chat path will not work — see
   below):
   ```bash
   TOKEN=$(gcloud auth print-access-token)
   curl -sS -X POST "$A2A_URL/v1/message:send" \
        -H "Authorization: Bearer $TOKEN" \
        -H "Content-Type: application/json" \
        -d '{"message":{"messageId":"m1","role":"user","parts":[{"kind":"text","text":"whoami"}]}}'
   ```

## Known limitations

1. **Transport mismatch.** AE's `A2aAgent` validator only accepts
   `preferred_transport = http_json`. GE's Custom-A2A proxy
   ("harpoon") only invokes endpoints whose card advertises
   `preferredTransport: "JSONRPC"`. So GE silently rejects the
   registered card — chat returns a synthetic 404 with zero outbound
   request. (See the `feedback` memory `ge-custom-a2a-jsonrpc-only`.)
2. **User OAuth is stripped.** Even bypassing the transport issue, the
   Vertex AI proxy validates the inbound bearer (the user's
   `ya29.user_token` GE forwarded), strips it, and re-signs the inner
   request as the AE service account. The executor sees an AE
   SA-signed JWT, not the user's token, so it cannot act as the user
   against Workspace APIs.

For real per-user delegation today, use [`../cloud-run/`](../cloud-run/).

## How to verify the limitations yourself

After deploying and registering, send any message in GE chat:

- Tail `gcloud logging read 'resource.type="aiplatform.googleapis.com/ReasoningEngine"'`.
  You will see **no request** corresponding to the chat message
  — confirms the transport-side rejection.
- Hit the A2A endpoint directly with `curl` as above. The agent
  responds. The `caller_identity` block embedded in the reply will
  show `iss=https://accounts.google.com` and the AE SA principal
  (not the user) when the request goes through AE.

## What's different vs. `../cloud-run/`

- Hosting: Vertex AI Agent Runtime (`vertexai.preview.reasoning_engines`)
  instead of Cloud Run.
- Card transport: `HTTP+JSON` (forced by `A2aAgent`) instead of
  `JSONRPC`. This is the blocker for GE chat.
- The container is managed; ADC + dependencies + a2a server framework
  are wired by the SDK. You only ship the `agent/` package and a
  `requirements.txt`.
- The bridge `agent_executor.py` includes a verbose `caller_identity`
  probe (headers, JWT claims, A2A request fields) so you can see
  exactly what reaches the executor.
