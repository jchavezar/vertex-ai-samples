import os
from google.adk.agents import LlmAgent
from google.adk.tools import FunctionTool
from mcp_sharepoint import SharePointMCP
from typing import List, Union
from pydantic import BaseModel, Field

from auth_context import get_user_token

def get_mcp():
    token = get_user_token()
    return SharePointMCP(token=token)

def _search_sharepoint_documents(query: str, limit: int = 5) -> str:
    """
    Search SharePoint documents for matching content using the Microsoft Graph API.
    Args:
        query: The search keywords or phrases. Use '*' for all documents.
        limit: Max number of documents to return.
    """
    import json
    res = get_mcp().search_documents(query, limit)
    return json.dumps(res, indent=2)

search_sharepoint_documents = FunctionTool(func=_search_sharepoint_documents)

def _read_document_content(item_id: str) -> str:
    """
    Reads the full content of a specified SharePoint document based on its item_id.
    Args:
        item_id: The unique identifier of the file from SharePoint.
    """
    return get_mcp().get_document_content(item_id)

read_document_content = FunctionTool(func=_read_document_content)

INSTRUCTIONS = """
You are a highly secure, general intelligence security proxy assistant for PWC. 
Your primary goal is to provide insightful consulting intelligence from confidential client documents while completely masking all sensitive and identifying information.
You will extract actionable best practices, benchmarks, and "success stories" from the documents but strip away who it was for, exact financial amounts, PII, and credentials.

Follow these rules for MASKING data:
1. Personal Identifiers -> Replace with role/title
2. Financial Details -> Generalize to percentages/ranges
3. Credentials -> Fully redact
4. Contact Information -> Fully redact 
5. Company Identifiers -> Replace with industry descriptors
6. Contract Specifics -> Generalize to ranges/patterns

Use your tools to search SharePoint and read the appropriate documents based on the user's query.
Synthesize the response generalizing the intelligence.
Crucially, when you formulate a strategy or best practice from a document, you MUST also emit a Project Card for that strategy/document to be displayed in the UI. Make sure the title is generic.

Return your response adhering strictly to the JSON schema.
"""

class ProjectCard(BaseModel):
    title: str = Field(description="Generic masked title (e.g. 'M&A Retention Strategy')")
    industry: str = Field(description="Industry of the referenced company")
    factual_information: str = Field(description="Factual information from the documents nicely formatted and organized but completely masking all sensitive data")
    insights: List[str] = Field(description="Strategic insights and recommendations derived from the source")
    key_metrics: List[str] = Field(description="General ranges or percentages of impact")
    document_name: str = Field(description="Original document name used as source")

class TextChunk(BaseModel):
    markdown_text: str = Field(description="Your insightful, masked answer to the user's question, strictly following zero-leak rules")

class ResponseOutput(BaseModel):
    parts: List[Union[TextChunk, ProjectCard]] = Field(description="A sequence of text parts and project cards to stream to the user. MUST alternate between Text and Cards or output all at once.")

agent = LlmAgent(
    name="PWC_Security_Proxy",
    model="gemini-3-pro-preview",
    instruction=INSTRUCTIONS,
    tools=[search_sharepoint_documents, read_document_content],
    output_schema=ResponseOutput,
    output_key="proxy_output"
)
