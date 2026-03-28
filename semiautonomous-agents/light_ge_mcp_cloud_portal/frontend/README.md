# Frontend

[← Back to Main README](../README.md)

React frontend with MSAL authentication and direct Agent Engine integration via Workforce Identity Federation.

## Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                         FRONTEND                                 │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────────┐  │
│  │   MSAL      │─▶│  STS        │─▶│   Agent Engine          │  │
│  │   (Entra)   │  │  Exchange   │  │   API Client            │  │
│  └─────────────┘  └─────────────┘  └─────────────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
```

## Files

| File | Purpose |
|------|---------|
| [`src/authConfig.ts`](src/authConfig.ts) | MSAL + WIF + Agent Engine configuration |
| [`src/agentService.ts`](src/agentService.ts) | STS exchange, session management, streaming queries |
| [`src/App.tsx`](src/App.tsx) | Main UI component with chat interface |
| [`src/App.css`](src/App.css) | Styling |

## Configuration

Edit `src/authConfig.ts`:

```typescript
// MSAL (Microsoft Authentication)
export const msalConfig = {
  auth: {
    clientId: "YOUR_ENTRA_CLIENT_ID",
    authority: "https://login.microsoftonline.com/YOUR_TENANT_ID",
  }
};

// Workforce Identity Federation
export const gcpConfig = {
  workforcePoolId: "YOUR_POOL_ID",
  providerId: "YOUR_PROVIDER_ID",
  location: "global",
};

// Agent Engine
export const agentConfig = {
  projectId: "YOUR_PROJECT_ID",
  location: "us-central1",
  agentEngineId: "YOUR_AGENT_ENGINE_ID",
};
```

## Development

```bash
# Install dependencies
npm install --registry=https://registry.npmjs.org

# Start dev server
npm run dev
```

Open http://localhost:3000

## Key Functions

### Token Exchange ([`agentService.ts`](src/agentService.ts))

```typescript
// Exchange Entra ID token for GCP token
export async function exchangeTokenForGcp(entraIdToken: string): Promise<string> {
  const response = await fetch("https://sts.googleapis.com/v1/token", {
    method: "POST",
    body: new URLSearchParams({
      grant_type: "urn:ietf:params:oauth:grant-type:token-exchange",
      audience: `//iam.googleapis.com/.../workforcePools/${pool}/providers/${provider}`,
      subject_token: entraIdToken,
      // ...
    }),
  });
  return (await response.json()).access_token;
}
```

### Session Creation ([`agentService.ts`](src/agentService.ts))

```typescript
// Create session with USER_TOKEN in state
export async function createSession(gcpToken, userId, userToken) {
  const response = await fetch(`${agentEngineUrl}:query`, {
    headers: { Authorization: `Bearer ${gcpToken}` },
    body: JSON.stringify({
      class_method: "create_session",
      input: {
        user_id: userId,
        state: { USER_TOKEN: userToken },  // Passed to MCP server
      },
    }),
  });
}
```

### Streaming Queries ([`agentService.ts`](src/agentService.ts))

```typescript
// Stream query results chunk by chunk
export async function* queryStream(gcpToken, sessionId, userId, message) {
  const response = await fetch(`${agentEngineUrl}:streamQuery`, {
    headers: { Authorization: `Bearer ${gcpToken}` },
    body: JSON.stringify({ input: { session_id: sessionId, message } }),
  });

  const reader = response.body.getReader();
  // Yield text chunks as they arrive
}
```

## Build for Production

```bash
npm run build
# Output in dist/
```

## Deploy to Cloud Run

```bash
# Build and deploy
gcloud run deploy servicenow-portal \
  --source . \
  --region us-central1 \
  --allow-unauthenticated
```

Remember to add the production URL to Entra ID redirect URIs.

## Related Documentation

- [Entra ID Setup](../docs/entra-id-setup.md)
- [GCP Setup](../docs/gcp-setup.md) - WIF configuration
- [Security Flow](../docs/security-flow.md)
