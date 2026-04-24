# Replicate end-to-end — copy-paste commands

This is the full set of commands to reproduce the StreamAssist + ServiceNow + WIF setup from a clean state.

> Prereqs: `gcloud` authenticated to your GCP project, ServiceNow admin credentials, Python 3, `curl`, `jq`. The browser tester is the only piece that needs a browser.

---

## 0 · Variables you need

Set these once at the top of your shell. **Replace every `<...>` with your real value.**

```bash
# ── GCP project ──────────────────────────────────────────────────────────────
export PROJECT_NUMBER="<NUMERIC_PROJECT_NUMBER>"        # e.g. 744983026323
export PROJECT_ID="<PROJECT_ID>"                        # e.g. sharepoint-wif-agent
export LOCATION="global"                                # or "us"

# ── Microsoft Entra (Portal App for MSAL login — already exists) ────────────
export PORTAL_APP_CLIENT_ID="<RAW_PORTAL_APP_GUID>"    # NO api:// prefix
export TENANT_ID="<ENTRA_TENANT_GUID>"

# ── Workforce Identity Federation (already exists) ──────────────────────────
export WIF_POOL_ID="<sn-wif-pool-prod>"
export WIF_PROVIDER_ID="<entra-id-oidc>"

# ── Discovery Engine app (existing engine you'll attach SN to) ──────────────
export ENGINE_ID="<gemini-enterprise-prod>"

# ── ServiceNow ──────────────────────────────────────────────────────────────
export SN_INSTANCE="https://<your-instance>.service-now.com"
export SN_ADMIN_USER="admin"
export SN_ADMIN_PASS="<sn-admin-password>"

# ── Generated below — leave blank for now ───────────────────────────────────
export SN_CLIENT_ID=""
export SN_CLIENT_SECRET=""
export SN_REFRESH_TOKEN=""
export CONNECTOR_ID=""
```

---

## 1 · Create the ServiceNow OAuth Application Registry entry

```bash
# Generate a 32-char client_id and 40-char client_secret (alphanumeric only —
# DE rejects setUpDataConnector if the secret has special chars).
SN_CLIENT_ID=$(python3 -c "import secrets,string;print(''.join(secrets.choice(string.ascii_lowercase+string.digits) for _ in range(32)))")
SN_CLIENT_SECRET=$(python3 -c "import secrets,string;print(''.join(secrets.choice(string.ascii_lowercase+string.digits) for _ in range(40)))")
echo "SN_CLIENT_ID=$SN_CLIENT_ID"
echo "SN_CLIENT_SECRET=$SN_CLIENT_SECRET"

# Create the OAuth app via SN's Table API (no Console UI needed)
SN_APP_SYS_ID=$(curl -s -u "$SN_ADMIN_USER:$SN_ADMIN_PASS" \
  -H "Accept: application/json" -H "Content-Type: application/json" \
  -X POST "$SN_INSTANCE/api/now/table/oauth_entity" \
  -d @- <<EOF | jq -r '.result.sys_id'
{
  "name": "Gemini Enterprise Federated Connector",
  "client_id": "$SN_CLIENT_ID",
  "client_secret": "$SN_CLIENT_SECRET",
  "type": "client",
  "active": "true",
  "redirect_url": "https://vertexaisearch.cloud.google.com/oauth-redirect",
  "refresh_token_lifespan": "8640000",
  "access_token_lifespan": "1800"
}
EOF
)
echo "SN_APP_SYS_ID=$SN_APP_SYS_ID"
```

---

## 2 · Bootstrap the admin refresh token (password grant)

```bash
SN_REFRESH_TOKEN=$(curl -s -X POST "$SN_INSTANCE/oauth_token.do" \
  --data-urlencode "grant_type=password" \
  --data-urlencode "client_id=$SN_CLIENT_ID" \
  --data-urlencode "client_secret=$SN_CLIENT_SECRET" \
  --data-urlencode "username=$SN_ADMIN_USER" \
  --data-urlencode "password=$SN_ADMIN_PASS" \
  | jq -r '.refresh_token')
echo "SN_REFRESH_TOKEN length: ${#SN_REFRESH_TOKEN}"   # should be ~80+ chars
```

---

