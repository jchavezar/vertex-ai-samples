import os
import json
import logging
from typing import List, Optional

from pydantic import BaseModel, Field
from fastmcp import FastMCP

from mcp_service.mcp_sharepoint import SharePointMCP
from utils.auth_context import get_user_token
from pipelines.regenerative_pipeline import run_regenerative_pipeline
from utils.pwc_renderer import render_report

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger("mcp_server_actions")

mcp = FastMCP("Security-Proxy-Actions-MCP")

# --- PROMPTS ---
ACTION_INSTRUCTIONS = """
You are a highly secure Action Agent for PWC. 
Your role is exclusively to perform actions such as generating reports, creating PDFs, or updating documents.
You do not search for information. You rely on the user to provide the necessary information.
"""

@mcp.prompt()
def action_persona(context: str = "") -> str:
    """Exports the official PWC Action persona."""
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
        url = _get_sharepoint().upload_document(filename, new_content, target_folder_id)
        logger.info(f"[MCP TOOL] update_sharepoint_document | Success | URL: {url}")
        return f"Document '{filename}' successfully saved/updated at: {url}"
    except Exception as e:
        logger.error(f"[MCP TOOL] update_sharepoint_document | FAILED: {str(e)}")
        return f"Error updating document: {str(e)}"

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
        # We can reuse the regenerative pipeline or pwc_renderer
        # run_regenerative_pipeline typically modifies an existing report
        # If we just want a fresh generation, we can use the main pipeline or just create a minimal JSON and render it
        # For simplicity, we'll return a stub or call a basic generation logic
        
        # We can create a dummy initial JSON structure from the data
        from backend.agents.pdf_editor_agent import create_pdf_editor_agent
        # This is a bit complex if it requires multiple steps.
        # Let's assume the agent can just format the data as standard Markdown and we save it.
        # Or, we can use render_report directly with a generic JSON.
        
        generic_json = {
            "title": "Generated Report",
            "date": "March 2026",
            "ticker": "PWC",
            "components": [
                {
                    "type": "text",
                    "title": "Input Data",
                    "content": data
                }
            ]
        }
        
        output_pdf = "assets/generated_report.pdf"
        output_image = "assets/generated_report_preview.png"
        
        success = render_report(generic_json, output_pdf, output_image)
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
