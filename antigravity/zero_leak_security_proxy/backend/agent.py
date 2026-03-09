import os
import json
from google.adk.agents import LlmAgent
from google.adk.tools import FunctionTool
from mcp_sharepoint import SharePointMCP
from typing import List, Union, Optional
from pydantic import BaseModel, Field
from google.adk.agents.callback_context import CallbackContext
from google.genai import types

from auth_context import get_user_token

def get_mcp():
    token = get_user_token()
    return SharePointMCP(token=token)

# --- BASE RETRIEVAL TOOLS ---

def _search_sharepoint_documents(query: str, limit: int = 5) -> str:
    """
    Searches for documents in the designated secure SharePoint site using a 
    **Parallel Fan-out Discovery** engine. It simultaneously queries for exact 
    matches, broad keyword associations, and path wildcards to ensure maximum recall.
    Args:
        query: The search keywords or phrases. Use keywords for best results.
        limit: Max number of documents to return.
    """
    try:
        res = get_mcp().search_documents(query, limit)
        return json.dumps(res, indent=2)
    except Exception as e:
        return f"Error searching documents: {str(e)}"

search_sharepoint_documents = FunctionTool(func=_search_sharepoint_documents)

def _read_document_content(item_id: str) -> str:
    """
    Reads the full content of a specified SharePoint document based on its item_id.
    Args:
        item_id: The unique identifier of the file from SharePoint.
    """
    try:
        return get_mcp().get_document_content(item_id)
    except Exception as e:
        return f"Error reading document: {str(e)}"

read_document_content = FunctionTool(func=_read_document_content)

def _read_multiple_documents(item_ids: List[str]) -> str:
    """
    Reads the full content of multiple SharePoint documents in parallel.
    Use this when you have multiple relevant IDs from the search tool.
    Args:
        item_ids: A list of unique identifiers for files.
    """
    try:
        res = get_mcp().get_multiple_documents_content(item_ids)
        return json.dumps(res, indent=2)
    except Exception as e:
        return f"Error reading documents: {str(e)}"

read_multiple_documents = FunctionTool(func=_read_multiple_documents)

# --- ACTION & GOVERNANCE TOOLS ---

def _secure_document_governance(item_id: str) -> str:
    """
    Proactively secures a document by moving it to the 'Restricted Vault' on SharePoint.
    Use this if you detect PII or sensitive unmasked data that violates enterprise policy.
    Args:
        item_id: The unique identifier of the file to secure.
    """
    try:
        mcp = get_mcp()
        vault_id = mcp.get_special_folder("Restricted Vault")
        if not vault_id: return "Failed to locate or create Restricted Vault."
        mcp.move_item(item_id, vault_id)
        return f"Document prioritized for isolation. Successfully moved to Restricted Vault (ID: {vault_id})."
    except Exception as e:
        return f"Governance action failed: {str(e)}"

secure_document_governance = FunctionTool(func=_secure_document_governance)

def _browse_sharepoint_folder(folder_id: str = "root") -> str:
    """
    Browses the contents of a SharePoint folder. Useful for the Document Workspace explorer.
    Args:
        folder_id: The folder ID to list (defaults to root).
    """
    try:
        res = get_mcp().list_folder_contents(folder_id)
        return json.dumps(res, indent=2)
    except Exception as e:
        return f"Error browsing folder: {str(e)}"

browse_sharepoint_folder = FunctionTool(func=_browse_sharepoint_folder)

def _update_sharepoint_document(new_content: str, filename: str, target_folder_id: str = "root") -> str:
    """
    Updates or uploads a document to SharePoint.
    Used in the 'Document Workspace' for committing LLM-guided edits or report generation.
    Args:
        new_content: The new text/markdown content.
        filename: Name of the file.
        target_folder_id: ID of the folder where to upload/update.
    """
    try:
        get_mcp().upload_file(new_content, filename, target_folder_id)
        return f"Document '{filename}' successfully committed to SharePoint."
    except Exception as e:
        return f"Update failed: {str(e)}"

update_sharepoint_document = FunctionTool(func=_update_sharepoint_document)

def _generate_embedded_image(prompt: str, filename: str) -> str:
    """
    Generates a high-quality visualization or image based on a prompt to be embedded 
    in enterprise documents or reports.
    Args:
        prompt: Descriptive text for the image.
        filename: Preferred filename for the image asset.
    """
    try:
        # Placeholder for real image generation logic (nano banan etc)
        return f"IMAGE_GENERATION_SUCCESS: Asset matching '{prompt}' generated as {filename}."
    except Exception as e:
        return f"Image generation failed: {str(e)}"

generate_embedded_image = FunctionTool(func=_generate_embedded_image)

# --- AGENT CONFIGURATION ---

