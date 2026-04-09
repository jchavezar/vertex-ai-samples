"""WIF Auth Monitor - FastAPI backend for audit log analysis."""

import os
import json
from datetime import datetime, timedelta, timezone
from collections import defaultdict

import httpx
import msal
from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from google.cloud import logging as cloud_logging
from google import genai

load_dotenv()

PROJECT_ID = os.getenv("PROJECT_ID", "sharepoint-wif-agent")
PROJECT_NUMBER = os.getenv("PROJECT_NUMBER", "REDACTED_PROJECT_NUMBER")
LOCATION = os.getenv("LOCATION", "us-central1")

app = FastAPI(title="WIF Auth Monitor")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

log_client = cloud_logging.Client(project=PROJECT_ID)
genai_client = genai.Client(vertexai=True, project=PROJECT_ID, location=LOCATION)

# ===== Microsoft Graph API (Entra ID) =====
AZURE_CLIENT_ID = os.getenv("AZURE_CLIENT_ID", "REDACTED_PORTAL_CLIENT_ID")
AZURE_CLIENT_SECRET = os.getenv("AZURE_CLIENT_SECRET", "")
AZURE_TENANT_ID = os.getenv("AZURE_TENANT_ID", "REDACTED_TENANT_ID")
GRAPH_BASE = "https://graph.microsoft.com/v1.0"

_msal_app = None


def get_msal_app():
    global _msal_app
    if _msal_app is None:
        _msal_app = msal.ConfidentialClientApplication(
            AZURE_CLIENT_ID,
            authority=f"https://login.microsoftonline.com/{AZURE_TENANT_ID}",
            client_credential=AZURE_CLIENT_SECRET,
        )
    return _msal_app


def get_graph_token():
    """Get an access token for Microsoft Graph using client credentials."""
    app = get_msal_app()
    result = app.acquire_token_for_client(scopes=["https://graph.microsoft.com/.default"])
    if "access_token" in result:
        return result["access_token"]
    raise Exception(f"Failed to get Graph token: {result.get('error_description', result)}")


def graph_get(path: str, params: dict | None = None):
    """Make a GET request to Microsoft Graph API."""
    token = get_graph_token()
    resp = httpx.get(
        f"{GRAPH_BASE}{path}",
        headers={"Authorization": f"Bearer {token}"},
        params=params or {},
        timeout=30,
    )
    resp.raise_for_status()
    return resp.json()

SYSTEM_PROMPT = """You are a WIF (Workload Identity Federation) authentication expert analyzing audit logs for a SharePoint + Google Discovery Engine integration.

Architecture overview:
- 1 Azure App Registration (client-id: REDACTED_PORTAL_CLIENT_ID) used for user auth via MSAL
- WIF Pool: sp-wif-pool-v2 with 2 providers:
  - ge-login-provider (aud: 7868d053... bare) — accepts ID Tokens for Gemini Enterprise login
  - entra-provider (aud: api://7868d053...) — accepts Access Tokens for Custom Portal (StreamAssist direct)
- A SEPARATE Connector App Registration — used by Discovery Engine to connect to SharePoint (with Sites.Search.All, AllSites.Read delegated permissions)

Auth flow (Custom Portal path — the one used in production):
1. User logs in via MSAL in React frontend → Entra ID issues Access Token with aud: api://7868d053...
2. Frontend sends Access Token to custom Portal backend (FastAPI on Cloud Run) via X-Entra-Id-Token header
3. Portal backend calls STS (sts.googleapis.com/v1/token) to exchange Entra JWT for GCP Access Token — this is the WIF token exchange
4. GCP token carries user identity as principal in workforcePools/sp-wif-pool-v2/subject/...
5. Portal backend calls StreamAssist API DIRECTLY with GCP token + dataStoreSpecs — NOT through Agent Engine
6. Discovery Engine calls AcquireAccessToken on the SharePoint Connector — this is where it gets the Connector App's credentials
7. Connector App queries SharePoint ON BEHALF of the user (delegated permissions) — SharePoint enforces ACLs based on user identity
8. Only documents the user is authorized to see are returned

Note: There is also a Gemini Enterprise direct login path using ge-login-provider (aud: bare client-id with ID Tokens), but the custom portal uses the entra-provider (aud: api://client-id with Access Tokens).

Key insight: AcquireAccessToken proves the mapping between the WIF identity (Portal App) and the Connector App. Same principalSubject appears in both StreamAssist and AcquireAccessToken calls.

When explaining logs, be specific about what each field means and how it proves the auth chain is working correctly. Use plain language."""

