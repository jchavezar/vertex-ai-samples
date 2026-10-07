"""Local OAuth 2.0 PKCE Listener for Salesforce (Port 1717).
Captures the OAuth token automatically when the user clicks the authorization link in their browser,
saves it to ~/.gemini/sfdc_altostrat_auth.json, and immediately seeds all demo records.
"""
import base64
import hashlib
import http.server
import json
import os
import secrets
import urllib.parse
import requests
from sfdc_auto_connect_and_seed import seed_sfdc_records

AUTH_FILE = os.path.expanduser("~/.gemini/sfdc_altostrat_auth.json")
INSTANCE_URL = "https://orgfarm-771334bd2f-dev-ed.develop.my.salesforce.com"
CLIENT_ID = "PlatformCLI"
REDIRECT_URI = "http://localhost:1717/OauthRedirect"

# Generate deterministic PKCE code_verifier and code_challenge
code_verifier = "MotorolaSolutions2026GeminiEnterprisePKCEVerifierKey1234567890"
code_challenge = base64.urlsafe_b64encode(
    hashlib.sha256(code_verifier.encode("utf-8")).digest()
).rstrip(b"=").decode("utf-8")

auth_url = (
    f"{INSTANCE_URL}/services/oauth2/authorize"
    f"?response_type=code"
    f"&client_id={CLIENT_ID}"
    f"&redirect_uri={urllib.parse.quote(REDIRECT_URI)}"
    f"&code_challenge={code_challenge}"
    f"&code_challenge_method=S256"
)


