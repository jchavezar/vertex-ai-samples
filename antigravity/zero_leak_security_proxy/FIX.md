# Problem Root Cause: Option 2 (Cloud Run Backend + Local Frontend) Authentication Issue

## What happened?
When we switched to "Option 2" (testing the local React frontend against the deployed Cloud Run backend API), you saw "Error: Failed to generate response" in the UI for the chat.

The reason is **Google Cloud Run Native IAM**.
1. The backend is deployed with `--no-allow-unauthenticated` according to your organization's Zero-Leak security policy. This means the Google Cloud Front End (GFE) intercepts all requests to the `mcp-sharepoint-server.run.app` URL and strictly requires a **Google Identity token**.
2. However, the React application's `useTerminalChat.ts` hook attaches the **Microsoft SharePoint (MSAL) token** in the `Authorization: Bearer <token>` header.
3. Because the MSAL token is not a valid Google Identity token, Cloud Run's security perimeter rejects the request with a **403 Forbidden** before it ever reaches the FastAPI application.
4. (FastAPI does actually validate the MSAL token inside `main.py`, but it never gets a chance because Cloud Run blocks it at the edge).

## Why did it work previously?
If it worked before, it was likely because you were testing "Option 1" where BOTH the frontend and backend were running locally (`http://127.0.0.1`). In local development, there is no Google IAM edge layer, so the FastAPI app directly received the MSAL token and parsed it successfully.

## How to Fix "Option 2"
Because organization policy forbids setting the Cloud Run service to `allUsers` (`--allow-unauthenticated`), the React frontend must somehow pass the MSAL token AND a Google ID token simultaneously when hitting the Cloud Run proxy from localhost.

To achieve this cleanly for local testing WITHOUT compromising the architecture:
We will configure the `vite.config.ts` proxy to intercept the local `/chat` calls, automatically fetch your developer Google Identity Token (`gcloud auth print-identity-token`), attach it to the `Authorization: Bearer` header, and move the MSAL token to a new custom header (e.g., `X-SharePoint-Token`). The backend FastAPI code will then be updated to read the MSAL token from `X-SharePoint-Token` instead.

I have documented this in `.agent/DEBUG_CLOUD_RUN_PROXY.md` and `FIX.md` so the next session can implement this fix seamlessly!
