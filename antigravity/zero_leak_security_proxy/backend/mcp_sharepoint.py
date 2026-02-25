
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
        self.site_id = os.getenv("SITE_ID")
        self.drive_id = os.getenv("DRIVE_ID")
        self.region = os.getenv("MS_GRAPH_REGION", "NAM")
        if token:
            logger.info("Using provided user-delegated token.")
            self.token = token
        else:
            logger.error("No user token provided. Delegated authentication required.")
            raise Exception("No user token provided. The application requires authorized requests from the frontend.")

    def get_drive_web_url(self):
        try:
            import base64, json
            parts = self.token.split('.')
            if len(parts) >= 2:
                payload = parts[1]
                payload += '=' * (-len(payload) % 4)
                decoded = json.loads(base64.urlsafe_b64decode(payload))
                logger.info(f"Token scopes: {decoded.get('scp')}")
                logger.info(f"Token audience: {decoded.get('aud')}")
                logger.info(f"Token expiration: {decoded.get('exp')}")
        except Exception as e:
            logger.info(f"Could not decode token: {e}")
            
        url = f"https://graph.microsoft.com/v1.0/sites/{self.site_id}/drives/{self.drive_id}"
        res = requests.get(url, headers={"Authorization": f"Bearer {self.token}"})
        if not res.ok:
            logger.error(f"get_drive_web_url HTTP Error {res.status_code}: {res.text}")
            res.raise_for_status()
        return res.json().get('webUrl')

    def search_documents(self, query: str = "*", limit: int = 5):

        drive_web_url = None
        try:
            drive_web_url = self.get_drive_web_url()
        except Exception as e:
            logger.error(f"Failed to get drive web url, continuing without path constraint: {e}")

        url = "https://graph.microsoft.com/v1.0/search/query"
        headers = {
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json"
        }
        
        query_string = query
        if drive_web_url:
            query_string = f'{query} path:"{drive_web_url}"'
            
        payload = {
            "requests": [
                {
                    "entityTypes": ["driveItem"],
                    "query": {
                        "queryString": query_string
                    },
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
            logger.info(f"Search results returned: {len(results)}")
            if results:
                for r in results:
                    logger.info(f"- {r.get('name')}")
            return results
        except requests.exceptions.RequestException as e:
            error_text = response.text if 'response' in locals() and hasattr(response, 'text') else str(e)
            logger.error(f"Failed to search items: {error_text}")
            raise Exception(f"Failed to search SharePoint: {error_text}")

    def get_document_content(self, item_id: str):

        url = f"https://graph.microsoft.com/v1.0/sites/{self.site_id}/drives/{self.drive_id}/items/{item_id}?$expand=listItem"
        headers = {"Authorization": f"Bearer {self.token}"}
        try:
            response = requests.get(url, headers=headers)
            if response.status_code == 429:
                return "Throttled by SharePoint, please retry."
            if not response.ok:
                logger.error(f"get_document_content HTTP Error {response.status_code}: {response.text}")
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
