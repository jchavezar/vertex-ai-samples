import os
import json
import logging
from typing import List, Optional

from pydantic import BaseModel, Field
from fastmcp import FastMCP

from mcp_service.mcp_sharepoint import SharePointMCP
from utils.auth_context import get_user_token

# Configure standard production-ready logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger("mcp_server")

# Initialize MCP Server (Standard Style for Production Reusability)
mcp = FastMCP("Security-Proxy-MCP")

# --- SCHEMAS ---

class ProjectCard(BaseModel):
    title: str = Field(description="Generic masked title (e.g. 'M&A Retention Strategy')")
    industry: str = Field(description="Industry of the referenced company")
    factual_information: str = Field(description="Factual information from the documents")
    original_context: str = Field(
        description="Exact source snippet containing the PII/Financials. You MUST wrap any sensitive PII or specific numbers in <redact> tags, e.g., <redact>$600,000</redact>."
    )
    insights: List[str] = Field(description="Strategic recommendations")
    key_metrics: List[str] = Field(description="Impact metrics")
    chart_data: str = Field(default="", description="Optional JSON metrics")
    document_weight: int = Field(default=100, description="Importance (0-100)")
    redacted_entities: List[str] = Field(description="List of masked entities")
    document_name: str = Field(description="Filename")
    document_url: Optional[str] = Field(default=None, description="Web URL")
    pii_detected: bool = Field(default=False, description="PII found status")
    governance_recommendation: str = Field(default="NONE", description="Security action")


@mcp.resource("schema://project-card")
def get_project_card_schema() -> str:
    """Returns the JSON schema for the Zero-Leak ProjectCard."""
    return json.dumps(ProjectCard.model_json_schema(), indent=2)


# --- PROMPTS ---

GOVERNANCE_INSTRUCTIONS = """
You are a highly secure Governance Agent for PWC. 
STRICT GROUNDING: Only answer from retrieved documents.
ZERO-LEAK PROTOCOL: All sensitive data (exact salaries, project dates, specific financial figures, PII) MUST be fuzzed or approximated in the main chat synthesis. Provide "close" representative values or ranges, never the exact figures found in the source documents.
"""

@mcp.prompt()
def governance_persona(context: str = "") -> str:
    """Exports the official PWC Governance persona."""
    return f"{GOVERNANCE_INSTRUCTIONS}\n\nContext: {context}"


# --- MCP CLIENT HELPER ---

def _get_sharepoint() -> SharePointMCP:
    """Instantiates a securely scoped SharePoint client using the current request token."""
    token = get_user_token()
    return SharePointMCP(token=token)


# --- TOOLS ---

@mcp.tool()
def search_documents(query: str, limit: int = 5) -> str:
    """
    Searches for documents in the designated secure SharePoint site using a 
    **Parallel Fan-out Discovery** engine. It simultaneously queries for exact 
    matches, broad keyword associations, and path wildcards to ensure maximum recall.
    
    Args:
        query: The search keywords or phrases. Use keywords for best results.
        limit: Max number of documents to return.
    """
    logger.info(f"[MCP TOOL] search_documents | Query: '{query}' | Limit: {limit}")
    try:
        results = _get_sharepoint().search_documents(query, limit)
        logger.info(f"[MCP TOOL] search_documents | Success | Found: {len(results)} results.")
        return json.dumps(results, indent=2)
    except Exception as e:
        logger.error(f"[MCP TOOL] search_documents | FAILED: {str(e)}")
        return f"Error searching SharePoint: {str(e)}"

@mcp.tool()
def emit_project_card(
    title: str,
    industry: str,
    factual_information: str,
    original_context: str,
    insights: List[str],
    key_metrics: List[str],
    document_name: str,
    document_url: Optional[str] = None,
    redacted_entities: Optional[List[str]] = None
) -> str:
    """
    Standard tool to emit a structured finding card to the frontend.
    Call this whenever you find a significant document or insight that deserves a dedicated UI card.
    
    IMPORTANT LATENCY RULE: Whenever possible, you MUST emit ALL discovered project cards in parallel via a single batch of parallel tool calls. Do NOT emit them one by one sequentially.
    
    DATA MASKING RULE: When providing `original_context` for a project card, you MUST wrap ALL sensitive/PII data in `<redact>...</redact>` tags exactly as it appears in the source, so the UI can apply the redacted hover effect. Example: "Company <redact>Acme</redact> grew by <redact>$50M</redact>".
    """
    logger.info(f"[MCP TOOL] emit_project_card | Document: '{document_name}'")
    # This tool's presence allows the agent to send structured data while still streaming text.
    # The backend main.py will intercept this and yield it as a 'project_card' event.
    return "SUCCESS: Project card queued for frontend display."