METHOD_LABELS = {
    "google.identity.sts.v1.SecurityTokenService.ExchangeToken": "STS Exchange",
    "google.cloud.discoveryengine.v1alpha.AssistantService.StreamAssist": "StreamAssist",
    "google.cloud.discoveryengine.v1main.DataConnectorService.AcquireAccessToken": "AcquireAccessToken",
    "google.cloud.discoveryengine.v1alpha.SessionService.CreateSession": "CreateSession",
    "google.cloud.discoveryengine.v1main.CompletionService.AdvancedCompleteQuery": "AutoComplete",
    "google.cloud.discoveryengine.v1alpha.AnalyticsService.RefreshDashboardSessionTokens": "RefreshDashboard",
}

METHOD_COLORS = {
    "STS Exchange": "blue",
    "StreamAssist": "purple",
    "AcquireAccessToken": "orange",
    "CreateSession": "green",
    "AutoComplete": "gray",
    "RefreshDashboard": "gray",
}


def parse_entry(entry):
    """Parse a cloud logging entry into a structured dict."""
    proto = entry.payload if isinstance(entry.payload, dict) else {}
    auth_info = proto.get("authenticationInfo", {})
    auth_list = proto.get("authorizationInfo", [])
    request_meta = proto.get("requestMetadata", {})
    method = proto.get("methodName", "")
    label = METHOD_LABELS.get(method, method.split(".")[-1])

    principal_subject = auth_info.get("principalSubject", "")
    return {
        "timestamp": entry.timestamp.isoformat() if entry.timestamp else "",
        "method": method,
        "methodLabel": label,
        "color": METHOD_COLORS.get(label, "gray"),
        "principal": principal_subject,
        "principalHash": principal_subject.split("/subject/")[-1] if "/subject/" in principal_subject else "",
        "oauthClient": auth_info.get("oauthInfo", {}).get("oauthClientId", ""),
        "resource": proto.get("resourceName", ""),
        "permission": auth_list[0].get("permission", "") if auth_list else "",
        "granted": auth_list[0].get("granted", False) if auth_list else None,
        "callerIp": request_meta.get("callerIp", ""),
        "userAgent": request_meta.get("callerSuppliedUserAgent", ""),
        "status": proto.get("status", {}),
        "request": proto.get("request", {}),
        "response": proto.get("response", {}),
        "severity": entry.severity,
        "insertId": entry.insert_id,
    }


def group_into_chains(entries):
    """Group log entries into request chains by principal + timestamp proximity."""
    by_principal = defaultdict(list)
    for e in entries:
        if e["principal"]:
            by_principal[e["principal"]].append(e)

    chains = []
    for principal, logs in by_principal.items():
        logs.sort(key=lambda x: x["timestamp"])
        current_chain = [logs[0]]
        for log in logs[1:]:
            t1 = datetime.fromisoformat(current_chain[-1]["timestamp"])
            t2 = datetime.fromisoformat(log["timestamp"])
            if abs((t2 - t1).total_seconds()) <= 10:
                current_chain.append(log)
            else:
                chains.append({
                    "principal": principal,
                    "principalHash": current_chain[0]["principalHash"],
                    "startTime": current_chain[0]["timestamp"],
                    "endTime": current_chain[-1]["timestamp"],
                    "events": current_chain,
                    "methods": list(dict.fromkeys(e["methodLabel"] for e in current_chain)),
                })
                current_chain = [log]
        chains.append({
            "principal": principal,
            "principalHash": current_chain[0]["principalHash"],
            "startTime": current_chain[0]["timestamp"],
            "endTime": current_chain[-1]["timestamp"],
            "events": current_chain,
            "methods": list(dict.fromkeys(e["methodLabel"] for e in current_chain)),
        })

    chains.sort(key=lambda c: c["startTime"], reverse=True)
    return chains


