# Setup Guide

## Prerequisites

- Python 3.11+
- Google Cloud project with Workspace APIs enabled
- OAuth 2.0 credentials (Desktop or TVs and Limited Input devices)

## 1. Create Google Cloud OAuth Credentials

1. Go to [Google Cloud Console](https://console.cloud.google.com/apis/credentials)
2. Create OAuth 2.0 Client ID:
   - Application type: **TVs and Limited Input devices** (recommended) or Desktop
   - Name: `gworkspace-mcp`
3. Download the credentials JSON or copy Client ID/Secret

## 2. Enable Required APIs

Enable these APIs in your Google Cloud project:

```bash
gcloud services enable gmail.googleapis.com
gcloud services enable drive.googleapis.com
gcloud services enable calendar-json.googleapis.com
gcloud services enable docs.googleapis.com
gcloud services enable sheets.googleapis.com
```

## 3. Environment Variables

Create a `.env` file:

```bash
# Required
GOOGLE_CLIENT_ID=your-client-id.apps.googleusercontent.com

# Optional (not needed for TVs type)
GOOGLE_CLIENT_SECRET=your-client-secret

# Server config
PORT=8080
MCP_TRANSPORT=streamable-http
```

## 4. Install Dependencies

```bash
# Create virtual environment
uv venv
source .venv/bin/activate

# Install packages
uv pip install -r requirements.txt
```

## 5. Run Locally

```bash
# Load environment
source .env

# Start server
python server.py
```

## 6. Authenticate

Once the server is running, use the MCP tools:

```
1. Call gworkspace_login() → Get auth URL
2. Open URL in browser → Sign in → Copy code
3. Call gworkspace_complete_login(code="...") → Done
```

## OAuth Scopes

The server requests these scopes:

| Scope | Purpose |
|-------|---------|
| `gmail.modify` | Read/send emails, manage labels |
| `drive.file` | Access files created by app |
| `calendar` | Full calendar access |
| `documents` | Read/write Google Docs |
| `spreadsheets` | Read/write Google Sheets |
| `userinfo.email` | Get user's email address |
| `userinfo.profile` | Get user's name |

## Troubleshooting

### "Access blocked: This app's request is invalid"
- Ensure redirect URI is correctly configured
- For TVs type, use `urn:ietf:wg:oauth:2.0:oob`

### "Token has been expired or revoked"
- Run `gworkspace_logout()` then `gworkspace_login()` again

### "Insufficient Permission"
- The user may not have access to the requested resource
- Check that required APIs are enabled in the project
