"""
One-shot SharePoint OAuth authorization via Playwright.

Opens a real browser window → Microsoft auth → intercepts the auth code
BEFORE Google's redirect page loads → stores via acquireAndStoreRefreshToken.

Usage:
    uv run python auth_sharepoint.py          # uses WIF (needs Entra JWT)
    uv run python auth_sharepoint.py --adc     # uses ADC (gcloud creds)
"""
import os
import sys
import json
import base64
import requests
from urllib.parse import urlencode, urlparse, parse_qs
from dotenv import load_dotenv

load_dotenv()

PROJECT_NUMBER = os.environ["PROJECT_NUMBER"]
CONNECTOR_ID = os.environ["CONNECTOR_ID"]
CONNECTOR_CLIENT_ID = os.environ["CONNECTOR_CLIENT_ID"]
TENANT_ID = os.environ["TENANT_ID"]
WIF_POOL_ID = os.environ["WIF_POOL_ID"]
WIF_PROVIDER_ID = os.environ["WIF_PROVIDER_ID"]
ENGINE_ID = os.environ["ENGINE_ID"]
DATA_STORE_ID = os.environ["DATA_STORE_ID"]
GOOGLE_REDIRECT_URI = "https://vertexaisearch.cloud.google.com/oauth-redirect"
CONNECTOR_URL = f"https://discoveryengine.googleapis.com/v1alpha/projects/{PROJECT_NUMBER}/locations/global/collections/{CONNECTOR_ID}"
BASE_URL = f"https://discoveryengine.googleapis.com/v1alpha/projects/{PROJECT_NUMBER}/locations/global/collections/default_collection/engines/{ENGINE_ID}"


def build_auth_url():
    """Build Microsoft OAuth URL with Google's redirect URI."""
    state = base64.b64encode(json.dumps({
        "origin": "https://console.cloud.google.com",
        "useBroadcastChannel": "false",
    }).encode()).decode()

    params = {
        "client_id": CONNECTOR_CLIENT_ID,
        "response_type": "code",
        "redirect_uri": GOOGLE_REDIRECT_URI,
        "scope": "openid offline_access Sites.Read.All Files.Read.All",
        "response_mode": "query",
        "state": state,
        "prompt": "consent",
    }
    return f"https://login.microsoftonline.com/{TENANT_ID}/oauth2/v2.0/authorize?{urlencode(params)}"


def capture_code():
    """Open browser, let user authenticate, intercept auth code before Google's page loads."""
    from playwright.sync_api import sync_playwright

    import time
    auth_url = build_auth_url()
    captured_url = None

    username = os.environ.get("SP_USERNAME", "")
    password = os.environ.get("SP_PASSWORD", "")

    print("[1] Opening browser for Microsoft authentication...")
    print("    You only need to complete MFA (Authenticator app) in the browser.")
    print()

    with sync_playwright() as p:
        browser = p.chromium.launch(
            headless=False,
            args=["--no-sandbox", "--disable-dev-shm-usage"],
        )
        context = browser.new_context()
        page = context.new_page()

        # Log all navigations for debugging
        page.on("framenavigated", lambda frame: print(f"    [nav] {frame.url[:120]}") if frame == page.main_frame else None)

        page.goto(auth_url, wait_until="domcontentloaded", timeout=60000)
        time.sleep(2)

        # Auto-fill email
        try:
            email_input = page.wait_for_selector('input[name="loginfmt"]', timeout=5000)
            email_input.fill(username)
            page.click('#idSIButton9')
            time.sleep(3)
            print("[2] Username entered automatically")
        except Exception:
            print("[2] Email field not found — may need manual entry")

        # Auto-fill password
        try:
            pwd_input = page.wait_for_selector('input[name="passwd"]', timeout=5000)
            pwd_input.fill(password)
            page.click('#idSIButton9')
            time.sleep(3)
            print("[3] Password entered automatically")
        except Exception:
            print("[3] Password field not found — may need manual entry")

        # Auto-click consent "Accept" button if it appears
        try:
            accept_btn = page.wait_for_selector('#idSIButton9', timeout=5000)
            # Check if this is the consent page (has "Permissions requested" text)
            if page.query_selector('text="Permissions requested"') or page.query_selector('text="Accept"'):
                accept_btn.click()
                time.sleep(3)
                print("[4] Consent accepted automatically")
        except Exception:
            pass

        # Handle "Stay signed in?" prompt
        try:
            stay_btn = page.wait_for_selector('#idSIButton9', timeout=3000)
            if page.query_selector('text="Stay signed in"') or page.query_selector('#KmsiBanner'):
                stay_btn.click()
                time.sleep(2)
                print("[4b] 'Stay signed in' accepted")
        except Exception:
            pass

        print("[5] Waiting for redirect to Google's page (up to 3 minutes)...")

        # Wait for redirect to Google's page
        try:
            page.wait_for_url(f"{GOOGLE_REDIRECT_URI}*", timeout=180000)
            captured_url = page.url
            print(f"[6] Captured redirect URL (length={len(captured_url)})")
        except Exception as e:
            current_url = page.url
            if "code=" in current_url:
                captured_url = current_url
                print(f"[6] Captured code from current URL")
            else:
                print(f"[!] Timeout — no code captured")
                print(f"    Final URL: {current_url[:120]}")
                print(f"    Error: {e}")

        browser.close()

    return captured_url


