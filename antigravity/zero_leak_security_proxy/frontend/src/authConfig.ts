import { PublicClientApplication } from "@azure/msal-browser";
import type { Configuration } from "@azure/msal-browser";

export const msalConfig: Configuration = {
  auth: {
    clientId: import.meta.env.VITE_CLIENT_ID || "",
    authority: `https://login.microsoftonline.com/${import.meta.env.VITE_TENANT_ID || ""}`,
    redirectUri: "/",
  },
  cache: {
    cacheLocation: "sessionStorage",
  },
};

export const loginRequest = {
  scopes: ["User.Read", "Sites.Read.All", "Files.Read.All"],
};

export const msalInstance = new PublicClientApplication(msalConfig);

