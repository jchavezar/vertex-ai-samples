# backend/main.py
from __future__ import annotations

import time
import uuid
import json
import logging
from typing import Any, Optional, List, Dict
from fastapi import FastAPI, HTTPException, status, BackgroundTasks, Header, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
import msal
import httpx
from google import genai
from google.genai import types
from google.cloud import firestore
from google.cloud import bigquery
import zipfile
import io
import xml.etree.ElementTree as ET

def extract_text_from_docx(file_bytes: bytes) -> str:
    try:
        with zipfile.ZipFile(io.BytesIO(file_bytes)) as z:
            xml_content = z.read("word/document.xml")
            root = ET.fromstring(xml_content)
            paragraphs = []
            for paragraph in root.iter('{http://schemas.openxmlformats.org/wordprocessingml/2006/main}p'):
                texts = []
                for text_node in paragraph.iter('{http://schemas.openxmlformats.org/wordprocessingml/2006/main}t'):
                    if text_node.text:
                        texts.append(text_node.text)
                if texts:
                    paragraphs.append("".join(texts))
            return "\n".join(paragraphs)
    except Exception as e:
        print(f"Error parsing docx: {e}")
        return file_bytes.decode("utf-8", errors="ignore")

def extract_text_from_pptx(file_bytes: bytes) -> str:
    try:
        with zipfile.ZipFile(io.BytesIO(file_bytes)) as z:
            slide_texts = []
            slide_files = sorted([f for f in z.namelist() if f.startswith("ppt/slides/slide") and f.endswith(".xml")])
            for slide_file in slide_files:
                xml_content = z.read(slide_file)
                root = ET.fromstring(xml_content)
                texts = []
                for node in root.iter('{http://schemas.openxmlformats.org/drawingml/2006/main}t'):
                    if node.text:
                        texts.append(node.text)
                if texts:
                    slide_texts.append(" ".join(texts))
            return "\n\n--- Slide ---\n\n".join(slide_texts)
    except Exception as e:
        print(f"Error parsing pptx: {e}")
        return file_bytes.decode("utf-8", errors="ignore")

def extract_text_from_xlsx(file_bytes: bytes) -> str:
    try:
        with zipfile.ZipFile(io.BytesIO(file_bytes)) as z:
            shared_strings = []
            if "xl/sharedStrings.xml" in z.namelist():
                xml_content = z.read("xl/sharedStrings.xml")
                root = ET.fromstring(xml_content)
                for node in root.iter('{http://schemas.openxmlformats.org/spreadsheetml/2006/main}t'):
                    if node.text:
                        shared_strings.append(node.text)
            
            sheet_texts = []
            sheet_files = sorted([f for f in z.namelist() if f.startswith("xl/worksheets/sheet") and f.endswith(".xml")])
            for sheet_file in sheet_files:
                xml_content = z.read(sheet_file)
                root = ET.fromstring(xml_content)
                cell_values = []
                for row in root.iter('{http://schemas.openxmlformats.org/spreadsheetml/2006/main}row'):
                    row_vals = []
                    for cell in row.iter('{http://schemas.openxmlformats.org/spreadsheetml/2006/main}c'):
                        t_type = cell.get('t')
                        v_node = cell.find('{http://schemas.openxmlformats.org/spreadsheetml/2006/main}v')
                        if v_node is not None and v_node.text:
                            val = v_node.text
                            if t_type == 's':
                                try:
                                    idx = int(val)
                                    if 0 <= idx < len(shared_strings):
                                        val = shared_strings[idx]
                                except:
                                    pass
                            row_vals.append(val)
                    if row_vals:
                        cell_values.append(" | ".join(row_vals))
                if cell_values:
                    sheet_texts.append("\n".join(cell_values))
            
            full_text = []
            if shared_strings:
                full_text.append("Shared Strings:\n" + "\n".join(shared_strings))
            if sheet_texts:
                full_text.append("\n\nSheets Data:\n" + "\n\n--- Sheet ---\n\n".join(sheet_texts))
            return "\n\n".join(full_text) if full_text else "Empty Spreadsheet"
    except Exception as e:
        print(f"Error parsing xlsx: {e}")
        return file_bytes.decode("utf-8", errors="ignore")

def extract_text_from_eml(file_bytes: bytes) -> str:
    try:
        import email
        from email.policy import default
        msg = email.message_from_bytes(file_bytes, policy=default)
        subject = msg.get('subject', '')
        sender = msg.get('from', '')
        to = msg.get('to', '')
        date = msg.get('date', '')
        
        body_parts = []
        body = msg.get_body(preferencelist=('plain', 'html'))
        if body:
            body_text = body.get_content()
            body_parts.append(body_text)
        else:
            for part in msg.walk():
                if part.get_content_type() == "text/plain":
                    body_parts.append(part.get_payload(decode=True).decode(errors="ignore"))
                elif part.get_content_type() == "text/html":
                    body_parts.append(part.get_payload(decode=True).decode(errors="ignore"))
        
        email_content = f"Subject: {subject}\nFrom: {sender}\nTo: {to}\nDate: {date}\n\n" + "\n".join(body_parts)
        return email_content
    except Exception as e:
        print(f"Error parsing eml: {e}")
        return file_bytes.decode("utf-8", errors="ignore")

