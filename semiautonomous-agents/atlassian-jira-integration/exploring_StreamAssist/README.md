# exploring-streamassist

Demo web app that drives Gemini Enterprise `streamAssist` against the `jira-testing` engine in vtxdemos and renders every event (request body, chat deltas, raw JSON chunks, planner steps, grounding references) side-by-side with the chat.

- **Backend:** FastAPI + httpx streaming, SSE re-emission (`/api/assist`).
- **Frontend:** vanilla JS + marked + highlight.js, two-pane resizable layout.
- **Deployed:** Cloud Run `exploring-streamassist` in `vtxdemos / us-central1`, public.

## Local

```
python3 -m venv .venv && .venv/bin/pip install -r requirements.txt
GOOGLE_CLOUD_QUOTA_PROJECT=cloud-llm-preview1 .venv/bin/uvicorn main:app --port 8080
```

Open `http://localhost:8080`.

## Deploy

```
bash deploy.sh
```

Uses the Compute Engine default SA (`254356041555-compute@developer.gserviceaccount.com`) which already has `discoveryengine.admin` in vtxdemos.

## Files

- `main.py` — FastAPI app + SSE re-emitter + streaming JSON-array parser + OAuth endpoints.
- `static/index.html`, `static/app.js`, `static/styles.css` — UI with Google Sign-In + Connect Jira button.
- `GROUNDING_OBSERVATIONS.md` — what `streamAssist` exposes about WHY a reference was picked.
- `sample_event_capture.json` — raw `streamAssist` response used to derive the observations.

## End-user OAuth (Option 2)

The app now forwards each end-user's Google OAuth access token to `streamAssist`,
so the federated Jira connector resolves the right per-user 3LO grant (keyed by
`userPseudoId = sha256(sub)[:32]`). If no user is signed in, the app falls back
to the Cloud Run SA token and emits an `auth_mode: service_account` SSE event so
the UI can warn the user.

Endpoints added:
- `GET  /api/auth/config` — bootstraps the frontend with `client_id` + scopes.
- `POST /api/auth/verify` — verifies the Google ID token and sets a signed session cookie carrying `user_pseudo_id`.
- `GET  /api/auth/me` — current session.
- `POST /api/auth/logout` — clears session.
- `GET  /api/auth/jira-consent-url` — engine consent URL the UI opens in a popup.

## Manual setup needed

The OAuth Web client is the only thing a human has to provision by hand:

1. Visit https://console.cloud.google.com/apis/credentials?project=vtxdemos
2. Click **+ CREATE CREDENTIALS → OAuth client ID**, Application type **Web application**, Name `exploring-streamassist`.
3. **Authorized JavaScript origins**: `https://exploring-streamassist-254356041555.us-central1.run.app`
4. **Authorized redirect URIs**: `https://exploring-streamassist-254356041555.us-central1.run.app/api/auth/callback` (not used but Google requires one).
5. Copy the Client ID and run: `echo 'CLIENT_ID_HERE' > .oauth_client_id && bash deploy.sh`
