import { Configuration, PopupRequest } from "@azure/msal-browser";

export const msalConfig: Configuration = {
  auth: {
    clientId: import.meta.env.VITE_ENTRA_CLIENT_ID || "7868d053-cf9c-4848-be5a-f9bbf8279234",
    authority: `https://login.microsoftonline.com/${import.meta.env.VITE_ENTRA_TENANT_ID || "de46a3fd-0d68-4b25-8343-6eb5d71afce9"}`,
    redirectUri: window.location.origin,
  },
  cache: {
    cacheLocation: "sessionStorage",
    storeAuthStateInCookie: false,
  },
};

// Request permissions to read sites and files in Microsoft Graph
export const loginRequest: PopupRequest = {
  scopes: [
    "openid", 
    "profile", 
    "email", 
    "https://graph.microsoft.com/User.Read",
    "https://graph.microsoft.com/Files.Read.All",
    "https://graph.microsoft.com/Sites.Read.All"
  ],
};