## 3 · Create the Discovery Engine ServiceNow connector

```bash
TS=$(date +%s)
CONNECTOR_ID="servicenow-connector-$TS"

curl -s -X POST \
  -H "Authorization: Bearer $(gcloud auth print-access-token)" \
  -H "X-Goog-User-Project: $PROJECT_NUMBER" \
  -H "Content-Type: application/json" \
  "https://discoveryengine.googleapis.com/v1alpha/projects/$PROJECT_NUMBER/locations/$LOCATION:setUpDataConnector" \
  -d @- <<EOF | jq .
{
  "collectionId": "$CONNECTOR_ID",
  "collectionDisplayName": "$CONNECTOR_ID",
  "dataConnector": {
    "dataSource": "servicenow",
    "connectorModes": ["FEDERATED"],
    "refreshInterval": "86400s",
    "params": {
      "instance_uri": "$SN_INSTANCE",
      "client_id": "$SN_CLIENT_ID",
      "client_secret": "$SN_CLIENT_SECRET",
      "user_account": "$SN_ADMIN_USER",
      "password": "$SN_ADMIN_PASS"
    },
    "destinationConfigs": [
      {"key": "host_url", "destinations": [{"host": "$SN_INSTANCE"}]}
    ],
    "entities": [
      {"entityName": "knowledge_base"},
      {"entityName": "knowledge"},
      {"entityName": "incident"},
      {"entityName": "catalog"},
      {"entityName": "users"},
      {"entityName": "attachment"}
    ],
    "actionConfig": {
      "actionParams": {
        "auth_type": "OAUTH",
        "instance_uri": "$SN_INSTANCE",
        "client_id": "$SN_CLIENT_ID",
        "client_secret": "$SN_CLIENT_SECRET",
        "auth_uri": "$SN_INSTANCE/oauth_auth.do",
        "token_uri": "$SN_INSTANCE/oauth_token.do"
      },
      "createBapConnection": true
    }
  }
}
EOF

echo "CONNECTOR_ID=$CONNECTOR_ID"
```

Allowed `entityName` values (any other returns 400): `knowledge_base`, `knowledge`, `incident`, `catalog`, `users`, `attachment`.

### Wait for state = ACTIVE (usually 1-3 min)

```bash
for i in {1..20}; do
  STATE=$(curl -s -H "Authorization: Bearer $(gcloud auth print-access-token)" \
    -H "X-Goog-User-Project: $PROJECT_NUMBER" \
    "https://discoveryengine.googleapis.com/v1alpha/projects/$PROJECT_NUMBER/locations/$LOCATION/collections/$CONNECTOR_ID/dataConnector" \
    | jq -r '.state')
  echo "[$i] state=$STATE"
  [ "$STATE" = "ACTIVE" ] && break
  sleep 15
done
```

---

## 4 · Attach the 5 SN datastores to your engine

```bash
# Get current dataStoreIds (so we don't lose existing connections)
EXISTING=$(curl -s -H "Authorization: Bearer $(gcloud auth print-access-token)" \
  -H "X-Goog-User-Project: $PROJECT_NUMBER" \
  "https://discoveryengine.googleapis.com/v1alpha/projects/$PROJECT_NUMBER/locations/$LOCATION/collections/default_collection/engines/$ENGINE_ID" \
  | jq -r '[.dataStoreIds[]?] + ["'$CONNECTOR_ID'_knowledge","'$CONNECTOR_ID'_incident","'$CONNECTOR_ID'_catalog","'$CONNECTOR_ID'_users","'$CONNECTOR_ID'_attachment"] | unique | tojson')

curl -s -X PATCH \
  -H "Authorization: Bearer $(gcloud auth print-access-token)" \
  -H "X-Goog-User-Project: $PROJECT_NUMBER" \
  -H "Content-Type: application/json" \
  "https://discoveryengine.googleapis.com/v1alpha/projects/$PROJECT_NUMBER/locations/$LOCATION/collections/default_collection/engines/$ENGINE_ID?updateMask=dataStoreIds" \
  -d "{\"dataStoreIds\": $EXISTING}" | jq '.dataStoreIds'
```

---

## 5 · Set engine-level `workforceIdentityPoolProvider` (Cloud Console)