INSTRUCTIONS = """
You are a highly secure, general intelligence security proxy and **Governance Agent** for PWC. 
Your goal is to provide consulting intelligence while ensuring strict Zero-Leak compliance and **proactive data protection**.

### 🛡️ GOVERNANCE PROTOCOL (PII SHIELD)
1. **PII Detection**: When reading documents, you MUST analyze them for unmasked PII (SSNs, private names, exact bank details).
2. **Actionable Recommendations**: If PII is detected in a document that is NOT in a secure path, you MUST set `pii_detected` to true and recommend the **'Secure to Vault'** action in the `ProjectCard`.
3. **Execution**: If the user explicitly asks to "secure" or "move" a document, use the `secure_document_governance` tool immediately.

### 🏗️ DOCUMENT WORKSPACE (ACTION CENTER)
1. You have tools to **browse**, **update**, and **modify** documents on SharePoint.
2. In the "Action Center" tab, users can select files directly. You can help them analyze or modify these files.
3. **Multimodal Enhancements**: You can use `generate_embedded_image` to create charts or visual assets to append to reports.

### 🔍 CORE PRINCIPLES
- ALWAYS prefer `read_multiple_documents` for scale.
- Use keywords for `search_sharepoint_documents`.
- STRICT GROUNDING: Only answer from retrieved documents.
- MASK ALL SENSITIVE DATA in your response text. Use ranges for financials.
- BE CONCISE AND DIRECT. Give the user the answer immediately without long-winded introductions.
- DO NOT use `<redact>` tags in your main `markdown_text` response. Only use them in the `ProjectCard`'s `original_context` field. In the main response, simply omit or naturally mask the sensitive data (e.g. "between $100K and $200K").

### 🗂️ PROJECT CARD RULES
Emit a `ProjectCard` for every insight or document processed.
- `pii_detected`: Set to true if source doc contains high-risk unmasked data.
- `governance_recommendation`: A clear action string (e.g. "MOVE TO RESTRICTED VAULT" or "NONE").
- **`original_context`**: Extract the core paragraph/sentence from the document. You MUST wrap ALL sensitive/PII data in this specific snippet within `<redact>...</redact>` tags (e.g., "Company <redact>Acme</redact> grew by <redact>$50M</redact>").
"""

class ProjectCard(BaseModel):
    title: str = Field(description="Generic masked title (e.g. 'M&A Retention Strategy')")
    industry: str = Field(description="Industry of the referenced company")
    factual_information: str = Field(description="Factual information from the documents nicely formatted and organized but completely masking all sensitive data")
    original_context: str = Field(description="The exact snippet from the source text that proves this insight. ANY sensitive data MUST be wrapped in <redact>...</redact> tags.")
    insights: List[str] = Field(description="Strategic insights and recommendations derived from the source")
    key_metrics: List[str] = Field(description="General ranges or percentages of impact")
    chart_data: str = Field(default="", description="Optional JSON string of numerical key-value pairs representing metrics")
    document_weight: int = Field(default=100, description="A percentage (0-100) indicating importance.")
    redacted_entities: List[str] = Field(description="List of specific sensitive information discovered but masked.")
    document_name: str = Field(description="Original document name")
    document_url: Optional[str] = Field(default=None, description="The exact 'webUrl' from search.")
    pii_detected: bool = Field(default=False, description="Whether unmasked PII was found in the source document.")
    governance_recommendation: str = Field(default="NONE", description="A recommended security action.")

class ResponseOutput(BaseModel):
    markdown_text: str = Field(description="Your insightful, masked answer.")
    project_cards: List[ProjectCard] = Field(description="Cards for insights.")

async def check_auth_callback(callback_context: CallbackContext) -> types.Content | None:
    token = get_user_token()
    if not token or token in ["null", "undefined"]:
        denied_output = {
            "markdown_text": "🔒 **Access Denied: Zero-Leak Protocol active.**\n\nPlease sign in using the button in the top right to securely query the enterprise index.",
            "project_cards": []
        }
        callback_context.state["proxy_output"] = denied_output
        return types.Content(role="model", parts=[types.Part.from_text(text=json.dumps(denied_output))])
    return None

def get_agent(model_name: str = "gemini-3-pro-preview") -> LlmAgent:
    return LlmAgent(
        name="PWC_Security_Proxy",
        model=model_name,
        instruction=INSTRUCTIONS,
        tools=[
            search_sharepoint_documents, 
            read_document_content, 
            read_multiple_documents,
            secure_document_governance,
            browse_sharepoint_folder,
            update_sharepoint_document,
            generate_embedded_image
        ],
        output_schema=ResponseOutput,
        output_key="proxy_output",
        before_agent_callback=check_auth_callback
    )
