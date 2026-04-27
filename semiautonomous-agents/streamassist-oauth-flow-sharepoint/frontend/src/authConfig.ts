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

export const loginRequest = {
  scopes: [
    `api://${CLIENT_ID}/user_impersonation`,
    'openid',
    'profile',
    'email',
  ],
  prompt: 'select_account' as const,
};
