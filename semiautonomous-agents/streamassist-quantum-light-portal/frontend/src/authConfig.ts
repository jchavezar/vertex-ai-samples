import { Configuration } from '@azure/msal-browser';

export const CLIENT_ID = '7868d053-cf9c-4848-be5a-f9bbf8279234';
export const TENANT_ID = 'de46a3fd-0d68-4b25-8343-6eb5d71afce9';

export const msalConfig: Configuration = {
  auth: {
    clientId: CLIENT_ID,
    authority: `https://login.microsoftonline.com/${TENANT_ID}`,
    redirectUri: window.location.origin,
  },
  cache: {
    cacheLocation: 'sessionStorage',
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
};
