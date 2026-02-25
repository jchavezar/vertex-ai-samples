import os
import sys
import json
import time
import logging
import asyncio
import msal
import requests
import tempfile
import vertexai
from typing import List, Optional, Generator, Dict, Any
from dotenv import load_dotenv
from markitdown import MarkItDown
from pydantic import BaseModel, Field

# Google ADK Imports
from google.adk.agents import LlmAgent, Agent
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai import types

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("classifier_agent.log"),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger("SharePointClassifier")

# Load env vars
load_dotenv()

# -------------------------------------------------------------------------
# Data Models (Structured Output)
# -------------------------------------------------------------------------
class SensitivityClassification(BaseModel):
    """Structured output for document sensitivity analysis."""
    file_uid: str = Field(..., description="Unique ID of the file")
    filename: str = Field(..., description="Name of the file")
    sensitivity_level: str = Field(..., description="High, Medium, or Low")
    contains_pii: bool = Field(..., description="True if PII is detected")
    classification_tags: List[str] = Field(description="Tags like 'Financial', 'Legal', 'Public', 'Internal'")
    summary: str = Field(description="Brief summary of the document content")
    reasoning: str = Field(description="Why this sensitivity level was assigned")
    recommended_action: Optional[str] = Field(default=None, description="e.g., 'Encrypt', 'Delete', 'Restrict Access'")

# -------------------------------------------------------------------------
# SharePoint Connector (Delta Query)
# -------------------------------------------------------------------------
class SharePointConnector:
    def __init__(self, tenant_id, client_id, client_secret, site_id, drive_id):
        self.site_id = site_id
        self.drive_id = drive_id
        self.app = msal.ConfidentialClientApplication(
            client_id, authority=f"https://login.microsoftonline.com/{tenant_id}",
            client_credential=client_secret
        )
        self.token = None
        self.token_expires_at = 0

    def get_token(self):
        """Refreshes token if expired."""
        if self.token and time.time() < self.token_expires_at - 60:
            return self.token
        
        result = self.app.acquire_token_for_client(scopes=["https://graph.microsoft.com/.default"])
        if "access_token" in result:
            self.token = result['access_token']
            self.token_expires_at = time.time() + result.get('expires_in', 3600)
            return self.token
        else:
            raise Exception(f"Auth failed: {result.get('error_description')}")

    def get_headers(self):
        return {"Authorization": f"Bearer {self.get_token()}"}

    def get_delta_changes(self, state: Dict[str, Any] = None) -> Generator[Dict, None, str]:
        """
        Yields items from the Delta Query.
        Returns the new 'deltaLink' to save for next time.
        """
        state = state or {}
        # Use existing delta_link or next_link, or start fresh
        url = state.get("next_link") or state.get("delta_link")
        
        if not url:
            # Initial Delta Query with explicit select for downloadUrl
            base_url = f"https://graph.microsoft.com/v1.0/sites/{self.site_id}/drives/{self.drive_id}/root/delta"
            url = f"{base_url}?$select=id,name,webUrl,file,parentReference,createdDateTime,@microsoft.graph.downloadUrl"
        
        logger.info(f"Starting Delta Query from: {url[:50]}...")

        while url:
            try:
                response = requests.get(url, headers=self.get_headers())
                if response.status_code == 429:
                    retry = int(response.headers.get('Retry-After', 10))
                    logger.warning(f"Throttled. Sleeping {retry}s...")
                    time.sleep(retry)
                    continue
                
                response.raise_for_status()
                data = response.json()
                
                items = data.get('value', [])
                for item in items:
                    yield item
                
                # Check for next page or final delta link
                if '@odata.nextLink' in data:
                    url = data['@odata.nextLink']
                elif '@odata.deltaLink' in data:
                    delta_link = data['@odata.deltaLink']
                    logger.info("Delta Query complete. Yielding deltaToken.")
                    yield {'delta_link': delta_link}
                    break
                else:
                    break
                    
            except Exception as e:
                logger.error(f"Delta Query Failed: {e}")
                raise

    def download_file(self, download_url: str, item_id: str) -> bytes:
        """Downloads file content. Tries downloadUrl first, then /content endpoint."""
        urls_to_try = []
        if download_url:
            urls_to_try.append(download_url)
        
        # Always add the direct content endpoint as fallback
        urls_to_try.append(f"https://graph.microsoft.com/v1.0/sites/{self.site_id}/drives/{self.drive_id}/items/{item_id}/content")
        
        for url in urls_to_try:
            try:
                logger.info(f"Attempting download from: {url[:50]}...")
                headers = self.get_headers()
                
                # HEAD check (skip for direct content endpoint as it might not support HEAD or be inefficient)
                if "downloadUrl" in url or "monitor" in url: 
                    try:
                        h = requests.head(url, headers=headers, timeout=5)
                        if h.status_code == 200:
                            size = int(h.headers.get('Content-Length', 0))
                            if size > 20 * 1024 * 1024:
                                logger.warning(f"File too large ({size} bytes). Skipping.")
                                return b""
                    except:
                        pass

                r = requests.get(url, headers=headers, timeout=30)
                if r.status_code == 200:
                    logger.info(f"Downloaded {len(r.content)} bytes.")
                    return r.content
                else:
                    logger.warning(f"Download failed from {url[:30]}... Status: {r.status_code}")
            
            except Exception as e:
                logger.warning(f"Error downloading from {url[:30]}...: {e}")
        
        logger.error(f"Failed to download file {item_id}")
        return b""

