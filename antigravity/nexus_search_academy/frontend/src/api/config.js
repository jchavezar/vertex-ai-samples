export const CONFIG = {
  PROJECT_NUMBER: import.meta.env.VITE_PROJECT_NUMBER || "REDACTED_PROJECT_NUMBER",
  LOCATION: import.meta.env.VITE_LOCATION || "global",
  WIF_POOL: import.meta.env.VITE_WIF_POOL || "entra-id-oidc-pool-d",
  WIF_PROVIDER: import.meta.env.VITE_WIF_PROVIDER || "entra-id-oidc-pool-provider-de",
  DATA_STORE_ID: import.meta.env.VITE_DATA_STORE_ID || "5817ee80-82a4-49e3-a19c-2cedc73a6300",
  ENGINE_ID: import.meta.env.VITE_ENGINE_ID || "deloitte-demo",
  TENANT_ID: import.meta.env.VITE_TENANT_ID || "REDACTED_TENANT_ID",
  MS_APP_ID: import.meta.env.VITE_MS_APP_ID || "REDACTED_CLIENT_ID",
  SP_APP_ID: import.meta.env.VITE_SP_APP_ID || "5817ee80-82a4-49e3-a19c-2cedc73a6300",
  ISSUER: import.meta.env.VITE_ISSUER || "https://login.microsoftonline.com/REDACTED_TENANT_ID/v2.0",
};
