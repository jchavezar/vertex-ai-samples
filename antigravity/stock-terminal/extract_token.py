import os
import requests
import base64
from urllib.parse import urlparse, parse_qs
from dotenv import load_dotenv

# Load credentials from .env
load_dotenv('backend/.env')

CLIENT_ID = os.getenv("FS_CLIENT_ID")
CLIENT_SECRET = os.getenv("FS_CLIENT_SECRET")
REDIRECT_URI = os.getenv("FS_REDIRECT_URI")
AUTH_URL = "https://auth.factset.com/as/authorization.oauth2"
TOKEN_URL = "https://auth.factset.com/as/token.oauth2"

def get_refresh_token():
    print("\n=== FactSet Refresh Token Extractor ===\n")
    
    if not all([CLIENT_ID, CLIENT_SECRET, REDIRECT_URI]):
        print("Error: Missing credentials in backend/.env")
        return

    # 1. Generate Auth URL
    params = {
        "response_type": "code",
        "client_id": CLIENT_ID,
        "redirect_uri": REDIRECT_URI,
        "scope": "mcp",
        "access_type": "offline",
        "prompt": "consent",
        "state": "manual_token_extract"
    }
    
    auth_url = requests.Request('GET', AUTH_URL, params=params).prepare().url
    
    print("1. Open this URL in your browser and log in:")
    print(f"\n{auth_url}\n")
    
    print("2. After clicking 'ALLOW', you will be redirected.")
    print("3. Copy the ENTIRE URL of the page you are on (it should contain 'code=...')")
    
    redirected_url = input("\nPaste the full redirected URL here: ").strip()
    
    # 2. Extract Code
    try:
        parsed = urlparse(redirected_url)
        code = parse_qs(parsed.query).get('code', [None])[0]
        
        if not code:
            # Check fragment if not in query
            fragment = parse_qs(parsed.fragment)
            code = fragment.get('code', [None])[0]

        if not code:
            print("Error: Could not find 'code' parameter in the URL.")
            return

        # 3. Exchange for Refresh Token
        auth_str = f"{CLIENT_ID}:{CLIENT_SECRET}"
        b64_auth = base64.b64encode(auth_str.encode()).decode()
        
        headers = {
            "Authorization": f"Basic {b64_auth}",
            "Content-Type": "application/x-www-form-urlencoded"
        }
        
        payload = {
            "grant_type": "authorization_code",
            "code": code,
            "redirect_uri": REDIRECT_URI
        }
        
        print("\nExchanging code for tokens...")
        response = requests.post(TOKEN_URL, data=payload, headers=headers)
        
        if response.status_code == 200:
            data = response.json()
            refresh_token = data.get("refresh_token")
            access_token = data.get("access_token")
            
            if refresh_token:
                print("\nSUCCESS! Your Refresh Token is:\n")
                print("-" * 50)
                print(refresh_token)
                print("-" * 50)
                print("\nCopy this token and paste it into the 'Advanced' field in the Sidebar UI.")
            else:
                print("\nConnection successful, but NO Refresh Token was returned.")
                print("Your account might not have 'offline_access' permissions enabled by your admin.")
                print(f"Access Token: {access_token[:50]}...")
        else:
            print(f"\nError from FactSet: {response.status_code}")
            print(response.text)

    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    get_refresh_token()
