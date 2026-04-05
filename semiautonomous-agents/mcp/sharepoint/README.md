# Microsoft 365 MCP Server

MCP (Model Context Protocol) server for Microsoft 365 access via Microsoft Graph API. Enables LLM assistants to interact with SharePoint, OneDrive, Outlook, Calendar, and Teams using delegated (user) authentication.

## Supported LLM Clients

| Client | Transport | Status |
|--------|-----------|--------|
| Claude Code | streamable-http | Tested |
| Gemini CLI | streamable-http | Compatible |
| Cursor | stdio / http | Compatible |
| Continue | stdio / http | Compatible |
| Any MCP-compatible client | streamable-http | Compatible |

## Prerequisites

- Python 3.11+
- [uv](https://docs.astral.sh/uv/) package manager
- Google Cloud account (for Cloud Run deployment)
- Azure AD app registration with delegated permissions

## Quick Start

### 1. Clone and setup

```bash
cd mcp/sharepoint
uv venv
source .venv/bin/activate
uv pip install -r requirements.txt
```

### 2. Create Azure AD App Registration

1. Go to [Azure Portal > App Registrations](https://portal.azure.com/#view/Microsoft_AAD_RegisteredApps)
2. Click **New registration**
   - Name: `MS365 MCP Server`
   - Supported account types: Single tenant
3. Go to **Authentication**
   - Add platform: Mobile and desktop applications
   - Select: `https://login.microsoftonline.com/common/oauth2/nativeclient`
   - Enable: **Allow public client flows** = Yes
4. Go to **API Permissions** > Add Microsoft Graph **Delegated** permissions:
   - `User.Read`
   - `Sites.ReadWrite.All`
   - `Files.ReadWrite.All`
   - `Mail.ReadWrite`
   - `Calendars.ReadWrite`
   - `Team.ReadBasic.All`
   - `Channel.ReadBasic.All`
   - `Chat.ReadWrite`
5. Click **Grant admin consent**
6. Copy the **Application (client) ID**

### 3. Configure environment

```bash
cp .env.example .env
# Edit .env with your Client ID and Tenant ID
```

### 4. Run locally

```bash
export MS365_CLIENT_ID="your-client-id"
export MS365_TENANT_ID="your-tenant-id"
uv run python server.py
```

Server starts at `http://localhost:8080/mcp`

### 5. Connect your LLM client

**Claude Code:**
```bash
claude mcp add ms365 --transport http http://localhost:8080/mcp
```

**Gemini CLI:**
```bash
# Add to ~/.gemini/settings.json
{
  "mcpServers": {
    "ms365": {
      "url": "http://localhost:8080/mcp"
    }
  }
}
```

### 6. Authenticate

In your LLM client, run:
```
login to microsoft 365
```

Follow the device code flow instructions.

## Cloud Run Deployment

See [DEPLOY.md](DEPLOY.md) for Google Cloud Run deployment instructions.

## Available Tools

| Tool | Description |
|------|-------------|
| `ms365_login` | Start device code authentication |
| `ms365_complete_login` | Complete authentication after browser sign-in |
| `ms365_logout` | Clear cached tokens |
| `ms365_verify_login` | Check authentication status |
| `sp_list_sites` | List SharePoint sites |
| `sp_list_drives` | List document libraries in a site |
| `sp_list_files` | List files/folders in a drive |
| `sp_upload_file` | Upload file to SharePoint/OneDrive |
| `sp_download_file` | Download file content |
| `sp_create_folder` | Create new folder |
| `sp_search_files` | Search files by name/content |
| `onedrive_list_files` | List personal OneDrive files |
| `mail_list_messages` | List emails |
| `mail_get_message` | Get email details |
| `mail_send` | Send email |
| `mail_search` | Search emails |
| `cal_list_events` | List calendar events |
| `cal_create_event` | Create calendar event |
| `cal_get_event` | Get event details |
| `teams_list_teams` | List Teams memberships |
| `teams_list_channels` | List channels in a team |
| `teams_send_channel_message` | Post to a channel |
| `teams_list_chats` | List personal chats |
| `teams_send_chat_message` | Send chat message |

## Security

- Uses MSAL device code flow (no client secrets required)
- Tokens cached in-memory only (cleared on restart)
- Delegated permissions = user sees only their own data
- Cloud Run deployment with `--no-allow-unauthenticated`

## License

MIT
