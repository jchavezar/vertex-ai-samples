/**
 * MSAL Configuration for Entra ID Authentication
 *
 * IMPORTANT: The scope uses api://{client-id}/user_impersonation to get
 * an access token with the correct audience for WIF exchange.
 */

// These MUST be set in .env - see .env.example
const CLIENT_ID = import.meta.env.VITE_CLIENT_ID;
const TENANT_ID = import.meta.env.VITE_TENANT_ID;

if (!CLIENT_ID || !TENANT_ID) {
  console.error('VITE_CLIENT_ID and VITE_TENANT_ID must be set in environment');
}

export const msalConfig = {
  auth: {
    clientId: CLIENT_ID,
    authority: `https://login.microsoftonline.com/${TENANT_ID}`,
    redirectUri: window.location.origin,
    postLogoutRedirectUri: window.location.origin,
  },
  cache: {
    cacheLocation: 'sessionStorage',
    storeAuthStateInCookie: false,
  },
};

// Scopes for login - using custom API scope for WIF-compatible token
export const loginRequest = {
  scopes: [
    `api://${CLIENT_ID}/user_impersonation`,
    'openid',
    'profile',
    'email',
  ],
};

// Graph scopes (if needed for profile info)
export const graphScopes = {
  scopes: ['User.Read'],
};
