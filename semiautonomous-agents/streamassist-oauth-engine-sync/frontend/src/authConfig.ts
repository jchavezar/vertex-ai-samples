const CLIENT_ID = import.meta.env.VITE_CLIENT_ID || "00000000-0000-0000-0000-000000000000";
const TENANT_ID = import.meta.env.VITE_TENANT_ID || "00000000-0000-0000-0000-000000000000";

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

export const loginRequest = {
  scopes: [
    `api://${CLIENT_ID}/user_impersonation`,
    'openid',
    'profile',
    'email',
  ],
  prompt: 'select_account' as const,
};