def query_logs(minutes=60, principal=None, services=None):
    """Query audit logs from Cloud Logging."""
    now = datetime.now(timezone.utc)
    start = now - timedelta(minutes=minutes)

    if services is None:
        services = ["discoveryengine.googleapis.com", "sts.googleapis.com"]

    service_filter = " OR ".join(
        f'protoPayload.serviceName="{s}"' for s in services
    )
    filter_str = (
        f'logName="projects/{PROJECT_ID}/logs/cloudaudit.googleapis.com%2Fdata_access"'
        f" AND ({service_filter})"
        f' AND timestamp>="{start.isoformat()}"'
    )
    if principal:
        filter_str += f' AND protoPayload.authenticationInfo.principalSubject:"{principal}"'

    entries = []
    for entry in log_client.list_entries(
        filter_=filter_str,
        order_by="timestamp desc",
        page_size=200,
    ):
        entries.append(parse_entry(entry))
        if len(entries) >= 200:
            break

    return entries


class ExplainRequest(BaseModel):
    log_entry: dict | list | None = None
    chain: dict | None = None
    question: str | None = None


class ChatRequest(BaseModel):
    message: str
    history: list[dict] = []


CONNECTOR_INFO = {
    "name": "sharepoint-data-def-connector",
    "type": "THIRD_PARTY_FEDERATED",
    "dataSource": "sharepoint",
    "tenant_id": "REDACTED_TENANT_ID",
    "instance_uri": "https://CONTOSO.sharepoint.com",
    "auth_type": "OAUTH",
    "connectorModes": ["FEDERATED", "ACTIONS"],
}

WIF_INFO = {
    "pool": "sp-wif-pool-v2",
    "providers": {
        "ge-login-provider": {
            "audience": "REDACTED_PORTAL_CLIENT_ID",
            "tokenType": "ID Token",
            "use": "Gemini Enterprise UI login",
        },
        "entra-provider": {
            "audience": "api://REDACTED_PORTAL_CLIENT_ID",
            "tokenType": "Access Token",
            "use": "Custom Portal backend — StreamAssist direct call via WIF exchange",
        },
    },
    "attributeMapping": {
        "google.subject": "assertion.sub",
    },
    "tenant_id": "REDACTED_TENANT_ID",
    "issuer": "https://sts.windows.net/REDACTED_TENANT_ID/",
}


@app.get("/api/health")
def health():
    return {"status": "ok", "project": PROJECT_ID}


@app.get("/api/logs")
def get_logs(minutes: int = 60, principal: str | None = None):
    entries = query_logs(minutes=minutes, principal=principal)
    chains = group_into_chains(entries) if entries else []
    principals = list({e["principalHash"] for e in entries if e["principalHash"]})
    return {
        "entries": entries,
        "chains": chains,
        "principals": principals,
        "total": len(entries),
        "query_minutes": minutes,
    }


@app.get("/api/chain/{principal_hash}")
def get_chain(principal_hash: str, minutes: int = 120):
    entries = query_logs(minutes=minutes, principal=principal_hash)
    chains = group_into_chains(entries) if entries else []
    return {
        "principalHash": principal_hash,
        "chains": chains,
        "total_events": len(entries),
    }


@app.post("/api/explain")
def explain(req: ExplainRequest):
    if req.chain:
        context = json.dumps(req.chain, indent=2, default=str)
        default_q = "Explain this complete auth chain step by step. What does each event prove about the WIF→Discovery Engine→SharePoint mapping?"
    elif req.log_entry:
        context = json.dumps(req.log_entry, indent=2, default=str)
        default_q = "Explain what this audit log entry means in the context of the WIF auth flow. What does it prove?"
    else:
        return {"error": "Provide log_entry or chain"}

    question = req.question or default_q
    prompt = f"Audit log data:\n```json\n{context}\n```\n\nQuestion: {question}"

    response = genai_client.models.generate_content(
        model="gemini-2.5-flash-lite",
        contents=prompt,
        config={"system_instruction": SYSTEM_PROMPT},
    )
    return {"explanation": response.text}


@app.post("/api/chat")
def chat(req: ChatRequest):
    contents = []
    for msg in req.history:
        contents.append({"role": msg["role"], "parts": [{"text": msg["content"]}]})
    contents.append({"role": "user", "parts": [{"text": req.message}]})

    response = genai_client.models.generate_content(
        model="gemini-2.5-flash-lite",
        contents=contents,
        config={"system_instruction": SYSTEM_PROMPT},
    )
    return {"response": response.text}


# ===== Microsoft Graph API Endpoints =====

