import os
import json
import time
import concurrent.futures
import requests
from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
import google.auth
import google.auth.transport.requests
from google.oauth2 import id_token
from google.auth.transport import requests as grequests

app = FastAPI()

PROJECT_ID = os.getenv("PROJECT_ID", "254356041555")
ENGINE_ID = os.getenv("ENGINE_ID", "vais-workspace_1779830576232")
OAUTH_CLIENT_ID = os.getenv("GOOGLE_OAUTH_CLIENT_ID", "")
LOCATION = "global"
COLLECTION = "default_collection"

SEARCH_URL = (
    f"https://discoveryengine.googleapis.com/v1alpha/projects/{PROJECT_ID}"
    f"/locations/{LOCATION}/collections/{COLLECTION}"
    f"/engines/{ENGINE_ID}/servingConfigs/default_search:search"
)


class SearchRequest(BaseModel):
    query: str
    credential: str    # Google ID token — used only for identity/display
    access_token: str  # Google OAuth access token — used to call Discovery Engine
    page_size: int = 10


def _emit(event_type: str, **kwargs) -> str:
    payload = json.dumps({"type": event_type, "ts": time.time(), **kwargs})
    return f"data: {payload}\n\n"


def _get_token_email(access_token: str) -> str:
    """Best-effort: fetch caller email from Google tokeninfo."""
    try:
        r = requests.get(
            "https://www.googleapis.com/oauth2/v3/tokeninfo",
            params={"access_token": access_token},
            timeout=5,
        )
        if r.status_code == 200:
            return r.json().get("email", "")
    except Exception:
        pass
    return ""


def _verify_token(credential: str):
    request = grequests.Request()
    return id_token.verify_oauth2_token(credential, request, OAUTH_CLIENT_ID)


def _icon(mime: str) -> str:
    if "spreadsheet" in mime:
        return "📊"
    if "presentation" in mime:
        return "📑"
    if "document" in mime:
        return "📝"
    if "pdf" in mime:
        return "📕"
    if "folder" in mime:
        return "📁"
    if "image" in mime:
        return "🖼️"
    return "📄"