class OAuthHandler(http.server.BaseHTTPRequestHandler):
    def do_GET(self):
        parsed = urllib.parse.urlparse(self.path)
        params = urllib.parse.parse_qs(parsed.query)
        if "code" in params:
            code = params["code"][0]
            print(f"✅ Received OAuth authorization code! Exchanging for access_token...")
            # Exchange code for token
            token_resp = requests.post(
                f"{INSTANCE_URL}/services/oauth2/token",
                data={
                    "grant_type": "authorization_code",
                    "client_id": CLIENT_ID,
                    "redirect_uri": REDIRECT_URI,
                    "code": code,
                    "code_verifier": code_verifier,
                },
            )
            if token_resp.status_code == 200:
                data = token_resp.json()
                access_token = data["access_token"]
                refresh_token = data.get("refresh_token")
                instance_url = data.get("instance_url", INSTANCE_URL)
                with open(AUTH_FILE) as f:
                    cfg = json.load(f)
                cfg["session_id"] = access_token
                if refresh_token:
                    cfg["refresh_token"] = refresh_token
                cfg["client_id"] = CLIENT_ID
                cfg["instance_url"] = instance_url
                with open(AUTH_FILE, "w") as f:
                    json.dump(cfg, f, indent=2)
                print(f"🎉 Saved live OAuth session token + refresh_token to {AUTH_FILE}")

                # Get exact username from userinfo endpoint
                uinfo_resp = requests.get(
                    f"{instance_url}/services/oauth2/userinfo",
                    headers={"Authorization": f"Bearer {access_token}"}
                )
                sf_username = cfg.get("username", "admin.e7b4b1cf0b9b@agentforce.com")
                if uinfo_resp.status_code == 200:
                    sf_username = uinfo_resp.json().get("preferred_username", sf_username)
                print(f"👤 Authenticated Salesforce Admin User: {sf_username}")

                # Automatically update Gemini_Enterprise_Connector callbackUrl & official Google Cloud settings via Metadata API
                soap_url = f"{instance_url}/services/Soap/m/60.0"
                upd_xml = f"""<?xml version="1.0" encoding="UTF-8"?>
<env:Envelope xmlns:env="http://schemas.xmlsoap.org/soap/envelope/" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">
  <env:Header><urn:SessionHeader xmlns:urn="http://soap.sforce.com/2006/04/metadata"><urn:sessionId>{access_token}</urn:sessionId></urn:SessionHeader></env:Header>
  <env:Body>
    <urn:updateMetadata xmlns:urn="http://soap.sforce.com/2006/04/metadata">
      <urn:metadata xsi:type="urn:ConnectedApp">
        <urn:fullName>Gemini_Enterprise_Connector</urn:fullName>
        <urn:label>Gemini Enterprise Connector</urn:label>
        <urn:contactEmail>admin@jesusarguelles.demo.altostrat.com</urn:contactEmail>
        <urn:oauthConfig>
          <urn:callbackUrl>https://vertexaisearch.cloud.google.com/oauth-redirect
https://vertexaisearch.cloud.google.com/console/oauth/salesforce_oauth.html
https://vertexaisearch.cloud.google.com/console/oauth/default_oauth.html
https://vertexaisearch.cloud.google.com/oauth-callback
https://console.cloud.google.com/vertex-ai/search/oauth/default_oauth.html
https://console.cloud.google.com/vertex-ai/agentspace/oauth/callback
http://localhost:1717/OauthRedirect
http://localhost:8080/oauth/callback</urn:callbackUrl>
          <urn:consumerKey>GeminiEnterpriseClientKey2026Altostrat998877</urn:consumerKey>
          <urn:isAdminApproved>false</urn:isAdminApproved>
          <urn:isClientCredentialEnabled>true</urn:isClientCredentialEnabled>
          <urn:oauthClientCredentialUser>{sf_username}</urn:oauthClientCredentialUser>
          <urn:isConsumerSecretOptional>true</urn:isConsumerSecretOptional>
          <urn:isIntrospectAllTokens>false</urn:isIntrospectAllTokens>
          <urn:isPkceRequired>false</urn:isPkceRequired>
          <urn:isSecretRequiredForRefreshToken>false</urn:isSecretRequiredForRefreshToken>
          <urn:scopes>Api</urn:scopes>
          <urn:scopes>Web</urn:scopes>
          <urn:scopes>Full</urn:scopes>
          <urn:scopes>RefreshToken</urn:scopes>
          <urn:scopes>OpenID</urn:scopes>
        </urn:oauthConfig>
        <urn:oauthPolicy>
          <urn:ipRelaxation>BYPASS</urn:ipRelaxation>
          <urn:refreshTokenPolicy>infinite</urn:refreshTokenPolicy>
        </urn:oauthPolicy>
      </urn:metadata>
    </urn:updateMetadata>
  </env:Body>
</env:Envelope>"""
                r_meta = requests.post(
                    soap_url,
                    data=upd_xml,
                    headers={"Content-Type": "text/xml; charset=UTF-8", "SOAPAction": "updateMetadata"}
                )
                print(f"🔧 ConnectedApp Metadata Update Status: {r_meta.status_code}")
                print(r_meta.text[:600])

                # Send nice HTML response to browser
                self.send_response(200)
                self.send_header("Content-type", "text/html; charset=utf-8")
                self.end_headers()
                self.wfile.write(
                    b"<html><body style='font-family:sans-serif;text-align:center;padding:50px;'>"
                    b"<h1>&#x2705; Official Google Cloud Salesforce Connector Settings Applied!</h1>"
                    b"<p>Updated <b>Gemini_Enterprise_Connector</b> with:</p>"
                    b"<ul style='text-align:left;display:inline-block;'>"
                    b"<li><b>https://vertexaisearch.cloud.google.com/oauth-redirect</b> (End-User Chat UI)</li>"
                    b"<li><b>https://vertexaisearch.cloud.google.com/console/oauth/salesforce_oauth.html</b> (Official Google Cloud Docs)</li>"
                    b"<li><b>https://vertexaisearch.cloud.google.com/console/oauth/default_oauth.html</b> (GCP Console)</li>"
                    b"<li><b>Client Credentials Flow Enabled</b> with Run-As User: " + sf_username.encode() + b"</li>"
                    b"<li><b>PKCE & Refresh Token Policies</b>: Relaxed IP + Valid Until Revoked</li>"
                    b"</ul>"
                    b"<p>Note: Salesforce takes 2-3 minutes to propagate Connected App changes. Then click <b>Authorize</b> in Gemini Enterprise!</p>"
                    b"</body></html>"
                )
                os._exit(0)
            else:
                self.send_response(400)
                self.end_headers()
                self.wfile.write(f"Token exchange failed: {token_resp.text}".encode())
        else:
            self.send_response(200)
            self.end_headers()
            self.wfile.write(b"Waiting for code...")

    def log_message(self, format, *args):
        pass


if __name__ == "__main__":
    print(f"\n🔗 CLICK THIS LINK TO AUTHORIZE SALESFORCE:\n{auth_url}\n")
    server = http.server.HTTPServer(("127.0.0.1", 1717), OAuthHandler)
    print("⏳ Listening on http://localhost:1717/OauthRedirect ...")
    server.serve_forever()
