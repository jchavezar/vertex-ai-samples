# Scripts

Registration and advanced testing scripts for Gemini Enterprise.

---

## Registration Scripts

### register_auth.sh

Register OAuth authorization to Agentspace.

```bash
./register_auth.sh
```

Creates authorization `sharepointauth2` with:
- Client ID/Secret from Entra ID
- Token endpoint: Microsoft v2.0
- Scope: `api://{client-id}/user_impersonation`

### register_agent.sh

Register InsightComparator agent to Agentspace.

```bash
./register_agent.sh
```

Links:
- Agent Engine deployment (REASONING_ENGINE_RES)
- OAuth authorization (sharepointauth2)
- Sharing scope: ALL_USERS

---

## Testing Scripts

### test_a2a_discovery.py

Test agent via Discovery Engine A2A protocol.

```bash
uv run python test_a2a_discovery.py              # Test via A2A
uv run python test_a2a_discovery.py --list       # List agents
uv run python test_a2a_discovery.py --sdk        # Test via SDK
```

**Note:** A2A can invoke the agent but cannot pass OAuth tokens to `tool_context.state`. This is handled server-side by GE when users authorize.

---

## Environment Variables

All scripts require these in `.env`:

| Variable | Purpose |
|----------|---------|
| `PROJECT_NUMBER` | GCP project number |
| `ENGINE_ID` | Discovery Engine ID |
| `OAUTH_CLIENT_ID` | Entra app client ID |
| `OAUTH_CLIENT_SECRET` | Entra app secret |
| `TENANT_ID` | Entra tenant ID |
| `REASONING_ENGINE_RES` | Agent Engine resource |
| `AUTH_ID` | Authorization name |