@mcp.tool()
def read_document_content(item_id: str) -> str:
    """
    Reads the full text content of a specified SharePoint document.
    
    Args:
        item_id: The unique identifier for the file in SharePoint.
    """
    logger.info(f"[MCP TOOL] read_document_content | Item ID: {item_id}")
    try:
        return _get_sharepoint().get_document_content(item_id)
    except Exception as e:
        logger.error(f"[MCP TOOL] read_document_content | FAILED: {str(e)}")
        return f"Error reading document: {str(e)}"

@mcp.tool()
def read_multiple_documents(item_ids: List[str]) -> str:
    """
    Reads the full content of multiple SharePoint documents in parallel.
    Use this when you have multiple relevant IDs from the search tool. This is 
    much faster than calling read_document_content sequentially on each ID.
    
    Args:
        item_ids: A list of unique identifiers for files.
    """
    logger.info(f"[MCP TOOL] read_multiple_documents | Item Count: {len(item_ids)}")
    try:
        results = _get_sharepoint().get_multiple_documents_content(item_ids)
        return json.dumps(results, indent=2)
    except Exception as e:
        logger.error(f"[MCP TOOL] read_multiple_documents | FAILED: {str(e)}")
        return f"Error reading multiple documents: {str(e)}"

@mcp.tool()
def secure_document_governance(item_id: str) -> str:
    """
    Proactively secures a document by moving it to the 'Restricted Vault'.
    
    Args:
        item_id: The unique identifier for the file in SharePoint.
    """
    logger.info(f"[MCP TOOL] secure_document_governance | Item ID: {item_id}")
    try:
        sp = _get_sharepoint()
        vault_id = sp.get_special_folder("Restricted Vault")
        if not vault_id:
            logger.warning("[MCP TOOL] secure_document_governance | FAILED: Vault not found.")
            return "Failed to locate or create Restricted Vault."
        
        sp.move_item(item_id, vault_id)
        logger.info(f"[MCP TOOL] secure_document_governance | Success | Vault ID: {vault_id}")
        return f"Document successfully moved to Restricted Vault (ID: {vault_id})."
    except Exception as e:
        logger.error(f"[MCP TOOL] secure_document_governance | FAILED: {str(e)}")
        return f"Governance action failed: {str(e)}"

@mcp.tool()
def browse_sharepoint_folder(folder_id: str = "root") -> str:
    """
    Lists the contents of a SharePoint folder.
    
    Args:
        folder_id: The unique identifier of the folder (default: 'root').
    """
    logger.info(f"[MCP TOOL] browse_sharepoint_folder | Folder ID: {folder_id}")
    try:
        results = _get_sharepoint().list_folder_contents(folder_id)
        return json.dumps(results, indent=2)
    except Exception as e:
        logger.error(f"[MCP TOOL] browse_sharepoint_folder | FAILED: {str(e)}")
        return f"Error browsing folder: {str(e)}"

@mcp.tool()
def update_sharepoint_document(new_content: str, filename: str, target_folder_id: str = "root") -> str:
    """
    Updates or uploads a document to SharePoint.
    
    Args:
        new_content: The text content to write into the document.
        filename: The desired name of the file.
        target_folder_id: The folder to place the file in (default: 'root').
    """
    logger.info(f"[MCP TOOL] update_sharepoint_document | Filename: '{filename}'")
    try:
        _get_sharepoint().upload_file(new_content, filename, target_folder_id)
        logger.info("[MCP TOOL] update_sharepoint_document | Success")
        return f"Document '{filename}' successfully committed to SharePoint."
    except Exception as e:
        logger.error(f"[MCP TOOL] update_sharepoint_document | FAILED: {str(e)}")
        return f"Update failed: {str(e)}"

@mcp.tool()
def generate_embedded_image(query: str, filename: Optional[str] = None, limit: int = 5) -> str:
    """
    Generates a high-quality visualization or image based on a query prompt.
    
    Args:
        query: The visual description or generation prompt.
        filename: Optional desired filename for the asset.
        limit: Number of variants (default 5).
    """
    actual_filename = filename or f"viz_{hash(query) % 10000}.png"
    logger.info(f"[MCP TOOL] generate_embedded_image | Query: '{query}'")
    return f"IMAGE_GENERATION_SUCCESS: Asset matching '{query}' generated as {actual_filename}. [MOCK]"


if __name__ == "__main__":
    # In Production: Run as SSE server (e.g. for Cloud Run)
    # For Local Dev: Runner/Agent will invoke via stdio (default)
    if os.environ.get("TRANSPORT") == "sse":
        from starlette.middleware import Middleware
        from starlette.middleware.cors import CORSMiddleware
        port = int(os.environ.get("PORT", 8088))
        middleware = [
            Middleware(
                CORSMiddleware,
                allow_origins=["*"],
                allow_credentials=True,
                allow_methods=["*"],
                allow_headers=["*"]
            )
        ]
        mcp.run(transport="sse", port=port, host="0.0.0.0", middleware=middleware)
    else:
        # Default to stdio for ADK MCPToolset.from_server local calls
        mcp.run()
