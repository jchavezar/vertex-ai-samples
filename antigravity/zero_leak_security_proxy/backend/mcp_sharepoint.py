
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
    _drive_web_url_cache = {}

    def __init__(self, token=None):
        self.site_id = os.getenv("SITE_ID")
        self.drive_id = os.getenv("DRIVE_ID")
        self.region = os.getenv("MS_GRAPH_REGION", "NAM")
        
        # Configure Vision-ready MarkItDown
        def describe_image(image_data, **kwargs):
            try:
                from google import genai
                from google.genai import types
                
                # Using Vertex AI for enterprise-grade security and scale
                client = genai.Client(vertexai=True, location='us-central1')
                
                # Optimized for speed using Flash variants
                model_id = 'gemini-2.5-flash' 
                
                logger.info(f"Triggering Neural Vision turn for embedded image using {model_id}...")
                response = client.models.generate_content(
                    model=model_id,
                    contents=[
                        "Analyze this image from an enterprise document. Describe any charts, tables, or key visual information. Be concise and maintain a professional tone suitable for markdown integration.",
                        types.Part.from_bytes(data=image_data, mime_type="image/png")
                    ]
                )
                return f"\n\n> [NEURAL VISION BLOCK: {response.text.strip()}]\n\n"
            except Exception as e:
                logger.warning(f"Vision description failed: {str(e)}")
                return "\n[VISION ERROR: Image could not be processed]\n"

        self._md = MarkItDown(image_description_callback=describe_image)
        
        if token:
            logger.info("Using provided user-delegated token.")
            self.token = token
        else:
            logger.error("No user token provided. Delegated authentication required.")
            raise Exception("No user token provided. The application requires authorized requests from the frontend.")

    def get_drive_web_url(self):
        cache_key = f"{self.site_id}_{self.drive_id}"
        if cache_key in SharePointMCP._drive_web_url_cache:
            return SharePointMCP._drive_web_url_cache[cache_key]

        url = f"https://graph.microsoft.com/v1.0/sites/{self.site_id}/drives/{self.drive_id}"
        res = requests.get(url, headers={"Authorization": f"Bearer {self.token}"})
        if not res.ok:
            logger.error(f"get_drive_web_url HTTP Error {res.status_code}: {res.text}")
            res.raise_for_status()
        
        web_url = res.json().get('webUrl')
        SharePointMCP._drive_web_url_cache[cache_key] = web_url
        return web_url

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
        
    def search_documents(self, query: str = "*", limit: int = 5):
        drive_web_url = None
        try:
            drive_web_url = self.get_drive_web_url()
        except Exception as e:
            logger.error(f"Failed to get drive web url: {e}")

        url = "https://graph.microsoft.com/v1.0/search/query"
        headers = {
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json"
        }
        
        # --- PHASE: QUERY EXPANSION (FAN-OUT) ---
        # We generate 3 different 'angles' to ensure we hit the index correctly
        search_queries = []
        
        # 1. Exact Match (Precision Angle)
        if drive_web_url:
            search_queries.append(f'{query} path:"{drive_web_url}"')
        else:
            search_queries.append(query)
            
        # 2. Broad Keyword Mix (Recall Angle)
        # We take the words and 'OR' them if it's a long query, or just use words
        words = [w for w in query.split() if len(w) > 2] # Skip small stop words
        if len(words) > 1:
            broad_q = " OR ".join(words[:4]) # Grab top 4 keywords
            if drive_web_url:
                search_queries.append(f'({broad_q}) path:"{drive_web_url}"')
            else:
                search_queries.append(broad_q)
        
        # 3. Path Discovery (Structural Angle)
        # Just look for the first word in the folder structure
        if len(words) > 0 and drive_web_url:
            search_queries.append(f'{words[0]}* path:"{drive_web_url.rstrip("/")}/*"')

        # --- PHASE: PARALLEL EXECUTION ---
        from concurrent.futures import ThreadPoolExecutor
        
        all_hits = {} # Use dict keyed by ID for deduplication
        
        def run_one_search(q_str):
            logger.info(f"Fan-out Search Attempt: {q_str}")
            payload = {
                "requests": [{
                    "entityTypes": ["driveItem"],
                    "query": {"queryString": q_str},
                    "fields": ["id", "name", "webUrl", "summary", "filetype"],
                    "size": limit
                }]
            }
            try:
                resp = requests.post(url, headers=headers, json=payload, timeout=8)
                resp.raise_for_status()
                data = resp.json().get('value', [])
                if data:
                    for container in data[0].get('hitsContainers', []):
                        for hit in container.get('hits', []):
                            res = hit.get('resource', {})
                            iid = res.get('id')
                            if iid:
                                all_hits[iid] = {
                                    "id": iid,
                                    "name": res.get('name'),
                                    "webUrl": res.get('webUrl'),
                                    "summary": res.get('summary'),
                                    "filetype": res.get('filetype')
                                }
            except Exception as e:
                logger.warning(f"Fan-out branch failed: {str(e)}")

        with ThreadPoolExecutor(max_workers=3) as executor:
            executor.map(run_one_search, search_queries)

        final_results = list(all_hits.values())[:limit]
        angles_used = ", ".join([q.split()[0] if " " in q else q for q in search_queries])
        logger.info(f"Fan-out parallel search complete. Total unique hits: {len(final_results)} found via [{angles_used}]")
        # Keep a small indicator of parallelism for logging but don't break agent logic
        if final_results:
            final_results[0]["_parallel_discovery"] = True
        return final_results

    def get_document_content(self, item_id: str):
        url = f"https://graph.microsoft.com/v1.0/sites/{self.site_id}/drives/{self.drive_id}/items/{item_id}"
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
            
            import tempfile
            with tempfile.NamedTemporaryFile(delete=False, suffix=".bin") as tmp:
                for chunk in resp.iter_content(chunk_size=8192):
                    tmp.write(chunk)
                temp_filename = tmp.name
            
            try:
                result = self._md.convert(temp_filename)
                text_content = result.text_content
            finally:
                if os.path.exists(temp_filename):
                    os.remove(temp_filename)
            
            # PHASE: SMART TRUNCATION FOR SECURITY PROXY
            original_size = len(text_content)
            char_limit = 12000
            if original_size > char_limit:
                logger.info(f"Applying smart truncation to document {item_id}. Sliced from {original_size} to {char_limit}.")
                # Take top 10k (context/header) and bottom 2k (footer/summary/legal)
                text_content = (
                    text_content[:10000] + 
                    f"\n\n[TRUNCATION ALERT: Security Proxy sliced this 150KB+ document down to top 10KB + bottom 2KB for performance optimization and synthesis focus.]\n\n" + 
                    text_content[-2000:]
                )
            else:
                text_content = text_content + f"\n\n[ANALYSIS: Document fits in security context ({original_size} chars). No truncation required.]"
            
            return text_content
            
        except Exception as e:
            logger.error(f"Failed to fetch file content: {e}")
            return f"Failed to fetch content: {e}"

    def get_multiple_documents_content(self, item_ids: list[str]):
        """Fetches multiple documents in parallel for better throughput."""
        from concurrent.futures import ThreadPoolExecutor
        
        results = {}
        with ThreadPoolExecutor(max_workers=5) as executor:
            future_to_id = {executor.submit(self.get_document_content, iid): iid for iid in item_ids}
            for future in future_to_id:
                iid = future_to_id[future]
                try:
                    results[iid] = future.result()
                except Exception as e:
                    results[iid] = f"Error: {str(e)}"
        return results


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
