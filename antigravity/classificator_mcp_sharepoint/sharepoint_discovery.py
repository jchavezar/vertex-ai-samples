import msal
import requests
import logging
import os
import sys
import time
from dotenv import load_dotenv

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

# 1. AUTHENTICATION (MSAL)
def get_ms_token(tenant_id, client_id, client_secret):
    """
    Acquires a token for the Microsoft Graph API using Client Credentials flow.
    """
    try:
        app = msal.ConfidentialClientApplication(
            client_id, authority=f"https://login.microsoftonline.com/{tenant_id}",
            client_credential=client_secret
        )
        result = app.acquire_token_for_client(scopes=["https://graph.microsoft.com/.default"])
        
        if "access_token" in result:
            return result['access_token']
        else:
            logger.error(f"Error acquiring token: {result.get('error_description')}")
            raise Exception(f"Could not acquire token: {result.get('error')}")
    except Exception as e:
        logger.error(f"Authentication failed: {e}")
        raise

# 2. DISCOVERY & SCOPING
def get_drive_web_url(site_id, drive_id, token):
    """
    Fetches the Web URL of the Drive (Document Library) to scope the search.
    This is required because the Search API uses 'path:"https://..."' for scoping.
    """
    url = f"https://graph.microsoft.com/v1.0/sites/{site_id}/drives/{drive_id}"
    headers = {"Authorization": f"Bearer {token}"}
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        return response.json().get('webUrl')
    except Exception as e:
        logger.error(f"Failed to get Drive URL: {e}")
        raise

# 3. SEARCH API
def search_drive_items(drive_web_url, token, query_text="*"):
    """
    Uses the Microsoft Graph Search API to find items within the specific drive.
    Returns the search hits which contain metadata and the 'hitHighlightedSummary'.
    """
    url = "https://graph.microsoft.com/v1.0/search/query"
    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
    
    # Scoping the search to the specific drive path
    # We use path:"<DRIVE_WEB_URL>" AND <QUERY>
    # Note: We append '*' to match everything if query_text is generic
    full_query = f'path:"{drive_web_url}" {query_text}'
    
    payload = {
        "requests": [
            {
                "entityTypes": ["driveItem"],
                "query": {
                    "queryString": full_query
                },
                # 'region' is REQUIRED for application permissions. 
                # Defaulting to "NAM" (North America) as per API error suggestion.
                "region": "NAM",
                # Request specific fields including the summary (content snippet)
                "fields": [
                    "id", "name", "webUrl", "summary", "lastModifiedDateTime", 
                    "size", "filetype", "title", "createdDateTime", "createdBy",
                    "parentReference"
                ],
                "size": 20  # Limit results per page
            }
        ]
    }
    
    try:
        response = requests.post(url, headers=headers, json=payload)
        response.raise_for_status()
        
        # Parse the nested search response structure
        # Response -> value[0] -> hitsContainers[0] -> hits
        output_hits = []
        result_blocks = response.json().get('value', [])
        if result_blocks:
            hits_containers = result_blocks[0].get('hitsContainers', [])
            if hits_containers:
                output_hits = hits_containers[0].get('hits', [])
                total_results = hits_containers[0].get('total', 0)
                logger.info(f"Search API matched {total_results} items.")
                
        return output_hits
        
    except Exception as e:
        logger.error(f"Search API failed: {e}")
        if 'response' in locals():
            logger.error(f"Response Body: {response.text}")
        raise

# -------------------------------------------------------------------------
# Main Execution
# -------------------------------------------------------------------------
if __name__ == "__main__":
    # Load required env vars
    TENANT_ID = os.getenv("TENANT_ID")
    CLIENT_ID = os.getenv("CLIENT_ID")
    CLIENT_SECRET = os.getenv("CLIENT_SECRET")
    SITE_ID = os.getenv("SITE_ID")
    DRIVE_ID = os.getenv("DRIVE_ID")
    
    if not all([TENANT_ID, CLIENT_ID, CLIENT_SECRET, SITE_ID, DRIVE_ID]):
        logger.error("Missing required environment variables. Please check your .env file.")
        print("\n[ERROR] Missing environment variables.")
        print("Ensure .env contains: TENANT_ID, CLIENT_ID, CLIENT_SECRET, SITE_ID, DRIVE_ID")
        sys.exit(1)
        
    logger.info("Starting SharePoint Search API Test...")
    
    try:
        # 1. Authenticate
        token = get_ms_token(TENANT_ID, CLIENT_ID, CLIENT_SECRET)
        logger.info("Authentication successful.")
        
        # 2. Get Scope (Drive URL)
        logger.info(f"Resolving Web URL for Drive ID: {DRIVE_ID}...")
        drive_url = get_drive_web_url(SITE_ID, DRIVE_ID, token)
        logger.info(f"Targeting Search Scope: {drive_url}")
        
        # 3. Run Search
        logger.info("Executing Search Query via Graph API...")
        results = search_drive_items(drive_url, token)
        
        print(f"\n--- Found {len(results)} Items via Search API ---")
        for res in results:
            resource = res.get('resource', {})
            # 'summary' field contains the indexed text snippet (HitHighlightedSummary)
            summary = res.get('summary', 'N/A')
            name = resource.get('name', 'Unknown')
            web_url = resource.get('webUrl', '#')
            file_type = resource.get('filetype', 'unknown')
            
            print(f"\n[File] {name} ({file_type})")
            print(f"Summary: {summary}")
            print(f"Link: {web_url}")
            print("-" * 40)
            
        print("\nTest Complete!")
        
    except Exception as em:
        logger.error(f"Script failed: {em}")
        sys.exit(1)
