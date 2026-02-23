import requests
import sys

BASE_URL = "http://localhost:8001"
DISPLAY_NAME = "FixedGEInterceptor"
TARGET_ENGINE_ID = "agentspace-testing_1748446185255"

def main():
    print(f"Deploying agent '{DISPLAY_NAME}'...")
    deploy_url = f"{BASE_URL}/api/agents/deploy"
    try:
        resp = requests.post(deploy_url, json={"display_name": DISPLAY_NAME})
        resp.raise_for_status()
        data = resp.json()
        print("Deployment successful!")
        print(f"Resource Name: {data.get('resource_name')}")
        resource_name = data.get("resource_name")
        
        if not resource_name:
            print("Error: No resource_name in response")
            sys.exit(1)
            
        print(f"Registering agent '{resource_name}' with GE engine '{TARGET_ENGINE_ID}'...")
        # Since resource_name contains slashes, we pass it as a path segment. 
        # Requests will URL-encode it if we aren't careful? No, formatted string puts it in path.
        # But if it has slashes, we rely on FastAPI {resource_id:path} to capture it.
        # Does requests client encode slashes? Usually no if in string.
        
        register_url = f"{BASE_URL}/api/agents/{resource_name}/register-ge"
        params = {"target_engine_id": TARGET_ENGINE_ID}
        print(f"Calling: {register_url}") 
        resp = requests.post(register_url, params=params)
        
        try:
            resp.raise_for_status()
            print("Registration successful!")
            print(resp.json())
        except Exception as e:
            print(f"Registration failed: {resp.text}")
            sys.exit(1)

    except Exception as e:
        print(f"Error: {e}")
        if 'resp' in locals():
            print(f"Response: {resp.text}")
        sys.exit(1)

if __name__ == "__main__":
    main()