@app.get("/api/microsoft/status")
def microsoft_status():
    """Check if Microsoft Graph integration is configured."""
    configured = bool(AZURE_CLIENT_SECRET)
    if not configured:
        return {"configured": False, "error": "AZURE_CLIENT_SECRET not set in .env"}
    try:
        get_graph_token()
        return {"configured": True, "tenant_id": AZURE_TENANT_ID, "client_id": AZURE_CLIENT_ID}
    except Exception as e:
        return {"configured": False, "error": str(e)}


@app.get("/api/microsoft/apps")
def microsoft_apps():
    """List all app registrations in the tenant with their API permissions."""
    try:
        data = graph_get("/applications", {"$select": "appId,displayName,requiredResourceAccess,web,api,createdDateTime"})
        apps = []
        for app_reg in data.get("value", []):
            permissions = []
            for resource in app_reg.get("requiredResourceAccess", []):
                resource_id = resource.get("resourceAppId", "")
                for perm in resource.get("resourceAccess", []):
                    permissions.append({
                        "resourceAppId": resource_id,
                        "id": perm.get("id", ""),
                        "type": perm.get("type", ""),
                    })
            apps.append({
                "appId": app_reg.get("appId", ""),
                "displayName": app_reg.get("displayName", ""),
                "createdDateTime": app_reg.get("createdDateTime", ""),
                "permissions": permissions,
            })
        return {"apps": apps, "total": len(apps)}
    except Exception as e:
        return {"error": str(e)}


@app.get("/api/microsoft/service-principals")
def microsoft_service_principals():
    """List service principals (enterprise apps) to find SharePoint connector."""
    try:
        data = graph_get(
            "/servicePrincipals",
            {"$select": "appId,displayName,servicePrincipalType,appOwnerOrganizationId,tags", "$top": "100"},
        )
        return {"servicePrincipals": data.get("value", []), "total": len(data.get("value", []))}
    except Exception as e:
        return {"error": str(e)}


@app.get("/api/microsoft/consent-grants")
def microsoft_consent_grants(app_id: str | None = None):
    """Get OAuth2 permission grants (delegated consent) for an app — proves ACL enforcement."""
    try:
        # First find the service principal (enterprise app) for the given app_id
        target_app_id = app_id or "REDACTED_CONNECTOR_CLIENT_ID"  # default to discovered connector
        sp_data = graph_get(
            "/servicePrincipals",
            {"$filter": f"appId eq '{target_app_id}'", "$select": "id,appId,displayName"},
        )
        sps = sp_data.get("value", [])
        if not sps:
            return {"error": f"No service principal found for appId {target_app_id}", "grants": []}

        sp_id = sps[0]["id"]
        sp_name = sps[0].get("displayName", "")

        # Get OAuth2 permission grants (delegated consent)
        grants_data = graph_get(f"/servicePrincipals/{sp_id}/oauth2PermissionGrants")
        grants = []
        for g in grants_data.get("value", []):
            # Resolve the resource service principal name
            resource_id = g.get("resourceId", "")
            resource_name = ""
            try:
                res_sp = graph_get(f"/servicePrincipals/{resource_id}", {"$select": "displayName,appId"})
                resource_name = res_sp.get("displayName", "")
            except Exception:
                pass

            grants.append({
                "consentType": g.get("consentType", ""),  # "AllPrincipals" = admin consent for all users
                "scope": g.get("scope", ""),  # The actual permissions granted
                "principalId": g.get("principalId"),  # null for AllPrincipals
                "resourceId": resource_id,
                "resourceName": resource_name,
                "startTime": g.get("startTime", ""),
                "expiryTime": g.get("expiryTime", ""),
            })

        # Also get app role assignments (application permissions)
        roles_data = graph_get(f"/servicePrincipals/{sp_id}/appRoleAssignments")
        role_assignments = []
        for r in roles_data.get("value", []):
            role_assignments.append({
                "resourceDisplayName": r.get("resourceDisplayName", ""),
                "principalDisplayName": r.get("principalDisplayName", ""),
                "createdDateTime": r.get("createdDateTime", ""),
            })

        return {
            "appId": target_app_id,
            "displayName": sp_name,
            "servicePrincipalId": sp_id,
            "oauth2PermissionGrants": grants,
            "appRoleAssignments": role_assignments,
            "aclProof": {
                "hasDelegatedConsent": any(g["consentType"] == "AllPrincipals" for g in grants),
                "isAdminConsent": any(g["consentType"] == "AllPrincipals" for g in grants),
                "delegatedScopes": [g["scope"] for g in grants if g["consentType"] == "AllPrincipals"],
                "explanation": "AllPrincipals consent means the app acts ON BEHALF of each user. "
                               "SharePoint enforces ACLs based on the user's identity, not the app's. "
                               "Only documents the user is authorized to see are returned.",
            },
        }
    except Exception as e:
        return {"error": str(e), "grants": []}


