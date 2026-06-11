import requests
import subprocess

def get_token():
    try:
        # Get identity token from gcloud
        result = subprocess.run(
            ["gcloud", "auth", "print-identity-token"],
            capture_output=True, text=True, check=True
        )
        return result.stdout.strip()
    except Exception as e:
        print(f"Failed to get token via gcloud: {e}")
        return None

urls = [
    "https://ge-custom-sharepoint-mcp-rxhrarbbrq-uc.a.run.app",
    "https://ge-custom-sharepoint-mcp-254356041555.us-central1.run.app"
]

token = get_token()
if not token:
    print("Cannot proceed without token.")
    exit(1)

headers = {"Authorization": f"Bearer {token}"}
print("Token obtained.")

for base_url in urls:
    print(f"\nTesting Base URL: {base_url}")
    for path in ["/sse", "/mcp", "/"]:
        url = base_url + path
        print(f"Trying {url} ...")
        try:
            # Try GET first
            resp = requests.get(url, headers=headers, timeout=5)
            print(f"GET Status: {resp.status_code}")
            print(f"GET Content: {resp.text[:100]}")
            
            # If 405, try POST for /mcp
            if resp.status_code == 405 or path == "/mcp":
                print(f"Trying POST to {url} ...")
                resp = requests.post(url, headers=headers, json={"method": "initialize", "params": {}}, timeout=5)
                print(f"POST Status: {resp.status_code}")
                print(f"POST Content: {resp.text[:100]}")
        except Exception as e:
            print(f"Failed: {e}")
