# Microsoft Entra ID Configuration

[← Back to Main README](../README.md) | [Security Flow](security-flow.md)

## Overview

This guide covers the Microsoft Entra ID (Azure AD) configuration required for authentication.

## 1. App Registration

### Create Application

1. Go to [Azure Portal](https://portal.azure.com) → **Microsoft Entra ID** → **App registrations**
2. Click **New registration**
3. Configure:
   - **Name:** `ServiceNow Agent Portal` (or your choice)
   - **Supported account types:** Single tenant (your organization)
   - **Redirect URI:** Leave blank for now

### Get Application IDs

After creation, note these values from the **Overview** page:

| Field | Description | Used In |
|-------|-------------|---------|
| **Application (client) ID** | Unique app identifier | Frontend, WIF Provider, ServiceNow |
| **Directory (tenant) ID** | Your Entra tenant | Frontend, WIF Provider |
| **Object ID** | Internal object ID | Not typically needed |

## 2. Authentication Settings

Navigate to **Authentication** in the left menu.

### Add SPA Redirect URIs

1. Click **Add a platform** → **Single-page application**
2. Add redirect URIs:
   - `http://localhost:3000` (local development)
   - `https://your-frontend.run.app` (production, if deployed)

### Configure Token Settings

Under **Implicit grant and hybrid flows**:
- [ ] Access tokens (ID tokens used instead)
- [x] ID tokens (required for OIDC)

## 3. Token Configuration

Navigate to **Token configuration**.

### Add Claims

Click **Add optional claim** → **ID** token type:

| Claim | Description |
|-------|-------------|
| `email` | User's email address (required for ServiceNow mapping) |
| `preferred_username` | User principal name |
| `upn` | User principal name (alternative) |

## 4. API Permissions

Navigate to **API permissions**.

### Required Permissions

| Permission | Type | Description |
|------------|------|-------------|
| `openid` | Delegated | Sign users in |
| `profile` | Delegated | View basic profile |
| `email` | Delegated | View email address |

Click **Add a permission** → **Microsoft Graph** → **Delegated** → Select permissions above.

Then click **Grant admin consent** (if you have admin rights).

## 5. Frontend Configuration

Update [`frontend/src/authConfig.ts`](../frontend/src/authConfig.ts):

```typescript
export const msalConfig: Configuration = {
  auth: {
    clientId: "YOUR_CLIENT_ID",  // Application (client) ID
    authority: "https://login.microsoftonline.com/YOUR_TENANT_ID",
    redirectUri: window.location.origin,
  },
  cache: {
    cacheLocation: "sessionStorage",
    storeAuthStateInCookie: false,
  },
};

export const loginRequest: PopupRequest = {
  scopes: ["openid", "profile", "email"],
};
```

## 6. GCP Workforce Identity Federation

The same app is used for WIF. In GCP, configure:

```bash
gcloud iam workforce-pools providers create-oidc entra-id-provider \
  --workforce-pool=entra-id-pool \
  --location=global \
  --issuer-uri="https://login.microsoftonline.com/YOUR_TENANT_ID/v2.0" \
  --client-id="YOUR_CLIENT_ID" \
  --attribute-mapping="google.subject=assertion.sub,google.display_name=assertion.preferred_username"
```

## 7. ServiceNow Configuration

The same Client ID is used in ServiceNow OIDC configuration.

See [ServiceNow Setup](servicenow-setup.md) for details.

## Configuration Summary

```
┌─────────────────────────────────────────────────────────────┐
│                    ENTRA ID APP REGISTRATION                 │
│                                                              │
│  Application (client) ID: xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxx │
│  Directory (tenant) ID:   yyyyyyyy-yyyy-yyyy-yyyy-yyyyyyyyyyyy│
│                                                              │
│  Used by:                                                    │
│  ├─ Frontend (MSAL login)                                   │
│  ├─ GCP Workforce Identity Federation (token exchange)     │
│  └─ ServiceNow OIDC Provider (JWT validation)              │
└─────────────────────────────────────────────────────────────┘
```

## Token Contents

Example decoded JWT from Entra ID:

```json
{
  "iss": "https://login.microsoftonline.com/TENANT_ID/v2.0",
  "sub": "unique-user-id",
  "aud": "CLIENT_ID",
  "email": "user@company.com",
  "preferred_username": "user@company.com",
  "name": "User Name",
  "iat": 1234567890,
  "exp": 1234571490
}
```

## Troubleshooting

### "Tenant not found" Error

- Verify the tenant ID is correct
- Check that you're signing into the correct Microsoft account

### "Application not found" Error

- Verify the client ID
- Ensure the app registration is in the correct tenant

### Token Claims Missing

- Add optional claims in Token configuration
- Grant admin consent for API permissions

## Related Documentation

- [GCP Setup](gcp-setup.md) - WIF configuration
- [ServiceNow Setup](servicenow-setup.md) - OIDC provider
- [Security Flow](security-flow.md) - Token flow details