@app.get("/api/microsoft/sharepoint-apps")
def microsoft_sharepoint_apps():
    """Find all app registrations with SharePoint API permissions — identifies potential connector apps."""
    SHAREPOINT_RESOURCE_ID = "00000003-0000-0ff1-ce00-000000000000"
    # Known SharePoint permission IDs
    SP_PERMISSION_NAMES = {
        "4e0d77b0-96ba-4398-af14-3baa780278f4": "Sites.Search.All",
        "1002502a-9a71-4426-8551-69ab83452fab": "AllSites.Read",
        "640ddd16-e5b7-4d71-9690-3f4022699ee7": "AllSites.FullControl",
        "9ac4404a-0323-446d-b334-b4ae4d18b38a": "Sites.ReadWrite.All",
        "20d37865-089c-4dee-8c41-6967602d4ac8": "Sites.FullControl.All (Application)",
    }
    try:
        data = graph_get("/applications", {"$select": "appId,displayName,requiredResourceAccess,createdDateTime"})
        sp_apps = []
        for app_reg in data.get("value", []):
            sp_perms = []
            for resource in app_reg.get("requiredResourceAccess", []):
                if resource.get("resourceAppId") == SHAREPOINT_RESOURCE_ID:
                    for perm in resource.get("resourceAccess", []):
                        perm_id = perm.get("id", "")
                        sp_perms.append({
                            "id": perm_id,
                            "name": SP_PERMISSION_NAMES.get(perm_id, perm_id),
                            "type": "Delegated" if perm.get("type") == "Scope" else "Application",
                        })
            if sp_perms:
                is_portal = app_reg.get("appId") == AZURE_CLIENT_ID
                sp_apps.append({
                    "appId": app_reg.get("appId", ""),
                    "displayName": app_reg.get("displayName", ""),
                    "createdDateTime": app_reg.get("createdDateTime", ""),
                    "sharePointPermissions": sp_perms,
                    "isPortalApp": is_portal,
                    "role": "Portal App (WIF user auth)" if is_portal else "Potential Connector App",
                })
        return {"apps": sp_apps, "total": len(sp_apps)}
    except Exception as e:
        return {"error": str(e)}


@app.get("/api/microsoft/correlate")
def correlate_logs():
    """Discover the Connector App by matching SharePoint permissions with GCP connector config."""
    try:
        # Step 1: Get all apps with SharePoint permissions from Entra ID
        sp_result = microsoft_sharepoint_apps()
        if "error" in sp_result:
            return {"error": sp_result["error"], "connector_app": None}

        sp_apps = sp_result.get("apps", [])

        # Step 2: Get GCP AcquireAccessToken events to confirm connector is active
        gcp_entries = query_logs(minutes=1440)
        acquire_events = [e for e in gcp_entries if e["methodLabel"] == "AcquireAccessToken"]

        # Step 3: Identify the connector app — it's NOT the portal app,
        # and has delegated SharePoint permissions (Sites.Search.All / AllSites.Read)
        connector_candidates = []
        for app in sp_apps:
            if app["isPortalApp"]:
                continue
            delegated_sp = [p for p in app["sharePointPermissions"] if p["type"] == "Delegated"]
            has_search = any("Search" in p["name"] or "AllSites" in p["name"] for p in delegated_sp)
            if has_search:
                connector_candidates.append({
                    **app,
                    "confidence": "high" if len(delegated_sp) >= 2 else "medium",
                    "reason": f"Has {len(delegated_sp)} delegated SharePoint permissions including search/read",
                })

        # Best candidate: most delegated SharePoint permissions, most recently created
        connector_candidates.sort(key=lambda x: (x["confidence"] == "high", x["createdDateTime"]), reverse=True)
        connector_app = connector_candidates[0] if connector_candidates else None

        return {
            "connector_app": connector_app,
            "all_sharepoint_apps": sp_apps,
            "connector_candidates": connector_candidates,
            "gcp_acquire_events": len(acquire_events),
            "portal_app_id": AZURE_CLIENT_ID,
            "method": "SharePoint permission analysis (sign-in logs require Azure AD Premium)",
        }
    except Exception as e:
        return {"error": str(e), "connector_app": None}