def _stream(req: SearchRequest):
    # ── STEP 1: token received ──────────────────────────────────────────────
    yield _emit(
        "log",
        step="auth_receive",
        level="info",
        tag="AUTH",
        message="Google ID token received from browser",
        detail={"token_prefix": req.credential[:24] + "…", "client_id": OAUTH_CLIENT_ID},
    )

    # ── STEP 2: verify token ────────────────────────────────────────────────
    yield _emit(
        "log",
        step="auth_verify",
        level="info",
        tag="AUTH",
        message="Verifying Google ID token signature via google-auth…",
        detail={"issuer": "accounts.google.com", "audience": OAUTH_CLIENT_ID},
    )

    try:
        t0 = time.time()
        id_info = _verify_token(req.credential)
        verify_ms = round((time.time() - t0) * 1000)
    except Exception as e:
        yield _emit(
            "log",
            step="auth_error",
            level="error",
            tag="AUTH",
            message=f"Token verification failed: {e}",
        )
        yield _emit("error", message=str(e))
        return

    user_email = id_info.get("email", "")
    user_name = id_info.get("name", "User")
    import datetime
    exp_dt = datetime.datetime.utcfromtimestamp(id_info.get("exp", 0)).strftime("%H:%M:%S UTC")

    yield _emit(
        "log",
        step="auth_ok",
        level="success",
        tag="AUTH",
        message=f"Token verified in {verify_ms}ms — {user_email}",
        detail={
            "name": user_name,
            "email": user_email,
            "sub": id_info.get("sub", ""),
            "hd": id_info.get("hd", "—"),
            "token_expires": exp_dt,
            "verify_ms": verify_ms,
        },
    )

    # ── STEP 3: user access token ───────────────────────────────────────────
    yield _emit(
        "log",
        step="token_receive",
        level="info",
        tag="TOKEN",
        message="User OAuth access token received from browser",
        detail={
            "scope": "https://www.googleapis.com/auth/cloud-platform",
            "token_prefix": req.access_token[:16] + "…",
            "note": "Workspace datastores require the user's own token — service accounts are blocked",
        },
    )

    # Verify the access token is valid and matches the ID token email
    t0 = time.time()
    token_email = _get_token_email(req.access_token)
    ti_ms = round((time.time() - t0) * 1000)

    if token_email and token_email != user_email:
        yield _emit(
            "log", step="token_mismatch", level="error", tag="TOKEN",
            message=f"Token email mismatch: ID token={user_email}, access token={token_email}",
        )
        yield _emit("error", message="Token mismatch — please sign in again.")
        return

    access_token = req.access_token
    yield _emit(
        "log",
        step="token_ok",
        level="success",
        tag="TOKEN",
        message=f"Access token validated in {ti_ms}ms — {token_email or user_email}",
        detail={
            "email": token_email or user_email,
            "tokeninfo_ms": ti_ms,
            "token_prefix": access_token[:16] + "…",
        },
    )

    # ── STEP 4: build two requests — fast (no summary) + summary ──────────────
    base = {
        "query": req.query,
        "queryExpansionSpec": {"condition": "AUTO"},
        "spellCorrectionSpec": {"mode": "AUTO"},
        "languageCode": "en-US",
        "userInfo": {"timeZone": "America/New_York", "userId": user_email},
    }
    body_fast = {
        **base,
        "pageSize": req.page_size,
        "contentSearchSpec": {
            "extractiveContentSpec": {"maxExtractiveAnswerCount": 1},
            "snippetSpec": {"returnSnippet": True},
        },
    }
    body_sum = {
        **base,
        "pageSize": 3,
        "contentSearchSpec": {
            "summarySpec": {
                "summaryResultCount": 3,
                "includeCitations": True,
                "ignoreAdversarialQuery": True,
                "ignoreNonSummarySeekingQuery": True,
            },
        },
    }

    yield _emit(
        "log",
        step="api_request",
        level="info",
        tag="API",
        message="Firing two parallel Discovery Engine calls — results + summary",
        detail={
            "method": "POST",
            "url": SEARCH_URL,
            "authorization": f"Bearer {access_token[:24]}… (user token — NOT service account)",
            "query": req.query,
            "acl_user": user_email,
            "fast_call": "no summarySpec — returns file results immediately",
            "sum_call": "summarySpec only — AI generation runs in parallel",
        },
    )

    # ── STEP 5: fire both in parallel ──────────────────────────────────────
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json",
    }

    with concurrent.futures.ThreadPoolExecutor(max_workers=2) as pool:
        fut_fast = pool.submit(requests.post, SEARCH_URL, headers=headers, json=body_fast)
        fut_sum  = pool.submit(requests.post, SEARCH_URL, headers=headers, json=body_sum)

        # Wait for fast results first
        t0 = time.time()
        resp_fast = fut_fast.result()
        fast_ms = round((time.time() - t0) * 1000)

        if resp_fast.status_code != 200:
            yield _emit(
                "log", step="api_error", level="error", tag="API",
                message=f"Discovery Engine (fast) HTTP {resp_fast.status_code} in {fast_ms}ms",
                detail={"status": resp_fast.status_code, "body": resp_fast.text[:500]},
            )
            yield _emit("error", message=resp_fast.text[:200])
            return

        data_fast = resp_fast.json()
        total = data_fast.get("totalSize", 0)

        yield _emit(
            "log", step="api_ok", level="success", tag="API",
            message=f"Fast response 200 OK in {fast_ms}ms — {total} results",
            detail={"status": 200, "elapsed_ms": fast_ms, "total_results": total,
                    "attribution_token": data_fast.get("attributionToken", "")[:32] + "…"},
        )

        # ── ACL note ──────────────────────────────────────────────────────────
        yield _emit(
            "log", step="acl", level="info", tag="ACL",
            message=f"Drive ACL enforced — results scoped to {user_email}",
            detail={
                "acl_mode": "userInfo.userId passthrough",
                "user": user_email,
                "note": "Discovery Engine filters results server-side to files accessible by this user",
            },
        )

        # ── Parse results ──────────────────────────────────────────────────────
        yield _emit(
            "log", step="parse", level="info", tag="PARSE",
            message=f"Parsing {len(data_fast.get('results', []))} result documents…",
        )

        results = []
        for r in data_fast.get("results", []):
            doc = r.get("document", {})
            derived = doc.get("derivedStructData", {})
            struct = doc.get("structData", {})
            title = derived.get("title", struct.get("title", doc.get("id", "Untitled")))
            link = derived.get("link", struct.get("url", ""))
            mime = derived.get("mime_type", "")
            snippet = ""
            ea = derived.get("extractive_answers", [])
            if ea:
                snippet = ea[0].get("content", "")
            if not snippet:
                snips = derived.get("snippets", [])
                if snips:
                    snippet = snips[0].get("snippet", "")
            results.append({
                "title": title,
                "link": link,
                "snippet": snippet,
                "mime_type": mime,
                "icon": _icon(mime),
                "source": "Google Drive",
            })

        yield _emit(
            "log", step="results_ready", level="success", tag="DONE",
            message=f"Streaming {len(results)} results — AI summary still generating…",
            detail={"result_count": len(results)},
        )

        # ── Emit results immediately (summary comes separately) ────────────────
        yield _emit(
            "results",
            data={
                "results": results,
                "total": total,
                "user": {"email": user_email, "name": user_name},
            },
        )

        # ── Wait for summary ───────────────────────────────────────────────────
        t1 = time.time()
        resp_sum = fut_sum.result()
        sum_ms = round((time.time() - t1) * 1000)

        if resp_sum.status_code == 200:
            data_sum = resp_sum.json()
            summary_text = data_sum.get("summary", {}).get("summaryText", "")
            yield _emit(
                "log", step="summary_ok", level="success", tag="API",
                message=f"AI summary received in {sum_ms}ms — {len(summary_text)} chars",
                detail={"elapsed_ms": sum_ms, "summary_chars": len(summary_text)},
            )
            if summary_text:
                yield _emit("summary", data={"summaryText": summary_text})
        else:
            yield _emit(
                "log", step="summary_err", level="warning", tag="API",
                message=f"Summary call HTTP {resp_sum.status_code} — results already shown",
                detail={"status": resp_sum.status_code, "body": resp_sum.text[:200]},
            )


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/api/search")
async def search(req: SearchRequest):
    return StreamingResponse(
        _stream(req),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no",
        },
    )


app.mount("/", StaticFiles(directory="static", html=True), name="static")
