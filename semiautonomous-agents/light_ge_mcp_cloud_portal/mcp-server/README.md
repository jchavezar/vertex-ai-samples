# MCP Server

[← Back to Main README](../README.md)

FastMCP server providing ServiceNow tools via SSE transport, deployed to Cloud Run.

## Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                      MCP SERVER (Cloud Run)                      │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────────┐  │
│  │   FastMCP   │─▶│   Header    │─▶│   ServiceNow            │  │
│  │   SSE       │  │   Extract   │  │   API Client            │  │
│  └─────────────┘  └─────────────┘  └─────────────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
```

## Files

| File | Purpose |
|------|---------|
| [`mcp_server.py`](mcp_server.py) | FastMCP server with ServiceNow tools |
| [`Dockerfile`](Dockerfile) | Container configuration |
| [`requirements.txt`](requirements.txt) | Python dependencies |

## Configuration

Create `.env` file:

```bash
SERVICENOW_INSTANCE_URL=https://your-instance.service-now.com
SERVICENOW_BASIC_AUTH_USER=admin     # Optional fallback
SERVICENOW_BASIC_AUTH_PASS=password  # Optional fallback
PORT=8080
MCP_TRANSPORT=sse
```

## Key Components

### Header Extraction ([`mcp_server.py`](mcp_server.py) lines 56-98)

For SSE transport, headers are on `request_context.request`:

```python
def _extract_token_from_context(ctx: Context) -> Optional[str]:
    headers = None

    # SSE transport: headers on request_context.request (Starlette)
    if ctx and ctx.request_context:
        request = getattr(ctx.request_context, "request", None)
        if request and hasattr(request, "headers"):
            headers = request.headers

    # Fallback: FastMCP dependency injection
    if headers is None:
        from fastmcp.server.dependencies import get_http_request
        headers = get_http_request().headers

    # Extract X-User-Token (user JWT for ServiceNow)
    user_token = headers.get("x-user-token")
    if user_token and user_token.startswith("eyJ"):
        return user_token

    return None
```

### Basic Auth Fallback ([`mcp_server.py`](mcp_server.py) lines 30-53)

```python
class FallbackSession(requests.Session):
    """Falls back to Basic Auth if JWT fails."""

    def request(self, method, url, **kwargs):
        resp = super().request(method, url, **kwargs)

        if resp.status_code == 401 and "Bearer" in self.headers.get("Authorization", ""):
            # JWT failed, try Basic Auth
            self.auth = (BASIC_USER, BASIC_PASS)
            resp = super().request(method, url, **kwargs)

        return resp
```

### Available Tools

| Tool | Description |
|------|-------------|
| `query_table` | Query any ServiceNow table |
| `list_incidents` | List incidents with filters |
| `search_incidents` | Search by description |
| `get_ticket` | Get ticket by number |
| `create_ticket` | Create new ticket |
| `update_ticket` | Update existing ticket |
| `add_comment` | Add comment/work note |
| `list_problems` | List problem records |
| `list_changes` | List change requests |

## Deployment

```bash
# Deploy to Cloud Run
gcloud run deploy servicenow-mcp \
  --source . \
  --region us-central1 \
  --no-allow-unauthenticated \
  --set-env-vars="SERVICENOW_INSTANCE_URL=https://your-instance.service-now.com"
```

### Grant Agent Engine Access

```bash
PROJECT_NUMBER=$(gcloud projects describe $PROJECT_ID --format="value(projectNumber)")

gcloud run services add-iam-policy-binding servicenow-mcp \
  --member="serviceAccount:service-$PROJECT_NUMBER@gcp-sa-aiplatform-re.iam.gserviceaccount.com" \
  --role="roles/run.invoker" \
  --region=us-central1
```

## Local Development

```bash
# Run locally
uv run python mcp_server.py

# Server starts at http://localhost:8080/sse
```

## Testing

### Direct Tool Call

```bash
# With JWT
curl -X POST http://localhost:8080/sse \
  -H "X-User-Token: eyJ..." \
  -H "Content-Type: application/json"
```

### Via MCP Inspector

```bash
npx @anthropic/mcp-inspector http://localhost:8080/sse
```

## Logs

```bash
# Cloud Run logs
gcloud run services logs read servicenow-mcp --region=us-central1 --limit=50

# Filter for MCP messages
gcloud logging read 'resource.type="cloud_run_revision" AND textPayload:("[MCP]")' \
  --project=$PROJECT_ID --limit=20
```

## Security

1. **Cloud Run IAM:** Only Agent Engine SA can invoke
2. **X-User-Token:** User identity for ServiceNow auth
3. **Basic Auth Fallback:** Only for testing (optional)

## Related Documentation

- [Agent Engine](../agent/README.md) - header_provider implementation
- [Security Flow](../docs/security-flow.md) - Token flow
- [ServiceNow Setup](../docs/servicenow-setup.md) - OIDC configuration
