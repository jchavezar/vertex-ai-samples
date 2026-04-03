
import requests
import time
import logging
import os
import json
import fitz  # PyMuPDF for visual patching
from typing import List, Optional, Dict
from markitdown import MarkItDown
from dotenv import load_dotenv

# Absolute path to the .env file in the project root
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
DOTENV_PATH = os.path.join(CURRENT_DIR, "../../.env")
load_dotenv(dotenv_path=DOTENV_PATH)

# Configure dedicated logging for SharePoint MCP
LOG_FILE = "/tmp/sharepoint_mcp.log"
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(LOG_FILE),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("SharePointMCP")

class SharePointMCP:
    """
    Microsoft Graph API Proxy for SharePoint Document Libraries.
    Optimized for Zero-Leak Security and Post-Extraction Governance.
    """
    _drive_web_url_cache = {}

    def __init__(self, token=None):
        self.site_id = os.getenv("SITE_ID")
        self.drive_id = os.getenv("DRIVE_ID")
        self.region = os.getenv("MS_GRAPH_REGION", "NAM")
        self.base_url = "https://graph.microsoft.com/v1.0"
        
        # Masked logging to verify values without leaking secrets
        site_log = str(self.site_id)[:10] + "..." if self.site_id else "MISSING"
        drive_log = str(self.drive_id)[:10] + "..." if self.drive_id else "MISSING"
        
        logger.info(f"SharePointMCP Initializing with DOTENV_PATH: {DOTENV_PATH}")
        logger.info(f"SITE_ID: {site_log}, DRIVE_ID: {drive_log}, Region: {self.region}")
        
        if not self.site_id or not self.drive_id:
            logger.error("CRITICAL: SITE_ID or DRIVE_ID missing from environment. SharePoint integration will fail.")
        
        # Configure Vision-ready MarkItDown
        self._md = MarkItDown(image_description_callback=self._neural_vision_callback)
        
        if token:
            self.token = token
        else:
            logger.error("No user token provided. Delegated authentication required.")
            raise Exception("No user token provided. The application requires authorized requests from the frontend.")

    def _neural_vision_callback(self, image_data, **kwargs):
        """Internal callback for MarkItDown to process images via Gemini Flash."""
        try:
            from google import genai
            from google.genai import types
            client = genai.Client(vertexai=True, location='us-central1')
            model_id = 'gemini-2.5-flash' 
            logger.info(f"Triggering Neural Vision turn using {model_id}...")
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

    # --- CORE RECOVERY & DISCOVERY METHODS ---

    def get_drive_web_url(self):
        cache_key = f"{self.site_id}_{self.drive_id}"
        if cache_key in SharePointMCP._drive_web_url_cache:
            return SharePointMCP._drive_web_url_cache[cache_key]

        url = f"{self.base_url}/sites/{self.site_id}/drives/{self.drive_id}"
        res = requests.get(url, headers={"Authorization": f"Bearer {self.token}"})
        if not res.ok:
            logger.error(f"get_drive_web_url HTTP Error {res.status_code}: {res.text}")
            res.raise_for_status()
        
        web_url = res.json().get('webUrl')
        SharePointMCP._drive_web_url_cache[cache_key] = web_url
        return web_url

    def search_documents(self, query: str = "*", limit: int = 5):
        """Parallel Fan-out Search for finding documents across the sharepoint index."""
        logger.info(f"Searching SharePoint for: {query} (limit: {limit})")
        drive_web_url = None
        try:
            drive_web_url = self.get_drive_web_url()
            logger.info(f"Drive Web URL: {drive_web_url}")
        except Exception as e:
            logger.error(f"Failed to get drive web url: {e}")

        url = f"{self.base_url}/search/query"
        headers = {"Authorization": f"Bearer {self.token}", "Content-Type": "application/json"}
        
        # Query Expansion Angles
        search_queries = []
        search_queries.append(f'{query} path:"{drive_web_url}"' if drive_web_url else query)
        words = [w for w in query.split() if len(w) > 2]
        if len(words) > 1:
            broad_q = " OR ".join(words[:4])
            search_queries.append(f'({broad_q}) path:"{drive_web_url}"' if drive_web_url else broad_q)
        if len(words) > 0 and drive_web_url:
            search_queries.append(f'{words[0]}* path:"{drive_web_url.rstrip("/")}/*"')

        from concurrent.futures import ThreadPoolExecutor
        all_hits = {}
        
        def run_search(q_str):
            payload = {
                "requests": [{
                    "entityTypes": ["driveItem"],
                    "query": {"queryString": q_str},
                    "fields": ["id", "name", "webUrl", "summary", "filetype", "parentReference"],
                    "size": limit
                }]
            }
            try:
                logger.info(f"Executing search branch: {q_str}")
                resp = requests.post(url, headers=headers, json=payload, timeout=20)
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
                                    "filetype": res.get('filetype'),
                                    "folder": res.get('parentReference', {}).get('path')
                                }
            except Exception as e:
                logger.warning(f"Fan-out branch failed: {str(e)}")

        with ThreadPoolExecutor(max_workers=3) as executor:
            executor.map(run_search, search_queries)

        logger.info(f"Search complete. Found {len(all_hits)} distinct documents.")
        final_results = list(all_hits.values())[:limit]
        return final_results

    def list_folder_contents(self, folder_id: str = "root"):
        """Lists files and folders for the UI Explorer."""
        url = f"{self.base_url}/sites/{self.site_id}/drives/{self.drive_id}/items/{folder_id}/children"
        headers = {"Authorization": f"Bearer {self.token}"}
        res = requests.get(url, headers=headers)
        res.raise_for_status()
        items = res.json().get('value', [])
        return [{
            "id": i.get('id'),
            "name": i.get('name'),
            "type": "folder" if i.get('folder') else "file",
            "webUrl": i.get('webUrl'),
            "size": i.get('size')
        } for i in items]

    # --- EXTRACTION & READING METHODS ---

    def get_document_content(self, item_id: str, native: bool = False):
        """Downloads, converts and optionally returns native bytes for direct model ingestion."""
        url = f"{self.base_url}/sites/{self.site_id}/drives/{self.drive_id}/items/{item_id}"
        headers = {"Authorization": f"Bearer {self.token}"}
        try:
            response = requests.get(url, headers=headers)
            response.raise_for_status()
            data = response.json()
            download_url = data.get('@microsoft.graph.downloadUrl')
            if not download_url: return "No download URL available."

            resp = requests.get(download_url, stream=True)
            resp.raise_for_status()
            
            import tempfile
            # We use the original suffix if possible
            filename = data.get('name', 'doc.bin')
            suffix = os.path.splitext(filename)[1] or ".bin"
            
            with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
                for chunk in resp.iter_content(chunk_size=8192): tmp.write(chunk)
                temp_filename = tmp.name
            
            if native and suffix.lower() == ".pdf":
                with open(temp_filename, "rb") as f:
                    content_bytes = f.read()
                # We return a dict for native handling
                return {"type": "pdf", "bytes": content_bytes, "local_path": temp_filename}

            try:
                result = self._md.convert(temp_filename)
                text_content = result.text_content
                
                # Smart Truncation for oversized docs
                if len(text_content) > 12000:
                    text_content = text_content[:10000] + "\n\n[TRUNCATION ALERT: Security Proxy sliced content...]\n\n" + text_content[-2000:]
                
                return text_content
            finally:
                # Only remove if we didn't return a native path to be used later
                if not native and os.path.exists(temp_filename): 
                    os.remove(temp_filename)
        except Exception as e:
            logger.error(f"Failed to fetch content: {e}")
            return f"Error: {e}"

    def patch_pdf_content(self, local_path: str, patches: List[Dict[str, str]]):
        """Applies visual patches to a PDF while preserving layout and fonts."""
        try:
            doc = fitz.open(local_path)
            output_path = local_path.replace(".pdf", "_patched.pdf")
            
            logger.info(f"Applying {len(patches)} patches to {local_path}")
            
            patched_regions = {}
            sorted_patches = sorted(patches, key=lambda x: len(x.get("find", "")), reverse=True)
            
            for patch in sorted_patches:
                search_text = patch.get("find")
                replacement_text = patch.get("replace")
                if not search_text or not replacement_text: continue
                if search_text == replacement_text: continue
                
                for page_idx, page in enumerate(doc):
                    if page_idx not in patched_regions:
                        patched_regions[page_idx] = []
                    
                    text_instances = page.search_for(search_text)
                    for inst in text_instances:
                        is_overlapping = False
                        for prev_rect in patched_regions[page_idx]:
                            if inst.intersects(prev_rect):
                                is_overlapping = True
                                break
                        
                        if is_overlapping:
                            continue

                        dict_content = page.get_text("dict", clip=inst + (-2, -2, 2, 2))
                        
                        font_size = 9
                        font_color = (0, 0, 0)
                        font_name = "helv"
                        origin = inst.bl + (0, -1)
                        
                        found_style = False
                        for block in dict_content.get("blocks", []):
                            if block.get("type") != 0: continue
                            for line in block.get("lines", []):
                                for span in line.get("spans", []):
                                    if search_text.lower() in span["text"].lower() or inst.intersects(span["bbox"]):
                                        font_size = span["size"]
                                        c = span["color"]
                                        r = ((c >> 16) & 0xFF) / 255.0
                                        g = ((c >> 8) & 0xFF) / 255.0
                                        b = (c & 0xFF) / 255.0
                                        font_color = (r, g, b)
                                        
                                        raw_font = span["font"].lower()
                                        if "inter" in raw_font or "sans" in raw_font:
                                            font_name = "helv"
                                        elif "georgia" in raw_font or "serif" in raw_font or "times" in raw_font:
                                            font_name = "tiro"
                                        else:
                                            font_name = "helv"
                                            
                                        origin = fitz.Point(span["origin"])
                                        found_style = True
                                        break
                                if found_style: break
                            if found_style: break
                        
                        mask_rect = inst + (-0.5, -0.5, 0.5, 0.5)
                        page.draw_rect(mask_rect, color=(1, 1, 1), fill=(1, 1, 1))
                        
                        page.insert_text(origin, replacement_text, 
                                        fontsize=font_size, 
                                        color=font_color, 
                                        fontname=font_name)
                        
                        patched_regions[page_idx].append(inst)
            
            doc.save(output_path)
            doc.close()
            
            with open(output_path, "rb") as f:
                patched_bytes = f.read()
            
            if os.path.exists(output_path): os.remove(output_path)
            if os.path.exists(local_path): os.remove(local_path)
            
            return patched_bytes
        except Exception as e:
            logger.error(f"Visual patching failed: {e}")
            raise e

    def get_preview_url(self, item_id: str):
        """Generates a short-lived embeddable preview URL for the document."""
        url = f"{self.base_url}/sites/{self.site_id}/drives/{self.drive_id}/items/{item_id}/preview"
        headers = {"Authorization": f"Bearer {self.token}", "Content-Type": "application/json"}
        try:
            res = requests.post(url, headers=headers, json={})
            res.raise_for_status()
            return res.json().get('getUrl')
        except Exception as e:
            logger.error(f"Failed to get preview URL: {e}")
            return None

    def get_multiple_documents_content(self, item_ids: List[str]):
        """Parallel extraction of multiple documents across the SharePoint index."""
        from concurrent.futures import ThreadPoolExecutor
        results = {}

        def fetch(iid):
            content = self.get_document_content(iid)
            results[iid] = content

        with ThreadPoolExecutor(max_workers=5) as executor:
            executor.map(fetch, item_ids)
        
        return results

    # --- ADVANCED GOVERNANCE & ACTION METHODS ---

    def move_item(self, item_id: str, target_folder_id: str):
        """Moves a document to a different folder."""
        url = f"{self.base_url}/sites/{self.site_id}/drives/{self.drive_id}/items/{item_id}"
        headers = {"Authorization": f"Bearer {self.token}", "Content-Type": "application/json"}
        payload = {"parentReference": {"id": target_folder_id}}
        res = requests.patch(url, headers=headers, json=payload)
        res.raise_for_status()
        return res.json()

    def create_folder(self, name: str, parent_id: str = "root"):
        """Creates a new folder in the document library."""
        url = f"{self.base_url}/sites/{self.site_id}/drives/{self.drive_id}/items/{parent_id}/children"
        headers = {"Authorization": f"Bearer {self.token}", "Content-Type": "application/json"}
        payload = {"name": name, "folder": {}, "@microsoft.graph.conflictBehavior": "replace"}
        res = requests.post(url, headers=headers, json=payload)
        res.raise_for_status()
        return res.json()

    def upload_file(self, content: str, filename: str, target_folder_id: str = "root"):
        """Uploads a modified or new text/markdown file to SharePoint."""
        url = f"{self.base_url}/sites/{self.site_id}/drives/{self.drive_id}/items/{target_folder_id}:/{filename}:/content"
        headers = {"Authorization": f"Bearer {self.token}", "Content-Type": "text/plain"}
        res = requests.put(url, headers=headers, data=content.encode('utf-8'))
        res.raise_for_status()
        return res.json()

    def create_backup(self, item_id: str):
        """Creates a timestamped backup of the document."""
        try:
            url = f"{self.base_url}/sites/{self.site_id}/drives/{self.drive_id}/items/{item_id}"
            headers = {"Authorization": f"Bearer {self.token}"}
            res = requests.get(url, headers=headers)
            res.raise_for_status()
            item_data = res.json()
            original_name = item_data.get('name')
            
            backup_folder_id = self.get_special_folder("_backups")
            if not backup_folder_id:
                return None
                
            name_parts = original_name.rsplit('.', 1)
            base_name = name_parts[0]
            ext = name_parts[1] if len(name_parts) > 1 else ""
            
            # Delete old backups
            backups = self.list_folder_contents(backup_folder_id)
            existing_backups = [b for b in backups if b['name'].startswith(base_name + "_BAK_")]
            for old_backup in existing_backups:
                try:
                    del_url = f"{self.base_url}/sites/{self.site_id}/drives/{self.drive_id}/items/{old_backup['id']}"
                    requests.delete(del_url, headers=headers)
                except: pass
            
            timestamp = int(time.time())
            backup_name = f"{base_name}_BAK_{timestamp}.{ext}" if ext else f"{base_name}_BAK_{timestamp}"
            
            copy_url = f"{self.base_url}/sites/{self.site_id}/drives/{self.drive_id}/items/{item_id}/copy"
            payload = {"parentReference": {"id": backup_folder_id}, "name": backup_name}
            requests.post(copy_url, headers=headers, json=payload)
            return backup_name
        except Exception as e:
            logger.error(f"Backup failed: {e}")
            return None

    def update_document_content(self, item_id: str, content: str):
        """Updates the content of an existing document."""
        self.create_backup(item_id)
        url = f"{self.base_url}/sites/{self.site_id}/drives/{self.drive_id}/items/{item_id}/content"
        headers = {"Authorization": f"Bearer {self.token}", "Content-Type": "text/plain"}
        res = requests.put(url, headers=headers, data=content.encode('utf-8'))
        res.raise_for_status()
        return res.json()

    def get_special_folder(self, name: str):
        """Finds or creates a special folder."""
        try:
            items = self.list_folder_contents("root")
            for i in items:
                if i['name'] == name and i['type'] == 'folder':
                    return i['id']
            folder = self.create_folder(name)
            return folder.get('id')
        except: return None

    def get_backups(self, item_id: str):
        """Lists backups."""
        try:
            url = f"{self.base_url}/sites/{self.site_id}/drives/{self.drive_id}/items/{item_id}"
            headers = {"Authorization": f"Bearer {self.token}"}
            res = requests.get(url, headers=headers)
            res.raise_for_status()
            original_name = res.json().get('name')
            base_name = os.path.splitext(original_name)[0]
            if "_BAK_" in base_name: base_name = base_name.split("_BAK_")[0]

            backup_folder_id = self.get_special_folder("_backups")
            backups = self.list_folder_contents(backup_folder_id)
            relevant_backups = [b for b in backups if b['name'].startswith(base_name + "_BAK_")]
            relevant_backups.sort(key=lambda x: x['name'], reverse=True)
            return relevant_backups
        except: return []

    def restore_backup(self, item_id: str, backup_id: str = None):
        """Restores a backup."""
        try:
            url = f"{self.base_url}/sites/{self.site_id}/drives/{self.drive_id}/items/{item_id}"
            headers = {"Authorization": f"Bearer {self.token}"}
            res = requests.get(url, headers=headers)
            res.raise_for_status()
            file_name = res.json().get('name')

            if "_BAK_" in file_name:
                name_parts = file_name.rsplit('.', 1)
                real_base = name_parts[0].split("_BAK_")[0]
                ext = name_parts[1] if len(name_parts) > 1 else ""
                original_name = f"{real_base}.{ext}" if ext else real_base
                root_items = self.list_folder_contents("root")
                original_item = next((i for i in root_items if i['name'] == original_name), None)
                if not original_item: raise Exception("Original not found")
                target_item_id = original_item['id']
                target_backup_id = backup_id if backup_id else item_id
            else:
                target_item_id = item_id
                relevant_backups = self.get_backups(target_item_id)
                if not relevant_backups: raise Exception("No backups")
                target_backup_id = backup_id if backup_id else relevant_backups[0]['id']

            content_res = self.get_document_content(target_backup_id, native=True)
            if not isinstance(content_res, dict): raise Exception("Could not get backup content")
            backup_path = content_res['local_path']

            with open(backup_path, "rb") as f: backup_bytes = f.read()
            os.remove(backup_path)

            upload_url = f"{self.base_url}/sites/{self.site_id}/drives/{self.drive_id}/items/{target_item_id}/content"
            requests.put(upload_url, headers={"Authorization": f"Bearer {self.token}", "Content-Type": "application/octet-stream"}, data=backup_bytes)
            return {"status": "success"}
        except Exception as e:
            return {"status": "error", "error": str(e)}
