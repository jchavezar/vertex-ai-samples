import { Configuration, PopupRequest } from "@azure/msal-browser";

export const ENTRA_CLIENT_ID = import.meta.env.VITE_CLIENT_ID || "7868d053-cf9c-4848-be5a-f9bbf8279234";
export const ENTRA_TENANT_ID = import.meta.env.VITE_TENANT_ID || "de46a3fd-0d68-4b25-8343-6eb5d71afce9";

export const msalConfig: Configuration = {
  auth: {
    clientId: ENTRA_CLIENT_ID,
    authority: `https://login.microsoftonline.com/${ENTRA_TENANT_ID}`,
    redirectUri: window.location.origin,
  },
  cache: {
    cacheLocation: "sessionStorage",
    storeAuthStateInCookie: false,
  },
};

export const loginRequest: PopupRequest = {
  scopes: ["openid", "profile", "email", "Sites.ReadWrite.All", "Files.ReadWrite.All"],
  prompt: "select_account",
};
