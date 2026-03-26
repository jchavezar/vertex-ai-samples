import { Configuration, PopupRequest } from "@azure/msal-browser";

// MSAL configuration for Entra ID
// TODO: Replace with your Entra ID values or use environment variables
export const msalConfig: Configuration = {
  auth: {
    clientId: import.meta.env.VITE_ENTRA_CLIENT_ID || "YOUR_ENTRA_CLIENT_ID",
    authority: `https://login.microsoftonline.com/${import.meta.env.VITE_ENTRA_TENANT_ID || "YOUR_ENTRA_TENANT_ID"}`,
    redirectUri: window.location.origin,
  },
  cache: {
    cacheLocation: "sessionStorage",
    storeAuthStateInCookie: false,
  },
};

// Scopes for MSAL login
export const loginRequest: PopupRequest = {
  scopes: ["openid", "profile", "email"],
};

// GCP Workforce Identity Federation config
export const gcpConfig = {
  workforcePoolId: import.meta.env.VITE_WIF_POOL_ID || "YOUR_WIF_POOL_ID",
  providerId: import.meta.env.VITE_WIF_PROVIDER_ID || "YOUR_WIF_PROVIDER_ID",
  location: "global",
};

// Agent Engine config
export const agentConfig = {
  projectId: import.meta.env.VITE_GCP_PROJECT_ID || "YOUR_PROJECT_ID",
  location: import.meta.env.VITE_GCP_LOCATION || "us-central1",
  agentEngineId: import.meta.env.VITE_AGENT_ENGINE_ID || "YOUR_AGENT_ENGINE_ID",
};