# -------------------------------------------------------------------------
# Content Analyzer (Google ADK)
# -------------------------------------------------------------------------
class ContentAnalyzer:
    def __init__(self, project_id, location):
        self.project_id = project_id
        
        # Explicitly init Vertex AI with GLOBAL location as requested
        vertexai.init(project=project_id, location=location)
        
        # Initialize ADK Components
        self.session_service = InMemorySessionService()
        
        # Define the ADK Agent
        self.agent = LlmAgent(
            name="DataSecurityOfficer",
            model="gemini-3-flash-preview",
            instruction="""
            You are a Data Security Officer. Analyze this document.
            
            Task:
            1. Summarize the document.
            2. Detect if it contains PII (Personally Identifiable Information) or sensitive data.
            3. Classify its sensitivity (High/Medium/Low).
            4. Tag it appropriately.
            
            Return the result in structured JSON format matching the schema.
            """,
            output_schema=SensitivityClassification,
            output_key="classification_result"
        )
        
        self.runner = Runner(
            agent=self.agent,
            session_service=self.session_service,
            app_name="sharepoint_classifier"
        )
        
    async def analyze_document_async(self, file_content: bytes, mime_type: str, metadata: Dict) -> SensitivityClassification:
        """
        Sends document to Gemini via ADK Runner.
        """
        if not file_content:
            return SensitivityClassification(
                file_uid=metadata.get('id'),
                filename=metadata.get('name'),
                sensitivity_level="Unknown",
                contains_pii=False,
                classification_tags=["Skipped", "No-Content"],
                summary="File was empty or too large.",
                reasoning="Content unavailable."
            )

        # 1. Prepare Content
        content_parts = []
        
        # Metadata Context
        meta_info = f"""
        Metadata:
        - Name: {metadata.get('name')}
        - Created: {metadata.get('createdDateTime')}
        - Path: {metadata.get('parentReference', {}).get('path')}
        - ID: {metadata.get('id')}
        """
        content_parts.append(types.Part(text=meta_info))

        # File Content Handling
        CONVERT_TYPES = [
            "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            "application/vnd.openxmlformats-officedocument.presentationml.presentation",
            "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
        ]
        
        try:
            if mime_type in CONVERT_TYPES:
                logger.info(f"Converting {mime_type} to text via MarkItDown...")
                with tempfile.NamedTemporaryFile(delete=False, suffix=".bin") as tmp:
                    tmp.write(file_content)
                    tmp_path = tmp.name
                try:
                    md = MarkItDown()
                    res = md.convert(tmp_path)
                    text = res.text_content
                    # Truncate
                    if len(text) > 1000000:
                        logger.warning(f"Truncating content from {len(text)} chars to 1,000,000 chars.")
                        text = text[:1000000]
                    content_parts.append(types.Part(text=text))
                finally:
                    if os.path.exists(tmp_path):
                        os.remove(tmp_path)
            else:
                # Pass as binary part if supported (PDF, text, etc)
                if mime_type.startswith("text/"):
                    try:
                        content_parts.append(types.Part(text=file_content.decode('utf-8', errors='ignore')))
                    except:
                        content_parts.append(types.Part(inline_data=types.Blob(data=file_content, mime_type=mime_type)))
                else:
                    content_parts.append(types.Part(inline_data=types.Blob(data=file_content, mime_type=mime_type)))

            # 2. execute Agent via Runner
            session_id = f"session_{metadata.get('id')}"
            # Ensure fresh session for each doc to avoid context pollution
            await self.session_service.create_session(
                app_name="sharepoint_classifier", 
                session_id=session_id, 
                user_id="system"
            )
            
            user_content = types.Content(role="user", parts=content_parts)
            
            final_result = None
            async for event in self.runner.run_async(session_id=session_id, new_message=user_content, user_id="system"):
                # We can log intermediate events here if needed
                pass
            
            # 3. Retrieve Structured Output from Session State
            session = await self.session_service.get_session(
                app_name="sharepoint_classifier", 
                session_id=session_id, 
                user_id="system"
            )
            
            raw_result = session.state.get("classification_result")
            
            if isinstance(raw_result, SensitivityClassification):
                # Ensure fields from metadata are preserved if model hallucinated them or if we want to enforce them
                raw_result.file_uid = metadata.get('id')
                raw_result.filename = metadata.get('name')
                return raw_result
            elif isinstance(raw_result, dict):
                 # Fallback if it acted weirdly and returned dict
                 raw_result['file_uid'] = metadata.get('id')
                 raw_result['filename'] = metadata.get('name')
                 return SensitivityClassification(**raw_result)
            else:
                 raise ValueError(f"Unexpected result type: {type(raw_result)}")

        except Exception as e:
            logger.exception("ADK Agent Analysis Failed")
            return SensitivityClassification(
                file_uid=metadata.get('id'),
                filename=metadata.get('name'),
                sensitivity_level="Error",
                contains_pii=False,
                classification_tags=["Analysis-Failed"],
                summary=f"Analysis failed: {str(e)}",
                reasoning="AI Error"
            )