@app.get("/api/mapping")
def get_mapping():
    """Return the full identity mapping proof between WIF and Connector."""
    connector_client_id = None
    connector_display_name = None
    all_sharepoint_apps = []

    if AZURE_CLIENT_SECRET:
        try:
            correlation = correlate_logs()
            if correlation.get("connector_app"):
                connector_client_id = correlation["connector_app"]["appId"]
                connector_display_name = correlation["connector_app"].get("displayName")
            all_sharepoint_apps = correlation.get("all_sharepoint_apps", [])
        except Exception:
            pass

    result = {
        "wif": WIF_INFO,
        "connector": {
            **CONNECTOR_INFO,
            "discovered_client_id": connector_client_id,
            "discovered_display_name": connector_display_name,
        },
        "proof": {
            "shared_tenant": WIF_INFO["tenant_id"] == CONNECTOR_INFO["tenant_id"],
            "tenant_id": WIF_INFO["tenant_id"],
            "wif_client_id": AZURE_CLIENT_ID,
            "connector_client_id": connector_client_id or "Not yet discovered",
            "connector_display_name": connector_display_name,
            "mapping_mechanism": "Same principalSubject appears in both StreamAssist and AcquireAccessToken audit logs",
            "acl_enforcement": "Connector uses delegated permissions (Sites.Search.All) — queries SharePoint as the WIF user, not as itself",
            "flow": [
                "1. User authenticates via MSAL in React frontend → Entra ID issues Access Token with aud: api://7868d053...",
                "2. Frontend sends Access Token to custom Portal backend (FastAPI on Cloud Run) via X-Entra-Id-Token header",
                "3. Portal backend calls STS (sts.googleapis.com/v1/token) → exchanges Entra JWT for GCP Access Token",
                "4. GCP token carries user identity as principal: .../workforcePools/sp-wif-pool-v2/subject/{hash}",
                "5. Portal backend calls StreamAssist API directly with GCP token + dataStoreSpecs",
                "6. Discovery Engine calls AcquireAccessToken on the Connector (sharepoint-data-def-connector)",
                "7. Connector authenticates to SharePoint using its OWN client-id + secret (separate app registration)",
                "8. But scoped to the USER's identity via delegated permissions → SharePoint enforces ACLs",
            ],
        },
        "microsoft_integration": bool(AZURE_CLIENT_SECRET),
        "all_sharepoint_apps": all_sharepoint_apps,
    }
    return result


# ===== Offline StreamAssist Test (uses captured JWT from portal) =====

PORTAL_WIF_POOL_ID = "sp-wif-pool-v2"
PORTAL_WIF_PROVIDER_ID = "entra-provider"
PORTAL_ENGINE_ID = "gemini-enterprise"
PORTAL_DATA_STORE_ID = "sharepoint-data-def-connector_file"
JWT_CAPTURE_FILE = "/tmp/entra_token.txt"


def _sts_exchange(jwt: str) -> dict:
    """Exchange Entra JWT for GCP workforce token via STS, with timing."""
    import time
    start = time.time()
    resp = httpx.post("https://sts.googleapis.com/v1/token", json={
        "audience": f"//iam.googleapis.com/locations/global/workforcePools/{PORTAL_WIF_POOL_ID}/providers/{PORTAL_WIF_PROVIDER_ID}",
        "grantType": "urn:ietf:params:oauth:grant-type:token-exchange",
        "requestedTokenType": "urn:ietf:params:oauth:token-type:access_token",
        "scope": "https://www.googleapis.com/auth/cloud-platform",
        "subjectToken": jwt,
        "subjectTokenType": "urn:ietf:params:oauth:token-type:jwt",
    }, timeout=10)
    elapsed = time.time() - start
    data = resp.json()
    return {
        "success": "access_token" in data,
        "token": data.get("access_token"),
        "error": data.get("error_description") if "access_token" not in data else None,
        "latency_ms": round(elapsed * 1000),
    }


