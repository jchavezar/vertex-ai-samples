# ServiceNow OIDC Configuration

[← Back to Main README](../README.md) | [Security Flow](security-flow.md)

## Overview

This guide configures ServiceNow to accept JWT tokens from Microsoft Entra ID for authentication.

## Prerequisites

- ServiceNow instance with admin access
- Entra ID app registration completed (see [Entra ID Setup](entra-id-setup.md))
- User accounts in ServiceNow with email addresses matching Entra ID

## 1. OIDC Provider Configuration

Navigate to: **System OAuth** → **OIDC Provider Configuration**

### Create New Configuration

| Field | Value | Notes |
|-------|-------|-------|
| **Name** | `Entra ID OIDC Config` | Display name |
| **OIDC Metadata URL** | `https://login.microsoftonline.com/TENANT_ID/v2.0/.well-known/openid-configuration` | Replace TENANT_ID |
| **User Claim** | `email` | Claim to identify user |
| **User Field** | `Email` | ServiceNow field to match |
| **Enable JTI claim verification** | **Unchecked** | Important: Must be disabled |

### Why Disable JTI Verification?

JTI (JWT ID) verification prevents token reuse. However, when the same token is used across multiple requests (which happens with AI agents), this causes authentication failures.

## 2. OAuth OIDC Entity

Navigate to: **System OAuth** → **Application Registry**

### Create New Application

| Field | Value |
|-------|-------|
| **Name** | `Entra ID OIDC` |
| **Client ID** | Your Entra ID Application (client) ID |
| **Client Secret** | Leave empty (for public clients) |
| **OAuth OIDC Provider Configuration** | Select `Entra ID OIDC Config` |
| **Active** | Checked |

## 3. User Mapping

### Email Field Requirement

ServiceNow users must have their **Email** field populated with the same email address used in Entra ID.

To verify:
1. Navigate to **User Administration** → **Users**
2. Find a test user
3. Ensure **Email** field matches their Entra ID email

### Bulk Update (if needed)

If users don't have email set, you can bulk update:

```javascript
// Background script to copy user_name to email (if user_name is email)
var gr = new GlideRecord('sys_user');
gr.addNullQuery('email');
gr.addActiveQuery();
gr.query();
while (gr.next()) {
    if (gr.user_name.indexOf('@') > -1) {
        gr.email = gr.user_name;
        gr.update();
    }
}
```

## 4. Testing Authentication

### Manual Test with curl

```bash
# Get a valid Entra ID token (from browser dev tools or MSAL)
TOKEN="eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9..."

# Test against ServiceNow API
curl -X GET "https://YOUR_INSTANCE.service-now.com/api/now/table/incident?sysparm_limit=1" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Accept: application/json"
```

### Expected Responses

| Response | Meaning |
|----------|---------|
| `200 OK` + JSON data | Authentication successful |
| `401 Unauthorized` | Token invalid or user not found |
| `403 Forbidden` | User found but no access to resource |

## 5. Troubleshooting

### 401 Unauthorized

1. **Check OIDC Configuration:**
   - Verify Metadata URL is correct
   - Ensure User Claim is `email`
   - Ensure User Field is `Email`

2. **Check User Mapping:**
   - Verify user exists in ServiceNow
   - Verify email field matches token claim

3. **Check Token:**
   ```bash
   # Decode JWT (base64)
   echo "TOKEN_PAYLOAD" | base64 -d
   ```
   Verify the `email` claim exists and is correct.

### Basic Auth Fallback

For testing, the MCP server supports Basic Auth fallback:

```bash
# In Cloud Run environment variables
SERVICENOW_BASIC_AUTH_USER=admin
SERVICENOW_BASIC_AUTH_PASS=password
```

The server will automatically fall back to Basic Auth if JWT fails.

## Configuration Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                     SERVICENOW INSTANCE                          │
│                                                                  │
│  ┌─────────────────────────────────────────────────────────────┐│
│  │              OIDC PROVIDER CONFIGURATION                     ││
│  │                                                              ││
│  │  Metadata URL → Fetches Entra ID public keys                ││
│  │  User Claim: email                                          ││
│  │  User Field: Email                                          ││
│  │                                                              ││
│  │       ┌──────────────────────────────────────────┐          ││
│  │       │         JWT VALIDATION                    │          ││
│  │       │                                          │          ││
│  │       │  1. Verify signature (RS256)             │          ││
│  │       │  2. Check issuer matches Entra ID        │          ││
│  │       │  3. Check audience matches Client ID     │          ││
│  │       │  4. Extract email claim                  │          ││
│  │       │  5. Find user by Email field             │          ││
│  │       └──────────────────────────────────────────┘          ││
│  └─────────────────────────────────────────────────────────────┘│
│                                                                  │
│  ┌─────────────────────────────────────────────────────────────┐│
│  │                     USER TABLE                               ││
│  │                                                              ││
│  │  sys_user:                                                   ││
│  │    user_name: jsmith                                         ││
│  │    email: jsmith@company.com  ← Must match JWT email claim  ││
│  │    first_name: John                                          ││
│  │    last_name: Smith                                          ││
│  └─────────────────────────────────────────────────────────────┘│
└─────────────────────────────────────────────────────────────────┘
```

## Security Considerations

1. **Token Expiration:** Entra ID tokens expire (typically 1 hour). Ensure your frontend refreshes tokens.

2. **User Provisioning:** Users must exist in ServiceNow. Consider SCIM provisioning for automation.

3. **ACLs:** ServiceNow ACLs still apply. Users only see data they have access to.

## Related Documentation

- [Entra ID Setup](entra-id-setup.md) - Microsoft app registration
- [Security Flow](security-flow.md) - Token flow diagrams
- [GCP Setup](gcp-setup.md) - WIF + Agent Engine setup
- [Architecture](architecture.md) - E2E system diagram
- [MCP Server](../mcp-server/README.md) - FastMCP implementation