# -------------------------------------------------------------------------
# Main Application
# -------------------------------------------------------------------------
STATE_FILE = "sync_state.json"
REPORT_FILE = "classification_report.jsonl"

async def main():
    # 1. Config
    TENANT_ID = os.getenv("TENANT_ID")
    CLIENT_ID = os.getenv("CLIENT_ID")
    CLIENT_SECRET = os.getenv("CLIENT_SECRET")
    SITE_ID = os.getenv("SITE_ID")
    DRIVE_ID = os.getenv("DRIVE_ID")
    PROJECT_ID = os.getenv("GOOGLE_CLOUD_PROJECT") or os.getenv("PROJECT_ID")
    LOCATION = "global"

    # Force ADK/GenAI SDK to use global location
    os.environ["GOOGLE_CLOUD_LOCATION"] = LOCATION
    os.environ["GOOGLE_GENAI_LOCATION"] = LOCATION

    if not all([TENANT_ID, CLIENT_ID, PROJECT_ID]):
        logger.error("Missing Env Vars. Ensure TENANT_ID, CLIENT_ID, GOOGLE_CLOUD_PROJECT are set.")
        sys.exit(1)

    # 2. Init Components
    connector = SharePointConnector(TENANT_ID, CLIENT_ID, CLIENT_SECRET, SITE_ID, DRIVE_ID)
    analyzer = ContentAnalyzer(PROJECT_ID, LOCATION)
    
    # 3. Load State
    state = {}
    if os.path.exists(STATE_FILE):
        try:
            with open(STATE_FILE, 'r') as f:
                state = json.load(f)
        except json.JSONDecodeError:
            logger.warning("State file corrupted, starting fresh.")
            state = {}

    logger.info("--- Starting Scalable Classification Run (ADK Powered) ---")

    # 4. Processing Loop
    MAX_FILES_TO_PROCESS = 1000 
    processed_count = 0
    all_results = []
    
    try:
        delta_iterator = connector.get_delta_changes(state)
        
        for item in delta_iterator:
            if 'delta_link' in item:
                 state['delta_link'] = item['delta_link']
                 continue
            
            if 'file' not in item:
                continue 
            
            if processed_count >= MAX_FILES_TO_PROCESS:
                logger.info(f"Hit limit of {MAX_FILES_TO_PROCESS} files. Stopping.")
                break

            name = item.get('name', 'unknown')
            mime = item.get('file', {}).get('mimeType', '')
            
            # Filter supported types
            if not any(ext in name.lower() for ext in ['.pdf', '.docx', '.pptx', '.xlsx', '.txt']):
                logger.info(f"Skipping unsupported type: {name}")
                continue

            logger.info(f"Processing: {name}...")
            
            # Download
            download_url = item.get('@microsoft.graph.downloadUrl')
            # Note: synchronous download helper method in async main loop is fine for this script
            content_bytes = connector.download_file(download_url, item.get('id'))
            
            # Analyze (Async)
            result = await analyzer.analyze_document_async(content_bytes, mime, item)
            
            # Collect Result
            all_results.append(result.model_dump())
            
            processed_count += 1
            print(f"✅ Classified: {name} -> {result.sensitivity_level}")

        # Save Final Report
        with open("classification_report.json", 'w') as f:
            json.dump(all_results, f, indent=2)
            
        # Save state
        with open(STATE_FILE, 'w') as f:
            json.dump(state, f)
            
    except Exception as e:
        logger.exception("Run failed.")
        sys.exit(1)

    logger.info("Run Complete.")

if __name__ == "__main__":
    if sys.platform == 'win32':
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    asyncio.run(main())
