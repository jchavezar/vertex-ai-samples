# Setup Guide

## Prerequisites

- Python 3.11+
- Microsoft 365 account (personal or organizational)
- Azure App Registration with delegated permissions

## 1. Create Azure App Registration

1. Go to [Azure Portal](https://portal.azure.com) > **App registrations**
2. Click **New registration**:
   - Name: `ms365-mcp`
   - Supported account types: Choose based on your needs
   - Redirect URI: Leave empty (device code flow)
3. Note the **Application (client) ID** and **Directory (tenant) ID**

## 2. Configure API Permissions

Add these **Delegated** permissions:

| API | Permission | Purpose |
|-----|------------|---------|
| Microsoft Graph | `Mail.ReadWrite` | Read/send emails |
| Microsoft Graph | `Mail.Send` | Send emails |
| Microsoft Graph | `Calendars.ReadWrite` | Calendar access |
| Microsoft Graph | `Files.ReadWrite.All` | OneDrive/SharePoint files |
| Microsoft Graph | `Sites.Read.All` | List SharePoint sites |
| Microsoft Graph | `Team.ReadBasic.All` | List Teams |
| Microsoft Graph | `Channel.ReadBasic.All` | List channels |
| Microsoft Graph | `ChannelMessage.Read.All` | Read channel messages |
| Microsoft Graph | `ChannelMessage.Send` | Send channel messages |
| Microsoft Graph | `Chat.ReadWrite` | Access chats |
| Microsoft Graph | `User.Read` | Basic profile |
| Microsoft Graph | `offline_access` | Refresh tokens |

**Important:** Grant admin consent if required by your organization.

## 3. Enable Public Client Flow

1. Go to **Authentication** in your app registration
2. Under **Advanced settings**, set **Allow public client flows** to **Yes**
3. Save changes

## 4. Environment Variables

Create a `.env` file:

```bash
# Required
MS365_CLIENT_ID=your-application-client-id
MS365_TENANT_ID=your-directory-tenant-id

# Optional - use 'common' for multi-tenant
# MS365_TENANT_ID=common

# Server config
PORT=8080
MCP_TRANSPORT=streamable-http
```

## 5. Install Dependencies

```bash
# Create virtual environment
uv venv
source .venv/bin/activate

# Install packages
uv pip install -r requirements.txt
```

## 6. Run Locally

```bash
# Load environment
source .env

# Start server
python server.py
```

## 7. Authenticate

```
1. Call ms365_login() → Get device code + URL
2. Open URL (https://microsoft.com/devicelogin)
3. Enter the device code
4. Sign in with your Microsoft account
5. Call ms365_complete_login() → Done
```

## Token Storage

Tokens are cached in `~/.ms365_tokens.json` (local) or managed by the server in production.

## Troubleshooting

### "AADSTS7000218: The request body must contain 'client_assertion' or 'client_secret'"
- Enable "Allow public client flows" in Azure Portal

### "Insufficient privileges"
- Check that all required permissions are granted
- Admin consent may be needed for some permissions

### "Token expired"
- Run `ms365_logout()` then `ms365_login()` again
- The server automatically refreshes tokens when possible
