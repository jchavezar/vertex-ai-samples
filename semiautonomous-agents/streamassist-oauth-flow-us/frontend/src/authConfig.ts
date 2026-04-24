const CLIENT_ID = import.meta.env.VITE_CLIENT_ID;
const TENANT_ID = import.meta.env.VITE_TENANT_ID;

if (!CLIENT_ID || !TENANT_ID) {
  console.error('VITE_CLIENT_ID and VITE_TENANT_ID must be set in .env');
}

export const msalConfig = {
  auth: {
    clientId: CLIENT_ID,
    authority: `https://login.microsoftonline.com/${TENANT_ID}`,
    redirectUri: window.location.origin,
  },
  cache: {
    cacheLocation: 'sessionStorage' as const,
    storeAuthStateInCookie: false,
  },
};

// Deloitte-pattern scopes: NO `api://...` URI scope.
// MSAL on the v2.0 endpoint issues an id_token whose `aud` claim is the raw
// client_id GUID (not `api://{guid}`), which matches the WIF provider's
// `--client-id="{RAW_GUID}"` config. Same pattern works in `global` and `us`.
export const loginRequest = {
  scopes: ['openid', 'profile', 'email'],
  prompt: 'select_account' as const,
};