def store_token_adc(full_redirect_uri: str):
    """Store refresh token using Application Default Credentials."""
    import google.auth
    import google.auth.transport.requests as gauth_requests

    credentials, _ = google.auth.default(
        scopes=["https://www.googleapis.com/auth/cloud-platform"]
    )
    credentials.refresh(gauth_requests.Request())

    url = f"{CONNECTOR_URL}/dataConnector:acquireAndStoreRefreshToken"
    resp = requests.post(
        url,
        headers={
            "Authorization": f"Bearer {credentials.token}",
            "Content-Type": "application/json",
            "X-Goog-User-Project": PROJECT_NUMBER,
        },
        json={"fullRedirectUri": full_redirect_uri},
        timeout=30,
    )

    print(f"[Store-ADC] Status: {resp.status_code}")
    print(f"[Store-ADC] Response: {resp.text[:500]}")
    return resp.ok


def store_token_wif(full_redirect_uri: str, entra_jwt: str):
    """Store refresh token using WIF (Entra JWT → GCP token)."""
    sts_resp = requests.post("https://sts.googleapis.com/v1/token", json={
        "audience": f"//iam.googleapis.com/locations/global/workforcePools/{WIF_POOL_ID}/providers/{WIF_PROVIDER_ID}",
        "grantType": "urn:ietf:params:oauth:grant-type:token-exchange",
        "requestedTokenType": "urn:ietf:params:oauth:token-type:access_token",
        "scope": "https://www.googleapis.com/auth/cloud-platform",
        "subjectToken": entra_jwt,
        "subjectTokenType": "urn:ietf:params:oauth:token-type:jwt"
    }, timeout=10)

    if not sts_resp.ok:
        print(f"[STS] Exchange failed: {sts_resp.text[:200]}")
        return False

    gcp_token = sts_resp.json().get("access_token")
    print(f"[STS] Exchange OK, token length={len(gcp_token)}")

    url = f"{CONNECTOR_URL}/dataConnector:acquireAndStoreRefreshToken"
    resp = requests.post(
        url,
        headers={
            "Authorization": f"Bearer {gcp_token}",
            "Content-Type": "application/json",
            "X-Goog-User-Project": PROJECT_NUMBER,
        },
        json={"fullRedirectUri": full_redirect_uri},
        timeout=30,
    )

    print(f"[Store-WIF] Status: {resp.status_code}")
    print(f"[Store-WIF] Response: {resp.text[:500]}")
    return resp.ok


def test_streamassist(gcp_token: str):
    """Quick StreamAssist test to verify SharePoint access."""
    ds = f"projects/{PROJECT_NUMBER}/locations/global/collections/default_collection/dataStores/{DATA_STORE_ID}"
    payload = {
        "query": {"text": "Who is the CFO?"},
        "toolsSpec": {
            "vertexAiSearchSpec": {
                "dataStoreSpecs": [{"dataStore": ds}]
            }
        },
    }

    print(f"\n[Test] Querying StreamAssist...")
    resp = requests.post(
        f"{BASE_URL}/assistants/default_assistant:streamAssist",
        headers={"Authorization": f"Bearer {gcp_token}", "Content-Type": "application/json"},
        json=payload,
        timeout=90,
    )

    if not resp.ok:
        print(f"[Test] FAILED: {resp.status_code} - {resp.text[:200]}")
        return

    data = resp.json()
    for chunk in data:
        for reply in chunk.get("answer", {}).get("replies", []):
            content = reply.get("groundedContent", {}).get("content", {})
            text = content.get("text", "")
            thought = content.get("thought", False)
            if text and not thought:
                print(f"[Test] ANSWER: {text[:300]}")
            elif text and thought:
                print(f"[Test] thought: {text[:80]}")
        for reply in chunk.get("answer", {}).get("replies", []):
            gc = reply.get("groundedContent", {})
            refs = gc.get("textGroundingMetadata", {}).get("references", [])
            for ref in refs:
                doc = ref.get("documentMetadata", {})
                print(f"[Test] SOURCE: {doc.get('title', '')} — {doc.get('uri', '')[:80]}")


def main():
    use_adc = "--adc" in sys.argv

    captured_url = capture_code()
    if not captured_url or "code=" not in captured_url:
        print("\n[FAIL] Could not capture auth code.")
        sys.exit(1)

    print(f"\n[6] Storing refresh token via {'ADC' if use_adc else 'WIF'}...")

    if use_adc:
        ok = store_token_adc(captured_url)
        gcp_token = None
    else:
        jwt_path = "/tmp/entra_token.txt"
        try:
            entra_jwt = open(jwt_path).read().strip()
        except FileNotFoundError:
            print(f"[!] No Entra JWT at {jwt_path}. Use --adc flag or login to the portal first.")
            sys.exit(1)
        ok = store_token_wif(captured_url, entra_jwt)

        # Get the WIF token for testing
        if ok:
            sts_resp = requests.post("https://sts.googleapis.com/v1/token", json={
                "audience": f"//iam.googleapis.com/locations/global/workforcePools/{WIF_POOL_ID}/providers/{WIF_PROVIDER_ID}",
                "grantType": "urn:ietf:params:oauth:grant-type:token-exchange",
                "requestedTokenType": "urn:ietf:params:oauth:token-type:access_token",
                "scope": "https://www.googleapis.com/auth/cloud-platform",
                "subjectToken": entra_jwt,
                "subjectTokenType": "urn:ietf:params:oauth:token-type:jwt"
            }, timeout=10)
            gcp_token = sts_resp.json().get("access_token") if sts_resp.ok else None

    if ok:
        print("\n[SUCCESS] SharePoint refresh token stored!")
        if gcp_token:
            test_streamassist(gcp_token)
        else:
            print("[!] No WIF token available for StreamAssist test (ADC mode).")
    else:
        print("\n[FAIL] Could not store token. Check errors above.")
        sys.exit(1)


if __name__ == "__main__":
    main()
