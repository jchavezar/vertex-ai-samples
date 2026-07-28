import os
import requests
from dotenv import load_dotenv

# Load credentials from backend/.env
dotenv_path = os.path.join(os.path.dirname(__file__), "..", "backend", ".env")
if os.path.exists(dotenv_path):
    load_dotenv(dotenv_path, override=True)
else:
    print(f"[warning] Backend .env not found at {dotenv_path}")

def test_config():
    """Verify that all required environment variables are set."""
    required = [
        "PROJECT_NUMBER",
        "ENGINE_ID",
        "CONNECTOR_ID",
        "WIF_POOL_ID",
        "WIF_PROVIDER_ID",
        "CONNECTOR_CLIENT_ID",
        "TENANT_ID"
    ]
    
    missing = []
    print("\n=== Checking Environment Variables ===")
    for var in required:
        val = os.environ.get(var)
        if not val:
            missing.append(var)
            print(f"❌ {var}: MISSING")
        else:
            # Mask sensitive values
            masked = val[:4] + "..." + val[-4:] if len(val) > 8 else "..."
            print(f"✅ {var}: {masked}")
            
    if missing:
        print(f"\n⚠️ Missing {len(missing)} environment variables: {', '.join(missing)}")
    else:
        print("\n🎉 All required environment variables are set!")

if __name__ == "__main__":
    test_config()