This is the **most-missed step**. Without it, federated search returns 0 results.

1. Open Cloud Console → AI Applications → Apps
2. Switch the location filter to match your `$LOCATION`
3. Click your engine (`$ENGINE_ID`)
4. The "Set up your workforce identity" card appears on the dashboard — click **Set up identity**
5. Choose **Use a third-party identity provider**
6. Workforce pool ID: `locations/global/workforcePools/<WIF_POOL_ID>`
7. Workforce provider ID: `<WIF_PROVIDER_ID>`
8. Click **Confirm Workforce Identity** → "Authentication configurations have been updated successfully"

> Skip this if you already did it for SharePoint or any other federated connector on the same engine.

---

## 6 · Per-user `acquireAndStoreRefreshToken` (one-time per user, via the tester UI)

Each user that will search must do this once. The tester UI (`tester/index.html`) drives it via the **Connect ServiceNow** button. The flow is:

1. User signs in to Microsoft (MSAL) → id_token
2. Browser STS-exchanges → WIF GCP access_token
3. User clicks **Connect ServiceNow** → SN OAuth popup → user logs in to SN as their SN-side user → clicks Allow
4. SN redirects to `vertexaisearch.cloud.google.com/oauth-redirect?code=...`
5. Browser POSTs `{fullRedirectUri}` to DE with the WIF GCP token as Bearer
6. DE exchanges the SN code for an SN refresh_token, stores it under the WIF principal hash

To test programmatically (admin user as test subject):

```bash
# 1. Capture an SN auth code via cookie-based consent (admin user)
COOKIES=$(mktemp)
curl -s -c "$COOKIES" -d "user_name=$SN_ADMIN_USER&user_password=$SN_ADMIN_PASS&sys_action=sysverb_login" \
  "$SN_INSTANCE/login.do" -o /dev/null

# Hit /oauth_auth.do, follow the consent form
curl -s -b "$COOKIES" -L -o /tmp/sn-form.html \
  "$SN_INSTANCE/oauth_auth.do?response_type=code&client_id=$SN_CLIENT_ID&redirect_uri=https%3A%2F%2Fvertexaisearch.cloud.google.com%2Foauth-redirect&state=test-$(date +%s)"

# Extract sysparm_ck and submit consent
CK=$(grep -oP 'name="sysparm_ck"[^>]*value="\K[^"]+' /tmp/sn-form.html | head -1)
SN_REDIRECT=$(curl -s -b "$COOKIES" -L \
  -d "sysparm_ck=$CK&oauth_auth_check_action=authorize" \
  "$SN_INSTANCE/oauth_auth.do" -o /dev/null -w "%{url_effective}")
echo "$SN_REDIRECT"   # → https://vertexaisearch.cloud.google.com/oauth-redirect?code=...

# 2. Get the user's MSAL JWT (skip — for testing use admin gcloud token instead)
#    For real users this comes from MSAL.loginPopup() in the browser.

# 3. STS-exchange the user's id_token for a WIF GCP token (real users do this client-side)
WIF_GCP=$(curl -s -X POST "https://sts.googleapis.com/v1/token" \
  --data-urlencode "grant_type=urn:ietf:params:oauth:grant-type:token-exchange" \
  --data-urlencode "audience=//iam.googleapis.com/locations/global/workforcePools/$WIF_POOL_ID/providers/$WIF_PROVIDER_ID" \
  --data-urlencode "scope=https://www.googleapis.com/auth/cloud-platform" \
  --data-urlencode "requested_token_type=urn:ietf:params:oauth:token-type:access_token" \
  --data-urlencode "subject_token_type=urn:ietf:params:oauth:token-type:id_token" \
  --data-urlencode "subject_token=<USER_MSAL_JWT>" \
  | jq -r '.access_token')

# 4. Call acquireAndStoreRefreshToken with the WIF token + the SN redirect URL
curl -s -X POST \
  -H "Authorization: Bearer $WIF_GCP" \
  -H "X-Goog-User-Project: $PROJECT_NUMBER" \
  -H "Content-Type: application/json" \
  "https://discoveryengine.googleapis.com/v1alpha/projects/$PROJECT_NUMBER/locations/$LOCATION/collections/$CONNECTOR_ID/dataConnector:acquireAndStoreRefreshToken" \
  -d "{\"fullRedirectUri\": \"$SN_REDIRECT\"}"

# 5. Verify storage worked: should return refreshTokenInfo with an accessToken
curl -s -X POST \
  -H "Authorization: Bearer $WIF_GCP" \
  -H "X-Goog-User-Project: $PROJECT_NUMBER" \
  -H "Content-Type: application/json" \
  "https://discoveryengine.googleapis.com/v1alpha/projects/$PROJECT_NUMBER/locations/$LOCATION/collections/$CONNECTOR_ID/dataConnector:acquireAccessToken" \
  -d '{}' | jq .
```

