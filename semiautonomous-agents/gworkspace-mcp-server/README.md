# Google Workspace MCP Server

MCP server providing access to Google Workspace APIs: Gmail, Drive, Calendar, Docs, and Sheets.

## Quick Start

```bash
# 1. Install dependencies
uv venv && source .venv/bin/activate
uv pip install -r requirements.txt

# 2. Set environment variables
export GOOGLE_CLIENT_ID="your-client-id"
export GOOGLE_CLIENT_SECRET="your-client-secret"

# 3. Run the server
python server.py
```

## Features

| Service | Capabilities |
|---------|-------------|
| **Gmail** | Read, send, search emails, manage labels |
| **Drive** | List, upload, download, delete files |
| **Calendar** | List, create, update, delete events |
| **Docs** | Read, create, append to documents |
| **Sheets** | Read, write, append to spreadsheets |

## Tools (37 total)

- **Authentication:** 4 tools (login, logout, verify, complete)
- **Gmail:** 6 tools
- **Drive:** 8 tools
- **Calendar:** 6 tools
- **Docs:** 5 tools
- **Sheets:** 6 tools

## Documentation

- [Setup Guide](docs/SETUP.md) - Installation and configuration
- [Tools Reference](docs/TOOLS.md) - All 37 tools with examples
- [Deployment Guide](docs/DEPLOYMENT.md) - Cloud Run deployment

## Architecture

```
gworkspace-mcp-server/
├── server.py           # FastMCP server + auth tools
├── auth.py             # Google OAuth flow
├── tools/
│   ├── gmail.py        # Gmail operations
│   ├── drive.py        # Drive operations
│   ├── calendar.py     # Calendar operations
│   ├── docs.py         # Docs operations
│   └── sheets.py       # Sheets operations
├── deploy.sh           # Cloud Run deployment
└── Dockerfile          # Container image
```

## Connect to Claude Code

```bash
# Start proxy
gcloud run services proxy gworkspace-mcp --region us-central1 --port=8081

# Add to Claude Code
claude mcp add gworkspace --transport http http://localhost:8081/mcp
```
