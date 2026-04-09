# Microsoft 365 MCP Server

MCP server providing access to Microsoft 365 services: Outlook Mail, SharePoint, OneDrive, Teams, and Calendar.

## Quick Start

```bash
# 1. Install dependencies
uv venv && source .venv/bin/activate
uv pip install -r requirements.txt

# 2. Set environment variables
export MS365_CLIENT_ID="your-client-id"
export MS365_TENANT_ID="your-tenant-id"

# 3. Run the server
python server.py
```

## Features

| Service | Capabilities |
|---------|-------------|
| **Mail (Outlook)** | Read, send, search emails |
| **SharePoint** | List sites, drives, files; upload/download |
| **OneDrive** | Personal file storage access |
| **Teams** | List teams, channels, chats; send messages |
| **Calendar** | List, create, delete events |

## Tools (31 total)

- **Authentication:** 4 tools (login, logout, verify, complete)
- **SharePoint/OneDrive:** 9 tools
- **Mail:** 5 tools
- **Calendar:** 5 tools
- **Teams:** 7 tools

## Documentation

- [Setup Guide](docs/SETUP.md) - Installation and configuration
- [Tools Reference](docs/TOOLS.md) - All 31 tools with examples
- [Deployment Guide](docs/DEPLOYMENT.md) - Cloud Run deployment

## Architecture

```
ms365-mcp-server/
├── server.py           # FastMCP server + tool registration
├── tools/
│   ├── auth_tools.py   # MSAL device code flow
│   ├── sharepoint.py   # SharePoint/OneDrive operations
│   ├── mail.py         # Outlook mail operations
│   ├── calendar.py     # Calendar operations
│   └── teams.py        # Teams operations
├── deploy.sh           # Cloud Run deployment
└── Dockerfile          # Container image
```

## Connect to Claude Code

```bash
# Start proxy
gcloud run services proxy ms365-mcp --region us-central1 --port=8083

# Add to Claude Code
claude mcp add ms365 --transport http http://localhost:8083/mcp
```

## Authentication Flow

Uses Microsoft's **device code flow** (delegated authentication):

1. Call `ms365_login()` - Get device code and URL
2. Open URL in browser, enter code
3. Sign in with Microsoft account
4. Call `ms365_complete_login()` - Exchange code for tokens
