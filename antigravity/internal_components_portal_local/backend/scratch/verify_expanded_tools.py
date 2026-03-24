import os
import sys
import json
import logging
from dotenv import load_dotenv

sys.path.append(os.path.abspath("."))

# Load local environment
load_dotenv("../.env")

# Preload placeholder token to satisfy auth structure fallback logic if testing isolated tools.
if not os.environ.get("USER_ID_TOKEN") and not os.environ.get("USER_TOKEN"):
    os.environ["USER_ID_TOKEN"] = "isolated_test_node"

from servicenow_mcp.mcp_server_servicenow import search_service_requests, search_catalog_items

# Configure basic logging to match script
logging.basicConfig(level=logging.INFO)

def test_expanded_tools():
    print("\n--- 🔍 Testing search_catalog_items('Laptop') ---")
    try:
        res_cat = search_catalog_items("Laptop", limit=2)
        print(res_cat)
    except Exception as e:
        print(f"Error test_catalog: {e}")

    print("\n--- 🔍 Testing search_service_requests('monitor') ---")
    try:
        res_req = search_service_requests("monitor", limit=2)
        print(res_req)
    except Exception as e:
        print(f"Error test_req: {e}")

if __name__ == "__main__":
    test_expanded_tools()