def _call_stream_assist(gcp_token: str, query: str, with_datastore: bool = True) -> dict:
    """Call StreamAssist with timing, optionally with dataStoreSpecs."""
    import time
    base = f"https://discoveryengine.googleapis.com/v1alpha/projects/{PROJECT_NUMBER}/locations/global/collections/default_collection/engines/{PORTAL_ENGINE_ID}"

    payload = {"query": {"text": query}, "session": "-"}
    if with_datastore:
        payload["toolsSpec"] = {
            "vertexAiSearchSpec": {
                "dataStoreSpecs": [{
                    "dataStore": f"projects/{PROJECT_NUMBER}/locations/global/collections/default_collection/dataStores/{PORTAL_DATA_STORE_ID}"
                }]
            }
        }

    start = time.time()
    resp = httpx.post(
        f"{base}/assistants/default_assistant:streamAssist",
        headers={"Authorization": f"Bearer {gcp_token}", "Content-Type": "application/json"},
        json=payload,
        timeout=90,
    )
    elapsed = time.time() - start

    if not resp.is_success:
        return {"success": False, "error": resp.text[:300], "status": resp.status_code, "latency_ms": round(elapsed * 1000)}

    data = resp.json()
    # Extract answer text
    answer_parts = []
    thoughts = []
    for chunk in data:
        for reply in chunk.get("answer", {}).get("replies", []):
            content = reply.get("groundedContent", {}).get("content", {})
            text = content.get("text", "")
            if content.get("thought"):
                thoughts.append(text.strip())
            elif text:
                answer_parts.append(text)

    return {
        "success": True,
        "answer": "".join(answer_parts),
        "thoughts": thoughts,
        "with_datastore": with_datastore,
        "latency_ms": round(elapsed * 1000),
        "chunks": len(data),
    }


@app.get("/api/test/jwt-status")
def test_jwt_status():
    """Check if a captured JWT is available from the portal."""
    import os
    if not os.path.exists(JWT_CAPTURE_FILE):
        return {"available": False, "message": "No JWT captured yet. Make a query on the portal first."}
    stat = os.stat(JWT_CAPTURE_FILE)
    age_seconds = (datetime.now(timezone.utc) - datetime.fromtimestamp(stat.st_mtime, tz=timezone.utc)).total_seconds()
    with open(JWT_CAPTURE_FILE) as f:
        jwt = f.read().strip()
    # Decode JWT header to check expiry (without verification)
    import base64
    parts = jwt.split(".")
    if len(parts) >= 2:
        payload_b64 = parts[1] + "=" * (4 - len(parts[1]) % 4)
        try:
            payload = json.loads(base64.urlsafe_b64decode(payload_b64))
            exp = payload.get("exp", 0)
            now = datetime.now(timezone.utc).timestamp()
            remaining = exp - now
            return {
                "available": True,
                "expired": remaining <= 0,
                "remaining_seconds": round(remaining),
                "subject": payload.get("sub", ""),
                "name": payload.get("name", ""),
                "audience": payload.get("aud", ""),
                "file_age_seconds": round(age_seconds),
            }
        except Exception:
            pass
    return {"available": True, "jwt_length": len(jwt), "file_age_seconds": round(age_seconds)}


class StreamAssistTestRequest(BaseModel):
    query: str = "salary of Jennifer Anne Walsh?"
    with_datastore: bool = True


@app.post("/api/test/stream-assist")
def test_stream_assist(req: StreamAssistTestRequest):
    """Test StreamAssist using the captured JWT from the portal. Full latency breakdown."""
    import os
    if not os.path.exists(JWT_CAPTURE_FILE):
        return {"error": "No JWT captured. Make a query on the portal first."}

    with open(JWT_CAPTURE_FILE) as f:
        jwt = f.read().strip()

    if not jwt:
        return {"error": "JWT file is empty."}

    # Step 1: STS Exchange
    sts_result = _sts_exchange(jwt)
    if not sts_result["success"]:
        return {"error": f"STS exchange failed: {sts_result['error']}", "sts": sts_result}

    # Step 2: Call StreamAssist
    sa_result = _call_stream_assist(sts_result["token"], req.query, req.with_datastore)

    return {
        "query": req.query,
        "sts_exchange": {"latency_ms": sts_result["latency_ms"]},
        "stream_assist": sa_result,
        "total_latency_ms": sts_result["latency_ms"] + sa_result["latency_ms"],
        "breakdown": {
            "sts_exchange_ms": sts_result["latency_ms"],
            "stream_assist_ms": sa_result["latency_ms"],
            "total_ms": sts_result["latency_ms"] + sa_result["latency_ms"],
        },
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