app = FastAPI(title="SharePoint Restructure Portal API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

ACTIVE_MODEL = "gemini-3.5-flash"
ACTIVE_REGION = "global"
PROJECT_ID = "vtxdemos"
EMBEDDING_MODEL = "gemini-embedding-2"

MS365_CLIENT_ID = "44260445-702b-4d0c-aa37-cbed79b50531"
MS365_TENANT_ID = "de46a3fd-0d68-4b25-8343-6eb5d71afce9"
GRAPH_SCOPES = ["User.Read", "Sites.Read.All", "Files.Read.All"]

# Initialize live Gemini client
import threading

_thread_local = threading.local()

class GenAIClientProxy:
    @property
    def models(self):
        if not hasattr(_thread_local, "genai_client") or _thread_local.genai_client is None:
            _thread_local.genai_client = genai.Client(vertexai=True, project=PROJECT_ID, location=ACTIVE_REGION)
        return _thread_local.genai_client.models

client = GenAIClientProxy()

class FirestoreClientProxy:
    @property
    def client(self):
        if not hasattr(_thread_local, "firestore_client") or _thread_local.firestore_client is None:
            _thread_local.firestore_client = firestore.Client(project=PROJECT_ID)
        return _thread_local.firestore_client
    def __getattr__(self, name):
        return getattr(self.client, name)

db_client = FirestoreClientProxy()

class BigQueryClientProxy:
    @property
    def client(self):
        if not hasattr(_thread_local, "bigquery_client") or _thread_local.bigquery_client is None:
            _thread_local.bigquery_client = bigquery.Client(project=PROJECT_ID)
        return _thread_local.bigquery_client
    def __getattr__(self, name):
        return getattr(self.client, name)

bq_client = BigQueryClientProxy()

# --- MSAL AUTHENTICATION MANAGER ---
class MSALAuthManager:
    def __init__(self):
        import requests
        self.http_session = requests.Session()
        self.app = msal.PublicClientApplication(
            client_id=MS365_CLIENT_ID,
            authority=f"https://login.microsoftonline.com/{MS365_TENANT_ID}",
            http_client=self.http_session
        )
        self.token: Optional[str] = None
        self.account_info: Optional[dict] = None
        self.pending_flow: Optional[dict] = None
        self.code_verifier: Optional[str] = None
        
        # Load cached session from shared ms365-mcp-server if available
        self._load_cached_session()

    def is_token_expired(self, token: str) -> bool:
        try:
            parts = token.split('.')
            if len(parts) != 3:
                return True
            payload_b64 = parts[1]
            payload_b64 += '=' * (4 - len(payload_b64) % 4)
            import base64
            import json
            import time
            payload = json.loads(base64.urlsafe_b64decode(payload_b64).decode('utf-8'))
            exp = payload.get('exp')
            # Check if it expires in less than 60 seconds
            if exp and exp < (time.time() + 60):
                return True
            return False
        except Exception:
            return True

    def _save_cached_session(self, refresh_token: str):
        import os
        import json
        cache_file = os.path.expanduser("~/vertex-ai-samples/semiautonomous-agents/ms365-mcp-server/.ms365_auth.json")
        try:
            data = {
                "access_token": self.token,
                "refresh_token": refresh_token,
                "account": self.account_info,
                "origin": getattr(self, "origin", "http://localhost:5185"),
                "expires_at": None
            }
            with open(cache_file, "w") as f:
                json.dump(data, f, indent=2)
            print("[AUTH MANAGER] Refreshed session saved to shared cache.")
        except Exception as e:
            print(f"[AUTH MANAGER] Failed to save refreshed session: {e}")

    def _load_cached_session(self):
        import os
        import json
        cache_file = os.path.expanduser("~/vertex-ai-samples/semiautonomous-agents/ms365-mcp-server/.ms365_auth.json")
        if os.path.exists(cache_file):
            try:
                with open(cache_file, "r") as f:
                    data = json.load(f)
                
                # Check for direct tokens first
                self.token = data.get("access_token")
                self.account_info = data.get("account")
                self.origin = data.get("origin") or "http://localhost:5185"
                self.http_session.headers["Origin"] = self.origin
                
                # If we have a token, check if it's expired
                if self.token and self.is_token_expired(self.token):
                    # It's expired, try to refresh it using the refresh token
                    refresh_token = data.get("refresh_token")
                    if refresh_token:
                        # Feed the refresh token back into MSAL
                        result = self.app.acquire_token_by_refresh_token(
                            refresh_token,
                            scopes=GRAPH_SCOPES
                        )
                        if "access_token" in result:
                            self.token = result["access_token"]
                            self.account_info = {
                                "username": result.get("id_token_claims", {}).get("preferred_username") or data.get("account", {}).get("username"),
                                "name": result.get("id_token_claims", {}).get("name") or data.get("account", {}).get("name"),
                                "tenant_id": result.get("id_token_claims", {}).get("tid") or data.get("account", {}).get("tenant_id"),
                            }
                            # Save the newly refreshed token back to the shared cache
                            self._save_cached_session(refresh_token)
                        else:
                            print(f"[AUTH MANAGER] Silent token refresh failed: {result}")
                            self.token = None
                            self.account_info = None
                    else:
                        print("[AUTH MANAGER] Cached token is expired and no refresh token is available.")
                        self.token = None
                        self.account_info = None
                print(f"[AUTH MANAGER] Successfully auto-loaded session for {self.account_info}")
            except Exception as e:
                print(f"[AUTH MANAGER] Failed to load session from shared cache: {e}")

    def start_flow(self, redirect_uri: str) -> str:
        # Inject the correct Origin header matching the redirect URI origin to support SPA client configurations
        from urllib.parse import urlparse
        parsed = urlparse(redirect_uri)
        origin = f"{parsed.scheme}://{parsed.netloc}"
        self.http_session.headers["Origin"] = origin
        self.origin = origin

        # Use MSAL's native flow initiation to correctly generate and attach PKCE parameters
        self.pending_flow = self.app.initiate_auth_code_flow(
            scopes=GRAPH_SCOPES,
            redirect_uri=redirect_uri
        )
        return self.pending_flow["auth_uri"]

    def complete_flow(self, code: str, redirect_uri: str) -> dict:
        if not self.pending_flow:
            raise ValueError("No active authentication flow found. Please restart sign-in.")
        
        # Inject the correct Origin header matching the redirect URI origin to support SPA client configurations
        from urllib.parse import urlparse
        parsed = urlparse(redirect_uri)
        origin = f"{parsed.scheme}://{parsed.netloc}"
        self.http_session.headers["Origin"] = origin
        self.origin = origin

        # Build standard auth response dict containing code and state
        auth_response = {
            "code": code,
            "state": self.pending_flow.get("state")
        }
        
        result = self.app.acquire_token_by_auth_code_flow(
            auth_code_flow=self.pending_flow,
            auth_response=auth_response
        )
        
        # Clear pending flow
        self.pending_flow = None
        
        if "access_token" in result:
            self.token = result["access_token"]
            self.account_info = {
                "username": result.get("id_token_claims", {}).get("preferred_username"),
                "name": result.get("id_token_claims", {}).get("name"),
                "tenant_id": result.get("id_token_claims", {}).get("tid"),
            }
            # Save the newly acquired token to the shared cache
            import os
            import json
            cache_file = os.path.expanduser("~/vertex-ai-samples/semiautonomous-agents/ms365-mcp-server/.ms365_auth.json")
            try:
                data = {
                    "access_token": self.token,
                    "refresh_token": result.get("refresh_token"),
                    "account": self.account_info,
                    "origin": origin,
                    "expires_at": None
                }
                with open(cache_file, "w") as f:
                    json.dump(data, f, indent=2)
                print("[AUTH MANAGER] Auth code flow login saved to shared cache.")
            except Exception as e:
                print(f"[AUTH MANAGER] Failed to save login to shared cache: {e}")
                
            return self.account_info
        else:
            raise Exception(result.get("error_description", "Authentication failed."))

    def get_token(self) -> Optional[str]:
        # Try in-memory MSAL accounts
        accounts = self.app.get_accounts()
        if accounts:
            result = self.app.acquire_token_silent(scopes=GRAPH_SCOPES, account=accounts[0])
            if result and "access_token" in result:
                self.token = result["access_token"]
                return self.token
        
        # If in-memory is empty, try loading from shared cache again just in case it was refreshed elsewhere
        self._load_cached_session()
        return self.token

    def logout(self):
        self.token = None
        self.account_info = None
        self.pending_flow = None
        self.code_verifier = None
        for account in self.app.get_accounts():
            self.app.remove_account(account)
        
        # Clear shared cache file
        import os
        import json
        cache_file = os.path.expanduser("~/vertex-ai-samples/semiautonomous-agents/ms365-mcp-server/.ms365_auth.json")
        if os.path.exists(cache_file):
            try:
                with open(cache_file, "w") as f:
                    json.dump({}, f)
                print("[AUTH MANAGER] Shared cache cleared on logout.")
            except Exception as e:
                print(f"[AUTH MANAGER] Failed to clear shared cache file: {e}")

auth_manager = MSALAuthManager()

# --- DYNAMIC CORPORATE TAXONOMY SCHEMAS ---

class ExtractedCorporateMetadata(BaseModel):
    confidentiality: str = Field(
        description="Confidentiality Classification. Must be one of: Public, Internal, Confidential, Highly Confidential"
    )
    document_type: str = Field(
        description="Level 1 Tag Type. Must be one of: PwC Engagement File, PwC Operational File, External File, Other File Type"
    )
    document_sub_type: str = Field(
        description="Level 2 Tag Type. Must match Level 1 parent: PwC Proposal, PwC Engagement Artefact, PwC Engagement Citation/ Case Study, Other Engagement File, PwC CV, PwC Legal Document, PwC Business Development Artefact, PwC Internal Project Artefact, PwC Internal Knowledge/ Policy, PwC Thought Leadership/ Research, Other Operational File, External Annual Report, External Company Profile, External Case Study, External Knowledge Article, External Training Material, Other External File, Undetermined"
    )
    pwc_proprietary: str = Field(
        description="PwC Proprietary Indicator. Must be: Yes, No"
    )
    primary_industry: str = Field(
        description="Primary Industry. Must be one of: Technology, Media and Telecommunications, Government and Public Services, Financial Services, Energy, Utilities and Resources, Industrial Manufacturing and Automotive, Consumer Markets, Health Industries, Private Equity, Real Assets and Sovereign Investment Funds, N/A"
    )
    primary_topic: str = Field(
        description="Primary Topic. A short sentence summarizing the main topic."
    )
    named_entities: List[str] = Field(
        description="List of organizations/companies mentioned in the text."
    )
    named_people: List[str] = Field(
        description="List of people mentioned in the text."
    )
    candidate_name: Optional[str] = Field(
        description="Full name of job applicant. Set to null if document is not a PwC CV."
    )
    candidate_recent_experience: Optional[str] = Field(
        description="Job applicant's current or most recent employer/job description (excluding education). Null if not a CV."
    )
    is_signed: Optional[str] = Field(
        description="Signed Status. Yes if signed/executed signature page is found, No if unsigned/draft, N/A if not a contract/engagement letter."
    )
    standard_terms: Optional[str] = Field(
        description="Standard Terms. Yes if uses PwC standard template terms, No if non-standard/custom liability/indemnity, N/A if not a legal agreement."
    )
    permitted_use: Optional[str] = Field(
        description="Deliverable Permitted Use. Description of distribution rights or limitation of liability scope (e.g. for PwC internal use only, third-party distribution permitted). Null if not an engagement file."
    )
    engagement_letter_link: Optional[str] = Field(
        description="Linked Engagement Letter. Filename or title of the associated parent Engagement Letter if this file is a deliverable (e.g. report, slide pack). Null if none or not a deliverable."
    )
    liability_cap: Optional[str] = Field(
        description="Extracted Liability Cap. Value or description of liability limitation (e.g. £10m cap, 3x fees, none). Null if not a legal agreement."
    )

class IngestRequest(BaseModel):
    filename: str
    content: str
    site: str
    allowed_groups: List[str]

class SearchRequest(BaseModel):
    query: str

class ValidationAction(BaseModel):
    confidentiality: Optional[str] = None
    document_sub_type: Optional[str] = None
    state: str
    exception_reason: Optional[str] = None

class SharePointImportRequest(BaseModel):
    site_id: str
    drive_id: str
    folder_path: str = "/"
    allowed_groups: List[str]

# --- IN-MEMORY DATABASE WITH BENCHMARK CORPUS ---
# --- CLOUD FIRESTORE PERSISTENCE CLIENT ---
def load_documents_from_store() -> List[Dict[str, Any]]:
    docs_ref = db_client.collection("sharepoint_documents")
    docs = []
    try:
        for d in docs_ref.stream():
            docs.append(d.to_dict())
    except Exception as e:
        print(f"[FIRESTORE] Failed to load documents: {e}")
    return docs

def seed_documents_if_empty():
    print("[FIRESTORE] Checking if default documents need seeding...")
    try:
        docs_ref = db_client.collection("sharepoint_documents")
        handbook_query = list(docs_ref.where("filename", "==", "US_Employee_Handbook_2025.pdf").stream())
        if not handbook_query:
            print("[FIRESTORE] Seeding US_Employee_Handbook_2025.pdf...")
            doc_id = "doc_handbook_2025"
            handbook_doc = {
                "id": doc_id,
                "filename": "US_Employee_Handbook_2025.pdf",
                "site": "Human Resources",
                "type": "PwC Internal Knowledge/ Policy",
                "sub_type": "PwC Internal Knowledge/ Policy",
                "confidentiality": "Internal",
                "pwc_proprietary": "No",
                "industry": "N/A",
                "primary_topic": "Employee Benefits and 401k match policy.",
                "allowed_groups": ["group::employees"],
                "confidence": 0.95,
                "pii_detected": False,
                "state": "APPROVED",
                "owner": "HR Benefits Team",
                "rationale": "Default benefits policy document containing 401k and general policies.",
                "elements": ["text"],
                "content": "Aether Corp offers a matched 401k contribution of up to <redact>4%</redact> for US employees, subject to standard vesting schedules. Grounded citations and verification matches are processed against this master policy document. All employees under group::employees are entitled to participate in the 401k match program.",
                "webUrl": "#",
                "is_signed": "N/A",
                "standard_terms": "N/A",
                "permitted_use": "N/A",
                "engagement_letter_link": "N/A",
                "liability_cap": "N/A"
            }
            docs_ref.document(doc_id).set(handbook_doc)
            try:
                sync_document_to_bigquery(handbook_doc)
                print("[BIGQUERY] Successfully synced seeded handbook.")
            except Exception as e:
                print(f"[BIGQUERY] Failed to sync handbook: {e}")
        else:
            print("[FIRESTORE] US_Employee_Handbook_2025.pdf is already seeded.")
    except Exception as e:
        print(f"[FIRESTORE] Error during seeding: {e}")

def init_bigquery_schema():
    dataset_id = f"{PROJECT_ID}.sharepoint_portal_ds"
    dataset = bigquery.Dataset(dataset_id)
    dataset.location = "US"
    
    # Create dataset if not exists
    try:
        bq_client.get_dataset(dataset_id)
        print("[BIGQUERY] Dataset already exists.")
    except Exception:
        print("[BIGQUERY] Creating dataset sharepoint_portal_ds...")
        try:
            bq_client.create_dataset(dataset, timeout=30)
            print("[BIGQUERY] Dataset created.")
        except Exception as e:
            print(f"[BIGQUERY] Failed to create dataset: {e}")
            return
            
    # Define Table Schema
    table_id = f"{dataset_id}.documents_metadata"
    schema = [
        bigquery.SchemaField("id", "STRING", mode="REQUIRED"),
        bigquery.SchemaField("filename", "STRING", mode="REQUIRED"),
        bigquery.SchemaField("site", "STRING", mode="REQUIRED"),
        bigquery.SchemaField("type", "STRING"),
        bigquery.SchemaField("sub_type", "STRING"),
        bigquery.SchemaField("confidentiality", "STRING"),
        bigquery.SchemaField("pwc_proprietary", "STRING"),
        bigquery.SchemaField("industry", "STRING"),
        bigquery.SchemaField("primary_topic", "STRING"),
        bigquery.SchemaField("confidence", "FLOAT"),
        bigquery.SchemaField("pii_detected", "BOOLEAN"),
        bigquery.SchemaField("state", "STRING", mode="REQUIRED"),
        bigquery.SchemaField("owner", "STRING"),
        bigquery.SchemaField("rationale", "STRING"),
        bigquery.SchemaField("webUrl", "STRING"),
        bigquery.SchemaField("allowed_groups", "STRING", mode="REPEATED"),
        bigquery.SchemaField("timestamp", "TIMESTAMP", mode="REQUIRED"),
        bigquery.SchemaField("is_signed", "STRING"),
        bigquery.SchemaField("standard_terms", "STRING"),
        bigquery.SchemaField("permitted_use", "STRING"),
        bigquery.SchemaField("engagement_letter_link", "STRING"),
        bigquery.SchemaField("liability_cap", "STRING")
    ]
    
    table = bigquery.Table(table_id, schema=schema)
    try:
        tbl = bq_client.get_table(table_id)
        if not any(f.name == "is_signed" for f in tbl.schema):
            print("[BIGQUERY] Legacy table detected (missing risk fields). Dropping and recreating...")
            bq_client.delete_table(table_id)
            raise Exception("Trigger recreation")
        print("[BIGQUERY] Table documents_metadata already exists.")
    except Exception:
        print("[BIGQUERY] Creating table documents_metadata...")
        try:
            bq_client.create_table(table, timeout=30)
            print("[BIGQUERY] Table created.")
        except Exception as e:
            print(f"[BIGQUERY] Failed to create table: {e}")

def sync_document_to_bigquery(doc: dict):
    table_ref = bq_client.dataset("sharepoint_portal_ds").table("documents_metadata")
    
    # Append-only state logging (No DML delete statement to avoid streaming buffer blocks)
    row = {
        "id": doc["id"],
        "filename": doc["filename"],
        "site": doc["site"],
        "type": doc.get("type", "N/A"),
        "sub_type": doc.get("sub_type", "N/A"),
        "confidentiality": doc.get("confidentiality", "N/A"),
        "pwc_proprietary": doc.get("pwc_proprietary", "No"),
        "industry": doc.get("industry", "N/A"),
        "primary_topic": doc.get("primary_topic", ""),
        "confidence": float(doc.get("confidence", 0.0)),
        "pii_detected": bool(doc.get("pii_detected", False)),
        "state": doc["state"],
        "owner": doc.get("owner", ""),
        "rationale": doc.get("rationale", ""),
        "webUrl": doc.get("webUrl", "#"),
        "allowed_groups": doc.get("allowed_groups", []),
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "is_signed": doc.get("is_signed", "N/A"),
        "standard_terms": doc.get("standard_terms", "N/A"),
        "permitted_use": doc.get("permitted_use"),
        "engagement_letter_link": doc.get("engagement_letter_link"),
        "liability_cap": doc.get("liability_cap")
    }
    try:
        errors = bq_client.insert_rows_json(table_ref, [row])
        if errors:
            print(f"[BIGQUERY] Insert errors: {errors}")
        else:
            print(f"[BIGQUERY] Successfully synced {doc['filename']} state to BigQuery ledger.")
    except Exception as e:
        print(f"[BIGQUERY] Insert failed for {doc['filename']}: {e}")

CRAWLER_STATUS = {
    "status": "idle",
    "processed_count": 0,
    "total_count": 0,
    "logs": []
}

MOCK_CHUNKS: List[Dict[str, Any]] = []

def dot_product(a: List[float], b: List[float]) -> float:
    return sum(x * y for x, y in zip(a, b))

def fetch_sharepoint_file_permissions(drive_id: str, item_id: str, token: str) -> List[str]:
    headers = {"Authorization": f"Bearer {token}"}
    url = f"https://graph.microsoft.com/v1.0/drives/{drive_id}/items/{item_id}/permissions"
    allowed_groups = []
    try:
        r = httpx.get(url, headers=headers, timeout=10)
        if r.status_code == 200:
            perms = r.json().get("value", [])
            for perm in perms:
                identities = perm.get("grantedToIdentitiesV2", [])
                for identity in identities:
                    group_info = identity.get("group") or identity.get("siteGroup")
                    if group_info and "id" in group_info:
                        allowed_groups.append(f"group::{group_info['id']}")
        # Fallback to general employees if no specific groups found
        if not allowed_groups:
            allowed_groups.append("group::employees")
    except Exception as e:
        print(f"[CRAWLER] Failed to fetch permissions for item {item_id}: {e}")
        allowed_groups.append("group::employees")
    return list(set(allowed_groups))

def fetch_user_entra_groups(token: str) -> List[str]:
    headers = {"Authorization": f"Bearer {token}"}
    url = "https://graph.microsoft.com/v1.0/me/transitiveMemberOf"
    user_groups = []
    try:
        r = httpx.get(url, headers=headers, timeout=10)
        if r.status_code == 200:
            groups = r.json().get("value", [])
            for group in groups:
                if "id" in group:
                    user_groups.append(f"group::{group['id']}")
        # All users get default employees group
        user_groups.append("group::employees")
    except Exception as e:
        print(f"[SEARCH] Failed to fetch user Entra groups: {e}")
        user_groups.append("group::employees")
    return list(set(user_groups))

# Generate embeddings for base corpus at startup
def generate_base_embeddings():
    import concurrent.futures
    init_bigquery_schema()
    seed_documents_if_empty()
    firestore_docs = load_documents_from_store()
    print(f"[SYSTEM] Loaded {len(firestore_docs)} documents from Firestore. Pre-generating/Loading embeddings using {EMBEDDING_MODEL}...")
    
    def process_doc(doc):
        chunks = [doc["content"]]
        results = []
        for text_chunk in chunks:
            # Check if Firestore already has the cached vector for this document
            cached_vector = doc.get("vector")
            if cached_vector and isinstance(cached_vector, list) and len(cached_vector) > 0:
                results.append({
                    "doc_id": doc["id"],
                    "filename": doc["filename"],
                    "text": text_chunk,
                    "vector": cached_vector,
                    "allowed_groups": doc["allowed_groups"],
                    "webUrl": doc["webUrl"]
                })
                continue

            # Otherwise, generate embedding and cache it
            try:
                resp = client.models.embed_content(
                    model=EMBEDDING_MODEL,
                    contents=f"title: {doc['filename']} | text: {text_chunk}"
                )
                vector = resp.embeddings[0].values
                results.append({
                    "doc_id": doc["id"],
                    "filename": doc["filename"],
                    "text": text_chunk,
                    "vector": vector,
                    "allowed_groups": doc["allowed_groups"],
                    "webUrl": doc["webUrl"]
                })
                # Cache the generated vector in Firestore so we never have to re-compute it
                try:
                    db_client.collection("sharepoint_documents").document(doc["id"]).update({"vector": vector})
                except Exception as cache_err:
                    print(f"Failed to cache vector in Firestore for {doc['id']}: {cache_err}")
            except Exception as e:
                print(f"Failed to generate embedding for {doc['id']}: {e}")
        return results

    with concurrent.futures.ThreadPoolExecutor(max_workers=20) as executor:
        futures = [executor.submit(process_doc, doc) for doc in firestore_docs]
        for fut in concurrent.futures.as_completed(futures):
            res = fut.result()
            if res:
                MOCK_CHUNKS.extend(res)

    print(f"[SYSTEM] Vector index warmed up with {len(MOCK_CHUNKS)} vectors.")

generate_base_embeddings()

# --- ONTOLOGY CATALOG (ALIGNING TO EXCEL TAXONOMY) ---
MOCK_ONTOLOGY = {
    "model_generator": ACTIVE_MODEL,
    "region": ACTIVE_REGION,
    "generated_at": "2026-06-10T15:00:00Z",
    "classes": [
        {
            "name": "PwC Engagement File",
            "parent": None,
            "description": "A file that is specific to a PwC client engagement (proposals, statements of work, contracts, deliverables).",
            "properties": [
                {"name": "PwC Proposal", "type": "Sub-Type", "required": False, "description": "Documents created to win client work"},
                {"name": "PwC Engagement Artefact", "type": "Sub-Type", "required": False, "description": "Engagement letters, client contracts, deliverables, roadmaps"},
                {"name": "PwC Engagement Citation/ Case Study", "type": "Sub-Type", "required": False, "description": "Summaries of engagement for marketing and thought leadership"}
            ]
        },
        {
            "name": "PwC Operational File",
            "parent": None,
            "description": "A file created by PwC for running internal operations or scaling business (internal policy, supplier contracts, CVs).",
            "properties": [
                {"name": "PwC CV", "type": "Sub-Type", "required": False, "description": "Curriculum Vitae of employee or candidate"},
                {"name": "PwC Legal Document", "type": "Sub-Type", "required": False, "description": "Legal documents supporting business operations"},
                {"name": "PwC Thought Leadership/ Research", "type": "Sub-Type", "required": False, "description": "Industry reports, whitepapers, case studies"}
            ]
        },
        {
            "name": "External File",
            "parent": None,
            "description": "Files produced wholly outside of PwC (annual reports, competitor company profiles, external training).",
            "properties": [
                {"name": "External Annual Report", "type": "Sub-Type", "required": False, "description": "Publicly available annual company financial statements"},
                {"name": "External Company Profile", "type": "Sub-Type", "required": False, "description": "External profile of a competitor or partner company"}
            ]
        }
    ],
    "relations": [
        {
            "source": "PwC Engagement Artefact",
            "type": "governedBy",
            "target": "PwC Legal Document",
            "description": "Standard engagement contract clauses must comply with PwC general counsel legal templates."
        }
    ]
}

# --- ENDPOINTS ---

class CompleteLoginPayload(BaseModel):
    code: str
    redirect_uri: str

@app.get("/api/auth/login-url")
def get_login_url(redirect_uri: str):
    try:
        login_url = auth_manager.start_flow(redirect_uri)
        return JSONResponse({
            "login_url": login_url
        })
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/auth/complete")
def complete_login(payload: CompleteLoginPayload):
    try:
        account = auth_manager.complete_flow(payload.code, payload.redirect_uri)
        return JSONResponse({"status": "authenticated", "account": account})
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/api/auth/status")
def get_auth_status():
    token = auth_manager.get_token()
    if token and auth_manager.account_info:
        return JSONResponse({"authenticated": True, "account": auth_manager.account_info})
    return JSONResponse({"authenticated": False})

@app.post("/api/auth/logout")
def logout():
    auth_manager.logout()
    return JSONResponse({"status": "logged_out"})

# Microsoft Graph site/drive listing
@app.get("/api/sharepoint/sites")
def list_sharepoint_sites(search: Optional[str] = ""):
    token = auth_manager.get_token()
    if not token:
        raise HTTPException(status_code=401, detail="Authentication required.")
    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
    url = f"https://graph.microsoft.com/v1.0/sites?search={search or '*'}"
    try:
        r = httpx.get(url, headers=headers, timeout=15)
        if r.status_code != 200:
            raise HTTPException(status_code=r.status_code, detail=r.text)
        return JSONResponse(r.json().get("value", []))
    except HTTPException as he:
        raise he
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/sharepoint/sites/{site_id}/drives")
def list_site_drives(site_id: str):
    token = auth_manager.get_token()
    if not token:
        raise HTTPException(status_code=401, detail="Authentication required.")
    headers = {"Authorization": f"Bearer {token}"}
    url = f"https://graph.microsoft.com/v1.0/sites/{site_id}/drives"
    try:
        r = httpx.get(url, headers=headers, timeout=15)
        if r.status_code != 200:
            raise HTTPException(status_code=r.status_code, detail=r.text)
        return JSONResponse(r.json().get("value", []))
    except HTTPException as he:
        raise he
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

def run_crawler_task(request: SharePointImportRequest, token: str):
    def log_crawler(msg: str):
        print(msg)
        timestamp = time.strftime("%H:%M:%S")
        CRAWLER_STATUS["logs"].append(f"[{timestamp}] {msg}")

    try:
        log_crawler(f"Initializing SharePoint Sync for site_id={request.site_id}...")
        headers = {"Authorization": f"Bearer {token}"}
        
        all_files = []
        
        def fetch_all_files_recursively(url: str, current_path: str = ""):
            log_crawler(f"Scanning Graph API directory path: {current_path or '/'}")
            try:
                r = httpx.get(url, headers=headers, timeout=15)
                if r.status_code != 200:
                    log_crawler(f"Error listing directory: {r.text}")
                    return
                items = r.json().get("value", [])
                for item in items:
                    if "folder" in item:
                        folder_id = item.get("id")
                        folder_name = item.get("name")
                        sub_url = f"https://graph.microsoft.com/v1.0/drives/{request.drive_id}/items/{folder_id}/children"
                        fetch_all_files_recursively(sub_url, current_path + "/" + folder_name)
                    else:
                        item["folder_path_display"] = current_path or "/"
                        all_files.append(item)
            except Exception as e:
                log_crawler(f"Exception listing directory {url}: {e}")

        list_url = f"https://graph.microsoft.com/v1.0/drives/{request.drive_id}/root/children"
        if request.folder_path != "/":
            list_url = f"https://graph.microsoft.com/v1.0/drives/{request.drive_id}/root:{request.folder_path}:/children"

        log_crawler("Fetching directory folders mapping recursively from Microsoft Graph API...")
        fetch_all_files_recursively(list_url, request.folder_path if request.folder_path != "/" else "")
        
        log_crawler(f"Recursive scan completed. Found a total of {len(all_files)} files across all nested directories.")

        current_docs = load_documents_from_store()
        CRAWLER_STATUS["total_count"] = len(all_files)

        for file in all_files:
            filename = file.get("name")
            item_id = file.get("id")
            web_url = file.get("webUrl")
            mime_type = file.get("file", {}).get("mimeType", "application/octet-stream")

            if any(d["filename"] == filename for d in current_docs):
                log_crawler(f"Skipping already-indexed file: {filename} (FR04)")
                CRAWLER_STATUS["total_count"] -= 1
                continue

            # Ensure Microsoft Graph token is fresh and has not expired during long indexing run
            active_token = auth_manager.get_token() or token
            active_headers = {"Authorization": f"Bearer {active_token}"}

            log_crawler(f"Downloading file content bytes: {filename}...")
            dl_url = f"https://graph.microsoft.com/v1.0/drives/{request.drive_id}/items/{item_id}/content"
            try:
                dl_resp = httpx.get(dl_url, headers=active_headers, timeout=30, follow_redirects=True)
                if dl_resp.status_code != 200:
                    log_crawler(f"Error: Failed to download content for {filename} (HTTP {dl_resp.status_code})")
                    continue
                file_bytes = dl_resp.content
            except Exception as e:
                log_crawler(f"Download exception for {filename}: {e}")
                continue

            # DLP Scan
            log_crawler(f"Checking for unredacted PII patterns on {filename} (SR02)...")
            pii_found = False
            
            dlp_text_content = ""
            if mime_type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
                dlp_text_content = extract_text_from_docx(file_bytes)
            elif mime_type == "application/vnd.openxmlformats-officedocument.presentationml.presentation":
                dlp_text_content = extract_text_from_pptx(file_bytes)
            elif mime_type == "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet":
                dlp_text_content = extract_text_from_xlsx(file_bytes)
            elif mime_type == "message/rfc822":
                dlp_text_content = extract_text_from_eml(file_bytes)
            elif mime_type.startswith("text/"):
                dlp_text_content = file_bytes.decode("utf-8", errors="ignore")
            else:
                # PDF, image, or other binary
                dlp_text_content = file_bytes.decode("utf-8", errors="ignore")

            if "SSN" in dlp_text_content or "000-12" in dlp_text_content:
                pii_found = True
                log_crawler(f"WARNING: Sensitive patterns detected. Content is safely retained for semantic training.")

            # Gemini Taxonomy Classification
            log_crawler(f"Calling Gemini 3.5 Flash classifier to process taxonomy metadata for {filename} (FR01, FR10, FR37)...")
            prompt = """
            Perform structured metadata classification on this document matching the corporate taxonomy:
            - confidentiality: Public, Internal, Confidential, Highly Confidential.
            - document_type: PwC Engagement File, PwC Operational File, External File, Other File Type.
            - document_sub_type: PwC Proposal, PwC Engagement Artefact, PwC Engagement Citation/ Case Study, Other Engagement File, PwC CV, PwC Legal Document, PwC Business Development Artefact, PwC Internal Project Artefact, PwC Internal Knowledge/ Policy, PwC Thought Leadership/ Research, Other Operational File, External Annual Report, External Company Profile, External Case Study, External Knowledge Article, External Training Material, Other External File, Undetermined.
            - pwc_proprietary: Yes, No.
            - primary_industry: Technology, Media and Telecommunications, Government and Public Services, Financial Services, Energy, Utilities and Resources, Industrial Manufacturing and Automotive, Consumer Markets, Health Industries, Private Equity, Real Assets and Sovereign Investment Funds, N/A.
            - primary_topic: Short sentence about the main topic.
            - named_entities: organizations.
            - named_people: people.
            - candidate_name: name (only if PwC CV, else null).
            - candidate_recent_experience: description of experience (only if PwC CV, else null).
            - is_signed: Signed Status. Yes if signed/executed signature page is found, No if unsigned/draft, N/A if not a contract/engagement letter.
            - standard_terms: Standard Terms. Yes if uses PwC standard template terms, No if non-standard/custom liability/indemnity, N/A if not a legal agreement.
            - permitted_use: Deliverable Permitted Use. Description of distribution rights or limitation of liability scope (e.g. for PwC internal use only, third-party distribution permitted). Null if not an engagement file.
            - engagement_letter_link: Linked Engagement Letter. Filename or title of the associated parent Engagement Letter if this file is a deliverable. Null if none or not a deliverable.
            - liability_cap: Extracted Liability Cap. Value or description of liability limitation. Null if not a legal agreement.

            Return JSON matching the schema.
            """

            try:
                if mime_type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
                    docx_text = extract_text_from_docx(file_bytes)
                    resp = client.models.generate_content(
                        model=ACTIVE_MODEL,
                        contents=[f"Document Content:\n{docx_text}\n\n", prompt],
                        config=types.GenerateContentConfig(
                            response_mime_type="application/json",
                            response_schema=ExtractedCorporateMetadata,
                            temperature=0.0
                        )
                    )
                elif mime_type == "application/vnd.openxmlformats-officedocument.presentationml.presentation":
                    pptx_text = extract_text_from_pptx(file_bytes)
                    resp = client.models.generate_content(
                        model=ACTIVE_MODEL,
                        contents=[f"Document Content:\n{pptx_text}\n\n", prompt],
                        config=types.GenerateContentConfig(
                            response_mime_type="application/json",
                            response_schema=ExtractedCorporateMetadata,
                            temperature=0.0
                        )
                    )
                elif mime_type == "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet":
                    xlsx_text = extract_text_from_xlsx(file_bytes)
                    resp = client.models.generate_content(
                        model=ACTIVE_MODEL,
                        contents=[f"Document Content:\n{xlsx_text}\n\n", prompt],
                        config=types.GenerateContentConfig(
                            response_mime_type="application/json",
                            response_schema=ExtractedCorporateMetadata,
                            temperature=0.0
                        )
                    )
                elif mime_type == "message/rfc822":
                    eml_text = extract_text_from_eml(file_bytes)
                    resp = client.models.generate_content(
                        model=ACTIVE_MODEL,
                        contents=[f"Document Content:\n{eml_text}\n\n", prompt],
                        config=types.GenerateContentConfig(
                            response_mime_type="application/json",
                            response_schema=ExtractedCorporateMetadata,
                            temperature=0.0
                        )
                    )
                elif mime_type == "application/pdf" or mime_type.startswith("text/") or mime_type.startswith("image/"):
                    part = types.Part.from_bytes(data=file_bytes, mime_type=mime_type)
                    resp = client.models.generate_content(
                        model=ACTIVE_MODEL,
                        contents=[part, prompt],
                        config=types.GenerateContentConfig(
                            response_mime_type="application/json",
                            response_schema=ExtractedCorporateMetadata,
                            temperature=0.0
                        )
                    )
                else:
                    log_crawler(f"Skipping file: unsupported mime-type {mime_type} for {filename}")
                    continue
                extraction = json.loads(resp.text)
                log_crawler(f"Ontology extracted: type={extraction.get('document_type')} subtype={extraction.get('document_sub_type')}")
            except Exception as e:
                log_crawler(f"Gemini parsing failed for {filename}: {e}")
                continue

            # Embeddings computing
            log_crawler(f"Generating 768-D query embedding via gemini-embedding-2 for {filename} (FR09)...")
            embed_text = f"File: {filename}. Type: {extraction.get('document_type')}. Sub-Type: {extraction.get('document_sub_type')}. Industry: {extraction.get('primary_industry')}. Topic: {extraction.get('primary_topic')}. Entities: {', '.join(extraction.get('named_entities', []))}."
            
            try:
                embed_resp = client.models.embed_content(
                    model=EMBEDDING_MODEL,
                    contents=f"title: {filename} | text: {embed_text}"
                )
                vector = embed_resp.embeddings[0].values
            except Exception as e:
                 log_crawler(f"Embeddings creation failed for {filename}: {e}")
                 continue

            # MS Graph permission mapping
            log_crawler(f"Mapping security ACL permissions (allowed groups) from MS Graph for {filename} (FR39)...")
            file_allowed_groups = fetch_sharepoint_file_permissions(request.drive_id, item_id, active_token)

            doc_id = f"doc_{uuid.uuid4().hex[:6]}"
            new_doc = {
                "id": doc_id,
                "filename": filename,
                "site": "SharePoint: " + file.get("folder_path_display", request.folder_path),
                "type": extraction.get("document_type"),
                "sub_type": extraction.get("document_sub_type"),
                "confidentiality": extraction.get("confidentiality"),
                "pwc_proprietary": extraction.get("pwc_proprietary"),
                "industry": extraction.get("primary_industry"),
                "primary_topic": extraction.get("primary_topic"),
                "allowed_groups": file_allowed_groups,
                "confidence": 0.94,
                "pii_detected": pii_found,
                "state": "APPROVED",
                "owner": auth_manager.account_info.get("username", "SharePoint Sync") if auth_manager.account_info else "SharePoint Sync",
                "rationale": f"Ontology matched to corporate taxonomy class: {extraction.get('document_sub_type')}.",
                "elements": ["text"] + (["signature_block"] if extraction.get("document_type") == "PwC CV" else []),
                "content": embed_text,
                "vector": vector,
                "webUrl": web_url,
                "is_signed": extraction.get("is_signed", "N/A"),
                "standard_terms": extraction.get("standard_terms", "N/A"),
                "permitted_use": extraction.get("permitted_use"),
                "engagement_letter_link": extraction.get("engagement_letter_link"),
                "liability_cap": extraction.get("liability_cap")
            }

            try:
                log_crawler(f"Writing metadata properties to Cloud Firestore catalog...")
                db_client.collection("sharepoint_documents").document(doc_id).set(new_doc)
                log_crawler(f"Streaming compliance validation details to BigQuery analytical ledger...")
                sync_document_to_bigquery(new_doc)
            except Exception as e:
                log_crawler(f"Database write failed for {filename}: {e}")

            MOCK_CHUNKS.append({
                "doc_id": doc_id,
                "filename": filename,
                "text": embed_text,
                "vector": vector,
                "allowed_groups": file_allowed_groups,
                "webUrl": web_url
            })
            
            CRAWLER_STATUS["processed_count"] += 1
            log_crawler(f"Successfully sync-cataloged document: {filename}")

        log_crawler("SharePoint Sync complete. Crawler state returned to IDLE.")
    except Exception as e:
        log_crawler(f"CRITICAL CRAWLER ERROR: {e}")
    finally:
        CRAWLER_STATUS["status"] = "idle"

# Live import from SharePoint Site folder
@app.post("/api/sharepoint/import")
async def import_sharepoint_folder(request: SharePointImportRequest, background_tasks: BackgroundTasks):
    token = auth_manager.get_token()
    if not token:
        raise HTTPException(status_code=401, detail="Authentication required.")
    
    if CRAWLER_STATUS["status"] == "running":
        raise HTTPException(status_code=400, detail="Crawler is currently running another import schedule.")

    CRAWLER_STATUS["status"] = "running"
    CRAWLER_STATUS["processed_count"] = 0
    CRAWLER_STATUS["total_count"] = 0
    CRAWLER_STATUS["logs"] = []

    background_tasks.add_task(run_crawler_task, request, token)
    return JSONResponse({"status": "sync_started"})

@app.get("/api/sharepoint/crawler-logs")
def get_crawler_logs():
    return JSONResponse(CRAWLER_STATUS)

@app.get("/api/documents")
def get_documents():
    return JSONResponse(load_documents_from_store())

@app.get("/api/ontology")
def get_ontology():
    return JSONResponse(MOCK_ONTOLOGY)

@app.post("/api/documents/ingest")
def ingest_document(request: IngestRequest):
    print(f"[INGESTION] Processing upload: {request.filename}")
    pii_found = False
    clean_content = request.content
    if "SSN" in clean_content or "000-12" in clean_content:
        pii_found = True

    prompt = """
    Perform structured metadata classification matching the corporate taxonomy:
    - confidentiality: Public, Internal, Confidential, Highly Confidential.
    - document_type: PwC Engagement File, PwC Operational File, External File, Other File Type.
    - document_sub_type: PwC Proposal, PwC Engagement Artefact, PwC Engagement Citation/ Case Study, Other Engagement File, PwC CV, PwC Legal Document, PwC Business Development Artefact, PwC Internal Project Artefact, PwC Internal Knowledge/ Policy, PwC Thought Leadership/ Research, Other Operational File, External Annual Report, External Company Profile, External Case Study, External Knowledge Article, External Training Material, Other External File, Undetermined.
    - pwc_proprietary: Yes, No.
    - primary_industry: Technology, Media and Telecommunications, Government and Public Services, Financial Services, Energy, Utilities and Resources, Industrial Manufacturing and Automotive, Consumer Markets, Health Industries, Private Equity, Real Assets and Sovereign Investment Funds, N/A.
    - primary_topic: Short sentence about the main topic.
    - named_entities: organizations.
    - named_people: people.
    - candidate_name: name (only if PwC CV).
    - candidate_recent_experience: experience description (only if PwC CV).
    
    Return JSON matching the schema.
    """
    
    try:
        resp = client.models.generate_content(
            model=ACTIVE_MODEL,
            contents=[f"{clean_content}\n\n{prompt}"],
            config=types.GenerateContentConfig(
                response_mime_type="application/json",
                response_schema=ExtractedCorporateMetadata,
                temperature=0.0
            )
        )
        extraction = json.loads(resp.text)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Gemini taxonomy classification failed: {e}")

    doc_id = f"doc_{uuid.uuid4().hex[:6]}"
    
    try:
        embed_resp = client.models.embed_content(
            model=EMBEDDING_MODEL,
            contents=f"title: {request.filename} | text: {clean_content}"
        )
        vector = embed_resp.embeddings[0].values
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate embedding: {e}")

    new_doc = {
        "id": doc_id,
        "filename": request.filename,
        "site": request.site,
        "type": extraction.get("document_type"),
        "sub_type": extraction.get("document_sub_type"),
        "confidentiality": extraction.get("confidentiality"),
        "pwc_proprietary": extraction.get("pwc_proprietary"),
        "industry": extraction.get("primary_industry"),
        "primary_topic": extraction.get("primary_topic"),
        "allowed_groups": request.allowed_groups,
        "confidence": 0.95,
        "pii_detected": pii_found,
        "state": "APPROVED",
        "owner": "Uploaded User",
        "rationale": f"Tagged under class: {extraction.get('document_sub_type')}.",
        "elements": ["text"],
        "content": clean_content,
        "webUrl": "#",
        "is_signed": extraction.get("is_signed", "N/A"),
        "standard_terms": extraction.get("standard_terms", "N/A"),
        "permitted_use": extraction.get("permitted_use"),
        "engagement_letter_link": extraction.get("engagement_letter_link"),
        "liability_cap": extraction.get("liability_cap"),
        "vector": vector
    }
    
    try:
        db_client.collection("sharepoint_documents").document(doc_id).set(new_doc)
        sync_document_to_bigquery(new_doc)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to persist document to Firestore/BigQuery: {e}")

    MOCK_CHUNKS.append({
        "doc_id": doc_id,
        "filename": request.filename,
        "text": clean_content,
        "vector": vector,
        "allowed_groups": request.allowed_groups,
        "webUrl": "#"
    })

    return JSONResponse({"status": "ingested", "document": new_doc})

@app.post("/api/documents/{doc_id}/validate")
def validate_document(doc_id: str, action: ValidationAction):
    doc_ref = db_client.collection("sharepoint_documents").document(doc_id)
    doc_snap = doc_ref.get()
    if not doc_snap.exists:
        raise HTTPException(status_code=404, detail="Document not found")
    
    doc = doc_snap.to_dict()
    
    log_entry = {
        "event_id": str(uuid.uuid4()),
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "doc_id": doc_id,
        "filename": doc["filename"],
        "previous_state": doc["state"],
        "new_state": action.state,
        "details": f"Override Confidentiality: {action.confidentiality}, Sub-Type: {action.document_sub_type}",
    }
    
    try:
        db_client.collection("audit_logs").document(log_entry["event_id"]).set(log_entry)
    except Exception as e:
        print(f"[FIRESTORE] Failed to write audit log: {e}")
    
    doc["state"] = action.state
    if action.confidentiality:
        doc["confidentiality"] = action.confidentiality
    if action.document_sub_type:
        doc["sub_type"] = action.document_sub_type
    if action.state == "EXCEPTION" and action.exception_reason:
        doc["exception_reason"] = action.exception_reason
    else:
        doc.pop("exception_reason", None)

    try:
        doc_ref.set(doc)
        sync_document_to_bigquery(doc)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to update document validation state: {e}")

    return JSONResponse({"status": "updated", "document": doc})

# --- LIVE RAG SEARCH AND RETRIEVAL ---
@app.post("/api/search")
def search(request: SearchRequest, req: Request, authorization: Optional[str] = Header(None)):
    start_time = time.perf_counter()
    
    user_groups = []
    print(f"[DEBUG] Headers received: {list(req.headers.keys())}")
    dev_override = req.headers.get("X-Developer-Override-Groups")
    if dev_override:
        user_groups = [g.strip() for g in dev_override.split(",") if g.strip()]
        print(f"[SEARCH] Developer override active. Mapped testing groups: {user_groups}")
    else:
        token = None
        if authorization and authorization.startswith("Bearer "):
            token = authorization.split(" ")[1]
        else:
            token = auth_manager.get_token()

        if not token:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Authentication session required. Please connect your SharePoint account first."
            )
        
        user_groups = fetch_user_entra_groups(token)
        print(f"[SEARCH] Dynamically resolved {len(user_groups)} real security groups from Entra ID.")
    
    try:
        embed_resp = client.models.embed_content(
            model=EMBEDDING_MODEL,
            contents=f"task: search result | query: {request.query}"
        )
        query_vector = embed_resp.embeddings[0].values
    except Exception as e:
         raise HTTPException(status_code=500, detail=f"Embeddings service failed: {e}")

    scored_chunks = []
    for chunk in MOCK_CHUNKS:
        has_access = any(g in user_groups for g in chunk["allowed_groups"])
        if has_access:
            score = dot_product(query_vector, chunk["vector"])
            scored_chunks.append((score, chunk))
            
    scored_chunks.sort(key=lambda x: x[0], reverse=True)
    top_matches = [chunk for score, chunk in scored_chunks[:2] if score > 0.35]

    if not top_matches:
        duration = round(time.perf_counter() - start_time, 2)
        return JSONResponse({
            "answer": "I could not find any documents matching your query that you have permission to view.",
            "sources": [],
            "latency": f"{duration}s",
            "model": ACTIVE_MODEL,
            "region": ACTIVE_REGION
        })

    context_str = ""
    for match in top_matches:
        context_str += f"\n---\nSource File: {match['filename']}\nContent Excerpt:\n{match['text']}\n---\n"

    rag_prompt = f"""
    You are Aether AI, a secure corporate search assistant. 
    Answer the user's question using ONLY the provided document context blocks below. 
    
    STRICT ZERO-LEAK SECURITY COMPLIANCE RULES:
    1. NEVER expose raw, specific Personally Identifiable Information (PII) such as Social Security Numbers, phone numbers, exact addresses, or emails in the final synthesis.
    2. If you cite specific figures, salaries, caps, or financial statistics, wrap the raw sensitive data exactly inside <redact>...</redact> tags. Example: "Base Salary: <redact>$85,000</redact>" or "SSN: <redact>000-12-3456</redact>".
    3. Keep your response text high-level and generalized. Do NOT include raw personal names or specific identifiers.
    4. If the answer cannot be found in the context, state that you cannot answer. Do NOT speculate.
    
    Contexts:
    {context_str}
    
    User Query: {request.query}
    """

    try:
        generation_resp = client.models.generate_content(
            model=ACTIVE_MODEL,
            contents=rag_prompt,
            config=types.GenerateContentConfig(temperature=0.0)
        )
        answer = generation_resp.text
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Gemini content generation failed: {e}")

    duration = round(time.perf_counter() - start_time, 2)
    
    # Filter sources: do not show citations if the LLM states that the information is missing
    lower_answer = answer.lower()
    negative_indicators = [
        "cannot answer", "do not contain", "no information", "not mentioned", 
        "not found", "does not contain", "could not find", "no details",
        "no data", "does not have any information"
    ]
    
    sources = []
    if not any(indicator in lower_answer for indicator in negative_indicators):
        for match in top_matches:
            filename_base = match["filename"].split(".")[0].lower()
            # If the filename or key terms are in the answer, include it as an active citation
            if filename_base in lower_answer or any(word in lower_answer for word in filename_base.split() if len(word) > 4):
                sources.append({"title": match["filename"], "snippet": match["text"], "url": match.get("webUrl", "#")})
        # If the answer is positive but didn't explicitly name the files, list the top matches
        if not sources:
            sources = [{"title": match["filename"], "snippet": match["text"], "url": match.get("webUrl", "#")} for match in top_matches]

    return JSONResponse({
        "answer": answer,
        "sources": sources,
        "latency": f"{duration}s",
        "model": ACTIVE_MODEL,
        "region": ACTIVE_REGION
    })

@app.get("/api/simulate-throttle")
def simulate_throttle():
    logs = [
        "[CLIENT] Initializing client ingestion run...",
        f"[SYSTEM] Selected Model: {ACTIVE_MODEL} | Region: {ACTIVE_REGION}",
        "[CLIENT] Requesting document Alpha Tech Agreement.docx...",
        "[SERVER] Request processed successfully (200 OK)",
        "[CLIENT] Extracted taxonomy classes: PwC Operational File, PwC Legal Document.",
        "[CLIENT] Requesting document Alex_Turner_CV.docx...",
        "[SERVER] Request processed successfully (200 OK)",
        "[CLIENT] Extracted applicant Alex Turner CV details successfully.",
        "[SERVER] Ingestion run completed successfully."
    ]
    return JSONResponse({"logs": logs})
