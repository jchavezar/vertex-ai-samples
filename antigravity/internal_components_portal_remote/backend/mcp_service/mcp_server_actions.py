import os
import json
import logging
from typing import List, Optional

from pydantic import BaseModel, Field
from fastmcp import FastMCP

from mcp_service.mcp_sharepoint import SharePointMCP
from utils.auth_context import get_user_token
from utils.internal_renderer import render_report
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger("mcp_server_actions")

mcp = FastMCP("Security-Proxy-Actions-MCP")

# --- PROMPTS ---
ACTION_INSTRUCTIONS = """
You are a highly secure Action Agent for Internal. 
Your role is exclusively to perform actions such as generating reports, creating PDFs, or updating documents.
You do not search for information. You rely on the user to provide the necessary information.
"""

@mcp.prompt()
def action_persona(context: str = "") -> str:
    """Exports the official Internal Action persona."""
    return f"{ACTION_INSTRUCTIONS}\n\nContext: {context}"

def _get_sharepoint() -> SharePointMCP:
    token = get_user_token()
    return SharePointMCP(token=token)

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
        url = _get_sharepoint().upload_file(new_content, filename, target_folder_id)
        logger.info(f"[MCP TOOL] update_sharepoint_document | Success | URL: {url}")
        return f"Document '{filename}' successfully saved/updated at: {url}"
    except Exception as e:
        logger.error(f"[MCP TOOL] update_sharepoint_document | FAILED: {str(e)}")
        return f"Error updating document: {str(e)}"

@mcp.tool()
def search_documents(query: str, limit: int = 3) -> str:
    """
    Search for documents in SharePoint related to a query.
    
    Args:
        query: The search term.
        limit: Max results.
    """
    logger.info(f"[Action MCP] Searching Documents for '{query}'")
    try:
        results = _get_sharepoint().search_documents(query, limit)
        if not results:
            return "No documents found."
        
        output = "Search Results:\n"
        for i, res in enumerate(results):
            output += f"{i+1}. {res['name']} (ID: {res['id']})\n   {res.get('webUrl', '')}\n"
        return output
    except Exception as e:
        logger.error(f"[Action MCP] Search failed: {str(e)}")
        return f"Search error: {str(e)}"

@mcp.tool()
def read_multiple_documents(document_ids: List[str]) -> str:
    """
    Reads the full content of multiple SharePoint documents given their IDs.
    
    Args:
        document_ids: A list of SharePoint document IDs.
    """
    logger.info(f"[Action MCP] Reading {len(document_ids)} documents")
    try:
        sp = _get_sharepoint()
        output = ""
        for d_id in document_ids:
            try:
                content = sp.get_document_content(d_id)
                output += f"--- Document ID: {d_id} ---\n{content}\n"
            except Exception as e:
                output += f"--- Error reading Document ID: {d_id}: {str(e)} ---\n"
        return output
    except Exception as e:
        return f"Error: {str(e)}"

@mcp.tool()
def generate_pdf_report(prompt: str, data: str) -> str:
    """
    Generates a professional PDF report based on the provided data and instructions.
    
    Args:
        prompt: Instructions on how to format the report.
        data: The content/data to include in the report.
    """
    logger.info(f"[MCP TOOL] generate_pdf_report | Prompt: '{prompt[:50]}...'")
    try:
        from google import genai
        from google.genai import types
        import os
        
        client = genai.Client()
        model_name = "gemini-2.5-flash"
        
        sys_instructions = (
            "You are a professional report formatter. Your task is to extract information from "
            "the provided data and format it into a specific JSON structure for PDF rendering. "
            "Maintain a formal, professional tone suitable for a Deloitte consultancy report.\n\n"
            "Return ONLY raw valid JSON matching this schema:\n"
            "{\n"
            '  "title": "Main Report Title",\n'
            '  "date": "Month Year",\n'
            '  "ticker": "Optional string",\n'
            '  "components": [\n'
            "    {\n"
            '      "type": "text",\n'
            '      "title": "Section Title",\n'
            '      "content": "Detailed text content using Markdown formatting (bolding, lists, etc.)"\n'
            "    },\n"
            "    {\n"
            '      "type": "table",\n'
            '      "title": "Data Overview",\n'
            '      "headers": ["Col 1", "Col 2"],\n'
            '      "rows": [["Val1", "Val2"]]\n'
            "    }\n"
            "  ]\n"
            "}"
        )
        
        response = client.models.generate_content(
            model=model_name,
            contents=[types.Content(role="user", parts=[types.Part.from_text(text=f"Instructions: {prompt}\n\nData to format:\n{data}")])],
            config={"system_instruction": sys_instructions, "response_mime_type": "application/json"}
        )
        
        try:
            report_json = json.loads(response.text)
        except Exception as e:
            logger.error(f"Failed to parse JSON from structured output: {e}\nResponse: {response.text}")
            return f"Failed to generate report structure. JSON parsing error."
        
        output_pdf = "assets/generated_report.pdf"
        output_image = "assets/generated_report_preview.png"
        
        from utils.internal_renderer import render_report
        success = render_report(report_json, output_pdf, output_image)
        if success:
            logger.info("[MCP TOOL] generate_pdf_report | Success")
            return f"PDF report generated successfully as {output_pdf} and preview as {output_image}"
        else:
            return "Failed to render PDF report."
            
    except Exception as e:
        logger.error(f"[MCP TOOL] generate_pdf_report | FAILED: {str(e)}")
        return f"Error generating PDF: {str(e)}"

if __name__ == "__main__":
    mcp.run()
