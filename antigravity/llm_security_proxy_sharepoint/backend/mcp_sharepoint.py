import msal
import requests
import time
import logging
import os
from markitdown import MarkItDown
from dotenv import load_dotenv

load_dotenv(dotenv_path="../.env")

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class SharePointMCP:
    def __init__(self, token=None):
        self.tenant_id = os.getenv("TENANT_ID")
        self.client_id = os.getenv("CLIENT_ID")
        self.client_secret = os.getenv("CLIENT_SECRET")
        self.site_id = os.getenv("SITE_ID")
        self.drive_id = os.getenv("DRIVE_ID")
        self.region = os.getenv("MS_GRAPH_REGION", "NAM")
        if token:
            logger.info("Using provided user-delegated token.")
            self.token = token
        else:
            logger.info("No token provided. Falling back to Application Credentials.")
            self.token = self._get_ms_token()

    def _get_ms_token(self):
        if not all([self.tenant_id, self.client_id, self.client_secret]):
            logger.error("Missing AD credentials")
            raise Exception("Missing AD Credentials in environment")
        try:
            app = msal.ConfidentialClientApplication(
                self.client_id, authority=f"https://login.microsoftonline.com/{self.tenant_id}",
                client_credential=self.client_secret
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

    def get_drive_web_url(self):
        url = f"https://graph.microsoft.com/v1.0/sites/{self.site_id}/drives/{self.drive_id}"
        res = requests.get(url, headers={"Authorization": f"Bearer {self.token}"})
        res.raise_for_status()
        return res.json().get('webUrl')

    def search_documents(self, query: str = "*", limit: int = 5):
        try:
            drive_web_url = self.get_drive_web_url()
        except Exception as e:
            logger.error(f"Failed to get drive web url: {e}")
            return f"Failed to get drive URL: {e}"

        url = "https://graph.microsoft.com/v1.0/search/query"
        headers = {
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json",
            "Region": self.region
        }
        payload = {
            "requests": [{
                "entityTypes": ["driveItem"],
                "query": { "queryString": f'path:"{drive_web_url}" {query}' },
                "region": self.region,
                "fields": ["id", "name", "webUrl", "summary", "filetype", "listId", "siteId"],
                "size": limit
            }]
        }
        logger.info(f"Querying graph api: {query}")
        try:
            response = requests.post(url, headers=headers, json=payload)
            response.raise_for_status()
            res_json = response.json()
            hits = []
            for container in res_json.get('value', [{}])[0].get('hitsContainers', []):
                hits.extend(container.get('hits', []))
            
            results = []
            for h in hits:
                r = h.get('resource', {})
                results.append({
                    "id": r.get('id'),
                    "name": r.get('name'),
                    "webUrl": r.get('webUrl'),
                    "summary": r.get('summary'),
                    "filetype": r.get('filetype')
                })
            return results
        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to search items: {e}")
            return f"Failed to search: {e}"

    def get_document_content(self, item_id: str):
        url = f"https://graph.microsoft.com/v1.0/sites/{self.site_id}/drives/{self.drive_id}/items/{item_id}?$expand=listItem"
        headers = {"Authorization": f"Bearer {self.token}"}
        try:
            response = requests.get(url, headers=headers)
            if response.status_code == 429:
                return "Throttled by SharePoint, please retry."
            response.raise_for_status()
            data = response.json()

            download_url = data.get('@microsoft.graph.downloadUrl')
            if not download_url:
                return "No download URL available for this document."

            # Download it
            resp = requests.get(download_url, headers=headers, stream=True)
            resp.raise_for_status()
            temp_filename = f"temp_{item_id}_{int(time.time())}.bin"
            with open(temp_filename, 'wb') as f:
                for chunk in resp.iter_content(chunk_size=8192):
                    f.write(chunk)
            
            md = MarkItDown()
            result = md.convert(temp_filename)
            text_content = result.text_content
            os.remove(temp_filename)
            
            if len(text_content) > 15000:
                logger.info(f"Truncating document content from {len(text_content)} to 15000 characters.")
                text_content = text_content[:15000] + "\n\n...[Content Truncated due to length]..."
            
            return text_content
            
        except Exception as e:
            logger.error(f"Failed to fetch file content: {e}")
            return f"Failed to fetch content: {e}"

if __name__ == "__main__":
    import sys
    if "--test" in sys.argv:
        print("Initializing SharePoint MCP...")
        mcp = SharePointMCP()
        if mcp.token:
            print("Successfully acquired MS Graph token!")
        else:
            print("Failed to acquire token.")
            sys.exit(1)
            
        print("Testing document search with query '*'...")
        results = mcp.search_documents("*", limit=2)
        print(f"Results: {results}")