---

## 7 · Run a search (streamAssist) — final E2E test

```bash
curl -s -X POST \
  -H "Authorization: Bearer $WIF_GCP" \
  -H "X-Goog-User-Project: $PROJECT_NUMBER" \
  -H "Content-Type: application/json" \
  "https://discoveryengine.googleapis.com/v1alpha/projects/$PROJECT_NUMBER/locations/$LOCATION/collections/default_collection/engines/$ENGINE_ID/assistants/default_assistant:streamAssist" \
  -d "{
    \"query\": {\"text\": \"list any open incidents\"},
    \"toolsSpec\": {
      \"vertexAiSearchSpec\": {
        \"dataStoreSpecs\": [
          {\"dataStore\": \"projects/$PROJECT_NUMBER/locations/$LOCATION/collections/default_collection/dataStores/${CONNECTOR_ID}_incident\"},
          {\"dataStore\": \"projects/$PROJECT_NUMBER/locations/$LOCATION/collections/default_collection/dataStores/${CONNECTOR_ID}_knowledge\"}
        ]
      }
    }
  }" | jq '[.[] | .answer.replies[]? | .groundedContent | {text: .content.text, sources: (.textGroundingMetadata.references[]?.content)}]'
```

If you see `text` filled in and `sources` populated with ServiceNow records → **done**. ✅

---

## 8 · Run the visual tester

```bash
cd tester
cp .env.example .env
# fill in: PORTAL_APP_CLIENT_ID, TENANT_ID, PROJECT_NUMBER, WIF_POOL_ID,
#         WIF_PROVIDER_ID, ENGINE_ID, LOCATION, SERVICENOW_CONNECTOR_ID,
#         SERVICENOW_INSTANCE_URI, SN_OAUTH_CLIENT_ID
python3 serve.py
# → open http://localhost:5176
```

The tester walks any user through the same 4 steps (Login → Exchange → Connect → Search) and shows every API call's input/output in real time on the right panel.

---

## Failure-mode lookup

| Symptom | Likely cause | Section |
|---|---|---|
| `setUpDataConnector` returns 400 *Missing Parameter User Account* | `params.user_account` + `params.password` missing | §3 |
| `setUpDataConnector` returns 400 *Missing Parameter Auth URI* | `actionConfig.actionParams.auth_uri/token_uri` missing | §3 |
| `setUpDataConnector` returns 400 *entity type must be one of …* | Used invalid entity name (e.g. `problem`) | §3 (allowed list) |
| `acquireAccessToken` returns 404 | No per-user token stored — run §6 | §6 |
| `acquireAccessToken` returns 200 with empty body | Token stored under a DIFFERENT identity (ADC vs WIF mismatch) — re-run §6 with the correct WIF GCP token | §6 |
| streamAssist returns 200 but no sources | Engine `workforceIdentityPoolProvider` not set | §5 |
| HTTP 400 `LICENSE_WITHOUT_SUBSCRIPTION_TIER` | User has no license seat — assign in Console | (Cloud Console → Manage subscriptions) |
| HTTP 401 on streamAssist | WIF principalSet missing `roles/discoveryengine.editor` | grant on the project |
| HTTP 500 on streamAssist | `X-Goog-User-Project` is the project ID, not the project number | use the numeric project number |

---

For the conceptual flow (why each step exists, what tokens are produced, how the bridge works), see **[FLOW.md](FLOW.md)** and **[AUTH_SEQUENCE.md](AUTH_SEQUENCE.md)**.
