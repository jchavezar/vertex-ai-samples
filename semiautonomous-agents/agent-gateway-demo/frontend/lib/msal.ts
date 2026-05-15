import { Configuration, PopupRequest, PublicClientApplication } from "@azure/msal-browser";

const tenantId = process.env.NEXT_PUBLIC_ENTRA_TENANT_ID || "common";
const clientId = process.env.NEXT_PUBLIC_ENTRA_CLIENT_ID || "";

export const msalConfig: Configuration = {
  auth: {
    clientId,
    authority: `https://login.microsoftonline.com/${tenantId}`,
    redirectUri: typeof window === "undefined" ? "" : window.location.origin,
  },
  cache: { cacheLocation: "sessionStorage", storeAuthStateInCookie: false },
};

export const loginRequest: PopupRequest = {
  scopes: (process.env.NEXT_PUBLIC_ENTRA_SCOPES ||
    "https://graph.microsoft.com/Files.Read offline_access openid profile")
    .split(/\s+/)
    .filter(Boolean),
};

let _instance: PublicClientApplication | null = null;
export function getMsal(): PublicClientApplication {
  if (typeof window === "undefined") throw new Error("msal in SSR");
  if (!_instance) _instance = new PublicClientApplication(msalConfig);
  return _instance;
}
